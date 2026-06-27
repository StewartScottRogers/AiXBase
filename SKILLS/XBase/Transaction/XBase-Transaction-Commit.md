# XBase-Transaction-Commit

Commit an open transaction by atomically moving all workspace files over their live counterparts, then deleting the transaction workspace directory.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TransactionName` | string | yes | Logical alias registered by `XBase-Transaction-Begin` |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "CommittedAt": "<ISO-8601>"
}
```

## Steps

1. Verify `TransactionName` is active in the session; if not found, return `XBASE_TRANSACTION_NOT_OPEN`.
2. Verify `{DatabasePath}/_txn_{TransactionName}/` exists on disk using `directory-exists(path)`; if not, return `XBASE_TRANSACTION_NOT_OPEN`.
3. For each file at the root of `_txn_{TransactionName}/` (excluding any `sp_*/` savepoint subdirectories): atomically move it over the corresponding live file in the database directory using `move-file-atomic(workspaceFile, liveFile)`.
4. Read the live `_meta.json` using `read-text-file(path)`, update the `UpdatedAt` field to the current UTC timestamp, and write it back using `write-text-file(path, content)`.
5. Delete the `_txn_{TransactionName}/` directory recursively using `delete-directory-recursive(path)`, removing any remaining savepoint subdirectories along with it.
6. Deregister `TransactionName` from the session.
7. Return `TransactionName` and `CommittedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction workspace for that name |

## Dependencies

- `XBase-Transaction-Begin`
