# Product Requirements Document: XBase Testing Criteria

## Overview

This document defines the complete set of acceptance tests, edge-case tests, error-condition tests, performance benchmarks, stress tests, and security tests required to certify that every XBase Skill behaves correctly. A skill is considered **passing** only when every applicable test ID in this document produces the stated expected result.

Test IDs follow the pattern `XBASE-<GROUP>-<NNN>` where group codes are:

| Code | Group |
|---|---|
| `DB` | Database Lifecycle |
| `SCH` | Schema Management |
| `REC` | Record Operations |
| `QRY` | Query Operations |
| `IDX` | Index Operations |
| `TXN` | Transaction Control |
| `BAK` | Backup and Restore |
| `PERF` | Performance Benchmarks |
| `STRESS` | Stress Tests |
| `SEC` | Security Tests |

---

## Test Environment Requirements

| Requirement | Specification |
|---|---|
| SQLite version | ≥ 3.40.0 |
| Available disk space | ≥ 10 GB for performance and stress suites |
| RAM | ≥ 4 GB |
| OS | Windows 10+ or Linux (kernel ≥ 5.15) |
| `data/` directory | Writable, on a local drive (not network share) for baseline perf tests |
| Clock | System clock must be stable; no large jumps during test run |

---

## Test Data Specifications

### Standard Column Set (used across schema tests)

```
Id          INTEGER PRIMARY KEY AUTOINCREMENT
Code        TEXT NOT NULL UNIQUE
Label       TEXT NOT NULL
Value       REAL
IsActive    INTEGER NOT NULL DEFAULT 1
CreatedAt   TEXT
UpdatedAt   TEXT
IsDeleted   INTEGER DEFAULT 0
```

### Data Scale Tiers

| Tier | Row Count | Label |
|---|---|---|
| S | 100 | Small |
| M | 10 000 | Medium |
| L | 100 000 | Large |
| XL | 1 000 000 | Extra-Large |
| XXL | 10 000 000 | Stress |

### Seed Helpers

- **Sequential rows**: `Code = 'CODE-{n}'`, `Label = 'Label {n}'`, `Value = n * 1.23`
- **Unicode rows**: `Label` contains CJK (`测试`), emoji (`🎉`), RTL Arabic (`اختبار`), null-byte–adjacent chars
- **Boundary rows**: one row where every nullable field is NULL; one where every text field is max-length (10 000 chars)

---

## Test Execution Standards

- Each test must set up its own state (create a fresh `data/test-<ID>.db`) and tear it down on completion
- Tests within a group may share a single database only when explicitly noted
- A test **fails** if: wrong output, wrong error code, unhandled exception, or execution time exceeds the stated limit
- Performance tests must be repeated 3 times; the **median** value must meet the target
- All tests must pass with `PRAGMA foreign_keys=ON` and `PRAGMA journal_mode=WAL`

---

## Test Cases: Database Lifecycle

### XBase-Database-Initialize

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-001` | Happy path — new database | `DatabasePath: "test/init.db"`, `OverwriteIfExists: false` | Returns `Success: true`, file exists, WAL mode confirmed via `PRAGMA journal_mode`, FK on confirmed via `PRAGMA foreign_keys` |
| `XBASE-DB-002` | Path in nested non-existent directories | `DatabasePath: "test/a/b/c/init.db"` | Directories created automatically; file exists |
| `XBASE-DB-003` | File already exists, OverwriteIfExists false | Pre-create the file | Returns `XBASE_DATABASE_EXISTS`; original file unchanged |
| `XBASE-DB-004` | File already exists, OverwriteIfExists true | Pre-create file with known content | Returns `Success: true`; original content gone; new file is valid SQLite |
| `XBASE-DB-005` | Path escapes `data/` via traversal | `DatabasePath: "../outside.db"` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-006` | Path with spaces and Unicode | `DatabasePath: "test/my db 测试.db"` | Returns `Success: true`; file created at path with spaces/Unicode |
| `XBASE-DB-007` | Absolute path outside `data/` | `DatabasePath: "C:/Windows/Temp/evil.db"` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-008` | Empty string path | `DatabasePath: ""` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-009` | Path exceeding 260 chars (Windows MAX_PATH) | 261-char path | Returns `XBASE_DATABASE_PATH_INVALID` or OS-level error wrapped in skill error envelope |
| `XBASE-DB-010` | Verify WAL sidecar files created | Normal init | After first write, `.db-shm` and `.db-wal` exist alongside `.db` |
| `XBASE-DB-011` | `CreatedAt` is valid ISO-8601 | Normal init | `CreatedAt` matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}` |
| `XBASE-DB-012` | Concurrent init same path (race) | Two threads call Initialize simultaneously | Exactly one succeeds; the other returns `XBASE_DATABASE_EXISTS` or serialises cleanly |

---

### XBase-Database-Connect

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-013` | Happy path | Valid path, unique `ConnectionName` | `IsOpen: true`; subsequent skills can use this alias |
| `XBASE-DB-014` | File does not exist | Non-existent path | Returns `XBASE_DATABASE_NOT_FOUND` |
| `XBASE-DB-015` | ConnectionName already in use | Same name as open connection | Returns `XBASE_CONNECTION_NAME_IN_USE` |
| `XBASE-DB-016` | Empty ConnectionName | `ConnectionName: ""` | Returns validation error |
| `XBASE-DB-017` | Two connections to same file with different names | `Name1`, `Name2` → same `.db` | Both open successfully; both can read concurrently |
| `XBASE-DB-018` | Connect to a non-SQLite file | Provide a `.txt` file | Returns `XBASE_DATABASE_NOT_FOUND` or `XBASE_DATABASE_CORRUPT` |
| `XBASE-DB-019` | Connect to zero-byte file | Pre-create empty file | Returns appropriate error (SQLite cannot open 0-byte file) |
| `XBASE-DB-020` | ConnectionName with special characters | `ConnectionName: "conn/with:special*chars"` | Handled as opaque alias; success or validation error — must not crash |

---

### XBase-Database-Disconnect

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-021` | Happy path | Open connection | `Success: true`; connection alias deregistered |
| `XBASE-DB-022` | Unknown ConnectionName | Name never opened | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-DB-023` | Open transaction, RollbackOpenTransaction true | Begin txn, then disconnect | Transaction rolled back; connection closed cleanly |
| `XBASE-DB-024` | Open transaction, RollbackOpenTransaction false | Begin txn, then disconnect | Returns `XBASE_TRANSACTION_STILL_OPEN`; connection remains open |
| `XBASE-DB-025` | Disconnect twice | Close, then close again | Second call returns `XBASE_CONNECTION_INVALID` |
| `XBASE-DB-026` | Verify ClosedAt timestamp | Normal disconnect | `ClosedAt` is ISO-8601 and ≥ connect timestamp |

---

### XBase-Database-Drop

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-027` | Happy path | `ConfirmDrop: true`, valid path | `Success: true`; `.db`, `.db-shm`, `.db-wal` all deleted |
| `XBASE-DB-028` | ConfirmDrop false | `ConfirmDrop: false` | Returns `XBASE_DROP_NOT_CONFIRMED`; file intact |
| `XBASE-DB-029` | ConfirmDrop omitted | No `ConfirmDrop` field | Returns `XBASE_DROP_NOT_CONFIRMED` |
| `XBASE-DB-030` | File does not exist | Non-existent path | Returns `XBASE_DATABASE_NOT_FOUND` |
| `XBASE-DB-031` | Drop with open connections | Two connections open | Both closed (with rollback); file deleted |
| `XBASE-DB-032` | Drop with active write transaction | Transaction open | Transaction rolled back; file deleted |
| `XBASE-DB-033` | WAL sidecars cleaned up | DB with in-flight WAL | All three files removed; no orphaned sidecars |

---

## Test Cases: Schema Management

### XBase-Schema-TableCreate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-001` | Happy path — standard columns | Standard column set | `Success: true`; `PRAGMA table_info` confirms all columns |
| `XBASE-SCH-002` | Implicit Id column injected | No `PrimaryKey` column supplied | `Id INTEGER PRIMARY KEY AUTOINCREMENT` prepended |
| `XBASE-SCH-003` | Explicit primary key honoured | Column with `PrimaryKey: true` | No implicit `Id` added; user PK used |
| `XBASE-SCH-004` | Implicit audit columns appended | No `CreatedAt/UpdatedAt/IsDeleted` in input | Three columns appended automatically |
| `XBASE-SCH-005` | IfNotExists true (default) — table exists | Call twice | Second call returns `Success: true`; no error; table unchanged |
| `XBASE-SCH-006` | IfNotExists false — table exists | `IfNotExists: false`, table pre-exists | Returns `XBASE_SCHEMA_TABLE_EXISTS` |
| `XBASE-SCH-007` | Table with 100 columns | 100 column definitions | All 100 columns present in `PRAGMA table_info` |
| `XBASE-SCH-008` | Column name is SQL reserved word | `Name: "Order"` | Column created with proper quoting; no SQL error |
| `XBASE-SCH-009` | Column name with spaces | `Name: "My Column"` | Created with quoting; accessible via quoted name |
| `XBASE-SCH-010` | Column name with Unicode | `Name: "列名"` | Created and accessible |
| `XBASE-SCH-011` | NOT NULL column, no default | `Nullable: false`, no `DefaultValue` | Insert without that column returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-SCH-012` | UNIQUE column | `Unique: true` | Duplicate insert returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-SCH-013` | Foreign key column | `ForeignKey: "Statuses.Id"` | `PRAGMA foreign_key_list` confirms FK; violation raises constraint error |
| `XBASE-SCH-014` | All SQLite types | One column each of INTEGER, TEXT, REAL, BLOB, NUMERIC | All created; type affinity confirmed via `PRAGMA table_info` |
| `XBASE-SCH-015` | Empty Columns array | `Columns: []` | Returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `XBASE-SCH-016` | Duplicate column names | Two columns both named `Name` | Returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `XBASE-SCH-017` | Table name with special characters | `TableName: "My Table!"` | Returns validation error (table names must be safe identifiers) |
| `XBASE-SCH-018` | Generated SQL returned | Any valid call | `SQL` field in output matches the DDL that was executed |

---

### XBase-Schema-TableAlter

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-019` | Add single column | `AddColumns: [{Name:"Score", Type:"REAL"}]` | Column present in `PRAGMA table_info`; existing rows have `Score = NULL` |
| `XBASE-SCH-020` | Add multiple columns at once | Three column definitions | All three added |
| `XBASE-SCH-021` | Add column that already exists | Existing column name | Returns `XBASE_SCHEMA_COLUMN_EXISTS` |
| `XBASE-SCH-022` | Table does not exist | Non-existent table name | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-SCH-023` | Add NOT NULL column to populated table | Existing table has rows, new column has no default | SQLite disallows this; returns appropriate error |
| `XBASE-SCH-024` | Add NOT NULL column with default | `Nullable: false`, `DefaultValue: "0"` | Column added; existing rows get default value |
| `XBASE-SCH-025` | Empty AddColumns array | `AddColumns: []` | Returns `Success: true` with `AddedColumns: []` (no-op) |

---

### XBase-Schema-TableDrop

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-026` | Happy path | `ConfirmDrop: true` | Table gone; `XBase-Schema-TableList` does not include it |
| `XBASE-SCH-027` | ConfirmDrop false | `ConfirmDrop: false` | Returns `XBASE_DROP_NOT_CONFIRMED`; table intact |
| `XBASE-SCH-028` | Table does not exist, IfExists true | Non-existent table | Returns `Success: true` (no-op) |
| `XBASE-SCH-029` | Table does not exist, IfExists false | `IfExists: false` | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-SCH-030` | Drop referenced table (FK violation) | Table referenced by another via FK | SQLite raises FK constraint error when `foreign_keys=ON`; skill wraps as error |
| `XBASE-SCH-031` | Drop table with rows | Table with L-tier data | All rows gone; no error |

---

### XBase-Schema-TableList

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-032` | Empty database | Freshly initialised DB | `Tables: []` |
| `XBASE-SCH-033` | Multiple tables | Create 5 tables | All 5 names returned, sorted alphabetically |
| `XBASE-SCH-034` | SQLite internal tables excluded | Normal database | `sqlite_sequence`, `sqlite_master` not in results |
| `XBASE-SCH-035` | Tables created then dropped | Drop 2 of 5 | Only 3 remain |

---

### XBase-Schema-ColumnList

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-036` | Happy path | Standard column set | Returns all columns with correct `Type`, `Nullable`, `DefaultValue`, `PrimaryKey` |
| `XBASE-SCH-037` | Table with no nullable columns | All `NOT NULL` | All `Nullable: false` |
| `XBASE-SCH-038` | Table does not exist | Non-existent name | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-SCH-039` | Column with DEFAULT value | Column has `DefaultValue: '42'` | `DefaultValue` field reflects the literal |
| `XBASE-SCH-040` | Composite PK | Two-column primary key | Both columns show `PrimaryKey: true` |

---

## Test Cases: Record Operations

### XBase-Record-Insert

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-001` | Single row | One `{ Code: "A", Label: "Alpha" }` | `InsertedCount: 1`; `LastInsertedId` matches DB `last_insert_rowid()` |
| `XBASE-REC-002` | Bulk insert | 1 000 rows | `InsertedCount: 1000`; all rows present |
| `XBASE-REC-003` | Auto-set CreatedAt | No `CreatedAt` in input | Row has valid ISO-8601 `CreatedAt` |
| `XBASE-REC-004` | Auto-set UpdatedAt | No `UpdatedAt` in input | Row has valid ISO-8601 `UpdatedAt` = `CreatedAt` on insert |
| `XBASE-REC-005` | NOT NULL violation | Omit required field | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-006` | UNIQUE violation | Two rows, same unique field | Second insert returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-007` | FK violation | FK column pointing to non-existent parent | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-008` | NULL value for nullable column | `{ Code: "B", Label: null }` | Row inserted with `Label = NULL` |
| `XBASE-REC-009` | Empty string vs NULL | `{ Label: "" }` | Row inserted with `Label = ""` (not NULL) |
| `XBASE-REC-010` | Integer 0 vs NULL | `{ Value: 0 }` | Row inserted with `Value = 0` (not NULL) |
| `XBASE-REC-011` | Text with single quotes | `{ Label: "it's a test" }` | Inserted correctly; no SQL error; retrieved value matches |
| `XBASE-REC-012` | Text with double quotes and backslashes | `{ Label: "say \"hello\" \\n" }` | Inserted and retrieved correctly |
| `XBASE-REC-013` | Unicode and emoji | `{ Label: "测试 🎉" }` | Stored and retrieved without corruption |
| `XBASE-REC-014` | Very long TEXT (10 000 chars) | `{ Label: "x" * 10000 }` | Stored and retrieved; `InsertedCount: 1` |
| `XBASE-REC-015` | BLOB data | Binary column with 1 MB payload | Stored and retrieved byte-for-byte identical |
| `XBASE-REC-016` | Float precision | `{ Value: 1.234567890123456789 }` | Stored as REAL (64-bit IEEE 754); retrieved within float tolerance |
| `XBASE-REC-017` | Insert empty Rows array | `Rows: []` | `InsertedCount: 0`; `Success: true` (no-op) |
| `XBASE-REC-018` | Unknown column in row | `{ Bogus: "x" }` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-REC-019` | Table does not exist | Non-existent table | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-REC-020` | Connection invalid | Closed connection name | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-REC-021` | Insert within transaction | `TransactionName` supplied | Row visible within transaction; not visible to second connection before commit |
| `XBASE-REC-022` | TransactionName not open | Random transaction name | Returns `XBASE_TRANSACTION_NOT_OPEN` |

---

### XBase-Record-Select

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-023` | All rows, all columns | No Filter, Columns `["*"]` | Returns all rows; `TotalCount` matches row count |
| `XBASE-REC-024` | Column projection | `Columns: ["Id", "Label"]` | Only those two columns in each row |
| `XBASE-REC-025` | Filter applied | Filter `Code = 'CODE-1'` | Returns exactly 1 row |
| `XBASE-REC-026` | Filter — no matching rows | Filter `Code = 'NONE'` | `Rows: []`, `TotalCount: 0` |
| `XBASE-REC-027` | Sort ascending | `Sort: [{Field:"Label", Direction:"ASC"}]` | Rows in alphabetical order |
| `XBASE-REC-028` | Sort descending | `Sort: [{Field:"Value", Direction:"DESC"}]` | Rows in reverse numeric order |
| `XBASE-REC-029` | Multi-column sort | `Sort: [{Field:"IsActive"},{Field:"Label"}]` | Primary sort on IsActive, secondary on Label |
| `XBASE-REC-030` | Pagination — page 1 | `Limit: 10, Offset: 0` | 10 rows; `TotalCount` = total rows |
| `XBASE-REC-031` | Pagination — last page (partial) | M-tier table, `Limit: 10, Offset: 9995` | 5 rows returned |
| `XBASE-REC-032` | Offset beyond row count | `Offset: 99999` on S-tier table | `Rows: []`; `TotalCount` = actual count |
| `XBASE-REC-033` | Limit 0 | `Limit: 0` | `Rows: []`; `TotalCount` = actual count |
| `XBASE-REC-034` | Soft-deleted rows excluded by default | Insert + soft-delete a row | Row absent without `IncludeDeleted`; present with it |
| `XBASE-REC-035` | Unknown column in projection | `Columns: ["Bogus"]` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-REC-036` | Table does not exist | Non-existent table | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-REC-037` | NULL values in rows | Rows with NULL fields | NULL preserved in output; not coerced to empty string or 0 |
| `XBASE-REC-038` | Sort on NULL values | Column with NULLs, ASC sort | NULLs sort as SQLite default (NULLS FIRST for ASC) |
| `XBASE-REC-039` | TotalCount accurate with filter + limit | L-tier data, filter returns 500 rows, Limit 10 | `TotalCount: 500`, `Rows.length: 10` |

---

### XBase-Record-Update

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-040` | Single row update | Filter `Id = 1`, `Values: {Label:"New"}` | `UpdatedCount: 1`; row has new value |
| `XBASE-REC-041` | Multi-row update | Filter `IsActive = 0` on 50-row set | `UpdatedCount: 50` |
| `XBASE-REC-042` | No matching rows | Filter `Code = 'NONE'` | `UpdatedCount: 0`; no error |
| `XBASE-REC-043` | Auto-set UpdatedAt | No `UpdatedAt` in Values | `UpdatedAt` updated to now; `CreatedAt` unchanged |
| `XBASE-REC-044` | Empty Filter rejected | No Filter supplied | Returns `XBASE_RECORD_FILTER_REQUIRED` |
| `XBASE-REC-045` | Empty Values | `Values: {}` | Returns validation error or `UpdatedCount: 0` no-op |
| `XBASE-REC-046` | UNIQUE violation on update | Set a field to a value that duplicates another row | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-047` | NOT NULL violation | Set a NOT NULL field to NULL | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-048` | Update within transaction | `TransactionName` supplied | Update visible in same transaction; not committed to DB until Commit |
| `XBASE-REC-049` | Unknown column in Values | `Values: {Bogus: 1}` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |

---

### XBase-Record-Delete

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-050` | Soft delete (default) | Filter `Id = 1` | `IsDeleted = 1` on that row; row still in DB |
| `XBASE-REC-051` | Hard delete | `HardDelete: true` | Row physically removed |
| `XBASE-REC-052` | Soft delete already soft-deleted | `IsDeleted` already 1 | `DeletedCount: 1`; UpdatedAt refreshed (idempotent) |
| `XBASE-REC-053` | No matching rows | Filter on non-existent value | `DeletedCount: 0`; no error |
| `XBASE-REC-054` | Empty Filter rejected | No Filter | Returns `XBASE_RECORD_FILTER_REQUIRED` |
| `XBASE-REC-055` | Bulk soft-delete | Filter covers L-tier subset (10 000 rows) | All 10 000 flagged; DB row count unchanged |
| `XBASE-REC-056` | Hard delete with FK child rows | Parent row has FK children | Returns FK constraint error (with `foreign_keys=ON`) |

---

### XBase-Record-Upsert

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-057` | Insert path | Row not present | `Action: "inserted"`, row in DB |
| `XBASE-REC-058` | Update path | Row with same conflict key exists | `Action: "updated"`, `UpdatedAt` refreshed |
| `XBASE-REC-059` | Idempotent — same row twice | Upsert same data twice | Second call: `Action: "updated"`; row unchanged logically |
| `XBASE-REC-060` | Multiple conflict columns | `ConflictColumns: ["TicketId", "Tag"]` | Both paths work correctly |
| `XBASE-REC-061` | CreatedAt preserved on update | Row pre-exists with `CreatedAt = T1` | After upsert, `CreatedAt` still `T1`; only `UpdatedAt` changes |
| `XBASE-REC-062` | ConflictColumns not found in table | `ConflictColumns: ["Bogus"]` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-REC-063` | Non-conflict constraint violation | Update path triggers NOT NULL violation | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |

---

## Test Cases: Query Operations

### XBase-Query-Filter

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-001` | Equals | `Field:"Code", Operator:"=", Value:"A"` | Compiled filter; used in Select returns 1 row |
| `XBASE-QRY-002` | Not equals | `Operator:"!="` | All rows except matching |
| `XBASE-QRY-003` | Less than / Greater than | `Operator:"<"` and `">"` on REAL column | Correct boundary rows returned |
| `XBASE-QRY-004` | Less than or equal / Greater than or equal | `"<="` and `">="` | Boundary row included |
| `XBASE-QRY-005` | LIKE — prefix | `Value:"CODE-%"` | Matches all CODE-* rows |
| `XBASE-QRY-006` | LIKE — suffix | `Value:"%test"` | Matches suffix correctly |
| `XBASE-QRY-007` | LIKE — contains | `Value:"%middle%"` | Full-scan match |
| `XBASE-QRY-008` | LIKE — case sensitivity | SQLite LIKE is case-insensitive for ASCII | `%code%` matches `CODE` |
| `XBASE-QRY-009` | IN — multiple values | `Value:["A","B","C"]` | Exactly those 3 rows |
| `XBASE-QRY-010` | IN — single value | `Value:["A"]` | One row |
| `XBASE-QRY-011` | IN — empty array | `Value:[]` | Returns `XBASE_FILTER_VALUE_REQUIRED` |
| `XBASE-QRY-012` | IN — 1 000 items | Array of 1 000 values | Handled without hitting SQLite variable limit (SQLITE_LIMIT_VARIABLE_NUMBER default 999) — batched if needed |
| `XBASE-QRY-013` | NOT IN | `Operator:"NOT IN"` | All rows not in array |
| `XBASE-QRY-014` | IS NULL | `Operator:"IS NULL"`, `Value` omitted | Only NULL rows returned |
| `XBASE-QRY-015` | IS NOT NULL | `Operator:"IS NOT NULL"` | Only non-NULL rows |
| `XBASE-QRY-016` | Chain AND | Two filters, `LogicalOperator:"AND"` | Intersection |
| `XBASE-QRY-017` | Chain OR | Two filters, `LogicalOperator:"OR"` | Union |
| `XBASE-QRY-018` | Nested filter groups | `Filters` array with sub-filters | Correct precedence `(A AND B) OR C` |
| `XBASE-QRY-019` | Field with injection attempt | `Field:"Id; DROP TABLE Users--"` | Returns `XBASE_FILTER_FIELD_INVALID` |
| `XBASE-QRY-020` | Unknown operator | `Operator:"BETWEEN"` | Returns `XBASE_FILTER_OPERATOR_UNKNOWN` |
| `XBASE-QRY-021` | Value required but missing | Operator `=` with no `Value` | Returns `XBASE_FILTER_VALUE_REQUIRED` |
| `XBASE-QRY-022` | Value is integer | `Operator:"=", Value:42` (integer, not string) | Correctly bound as integer parameter |
| `XBASE-QRY-023` | Value is float | `Value:3.14` | Correctly bound as REAL |
| `XBASE-QRY-024` | Value is boolean | `Value:true` → bound as `1` | SQLite receives integer 1 |

---

### XBase-Query-Sort

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-025` | Single column ASC | `[{Field:"Label", Direction:"ASC"}]` | Ascending order |
| `XBASE-QRY-026` | Single column DESC | `Direction:"DESC"` | Descending order |
| `XBASE-QRY-027` | Default direction | `Direction` omitted | Defaults to `ASC` |
| `XBASE-QRY-028` | Multi-column sort | Two columns | Primary/secondary sort applied |
| `XBASE-QRY-029` | Invalid direction | `Direction:"SIDEWAYS"` | Returns `XBASE_SORT_DIRECTION_INVALID` |
| `XBASE-QRY-030` | Field with injection | `Field:"Id; --"` | Returns `XBASE_SORT_FIELD_INVALID` |
| `XBASE-QRY-031` | Empty Columns array | `Columns:[]` | Returns validation error |
| `XBASE-QRY-032` | Sort on NULL-containing column | Mix of NULL and non-NULL | NULLs sort per SQLite default; no crash |

---

### XBase-Query-Join

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-033` | INNER JOIN — matching rows | Tickets JOIN Statuses on StatusId=Id | Only tickets with a matching status returned |
| `XBASE-QRY-034` | LEFT JOIN — no match | Ticket with NULL StatusId (if allowed) | Ticket row present, Status columns NULL |
| `XBASE-QRY-035` | Join with alias | `Alias:"s"` | Compiled SQL uses alias; no ambiguous column errors |
| `XBASE-QRY-036` | Invalid JoinType | `JoinType:"BANANA"` | Returns `XBASE_JOIN_TYPE_INVALID` |
| `XBASE-QRY-037` | Malformed OnLeft | `OnLeft:"Tickets..StatusId"` | Returns `XBASE_JOIN_REFERENCE_INVALID` |
| `XBASE-QRY-038` | Multiple joins chained | Three joins in sequence | All three applied correctly |
| `XBASE-QRY-039` | Self-join | Same table joined to itself with different aliases | Returns valid results |

---

### XBase-Query-Aggregate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-040` | COUNT(*) | `Function:"COUNT", Column:"*"` | Returns total row count |
| `XBASE-QRY-041` | COUNT on column with NULLs | Column has 10 NULLs, 90 values | COUNT returns 90 (NULLs excluded) |
| `XBASE-QRY-042` | SUM | `Function:"SUM", Column:"Value"` | Correct numeric sum |
| `XBASE-QRY-043` | AVG | `Function:"AVG"` | Correct average; float result |
| `XBASE-QRY-044` | MIN / MAX | Both functions | Correct boundary values |
| `XBASE-QRY-045` | Aggregate on empty table | No rows | COUNT = 0; SUM/AVG/MIN/MAX = NULL (not crash) |
| `XBASE-QRY-046` | GROUP BY single column | `GroupBy:["IsActive"]` | Two result groups (0 and 1) with correct counts |
| `XBASE-QRY-047` | GROUP BY with filter | Filter + GroupBy | Filter applied before grouping |
| `XBASE-QRY-048` | GROUP BY high-cardinality column | Group by unique column on L-tier | Returns L rows (one per group); no timeout |
| `XBASE-QRY-049` | Multiple aggregates | COUNT + SUM in one call | Both returned in same result row |
| `XBASE-QRY-050` | Unknown function | `Function:"MEDIAN"` | Returns `XBASE_AGGREGATE_FUNCTION_UNKNOWN` |
| `XBASE-QRY-051` | Alias used in output | `Alias:"TicketCount"` | Result field named `TicketCount` |

---

### XBase-Query-Execute

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-052` | SELECT statement | `SQL:"SELECT * FROM Users"` | Returns `Rows` array |
| `XBASE-QRY-053` | INSERT statement | `SQL:"INSERT INTO ..."` | Returns `AffectedRows: 1`, `LastInsertedId` |
| `XBASE-QRY-054` | UPDATE statement | `SQL:"UPDATE ..."` | Returns `AffectedRows` |
| `XBASE-QRY-055` | DELETE statement | `SQL:"DELETE ..."` | Returns `AffectedRows` |
| `XBASE-QRY-056` | CREATE TABLE statement | `SQL:"CREATE TABLE ..."` | `Success: true` |
| `XBASE-QRY-057` | Parameterized query | `SQL:"SELECT * FROM t WHERE Id = ?"`, `Parameters:[1]` | Row returned; no injection possible |
| `XBASE-QRY-058` | Syntax error | Invalid SQL | Returns `XBASE_QUERY_SYNTAX_ERROR` with SQLite message |
| `XBASE-QRY-059` | Empty SQL | `SQL:""` | Returns `XBASE_QUERY_SYNTAX_ERROR` |
| `XBASE-QRY-060` | Parameter count mismatch | Two `?` but one Parameter | Returns error |
| `XBASE-QRY-061` | Multiple statements | `SQL:"SELECT 1; SELECT 2"` | Only first statement executed (SQLite `sqlite3_prepare_v2` behaviour); caller warned |
| `XBASE-QRY-062` | PRAGMA execution | `SQL:"PRAGMA integrity_check"` | Returns as Rows |

---

## Test Cases: Index Operations

### XBase-Index-Create

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-001` | Single column index | `Columns:["StatusId"]` | Index in `PRAGMA index_list` |
| `XBASE-IDX-002` | Composite index | `Columns:["StatusId","CreatedAt"]` | Both columns in `PRAGMA index_info` |
| `XBASE-IDX-003` | UNIQUE index | `Unique: true` | Duplicate value in indexed column returns constraint error |
| `XBASE-IDX-004` | IfNotExists true (default) — index exists | Call twice | Second call succeeds; index unchanged |
| `XBASE-IDX-005` | IfNotExists false — index exists | `IfNotExists: false`, index pre-exists | Returns `XBASE_INDEX_EXISTS` |
| `XBASE-IDX-006` | Non-existent table | Random table name | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-IDX-007` | Non-existent column | `Columns:["Bogus"]` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-IDX-008` | Index on all columns (wide) | 10-column composite | Created; query planner may not use it — but creation succeeds |
| `XBASE-IDX-009` | Generated SQL returned | Any valid call | `SQL` matches executed DDL |

---

### XBase-Index-Drop

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-010` | Happy path | Existing index name | Removed from `PRAGMA index_list` |
| `XBASE-IDX-011` | IfExists true — index not found | `IfExists: true`, no such index | `Success: true` (no-op) |
| `XBASE-IDX-012` | IfExists false — index not found | `IfExists: false` | Returns `XBASE_INDEX_NOT_FOUND` |
| `XBASE-IDX-013` | Drop auto-created PK index | SQLite implicit rowid index | Should return error; implicit indexes are not droppable |

---

### XBase-Index-Rebuild

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-014` | Rebuild named index | Valid `IndexName` | `RebuiltIndexes: ["<name>"]`; integrity check passes |
| `XBASE-IDX-015` | Rebuild all on table | `TableName` provided, no `IndexName` | All indexes on that table listed in output |
| `XBASE-IDX-016` | Rebuild all in database | Neither `IndexName` nor `TableName` | All user indexes rebuilt |
| `XBASE-IDX-017` | Table with no indexes | `TableName` pointing to unindexed table | `RebuiltIndexes: []`; no error |
| `XBASE-IDX-018` | Non-existent index | `IndexName:"bogus"` | Returns `XBASE_INDEX_NOT_FOUND` |
| `XBASE-IDX-019` | Non-existent table | `TableName:"bogus"` | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |

---

### XBase-Index-List

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-020` | Table with no indexes | Unindexed table | `Indexes: []` |
| `XBASE-IDX-021` | Table with multiple indexes | Create 3 indexes | All 3 returned with correct `Columns` and `Unique` flag |
| `XBASE-IDX-022` | UNIQUE index flagged | Index created with `Unique: true` | `Unique: true` in output |
| `XBASE-IDX-023` | Table does not exist | Non-existent table | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-IDX-024` | Composite index columns in order | Two-column index | `Columns` array reflects correct column order |

---

## Test Cases: Transaction Control

### XBase-Transaction-Begin

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-001` | Happy path — IMMEDIATE | `IsolationLevel:"IMMEDIATE"` | `Success: true`; `StartedAt` is ISO-8601 |
| `XBASE-TXN-002` | DEFERRED isolation | `IsolationLevel:"DEFERRED"` | Transaction opened; write acquires lock on first write |
| `XBASE-TXN-003` | EXCLUSIVE isolation | `IsolationLevel:"EXCLUSIVE"` | Transaction opened; no other connection can read |
| `XBASE-TXN-004` | Default isolation is IMMEDIATE | `IsolationLevel` omitted | Behaves as IMMEDIATE |
| `XBASE-TXN-005` | TransactionName already in use | Same name twice | Returns `XBASE_TRANSACTION_NAME_IN_USE` |
| `XBASE-TXN-006` | Invalid isolation level | `IsolationLevel:"SNAPSHOT"` | Returns `XBASE_TRANSACTION_ISOLATION_INVALID` |
| `XBASE-TXN-007` | Connection invalid | Closed connection | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-TXN-008` | Second transaction on same connection | SQLite allows only one write txn per connection | Returns error; not silently ignored |

---

### XBase-Transaction-Commit

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-009` | Happy path | Open transaction, insert row, commit | Row visible to second connection after commit |
| `XBASE-TXN-010` | Commit deregisters name | After commit, same name available to reuse | Can begin again with same `TransactionName` |
| `XBASE-TXN-011` | Commit with no open transaction | Random name | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-012` | Commit empty transaction (no writes) | Begin + commit, no ops | `Success: true`; no error |
| `XBASE-TXN-013` | CommittedAt timestamp | Normal commit | `CommittedAt` ≥ `StartedAt` |

---

### XBase-Transaction-Rollback

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-014` | Full rollback | Insert row in txn, rollback | Row absent from DB |
| `XBASE-TXN-015` | Rollback deregisters name | After rollback, name reusable | New begin succeeds |
| `XBASE-TXN-016` | Rollback with no open transaction | Random name | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-017` | Rollback to savepoint | Create savepoint after insert A; insert B; rollback to savepoint | A present, B absent; transaction still open |
| `XBASE-TXN-018` | Rollback to non-existent savepoint | `ToSavepoint:"ghost"` | Returns `XBASE_SAVEPOINT_NOT_FOUND` |
| `XBASE-TXN-019` | RolledBackTo field | Full rollback | `RolledBackTo:"full"` |
| `XBASE-TXN-020` | RolledBackTo savepoint name | Savepoint rollback | `RolledBackTo:"<savepoint name>"` |

---

### XBase-Transaction-Savepoint

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-021` | Create savepoint | `SavepointName:"sp1"` | `Success: true`; subsequent rollback to `sp1` works |
| `XBASE-TXN-022` | Multiple savepoints | `sp1`, `sp2`, `sp3` in sequence | Each can be rolled back to independently |
| `XBASE-TXN-023` | Duplicate savepoint name | `sp1` twice | Returns `XBASE_SAVEPOINT_NAME_IN_USE` |
| `XBASE-TXN-024` | No active transaction | Random TransactionName | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-025` | Savepoint after commit | TransactionName committed, then savepoint | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-026` | Release savepoint (commit partial) | Commit to savepoint, leaving outer txn open | Changes within savepoint permanent; outer txn continues |

---

## Test Cases: Backup and Restore

### XBase-Backup-Create

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-BAK-001` | Happy path | Open connection, no label | File in `data/backups/`; name matches `<db>_<timestamp>.db` |
| `XBASE-BAK-002` | With label | `BackupLabel:"pre-migration"` | Filename ends with `_pre-migration.db` |
| `XBASE-BAK-003` | Backup is valid SQLite | After backup | `PRAGMA integrity_check` on backup returns `ok` |
| `XBASE-BAK-004` | Backup during active transaction | Transaction open with uncommitted writes | Backup reflects committed state only (not uncommitted writes) |
| `XBASE-BAK-005` | `data/backups/` auto-created | Directory does not exist | Directory created; backup written |
| `XBASE-BAK-006` | Two backups same second | Called twice within same second | Unique filenames (suffix counter or milliseconds) |
| `XBASE-BAK-007` | Connection invalid | Closed connection | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-BAK-008` | Backup of XL-tier database | 1M-row database | Completes; backup file size within 10% of source |

---

### XBase-Backup-Restore

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-BAK-009` | Happy path with pre-restore snapshot | `ConfirmRestore: true`, `CreateBackupBeforeRestore: true` | `PreRestoreBackupPath` present; target DB reflects backup state |
| `XBASE-BAK-010` | Without pre-restore snapshot | `CreateBackupBeforeRestore: false` | `PreRestoreBackupPath: null`; target overwritten |
| `XBASE-BAK-011` | ConfirmRestore false | `ConfirmRestore: false` | Returns `XBASE_RESTORE_NOT_CONFIRMED` |
| `XBASE-BAK-012` | ConfirmRestore omitted | No field | Returns `XBASE_RESTORE_NOT_CONFIRMED` |
| `XBASE-BAK-013` | Backup file not found | Non-existent path | Returns `XBASE_BACKUP_NOT_FOUND` |
| `XBASE-BAK-014` | Connection reopened after restore | Target connection | Connection is valid and returns rows from restored state |
| `XBASE-BAK-015` | Restore to different database path | `TargetConnectionName` points to DB B, backup from DB A | DB B now contains DB A's data |
| `XBASE-BAK-016` | Restore with active write transaction on target | Transaction open | Transaction rolled back; restore proceeds |

---

### XBase-Backup-Verify

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-BAK-017` | Valid backup | Good backup file | `IntegrityOk: true`, `Issues: []` |
| `XBASE-BAK-018` | Corrupt backup | Manually truncate backup file | `IntegrityOk: false`; `Issues` non-empty |
| `XBASE-BAK-019` | Non-existent file | Random path | Returns `XBASE_BACKUP_NOT_FOUND` |
| `XBASE-BAK-020` | Non-SQLite file | Provide a `.txt` file | Returns `XBASE_BACKUP_CORRUPT` |
| `XBASE-BAK-021` | Zero-byte file | Empty file | Returns `XBASE_BACKUP_CORRUPT` |
| `XBASE-BAK-022` | Verify does not require open connection | No `ConnectionName` input | Opens own read-only handle; `Success: true` |
| `XBASE-BAK-023` | Does not modify backup | Before and after checksums match | File bytes identical pre- and post-verify |

---

## Performance Benchmarks

All benchmarks use a dedicated `data/perf.db`, freshly initialised with WAL mode. Median of 3 runs must meet target. Transactions are used where noted.

### Insert Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-001` | Single-row inserts, auto-commit | 1 000 rows, one call each | ≥ 500 rows/sec |
| `XBASE-PERF-002` | Bulk insert, single transaction | 100 000 rows in one `XBase-Record-Insert` call | ≤ 10 s total |
| `XBASE-PERF-003` | Bulk insert, single transaction | 1 000 000 rows in batches of 10 000 | ≤ 120 s total (≥ 8 000 rows/sec) |
| `XBASE-PERF-004` | Insert throughput: auto-commit vs single txn | 10 000 rows | Single-txn ≥ 10× faster than auto-commit |

### Select Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-005` | Full table scan, no index | L-tier (100 000 rows), `SELECT *` | ≤ 500 ms |
| `XBASE-PERF-006` | Full table scan | XL-tier (1 000 000 rows), `SELECT *` | ≤ 5 s |
| `XBASE-PERF-007` | Point lookup, no index | XL-tier, filter on non-indexed column | ≤ 2 s |
| `XBASE-PERF-008` | Point lookup, with index | XL-tier, filter on indexed column | ≤ 50 ms |
| `XBASE-PERF-009` | Range scan, with index | XL-tier, filter `Id BETWEEN 1 AND 10000` | ≤ 100 ms |
| `XBASE-PERF-010` | Paginated select | XL-tier, `LIMIT 25 OFFSET 500000` | ≤ 500 ms |
| `XBASE-PERF-011` | Projection (2 columns) vs SELECT * | XL-tier | Projection ≤ 60% of SELECT * time |

### Update / Delete Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-012` | Bulk update (soft delete flag) | Update 100 000 rows in one transaction | ≤ 5 s |
| `XBASE-PERF-013` | Bulk hard delete | Delete 100 000 rows in one transaction | ≤ 5 s |
| `XBASE-PERF-014` | Update single indexed row | XL-tier, filter by indexed PK | ≤ 10 ms |

### Aggregate Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-015` | COUNT(*) | XL-tier | ≤ 200 ms |
| `XBASE-PERF-016` | SUM on REAL column | XL-tier | ≤ 200 ms |
| `XBASE-PERF-017` | GROUP BY low-cardinality column | XL-tier, 4 distinct values | ≤ 500 ms |
| `XBASE-PERF-018` | GROUP BY high-cardinality column | XL-tier, 1 000 distinct values | ≤ 2 s |
| `XBASE-PERF-019` | JOIN aggregate | XL-tier Tickets × 4-row Statuses, COUNT by Status | ≤ 1 s |

### Index Impact

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-020` | Create index on XL-tier table | 1M rows, single column | ≤ 30 s |
| `XBASE-PERF-021` | Create composite index | 1M rows, two columns | ≤ 45 s |
| `XBASE-PERF-022` | Rebuild index, XL-tier | After bulk insert without index | ≤ 45 s |
| `XBASE-PERF-023` | Query speedup with index | Before/after index on filter column, XL-tier | ≥ 20× faster with index |

### Transaction Overhead

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-024` | Begin + Commit, empty | 10 000 cycles | ≤ 5 s total |
| `XBASE-PERF-025` | Savepoint creation | 1 000 savepoints in one transaction | ≤ 1 s |
| `XBASE-PERF-026` | Rollback of large transaction | 100 000 inserts then rollback | Rollback ≤ 10 s |

### Backup Performance

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-027` | Backup L-tier database | 100 000 rows | ≤ 5 s |
| `XBASE-PERF-028` | Backup XL-tier database | 1 000 000 rows | ≤ 60 s |
| `XBASE-PERF-029` | Restore XL-tier backup | 1 000 000 rows | ≤ 60 s |
| `XBASE-PERF-030` | Verify XL-tier backup | 1 000 000 rows | ≤ 30 s |

---

## Stress Tests

| ID | Description | Setup | Pass Criterion |
|---|---|---|---|
| `XBASE-STRESS-001` | Sustained insert load | Insert 10 000 000 rows in batches of 10 000, single connection | No crash; final row count = 10M; `PRAGMA integrity_check` passes |
| `XBASE-STRESS-002` | Concurrent readers | 10 connections reading XL-tier simultaneously | All return correct results; no `SQLITE_BUSY` errors |
| `XBASE-STRESS-003` | Concurrent read + write | 5 readers + 1 writer on same database | Writer completes; readers never return corrupt data; no deadlock |
| `XBASE-STRESS-004` | Rapid transaction cycling | 10 000 Begin → Insert 1 row → Commit in sequence | All succeed; final row count = 10 000; no leftover locks |
| `XBASE-STRESS-005` | Connection exhaustion | Open 200 connections without closing | Either all open or graceful error; no process crash; clean up works |
| `XBASE-STRESS-006` | Very long query string | `XBase-Query-Execute` with 500 KB SQL string | Either executes or returns `XBASE_QUERY_SYNTAX_ERROR`; no buffer overflow |
| `XBASE-STRESS-007` | Disk-near-full insert | Fill disk to within 1 MB, then insert 10 000 rows | Error returned gracefully; database not corrupted; existing data intact |
| `XBASE-STRESS-008` | Repeated backup/restore cycle | Backup → Restore → Backup × 100 | Each restore produces valid DB; `integrity_check` passes every cycle |
| `XBASE-STRESS-009` | Long-running transaction (idle) | Begin, wait 60 s, then write + commit | Commit succeeds; WAL file cleaned up |
| `XBASE-STRESS-010` | Rollback after large write | Insert 500 000 rows in one transaction, then rollback | All 500 000 rows absent; DB integrity intact; disk space recovered |
| `XBASE-STRESS-011` | 10 000-column filter (IN list batching) | `IN` filter with 10 000 values | Skill batches into multiple `IN` calls or uses temp table; no SQLite variable limit error |
| `XBASE-STRESS-012` | Unicode data at scale | Insert XL-tier rows where Label is 500-char CJK string | No corruption; correct retrieval; `integrity_check` passes |
| `XBASE-STRESS-013` | Max TEXT length at scale | Insert M-tier rows with 10 000-char Label | All stored and retrieved correctly |
| `XBASE-STRESS-014` | Simultaneous backup during heavy write | Start backup, concurrently insert 50 000 rows | Backup completes with consistent snapshot; no error |

---

## Security Tests

| ID | Description | Attack Vector | Pass Criterion |
|---|---|---|---|
| `XBASE-SEC-001` | SQL injection via `DatabasePath` | `DatabasePath:"'; DROP TABLE Users; --"` | Returns `XBASE_DATABASE_PATH_INVALID`; no SQL executed |
| `XBASE-SEC-002` | SQL injection via `TableName` | `TableName:"Users; DROP TABLE Tickets--"` | Returns validation error; no DROP executed |
| `XBASE-SEC-003` | SQL injection via `ColumnName` | Column name `"Id); DROP TABLE Users--"` | Returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `XBASE-SEC-004` | SQL injection via `Value` in Filter | `Value:"' OR '1'='1"` with `Operator:"="` | Treated as literal string via parameterised query; no injection |
| `XBASE-SEC-005` | SQL injection via `XBase-Query-Execute` `Parameters` | `Parameters:["1; DROP TABLE Users"]` | Bound as string literal; no extra statement executed |
| `XBASE-SEC-006` | Path traversal in `DatabasePath` | `DatabasePath:"../../etc/passwd"` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-SEC-007` | Path traversal in `BackupPath` | `BackupPath:"../../Windows/System32/evil.db"` | Returns error; no file written outside `data/` |
| `XBASE-SEC-008` | Null byte in path | `DatabasePath:"test\x00evil.db"` | Returns `XBASE_DATABASE_PATH_INVALID`; null byte stripped or rejected |
| `XBASE-SEC-009` | Null byte in column value | `Value:"hello\x00world"` | Stored and retrieved as-is (SQLite supports embedded nulls in TEXT); no truncation |
| `XBASE-SEC-010` | Homoglyph attack in table name | `TableName:"Uѕerѕ"` (Cyrillic `ѕ`) | Treated as a different table name from `Users`; no unintended access |
| `XBASE-SEC-011` | Excessive `Limit` value | `Limit:2147483647` | Either executes (returns all rows) or caps at a safe maximum; no integer overflow |
| `XBASE-SEC-012` | Negative `Offset` | `Offset:-1` | Returns validation error or treated as 0; no SQL error |
| `XBASE-SEC-013` | Read-only connection bypass | Attempt write via `XBase-Query-Execute` on a read-only connection | Error; write not applied |
| `XBASE-SEC-014` | ConfirmDrop spoofing | `ConfirmDrop:"true"` (string not bool) | Rejected or coerced to `false`; drop not executed |

---

## Acceptance Criteria

A build of XBase is considered **release-ready** when:

1. **All functional tests pass** — every `XBASE-DB-*`, `XBASE-SCH-*`, `XBASE-REC-*`, `XBASE-QRY-*`, `XBASE-IDX-*`, `XBASE-TXN-*`, `XBASE-BAK-*` test ID returns the stated expected result with no exceptions or unhandled errors.

2. **All performance benchmarks pass** — the median result of 3 runs meets or beats every target in `XBASE-PERF-*`.

3. **All stress tests pass** — every `XBASE-STRESS-*` test completes without process crash, data corruption, or unrecovered lock. `PRAGMA integrity_check` returns `ok` after each stress test.

4. **All security tests pass** — every `XBASE-SEC-*` test produces the stated pass criterion with no SQL injection, path traversal, or data exposure.

5. **Error envelope conformance** — every error path returns the standard envelope `{ Success: false, ErrorCode: "XBASE_…", Message: "…", SkillName: "…" }` with no stack traces or internal paths leaked in `Message`.

6. **WAL cleanup** — after every test, `data/backups/` and `data/` contain no orphaned `.db-shm` or `.db-wal` files from prior runs.

7. **Regression gate** — re-running the full suite after any skill file change must produce no new failures.
