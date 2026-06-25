# XBase-Index-List

List all indexes defined on a table.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to inspect |

## Outputs

```json
{
  "Success": true,
  "TableName": "Tickets",
  "Indexes": [
    { "IndexName": "idx_tickets_status", "Unique": false, "Columns": ["StatusId"] },
    { "IndexName": "idx_tickets_created", "Unique": false, "Columns": ["CreatedAt"] }
  ]
}
```

## Steps

1. Validate `ConnectionName` and `TableName`
2. Execute: `PRAGMA index_list(<TableName>)`
3. For each index, execute `PRAGMA index_info(<IndexName>)` to get column list
4. Return the `Indexes` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |

## Dependencies

- `XBase-Database-Connect`
