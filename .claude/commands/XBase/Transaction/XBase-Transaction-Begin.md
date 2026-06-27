# XBase-Transaction-Begin

Begin a named transaction by creating a directory snapshot workspace.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TransactionName` | string | yes | — | Logical alias for this transaction, used by Commit / Rollback / Savepoint |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "StartedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. Resolve `_txn_{TransactionName}/` inside the database directory
3. If the `_txn_{TransactionName}/` directory already exists, return `XBASE_TRANSACTION_NAME_IN_USE`
4. `Directory.CreateDirectory(_txn_{TransactionName}/)`
5. Copy `_schema.json` into `_txn_{TransactionName}/_schema.json`
6. Register `TransactionName → DatabasePath` mapping in the session
7. Return `StartedAt`

**How transaction isolation works:** All writes during the transaction operate only on files inside `_txn_{TransactionName}/`. Table `.dbf` files are copied lazily — only when a table is first modified. Reads within the transaction check the transaction workspace first; if the file is not there, the live directory is read. The live data files are not modified until `XBase-Transaction-Commit` moves the workspace files over them. `XBase-Transaction-Rollback` simply deletes the workspace directory, leaving live files untouched.

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection alias not registered |
| `XBASE_TRANSACTION_NAME_IN_USE` | `_txn_{TransactionName}/` directory already exists |

## Dependencies

- `XBase-Database-Connect`
