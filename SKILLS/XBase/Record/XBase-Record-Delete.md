# XBase-Record-Delete

Delete rows matching a filter. Performs a soft delete by default (sets `IsDeleted = 1`).

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Target table |
| `Filter` | object | yes | — | Compiled filter from `XBase-Query-Filter` |
| `HardDelete` | bool | no | `false` | If `true`, issues a physical `DELETE` instead of soft delete |
| `TransactionName` | string | no | — | Execute within this named transaction |

## Outputs

```json
{
  "Success": true,
  "DeletedCount": 1,
  "HardDelete": false
}
```

## Steps

1. Validate `ConnectionName`, `TableName`, and that `Filter` is not empty
2. If `HardDelete` is `false`:
   - Execute `UPDATE <TableName> SET IsDeleted = 1, UpdatedAt = <now> WHERE <filter>`
3. If `HardDelete` is `true`:
   - Execute `DELETE FROM <TableName> WHERE <filter>`
4. Return `DeletedCount` and `HardDelete` mode used

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_RECORD_FILTER_REQUIRED` | `Filter` was empty or omitted |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter`
- `XBase-Transaction-Begin` — if using a transaction
