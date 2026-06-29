# Product Requirements Document: XBase Universal SQL — Testing Criteria

## Overview

This document defines the complete set of acceptance tests, edge-case tests, error-condition tests, performance benchmarks, stress tests, and security tests required to certify that every XBase UniversalSQL Skill behaves correctly. A skill is considered **passing** only when every applicable test ID in this document produces the stated expected result.

Test IDs follow the pattern `USQL-<GROUP>-<NNN>` where group codes are:

| Code | Group |
|---|---|
| `DDL` | Data Definition Language (CREATE TABLE, DROP TABLE, ALTER TABLE, CREATE INDEX, DROP INDEX) |
| `SEL` | SELECT statements |
| `INS` | INSERT statements |
| `UPD` | UPDATE statements |
| `DEL` | DELETE statements |
| `JOIN` | JOIN clauses |
| `AGG` | Aggregate functions and GROUP BY |
| `TXN` | Transaction control (BEGIN, COMMIT, ROLLBACK, SAVEPOINT) |
| `BAK` | BACKUP and RESTORE |
| `EXP` | EXPLAIN and PARSE |
| `VAL` | VALIDATE |
| `PERF` | Performance benchmarks |
| `STRESS` | Stress tests |
| `SEC` | Security tests |

---

## Test Environment Requirements

| Requirement | Specification |
|---|---|
| Available disk space | ≥ 10 GB for performance and stress suites |
| RAM | ≥ 4 GB |
| OS | Any OS with a writable local file system |
| Database root | Writable local directory; default `XBaseFiles/` |
| Prerequisite | All 30 core XBase skills must pass XBase-Testing-PRD before UniversalSQL tests run |
| Prerequisite | All 4 UniversalSQL skills (`Execute`, `Parse`, `Explain`, `Validate`) must be loaded |
| Connection | Each test establishes its own `XBase-Database-Connect` and tears it down on completion |

---

## Test Data Specification

Each test creates and tears down its own database at `{DatabaseRoot}/usql-test-<ID>/`. Unless noted, tests use a two-table schema:

```sql
CREATE TABLE Products (
    Id      INTEGER PRIMARY KEY,
    SKU     TEXT NOT NULL UNIQUE,
    Label   TEXT NOT NULL,
    Price   REAL,
    IsActive INTEGER NOT NULL DEFAULT 1
)

CREATE TABLE Orders (
    Id         INTEGER PRIMARY KEY,
    ProductId  INTEGER NOT NULL REFERENCES Products(Id),
    Quantity   INTEGER NOT NULL,
    OrderedAt  TEXT
)
```

### Data Scale Tiers

| Tier | Row Count | Label |
|---|---|---|
| S | 100 | Small |
| M | 10 000 | Medium |
| L | 100 000 | Large |

---

## Test Cases: DDL

### CREATE TABLE

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-DDL-001` | `CREATE TABLE Items (Id INTEGER PRIMARY KEY, Name TEXT NOT NULL)` | `Success: true`; `StatementType: "CREATE_TABLE"`; `Items` table present in `_schema.json`; `Items.dbf` exists |
| `USQL-DDL-002` | `CREATE TABLE IF NOT EXISTS Products (...)` when Products already exists | `Success: true`; no error; schema unchanged |
| `USQL-DDL-003` | `CREATE TABLE Products (...)` when Products already exists (no `IF NOT EXISTS`) | Returns `XBASE_SCHEMA_TABLE_EXISTS` |
| `USQL-DDL-004` | Column with `NOT NULL` | Subsequent insert omitting that column returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-DDL-005` | Column with `UNIQUE` | Duplicate value insert returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-DDL-006` | Column with `DEFAULT 0` | Insert omitting that column; select shows `0` |
| `USQL-DDL-007` | Column with `REFERENCES Products(Id)` | Insert with non-existent `ProductId` returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-DDL-008` | Column with `PRIMARY KEY` | Implicit `Id AutoIncrement` not added when explicit PK supplied |
| `USQL-DDL-009` | `VARCHAR(255)` mapped to `TEXT` | Column type recorded as `TEXT` in `_schema.json` |
| `USQL-DDL-010` | `BOOLEAN` column | Type recorded as `INTEGER`; `TRUE` literal → `1`; `FALSE` → `0` |
| `USQL-DDL-011` | Zero-column CREATE | `CREATE TABLE Empty ()` | Returns `USQL_PARSE_SYNTAX_ERROR` or `XBASE_SCHEMA_COLUMN_INVALID` |
| `USQL-DDL-012` | Duplicate column names | `CREATE TABLE T (A TEXT, A INTEGER)` | Returns `XBASE_SCHEMA_COLUMN_INVALID` |

---

### DROP TABLE

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-DDL-013` | `DROP TABLE Products` | `Success: true`; `Products.dbf` deleted; entry removed from `_schema.json` |
| `USQL-DDL-014` | `DROP TABLE IF EXISTS NonExistent` | `Success: true`; no error |
| `USQL-DDL-015` | `DROP TABLE NonExistent` (no `IF EXISTS`) | Returns `XBASE_SCHEMA_TABLE_NOT_FOUND` |

---

### ALTER TABLE

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-DDL-016` | `ALTER TABLE Products ADD COLUMN Rating REAL` | `Success: true`; `Rating` column present in `_schema.json`; existing rows return `null` for `Rating` |
| `USQL-DDL-017` | Add column that already exists | Returns `XBASE_SCHEMA_COLUMN_EXISTS` |
| `USQL-DDL-018` | Add `NOT NULL` column without `DEFAULT` to populated table | Returns `XBASE_SCHEMA_COLUMN_INVALID` |
| `USQL-DDL-019` | Add `NOT NULL` column with `DEFAULT 0` to populated table | `Success: true`; existing rows return `0` |

---

### CREATE / DROP INDEX

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-DDL-020` | `CREATE INDEX idx_sku ON Products (SKU)` | `Success: true`; `.ndx` file created |
| `USQL-DDL-021` | `CREATE UNIQUE INDEX idx_sku ON Products (SKU)` | `Success: true`; `Unique: true` in `_schema.json` |
| `USQL-DDL-022` | `CREATE INDEX IF NOT EXISTS idx_sku ON Products (SKU)` (already exists) | `Success: true`; no error |
| `USQL-DDL-023` | `DROP INDEX idx_sku` | `Success: true`; `.ndx` file deleted |
| `USQL-DDL-024` | `DROP INDEX IF EXISTS NonExistent` | `Success: true`; no error |

---

## Test Cases: SELECT

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-SEL-001` | `SELECT * FROM Products` | All rows returned; `StatementType: "SELECT"` |
| `USQL-SEL-002` | `SELECT SKU, Label FROM Products` | Only `SKU` and `Label` columns in each row |
| `USQL-SEL-003` | `SELECT * FROM Products WHERE Price > 10` | Only rows where Price > 10 |
| `USQL-SEL-004` | `SELECT * FROM Products WHERE Price > 10 AND IsActive = 1` | Rows matching both conditions |
| `USQL-SEL-005` | `SELECT * FROM Products WHERE Price > 10 OR IsActive = 0` | Union of both conditions |
| `USQL-SEL-006` | `SELECT * FROM Products WHERE SKU LIKE 'SKU-%'` | Matching rows only |
| `USQL-SEL-007` | `SELECT * FROM Products WHERE SKU IN ('A', 'B', 'C')` | Exactly those rows |
| `USQL-SEL-008` | `SELECT * FROM Products WHERE Price IS NULL` | Rows with null Price |
| `USQL-SEL-009` | `SELECT * FROM Products WHERE Price IS NOT NULL` | Rows with non-null Price |
| `USQL-SEL-010` | `SELECT * FROM Products ORDER BY Price ASC` | Ascending order by Price |
| `USQL-SEL-011` | `SELECT * FROM Products ORDER BY Price DESC` | Descending order |
| `USQL-SEL-012` | `SELECT * FROM Products ORDER BY IsActive DESC, Label ASC` | Multi-column sort |
| `USQL-SEL-013` | `SELECT * FROM Products LIMIT 10` | At most 10 rows; `TotalCount` = full matching count |
| `USQL-SEL-014` | `SELECT * FROM Products LIMIT 10 OFFSET 20` | Rows 21–30 |
| `USQL-SEL-015` | `SELECT * FROM Products WHERE 1=1` | All rows (trivially true WHERE) |
| `USQL-SEL-016` | `SHOW TABLES` | `Rows` contains one entry per table in `_schema.json` |
| `USQL-SEL-017` | `DESCRIBE Products` | `Rows` contains one entry per column with Name, Type, Nullable, Default, PrimaryKey |
| `USQL-SEL-018` | `SHOW COLUMNS FROM Products` | Same result as `DESCRIBE Products` |
| `USQL-SEL-019` | SELECT from non-existent table | Returns `USQL_VALIDATE_TABLE_NOT_FOUND` |
| `USQL-SEL-020` | SELECT non-existent column | Returns `USQL_VALIDATE_COLUMN_NOT_FOUND` |
| `USQL-SEL-021` | `SELECT DISTINCT IsActive FROM Products` | At most 2 rows (0 and 1); no duplicates |
| `USQL-SEL-022` | `SELECT Id AS ProductId, Label AS Name FROM Products` | Columns named `ProductId` and `Name` in output |

---

## Test Cases: INSERT

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-INS-001` | `INSERT INTO Products (SKU, Label, Price) VALUES ('P001', 'Widget', 9.99)` | `InsertedCount: 1`; row retrievable via SELECT |
| `USQL-INS-002` | Multi-row insert: `INSERT INTO Products (SKU, Label) VALUES ('P001','A'), ('P002','B')` | `InsertedCount: 2` |
| `USQL-INS-003` | `INSERT INTO Products SELECT * FROM BackupProducts` (cross-table copy) | `InsertedCount` = row count of BackupProducts |
| `USQL-INS-004` | `INSERT INTO Products ... ON CONFLICT (SKU) DO UPDATE SET Price = excluded.Price` | `Action: "inserted"` on first call; `Action: "updated"` on second with same SKU |
| `USQL-INS-005` | Insert omitting NOT NULL column | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-INS-006` | Insert duplicate UNIQUE value | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-INS-007` | Insert FK value that does not exist in parent | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-INS-008` | `TRUE` literal into BOOLEAN column | Stored as `1`; retrieved as `1` |
| `USQL-INS-009` | `FALSE` literal into BOOLEAN column | Stored as `0` |
| `USQL-INS-010` | `NULL` literal into nullable column | Row has `null` for that field |
| `USQL-INS-011` | `NULL` literal into NOT NULL column | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-INS-012` | String with single quotes | `INSERT INTO Products (Label) VALUES ('it''s fine')` | Row stored with `it's fine`; no parse error |
| `USQL-INS-013` | Named parameter `?sku` | `SQL: "INSERT INTO Products (SKU) VALUES (?sku)"`, `Parameters: {sku:"P001"}` | `InsertedCount: 1` |

---

## Test Cases: UPDATE

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-UPD-001` | `UPDATE Products SET Price = 12.99 WHERE SKU = 'P001'` | `AffectedRows: 1`; row has `Price: 12.99` |
| `USQL-UPD-002` | `UPDATE Products SET IsActive = 0 WHERE Price < 1.00` | `AffectedRows` = count of matching rows; all now have `IsActive: 0` |
| `USQL-UPD-003` | `UPDATE Products SET Price = 0 WHERE SKU = 'NONE'` | `AffectedRows: 0`; no error |
| `USQL-UPD-004` | `UPDATE Products SET Price = NULL WHERE SKU = 'P001'` | Price is `null` for that row |
| `USQL-UPD-005` | Update multiple columns: `SET Price = 1.0, IsActive = 0 WHERE SKU = 'P001'` | Both columns updated |
| `USQL-UPD-006` | `UPDATE Products SET Price = 9.99` (no WHERE) | Returns `USQL_WHERE_REQUIRED` |
| `USQL-UPD-007` | Update to violate UNIQUE | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |
| `USQL-UPD-008` | Update to set NOT NULL column to NULL | Returns `XBASE_RECORD_CONSTRAINT_VIOLATION` |

---

## Test Cases: DELETE

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-DEL-001` | `DELETE FROM Products WHERE SKU = 'P001'` | `AffectedRows: 1`; row has `IsDeleted: 1` |
| `USQL-DEL-002` | `DELETE FROM Products WHERE Price < 1.00` | `AffectedRows` = matching count |
| `USQL-DEL-003` | `DELETE FROM Products WHERE SKU = 'NONE'` | `AffectedRows: 0`; no error |
| `USQL-DEL-004` | `DELETE FROM Products` (no WHERE) | Returns `USQL_WHERE_REQUIRED` |
| `USQL-DEL-005` | Delete already soft-deleted row | `AffectedRows: 1`; idempotent |

---

## Test Cases: JOIN

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-JOIN-001` | `SELECT p.SKU, o.Quantity FROM Products p INNER JOIN Orders o ON p.Id = o.ProductId` | Only Products that have at least one Order; correct Quantity values |
| `USQL-JOIN-002` | `SELECT p.SKU, o.Quantity FROM Products p LEFT JOIN Orders o ON p.Id = o.ProductId` | All Products; `Quantity: null` for Products with no Orders |
| `USQL-JOIN-003` | Join with WHERE | `... INNER JOIN Orders o ON ... WHERE o.Quantity > 5` | Filter applied after join |
| `USQL-JOIN-004` | Join with ORDER BY | `... INNER JOIN ... ORDER BY p.Label ASC` | Joined result sorted |
| `USQL-JOIN-005` | Join with LIMIT | `... INNER JOIN ... LIMIT 5` | At most 5 rows |
| `USQL-JOIN-006` | Ambiguous column name without qualifier | `SELECT Id FROM Products INNER JOIN Orders ON ...` | Returns `USQL_VALIDATE_AMBIGUOUS_COLUMN` |
| `USQL-JOIN-007` | Three-way join | `Products INNER JOIN Orders ON ... INNER JOIN ...` | All three tables joined in order |
| `USQL-JOIN-008` | Unsupported RIGHT JOIN | `RIGHT JOIN` | Returns `USQL_PARSE_UNSUPPORTED_CLAUSE` |

---

## Test Cases: Aggregate

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-AGG-001` | `SELECT COUNT(*) FROM Products` | `Rows: [{COUNT(*): n}]` where n = row count |
| `USQL-AGG-002` | `SELECT COUNT(Price) FROM Products` | Counts non-null Price values only |
| `USQL-AGG-003` | `SELECT SUM(Price) FROM Products` | Correct numeric sum |
| `USQL-AGG-004` | `SELECT AVG(Price) FROM Products` | Correct average |
| `USQL-AGG-005` | `SELECT MIN(Price), MAX(Price) FROM Products` | Correct boundary values |
| `USQL-AGG-006` | `SELECT COUNT(*) FROM Products WHERE IsActive = 1` | Count of active-only rows |
| `USQL-AGG-007` | `SELECT IsActive, COUNT(*) FROM Products GROUP BY IsActive` | Two rows: one per IsActive value |
| `USQL-AGG-008` | `SELECT IsActive, SUM(Price) FROM Products GROUP BY IsActive ORDER BY IsActive` | Grouped totals, sorted |
| `USQL-AGG-009` | Aggregate on empty table | `COUNT(*) = 0`; SUM/AVG/MIN/MAX = `null`; no crash |
| `USQL-AGG-010` | `SELECT COUNT(*) AS TotalProducts FROM Products` | Column named `TotalProducts` in output |
| `USQL-AGG-011` | `HAVING` clause | `SELECT IsActive, COUNT(*) FROM Products GROUP BY IsActive HAVING COUNT(*) > 10` | Returns `USQL_PARSE_UNSUPPORTED_CLAUSE` |

---

## Test Cases: Transaction Control

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-TXN-001` | `BEGIN TRANSACTION tx1` | `StatementType: "BEGIN"`, `TransactionName: "tx1"`; `_txn_tx1/` directory created |
| `USQL-TXN-002` | `BEGIN` (no name) | `StatementType: "BEGIN"`; auto-generated `TransactionName` in output |
| `USQL-TXN-003` | Insert in transaction, then commit | Rows visible after `COMMIT tx1` |
| `USQL-TXN-004` | Insert in transaction, then rollback | Rows absent after `ROLLBACK TRANSACTION tx1` |
| `USQL-TXN-005` | `SAVEPOINT sp1` | `StatementType: "SAVEPOINT"`; snapshot directory created |
| `USQL-TXN-006` | Insert B, savepoint sp1, insert C, rollback to sp1, commit | C absent; B present after commit |
| `USQL-TXN-007` | `ROLLBACK TO SAVEPOINT sp1` | Workspace rolled back to savepoint state; transaction still open |
| `USQL-TXN-008` | `COMMIT` with no open transaction | Returns `XBASE_TRANSACTION_NOT_OPEN` |
| `USQL-TXN-009` | `ROLLBACK` with no open transaction | Returns `XBASE_TRANSACTION_NOT_OPEN` |

---

## Test Cases: Backup and Restore

| ID | SQL | Expected Result |
|---|---|---|
| `USQL-BAK-001` | `BACKUP DATABASE usql-test-bak` | Backup created in `{DatabaseRoot}/backups/`; `BackupPath` in output |
| `USQL-BAK-002` | `BACKUP DATABASE usql-test-bak LABEL pre-test` | Backup directory name contains `pre-test` |
| `USQL-BAK-003` | `RESTORE DATABASE usql-test-bak FROM {BackupPath} CONFIRM` | Database restored; rows match backup state |
| `USQL-BAK-004` | `RESTORE DATABASE usql-test-bak FROM {BackupPath}` (no CONFIRM) | Returns `XBASE_RESTORE_NOT_CONFIRMED` |

---

## Test Cases: EXPLAIN and PARSE

### XBase-UniversalSQL-Parse

| ID | Description | SQL | Expected Result |
|---|---|---|---|
| `USQL-EXP-001` | Parse simple SELECT | `SELECT * FROM Products WHERE Price > 10` | `StatementType: "SELECT"`; `ExecutionPlan` has 3 steps: Filter, Sort (default ASC CreatedAt), Select |
| `USQL-EXP-002` | Parse INSERT | `INSERT INTO Products (SKU) VALUES ('X')` | `StatementType: "INSERT"`; plan step is `XBase-Record-Insert` |
| `USQL-EXP-003` | Parse JOIN | `SELECT * FROM Products INNER JOIN Orders ON Products.Id = Orders.ProductId` | Plan contains `XBase-Query-Join` step |
| `USQL-EXP-004` | Parse aggregate | `SELECT COUNT(*) FROM Products GROUP BY IsActive` | Plan contains `XBase-Query-Aggregate` step |
| `USQL-EXP-005` | Parse BEGIN | `BEGIN TRANSACTION tx1` | `StatementType: "BEGIN"` |
| `USQL-EXP-006` | Syntax error | `SELECT FROM` | Returns `USQL_PARSE_SYNTAX_ERROR` with position |
| `USQL-EXP-007` | Unsupported statement | `TRUNCATE TABLE Products` | Returns `USQL_PARSE_UNSUPPORTED_STATEMENT` |
| `USQL-EXP-008` | Named parameter substituted | `SELECT * FROM Products WHERE SKU = ?sku`, `Parameters: {sku:"P001"}` | AST WHERE value is `"P001"` |
| `USQL-EXP-009` | Missing parameter | `SELECT * FROM Products WHERE SKU = ?sku`, no Parameters | Returns `USQL_PARSE_PARAMETER_MISSING` |

### XBase-UniversalSQL-Explain

| ID | Description | SQL | Expected Result |
|---|---|---|---|
| `USQL-EXP-010` | Explain SELECT | `SELECT * FROM Products WHERE Price > 10 ORDER BY Label` | `ExplainText` rendered as markdown table; 3 plan steps |
| `USQL-EXP-011` | Explain with connection (index note) | `SELECT * FROM Products WHERE SKU = 'X'`; index on SKU exists | `Notes` for Filter step mentions index available |
| `USQL-EXP-012` | Explain with connection (no index) | `SELECT * FROM Products WHERE Price > 10`; no index on Price | `Notes` mentions full table scan |
| `USQL-EXP-013` | Explain INSERT | `INSERT INTO Products (SKU) VALUES ('X')` | Plan shows `XBase-Record-Insert`; notes show constraint checks |
| `USQL-EXP-014` | Explain JOIN | `SELECT * FROM Products INNER JOIN Orders ON ...` | Plan shows Join + Select steps |

---

## Test Cases: VALIDATE

| ID | Description | SQL | ConnectionName | Expected Result |
|---|---|---|---|---|
| `USQL-VAL-001` | Valid SELECT | `SELECT * FROM Products` | Supplied | `Valid: true`, `IssueCount: 0` |
| `USQL-VAL-002` | Syntax error | `SELECT FROM` | Not supplied | `Valid: false`; `USQL_PARSE_SYNTAX_ERROR` in Issues |
| `USQL-VAL-003` | Table not found | `SELECT * FROM Bogus` | Supplied | `Valid: false`; `USQL_VALIDATE_TABLE_NOT_FOUND` |
| `USQL-VAL-004` | Column not found | `SELECT Bogus FROM Products` | Supplied | `Valid: false`; `USQL_VALIDATE_COLUMN_NOT_FOUND` |
| `USQL-VAL-005` | Ambiguous column | `SELECT Id FROM Products INNER JOIN Orders ON Products.Id = Orders.ProductId` | Supplied | `Valid: false`; `USQL_VALIDATE_AMBIGUOUS_COLUMN` |
| `USQL-VAL-006` | UPDATE no WHERE | `UPDATE Products SET Price = 0` | Not supplied | `Valid: true` (syntax OK); `USQL_WHERE_REQUIRED` Warning in Issues |
| `USQL-VAL-007` | DELETE no WHERE | `DELETE FROM Products` | Not supplied | `Valid: true`; `USQL_WHERE_REQUIRED` Warning in Issues |
| `USQL-VAL-008` | DROP TABLE no IF EXISTS | `DROP TABLE Products` | Not supplied | `Valid: true`; `USQL_DROP_NO_IF_EXISTS` Info in Issues |
| `USQL-VAL-009` | Type mismatch warning | `INSERT INTO Products (Price) VALUES ('not-a-number')` | Supplied | `Valid: true`; `USQL_VALIDATE_TYPE_MISMATCH` Warning |
| `USQL-VAL-010` | Unsupported statement | `TRUNCATE TABLE Products` | Not supplied | `Valid: false`; `USQL_PARSE_UNSUPPORTED_STATEMENT` |
| `USQL-VAL-011` | No connection — semantic checks skipped | `SELECT Bogus FROM Products` | Not supplied | `Valid: true`; no table/column checks without a connection |

---

## Performance Benchmarks

All benchmarks use a dedicated database at `{DatabaseRoot}/usql-perf/`. Median of 3 runs must meet the target. The same SQL benchmark is compared with an equivalent direct XBase skill call; UniversalSQL overhead must not exceed 20% (i.e. parse + dispatch adds at most 20% to the underlying skill time).

| ID | Description | SQL | Data | Target |
|---|---|---|---|---|
| `USQL-PERF-001` | SELECT all rows — small | `SELECT * FROM Products` | S-tier (100 rows) | ≤ 500 ms including parse |
| `USQL-PERF-002` | SELECT all rows — medium | `SELECT * FROM Products` | M-tier (10 000 rows) | ≤ 2 s |
| `USQL-PERF-003` | SELECT with WHERE filter | `SELECT * FROM Products WHERE IsActive = 1` | M-tier | ≤ 2 s |
| `USQL-PERF-004` | INSERT single row | `INSERT INTO Products (SKU, Label) VALUES ('X', 'Y')` | — | ≤ 500 ms |
| `USQL-PERF-005` | INSERT 1 000 rows in a loop | 1 000 single-row INSERT calls | — | ≤ 30 s total |
| `USQL-PERF-006` | UPDATE matching rows | `UPDATE Products SET IsActive = 0 WHERE Price < 5` (50 rows match) | M-tier | ≤ 3 s |
| `USQL-PERF-007` | DELETE matching rows | `DELETE FROM Products WHERE Price < 5` (50 rows match) | M-tier | ≤ 3 s |
| `USQL-PERF-008` | SELECT with INNER JOIN | `SELECT ... FROM Products INNER JOIN Orders ON ...` | M-tier × 500 Orders | ≤ 4 s |
| `USQL-PERF-009` | COUNT aggregate | `SELECT COUNT(*) FROM Products` | L-tier (100 000 rows) | ≤ 3 s |
| `USQL-PERF-010` | GROUP BY aggregate | `SELECT IsActive, COUNT(*) FROM Products GROUP BY IsActive` | L-tier | ≤ 3 s |
| `USQL-PERF-011` | Parse overhead (syntax only) | `XBase-UniversalSQL-Parse` with no ConnectionName | Complex SELECT with JOIN and filter | ≤ 100 ms (pure parse; no I/O) |
| `USQL-PERF-012` | Validate overhead (semantic) | `XBase-UniversalSQL-Validate` with ConnectionName | Complex SELECT | ≤ 500 ms |
| `USQL-PERF-013` | TransactionalSQL bulk insert | `BEGIN` → 1 000 INSERTs → `COMMIT` | — | ≤ 15 s total |
| `USQL-PERF-014` | Parse + Execute vs direct XBase | Both paths; S-tier SELECT | S-tier | UniversalSQL ≤ 120% of direct call time |

---

## Stress Tests

| ID | Description | Setup | Pass Criterion |
|---|---|---|---|
| `USQL-STRESS-001` | Sustained INSERT load | `INSERT` 100 000 rows in batches of 1 000 via SQL | No crash; final row count correct; `XBase-Backup-Verify` passes |
| `USQL-STRESS-002` | Long SQL string | SELECT with 200-column projection and 50-condition WHERE | Parses and executes; no timeout |
| `USQL-STRESS-003` | IN clause with 1 000 values | `WHERE SKU IN ('A','B',...,'ZZZ')` | Executes correctly; no crash |
| `USQL-STRESS-004` | Rapid parse cycling | Call `XBase-UniversalSQL-Parse` 10 000 times with the same SQL | All succeed; no memory growth; all return identical results |
| `USQL-STRESS-005` | Transaction with 10 000 SQL inserts | `BEGIN` → 10 000 INSERTs → `COMMIT` | Commit succeeds; all 10 000 rows visible; workspace cleaned up |
| `USQL-STRESS-006` | Transaction with 10 000 SQL inserts → ROLLBACK | Same as above but `ROLLBACK` | All 10 000 rows absent; workspace directory deleted |
| `USQL-STRESS-007` | Concurrent VALIDATE calls | 50 simultaneous `VALIDATE` calls | All return correct result; no race condition on `_schema.json` |
| `USQL-STRESS-008` | Deeply chained JOIN | 5-table join | Returns result or returns `USQL_PARSE_UNSUPPORTED_CLAUSE`; must not crash |
| `USQL-STRESS-009` | Unicode in SQL literal | `WHERE Label = '测试 🎉 اختبار'` | Correct rows returned; no encoding error |
| `USQL-STRESS-010` | Very long literal value | `INSERT INTO Products (Label) VALUES ('x' * 10000)` | Row inserted and retrieved correctly |

---

## Security Tests

| ID | Description | Attack Vector | Pass Criterion |
|---|---|---|---|
| `USQL-SEC-001` | SQL injection in literal | `SELECT * FROM Products WHERE Label = ''; DROP TABLE Products--'` | The entire string `'; DROP TABLE Products--` is treated as a literal; no DROP executed; Products table intact |
| `USQL-SEC-002` | SQL injection via parameter | `Parameters: {sku: "'; DROP TABLE Products--"}` | Parameter value treated as a literal; no DROP executed |
| `USQL-SEC-003` | Path traversal in `DatabaseName` in BACKUP | `BACKUP DATABASE "../outside"` | Passed to `XBase-Backup-Create` which returns `XBASE_DATABASE_PATH_INVALID` |
| `USQL-SEC-004` | Path traversal in RESTORE path | `RESTORE DATABASE x FROM "../../etc/passwd" CONFIRM` | Passed to `XBase-Backup-Restore` which returns `XBASE_BACKUP_NOT_FOUND` or path-validation error |
| `USQL-SEC-005` | Null byte in string literal | `WHERE Label = "hello\x00world"` | Literal stored and compared as-is; no truncation; no directory traversal |
| `USQL-SEC-006` | UPDATE without WHERE guard | `UPDATE Products SET Price = 0` | Returns `USQL_WHERE_REQUIRED`; no XBase update skill called |
| `USQL-SEC-007` | DELETE without WHERE guard | `DELETE FROM Products` | Returns `USQL_WHERE_REQUIRED`; no delete skill called |
| `USQL-SEC-008` | RESTORE without CONFIRM | `RESTORE DATABASE x FROM path` | Returns `XBASE_RESTORE_NOT_CONFIRMED`; no files overwritten |
| `USQL-SEC-009` | Homoglyph in table name | `SELECT * FROM Рroducts` (Cyrillic Р) | Returns `USQL_VALIDATE_TABLE_NOT_FOUND`; `Products` table untouched |
| `USQL-SEC-010` | Oversized LIMIT | `SELECT * FROM Products LIMIT 2147483647` | Executes (returns all rows) or caps at a safe maximum; no integer overflow |
| `USQL-SEC-011` | Negative OFFSET | `SELECT * FROM Products LIMIT 10 OFFSET -1` | Returns `USQL_PARSE_SYNTAX_ERROR` or treats as `0`; no crash |
| `USQL-SEC-012` | `USQL_DROP_NO_IF_EXISTS` warning | `DROP TABLE Products` | Skill drops the table as directed; the warning is informational only — it does not block the statement |
| `USQL-SEC-013` | Comment stripping required | `SELECT * FROM Products -- where 1=0` | Returns `USQL_PARSE_SYNTAX_ERROR` (comments must be stripped before submission; inline comments are not supported) |

---

## Acceptance Criteria

A build of XBase UniversalSQL is considered **release-ready** when:

1. **All DDL tests pass** — every `USQL-DDL-*` test ID returns the stated result; type mapping and constraint mapping are correct.

2. **All DML tests pass** — every `USQL-SEL-*`, `USQL-INS-*`, `USQL-UPD-*`, `USQL-DEL-*` test ID returns the stated result; WHERE guards are enforced; parameter substitution is correct.

3. **All JOIN and aggregate tests pass** — every `USQL-JOIN-*` and `USQL-AGG-*` test ID returns the stated result; unsupported clauses (`HAVING`, `RIGHT JOIN`) return the correct error code.

4. **All transaction, backup, explain, and validate tests pass** — every `USQL-TXN-*`, `USQL-BAK-*`, `USQL-EXP-*`, and `USQL-VAL-*` test ID returns the stated result.

5. **All performance benchmarks pass** — the median of 3 runs meets every `USQL-PERF-*` target; UniversalSQL overhead over direct XBase skill calls does not exceed 20%.

6. **All stress tests pass** — every `USQL-STRESS-*` test completes without crash, data corruption, or orphaned transaction directories.

7. **All security tests pass** — every `USQL-SEC-*` test produces the stated pass criterion; no SQL injection, path traversal, or unauthorised destructive action occurs.

8. **Underlying XBase tests still pass** — running UniversalSQL tests against a database must not corrupt the database in a way that causes XBase-Testing-PRD tests to fail.
