# Product Requirements Document: XBase Universal SQL

## Overview

XBase Universal SQL (UniversalSQL) is a SQL translation layer that sits above the existing 30 XBase skills. It accepts a standard SQL statement as plain text, parses it into an abstract syntax tree (AST), maps the AST to one or more XBase skill calls, executes them, and returns the result in the standard XBase JSON envelope.

**No new file I/O primitives are introduced.** All reads and writes continue to route through existing XBase skills. UniversalSQL is a pure orchestration layer — it parses, validates, and dispatches; it never touches the file system directly.

**Naming convention:**

```
XBase-UniversalSQL-{Operation}
```

Examples: `XBase-UniversalSQL-Execute`, `XBase-UniversalSQL-Parse`

**Dependency:** All UniversalSQL skills require an active `XBase-Database-Connect` session. They are harness-agnostic: any AI agent that can invoke skill files and perform in-memory string operations can run UniversalSQL without modification.

---

## Supported SQL Dialect

UniversalSQL implements a deterministic subset of SQL:2003. The supported statements are defined exactly below; anything not in this list returns `USQL_PARSE_UNSUPPORTED_STATEMENT`.

### Data Definition Language (DDL)

```sql
-- Create a table
CREATE TABLE [IF NOT EXISTS] table_name (
    column_name data_type [NOT NULL] [UNIQUE] [PRIMARY KEY] [DEFAULT literal]
                          [REFERENCES other_table(other_column)],
    ...
)

-- Drop a table
DROP TABLE [IF EXISTS] table_name

-- Add columns
ALTER TABLE table_name ADD COLUMN column_name data_type [NOT NULL] [DEFAULT literal]

-- Index management
CREATE [UNIQUE] INDEX [IF NOT EXISTS] index_name ON table_name (column, ...)
DROP INDEX [IF EXISTS] index_name
```

### Data Manipulation Language (DML)

```sql
-- Select
SELECT [DISTINCT] { * | column [AS alias], ... }
FROM table_name [AS alias]
[{ INNER | LEFT } JOIN table_name [AS alias] ON left_col = right_col]
[WHERE condition]
[GROUP BY column, ...]
[ORDER BY column [ASC | DESC], ...]
[LIMIT n]
[OFFSET n]

-- Insert (values)
INSERT INTO table_name [(column, ...)] VALUES (literal, ...) [, (literal, ...)]

-- Insert (select)
INSERT INTO table_name [(column, ...)] SELECT ...

-- Update
UPDATE table_name SET column = literal [, column = literal] WHERE condition

-- Delete
DELETE FROM table_name WHERE condition

-- Upsert (XBase extension)
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
DESCRIBE table_name                 -- alias: SHOW COLUMNS FROM table_name

BACKUP DATABASE database_name [LABEL label_string]
RESTORE DATABASE database_name FROM backup_path [CONFIRM]

EXPLAIN { SELECT | INSERT | UPDATE | DELETE | ... }   -- execution plan only; no execution
```

---

## SQL → XBase Skill Mapping

| SQL Construct | XBase Skills Invoked |
|---|---|
| `SELECT` | `XBase-Record-Select` |
| `WHERE` | `XBase-Query-Filter` |
| `ORDER BY` | `XBase-Query-Sort` |
| `INNER JOIN` / `LEFT JOIN` | `XBase-Query-Join` |
| `GROUP BY` + aggregate functions | `XBase-Query-Aggregate` |
| `INSERT ... VALUES` | `XBase-Record-Insert` |
| `INSERT ... SELECT` | `XBase-Record-Select` → `XBase-Record-Insert` |
| `UPDATE ... SET ... WHERE` | `XBase-Record-Update` + `XBase-Query-Filter` |
| `DELETE FROM ... WHERE` | `XBase-Record-Delete` + `XBase-Query-Filter` |
| `INSERT ... ON CONFLICT` | `XBase-Record-Upsert` |
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
| `EXPLAIN` | `XBase-UniversalSQL-Parse` (plan returned; no execution) |

---

## Data Type Mapping

### SQL Type → XBase Type

| SQL Types | XBase Type | Notes |
|---|---|---|
| `INTEGER`, `INT`, `BIGINT`, `SMALLINT`, `TINYINT` | `INTEGER` | |
| `TEXT`, `VARCHAR(n)`, `CHAR(n)`, `NVARCHAR(n)` | `TEXT` | Length annotation ignored; XBase TEXT is unbounded |
| `REAL`, `FLOAT`, `DOUBLE`, `NUMERIC(p,s)`, `DECIMAL(p,s)` | `REAL` | Precision/scale annotations ignored |
| `BOOLEAN`, `BOOL` | `INTEGER` | `TRUE` → `1`, `FALSE` → `0` |
| `DATE`, `DATETIME`, `TIMESTAMP` | `TEXT` | Stored as ISO-8601 string |
| `BLOB`, `BINARY`, `VARBINARY` | `TEXT` | Stored as base-64 string |
| *(unknown)* | `TEXT` | Unknown types accepted; stored as TEXT |

### XBase Type → SQL Type (for `EXPLAIN` and `DESCRIBE` output)

| XBase Type | Reported SQL Type |
|---|---|
| `INTEGER` | `INTEGER` |
| `TEXT` | `TEXT` |
| `REAL` | `REAL` |

---

## Constraint Mapping

| SQL Constraint | XBase Mechanism |
|---|---|
| `NOT NULL` | `Nullable: false` in column definition |
| `UNIQUE` | `Unique: true` in column definition |
| `PRIMARY KEY` | `PrimaryKey: true, AutoIncrement: true` (or explicit) |
| `DEFAULT literal` | `Default: literal` in column definition |
| `REFERENCES table(col)` | `ForeignKey: "table.col"` in column definition |
| `ON CONFLICT DO UPDATE` | Dispatched to `XBase-Record-Upsert` with `ConflictColumns` |

---

## Skill Catalog

| Skill | Description |
|---|---|
| `XBase-UniversalSQL-Execute` | Parse and execute a SQL statement against an XBase connection; return results |
| `XBase-UniversalSQL-Parse` | Parse a SQL statement into a structured execution plan object; no execution |
| `XBase-UniversalSQL-Explain` | Return a human-readable mapping of SQL clauses to XBase skill calls |
| `XBase-UniversalSQL-Validate` | Check SQL syntax and semantic correctness against the schema; no execution |

---

## Skill Specifications

### XBase-UniversalSQL-Execute

Parse and execute a SQL statement in one call.

**Inputs**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | Yes | — | Active XBase connection |
| `SQL` | string | Yes | — | The SQL statement to execute |
| `TransactionName` | string | No | — | Route all XBase skill calls through this transaction workspace |
| `Parameters` | object | No | `{}` | Named parameter bindings; substituted for `?name` placeholders in `SQL` |

**Outputs**

For `SELECT` / `SHOW TABLES` / `DESCRIBE`:
```json
{
  "Success": true,
  "StatementType": "SELECT",
  "Rows": [ { "Id": 1, "Label": "Alpha" } ],
  "TotalCount": 1,
  "ReturnedCount": 1,
  "ColumnNames": ["Id", "Label"]
}
```

For `INSERT`:
```json
{
  "Success": true,
  "StatementType": "INSERT",
  "InsertedCount": 3,
  "LastInsertedId": 42
}
```

For `UPDATE` / `DELETE`:
```json
{
  "Success": true,
  "StatementType": "UPDATE",
  "AffectedRows": 5
}
```

For DDL (`CREATE TABLE`, `DROP TABLE`, `ALTER TABLE`, `CREATE INDEX`, `DROP INDEX`):
```json
{
  "Success": true,
  "StatementType": "CREATE_TABLE",
  "TableName": "Products"
}
```

For TCL (`BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`):
```json
{
  "Success": true,
  "StatementType": "BEGIN",
  "TransactionName": "tx1"
}
```

**Steps**
1. Call `XBase-UniversalSQL-Validate` with `ConnectionName` and `SQL`; if `Valid: false`, return `Issues[0].Code` as the error code.
2. Substitute `Parameters` into any `?name` placeholders in `SQL`.
3. Call `XBase-UniversalSQL-Parse` to obtain the execution plan.
4. Dispatch each plan step to its mapped XBase skill, passing `TransactionName` where the step is a DML write.
5. Collect results; unify into the output envelope matching the statement type.
6. Return the unified result.

---

### XBase-UniversalSQL-Parse

Parse a SQL statement and return the execution plan — without executing any XBase skills.

**Inputs**

| Name | Type | Required | Description |
|---|---|---|---|
| `SQL` | string | Yes | The SQL statement to parse |
| `Parameters` | object | No | Named parameter bindings (substituted before parsing) |

**Outputs**

```json
{
  "Success": true,
  "StatementType": "SELECT",
  "AST": {
    "Type": "SelectStatement",
    "Columns":    [{ "TableAlias": null, "ColumnName": "*" }],
    "From":       { "TableName": "Products", "Alias": "p" },
    "Joins":      [],
    "Where":      { "Field": "Price", "Operator": ">", "Value": 50 },
    "GroupBy":    [],
    "OrderBy":    [{ "Field": "Label", "Direction": "ASC" }],
    "Limit":      25,
    "Offset":     0
  },
  "ExecutionPlan": [
    { "Step": 1, "Skill": "XBase-Query-Filter",  "Parameters": { "Field": "Price", "Operator": ">", "Value": 50 } },
    { "Step": 2, "Skill": "XBase-Query-Sort",    "Parameters": { "Columns": [{ "Field": "Label", "Direction": "ASC" }] } },
    { "Step": 3, "Skill": "XBase-Record-Select", "Parameters": { "TableName": "Products", "Limit": 25, "Offset": 0 } }
  ]
}
```

**Steps**
1. Substitute `Parameters` into `?name` placeholders.
2. Tokenise `SQL` into a token stream (keywords, identifiers, literals, operators, punctuation).
3. Parse the token stream into an AST using the grammar rules in the Supported SQL Dialect section; on syntax error return `USQL_PARSE_SYNTAX_ERROR` with position and context.
4. Verify the statement type is in the supported set; if not return `USQL_PARSE_UNSUPPORTED_STATEMENT`.
5. Map each AST node to an execution plan step using the SQL → XBase Skill Mapping table.
6. Return `StatementType`, `AST`, and `ExecutionPlan`.

---

### XBase-UniversalSQL-Explain

Render a human-readable breakdown showing how each SQL clause maps to an XBase skill call.

**Inputs**

| Name | Type | Required | Description |
|---|---|---|---|
| `SQL` | string | Yes | The SQL statement to explain |
| `ConnectionName` | string | No | If supplied, includes estimated row counts from schema |

**Outputs**

```json
{
  "Success": true,
  "StatementType": "SELECT",
  "ExplainText": "...",
  "Plan": [
    { "Step": 1, "Clause": "WHERE Price > 50", "Skill": "XBase-Query-Filter",  "Notes": "In-memory filter; full table scan (no index on Price)" },
    { "Step": 2, "Clause": "ORDER BY Label ASC", "Skill": "XBase-Query-Sort",  "Notes": "In-memory sort after filter" },
    { "Step": 3, "Clause": "SELECT * FROM Products LIMIT 25", "Skill": "XBase-Record-Select", "Notes": "Reads Products.dbf; returns first 25 matching rows" }
  ]
}
```

`ExplainText` is the `Plan` rendered as a markdown table, suitable for display directly to a user.

**Steps**
1. Call `XBase-UniversalSQL-Parse` → `ExecutionPlan`.
2. If `ConnectionName` supplied, call `XBase-Schema-TableList` and `XBase-Schema-ColumnList` for each referenced table to annotate index coverage.
3. For each plan step, compose a `Notes` string describing the operation, whether an index is used, and the expected read scope.
4. Render `ExplainText` as a markdown table with columns: Step, SQL Clause, XBase Skill, Notes.
5. Return `Plan` and `ExplainText`.

---

### XBase-UniversalSQL-Validate

Check a SQL statement for syntax errors and semantic errors against the live schema without executing.

**Inputs**

| Name | Type | Required | Description |
|---|---|---|---|
| `SQL` | string | Yes | The SQL statement to validate |
| `ConnectionName` | string | No | If supplied, semantic validation checks tables and columns against live schema |

**Outputs**

```json
{
  "Success": true,
  "Valid": false,
  "Issues": [
    { "Severity": "Error", "Code": "USQL_VALIDATE_COLUMN_NOT_FOUND", "Position": 12, "Message": "Column 'Bogus' not found in table 'Products'" }
  ],
  "IssueCount": 1
}
```

`Valid: true` when `Issues` contains no `Error`-severity entries. `Success` refers to the skill call itself succeeding, not to `Valid`.

**Checks performed**

| Phase | Check | Severity | Issue Code |
|---|---|---|---|
| Syntax | Token sequence matches grammar | Error | `USQL_PARSE_SYNTAX_ERROR` |
| Syntax | Statement type in supported set | Error | `USQL_PARSE_UNSUPPORTED_STATEMENT` |
| Syntax | Clause combination allowed (e.g. GROUP BY requires SELECT) | Error | `USQL_PARSE_UNSUPPORTED_CLAUSE` |
| Semantic | Table name exists in schema | Error | `USQL_VALIDATE_TABLE_NOT_FOUND` |
| Semantic | Column name exists in table | Error | `USQL_VALIDATE_COLUMN_NOT_FOUND` |
| Semantic | Column reference not ambiguous across joins | Error | `USQL_VALIDATE_AMBIGUOUS_COLUMN` |
| Semantic | Literal value compatible with column type | Warning | `USQL_VALIDATE_TYPE_MISMATCH` |
| Safety | `UPDATE` or `DELETE` without `WHERE` | Warning | `USQL_WHERE_REQUIRED` |
| Safety | `DROP TABLE` or `DROP INDEX` with no `IF EXISTS` | Info | `USQL_DROP_NO_IF_EXISTS` |

**Steps**
1. Tokenise and parse `SQL`; record any syntax errors.
2. If `ConnectionName` supplied and no syntax errors: call `XBase-Schema-TableList` and validate each referenced table.
3. For each valid table reference: call `XBase-Schema-ColumnList` and validate each referenced column.
4. Check clause combinations.
5. Check safety rules (missing WHERE on mutating statements, drop guards).
6. Return `Valid`, `Issues`, and `IssueCount`.

---

## Error Code Catalog

### Parse errors

| Code | Condition |
|---|---|
| `USQL_PARSE_SYNTAX_ERROR` | Token sequence does not match any supported grammar rule |
| `USQL_PARSE_UNSUPPORTED_STATEMENT` | Statement type (e.g. `MERGE`, `TRUNCATE`) is not in the supported set |
| `USQL_PARSE_UNSUPPORTED_CLAUSE` | A clause within a supported statement is not supported (e.g. `HAVING`) |
| `USQL_PARSE_PARAMETER_MISSING` | A `?name` placeholder has no matching entry in `Parameters` |

### Validation errors

| Code | Condition |
|---|---|
| `USQL_VALIDATE_TABLE_NOT_FOUND` | Table name in the SQL does not exist in `_schema.json` |
| `USQL_VALIDATE_COLUMN_NOT_FOUND` | Column name does not exist in the referenced table |
| `USQL_VALIDATE_AMBIGUOUS_COLUMN` | Column name appears in two or more joined tables with no table qualifier |
| `USQL_VALIDATE_TYPE_MISMATCH` | Literal value is incompatible with the column's XBase type |

### Execution errors

| Code | Condition |
|---|---|
| `USQL_EXECUTE_NO_CONNECTION` | `ConnectionName` not registered |
| `USQL_WHERE_REQUIRED` | `UPDATE` or `DELETE` submitted with no `WHERE` clause |

### Propagated XBase errors

All error codes from the underlying XBase skill set (e.g. `XBASE_RECORD_CONSTRAINT_VIOLATION`, `XBASE_SCHEMA_TABLE_NOT_FOUND`) are propagated unchanged in the error envelope.

---

## Non-Goals

UniversalSQL does not implement:

- `HAVING` clause (aggregate filters)
- Subqueries or correlated subqueries
- Window functions (`OVER`, `PARTITION BY`, `RANK`)
- `UNION`, `INTERSECT`, `EXCEPT`
- `TRUNCATE TABLE` (use `DELETE FROM t WHERE 1=1` instead)
- `MERGE`
- Stored procedures, functions, triggers, or views
- Multi-statement batches separated by `;` in one call
- `GRANT`, `REVOKE`, or any access-control SQL
- Schema-level or cross-database joins
- SQL comments inside the statement string (strip before passing)

---

## Dependencies

| Dependency | Purpose |
|---|---|
| `XBase-Database-Connect` | Session must be established before Execute or Validate |
| `XBase-Schema-TableList` | Semantic validation and SHOW TABLES |
| `XBase-Schema-ColumnList` | Semantic validation and DESCRIBE |
| `XBase-Schema-TableCreate` | `CREATE TABLE` |
| `XBase-Schema-TableDrop` | `DROP TABLE` |
| `XBase-Schema-TableAlter` | `ALTER TABLE ADD COLUMN` |
| `XBase-Record-Insert` | `INSERT` |
| `XBase-Record-Select` | `SELECT` |
| `XBase-Record-Update` | `UPDATE` |
| `XBase-Record-Delete` | `DELETE` |
| `XBase-Record-Upsert` | `INSERT ... ON CONFLICT` |
| `XBase-Query-Filter` | `WHERE` |
| `XBase-Query-Sort` | `ORDER BY` |
| `XBase-Query-Join` | `JOIN` |
| `XBase-Query-Aggregate` | `GROUP BY` + aggregate functions |
| `XBase-Query-Execute` | Compound queries (Select + Filter + Join + Aggregate in one call) |
| `XBase-Index-Create` | `CREATE INDEX` |
| `XBase-Index-Drop` | `DROP INDEX` |
| `XBase-Transaction-Begin` | `BEGIN` |
| `XBase-Transaction-Commit` | `COMMIT` |
| `XBase-Transaction-Rollback` | `ROLLBACK` |
| `XBase-Transaction-Savepoint` | `SAVEPOINT` |
| `XBase-Backup-Create` | `BACKUP DATABASE` |
| `XBase-Backup-Restore` | `RESTORE DATABASE` |
