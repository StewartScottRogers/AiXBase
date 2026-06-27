# XBase-Record-Update

Update field values for all records matching a filter by seeking to each matching record's byte offset in the DBF file and overwriting the affected field bytes in place.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Registered connection alias |
| `TableName` | string | yes | Target table name |
| `Filter` | object | yes | Compiled filter specification from `XBase-Query-Filter` — required to prevent unintentional full-table updates |
| `Values` | object | yes | `{ ColumnName: newValue }` map of fields to update |
| `TransactionName` | string | no | If supplied, execute within this transaction's workspace directory |

## Outputs

```json
{
  "Success": true,
  "UpdatedCount": 2
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Validate `Filter` is present and non-empty; if absent or empty, return `XBASE_RECORD_FILTER_REQUIRED`.
3. Resolve the active data directory: if `TransactionName` is supplied, verify `_txn_{TransactionName}/` exists (return `XBASE_TRANSACTION_NOT_OPEN` if not); if `{TableName}.dbf` is not yet present in the workspace, copy it lazily from the live directory; use workspace paths for all reads and writes. Otherwise use the live database directory.
4. read-text-file(`_schema.json`); locate the `TableName` entry in `Tables`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
5. Validate each key in `Values` against the table's column definitions; return `XBASE_SCHEMA_COLUMN_MISSING` for any unknown column name.
6. read-binary-file(`{TableName}.dbf`); parse the DBF header (first 32 bytes) to obtain `HeaderSize`, `RecordSize`, `RecordCount`, and the field descriptor array; decode each record from its fixed byte positions using the field descriptor array.
7. Evaluate the `Filter` specification against each active (non-deleted) record. For each matching record:
   a. Apply the new values from `Values` to the corresponding fields in the decoded record.
   b. Set `UpdatedAt` to the current ISO-8601 UTC timestamp.
   c. Enforce `UNIQUE` constraints on updated columns: scan all other active records to check for duplicate values in those columns; return `XBASE_RECORD_CONSTRAINT_VIOLATION` on conflict.
   d. Enforce `FOREIGN KEY` constraints for any updated FK column: read-binary-file the referenced table's `.dbf` and verify the referenced parent `Id` exists with `IsDeleted = 0`; return `XBASE_RECORD_CONSTRAINT_VIOLATION` if the parent is absent or deleted.
   e. Re-encode the updated field values as fixed-width bytes per the field descriptor array.
   f. Seek to the record's byte offset in the file (`HeaderSize + (RecordIndex × RecordSize) + fieldByteOffset`); overwrite only the modified field bytes in place within the binary file.
   g. Increment `UpdatedCount`.
8. For each `.ndx` B-tree index whose indexed column appears in `Values`: remove the old key entry for each updated record and insert the new key entry.
9. Return `UpdatedCount`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but workspace directory not found |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_SCHEMA_COLUMN_MISSING` | A column in `Values` is not defined for this table |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | `UNIQUE` or `FOREIGN KEY` constraint violated on update |
| `XBASE_RECORD_FILTER_REQUIRED` | `Filter` was empty or omitted |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — to build the required filter specification
- `XBase-Transaction-Begin` — if using a named transaction
