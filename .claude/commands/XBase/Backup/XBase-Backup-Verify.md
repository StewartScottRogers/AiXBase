# XBase-Backup-Verify

Validate the integrity of a backup directory by reading its metadata and every NDJSON data line.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `BackupPath` | string | yes | — | Path to the backup directory (absolute or relative to `AiXBase/backups/`) |

## Outputs

```json
{
  "Success": true,
  "BackupPath": "<path>",
  "IntegrityOk": true,
  "Issues": [],
  "VerifiedAt": "<ISO-8601>"
}
```

If issues are found, `IntegrityOk` is `false` and `Issues` lists each problem: the file name and line number of each invalid JSON line, plus any missing or corrupt metadata files.

## Steps

1. Verify the backup directory exists; if not, return `XBASE_BACKUP_NOT_FOUND`
2. Read `_meta.json`; verify it is valid JSON with an `XBaseVersion` field; if invalid, add to `Issues`
3. Read `_schema.json`; verify it is valid JSON with `Tables` and `Indexes` arrays; if invalid, add to `Issues`
4. For each table in `_schema.json`:
   a. Verify `{TableName}.ndjson` exists; if absent, add to `Issues`
   b. Read every line of `{TableName}.ndjson`; attempt `JSON.Parse(line)` on each; record file name and line number for any line that fails to parse
5. Set `IntegrityOk: true` if `Issues` is empty; `false` otherwise
6. Return `IntegrityOk`, `Issues`, and `VerifiedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_BACKUP_NOT_FOUND` | Directory does not exist at `BackupPath` |
| `XBASE_BACKUP_CORRUPT` | `_meta.json` missing, unreadable, or invalid JSON |

## Dependencies

None — reads files directly; does not require an open connection.
