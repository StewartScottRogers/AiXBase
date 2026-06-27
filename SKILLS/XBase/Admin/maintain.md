# XBase-Admin-Maintain

Perform routine maintenance on a connected database: pack deleted records from tables, rebuild indexes, and verify backup integrity.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ConnectionName | string | yes | The connection alias for the database to maintain |
| PackTables | bool | no (default true) | Rewrite each `.dbf` file excluding soft-deleted records (hard-delete PACK) |
| RebuildIndexes | bool | no (default true) | Rebuild all `.ndx` index files from the current `.dbf` data |
| VerifyBackups | bool | no (default false) | Verify integrity of all backup directories belonging to this database |
| DryRun | bool | no (default false) | Report what would be done without performing any operations |

## Outputs

```json
{
  "Success": true,
  "TablesPackaged": 3,
  "IndexesRebuilt": 5,
  "BackupsVerified": 2,
  "Issues": [],
  "MaintenanceAt": "2026-06-27T14:00:00Z"
}
```

## Steps

1. Validate `ConnectionName`. If it is not registered in the current session, return `XBASE_CONNECTION_INVALID`.
2. If `DryRun` is true: read `_schema.json` to determine the number of tables and indexes. If `VerifyBackups` is true, also count the backup directories under `{DatabaseRoot}/backups/` whose names begin with the database name. Return a summary of the operations that would be performed — tables to pack, indexes to rebuild, and backups to verify — without executing any of them. Set the counter outputs to the counts of items that would have been processed, and return immediately.
3. If `PackTables` is true: read `_schema.json` to obtain the list of tables. For each table, invoke `XBase-Record-Delete` with `HardDelete: true` and a filter targeting all soft-deleted records (where `IsDeleted = 1`). This rewrites the `.dbf` file excluding those records and updates the header record count. Increment `TablesPackaged` for each table processed.
4. If `RebuildIndexes` is true: read `_schema.json` to obtain the list of index definitions. For each index entry, invoke `XBase-Index-Rebuild` supplying the index's `TableName` and `IndexName`. Increment `IndexesRebuilt` for each index processed.
5. If `VerifyBackups` is true: list all directories under `{DatabaseRoot}/backups/` whose names begin with the database name. For each directory, invoke `XBase-Backup-Verify` with that directory path as `BackupPath`. If a directory cannot be located or accessed, return `XBASE_BACKUP_NOT_FOUND`. Increment `BackupsVerified` for each directory verified. Collect any issue strings reported by `XBase-Backup-Verify` into the `Issues` array.
6. Return `TablesPackaged`, `IndexesRebuilt`, `BackupsVerified`, `Issues`, and `MaintenanceAt` set to the current ISO-8601 timestamp.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the current session |
| `XBASE_BACKUP_NOT_FOUND` | A backup directory listed for verification does not exist or cannot be accessed |

## Dependencies

- XBase-Database-Connect (ConnectionName must already be registered)
- XBase-Record-Delete
- XBase-Index-Rebuild
- XBase-Backup-Verify
