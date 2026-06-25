# XBase-Transaction-Rollback

Roll back the current transaction and discard all uncommitted changes.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TransactionName` | string | yes | — | Logical alias registered by `XBase-Transaction-Begin` |
| `ToSavepoint` | string | no | — | If provided, rolls back only to the named savepoint instead of the full transaction |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "RolledBackTo": "full",
  "RolledBackAt": "<ISO-8601>"
}
```

`RolledBackTo` is `"full"` or the savepoint name.

## Steps

1. Look up `TransactionName`
2. If `ToSavepoint` is provided:
   - Execute `ROLLBACK TO SAVEPOINT <ToSavepoint>`
   - Leave the transaction open
3. Otherwise:
   - Execute `ROLLBACK`
   - Deregister `TransactionName` from the session
4. Return `RolledBackTo` and `RolledBackAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction with that name |
| `XBASE_SAVEPOINT_NOT_FOUND` | `ToSavepoint` name was not created on this transaction |

## Dependencies

- `XBase-Transaction-Begin`
