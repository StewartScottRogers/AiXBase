# XBase-Query-Execute

Execute a compound query specification against the database in a single call, combining filter, join, aggregate, and sort into one round-trip. Dispatches to the appropriate binary DBF file operations based on the requested operation.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Registered connection alias |
| `Operation` | string | yes | `SELECT`, `INSERT`, `UPDATE`, or `DELETE` |
| `TableName` | string | yes | Target table name |
| `Columns` | array | no | Column projection for `SELECT` (default `["*"]`) |
| `Filter` | object | no | Compiled filter specification from `XBase-Query-Filter` |
| `Sort` | object | no | Compiled sort specification from `XBase-Query-Sort` |
| `Join` | object | no | Compiled join specification from `XBase-Query-Join` |
| `Aggregate` | object | no | Compiled aggregate specification from `XBase-Query-Aggregate` |
| `Limit` | int | no | Maximum rows to return (`SELECT` only) |
| `Offset` | int | no | Rows to skip before returning results (`SELECT` only, default `0`) |
| `Values` | object | no | Field values for `INSERT` or `UPDATE` |
| `IncludeDeleted` | bool | no | Include soft-deleted rows in `SELECT` (default `false`) |
| `HardDelete` | bool | no | Physically remove matched records on `DELETE`; default is soft-delete (default `false`) |
| `TransactionName` | string | no | Execute within this named transaction |

## Outputs

For `SELECT`:
```json
{ "Success": true, "Rows": [...], "TotalCount": 5 }
```

For `INSERT`:
```json
{ "Success": true, "InsertedCount": 1, "LastInsertedId": 42 }
```

For `UPDATE` / `DELETE`:
```json
{ "Success": true, "AffectedRows": 3 }
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Validate `Operation` is one of `SELECT`, `INSERT`, `UPDATE`, `DELETE`; return an error if not recognized.
3. Resolve the active data directory: if `TransactionName` is supplied, verify `_txn_{TransactionName}/` exists (return `XBASE_TRANSACTION_NOT_OPEN` if not) and use workspace paths; otherwise use the live database directory.
4. read-text-file(`_schema.json`); locate the `TableName` entry in `Tables`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
5. Dispatch based on `Operation`:

   **SELECT**: read-binary-file(`{TableName}.dbf`); parse the DBF header to obtain `HeaderSize`, `RecordSize`, `RecordCount`, and the field descriptor array; decode each record from its fixed byte positions. Discard soft-deleted records (deletion flag `0x2A` or `IsDeleted = 1`) unless `IncludeDeleted` is `true`. Apply the `Filter` specification in memory. Apply the `Join` specification: read-binary-file the joined table's `.dbf`, decode its active records, perform the in-memory INNER or LEFT join on `OnLeft == OnRight`. Compute `TotalCount` as the count of rows remaining after filtering and joining. Apply the `Aggregate` specification: group the row set by `GroupBy` column values and compute the aggregate function per group, replacing the row set with aggregated result rows. Apply the `Sort` specification: sort in memory by the specified columns and directions. Apply `Offset` (skip rows) and `Limit` (retain at most N rows). Project `Columns`. Return `Rows` and `TotalCount`.

   **INSERT**: require `Values` (or a `Rows` array if multiple inserts); enforce `NOT NULL`, `UNIQUE`, and `FOREIGN KEY` constraints; assign `Id = table.NextId`; set `CreatedAt`, `UpdatedAt` to the current ISO-8601 UTC timestamp and `IsDeleted = 0`; encode the fixed-length binary record with deletion flag `0x20`; append-binary-record to `{TableName}.dbf`; update `RecordCount` at bytes 4–7 and last-modified date at bytes 1–3 in the DBF header; update each `.ndx` B-tree index; increment `table.NextId`; write-text-file(`_schema.json`, updatedSchema); return `InsertedCount` and `LastInsertedId`.

   **UPDATE**: require `Filter` (return `XBASE_RECORD_FILTER_REQUIRED` if absent); read-binary-file(`{TableName}.dbf`); decode all records; apply `Filter` to find matching active records; for each match, apply `Values`, set `UpdatedAt` to the current ISO-8601 UTC timestamp, enforce `UNIQUE` and `FOREIGN KEY` constraints, re-encode updated field bytes, seek to the record's byte offset (`HeaderSize + (RecordIndex × RecordSize)`), and overwrite the updated field bytes in place; update each `.ndx` index whose indexed column appears in `Values`; return `AffectedRows`.

   **DELETE**: require `Filter` (return `XBASE_RECORD_FILTER_REQUIRED` if absent); read-binary-file(`{TableName}.dbf`); decode all records; apply `Filter` to find matching active records. If `HardDelete` is `false`: seek to each matching record's byte offset and write `0x2A` at byte 0, update the `IsDeleted` and `UpdatedAt` field bytes in place. If `HardDelete` is `true`: rewrite the entire `.dbf` file containing only retained (non-matching, non-deleted) records; write an updated DBF header with the reduced `RecordCount` and current last-modified date; rebuild all `.ndx` indexes for this table from the retained record set. Return `AffectedRows`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but workspace directory not found |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | `NOT NULL`, `UNIQUE`, or `FOREIGN KEY` constraint violated during `INSERT` or `UPDATE` |
| `XBASE_RECORD_FILTER_REQUIRED` | `UPDATE` or `DELETE` called without a `Filter` |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — to build the `Filter` specification
- `XBase-Query-Sort` — to build the `Sort` specification
- `XBase-Query-Join` — to build the `Join` specification
- `XBase-Query-Aggregate` — to build the `Aggregate` specification
- `XBase-Transaction-Begin` — if using a named transaction
