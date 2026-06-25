# XBase-Index-Rebuild

Rebuild one or all indexes on a table. Useful after bulk inserts or data migrations.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `IndexName` | string | no | — | Specific index to rebuild; omit to rebuild all indexes on `TableName` |
| `TableName` | string | no | — | Table whose indexes to rebuild (ignored if `IndexName` is provided) |

## Outputs

```json
{
  "Success": true,
  "RebuiltIndexes": ["idx_tickets_status", "idx_tickets_created"]
}
```

## Steps

1. Validate `ConnectionName`
2. If `IndexName` is provided: execute `REINDEX <IndexName>`
3. Else if `TableName` is provided: execute `REINDEX <TableName>`
4. Else execute `REINDEX` (rebuilds all indexes in the database)
5. Query `sqlite_master` for affected index names and return them

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_INDEX_NOT_FOUND` | Specified `IndexName` does not exist |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Specified `TableName` does not exist |

## Dependencies

- `XBase-Database-Connect`
