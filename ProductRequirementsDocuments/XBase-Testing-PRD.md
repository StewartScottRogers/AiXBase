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
| Available disk space | ≥ 10 GB for performance and stress suites |
| RAM | ≥ 4 GB |
| OS | Windows 10+ or Linux (kernel ≥ 5.15) |
| `AiXBase/` directory | Writable, on a local drive (not network share) for baseline perf tests |
| Clock | System clock must be stable; no large jumps during test run |

---

## Test Data Specifications

### Standard Column Set (used across schema tests)

```
Id          INTEGER  (auto-increment primary key)
Code        TEXT     NOT NULL UNIQUE
Label       TEXT     NOT NULL
Value       REAL
IsActive    INTEGER  NOT NULL DEFAULT 1
CreatedAt   TEXT
UpdatedAt   TEXT
IsDeleted   INTEGER  DEFAULT 0
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

- Each test must set up its own state (create a fresh `AiXBase/test-<ID>/` database directory) and tear it down on completion
- Tests within a group may share a single database only when explicitly noted
- A test **fails** if: wrong output, wrong error code, unhandled exception, or execution time exceeds the stated limit
- Performance tests must be repeated 3 times; the **median** value must meet the target
- All tests must pass with the native file-format engine only — no third-party database libraries

---

## Test Cases: Database Lifecycle

### XBase-Database-Initialize

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-001` | Happy path — new database | `DatabaseName: "test-db-001"` | Returns `Success: true`; directory exists; `_meta.json` and `_schema.json` both present and valid JSON |
| `XBASE-DB-002` | DatabaseName produces nested path | (Not supported; name is a single directory segment) | `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-003` | Directory already exists, OverwriteIfExists false | Pre-create the directory | Returns `XBASE_DATABASE_EXISTS`; original directory unchanged |
| `XBASE-DB-004` | Directory already exists, OverwriteIfExists true | Pre-create directory with known content | Returns `Success: true`; original content removed; new `_meta.json` and `_schema.json` present |
| `XBASE-DB-005` | Name escapes `AiXBase/` via traversal | `DatabaseName: "../outside"` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-006` | Name with spaces and Unicode | `DatabaseName: "my db 测试"` | Returns `Success: true`; directory created at path with spaces/Unicode |
| `XBASE-DB-007` | Absolute path supplied as name | `DatabaseName: "C:/Windows/Temp/evil"` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-008` | Empty string name | `DatabaseName: ""` | Returns `XBASE_DATABASE_PATH_INVALID` |
| `XBASE-DB-009` | Name exceeding 260 chars (Windows MAX_PATH) | 261-char name | Returns `XBASE_DATABASE_PATH_INVALID` or OS-level error wrapped in skill error envelope |
| `XBASE-DB-010` | `_meta.json` has correct version field | Normal init | `_meta.json` parsed; `XBaseVersion` equals `1` |
| `XBASE-DB-011` | `CreatedAt` is valid ISO-8601 | Normal init | `CreatedAt` matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}` |
| `XBASE-DB-012` | Concurrent init same name (race) | Two callers simultaneously | Exactly one succeeds; the other returns `XBASE_DATABASE_EXISTS` or serialises cleanly |

---

### XBase-Database-Connect

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-013` | Happy path | Valid name, unique `ConnectionName` | `IsOpen: true`; subsequent skills can use this alias |
| `XBASE-DB-014` | Directory does not exist | Non-existent name | Returns `XBASE_DATABASE_NOT_FOUND` |
| `XBASE-DB-015` | ConnectionName already in use | Same alias as open connection | Returns `XBASE_CONNECTION_NAME_IN_USE` |
| `XBASE-DB-016` | Empty ConnectionName | `ConnectionName: ""` | Returns validation error |
| `XBASE-DB-017` | Two connections to same directory with different names | `Name1`, `Name2` → same directory | Both open successfully; both can read concurrently |
| `XBASE-DB-018` | Connect to a directory missing `_meta.json` | Directory exists but `_meta.json` absent | Returns `XBASE_DATABASE_CORRUPT` |
| `XBASE-DB-019` | Connect to directory with invalid `_meta.json` | `_meta.json` is empty or not valid JSON | Returns `XBASE_DATABASE_CORRUPT` |
| `XBASE-DB-020` | ConnectionName with special characters | `ConnectionName: "conn/with:special*chars"` | Handled as opaque alias; success or validation error — must not crash |

---

### XBase-Database-Disconnect

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-021` | Happy path | Open connection | `Success: true`; connection alias deregistered |
| `XBASE-DB-022` | Unknown ConnectionName | Name never opened | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-DB-023` | Open transaction, RollbackOpenTransaction true | Begin txn, then disconnect | Transaction workspace deleted; connection closed cleanly |
| `XBASE-DB-024` | Open transaction, RollbackOpenTransaction false | Begin txn, then disconnect | Returns `XBASE_TRANSACTION_STILL_OPEN`; connection remains registered |
| `XBASE-DB-025` | Disconnect twice | Close, then close again | Second call returns `XBASE_CONNECTION_INVALID` |
| `XBASE-DB-026` | Verify ClosedAt timestamp | Normal disconnect | `ClosedAt` is ISO-8601 and ≥ connect timestamp |

---

### XBase-Database-Drop

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-DB-027` | Happy path | `ConfirmDrop: true`, valid name | `Success: true`; database directory and all its files deleted |
| `XBASE-DB-028` | ConfirmDrop false | `ConfirmDrop: false` | Returns `XBASE_DROP_NOT_CONFIRMED`; directory intact |
| `XBASE-DB-029` | ConfirmDrop omitted | No `ConfirmDrop` field | Returns `XBASE_DROP_NOT_CONFIRMED` |
| `XBASE-DB-030` | Directory does not exist | Non-existent name | Returns `XBASE_DATABASE_NOT_FOUND` |
| `XBASE-DB-031` | Drop with open connections | Two connections open | Both deregistered; directory deleted |
| `XBASE-DB-032` | Drop with active transaction | Transaction workspace present | Workspace deleted with directory; no error |
| `XBASE-DB-033` | All DBF and index files removed | Directory with tables and indexes | Entire directory tree deleted; no orphaned files |

---

## Test Cases: Schema Management

### XBase-Schema-TableCreate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-001` | Happy path — standard columns | Standard column set | `Success: true`; table entry in `_schema.json`; `{TableName}.dbf` exists and is empty |
| `XBASE-SCH-002` | Implicit Id column injected | No `PrimaryKey` column supplied | `Id` column prepended in `_schema.json` with `AutoIncrement: true`; `NextId: 1` |
| `XBASE-SCH-003` | Explicit primary key honoured | Column with `PrimaryKey: true` | No implicit `Id` added; user PK column is first |
| `XBASE-SCH-004` | Implicit audit columns appended | No `CreatedAt/UpdatedAt/IsDeleted` in input | Three columns appended automatically in `_schema.json` |
| `XBASE-SCH-005` | IfNotExists true (default) — table exists | Call twice | Second call returns `Success: true`; no error; `_schema.json` unchanged |
| `XBASE-SCH-006` | IfNotExists false — table exists | `IfNotExists: false`, table pre-exists | Returns `XBASE_SCHEMA_TABLE_EXISTS` |
| `XBASE-SCH-007` | Table with 100 columns | 100 column definitions | All 100 present in `_schema.json` column array |
| `XBASE-SCH-008` | Column name is a reserved word | `Name: "Order"` | Column created; accessible via exact name match in skill layer |
| `XBASE-SCH-009` | Column name with spaces | `Name: "My Column"` | Created and accessible (stored in JSON as-is) |
| `XBASE-SCH-010` | Column name with Unicode | `Name: "列名"` | Created and accessible |
| `XBASE-SCH-011` | NOT NULL column, no default | `Nullable: false`, no `Default` | Insert without that column returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-SCH-012` | UNIQUE column | `Unique: true` | Duplicate insert returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-SCH-013` | Foreign key column | `ForeignKey: "Statuses.Id"` | FK entry in `_schema.json`; insert with non-existent parent returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-SCH-014` | All supported types | One column each of INTEGER, TEXT, REAL, NUMERIC | All recorded in `_schema.json` with correct `Type` field |
| `XBASE-SCH-015` | Empty Columns array | `Columns: []` | Returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `XBASE-SCH-016` | Duplicate column names | Two columns both named `Name` | Returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `XBASE-SCH-017` | Table name with special characters | `TableName: "My Table!"` | Returns validation error (table names must be safe identifiers) |

---

### XBase-Schema-TableAlter

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-018` | Add single column | `AddColumns: [{Name:"Score", Type:"REAL"}]` | Column present in `_schema.json`; existing rows in `.dbf` do not have the field (treated as NULL on read) |
| `XBASE-SCH-019` | Add multiple columns at once | Three column definitions | All three in `_schema.json` |
| `XBASE-SCH-020` | Add column that already exists | Existing column name | Returns `XBASE_SCHEMA_COLUMN_EXISTS` |
| `XBASE-SCH-021` | Table does not exist | Non-existent table name | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-SCH-022` | Add NOT NULL column to populated table | Existing table has rows, new column has no default | Skill rejects this: existing rows cannot satisfy NOT NULL without a default; returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `XBASE-SCH-023` | Add NOT NULL column with default | `Nullable: false`, `Default: "0"` | Column added; new inserts must supply the field; existing rows return the default when field is absent |
| `XBASE-SCH-024` | Empty AddColumns array | `AddColumns: []` | Returns `Success: true` with `AddedColumns: []` (no-op) |

---

### XBase-Schema-TableDrop

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-025` | Happy path | `ConfirmDrop: true` | Table entry removed from `_schema.json`; `.dbf` and all `.ndx` files deleted |
| `XBASE-SCH-026` | ConfirmDrop false | `ConfirmDrop: false` | Returns `XBASE_DROP_NOT_CONFIRMED`; table intact |
| `XBASE-SCH-027` | Table does not exist, IfExists true | Non-existent table | Returns `Success: true` (no-op) |
| `XBASE-SCH-028` | Table does not exist, IfExists false | `IfExists: false` | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-SCH-029` | Drop referenced table (FK violation) | Table referenced by another as FK target | Skill checks `_schema.json` for FK references; returns error if dependent tables exist |
| `XBASE-SCH-030` | Drop table with rows | Table with L-tier data | `.dbf` deleted; no error |

---

### XBase-Schema-TableList

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-031` | Empty database | Freshly initialised DB | `Tables: []` |
| `XBASE-SCH-032` | Multiple tables | Create 5 tables | All 5 names returned, sorted alphabetically |
| `XBASE-SCH-033` | Internal files excluded | Normal database | `_meta`, `_schema`, and `_txn_*` directories not in results |
| `XBASE-SCH-034` | Tables created then dropped | Drop 2 of 5 | Only 3 remain |

---

### XBase-Schema-ColumnList

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-SCH-035` | Happy path | Standard column set | Returns all columns with correct `Type`, `Nullable`, `Default`, `PrimaryKey` from `_schema.json` |
| `XBASE-SCH-036` | Table with no nullable columns | All `Nullable: false` | All `Nullable: false` |
| `XBASE-SCH-037` | Table does not exist | Non-existent name | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-SCH-038` | Column with default value | Column has `Default: "42"` | `Default` field reflects the value |
| `XBASE-SCH-039` | Composite PK | Two-column primary key | Both columns show `PrimaryKey: true` |

---

## Test Cases: Record Operations

### XBase-Record-Insert

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-001` | Single row | One `{ Code: "A", Label: "Alpha" }` | `InsertedCount: 1`; `LastInsertedId` equals the `NextId` value consumed; row present in `.dbf` |
| `XBASE-REC-002` | Bulk insert | 1 000 rows | `InsertedCount: 1000`; all rows in `.dbf` |
| `XBASE-REC-003` | Auto-set CreatedAt | No `CreatedAt` in input | Row has valid ISO-8601 `CreatedAt` |
| `XBASE-REC-004` | Auto-set UpdatedAt | No `UpdatedAt` in input | Row has valid ISO-8601 `UpdatedAt` equal to `CreatedAt` on insert |
| `XBASE-REC-005` | NOT NULL violation | Omit required field | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-006` | UNIQUE violation | Two rows, same unique field | Second insert returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-007` | FK violation | FK column pointing to non-existent parent | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-008` | NULL value for nullable column | `{ Code: "B", Label: null }` | Row in `.dbf` has `"Label": null` |
| `XBASE-REC-009` | Empty string vs NULL | `{ Label: "" }` | Row has `"Label": ""` (not null) |
| `XBASE-REC-010` | Integer 0 vs NULL | `{ Value: 0 }` | Row has `"Value": 0` (not null) |
| `XBASE-REC-011` | Text with quotes | `{ Label: "it's a \"test\"" }` | JSON serialisation handles escaping; retrieved value matches input exactly |
| `XBASE-REC-012` | Text with backslashes | `{ Label: "path\\to\\file" }` | Stored and retrieved correctly via JSON escaping |
| `XBASE-REC-013` | Unicode and emoji | `{ Label: "测试 🎉" }` | Stored and retrieved without corruption |
| `XBASE-REC-014` | Very long TEXT (10 000 chars) | `{ Label: "x" * 10000 }` | Stored and retrieved; `InsertedCount: 1` |
| `XBASE-REC-015` | REAL precision | `{ Value: 1.234567890123456789 }` | Stored as JSON number; retrieved within IEEE 754 double tolerance |
| `XBASE-REC-016` | Insert empty Rows array | `Rows: []` | `InsertedCount: 0`; `Success: true` (no-op) |
| `XBASE-REC-017` | Unknown column in row | `{ Bogus: "x" }` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-REC-018` | Table does not exist | Non-existent table | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-REC-019` | Connection invalid | Closed connection name | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-REC-020` | Insert within transaction | `TransactionName` supplied | Row appended in transaction workspace `.dbf`; absent from live file before commit |
| `XBASE-REC-021` | TransactionName not open | Random transaction name | Returns `XBASE_TRANSACTION_NOT_OPEN` |

---

### XBase-Record-Select

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-022` | All rows, all columns | No Filter, `Columns: ["*"]` | Returns all rows; `TotalCount` matches row count in `.dbf` |
| `XBASE-REC-023` | Column projection | `Columns: ["Id", "Label"]` | Only those two fields in each returned row |
| `XBASE-REC-024` | Filter applied | Filter `Code = 'CODE-1'` | Returns exactly 1 row |
| `XBASE-REC-025` | Filter — no matching rows | Filter `Code = 'NONE'` | `Rows: []`, `TotalCount: 0` |
| `XBASE-REC-026` | Sort ascending | `Sort: [{Field:"Label", Direction:"ASC"}]` | Rows in alphabetical order |
| `XBASE-REC-027` | Sort descending | `Sort: [{Field:"Value", Direction:"DESC"}]` | Rows in reverse numeric order |
| `XBASE-REC-028` | Multi-column sort | `Sort: [{Field:"IsActive"},{Field:"Label"}]` | Primary sort on IsActive, secondary on Label |
| `XBASE-REC-029` | Pagination — page 1 | `Limit: 10, Offset: 0` | 10 rows; `TotalCount` = total matching rows |
| `XBASE-REC-030` | Pagination — last page (partial) | M-tier table, `Limit: 10, Offset: 9995` | 5 rows returned |
| `XBASE-REC-031` | Offset beyond row count | `Offset: 99999` on S-tier table | `Rows: []`; `TotalCount` = actual count |
| `XBASE-REC-032` | Limit 0 | `Limit: 0` | `Rows: []`; `TotalCount` = actual count |
| `XBASE-REC-033` | Soft-deleted rows excluded by default | Insert + soft-delete a row | Row absent without `IncludeDeleted`; present with `IncludeDeleted: true` |
| `XBASE-REC-034` | Unknown column in projection | `Columns: ["Bogus"]` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-REC-035` | Table does not exist | Non-existent table | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-REC-036` | NULL values in rows | Rows with null fields | `null` preserved in output; not coerced to empty string or 0 |
| `XBASE-REC-037` | Sort on NULL-containing column | Mix of null and non-null, ASC sort | NULLs sort consistently (nulls last for ASC is the XBase default) |
| `XBASE-REC-038` | TotalCount accurate with filter + limit | L-tier data, filter returns 500 rows, Limit 10 | `TotalCount: 500`, `Rows.length: 10` |

---

### XBase-Record-Update

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-039` | Single row update | Filter `Id = 1`, `Values: {Label:"New"}` | `UpdatedCount: 1`; row in `.dbf` has new value |
| `XBASE-REC-040` | Multi-row update | Filter `IsActive = 0` on 50-row set | `UpdatedCount: 50` |
| `XBASE-REC-041` | No matching rows | Filter `Code = 'NONE'` | `UpdatedCount: 0`; no error |
| `XBASE-REC-042` | Auto-set UpdatedAt | No `UpdatedAt` in Values | `UpdatedAt` updated to now; `CreatedAt` unchanged in `.dbf` |
| `XBASE-REC-043` | Empty Filter rejected | No Filter supplied | Returns `XBASE_RECORD_FILTER_REQUIRED` |
| `XBASE-REC-044` | Empty Values | `Values: {}` | Returns validation error or `UpdatedCount: 0` no-op |
| `XBASE-REC-045` | UNIQUE violation on update | Set a field to a value duplicating another row | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-046` | NOT NULL violation | Set a NOT NULL field to null | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `XBASE-REC-047` | Update within transaction | `TransactionName` supplied | Update applied in workspace; not present in live file until commit |
| `XBASE-REC-048` | Unknown column in Values | `Values: {Bogus: 1}` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |

---

### XBase-Record-Delete

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-049` | Soft delete (default) | Filter `Id = 1` | `IsDeleted = 1` on that row; line still in `.dbf` |
| `XBASE-REC-050` | Hard delete | `HardDelete: true` | Line physically removed from `.dbf` |
| `XBASE-REC-051` | Soft delete already soft-deleted | `IsDeleted` already 1 | `DeletedCount: 1`; `UpdatedAt` refreshed (idempotent) |
| `XBASE-REC-052` | No matching rows | Filter on non-existent value | `DeletedCount: 0`; no error |
| `XBASE-REC-053` | Empty Filter rejected | No Filter | Returns `XBASE_RECORD_FILTER_REQUIRED` |
| `XBASE-REC-054` | Bulk soft-delete | Filter covers L-tier subset (10 000 rows) | All 10 000 flagged; line count unchanged |
| `XBASE-REC-055` | Hard delete with FK child rows | Parent row has FK children | Skill checks `_schema.json` for FK references; returns error if children reference the parent |

---

### XBase-Record-Upsert

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-REC-056` | Insert path | Row not present | `Action: "inserted"`, row in `.dbf` |
| `XBASE-REC-057` | Update path | Row with same conflict key exists | `Action: "updated"`, `UpdatedAt` refreshed |
| `XBASE-REC-058` | Idempotent — same row twice | Upsert same data twice | Second call: `Action: "updated"`; row unchanged logically |
| `XBASE-REC-059` | Multiple conflict columns | `ConflictColumns: ["TicketId", "Tag"]` | Both paths work correctly |
| `XBASE-REC-060` | CreatedAt preserved on update | Row pre-exists with `CreatedAt = T1` | After upsert, `CreatedAt` still `T1`; only `UpdatedAt` changes |
| `XBASE-REC-061` | ConflictColumns not found in table | `ConflictColumns: ["Bogus"]` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-REC-062` | Non-conflict constraint violation | Update path triggers NOT NULL violation | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |

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
| `XBASE-QRY-008` | LIKE — case sensitivity | `Value:"%code%"` applied to values containing `CODE` | Case-insensitive for ASCII characters (AI normalises to lowercase for comparison) |
| `XBASE-QRY-009` | IN — multiple values | `Value:["A","B","C"]` | Exactly those 3 rows returned |
| `XBASE-QRY-010` | IN — single value | `Value:["A"]` | One row returned |
| `XBASE-QRY-011` | IN — empty array | `Value:[]` | Returns `XBASE_FILTER_VALUE_REQUIRED` |
| `XBASE-QRY-012` | IN — 1 000 items | Array of 1 000 values | Handled in a single in-memory membership check; no limit issues |
| `XBASE-QRY-013` | NOT IN | `Operator:"NOT IN"` | All rows not in the array |
| `XBASE-QRY-014` | IS NULL | `Operator:"IS NULL"`, `Value` omitted | Only rows where the field is `null` or absent |
| `XBASE-QRY-015` | IS NOT NULL | `Operator:"IS NOT NULL"` | Only rows where the field is non-null |
| `XBASE-QRY-016` | Chain AND | Two filters, `LogicalOperator:"AND"` | Intersection |
| `XBASE-QRY-017` | Chain OR | Two filters, `LogicalOperator:"OR"` | Union |
| `XBASE-QRY-018` | Nested filter groups | `Filters` array with sub-filters | Correct precedence `(A AND B) OR C` |
| `XBASE-QRY-019` | Field with injection attempt | `Field:"Id; DROP TABLE Users--"` | Returns `XBASE_FILTER_FIELD_INVALID` |
| `XBASE-QRY-020` | Unknown operator | `Operator:"BETWEEN"` | Returns `XBASE_FILTER_OPERATOR_UNKNOWN` |
| `XBASE-QRY-021` | Value required but missing | Operator `=` with no `Value` | Returns `XBASE_FILTER_VALUE_REQUIRED` |
| `XBASE-QRY-022` | Value is integer | `Operator:"=", Value:42` | Correctly compared as a number |
| `XBASE-QRY-023` | Value is float | `Value:3.14` | Correctly compared as a floating-point number |
| `XBASE-QRY-024` | Value is boolean | `Value:true` | Correctly compared as integer 1 |

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
| `XBASE-QRY-032` | Sort on NULL-containing column | Mix of null and non-null | Nulls sort consistently; no crash |

---

### XBase-Query-Join

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-033` | INNER JOIN — matching rows | Tickets JOIN Statuses on StatusId=Id | Only tickets with a matching status returned; AI loads both `.dbf` files and joins in memory |
| `XBASE-QRY-034` | LEFT JOIN — no match | Ticket with null StatusId | Ticket row present; Status fields null in merged result |
| `XBASE-QRY-035` | Join with alias | `Alias:"s"` for joined table | Compiled specification uses alias prefix for column disambiguation |
| `XBASE-QRY-036` | Invalid JoinType | `JoinType:"BANANA"` | Returns `XBASE_JOIN_TYPE_INVALID` |
| `XBASE-QRY-037` | Malformed OnLeft | `OnLeft:"Tickets..StatusId"` | Returns `XBASE_JOIN_REFERENCE_INVALID` |
| `XBASE-QRY-038` | Multiple joins chained | Three joins in sequence | All three applied correctly in order |
| `XBASE-QRY-039` | Self-join | Same table joined to itself with different aliases | Returns valid merged results |

---

### XBase-Query-Aggregate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-QRY-040` | COUNT(*) | `Function:"COUNT", Column:"*"` | Returns total row count |
| `XBASE-QRY-041` | COUNT on column with NULLs | Column has 10 nulls, 90 values | COUNT returns 90 (nulls excluded) |
| `XBASE-QRY-042` | SUM | `Function:"SUM", Column:"Value"` | Correct numeric sum |
| `XBASE-QRY-043` | AVG | `Function:"AVG"` | Correct average; float result |
| `XBASE-QRY-044` | MIN / MAX | Both functions | Correct boundary values |
| `XBASE-QRY-045` | Aggregate on empty table | No rows | COUNT = 0; SUM/AVG/MIN/MAX = null (not crash) |
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
| `XBASE-QRY-052` | SELECT with filter and sort | `Operation:"SELECT"`, `Filter`, `Sort` | Returns `Rows` and `TotalCount` |
| `XBASE-QRY-053` | SELECT with join | `Operation:"SELECT"`, `Join` | Joined rows returned correctly |
| `XBASE-QRY-054` | SELECT with aggregate | `Operation:"SELECT"`, `Aggregate` | Aggregate result returned |
| `XBASE-QRY-055` | INSERT via Execute | `Operation:"INSERT"`, `Values` | Returns `InsertedCount: 1` and `LastInsertedId` |
| `XBASE-QRY-056` | UPDATE via Execute | `Operation:"UPDATE"`, `Filter`, `Values` | Returns `AffectedRows` |
| `XBASE-QRY-057` | DELETE via Execute | `Operation:"DELETE"`, `Filter` | Returns `AffectedRows` |
| `XBASE-QRY-058` | Missing Operation | `Operation` omitted | Returns validation error |
| `XBASE-QRY-059` | Unknown Operation | `Operation:"MERGE"` | Returns validation error |
| `XBASE-QRY-060` | UPDATE without Filter | `Operation:"UPDATE"`, no `Filter` | Returns `XBASE_RECORD_FILTER_REQUIRED` |
| `XBASE-QRY-061` | DELETE without Filter | `Operation:"DELETE"`, no `Filter` | Returns `XBASE_RECORD_FILTER_REQUIRED` |

---

## Test Cases: Index Operations

### XBase-Index-Create

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-001` | Single column index | `Columns:["StatusId"]` | Index entry added to `_schema.json`; `.ndx` file created and sorted |
| `XBASE-IDX-002` | Composite index | `Columns:["StatusId","CreatedAt"]` | Both columns in index entry in `_schema.json`; `.ndx` key is pipe-joined value |
| `XBASE-IDX-003` | UNIQUE index | `Unique: true` | Index entry has `Unique: true`; insert of duplicate value returns constraint error |
| `XBASE-IDX-004` | IfNotExists true (default) — index exists | Call twice | Second call returns `Success: true`; `.ndx` unchanged |
| `XBASE-IDX-005` | IfNotExists false — index exists | `IfNotExists: false`, index pre-exists | Returns `XBASE_INDEX_EXISTS` |
| `XBASE-IDX-006` | Non-existent table | Random table name | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-IDX-007` | Non-existent column | `Columns:["Bogus"]` | Returns `XBASE_SCHEMA_COLUMN_MISSING` |
| `XBASE-IDX-008` | Index on 10 columns (wide) | 10-column composite | Created; `.ndx` key uses all 10 fields pipe-joined |

---

### XBase-Index-Drop

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-009` | Happy path | Existing index name | `.ndx` file deleted; entry removed from `_schema.json` |
| `XBASE-IDX-010` | IfExists true — index not found | `IfExists: true`, no such index | `Success: true` (no-op) |
| `XBASE-IDX-011` | IfExists false — index not found | `IfExists: false` | Returns `XBASE_INDEX_NOT_FOUND` |

---

### XBase-Index-Rebuild

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-012` | Rebuild named index | Valid `IndexName` | `RebuiltIndexes: ["<name>"]`; `.ndx` file rewritten from `.dbf` data |
| `XBASE-IDX-013` | Rebuild all on table | `TableName` provided, no `IndexName` | All indexes on that table listed in output; each `.ndx` rewritten |
| `XBASE-IDX-014` | Rebuild all in database | Neither `IndexName` nor `TableName` | All indexes in `_schema.json` rebuilt |
| `XBASE-IDX-015` | Table with no indexes | `TableName` pointing to unindexed table | `RebuiltIndexes: []`; no error |
| `XBASE-IDX-016` | Non-existent index | `IndexName:"bogus"` | Returns `XBASE_INDEX_NOT_FOUND` |
| `XBASE-IDX-017` | Non-existent table | `TableName:"bogus"` | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |

---

### XBase-Index-List

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-IDX-018` | Table with no indexes | Unindexed table | `Indexes: []` |
| `XBASE-IDX-019` | Table with multiple indexes | Create 3 indexes | All 3 returned from `_schema.json` with correct `Columns` and `Unique` flag |
| `XBASE-IDX-020` | UNIQUE index flagged | Index created with `Unique: true` | `Unique: true` in output |
| `XBASE-IDX-021` | Table does not exist | Non-existent table | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |
| `XBASE-IDX-022` | Composite index columns in order | Two-column index | `Columns` array reflects the creation order |

---

## Test Cases: Transaction Control

### XBase-Transaction-Begin

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-001` | Happy path | Valid `ConnectionName` and `TransactionName` | `Success: true`; `StartedAt` is ISO-8601; `_txn_{name}/` directory created; `_schema.json` copied inside |
| `XBASE-TXN-002` | TransactionName already in use | Same name twice | Returns `XBASE_TRANSACTION_NAME_IN_USE` |
| `XBASE-TXN-003` | Connection invalid | Closed connection | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-TXN-004` | Two concurrent transactions, different names | Two Begin calls, different names | Both workspace directories exist simultaneously |
| `XBASE-TXN-005` | Table file not yet copied | Begin, then read a table | Read returns data from live file (lazy copy not yet triggered) |
| `XBASE-TXN-006` | Table file copied on first write | Begin, then insert into table | `_txn_{name}/{Table}.dbf` exists; live file unchanged |

---

### XBase-Transaction-Commit

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-007` | Happy path | Open transaction, insert row, commit | Row visible in live `.dbf` after commit; workspace directory gone |
| `XBASE-TXN-008` | Commit deregisters name | After commit, same name available | Can begin again with same `TransactionName` |
| `XBASE-TXN-009` | Commit with no open transaction | Random name | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-010` | Commit empty transaction (no writes) | Begin + commit, no ops | `Success: true`; workspace directory removed |
| `XBASE-TXN-011` | CommittedAt timestamp | Normal commit | `CommittedAt` ≥ `StartedAt` |
| `XBASE-TXN-012` | Live file updated atomically | Commit of large insert | `File.Move` replaces each live file; no partial state observed by concurrent reader |

---

### XBase-Transaction-Rollback

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-013` | Full rollback | Insert row in txn, rollback | Row absent from live `.dbf`; workspace directory deleted |
| `XBASE-TXN-014` | Rollback deregisters name | After rollback, name reusable | New begin succeeds with same name |
| `XBASE-TXN-015` | Rollback with no open transaction | Random name | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-016` | Rollback to savepoint | Create savepoint after insert A; insert B; rollback to savepoint | B absent from workspace; A present; transaction still open |
| `XBASE-TXN-017` | Rollback to non-existent savepoint | `ToSavepoint:"ghost"` | Returns `XBASE_SAVEPOINT_NOT_FOUND` |
| `XBASE-TXN-018` | RolledBackTo field — full rollback | Full rollback | `RolledBackTo:"full"` |
| `XBASE-TXN-019` | RolledBackTo field — savepoint | Savepoint rollback | `RolledBackTo:"<savepoint name>"` |

---

### XBase-Transaction-Savepoint

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-TXN-020` | Create savepoint | `SavepointName:"sp1"` | `Success: true`; `_txn_{name}/sp_sp1/` directory created with snapshot |
| `XBASE-TXN-021` | Multiple savepoints | `sp1`, `sp2`, `sp3` in sequence | Each savepoint directory exists; each can be rolled back to independently |
| `XBASE-TXN-022` | Duplicate savepoint name | `sp1` twice | Returns `XBASE_SAVEPOINT_NAME_IN_USE` |
| `XBASE-TXN-023` | No active transaction | Random `TransactionName` | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `XBASE-TXN-024` | Savepoint after commit | `TransactionName` committed, then savepoint | Returns `XBASE_TRANSACTION_NOT_OPEN` |

---

## Test Cases: Backup and Restore

### XBase-Backup-Create

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-BAK-001` | Happy path | Open connection, no label | Directory in `AiXBase/backups/`; name matches `<db>_<timestamp>` pattern |
| `XBASE-BAK-002` | With label | `BackupLabel:"pre-migration"` | Directory name ends with `_pre-migration` |
| `XBASE-BAK-003` | Backup is valid XBase directory | After backup | `_meta.json` and `_schema.json` present in backup; all `.dbf` files present |
| `XBASE-BAK-004` | Backup during active transaction | Transaction open with uncommitted writes | Backup reflects committed live files only; transaction workspace excluded |
| `XBASE-BAK-005` | `AiXBase/backups/` auto-created | Directory does not exist | Directory created; backup written |
| `XBASE-BAK-006` | Two backups same second | Called twice within same second | Unique directory names (millisecond suffix or counter) |
| `XBASE-BAK-007` | Connection invalid | Closed connection | Returns `XBASE_CONNECTION_INVALID` |
| `XBASE-BAK-008` | Backup of XL-tier database | 1M-row database | Completes; backup file count and total size within 5% of source |

---

### XBase-Backup-Restore

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-BAK-009` | Happy path with pre-restore snapshot | `ConfirmRestore: true`, `CreateBackupBeforeRestore: true` | `PreRestoreBackupPath` set; target directory replaced with backup contents |
| `XBASE-BAK-010` | Without pre-restore snapshot | `CreateBackupBeforeRestore: false` | `PreRestoreBackupPath: null`; target overwritten |
| `XBASE-BAK-011` | ConfirmRestore false | `ConfirmRestore: false` | Returns `XBASE_RESTORE_NOT_CONFIRMED` |
| `XBASE-BAK-012` | ConfirmRestore omitted | No field | Returns `XBASE_RESTORE_NOT_CONFIRMED` |
| `XBASE-BAK-013` | Backup directory not found | Non-existent path | Returns `XBASE_BACKUP_NOT_FOUND` |
| `XBASE-BAK-014` | Connection reopened after restore | Target connection | Connection is valid and returns rows from restored state |
| `XBASE-BAK-015` | Restore to different database | `TargetConnectionName` points to DB B, backup from DB A | DB B directory now contains DB A's files |
| `XBASE-BAK-016` | Restore with active transaction on target | Transaction workspace present | Transaction workspace deleted; restore proceeds |

---

### XBase-Backup-Verify

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `XBASE-BAK-017` | Valid backup | Good backup directory | `IntegrityOk: true`, `Issues: []` |
| `XBASE-BAK-018` | Corrupt DBF line | Manually write an invalid JSON line into a `.dbf` file | `IntegrityOk: false`; `Issues` contains the file name and line number |
| `XBASE-BAK-019` | Non-existent path | Random path | Returns `XBASE_BACKUP_NOT_FOUND` |
| `XBASE-BAK-020` | Directory missing `_meta.json` | Directory exists but no `_meta.json` | Returns `XBASE_BACKUP_CORRUPT` |
| `XBASE-BAK-021` | Empty `_meta.json` | Zero-byte file | Returns `XBASE_BACKUP_CORRUPT` |
| `XBASE-BAK-022` | Verify does not require open connection | No `ConnectionName` input | Reads files directly; `Success: true` |
| `XBASE-BAK-023` | Does not modify backup | Before and after checksums match | File bytes identical pre- and post-verify |

---

## Performance Benchmarks

All benchmarks use a dedicated `AiXBase/perf/` database, freshly initialised. Median of 3 runs must meet target.

### Insert Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-001` | Single-row inserts, one call per row | 1 000 rows | ≥ 200 rows/sec (each call reads `_schema.json`, appends 1 line) |
| `XBASE-PERF-002` | Bulk insert, single `XBase-Record-Insert` call | 10 000 rows | ≤ 10 s total |
| `XBASE-PERF-003` | Bulk insert in batches of 1 000 | 100 000 rows | ≤ 120 s total |
| `XBASE-PERF-004` | Transactional bulk insert vs direct | 10 000 rows each | Times within 20% of each other (both use append) |

### Select Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-005` | Full table scan, no filter | L-tier (100 000 rows), all columns | ≤ 2 s |
| `XBASE-PERF-006` | Full table scan | XL-tier (1 000 000 rows), all columns | ≤ 20 s |
| `XBASE-PERF-007` | Point lookup, no index | M-tier, filter on non-indexed column | ≤ 1 s |
| `XBASE-PERF-008` | Point lookup, with index | M-tier, binary-search on `.ndx` | ≤ 100 ms |
| `XBASE-PERF-009` | Range scan, with filter | M-tier, filter `Id` between 1 and 1000 | ≤ 500 ms |
| `XBASE-PERF-010` | Paginated select | L-tier, `Limit: 25, Offset: 50000` | ≤ 2 s |
| `XBASE-PERF-011` | Projection (2 columns) vs all columns | L-tier | Both complete; projection not slower than full row |

### Update / Delete Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-012` | Bulk update (set IsActive flag) | Update 10 000 rows in one call | ≤ 5 s (full `.dbf` rewrite) |
| `XBASE-PERF-013` | Bulk hard delete | Delete 10 000 rows in one call | ≤ 5 s (full `.dbf` rewrite) |
| `XBASE-PERF-014` | Update single row by Id | S-tier, filter by Id | ≤ 500 ms |

### Aggregate Throughput

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-015` | COUNT(*) | L-tier | ≤ 2 s |
| `XBASE-PERF-016` | SUM on REAL column | L-tier | ≤ 2 s |
| `XBASE-PERF-017` | GROUP BY low-cardinality column | L-tier, 4 distinct values | ≤ 3 s |
| `XBASE-PERF-018` | GROUP BY medium-cardinality column | M-tier, 100 distinct values | ≤ 2 s |
| `XBASE-PERF-019` | In-memory join + COUNT | M-tier Tickets × 4-row Statuses | ≤ 2 s |

### Index Impact

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-020` | Create index on L-tier table | 100 000 rows, single column | ≤ 10 s |
| `XBASE-PERF-021` | Create composite index | 100 000 rows, two columns | ≤ 15 s |
| `XBASE-PERF-022` | Rebuild index | After bulk insert | ≤ 15 s for L-tier |
| `XBASE-PERF-023` | Query speedup with index | Before/after index on filter column, M-tier | ≥ 5× faster with index (binary search vs full scan) |

### Transaction Overhead

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-024` | Begin + Commit, empty | 1 000 cycles | ≤ 30 s total (directory create/delete per cycle) |
| `XBASE-PERF-025` | Savepoint creation | 100 savepoints in one transaction | ≤ 5 s |
| `XBASE-PERF-026` | Rollback of large transaction | 10 000 inserts then rollback | Rollback ≤ 5 s (directory delete) |

### Backup Performance

| ID | Description | Data | Target |
|---|---|---|---|
| `XBASE-PERF-027` | Backup M-tier database | 10 000 rows | ≤ 5 s |
| `XBASE-PERF-028` | Backup L-tier database | 100 000 rows | ≤ 30 s |
| `XBASE-PERF-029` | Restore L-tier backup | 100 000 rows | ≤ 30 s |
| `XBASE-PERF-030` | Verify L-tier backup | 100 000 rows | ≤ 15 s |

---

## Stress Tests

| ID | Description | Setup | Pass Criterion |
|---|---|---|---|
| `XBASE-STRESS-001` | Sustained insert load | Insert 1 000 000 rows in batches of 1 000, single database | No crash; final row count = 1 M; `XBase-Backup-Verify` passes on the database |
| `XBASE-STRESS-002` | Concurrent readers | 10 callers reading L-tier simultaneously | All return correct results; no file corruption |
| `XBASE-STRESS-003` | Sequential read + write | Alternate between select and insert on the same table, 1 000 cycles | All operations succeed; final row count correct |
| `XBASE-STRESS-004` | Rapid transaction cycling | 1 000 Begin → Insert 1 row → Commit in sequence | All succeed; final row count = 1 000; no orphaned `_txn_*/` directories |
| `XBASE-STRESS-005` | Many open connections | Register 100 connection aliases | Either all registered or graceful error; no process crash; all deregister cleanly |
| `XBASE-STRESS-006` | Large compound query specification | `XBase-Query-Execute` with 100 chained filter conditions | Executes or returns validation error; no crash |
| `XBASE-STRESS-007` | Disk-near-full insert | Fill disk to within 1 MB, then insert 1 000 rows | Error returned gracefully; database not corrupted; existing data intact |
| `XBASE-STRESS-008` | Repeated backup/restore cycle | Backup → Restore → Backup × 50 | Each restore produces valid database; `XBase-Backup-Verify` passes every cycle |
| `XBASE-STRESS-009` | Long-running transaction (idle) | Begin, wait 60 s, then write + commit | Commit succeeds; no orphaned workspace directory |
| `XBASE-STRESS-010` | Rollback after large write | Insert 50 000 rows in one transaction, then rollback | All 50 000 rows absent from live file; workspace directory deleted |
| `XBASE-STRESS-011` | Large IN filter | `IN` filter with 10 000 values | Handled by in-memory membership Set; no memory error |
| `XBASE-STRESS-012` | Unicode data at scale | Insert L-tier rows where Label is 500-char CJK string | No corruption; correct retrieval; `XBase-Backup-Verify` passes |
| `XBASE-STRESS-013` | Max TEXT length at scale | Insert M-tier rows with 10 000-char Label | All stored and retrieved correctly |
| `XBASE-STRESS-014` | Backup during inserts | Start backup while concurrently inserting 10 000 rows | Backup reflects pre-backup committed state; no error |

---

## Security Tests

| ID | Description | Attack Vector | Pass Criterion |
|---|---|---|---|
| `XBASE-SEC-001` | Path traversal in `DatabaseName` | `DatabaseName:"../outside"` | Returns `XBASE_DATABASE_PATH_INVALID`; no directory created outside `AiXBase/` |
| `XBASE-SEC-002` | Path traversal in `TableName` | `TableName:"../secret"` | Returns validation error; no file accessed outside database directory |
| `XBASE-SEC-003` | Injection in `ColumnName` | `Name:"Id\"); DROP TABLE Users--"` | Returns `XBASE_SCHEMA_COLUMN_INVALID`; no unexpected change to `_schema.json` |
| `XBASE-SEC-004` | Injection attempt in filter `Value` | `Value:"' OR '1'='1"` with `Operator:"="` | Treated as a literal string in in-memory comparison; no extra rows returned |
| `XBASE-SEC-005` | Null byte in `DatabaseName` | `DatabaseName:"test\x00evil"` | Returns `XBASE_DATABASE_PATH_INVALID`; null byte rejected |
| `XBASE-SEC-006` | Null byte in column value | `Value:"hello\x00world"` | Stored as JSON string with the null character; retrieved as-is; no truncation |
| `XBASE-SEC-007` | Path traversal in `BackupPath` input | `BackupPath:"../../Windows/System32/evil"` | Returns error; no file written outside `AiXBase/` |
| `XBASE-SEC-008` | Homoglyph attack in table name | `TableName:"Uѕerѕ"` (Cyrillic `ѕ`) | Treated as a different name from `Users`; no unintended access |
| `XBASE-SEC-009` | Excessive `Limit` value | `Limit:2147483647` | Executes (returns all rows) or caps at a safe maximum; no integer overflow crash |
| `XBASE-SEC-010` | Negative `Offset` | `Offset:-1` | Returns validation error or treated as 0; no crash |
| `XBASE-SEC-011` | Injection in `TransactionName` | `TransactionName:"../live"` | Returns `XBASE_DATABASE_PATH_INVALID`; no directory created outside database directory |
| `XBASE-SEC-012` | ConfirmDrop spoofing | `ConfirmDrop:"true"` (string not bool) | Rejected or coerced to `false`; drop not executed |
| `XBASE-SEC-013` | Field name injection in filter | `Field:"IsDeleted=0 OR 1=1 --"` | Returns `XBASE_FILTER_FIELD_INVALID` |

---

## Acceptance Criteria

A build of XBase is considered **release-ready** when:

1. **All functional tests pass** — every `XBASE-DB-*`, `XBASE-SCH-*`, `XBASE-REC-*`, `XBASE-QRY-*`, `XBASE-IDX-*`, `XBASE-TXN-*`, `XBASE-BAK-*` test ID returns the stated expected result with no exceptions or unhandled errors.

2. **All performance benchmarks pass** — the median result of 3 runs meets or beats every target in `XBASE-PERF-*`.

3. **All stress tests pass** — every `XBASE-STRESS-*` test completes without process crash, data corruption, or orphaned workspace directories. `XBase-Backup-Verify` returns `IntegrityOk: true` after each stress test that writes data.

4. **All security tests pass** — every `XBASE-SEC-*` test produces the stated pass criterion with no path traversal, field injection, or data exposure.
