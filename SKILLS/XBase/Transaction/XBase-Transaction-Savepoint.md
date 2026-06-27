# XBase-Transaction-Savepoint

Create a named savepoint within an open transaction by copying the current workspace state into a `sp_{SavepointName}/` subdirectory.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TransactionName` | string | yes | Logical alias of the enclosing transaction |
| `SavepointName` | string | yes | Name for this savepoint (alphanumeric and underscore characters only) |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "SavepointName": "<name>",
  "SavedAt": "<ISO-8601>"
}
```

## Steps

1. Verify `TransactionName` is active in the session; if not found, return `XBASE_TRANSACTION_NOT_OPEN`.
2. Verify `{DatabasePath}/_txn_{TransactionName}/` exists on disk using `directory-exists(path)`; if not, return `XBASE_TRANSACTION_NOT_OPEN`.
3. Resolve the savepoint path: `{DatabasePath}/_txn_{TransactionName}/sp_{SavepointName}/`.
4. If `sp_{SavepointName}/` already exists, return `XBASE_SAVEPOINT_NAME_IN_USE`.
5. Create the directory `{DatabasePath}/_txn_{TransactionName}/sp_{SavepointName}/` using `create-directory(path)`.
6. For each file at the root of `_txn_{TransactionName}/` (do not recurse into existing `sp_*/` subdirectories), copy it into `sp_{SavepointName}/` using `copy-file(workspaceFile, savepointFile)`.
7. Return `SavepointName` and `SavedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction with that name |
| `XBASE_SAVEPOINT_NAME_IN_USE` | `sp_{SavepointName}/` already exists in the workspace |

## Dependencies

- `XBase-Transaction-Begin`
