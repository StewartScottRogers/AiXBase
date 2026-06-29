# Product Requirements Document: XBase Universal SQL Administrative Console

## Overview

The XBase Universal SQL Administrative Console provides three composable commands for interacting with XBase databases using standard SQL — without needing to know the individual XBase or UniversalSQL skill APIs.

The console is implemented across two delivery surfaces, each orchestrating the four UniversalSQL skills. No new file I/O primitives are added; all operations delegate to the UniversalSQL and XBase skill layers.

- **Distributable skills** (`SKILLS/XBase/UniversalSQL-Admin/`) — `repl.md`, `explain.md`, `schema.md` — packaged with the UniversalSQL skill set for distribution. These are harness-agnostic: any AI agent or runtime that can invoke skill files can use them.
- **Harness-specific invocation wrappers** — e.g. Claude Code slash commands (`.claude/commands/XBase/UniversalSQL-Admin/`) — `sql.proompt.md`, `explain.proompt.md`, `schema.proompt.md`. These are reference implementations for a specific harness and are not part of the distributable SKILLS package.

Both surfaces implement identical workflows. The Claude Code slash commands use the shorter `/sql`, `/explain`, `/schema` invocation names; the distributable skills use the full `repl`, `explain`, and `schema` names.

---

## Command Summary

| Role | SKILLS File | Slash Command | Description |
|---|---|---|---|
| **REPL** | `repl.md` | `/sql` (`sql.proompt.md`) | Interactive SQL shell — run SQL statements one at a time, view formatted results |
| **Explain** | `explain.md` | `/explain` (`explain.proompt.md`) | Show the XBase execution plan for a SQL statement without running it |
| **Schema** | `schema.md` | `/schema` (`schema.proompt.md`) | Extract and display `CREATE TABLE` DDL for tables in an XBase database |

---

## Architecture

```
User SQL input (or natural-language /explain / /schema request)
        │
        ▼
  UniversalSQL-Admin command layer    (repl / explain / schema — no direct file I/O)
        │
        ▼
  UniversalSQL skill layer            (Execute, Parse, Explain, Validate)
        │
        ▼
  XBase skill layer                   (30 existing skills — all file I/O here)
        │
        ▼
  XBaseFiles/ directory               (DBF files, _meta.json, _schema.json, .ndx files)
```

Admin commands are **orchestration only**. They manage the interactive loop, format output, and sequence skill calls. Every byte read from or written to disk goes through a named XBase skill.

---

## Command Specifications

### `/sql` — REPL (Interactive SQL Shell)

Accepts a SQL statement (or a plain-English description of an SQL operation) and executes it against a named XBase connection.

**Workflow:**

1. If no `ConnectionName` is supplied or no connection is open, prompt: `Database? (name or connection alias):` and call `XBase-Database-Connect`.
2. Accept the SQL statement from the user.
3. If the input looks like natural language (no SQL keywords at the start), attempt to infer the SQL statement and show it to the user before executing:
   `→ Running: SELECT * FROM Products WHERE Price > 10 ORDER BY Label`
4. Call `XBase-UniversalSQL-Validate` with the `ConnectionName`; if `Valid: false`, display issues and return to the prompt without executing.
5. Call `XBase-UniversalSQL-Execute` with the `ConnectionName` and `SQL`.
6. Format and display results (see Output Formats below).
7. Return to the SQL prompt. Repeat until the user types `EXIT` or `\q`.

**Output Formats:**

For `SELECT` / `SHOW TABLES` / `DESCRIBE`:
```
┌────┬──────┬───────────┬───────┐
│ Id │ SKU  │ Label     │ Price │
├────┼──────┼───────────┼───────┤
│  1 │ P001 │ Widget    │  9.99 │
│  2 │ P002 │ Gadget    │ 19.99 │
└────┴──────┴───────────┴───────┘
2 rows  (TotalCount: 2)
```

For `INSERT` / `UPDATE` / `DELETE`:
```
✓  3 rows affected
   LastInsertedId: 42
```

For DDL (`CREATE TABLE`, `DROP TABLE`, etc.):
```
✓  Table "Products" created (5 columns)
```

For TCL (`BEGIN`, `COMMIT`, `ROLLBACK`):
```
✓  Transaction "tx1" started
✓  Transaction "tx1" committed
```

For errors:
```
✗  XBASE_RECORD_CONSTRAINT_VIOLATION
   NOT NULL constraint failed on column "SKU"
```

**REPL Session State:**

The session tracks:
- `ConnectionName` — the current active connection alias
- `TransactionName` — if a `BEGIN` was issued without a matching `COMMIT` / `ROLLBACK`, subsequent DML statements are routed through this transaction
- Command history — previous SQL statements recallable with `/history` or `!n` (repeat statement n)

**Special REPL Commands:**

| Command | Action |
|---|---|
| `EXIT` or `\q` | Close the connection and exit the session |
| `\t table_name` | Shortcut for `DESCRIBE table_name` |
| `\l` | Shortcut for `SHOW TABLES` |
| `\history` | List the last 20 SQL statements from the current session |
| `!n` | Re-execute the nth statement from history |
| `\explain SQL` | Call `/explain` on the SQL without executing it |
| `\schema [table]` | Call `/schema` for the current database (optional: one table) |

**Example invocations:**
```sql
SELECT * FROM Products WHERE Price > 10 ORDER BY Label
INSERT INTO Products (SKU, Label, Price) VALUES ('P099', 'Doohickey', 4.99)
BEGIN TRANSACTION batch
UPDATE Products SET IsActive = 0 WHERE Price < 1.00
COMMIT batch
SHOW TABLES
DESCRIBE Orders
```

---

### `/explain` — Execution Plan Inspector

Accepts a SQL statement and returns a human-readable execution plan showing which XBase skills will be called and how the SQL maps to them — **without executing the statement**.

**Workflow:**
1. Accept the SQL statement from the user (or parse it from `/explain SELECT ...` syntax).
2. If `ConnectionName` available, call `XBase-UniversalSQL-Explain` with it; otherwise call without (syntax-only plan, no index annotations).
3. Display the `ExplainText` markdown table.
4. If any validation warnings or info issues exist (from internal `Validate` call), display them after the plan.

**Output example:**
```
Execution Plan for: SELECT * FROM Products WHERE Price > 10 ORDER BY Label LIMIT 25

Step │ SQL Clause                     │ XBase Skill           │ Notes
─────┼────────────────────────────────┼───────────────────────┼──────────────────────────────────
  1  │ WHERE Price > 10               │ XBase-Query-Filter    │ Full table scan (no index on Price)
  2  │ ORDER BY Label ASC             │ XBase-Query-Sort      │ In-memory sort after filter
  3  │ SELECT * FROM Products LIMIT 25│ XBase-Record-Select   │ Reads Products.dbf; returns ≤ 25 rows

⚠  No index on column "Price" — consider: CREATE INDEX idx_price ON Products (Price)
```

**Example invocations:**
```
/explain SELECT * FROM Products WHERE Price > 10 ORDER BY Label
/explain UPDATE Products SET IsActive = 0 WHERE Price < 1.00
/explain BEGIN TRANSACTION tx1
```

---

### `/schema` — SQL DDL Extractor

Reads the XBase `_schema.json` for a database and emits equivalent `CREATE TABLE` SQL for all or specified tables. Useful for documentation, cross-database migration, and understanding the schema in familiar SQL syntax.

**Workflow:**
1. Accept an optional `DatabaseName` or `ConnectionName` and an optional list of table names.
2. Call `XBase-Schema-TableList` to enumerate tables (filtered to the requested subset if supplied).
3. For each table, call `XBase-Schema-ColumnList` to retrieve column definitions.
4. Emit one `CREATE TABLE IF NOT EXISTS` block per table, mapping XBase types and constraints back to SQL.
5. Append `CREATE INDEX` statements for each index defined in `_schema.json`.
6. Display the full DDL block in a fenced SQL code block.

**Output example:**
```sql
-- XBase Schema: inventory
-- Generated: 2026-06-29T15:50:00Z

CREATE TABLE IF NOT EXISTS Products (
    Id        INTEGER  NOT NULL  PRIMARY KEY,
    SKU       TEXT     NOT NULL  UNIQUE,
    Label     TEXT     NOT NULL,
    Price     REAL,
    IsActive  INTEGER  NOT NULL  DEFAULT 1,
    CreatedAt TEXT,
    UpdatedAt TEXT,
    IsDeleted INTEGER  NOT NULL  DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Orders (
    Id         INTEGER  NOT NULL  PRIMARY KEY,
    ProductId  INTEGER  NOT NULL  REFERENCES Products(Id),
    Quantity   INTEGER  NOT NULL,
    OrderedAt  TEXT,
    CreatedAt  TEXT,
    UpdatedAt  TEXT,
    IsDeleted  INTEGER  NOT NULL  DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_orders_product ON Orders (ProductId);
```

**Example invocations:**
```
/schema inventory
/schema inventory Products
/schema (uses currently open connection)
```

---

## File Layout

```
SKILLS/XBase/UniversalSQL-Admin/
├── repl.md        Interactive SQL shell
├── explain.md     Execution plan display
└── schema.md      SQL DDL extractor

.claude/commands/XBase/UniversalSQL-Admin/
├── sql.proompt.md      Slash command — same workflow as repl.md
├── explain.proompt.md  Slash command — same workflow as explain.md
└── schema.proompt.md   Slash command — same workflow as schema.md
```

---

## Non-Goals

- The admin console does not implement its own file I/O — all reads and writes go through the skill layer
- It does not add new error codes beyond what UniversalSQL and XBase define
- It does not provide a GUI or web interface — output is markdown text to stdout
- It does not save session history between separate invocations (history is in-session only)
- It does not support multi-statement batches delimited by `;` — each invocation accepts one statement
- The `/schema` command is read-only; it does not modify the database

---

## Dependencies

| Dependency | Required by |
|---|---|
| `XBase-Database-Connect` | REPL (session setup) |
| `XBase-Database-Disconnect` | REPL (session teardown on EXIT) |
| `XBase-UniversalSQL-Execute` | REPL (statement execution) |
| `XBase-UniversalSQL-Validate` | REPL (pre-execution validation) |
| `XBase-UniversalSQL-Parse` | Explain (via Explain skill) |
| `XBase-UniversalSQL-Explain` | Explain command |
| `XBase-Schema-TableList` | Schema command; Explain (index annotations) |
| `XBase-Schema-ColumnList` | Schema command; Explain (index annotations) |
| `XBase-Index-List` | Schema command (index DDL generation) |
