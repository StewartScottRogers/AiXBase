# XBase-Transaction-Savepoint

Create a named savepoint within an active transaction, allowing partial rollback.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TransactionName` | string | yes | — | Logical alias of the enclosing transaction |
| `SavepointName` | string | yes | — | Name for this savepoint |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "SavepointName": "<name>",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `TransactionName` is active
2. Execute `SAVEPOINT <SavepointName>`
3. Register `SavepointName` on the transaction record
4. Return `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction with that name |
| `XBASE_SAVEPOINT_NAME_IN_USE` | A savepoint with that name already exists on this transaction |

## Dependencies

- `XBase-Transaction-Begin`
