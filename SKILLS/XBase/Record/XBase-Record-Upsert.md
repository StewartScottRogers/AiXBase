# XBase-Record-Upsert

Insert a row if no conflict is detected on the specified columns, or update the
existing matching row in place if a conflict is found.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Target table |
| `Row` | object | yes | — | `{ ColumnName: value }` map for the row |
| `ConflictColumns` | array | yes | — | Column names that define uniqueness for conflict detection |
| `TransactionName` | string | no | — | Execute within this named transaction |

## Outputs

```json
{
  "Success": true,
  "Action": "inserted",
  "RowId": 42
}
```

`Action` is `"inserted"` or `"updated"`.

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. Resolve the active data directory (transaction workspace if `TransactionName` supplied; copy `.dbf` lazily if needed)
3. `File.ReadAllText(_schema.json)`; locate `TableName`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`
4. Validate each column in `ConflictColumns` exists in the table definition; return `XBASE_SCHEMA_COLUMN_MISSING` on failure
5. `File.ReadAllBytes({TableName}.dbf)`; read DBF header to obtain `HeaderSize`, `RecordSize`, `RecordCount`, and field descriptors; decode each record from its fixed-width byte positions line as JSON
6. Search for an existing non-deleted row where every `ConflictColumns` field value matches the corresponding `Row` value
7. **No conflict (insert path):**
   - Assign `Id` from `table.NextId`; increment `NextId`
   - Set `CreatedAt` and `UpdatedAt` to current ISO-8601 timestamp; set `IsDeleted = 0`
   - Enforce NOT NULL, UNIQUE (non-conflict columns), and FK constraints; return `XBASE_RECORD_CONSTRAINT_VIOLATION` on failure
   - `File.OpenAppend({TableName}.dbf)`; encode each field to fixed-width bytes per DBF type map; prepend deletion flag `0x20`; append the `RecordSize`-byte record
   - Update `.ndx` files for all indexed columns
   - Set `Action = "inserted"`, `RowId = new Id`
8. **Conflict found (update path):**
   - Apply all non-`ConflictColumns` values from `Row` to the matching row in memory
   - Set `UpdatedAt` to current ISO-8601 timestamp
   - Enforce constraints on updated fields
   - `File.WriteAllBytes({TableName}.dbf, packedBytes)`; write compacted DBF excluding deletion-flagged records; update header record count
   - Rebuild `.ndx` files for changed indexed columns
   - Set `Action = "updated"`, `RowId = existing row Id`
9. Write updated `_schema.json` if `NextId` changed
10. Return `Action` and `RowId`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_SCHEMA_COLUMN_MISSING` | A conflict column does not exist |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | Non-conflict constraint failed |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but workspace not found |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Transaction-Begin` — if using a transaction
