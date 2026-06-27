# XBase-Transaction-Begin

Begin a named transaction by creating a directory snapshot workspace inside the database directory.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Open connection alias |
| `TransactionName` | string | yes | Logical alias for this transaction; used by Commit, Rollback, and Savepoint |
| `IsolationLevel` | string | no | Reserved for future use; currently ignored — all transactions use the directory-snapshot isolation model |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "StartedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Resolve the workspace path: `{DatabasePath}/_txn_{TransactionName}/`.
3. If `_txn_{TransactionName}/` already exists in the database directory, return `XBASE_TRANSACTION_NAME_IN_USE`.
4. Create the directory `{DatabasePath}/_txn_{TransactionName}/` using `create-directory(path)`.
5. Copy `_schema.json` from the database directory into `{DatabasePath}/_txn_{TransactionName}/_schema.json` using `copy-file(src, dest)`.
6. Register the `TransactionName → DatabasePath` mapping in the session.
7. Return `TransactionName` and `StartedAt`.

All subsequent reads and writes during the transaction operate on files inside `_txn_{TransactionName}/`. Table `.dbf` files are copied lazily into the workspace only when first modified. Reads check the workspace first; if the file is absent, the live directory is read instead. Live data files remain untouched until `XBase-Transaction-Commit` moves them. `XBase-Transaction-Rollback` deletes the workspace, leaving live files untouched.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `XBASE_TRANSACTION_NAME_IN_USE` | `_txn_{TransactionName}/` directory already exists |

## Dependencies

- `XBase-Database-Connect`
