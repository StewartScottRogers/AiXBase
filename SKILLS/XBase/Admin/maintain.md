# XBase-Admin-Maintain

Perform a maintenance operation on a target XBase database.

## Usage

```
/maintain <DatabaseName> [operation]
```

`operation` defaults to `report` when omitted.

---

## Operations

| Operation | Description |
|---|---|
| `report` | Full health report: integrity + index health + record counts + backup status |
| `verify` | Parse every NDJSON line; list any corrupt rows with file name and line number |
| `backup` | Create a timestamped backup in `XBaseFiles/backups/` |
| `rebuild-indexes` | Rebuild all `.ndx` files from the source NDJSON data |
| `vacuum` | Hard-delete all soft-deleted rows across all tables (requires confirmation) |

---

## Steps

### `report` (default)

1. Run `verify` sub-steps and capture `IntegrityOk` + `Issues`
2. Invoke `XBase-Database-Connect` with alias `admin-report`
3. Invoke `XBase-Schema-TableList`
4. For each table:
   - Count active rows (`IsDeleted = 0`) and soft-deleted rows (`IsDeleted = 1`)
   - Invoke `XBase-Index-List`; for each index verify the `.ndx` file exists
5. Check `XBaseFiles/backups/` for the most recent backup of this database
6. Invoke `XBase-Database-Disconnect`
7. Print the health report:

```
XBase Health Report — {DatabaseName}
──────────────────────────────────────────────────────
Integrity:       {OK / {N} issues found}
Indexes:         {N} healthy  /  {M} missing
Record counts:   {TotalActive} active  /  {TotalSoftDeleted} soft-deleted
Last Backup:     {timestamp and path / "NONE — recommend running: /that {DatabaseName} backup"}
──────────────────────────────────────────────────────
{Recommendations if any issues found}
```

---

### `verify`

1. Invoke `XBase-Backup-Verify` with `BackupPath` set to `XBaseFiles/{DatabaseName}/`
   (Backup-Verify works on any valid XBase directory, not just backup copies)
2. Display:
   - `IntegrityOk: true` → "All NDJSON files are valid"
   - `IntegrityOk: false` → list each entry from `Issues` with file name and line number

---

### `backup`

1. Invoke `XBase-Database-Connect` with alias `admin-backup`
2. Invoke `XBase-Backup-Create`; optionally pass `BackupLabel` if the user provided one
3. Display the `BackupPath` and timestamp from the result
4. Invoke `XBase-Database-Disconnect`

---

### `rebuild-indexes`

1. Invoke `XBase-Database-Connect` with alias `admin-rebuild`
2. Invoke `XBase-Index-Rebuild` with no `IndexName` or `TableName` (rebuilds all indexes in the database)
3. Display the `RebuiltIndexes` list from the result
4. Invoke `XBase-Database-Disconnect`

---

### `vacuum`

1. Confirm with the user: "This will permanently hard-delete {N} soft-deleted rows across all tables. This cannot be undone. Confirm? (yes / no)"
2. If not confirmed, abort and return without changes
3. Invoke `XBase-Database-Connect` with alias `admin-vacuum`
4. Invoke `XBase-Schema-TableList` to get all table names
5. For each table:
   - Invoke `XBase-Record-Delete` with `HardDelete: true` and `Filter: {Field:"IsDeleted", Operator:"=", Value:1}`
   - Record `DeletedCount` for the report
6. Invoke `XBase-Database-Disconnect`
7. Display a per-table summary of rows permanently removed

---

## Error Handling

All errors are surfaced as the XBase error code with plain-English context:

```
Error: XBASE_DATABASE_NOT_FOUND
No database named "inventory" found in XBaseFiles/. Check the name with /this.
```

---

## Dependencies

- `XBase-Database-Connect`, `XBase-Database-Disconnect`
- `XBase-Backup-Verify`, `XBase-Backup-Create`
- `XBase-Index-Rebuild`
- `XBase-Schema-TableList`
- `XBase-Record-Delete`
