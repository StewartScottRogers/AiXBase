# XBase-Transaction-Begin

Begin an explicit database transaction on a connection.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TransactionName` | string | yes | — | Logical alias for this transaction, used by Commit/Rollback/Savepoint |
| `IsolationLevel` | string | no | `IMMEDIATE` | `DEFERRED`, `IMMEDIATE`, or `EXCLUSIVE` |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "StartedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`
2. Check no transaction with `TransactionName` is already active; if so, return `XBASE_TRANSACTION_NAME_IN_USE`
3. Execute `BEGIN <IsolationLevel>`
4. Register `TransactionName` mapped to `ConnectionName` for the session
5. Return `StartedAt`

**Why `IMMEDIATE` default?** SQLite's deferred mode acquires a read lock on first read and upgrades to write on first write. If two transactions both start deferred and both try to write, one will fail with `SQLITE_BUSY`. `IMMEDIATE` acquires the write lock up front, preventing this class of conflict.

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_TRANSACTION_NAME_IN_USE` | A transaction with this alias is already active |
| `XBASE_TRANSACTION_ISOLATION_INVALID` | Unknown isolation level |

## Dependencies

- `XBase-Database-Connect`
