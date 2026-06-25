# XBase-Transaction-Commit

Commit the current transaction and make all changes permanent.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TransactionName` | string | yes | — | Logical alias registered by `XBase-Transaction-Begin` |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "CommittedAt": "<ISO-8601>"
}
```

## Steps

1. Look up `TransactionName` to resolve the connection
2. Execute `COMMIT`
3. Deregister `TransactionName` from the session
4. Return `CommittedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction with that name |

## Dependencies

- `XBase-Transaction-Begin`
