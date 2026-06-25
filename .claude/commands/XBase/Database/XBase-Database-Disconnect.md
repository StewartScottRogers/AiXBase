# XBase-Database-Disconnect

Close a named connection handle and release its resources.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | The logical alias registered by `XBase-Database-Connect` |
| `RollbackOpenTransaction` | bool | no | `true` | If a transaction is open, roll it back before closing |

## Outputs

```json
{
  "Success": true,
  "ConnectionName": "<alias>",
  "ClosedAt": "<ISO-8601>"
}
```

## Steps

1. Look up the connection by `ConnectionName`; if not found, return `XBASE_CONNECTION_INVALID`
2. If an open transaction exists on this connection:
   - If `RollbackOpenTransaction` is `true`, issue `ROLLBACK`
   - If `RollbackOpenTransaction` is `false`, return `XBASE_TRANSACTION_STILL_OPEN`
3. Close the SQLite connection
4. Deregister the `ConnectionName` from the session
5. Return `ClosedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not found in the session |
| `XBASE_TRANSACTION_STILL_OPEN` | Open transaction exists and `RollbackOpenTransaction` is `false` |

## Dependencies

- `XBase-Database-Connect` — must have been called to open this connection
