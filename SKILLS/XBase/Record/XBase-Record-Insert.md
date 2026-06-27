# XBase-Record-Insert

Insert one or more rows into a table, enforcing constraints and updating indexes in the binary DBF file.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Registered connection alias |
| `TableName` | string | yes | Target table name |
| `Rows` | array | yes | Array of `{ ColumnName: value }` objects to insert |
| `TransactionName` | string | no | If supplied, write into this transaction's workspace directory |

## Outputs

```json
{
  "Success": true,
  "InsertedCount": 3,
  "LastInsertedId": 42
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Resolve the active data directory: if `TransactionName` is supplied, verify `_txn_{TransactionName}/` exists (return `XBASE_TRANSACTION_NOT_OPEN` if not); if `{TableName}.dbf` is not yet present in the workspace, copy it lazily from the live directory; use workspace paths for all subsequent reads and writes. Otherwise use the live database directory.
3. read-text-file(`_schema.json`) from the resolved directory; parse the JSON; locate the `TableName` entry in `Tables`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. For each row in `Rows`:
   a. Inject `Default` values for any column whose value is omitted and which has a `Default` defined in the schema.
   b. Enforce `NOT NULL` constraints: if any non-nullable column has no value and no default, return `XBASE_RECORD_CONSTRAINT_VIOLATION`.
   c. Enforce `UNIQUE` constraints: for each unique column, read its `.ndx` index (if present) or scan all active records in `{TableName}.dbf` to check for a duplicate value; return `XBASE_RECORD_CONSTRAINT_VIOLATION` on conflict.
   d. Enforce `FOREIGN KEY` constraints: for each FK column, read-binary-file the referenced table's `.dbf`, decode its records, and confirm the parent `Id` exists with `IsDeleted = 0`; return `XBASE_RECORD_CONSTRAINT_VIOLATION` if the parent is absent or deleted.
   e. Assign `Id = table.NextId`; set `CreatedAt` and `UpdatedAt` to the current ISO-8601 UTC timestamp; set `IsDeleted = 0`.
   f. Encode the row as a fixed-length dBASE III binary record: one byte `0x20` (active deletion flag) followed by each field's bytes at its fixed offset within the record, as defined by the field descriptor array in the DBF header. Encode `N`-type fields as space-left-padded ASCII numeric strings padded to the declared field width; encode `C`-type fields as space-right-padded ASCII strings padded to the declared field width.
   g. append-binary-record(`{TableName}.dbf`, encodedRecord) to add the fixed-length record at the end of the file.
   h. Read the DBF header (first 32 bytes) from `{TableName}.dbf`; increment the `RecordCount` at bytes 4–7 (uint32, little-endian) by 1; update the last-modified date at bytes 1–3 (YY, MM, DD binary) to today's date; write-binary-file the updated 32-byte header back to the file at byte offset 0.
   i. Insert a sorted key entry into each `.ndx` B-tree index defined for this table, associating the indexed column value(s) with the new record's `Id`.
   j. Increment `table.NextId` by 1 in the parsed schema.
5. write-text-file(`_schema.json`, updatedSchema) to persist the incremented `NextId` values.
6. Return `InsertedCount` and `LastInsertedId`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but workspace directory not found |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | `NOT NULL`, `UNIQUE`, or `FOREIGN KEY` constraint violated |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must exist before inserting
- `XBase-Transaction-Begin` — if using a named transaction
