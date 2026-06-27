# XBase-Backup-Create

Copy the entire database directory to a timestamped backup directory under `{DatabaseRoot}/backups/`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Open connection alias |
| `BackupLabel` | string | no | Human-readable label appended to the backup directory name (e.g. `pre-migration`) |

## Outputs

```json
{
  "Success": true,
  "BackupPath": "{DatabaseRoot}/backups/myapp_20260625T143201_pre-migration/",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Resolve the source database directory from the registered connection.
3. Verify `{DatabaseRoot}/backups/` exists; if not, create it using `create-directory({DatabaseRoot}/backups/)`.
4. Generate the destination directory name: `{DatabaseName}_{YYYYMMDDTHHmmss}` appended with `_{BackupLabel}` if `BackupLabel` is provided.
5. Recursively copy the source database directory into `{DatabaseRoot}/backups/{destName}/` using `copy-directory-recursive(sourcePath, destPath)`. If a file system error occurs during the copy, return `XBASE_BACKUP_IO_ERROR`.
6. Return `BackupPath` (the full path to the newly created backup directory) and `CreatedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `XBASE_BACKUP_IO_ERROR` | File system error during the directory copy |

## Dependencies

- `XBase-Database-Connect`
