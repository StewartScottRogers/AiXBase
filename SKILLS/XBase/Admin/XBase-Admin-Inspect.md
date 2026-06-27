# XBase-Admin-Inspect

Inspect the structural health of a connected database: report tables, record counts, index counts, active transaction workspaces, and any detected anomalies.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ConnectionName | string | yes | The connection alias for the database to inspect |
| IncludeRecordCounts | bool | no (default true) | Read each `.dbf` file and count active and deleted records |
| IncludeIndexInfo | bool | no (default true) | Count `.ndx` files for each table and check for orphans or missing files |
| IncludeTransactions | bool | no (default true) | List active transaction workspace directories |

## Outputs

```json
{
  "Success": true,
  "DatabaseName": "inventory",
  "Tables": [
    { "Name": "Products", "RecordCount": 4210, "DeletedCount": 12, "IndexCount": 2 }
  ],
  "ActiveTransactions": ["_txn_batch-import"],
  "Anomalies": [],
  "InspectedAt": "2026-06-27T14:00:00Z"
}
```

## Steps

1. Validate `ConnectionName`. If it is not registered in the current session, return `XBASE_CONNECTION_INVALID`.
2. Read `_meta.json` and `_schema.json` from the database directory. If either file is missing or unparseable, return `XBASE_DATABASE_CORRUPT`.
3. For each table defined in `_schema.json`:
   a. Verify that `{TableName}.dbf` exists in the database directory. If the file is absent, record an anomaly: "Missing .dbf for table {TableName}".
   b. If `IncludeRecordCounts` is true: read the DBF header; bytes 4–7 contain the declared record count as a uint32 little-endian integer. Scan each record in the file: records with deletion flag `0x20` are active; records with flag `0x2A` are deleted. If the header's declared count does not match the scanned total, record an anomaly describing the mismatch with the table name and both counts.
   c. If `IncludeIndexInfo` is true: count the `.ndx` files present in the database directory whose names begin with `{TableName}.`. For each index entry in `_schema.json` that belongs to this table, verify a corresponding `.ndx` file exists; if any are absent, record an anomaly. If `.ndx` files exist that are not referenced in `_schema.json` for any table, record each as an orphaned index file.
4. If `IncludeTransactions` is true: list all directories inside the database directory whose names match the pattern `_txn_*`. Record each directory name in `ActiveTransactions`.
5. Collect all anomaly strings identified across steps 3 and 4 into the `Anomalies` array.
6. Return `DatabaseName`, `Tables` (one entry per table containing `Name`, `RecordCount`, `DeletedCount`, and `IndexCount`), `ActiveTransactions`, `Anomalies`, and `InspectedAt` set to the current ISO-8601 timestamp.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the current session |
| `XBASE_DATABASE_CORRUPT` | `_meta.json` or `_schema.json` is missing or cannot be parsed |

## Dependencies

- XBase-Database-Connect (ConnectionName must already be registered before calling this skill)
- Readable file system access to the database directory
