# XBase-Record-Insert

Insert one or more rows into a table.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Target table |
| `Rows` | array | yes | — | Array of `{ ColumnName: value }` maps |
| `TransactionName` | string | no | — | If supplied, execute within this named transaction |

## Outputs

```json
{
  "Success": true,
  "InsertedCount": 3,
  "LastInsertedId": 42
}
```

## Steps

1. Validate `ConnectionName` and `TableName`
2. If `TransactionName` is supplied, verify the transaction is open
3. For each row in `Rows`:
   - Auto-set `CreatedAt` and `UpdatedAt` to current ISO-8601 timestamp if the columns exist and are not provided
   - Build and execute `INSERT INTO <TableName> (<cols>) VALUES (<placeholders>)` with parameterized values
4. Return `InsertedCount` and `LastInsertedId`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | NOT NULL / UNIQUE / FK constraint failed |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but not active |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must exist
- `XBase-Transaction-Begin` — if using a transaction
