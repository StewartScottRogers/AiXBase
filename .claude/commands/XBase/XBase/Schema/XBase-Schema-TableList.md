# XBase-Schema-TableList

Return all user-defined table names from `_schema.json`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |

## Outputs

```json
{
  "Success": true,
  "Tables": ["Tickets", "Users", "Statuses"]
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. Resolve the active `_schema.json` path:
   - If a `TransactionName` is in scope and `_txn_{TransactionName}/_schema.json` exists, use that
   - Otherwise use the live `_schema.json`
3. `File.ReadAllText(_schema.json)`; parse JSON
4. Extract the `Name` field from each entry in the `Tables` array
5. Return the names sorted alphabetically as the `Tables` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |

## Dependencies

- `XBase-Database-Connect`
