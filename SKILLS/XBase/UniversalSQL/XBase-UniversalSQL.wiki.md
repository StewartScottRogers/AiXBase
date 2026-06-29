# XBase UniversalSQL

XBase UniversalSQL is a SQL translation layer that sits above the 35 XBase skills. It accepts a standard SQL statement as plain text, parses it into an abstract syntax tree (AST), maps the AST to one or more XBase skill calls, executes them, and returns the result in the standard XBase JSON envelope.

**No new file I/O primitives are introduced.** All reads and writes continue to route through existing XBase skills. UniversalSQL is a pure orchestration layer — it parses, validates, and dispatches. It never touches the file system directly.

All UniversalSQL skills require an active `XBase-Database-Connect` session. They are harness-agnostic: any AI agent that can invoke skill files and perform in-memory string operations can run UniversalSQL.

---

## Supported SQL Dialect

UniversalSQL implements a deterministic subset of SQL:2003. Anything outside this list returns `USQL_PARSE_UNSUPPORTED_STATEMENT`.

### Data Definition Language (DDL)

```sql
CREATE TABLE [IF NOT EXISTS] table_name (
    column_name data_type [NOT NULL] [UNIQUE] [PRIMARY KEY] [DEFAULT literal]
                          [REFERENCES other_table(other_column)],
    ...
)

DROP TABLE [IF EXISTS] table_name

ALTER TABLE table_name ADD COLUMN column_name data_type [NOT NULL] [DEFAULT literal]

CREATE [UNIQUE] INDEX [IF NOT EXISTS] index_name ON table_name (column, ...)
DROP INDEX [IF EXISTS] index_name
```

### Data Manipulation Language (DML)

```sql
SELECT [DISTINCT] { * | column [AS alias], ... }
FROM table_name [AS alias]
[{ INNER | LEFT } JOIN table_name [AS alias] ON left_col = right_col]
[WHERE condition]
[GROUP BY column, ...]
[ORDER BY column [ASC | DESC], ...]
[LIMIT n]
[OFFSET n]

INSERT INTO table_name [(column, ...)] VALUES (literal, ...) [, (literal, ...)]

INSERT INTO table_name [(column, ...)] SELECT ...

UPDATE table_name SET column = literal [, column = literal] WHERE condition

DELETE FROM table_name WHERE condition

INSERT INTO table_name [(column, ...)] VALUES (literal, ...)
ON CONFLICT (column, ...) DO UPDATE SET column = excluded.column, ...
```

### Transaction Control Language (TCL)

```sql
BEGIN [TRANSACTION] [transaction_name]
COMMIT [transaction_name]
ROLLBACK [TRANSACTION [transaction_name] | TO SAVEPOINT savepoint_name]
SAVEPOINT savepoint_name
```

### Meta Statements

```sql
SHOW TABLES
DESCRIBE table_name
SHOW COLUMNS FROM table_name

BACKUP DATABASE database_name [LABEL label_string]
RESTORE DATABASE database_name FROM backup_path [CONFIRM]

EXPLAIN { SELECT | INSERT | UPDATE | DELETE | ... }
```

### Non-Goals (explicitly not supported)

- `HAVING` clause
- Subqueries or correlated subqueries
- Window functions (`OVER`, `PARTITION BY`)
- `UNION`, `INTERSECT`, `EXCEPT`
- `TRUNCATE TABLE` (use `DELETE FROM t WHERE 1=1`)
- `MERGE`
- Multi-statement batches (`;`-separated in one call)
- SQL comments inside the statement string (strip before passing)

---

## SQL → XBase Skill Mapping

| SQL Construct | XBase Skills Invoked |
|---|---|
| `SELECT` | `XBase-Record-Select` |
| `WHERE` | `XBase-Query-Filter` |
| `ORDER BY` | `XBase-Query-Sort` |
| `INNER JOIN` / `LEFT JOIN` | `XBase-Query-Join` |
| `GROUP BY` + aggregate functions | `XBase-Query-Aggregate` |
| `INSERT … VALUES` | `XBase-Record-Insert` |
| `INSERT … SELECT` | `XBase-Record-Select` → `XBase-Record-Insert` |
| `UPDATE … SET … WHERE` | `XBase-Record-Update` + `XBase-Query-Filter` |
| `DELETE FROM … WHERE` | `XBase-Record-Delete` + `XBase-Query-Filter` |
| `INSERT … ON CONFLICT` | `XBase-Record-Upsert` |
| `CREATE TABLE` | `XBase-Schema-TableCreate` |
| `DROP TABLE` | `XBase-Schema-TableDrop` |
| `ALTER TABLE ADD COLUMN` | `XBase-Schema-TableAlter` |
| `CREATE INDEX` | `XBase-Index-Create` |
| `DROP INDEX` | `XBase-Index-Drop` |
| `SHOW TABLES` | `XBase-Schema-TableList` |
| `DESCRIBE` / `SHOW COLUMNS` | `XBase-Schema-ColumnList` |
| `BEGIN` | `XBase-Transaction-Begin` |
| `COMMIT` | `XBase-Transaction-Commit` |
| `ROLLBACK` | `XBase-Transaction-Rollback` |
| `SAVEPOINT` | `XBase-Transaction-Savepoint` |
| `BACKUP DATABASE` | `XBase-Backup-Create` |
| `RESTORE DATABASE` | `XBase-Backup-Restore` |
| `EXPLAIN` | `XBase-UniversalSQL-Parse` (plan only; no execution) |

---

## Data Type Mapping

| SQL Types | XBase Type | Notes |
|---|---|---|
| `INTEGER`, `INT`, `BIGINT`, `SMALLINT`, `TINYINT` | `INTEGER` | |
| `TEXT`, `VARCHAR(n)`, `CHAR(n)`, `NVARCHAR(n)` | `TEXT` | Length annotation ignored; XBase TEXT is unbounded |
| `REAL`, `FLOAT`, `DOUBLE`, `NUMERIC(p,s)`, `DECIMAL(p,s)` | `REAL` | Precision/scale annotations ignored |
| `BOOLEAN`, `BOOL` | `INTEGER` | `TRUE` → `1`, `FALSE` → `0` |
| `DATE`, `DATETIME`, `TIMESTAMP` | `TEXT` | Stored as ISO-8601 string |
| `BLOB`, `BINARY`, `VARBINARY` | `TEXT` | Stored as base-64 string |
| *(unknown)* | `TEXT` | Unknown types accepted; stored as TEXT |

---

## Skill Groups

### Core (4 skills)

**`XBase-UniversalSQL-Parse`** tokenises a SQL statement and maps it to an AST and an ordered execution plan — without invoking any XBase skills or touching the file system. Use it to inspect what a statement would do before running it, or to feed its output into `Explain`.

**`XBase-UniversalSQL-Validate`** checks syntax and, when a `ConnectionName` is supplied, also checks semantic correctness against the live schema (table existence, column existence, type compatibility). Returns a `Valid` flag and a list of issues with severity levels (Error, Warning, Info). `Execute` always calls `Validate` first and refuses to run if `Valid: false`.

**`XBase-UniversalSQL-Explain`** calls `Parse` then annotates each execution plan step with notes about index coverage, join strategy, read scope, and expected cost. Renders the result as a `Plan` array and as a markdown `ExplainText` table ready for direct display.

**`XBase-UniversalSQL-Execute`** is the main entry point. It calls `Validate`, then `Parse`, then dispatches each plan step to the appropriate XBase skill, collects results, and returns a unified output envelope shaped to the statement type (rows for SELECT, affected counts for DML, table name for DDL, transaction name for TCL).

### Admin (3 skills)

**`XBase-UniversalSQL-Admin-REPL`** (`repl.md`) is an interactive SQL shell. It accepts a SQL statement (or plain-English description) each turn, validates and executes it, and renders results as a Unicode box-drawing table. It maintains connection and transaction state across turns, supports REPL shortcuts (`\l`, `\t table`, `\history`, `!n`, `\explain`, `\schema`), and stays in a loop until the user types `EXIT` or `\q`.

**`XBase-UniversalSQL-Admin-Explain`** (`explain.md`) renders the execution plan for a SQL statement as a plain-text table with Step, SQL Clause, XBase Skill, and Notes columns. Appends index advisory lines for any columns without index coverage.

**`XBase-UniversalSQL-Admin-Schema`** (`schema.md`) reads the XBase `_schema.json` and emits equivalent `CREATE TABLE IF NOT EXISTS` DDL for all or specified tables, plus `CREATE INDEX IF NOT EXISTS` for each index. Output is in a fenced `sql` code block with a comment header.

---

## Error Code Catalog

### Parse errors

| Code | Condition |
|---|---|
| `USQL_PARSE_SYNTAX_ERROR` | Token sequence does not match any supported grammar rule |
| `USQL_PARSE_UNSUPPORTED_STATEMENT` | Statement type (e.g. `MERGE`) is not in the supported set |
| `USQL_PARSE_UNSUPPORTED_CLAUSE` | A clause within a supported statement is not supported |
| `USQL_PARSE_PARAMETER_MISSING` | A `?name` placeholder has no matching entry in `Parameters` |

### Validation errors

| Code | Severity | Condition |
|---|---|---|
| `USQL_VALIDATE_TABLE_NOT_FOUND` | Error | Table name does not exist in `_schema.json` |
| `USQL_VALIDATE_COLUMN_NOT_FOUND` | Error | Column name not defined in the referenced table |
| `USQL_VALIDATE_AMBIGUOUS_COLUMN` | Error | Column name is ambiguous across joined tables |
| `USQL_VALIDATE_TYPE_MISMATCH` | Warning | Literal value is incompatible with the column's XBase type |
| `USQL_WHERE_REQUIRED` | Warning | `UPDATE` or `DELETE` has no `WHERE` clause |
| `USQL_DROP_NO_IF_EXISTS` | Info | `DROP TABLE` or `DROP INDEX` lacks `IF EXISTS` guard |

### Execution errors

| Code | Condition |
|---|---|
| `USQL_EXECUTE_NO_CONNECTION` | `ConnectionName` not registered |
| `USQL_WHERE_REQUIRED` | `UPDATE` or `DELETE` submitted without `WHERE` |

All XBase skill error codes (e.g. `XBASE_RECORD_CONSTRAINT_VIOLATION`) are propagated unchanged.

---

## Getting Started

This walkthrough takes you from a plain SQL string to a SELECT result using the four core skills in sequence.

### Step 1 — Connect to a database

```
XBase-Database-Connect
  DatabaseName: "inventory"
  ConnectionName: "inv"
```

### Step 2 — Validate a SELECT before running it

```
XBase-UniversalSQL-Validate
  ConnectionName: "inv"
  SQL: "SELECT * FROM Products WHERE Price > 10 ORDER BY Label LIMIT 25"
```

Result: `Valid: true, IssueCount: 0`. If validation returns issues, inspect them before proceeding.

### Step 3 — Inspect the execution plan

```
XBase-UniversalSQL-Explain
  ConnectionName: "inv"
  SQL: "SELECT * FROM Products WHERE Price > 10 ORDER BY Label LIMIT 25"
```

Returns a `Plan` array and an `ExplainText` markdown table showing which XBase skills will run and whether any indexes are missing.

### Step 4 — Execute

```
XBase-UniversalSQL-Execute
  ConnectionName: "inv"
  SQL: "SELECT * FROM Products WHERE Price > 10 ORDER BY Label LIMIT 25"
```

Returns `Rows`, `TotalCount`, `ReturnedCount`, and `ColumnNames`.

### Step 5 — Run DML inside a transaction

```
XBase-UniversalSQL-Execute
  ConnectionName: "inv"
  SQL: "BEGIN TRANSACTION restock"

XBase-UniversalSQL-Execute
  ConnectionName: "inv"
  SQL: "UPDATE Products SET Stock = 50 WHERE Stock = 0"
  TransactionName: "restock"

XBase-UniversalSQL-Execute
  ConnectionName: "inv"
  SQL: "COMMIT restock"
```

### Step 6 — Use the interactive REPL

```
XBase-UniversalSQL-Admin-REPL
  ConnectionName: "inv"
  SQL: "SELECT Id, SKU, Price FROM Products LIMIT 5"
```

Displays a Unicode box-drawing table and stays in the prompt loop for follow-up statements.

---

## Claude Code Slash Commands

When using the Claude Code harness, three slash commands are available as thin wrappers around the Admin skills:

| Command | Skill | Description |
|---|---|---|
| `/sql` | `XBase-UniversalSQL-Admin-REPL` | Interactive SQL shell |
| `/explain` | `XBase-UniversalSQL-Admin-Explain` | Execution plan display |
| `/schema` | `XBase-UniversalSQL-Admin-Schema` | SQL DDL extractor |

These commands are installed in `.claude/commands/XBase/UniversalSQL-Admin/`. They are harness-specific reference implementations and are not part of the distributable `SKILLS/` package.
