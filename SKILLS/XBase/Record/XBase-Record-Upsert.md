# XBase-Record-Upsert

Insert a row if no matching record is found on the specified conflict columns, or update the existing matching record in place if a conflict is detected.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Registered connection alias |
| `TableName` | string | yes | Target table name |
| `Row` | object | yes | `{ ColumnName: value }` map representing the row to insert or update |
| `ConflictColumns` | array | yes | Column names that define uniqueness for conflict detection |
| `TransactionName` | string | no | If supplied, execute within this transaction's workspace directory |

## Outputs

```json
{
  "Success": true,
  "Action": "inserted",
  "RowId": 42
}
```

`Action` is either `"inserted"` or `"updated"`.

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Resolve the active data directory: if `TransactionName` is supplied, verify `_txn_{TransactionName}/` exists (return `XBASE_TRANSACTION_NOT_OPEN` if not); if `{TableName}.dbf` is not yet present in the workspace, copy it lazily from the live directory; use workspace paths for all reads and writes. Otherwise use the live database directory.
3. read-text-file(`_schema.json`); locate the `TableName` entry in `Tables`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. Validate each name in `ConflictColumns` against the table's column definitions; return `XBASE_SCHEMA_COLUMN_MISSING` for any unknown name.
5. read-binary-file(`{TableName}.dbf`); parse the DBF header to obtain `HeaderSize`, `RecordSize`, `RecordCount`, and the field descriptor array; decode each active (non-deleted) record from its fixed byte positions.
6. Search the decoded active records for an existing record where every `ConflictColumns` field value matches the corresponding value in `Row`.
7. **No conflict — insert path:** Follow the full `XBase-Record-Insert` logic for this single row:
   a. Inject `Default` values for omitted columns with defaults defined in the schema.
   b. Enforce `NOT NULL`, `UNIQUE` (for columns not in `ConflictColumns`), and `FOREIGN KEY` constraints; return `XBASE_RECORD_CONSTRAINT_VIOLATION` on any violation.
   c. Assign `Id = table.NextId`; set `CreatedAt` and `UpdatedAt` to the current ISO-8601 UTC timestamp; set `IsDeleted = 0`.
   d. Encode the row as a fixed-length dBASE III binary record: deletion flag `0x20` followed by each field's bytes at its fixed offset within the record.
   e. append-binary-record(`{TableName}.dbf`, encodedRecord).
   f. Read the DBF header; increment `RecordCount` at bytes 4–7 by 1; update last-modified date at bytes 1–3; write-binary-file the updated header back at byte offset 0.
   g. Insert a sorted key entry into each `.ndx` B-tree index for this table.
   h. Increment `table.NextId` by 1; write-text-file(`_schema.json`, updatedSchema).
   i. Set `Action = "inserted"` and `RowId = new Id`.
8. **Conflict found — update path:** Follow the `XBase-Record-Update` logic for the single matching record:
   a. Apply all field values from `Row` that are not in `ConflictColumns` to the matching record.
   b. Set `UpdatedAt` to the current ISO-8601 UTC timestamp.
   c. Enforce `UNIQUE` and `FOREIGN KEY` constraints on updated fields; return `XBASE_RECORD_CONSTRAINT_VIOLATION` on any violation.
   d. Re-encode the updated field bytes; seek to the record's byte offset (`HeaderSize + (RecordIndex × RecordSize)`); overwrite the updated field bytes in place.
   e. Update each `.ndx` B-tree index whose indexed column was changed: remove the old key entry and insert the new key entry.
   f. Set `Action = "updated"` and `RowId = existing record's Id`.
9. Return `Action` and `RowId`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but workspace directory not found |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_SCHEMA_COLUMN_MISSING` | A conflict column or value column is not defined for this table |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | `NOT NULL`, `UNIQUE`, or `FOREIGN KEY` constraint violated |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must exist before upserting
- `XBase-Transaction-Begin` — if using a named transaction
