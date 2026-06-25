# XBase-Backup-Restore

Replace the live database directory with a copy from a backup directory.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `BackupPath` | string | yes | — | Path to the backup directory (absolute or relative to `AiXBase/backups/`) |
| `TargetConnectionName` | string | yes | — | Registered connection whose database directory will be overwritten |
| `CreateBackupBeforeRestore` | bool | no | `true` | Snapshot the current live database before overwriting |
| `ConfirmRestore` | bool | yes | — | Must be `true`; guards against accidental data loss |

## Outputs

```json
{
  "Success": true,
  "RestoredFrom": "<BackupPath>",
  "PreRestoreBackupPath": "AiXBase/backups/myapp_20260625T143900_pre-restore/",
  "RestoredAt": "<ISO-8601>"
}
```

## Steps

1. If `ConfirmRestore` is not `true`, return `XBASE_RESTORE_NOT_CONFIRMED`
2. Verify backup directory exists at `BackupPath`; if not, return `XBASE_BACKUP_NOT_FOUND`
3. Validate `TargetConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
4. If `CreateBackupBeforeRestore` is `true`, call `XBase-Backup-Create` on `TargetConnectionName`; record `PreRestoreBackupPath`
5. Deregister all connections to the target database from the session
6. `Directory.Delete(TargetDatabasePath, recursive:true)`
7. Recursively copy all files from `BackupPath` to `TargetDatabasePath` (`Directory.Copy`)
8. Re-register `TargetConnectionName → TargetDatabasePath` in the session
9. Return `RestoredAt` and `PreRestoreBackupPath`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_RESTORE_NOT_CONFIRMED` | `ConfirmRestore` was not `true` |
| `XBASE_CONNECTION_INVALID` | `TargetConnectionName` not registered |
| `XBASE_BACKUP_NOT_FOUND` | `BackupPath` directory does not exist |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Backup-Create` — used optionally before overwriting
