# XBase-Backup-Restore

Replace the live database directory with a copy restored from a backup directory.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `BackupPath` | string | yes | Path to the backup directory to restore from |
| `TargetConnectionName` | string | yes | Registered connection whose database directory will be replaced |
| `ConfirmRestore` | bool | yes | Must be `true`; guards against accidental data loss |
| `CreateBackupBeforeRestore` | bool | no (default `true`) | Snapshot the current live database before overwriting |

## Outputs

```json
{
  "Success": true,
  "RestoredFrom": "<BackupPath>",
  "PreRestoreBackupPath": "{DatabaseRoot}/backups/myapp_20260625T143900_pre-restore/",
  "RestoredAt": "<ISO-8601>"
}
```

`PreRestoreBackupPath` is omitted if `CreateBackupBeforeRestore` is `false`.

## Steps

1. If `ConfirmRestore` is not `true`, return `XBASE_RESTORE_NOT_CONFIRMED`.
2. Verify the backup directory exists at `BackupPath` using `directory-exists(BackupPath)`; if not, return `XBASE_BACKUP_NOT_FOUND`.
3. Validate `TargetConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
4. Resolve `TargetDatabasePath` from the registered connection.
5. If `CreateBackupBeforeRestore` is `true`, invoke `XBase-Backup-Create` with `TargetConnectionName` and `BackupLabel: "pre-restore"`; record the returned path as `PreRestoreBackupPath`.
6. Deregister all connections to the target database from the session.
7. Delete `TargetDatabasePath` recursively using `delete-directory-recursive(TargetDatabasePath)`.
8. Recursively copy `BackupPath` to `TargetDatabasePath` using `copy-directory-recursive(BackupPath, TargetDatabasePath)`.
9. Re-register `TargetConnectionName → TargetDatabasePath` in the session.
10. Return `RestoredFrom`, `PreRestoreBackupPath` (if taken), and `RestoredAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_RESTORE_NOT_CONFIRMED` | `ConfirmRestore` was not `true` |
| `XBASE_BACKUP_NOT_FOUND` | `BackupPath` directory does not exist |
| `XBASE_CONNECTION_INVALID` | `TargetConnectionName` is not registered |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Backup-Create` — invoked optionally before overwriting
