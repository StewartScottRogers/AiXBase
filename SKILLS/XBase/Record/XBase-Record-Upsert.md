# XBase-Record-Upsert

Insert a row, or update it in place if a key conflict is detected.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Target table |
| `Row` | object | yes | — | `{ ColumnName: value }` map for the row |
| `ConflictColumns` | array | yes | — | Columns that define uniqueness for conflict detection |
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

1. Validate `ConnectionName`, `TableName`, and `ConflictColumns`
2. Auto-set `CreatedAt` on insert path; auto-set `UpdatedAt` on both paths
3. Build and execute:
   `INSERT INTO <TableName> (...) VALUES (...) ON CONFLICT (<ConflictColumns>) DO UPDATE SET <non-conflict columns>`
4. Determine whether a row was inserted or updated via `changes()` and `last_insert_rowid()`
5. Return `Action` and `RowId`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_SCHEMA_COLUMN_MISSING` | A conflict column does not exist |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | Non-conflict constraint failed |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Transaction-Begin` — if using a transaction
