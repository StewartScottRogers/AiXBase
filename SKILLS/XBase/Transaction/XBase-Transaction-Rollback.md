# XBase-Transaction-Rollback

Roll back an open transaction by deleting its workspace directory (full rollback) or restoring the workspace from a savepoint snapshot (partial rollback).

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TransactionName` | string | yes | Logical alias registered by `XBase-Transaction-Begin` |
| `ToSavepoint` | string | no | If provided, restore the workspace to this savepoint and leave the transaction open |

## Outputs

```json
{
  "Success": true,
  "TransactionName": "<alias>",
  "RolledBackTo": "full",
  "RolledBackAt": "<ISO-8601>"
}
```

`RolledBackTo` is `"full"` when no savepoint is specified, or the savepoint name when rolling back to a savepoint.

## Steps

### Full Rollback (`ToSavepoint` not supplied)

1. Verify `TransactionName` is active in the session; if not found, return `XBASE_TRANSACTION_NOT_OPEN`.
2. Verify `{DatabasePath}/_txn_{TransactionName}/` exists on disk using `directory-exists(path)`; if not, return `XBASE_TRANSACTION_NOT_OPEN`.
3. Delete `{DatabasePath}/_txn_{TransactionName}/` recursively using `delete-directory-recursive(path)`, discarding all workspace files and savepoint subdirectories.
4. Deregister `TransactionName` from the session.
5. Return `RolledBackTo: "full"` and `RolledBackAt`.

### Savepoint Rollback (`ToSavepoint` supplied)

1. Verify `TransactionName` is active in the session; if not found, return `XBASE_TRANSACTION_NOT_OPEN`.
2. Resolve the savepoint path: `{DatabasePath}/_txn_{TransactionName}/sp_{ToSavepoint}/`.
3. If the savepoint directory does not exist, return `XBASE_SAVEPOINT_NOT_FOUND`.
4. For each file in `sp_{ToSavepoint}/`, overwrite the corresponding file in the workspace root `_txn_{TransactionName}/` using `copy-file(savepointFile, workspaceFile)`.
5. Delete the `sp_{ToSavepoint}/` savepoint subdirectory using `delete-directory-recursive(path)`.
6. Leave the transaction open — do not deregister `TransactionName`.
7. Return `RolledBackTo: ToSavepoint` and `RolledBackAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction with that name |
| `XBASE_SAVEPOINT_NOT_FOUND` | `sp_{ToSavepoint}/` directory does not exist in the workspace |

## Dependencies

- `XBase-Transaction-Begin`
