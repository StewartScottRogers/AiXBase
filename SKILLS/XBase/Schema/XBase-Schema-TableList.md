# XBase-Schema-TableList

Return all user-defined table names in the connected database.

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

1. Validate `ConnectionName`
2. Execute: `SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name`
3. Return the `name` column as the `Tables` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |

## Dependencies

- `XBase-Database-Connect`
