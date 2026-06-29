# Product Requirements Document: XBase Universal SQL Administrative Console — Testing Criteria

## Overview

This document defines the acceptance tests, edge-case tests, error-condition tests, and security tests required to certify that all three XBase UniversalSQL Administrative Console commands — REPL, Explain, and Schema — behave correctly across both delivery surfaces (`SKILLS/XBase/UniversalSQL-Admin/` and `.claude/commands/XBase/UniversalSQL-Admin/`).

A command is considered **passing** only when every applicable test ID in this document produces the stated expected result.

Test IDs follow the pattern `USQL-ADM-<GROUP>-<NNN>` where group codes are:

| Code | Group |
|---|---|
| `REPL` | REPL command (`repl.md` / `sql.proompt.md`) |
| `EXP` | Explain command (`explain.md` / `explain.proompt.md`) |
| `SCH` | Schema command (`schema.md` / `schema.proompt.md`) |
| `SEC` | Security tests across all three commands |

---

## Test Environment Requirements

| Requirement | Specification |
|---|---|
| Available disk space | ≥ 1 GB |
| Database root | Writable local directory; default `XBaseFiles/` |
| Pre-existing test databases | Each test creates and tears down its own database at `{DatabaseRoot}/usql-adm-test-<ID>/` |
| Prerequisite: XBase | All 30 core XBase skills must pass XBase-Testing-PRD |
| Prerequisite: UniversalSQL | All 4 UniversalSQL skills must pass XBase-UniversalSQL-Testing-PRD |

**Harness note:** Tests for the distributable SKILLS files (`repl.md`, `explain.md`, `schema.md`) must pass under any compliant AI harness. The Claude Code slash command wrappers (`sql.proompt.md`, `explain.proompt.md`, `schema.proompt.md`) are a reference implementation tested separately; their failure does not block release of the harness-agnostic SKILLS package.

---

## Shared Test Schema

Unless a test specifies otherwise, the test database contains:

```sql
CREATE TABLE Products (
    Id       INTEGER PRIMARY KEY,
    SKU      TEXT NOT NULL UNIQUE,
    Label    TEXT NOT NULL,
    Price    REAL,
    IsActive INTEGER NOT NULL DEFAULT 1
)

CREATE TABLE Orders (
    Id        INTEGER PRIMARY KEY,
    ProductId INTEGER NOT NULL REFERENCES Products(Id),
    Quantity  INTEGER NOT NULL,
    OrderedAt TEXT
)

CREATE INDEX idx_products_sku ON Products (SKU)
```

Seeded with 10 Products (SKU: P001–P010, Price: 1.99–19.99) and 5 Orders.

---

## Test Cases: REPL Command

Tests cover `repl.md` (`/sql`) and, where a Claude Code environment is available, `sql.proompt.md`.

### Connection Setup

| ID | Scenario | Expected Behaviour |
|---|---|---|
| `USQL-ADM-REPL-001` | Open session, no `ConnectionName` supplied | Prompts `Database? (name or connection alias):`; does not call any skill until a name is provided |
| `USQL-ADM-REPL-002` | `ConnectionName` supplied in invocation | Session opens directly with that connection; no prompt |
| `USQL-ADM-REPL-003` | Supplied `ConnectionName` does not exist | Prompts user to check the name; calls `XBase-Database-Connect` which returns `XBASE_DATABASE_NOT_FOUND`; error displayed clearly |
| `USQL-ADM-REPL-004` | EXIT before entering any SQL | Session closes cleanly; `XBase-Database-Disconnect` called; connection deregistered |

### SQL Execution — Happy Path

| ID | SQL Input | Expected Output |
|---|---|---|
| `USQL-ADM-REPL-005` | `SELECT * FROM Products` | Table rendered with headers and 10 data rows; footer shows `10 rows (TotalCount: 10)` |
| `USQL-ADM-REPL-006` | `SELECT SKU, Price FROM Products WHERE Price > 10` | Only SKU and Price columns; rows with Price > 10 only |
| `USQL-ADM-REPL-007` | `INSERT INTO Products (SKU, Label, Price) VALUES ('P099', 'New', 5.00)` | `✓  1 rows affected` with `LastInsertedId` |
| `USQL-ADM-REPL-008` | `UPDATE Products SET IsActive = 0 WHERE SKU = 'P001'` | `✓  1 rows affected` |
| `USQL-ADM-REPL-009` | `DELETE FROM Products WHERE SKU = 'P001'` | `✓  1 rows affected` |
| `USQL-ADM-REPL-010` | `CREATE TABLE Temp (Id INTEGER PRIMARY KEY, Name TEXT)` | `✓  Table "Temp" created (2 columns)` |
| `USQL-ADM-REPL-011` | `DROP TABLE IF EXISTS Temp` | `✓  Table "Temp" dropped` |
| `USQL-ADM-REPL-012` | `BEGIN TRANSACTION tx1` | `✓  Transaction "tx1" started` |
| `USQL-ADM-REPL-013` | `COMMIT tx1` (after BEGIN) | `✓  Transaction "tx1" committed` |
| `USQL-ADM-REPL-014` | `SHOW TABLES` | Table rendered with one row per table; `Products` and `Orders` present |
| `USQL-ADM-REPL-015` | `DESCRIBE Products` | Table rendered with one row per column; Name, Type, Nullable, Default, PrimaryKey columns shown |

### Natural-Language Inference

| ID | Natural-Language Input | Expected Behaviour |
|---|---|---|
| `USQL-ADM-REPL-016` | `show me all products` | Displays inferred SQL: `→ Running: SELECT * FROM Products`; executes it |
| `USQL-ADM-REPL-017` | `get all active products sorted by price` | Infers `SELECT * FROM Products WHERE IsActive = 1 ORDER BY Price ASC`; shows inference before executing |
| `USQL-ADM-REPL-018` | `insert a product with SKU P099, Label Test, Price 1.00` | Infers `INSERT INTO Products (SKU, Label, Price) VALUES ('P099', 'Test', 1.00)` |
| `USQL-ADM-REPL-019` | Ambiguous natural language with no clear table | Asks `Which table?` before inferring SQL |

### Validation Before Execution

| ID | SQL Input | Expected Behaviour |
|---|---|---|
| `USQL-ADM-REPL-020` | `SELECT Bogus FROM Products` | `XBase-UniversalSQL-Validate` called; `USQL_VALIDATE_COLUMN_NOT_FOUND` displayed; no Execute called |
| `USQL-ADM-REPL-021` | `SELECT * FROM NonExistent` | `USQL_VALIDATE_TABLE_NOT_FOUND` displayed; no Execute called; session continues |
| `USQL-ADM-REPL-022` | `UPDATE Products SET Price = 0` (no WHERE) | Warning displayed: `USQL_WHERE_REQUIRED`; REPL asks `No WHERE clause — execute anyway? (y/n):`; executes only if user confirms |
| `USQL-ADM-REPL-023` | `DELETE FROM Products` (no WHERE) | Same confirmation prompt as REPL-022 |
| `USQL-ADM-REPL-024` | `SELECT FROM` (syntax error) | `USQL_PARSE_SYNTAX_ERROR` displayed with position; no Execute called |

### Transaction State Tracking

| ID | Scenario | Expected Behaviour |
|---|---|---|
| `USQL-ADM-REPL-025` | `BEGIN tx1` followed by `INSERT` | Insert uses `TransactionName:"tx1"`; visible in transaction workspace but not live |
| `USQL-ADM-REPL-026` | `BEGIN tx1` → `INSERT` → `ROLLBACK tx1` → `SELECT` | SELECT shows no new rows; row from insert absent |
| `USQL-ADM-REPL-027` | `BEGIN tx1` → `SAVEPOINT sp1` → `INSERT` → `ROLLBACK TO SAVEPOINT sp1` → `COMMIT tx1` | Insert rolled back; commit succeeds; no rows from the insert |
| `USQL-ADM-REPL-028` | `EXIT` with open transaction | REPL warns: `Open transaction "tx1" — commit or rollback before exiting?`; waits for choice; does not exit until transaction resolved or user confirms abandonment |

### Special REPL Commands

| ID | Input | Expected Behaviour |
|---|---|---|
| `USQL-ADM-REPL-029` | `\l` | Equivalent to `SHOW TABLES`; displays table list |
| `USQL-ADM-REPL-030` | `\t Products` | Equivalent to `DESCRIBE Products`; displays column list |
| `USQL-ADM-REPL-031` | `\history` | Lists up to 20 previous SQL statements from the current session, numbered |
| `USQL-ADM-REPL-032` | `!3` (after 3+ SQL statements) | Re-executes statement #3 from history; displays the SQL before running |
| `USQL-ADM-REPL-033` | `!3` (fewer than 3 statements in history) | Displays `No statement #3 in history` |
| `USQL-ADM-REPL-034` | `\explain SELECT * FROM Products WHERE Price > 10` | Displays explain plan without executing; returns to SQL prompt |
| `USQL-ADM-REPL-035` | `\schema` | Displays CREATE TABLE DDL for all tables in the current database |
| `USQL-ADM-REPL-036` | `\schema Products` | Displays CREATE TABLE DDL for Products only |
| `USQL-ADM-REPL-037` | `EXIT` (clean exit) | `XBase-Database-Disconnect` called; connection deregistered; session ends |
| `USQL-ADM-REPL-038` | `\q` | Same as `EXIT` |

### Error Display

| ID | Scenario | Expected Output |
|---|---|---|
| `USQL-ADM-REPL-039` | UNIQUE constraint violation on INSERT | `✗  XBASE_RECORD_CONSTRAINT_VIOLATION` followed by plain-English explanation; session continues |
| `USQL-ADM-REPL-040` | FK violation on INSERT | `✗  XBASE_RECORD_CONSTRAINT_VIOLATION`; mentions which FK failed; session continues |
| `USQL-ADM-REPL-041` | `COMMIT` with no open transaction | `✗  XBASE_TRANSACTION_NOT_OPEN`; session continues |
| `USQL-ADM-REPL-042` | Zero-row UPDATE | `✓  0 rows affected`; no error |

---

## Test Cases: Explain Command

Tests cover `explain.md` (`/explain`) and, where available, `explain.proompt.md`.

### Happy Path

| ID | SQL | Expected Output |
|---|---|---|
| `USQL-ADM-EXP-001` | `SELECT * FROM Products WHERE Price > 10 ORDER BY Label LIMIT 25` | Markdown table with 3 steps: Filter → Sort → Select; `ExplainText` rendered |
| `USQL-ADM-EXP-002` | `SELECT * FROM Products` (no WHERE, no ORDER BY) | 1-step plan: Select with full-table-scan note |
| `USQL-ADM-EXP-003` | `INSERT INTO Products (SKU, Label) VALUES ('X', 'Y')` | Plan shows `XBase-Record-Insert` with constraint-check note |
| `USQL-ADM-EXP-004` | `UPDATE Products SET Price = 5 WHERE SKU = 'P001'` | Plan shows Filter → Update |
| `USQL-ADM-EXP-005` | `DELETE FROM Products WHERE Price < 1` | Plan shows Filter → Delete |
| `USQL-ADM-EXP-006` | `SELECT * FROM Products INNER JOIN Orders ON Products.Id = Orders.ProductId` | Plan shows Join → Select |
| `USQL-ADM-EXP-007` | `SELECT IsActive, COUNT(*) FROM Products GROUP BY IsActive` | Plan shows Aggregate → Select |
| `USQL-ADM-EXP-008` | `BEGIN TRANSACTION tx1` | Plan shows single step: `XBase-Transaction-Begin` |
| `USQL-ADM-EXP-009` | `CREATE TABLE T (Id INTEGER PRIMARY KEY)` | Plan shows `XBase-Schema-TableCreate` step |

### Index Annotations (ConnectionName supplied)

| ID | SQL | Setup | Expected Annotation |
|---|---|---|---|
| `USQL-ADM-EXP-010` | `SELECT * FROM Products WHERE SKU = 'P001'` | Index `idx_products_sku` exists on SKU | Step note: `Index idx_products_sku available — binary search` |
| `USQL-ADM-EXP-011` | `SELECT * FROM Products WHERE Price > 10` | No index on Price | Step note: `Full table scan (no index on Price)` — also shows `CREATE INDEX` suggestion |
| `USQL-ADM-EXP-012` | `SELECT * FROM Orders WHERE ProductId = 1` | No index on ProductId | Step note mentions full table scan and suggests creating index |

### Errors and Edge Cases

| ID | SQL | Expected Behaviour |
|---|---|---|
| `USQL-ADM-EXP-013` | `SELECT FROM` (syntax error) | Displays `USQL_PARSE_SYNTAX_ERROR` with position; no plan rendered |
| `USQL-ADM-EXP-014` | `TRUNCATE TABLE Products` | Displays `USQL_PARSE_UNSUPPORTED_STATEMENT`; no plan |
| `USQL-ADM-EXP-015` | Validate warnings shown | `UPDATE Products SET Price = 0` (no WHERE) | Plan rendered normally; `⚠ USQL_WHERE_REQUIRED` appended after plan |
| `USQL-ADM-EXP-016` | No execution guaranteed | Any statement | Command must never call `XBase-UniversalSQL-Execute`; only `Parse` and `Explain` |

---

## Test Cases: Schema Command

Tests cover `schema.md` (`/schema`) and, where available, `schema.proompt.md`.

### Happy Path

| ID | Input | Expected Output |
|---|---|---|
| `USQL-ADM-SCH-001` | `/schema` (current connection) | Fenced SQL block containing `CREATE TABLE IF NOT EXISTS` for all tables, then `CREATE INDEX IF NOT EXISTS` for all indexes |
| `USQL-ADM-SCH-002` | `/schema Products` (single table) | Only the `CREATE TABLE IF NOT EXISTS Products (...)` block and its indexes |
| `USQL-ADM-SCH-003` | `/schema usql-adm-test-sch` (database name) | Connects temporarily; emits full DDL; disconnects |
| `USQL-ADM-SCH-004` | Column with `NOT NULL` | Emitted as `NOT NULL` in DDL |
| `USQL-ADM-SCH-005` | Column with `UNIQUE` | Emitted as `UNIQUE` in DDL |
| `USQL-ADM-SCH-006` | Column with `DEFAULT 1` | Emitted as `DEFAULT 1` in DDL |
| `USQL-ADM-SCH-007` | Column with `REFERENCES Products(Id)` | Emitted as `REFERENCES Products(Id)` in DDL |
| `USQL-ADM-SCH-008` | Column with `PRIMARY KEY` | Emitted as `PRIMARY KEY` in DDL |
| `USQL-ADM-SCH-009` | UNIQUE index | Emitted as `CREATE UNIQUE INDEX IF NOT EXISTS ...` |
| `USQL-ADM-SCH-010` | Composite index | Emitted as `CREATE INDEX ... ON T (col1, col2)` with both columns |
| `USQL-ADM-SCH-011` | `INTEGER` column | Type emitted as `INTEGER` |
| `USQL-ADM-SCH-012` | `REAL` column | Type emitted as `REAL` |
| `USQL-ADM-SCH-013` | `TEXT` column | Type emitted as `TEXT` |
| `USQL-ADM-SCH-014` | Header comment | Output begins with `-- XBase Schema: {DatabaseName}` and `-- Generated: {ISO-8601 timestamp}` |

### Edge Cases

| ID | Scenario | Expected Behaviour |
|---|---|---|
| `USQL-ADM-SCH-015` | Empty database (no tables) | Outputs header comment only; `-- (no tables defined)` note |
| `USQL-ADM-SCH-016` | Table with no indexes | No `CREATE INDEX` line for that table |
| `USQL-ADM-SCH-017` | `/schema NonExistentTable` | Reports `XBASE_SCHEMA_TABLE_NOT_FOUND`; no partial output |
| `USQL-ADM-SCH-018` | Non-existent database name | Reports `XBASE_DATABASE_NOT_FOUND`; no DDL output |
| `USQL-ADM-SCH-019` | Read-only guarantee | Running `/schema` must not modify any file; all file timestamps unchanged after the command |
| `USQL-ADM-SCH-020` | Temporary connection cleaned up | If schema command opened its own connection, it must disconnect on exit | Connection alias deregistered after schema output |

### Round-Trip Fidelity

| ID | Scenario | Expected Behaviour |
|---|---|---|
| `USQL-ADM-SCH-021` | `/schema` output applied to a new database | Copy the DDL from `/schema`; run it against a fresh database via `XBase-UniversalSQL-Execute` calls; then run `/schema` on the new database | Both schema outputs are semantically identical (same tables, columns, constraints, indexes) |

---

## Security Tests

| ID | Description | Attack Vector | Pass Criterion |
|---|---|---|---|
| `USQL-ADM-SEC-001` | SQL injection in REPL literal | `SELECT * FROM Products WHERE Label = ''; DROP TABLE Products--'` | The string is treated as a SQL literal; `XBase-UniversalSQL-Execute` receives it as a literal comparison value; `Products` table intact |
| `USQL-ADM-SEC-002` | Path traversal in database name | REPL prompts for database name; user enters `../outside` | `XBase-Database-Connect` called with `DatabaseName:"../outside"`; returns `XBASE_DATABASE_NOT_FOUND` or `XBASE_DATABASE_PATH_INVALID`; no connection outside `{DatabaseRoot}/` |
| `USQL-ADM-SEC-003` | Injection in table name | `SELECT * FROM "../secret"` | Passed to `XBase-UniversalSQL-Validate`; returned as `USQL_VALIDATE_TABLE_NOT_FOUND` or `USQL_PARSE_SYNTAX_ERROR`; no file accessed outside database directory |
| `USQL-ADM-SEC-004` | UPDATE without WHERE — REPL guard | `UPDATE Products SET Price = 0` | REPL displays `USQL_WHERE_REQUIRED` warning and prompts for confirmation; does not call Execute unless user explicitly confirms |
| `USQL-ADM-SEC-005` | DELETE without WHERE — REPL guard | `DELETE FROM Products` | Same confirmation guard as SEC-004 |
| `USQL-ADM-SEC-006` | Open transaction on EXIT | `BEGIN tx1` in REPL; then EXIT | REPL warns about open transaction; does not disconnect until user resolves or explicitly abandons; no orphaned workspace directory left after confirmed exit |
| `USQL-ADM-SEC-007` | Path traversal in BACKUP via REPL | `BACKUP DATABASE "../outside"` | Passed to `XBase-Backup-Create`; returns `XBASE_DATABASE_PATH_INVALID`; no file created outside `{DatabaseRoot}/` |
| `USQL-ADM-SEC-008` | RESTORE without CONFIRM via REPL | `RESTORE DATABASE x FROM path` | Passed to `XBase-UniversalSQL-Execute` which calls `XBase-Backup-Restore`; returns `XBASE_RESTORE_NOT_CONFIRMED`; no files overwritten |
| `USQL-ADM-SEC-009` | Schema command leaves no modifications | `/schema` on any database | No file modification timestamps change; no new files created; no write skill called |
| `USQL-ADM-SEC-010` | Explain command leaves no modifications | `/explain SELECT * FROM Products` | No Execute skill called; no file modification timestamps change |
| `USQL-ADM-SEC-011` | Null byte in REPL literal | `WHERE Label = "hello\x00world"` | Passed to `XBase-UniversalSQL-Execute` as a literal; no directory traversal; stored and compared as-is |
| `USQL-ADM-SEC-012` | Injection in Explain SQL argument | `/explain SELECT * FROM Products; DROP TABLE Products` | Multi-statement separator `;` not supported; returns `USQL_PARSE_UNSUPPORTED_STATEMENT` or `USQL_PARSE_SYNTAX_ERROR`; Products table intact |

---

## Acceptance Criteria

An implementation of the XBase UniversalSQL Administrative Console is considered **release-ready** when:

1. **All REPL tests pass** — every `USQL-ADM-REPL-*` test produces the stated expected result, including connection management, SQL execution, natural-language inference, validation guards, transaction state tracking, special commands, and error display.

2. **All Explain tests pass** — every `USQL-ADM-EXP-001` through `USQL-ADM-EXP-016` test produces the stated output; `XBase-UniversalSQL-Execute` is never called by the Explain command.

3. **All Schema tests pass** — every `USQL-ADM-SCH-*` test produces syntactically valid SQL DDL that round-trips correctly; the command is read-only and cleans up any temporary connection.

4. **All security tests pass** — every `USQL-ADM-SEC-*` test produces the stated pass criterion; no SQL injection, path traversal, confirmation bypass, or unauthorised destructive action occurs.

5. **Harness-agnostic surface passes** — every test above must pass for the SKILLS distributable files (`repl.md`, `explain.md`, `schema.md`) under any compliant AI harness. Claude Code slash command wrappers (`sql.proompt.md`, `explain.proompt.md`, `schema.proompt.md`) are tested separately where a Claude Code environment is available, but their failure does not block release of the harness-agnostic SKILLS package.

6. **Underlying UniversalSQL and XBase tests still pass** — REPL session activity must not corrupt any database such that XBase-Testing-PRD or XBase-UniversalSQL-Testing-PRD tests fail on that database.
