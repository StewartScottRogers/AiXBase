# XBase-Record-Update

Update columns on rows matching a filter expression.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Target table |
| `Values` | object | yes | — | `{ ColumnName: newValue }` map of fields to set |
| `Filter` | object | yes | — | Compiled filter from `XBase-Query-Filter` — must be provided to avoid full-table updates |
| `TransactionName` | string | no | — | Execute within this named transaction |

## Outputs

```json
{
  "Success": true,
  "UpdatedCount": 2
}
```

## Steps

1. Validate `ConnectionName`, `TableName`, and that `Filter` is not empty
2. Auto-set `UpdatedAt` to current ISO-8601 timestamp if the column exists and is not in `Values`
3. Build `UPDATE <TableName> SET <assignments> WHERE <filter>`
4. Execute with parameterized values
5. Return `UpdatedCount`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_SCHEMA_COLUMN_MISSING` | A column in `Values` does not exist |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | Constraint failed on update |
| `XBASE_RECORD_FILTER_REQUIRED` | `Filter` was empty or omitted |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter`
- `XBase-Transaction-Begin` — if using a transaction
