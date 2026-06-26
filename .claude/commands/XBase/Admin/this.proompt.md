# XBase-Admin-this

Inspect and display the current state of one or all XBase databases.

## Usage

```
/this                          — survey all databases
/this <DatabaseName>           — detailed view of one database
```

---

## Steps

### Mode 1 — Survey (no DatabaseName)

1. List all subdirectories in `XBaseFiles/` that contain `_meta.json` (exclude `backups/` and `_txn_*`)
2. For each database directory:
   a. Read `_meta.json` → extract `Name`, `UpdatedAt`
   b. Read `_schema.json` → count `Tables` entries
   c. For each table, count non-empty lines in `{TableName}.ndjson` where `IsDeleted` ≠ 1 (active rows)
   d. Sum directory size by reading all file sizes
3. Display a formatted summary table:

```
XBase Databases — XBaseFiles/
────────────────────────────────────────────────────
  {Name}    {TableCount} tables    {ActiveRows} rows    {SizeMB} MB    {UpdatedAt}
────────────────────────────────────────────────────
{N} databases
```

4. Note if `XBaseFiles/backups/` exists and how many backup directories it contains

---

### Mode 2 — Detail (DatabaseName provided)

1. Invoke `XBase-Database-Connect` with a temporary alias (e.g. `admin-inspect`)
2. Invoke `XBase-Schema-TableList` → get list of table names
3. For each table:
   a. Invoke `XBase-Schema-ColumnList` → get column definitions
   b. Read `{TableName}.ndjson`:
      - Count lines where `IsDeleted = 0` (or field absent) → active rows
      - Count lines where `IsDeleted = 1` → soft-deleted rows
   c. Invoke `XBase-Index-List` → get indexes for this table
4. Check for any `_txn_*/` directories inside the database directory → pending transactions
5. Check `XBaseFiles/backups/` for directories starting with `{DatabaseName}_` → backup history
6. Display the detailed report:

```
Database: {Name}
Path:     XBaseFiles/{DatabaseName}/
Created:  {CreatedAt from _meta.json}
Updated:  {UpdatedAt from _meta.json}

Tables ({count}):
  {TableName}    {ActiveRows} rows  ({SoftDeleted} soft-deleted)  {ColumnCount} columns  {IndexCount} indexes
  ...

Connections:      {list of open connection aliases or "none"}
Transactions:     {list of _txn_* directory names or "none"}
Backups:          {most recent backup path and timestamp, or "none found"}
```

7. Invoke `XBase-Database-Disconnect` to release the temporary alias

---

## Notes

- This command is **read-only** — it never modifies any file
- If a database directory is missing `_meta.json`, report it as `[corrupt — missing _meta.json]` in the survey
- Soft-deleted rows are counted separately; they are not included in the active-row count
- Index health is reported as present/missing (`.ndx` file exists for each index in `_schema.json`)

---

## Dependencies

- `XBase-Database-Connect`, `XBase-Database-Disconnect`
- `XBase-Schema-TableList`, `XBase-Schema-ColumnList`
- `XBase-Index-List`
