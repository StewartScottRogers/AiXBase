# XBase-Backup-Create

Copy the entire database directory to a timestamped backup in `XBaseFiles/backups/`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `BackupLabel` | string | no | — | Human-readable label appended to the directory name, e.g. `pre-migration` |

## Outputs

```json
{
  "Success": true,
  "BackupPath": "XBaseFiles/backups/myapp_20260625T143201_pre-migration/",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. Resolve the source database directory from the registered connection
3. Ensure `XBaseFiles/backups/` exists; create it if not
4. Generate the backup directory name: `{DatabaseName}_{YYYYMMDDTHHmmss}[_{BackupLabel}]`
5. Recursively copy every file from the source database directory into `XBaseFiles/backups/{name}/`, preserving subdirectory structure
6. Skip any active transaction directories (`_txn_*/`) — backup reflects committed state only
7. Return `BackupPath` and `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection alias not registered |
| `XBASE_BACKUP_IO_ERROR` | File system error reading or writing during the copy |

## Dependencies

- `XBase-Database-Connect`
