# Product Requirements Document: XBase

## Overview

XBase is a skill-based, file-backed database engine implemented exclusively through AI Skills. All database interactions — from schema management through record CRUD and transaction control — are exposed as discrete, composable Skills following the naming convention:

```
[Feature Name]-[Feature-Operation]-[Any Subdivision Needed]
```

Example: `XBase-Record-Create`, `XBase-Transaction-Rollback`

Storage engine: SQLite (local `.db` file under `AiXBase/`).

---

## Skill Catalog

### Database Lifecycle

| Skill | Description |
|---|---|
| `XBase-Database-Initialize` | Create a new SQLite database file at a given path |
| `XBase-Database-Connect` | Open an existing database and return a named connection handle |
| `XBase-Database-Disconnect` | Close an open connection handle |
| `XBase-Database-Drop` | Delete a database file entirely |

### Schema Management

| Skill | Description |
|---|---|
| `XBase-Schema-TableCreate` | Define a new table with typed columns and constraints |
| `XBase-Schema-TableAlter` | Add or rename columns on an existing table |
| `XBase-Schema-TableDrop` | Remove a table and all its data |
| `XBase-Schema-TableList` | Return all table names in the connected database |
| `XBase-Schema-ColumnList` | Return column definitions for a given table |

### Record Operations (CRUD)

| Skill | Description |
|---|---|
| `XBase-Record-Insert` | Insert one or more rows into a table |
| `XBase-Record-Select` | Select rows with optional column projection |
| `XBase-Record-Update` | Update rows matching a filter expression |
| `XBase-Record-Delete` | Delete rows matching a filter expression |
| `XBase-Record-Upsert` | Insert a row or update it if a key already exists |

### Query Operations

| Skill | Description |
|---|---|
| `XBase-Query-Filter` | Apply a WHERE-style predicate to a result set |
| `XBase-Query-Sort` | Apply ORDER BY to a result set |
| `XBase-Query-Join` | Combine two tables on a key expression |
| `XBase-Query-Aggregate` | Compute COUNT, SUM, AVG, MIN, MAX over a result set |
| `XBase-Query-Execute` | Run a raw SQL string (escape hatch; prefer typed skills) |

### Index Operations

| Skill | Description |
|---|---|
| `XBase-Index-Create` | Create an index on one or more columns |
| `XBase-Index-Drop` | Drop a named index |
| `XBase-Index-Rebuild` | Rebuild an index (useful after bulk inserts) |
| `XBase-Index-List` | List all indexes on a table |

### Transaction Control

| Skill | Description |
|---|---|
| `XBase-Transaction-Begin` | Begin an explicit transaction on a connection |
| `XBase-Transaction-Commit` | Commit the current transaction |
| `XBase-Transaction-Rollback` | Roll back the current transaction |
| `XBase-Transaction-Savepoint` | Set a named savepoint within a transaction |

### Backup and Restore

| Skill | Description |
|---|---|
| `XBase-Backup-Create` | Copy the database file to a timestamped backup |
| `XBase-Backup-Restore` | Restore database from a named backup |
| `XBase-Backup-Verify` | Validate backup file integrity |

---

## Skill Specifications

### XBase-Database-Initialize

**Inputs**
- `DatabasePath` (string) — relative path under `AiXBase/` for the new `.db` file
- `OverwriteIfExists` (bool, default `false`)

**Outputs**
- `DatabasePath` (string) — resolved absolute path
- `CreatedAt` (ISO-8601 timestamp)

**Behavior**
Creates the SQLite file and runs `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON`.

---

### XBase-Database-Connect

**Inputs**
- `DatabasePath` (string)
- `ConnectionName` (string) — logical alias used by subsequent skills

**Outputs**
- `ConnectionName` (string)
- `IsOpen` (bool)

**Behavior**
Opens the SQLite file in read-write mode. Stores the handle keyed by `ConnectionName` for the session lifetime.

---

### XBase-Schema-TableCreate

**Inputs**
- `ConnectionName` (string)
- `TableName` (string)
- `Columns` (array of `{ Name, Type, Nullable, DefaultValue, PrimaryKey, Unique }`)

**Outputs**
- `TableName` (string)
- `SQL` (string) — the generated DDL statement

**Behavior**
Emits and executes a `CREATE TABLE IF NOT EXISTS` statement. Always adds an `Id` column (INTEGER PRIMARY KEY AUTOINCREMENT) unless one is explicitly supplied.

---

### XBase-Record-Insert

**Inputs**
- `ConnectionName` (string)
- `TableName` (string)
- `Rows` (array of key-value maps)
- `TransactionName` (string, optional)

**Outputs**
- `InsertedCount` (int)
- `LastInsertedId` (int)

---

### XBase-Record-Select

**Inputs**
- `ConnectionName` (string)
- `TableName` (string)
- `Columns` (array of strings, default `["*"]`)
- `Filter` (XBase-Query-Filter expression, optional)
- `Sort` (XBase-Query-Sort expression, optional)
- `Limit` (int, optional)
- `Offset` (int, optional)

**Outputs**
- `Rows` (array of key-value maps)
- `TotalCount` (int) — count without LIMIT/OFFSET

---

### XBase-Query-Filter

**Inputs**
- `Field` (string)
- `Operator` (`=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `IS NULL`, `IS NOT NULL`)
- `Value` (scalar or array for `IN`)
- `LogicalOperator` (`AND` | `OR`, used when chaining multiple filters)

**Outputs**
- Compiled filter expression passed into Record skills

---

### XBase-Transaction-Begin

**Inputs**
- `ConnectionName` (string)
- `TransactionName` (string) — logical alias

**Outputs**
- `TransactionName` (string)
- `StartedAt` (ISO-8601 timestamp)

**Behavior**
Issues `BEGIN IMMEDIATE` to prevent read-then-write races.

---

## Data Model

All tables managed by XBase share these implicit conventions:

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER | Primary key, auto-increment |
| `CreatedAt` | TEXT | ISO-8601, set on insert |
| `UpdatedAt` | TEXT | ISO-8601, set on update |
| `IsDeleted` | INTEGER | Soft-delete flag (0/1) |

---

## Error Handling

Every Skill returns a standardized error envelope when it cannot complete:

```
{
  "Success": false,
  "ErrorCode": "XBASE_<CATEGORY>_<REASON>",
  "Message": "human-readable description",
  "SkillName": "XBase-Record-Insert"
}
```

Common error codes:

| Code | Meaning |
|---|---|
| `XBASE_DATABASE_NOT_FOUND` | Database file does not exist |
| `XBASE_CONNECTION_INVALID` | ConnectionName not open |
| `XBASE_SCHEMA_TABLE_EXISTS` | Table already exists (non-IF NOT EXISTS path) |
| `XBASE_SCHEMA_COLUMN_MISSING` | Referenced column not in table |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | NOT NULL / UNIQUE / FK violation |
| `XBASE_TRANSACTION_NOT_OPEN` | No active transaction for given name |

---

## Dependencies

- SQLite (bundled via `Microsoft.Data.Sqlite` or equivalent)
- No external network dependencies
- All skill inputs and outputs are serializable to JSON
