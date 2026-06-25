# XBase

XBase is a SQLite-backed database engine accessed entirely through AI Skills. It provides connection management, schema DDL, full CRUD, composite queries, index management, transactions, and backup — each operation as a single slash command.

---

## Architecture

| Layer | Technology |
|---|---|
| Storage engine | SQLite (WAL mode, `PRAGMA journal_mode=WAL`) |
| Foreign key enforcement | `PRAGMA foreign_keys=ON` on every connection |
| Soft deletes | `IsDeleted INTEGER DEFAULT 0` on every table |
| Transactions | `BEGIN IMMEDIATE` by default (prevents SQLITE_BUSY races) |
| Client library | `Microsoft.Data.Sqlite` |

### Implicit Columns

Every table created through XBase automatically receives these columns:

| Column | Type | Notes |
|---|---|---|
| `Id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Prepended unless a PK is explicitly provided |
| `CreatedAt` | `TEXT` | ISO-8601 timestamp; set on insert, never changed |
| `UpdatedAt` | `TEXT` | ISO-8601 timestamp; refreshed on every update |
| `IsDeleted` | `INTEGER DEFAULT 0` | `0` = active, `1` = soft-deleted |

`XBase-Record-Select` automatically appends `AND IsDeleted = 0` to every query unless `IncludeDeleted: true` is passed. `XBase-Record-Delete` sets `IsDeleted = 1` by default; pass `HardDelete: true` for a physical `DELETE`.

### WAL Sidecar Files

SQLite in WAL mode creates two sidecar files alongside the `.db`:

```
AiXBase/myapp.db
AiXBase/myapp.db-shm
AiXBase/myapp.db-wal
```

`XBase-Database-Drop` removes all three. Never delete sidecars manually while a connection is open.

---

## Quick Start

```
# 1. Create and open a database
/XBase-Database-Initialize  DatabasePath:"AiXBase/myapp.db"
/XBase-Database-Connect     DatabasePath:"AiXBase/myapp.db"  ConnectionName:"main"

# 2. Create a table
/XBase-Schema-TableCreate
  ConnectionName:"main"
  TableName:"Products"
  Columns:[
    {"Name":"SKU",   "Type":"TEXT",    "Nullable":false, "Unique":true},
    {"Name":"Label", "Type":"TEXT",    "Nullable":false},
    {"Name":"Price", "Type":"REAL",    "Nullable":true}
  ]

# 3. Insert rows
/XBase-Record-Insert
  ConnectionName:"main"
  TableName:"Products"
  Rows:[
    {"SKU":"A001", "Label":"Widget", "Price":9.99},
    {"SKU":"A002", "Label":"Gadget", "Price":19.99}
  ]

# 4. Query
/XBase-Record-Select
  ConnectionName:"main"
  TableName:"Products"
  Filter:{"Field":"Price", "Operator":"<", "Value":15}
  Sort:[{"Field":"Price", "Direction":"ASC"}]
  Limit:25

# 5. Close
/XBase-Database-Disconnect  ConnectionName:"main"
```

---

## Operation Groups

### Database (4 skills)

| Skill | Purpose |
|---|---|
| `XBase-Database-Initialize` | Create a new `.db` file with WAL mode and FK enforcement |
| `XBase-Database-Connect` | Open an existing database and register it under a named alias |
| `XBase-Database-Disconnect` | Close a named connection (optionally rolling back open transactions) |
| `XBase-Database-Drop` | Delete the `.db` file and all WAL sidecars (`ConfirmDrop: true` required) |

### Schema (5 skills)

| Skill | Purpose |
|---|---|
| `XBase-Schema-TableCreate` | Create a table; implicit Id/audit columns added automatically |
| `XBase-Schema-TableAlter` | Add columns to an existing table |
| `XBase-Schema-TableDrop` | Drop a table (`ConfirmDrop: true` required) |
| `XBase-Schema-TableList` | List all user tables in the database |
| `XBase-Schema-ColumnList` | List columns and their types/constraints for a table |

### Record (5 skills)

| Skill | Purpose |
|---|---|
| `XBase-Record-Insert` | Insert one or more rows; returns `InsertedCount` and `LastInsertedId` |
| `XBase-Record-Select` | Query rows with optional filter, sort, pagination, and column projection |
| `XBase-Record-Update` | Update rows matching a filter; `Filter` is required (no blind mass-updates) |
| `XBase-Record-Delete` | Soft-delete (default) or hard-delete rows matching a filter |
| `XBase-Record-Upsert` | Insert or update based on conflict columns; returns `Action:"inserted"` or `"updated"` |

### Query (5 skills)

These skills compile reusable query components that are passed to `XBase-Record-Select` or `XBase-Query-Execute`.

| Skill | Purpose |
|---|---|
| `XBase-Query-Filter` | Compile a parameterised WHERE clause (supports `=`, `!=`, `<`, `>`, `<=`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`; AND/OR chaining) |
| `XBase-Query-Sort` | Compile an ORDER BY clause |
| `XBase-Query-Join` | Compile a JOIN clause (INNER, LEFT; alias support) |
| `XBase-Query-Aggregate` | Compile a SELECT aggregate (COUNT, SUM, AVG, MIN, MAX; GROUP BY support) |
| `XBase-Query-Execute` | Run arbitrary parameterised SQL; returns rows or affected-row count |

`XBase-Query-Filter` never touches the database — it is a pure compilation step. All values are bound as parameters, never interpolated into SQL text.

### Index (4 skills)

| Skill | Purpose |
|---|---|
| `XBase-Index-Create` | Create a single-column or composite index (optionally UNIQUE) |
| `XBase-Index-Drop` | Drop a named index |
| `XBase-Index-Rebuild` | Run `REINDEX` on a named index, all indexes on a table, or all indexes in the database |
| `XBase-Index-List` | List indexes on a table with column order and uniqueness flag |

### Transaction (4 skills)

| Skill | Purpose |
|---|---|
| `XBase-Transaction-Begin` | Begin a named transaction (`IMMEDIATE` by default) |
| `XBase-Transaction-Commit` | Commit a named transaction |
| `XBase-Transaction-Rollback` | Rollback a named transaction, optionally to a savepoint |
| `XBase-Transaction-Savepoint` | Create a named savepoint within an open transaction |

Pass `TransactionName` to any Record or Query skill to run it inside an open transaction. Changes are invisible to other connections until committed.

### Backup (3 skills)

| Skill | Purpose |
|---|---|
| `XBase-Backup-Create` | Hot-backup a live database to `AiXBase/backups/`; filename includes timestamp and optional label |
| `XBase-Backup-Restore` | Restore a backup over a target database (`ConfirmRestore: true` required; optionally creates a pre-restore snapshot) |
| `XBase-Backup-Verify` | Open the backup read-only and run `PRAGMA integrity_check`; does not require an active connection |

---

## Error Codes

All XBase error codes follow the pattern `XBASE_<CATEGORY>_<REASON>`.

| Category | Example Codes |
|---|---|
| `DATABASE` | `XBASE_DATABASE_NOT_FOUND`, `XBASE_DATABASE_EXISTS`, `XBASE_DATABASE_PATH_INVALID`, `XBASE_DATABASE_CORRUPT` |
| `CONNECTION` | `XBASE_CONNECTION_INVALID`, `XBASE_CONNECTION_NAME_IN_USE` |
| `SCHEMA` | `XBASE_SCHEMA_TABLE_NOT_FOUND`, `XBASE_SCHEMA_TABLE_EXISTS`, `XBASE_SCHEMA_COLUMN_MISSING`, `XBASE_SCHEMA_COLUMN_INVALID`, `XBASE_SCHEMA_COLUMN_EXISTS` |
| `RECORD` | `XBASE_RECORD_CONSTRAINT_VIOLATION`, `XBASE_RECORD_FILTER_REQUIRED` |
| `FILTER` | `XBASE_FILTER_FIELD_INVALID`, `XBASE_FILTER_OPERATOR_UNKNOWN`, `XBASE_FILTER_VALUE_REQUIRED` |
| `QUERY` | `XBASE_QUERY_SYNTAX_ERROR` |
| `INDEX` | `XBASE_INDEX_EXISTS`, `XBASE_INDEX_NOT_FOUND` |
| `TRANSACTION` | `XBASE_TRANSACTION_NOT_OPEN`, `XBASE_TRANSACTION_NAME_IN_USE`, `XBASE_TRANSACTION_ISOLATION_INVALID`, `XBASE_TRANSACTION_STILL_OPEN`, `XBASE_SAVEPOINT_NOT_FOUND`, `XBASE_SAVEPOINT_NAME_IN_USE` |
| `BACKUP` | `XBASE_BACKUP_NOT_FOUND`, `XBASE_BACKUP_CORRUPT` |
| `DROP` | `XBASE_DROP_NOT_CONFIRMED`, `XBASE_RESTORE_NOT_CONFIRMED` |
| `AGGREGATE` | `XBASE_AGGREGATE_FUNCTION_UNKNOWN` |
| `SORT` | `XBASE_SORT_DIRECTION_INVALID`, `XBASE_SORT_FIELD_INVALID` |
| `JOIN` | `XBASE_JOIN_TYPE_INVALID`, `XBASE_JOIN_REFERENCE_INVALID` |

---

## Design Decisions

**Why `BEGIN IMMEDIATE` by default?**
SQLite's default `DEFERRED` mode acquires a write lock only on the first write statement. Under concurrent access this causes `SQLITE_BUSY` errors mid-transaction. `IMMEDIATE` acquires the write lock at `BEGIN`, so a busy error surfaces immediately rather than deep into a multi-step operation.

**Why soft deletes?**
Soft deletes preserve audit history and allow accidental-delete recovery without a separate audit table. Hard deletes are opt-in via `HardDelete: true`.

**Why is `Filter` required for Update and Delete?**
Requiring an explicit filter prevents silent mass-updates or mass-deletes caused by omitting a WHERE clause. If you genuinely need to update all rows, pass `Filter: {"Field": "Id", "Operator": ">", "Value": 0}`.

**Why does `XBase-Query-Filter` touch no database?**
Keeping compilation separate from execution allows filters to be built incrementally and reused across multiple selects without redundant round-trips.
