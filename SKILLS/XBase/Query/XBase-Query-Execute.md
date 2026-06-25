# XBase-Query-Execute

Execute a raw SQL string against the database. Escape hatch — prefer typed skills where possible.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `SQL` | string | yes | — | The SQL statement to execute |
| `Parameters` | array | no | `[]` | Ordered parameter values for `?` placeholders |
| `TransactionName` | string | no | — | Execute within this named transaction |

## Outputs

For `SELECT`:
```json
{
  "Success": true,
  "Rows": [ { "Id": 1, "Name": "..." } ],
  "RowCount": 5
}
```

For `INSERT` / `UPDATE` / `DELETE`:
```json
{
  "Success": true,
  "AffectedRows": 3,
  "LastInsertedId": 42
}
```

## Steps

1. Validate `ConnectionName`
2. Detect statement type from the first keyword (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, etc.)
3. Execute with parameterized `Parameters` list
4. Return the appropriate output shape based on statement type

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_QUERY_SYNTAX_ERROR` | SQLite rejected the SQL |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | Constraint violation during write |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Transaction-Begin` — if using a transaction
