# Product Requirements Document: XBase Administrative Console

## Overview

The XBase Administrative Console provides three composable commands for database administrators to inspect, operate, and maintain XBase databases through natural language — without needing to know the individual skill APIs.

The console is implemented across two delivery surfaces, each orchestrating the existing 28 XBase skills. No new file I/O primitives are added; all operations delegate to the underlying skill layer.

- **Distributable skills** (`SKILLS/XBase/Admin/`) — `execute.md`, `Inspect.md`, `maintain.md` — packaged with the XBase skill set for distribution
- **Claude Code slash commands** (`.claude/commands/XBase/Admin/`) — `do.proompt.md`, `this.proompt.md`, `that.proompt.md` — registered locally for CLI use

Both surfaces implement identical workflows. The slash commands use the shorter `/do`, `/this`, `/that` invocation names; the distributable skills use the longer `/execute`, `/Inspect`, `/maintain` names.

---

## Command Summary

| Role | SKILLS File | Slash Command | Description |
|---|---|---|---|
| **Execute** | `execute.md` | `/do` (`do.proompt.md`) | Run any XBase operation from a plain-English description |
| **Inspect** | `Inspect.md` | `/this` (`this.proompt.md`) | Display status, schema, record counts, and connection state |
| **Maintain** | `maintain.md` | `/that` (`that.proompt.md`) | Rebuild indexes, verify integrity, backup, vacuum |

---

## Architecture

```
User natural-language input
        │
        ▼
  Admin command layer      (do / this / that — no direct file I/O)
        │
        ▼
  XBase skill layer        (28 existing skills — all file I/O here)
        │
        ▼
  XBaseFiles/ directory    (NDJSON files, _meta.json, _schema.json, .ndx files)
```

Admin commands are **orchestration prompts only**. They parse intent, collect parameters, sequence skill calls, and present human-readable results. Every byte read from or written to disk goes through a named XBase skill.

---

## Command Specifications

### `/do` — Execute

Accepts a plain-English description of any XBase operation and executes it.

**Workflow:**
1. Parse the user's request to identify the operation type
2. Map to the appropriate XBase skill(s)
3. Ask for any missing required parameters before executing
4. Execute the skill(s) and present results in a readable summary

**Intent-to-skill mapping:**

| Natural-language intent | Skill(s) invoked |
|---|---|
| Create / initialise a database | `XBase-Database-Initialize` |
| Connect / open a database | `XBase-Database-Connect` |
| Close / disconnect | `XBase-Database-Disconnect` |
| Create a table | `XBase-Schema-TableCreate` |
| Alter a table | `XBase-Schema-TableAlter` |
| Drop a table | `XBase-Schema-TableDrop` |
| List tables | `XBase-Schema-TableList` |
| List columns | `XBase-Schema-ColumnList` |
| Insert / add records | `XBase-Record-Insert` |
| Query / show / find records | `XBase-Record-Select` + `XBase-Query-Filter` + `XBase-Query-Sort` |
| Update records | `XBase-Record-Update` |
| Delete / remove records | `XBase-Record-Delete` |
| Upsert | `XBase-Record-Upsert` |
| Create index | `XBase-Index-Create` |
| Drop index | `XBase-Index-Drop` |
| Rebuild index | `XBase-Index-Rebuild` |
| List indexes | `XBase-Index-List` |
| Begin transaction | `XBase-Transaction-Begin` |
| Commit transaction | `XBase-Transaction-Commit` |
| Rollback transaction | `XBase-Transaction-Rollback` |
| Create savepoint | `XBase-Transaction-Savepoint` |
| Backup database | `XBase-Backup-Create` |
| Restore backup | `XBase-Backup-Restore` |
| Verify backup | `XBase-Backup-Verify` |

**Destructive operation guard:** For any operation that deletes or overwrites data (`Drop`, `HardDelete`, `Restore`, `OverwriteIfExists`), require explicit confirmation from the user before proceeding unless the request includes a phrase such as "I'm sure" or "confirm".

**Example invocations:**
```
/do create a database called "inventory"
/do show all products where Price > 50, sorted by Label ascending
/do insert a product: SKU=P001, Label=Widget, Price=9.99
/do begin a transaction called "batch-import"
/do backup the inventory database with label "pre-migration"
/do drop table OldLogs — I'm sure
```

---

### `/this` — Inspect

Displays the current state of one or all XBase databases.

**Mode 1 — Survey (no `DatabaseName`):**

Lists all databases in `XBaseFiles/` (excluding `backups/`). For each:
- Name, table count, total active row count, total directory size, last-modified timestamp

```
XBase Databases — XBaseFiles/
────────────────────────────────────────────────────
  inventory    5 tables    12,847 rows    4.2 MB    2026-06-25
  analytics    3 tables   891,204 rows  287.0 MB   2026-06-26
────────────────────────────────────────────────────
2 databases
```

**Mode 2 — Detail (`DatabaseName` provided):**

Full breakdown of one database:
- Schema: all tables, column counts, active/soft-deleted row counts, index count per table
- Active connections and pending transactions
- Backup history (last N backups from `XBaseFiles/backups/`)

```
Database: inventory
Path:     XBaseFiles/inventory/
Created:  2026-06-01T09:00:00
Updated:  2026-06-25T18:30:00

Tables (5):
  Products     4,210 rows  (12 soft-deleted)   8 columns   2 indexes
  Orders       8,204 rows  (0 soft-deleted)    12 columns  3 indexes
  Customers      433 rows  (5 soft-deleted)    9 columns   1 index
  Statuses         6 rows  (0 soft-deleted)    4 columns   0 indexes
  Categories      48 rows  (2 soft-deleted)    5 columns   1 index

Active Connections:  conn-main
Pending Transactions: none
Last Backup: XBaseFiles/backups/inventory_20260625T183000  (24h ago)
```

---

### `/that` — Maintain

Performs a maintenance operation on a target database.

**Operations:**

| Operation | Description |
|---|---|
| `report` (default) | Full health report: integrity check + index health + record counts + backup status |
| `verify` | Parse every NDJSON line; report corrupt rows with file name and line number |
| `backup` | Create a timestamped backup in `XBaseFiles/backups/` |
| `rebuild-indexes` | Rebuild all `.ndx` files from source NDJSON data |
| `vacuum` | Hard-delete all soft-deleted rows across all tables (requires confirmation) |

**Default report output:**
```
XBase Health Report — inventory
──────────────────────────────────────────────
Integrity:      OK  (0 issues across 5 tables)
Indexes:        10 healthy
Record counts:  12,901 active  /  19 soft-deleted
Last Backup:    2026-06-25T18:30:00  (24h ago)
──────────────────────────────────────────────
Recommendation: Consider a backup (last was >12h ago)
```

---

## File Layout

```
SKILLS/XBase/Admin/
├── execute.md          Natural-language XBase command executor
├── Inspect.md          Database inspector and status viewer
└── maintain.md         Maintenance and health operations

.claude/commands/XBase/Admin/
├── do.proompt.md       Slash command — same workflow as execute.md
├── this.proompt.md     Slash command — same workflow as Inspect.md
└── that.proompt.md     Slash command — same workflow as maintain.md
```

---

## Non-Goals

- The admin console does not implement its own file I/O — all reads and writes go through XBase skills
- It does not add new error codes; it surfaces existing XBase error envelopes with added context
- It does not provide a GUI or web interface — output is plain text to stdout

---

## Dependencies

All three admin commands depend on the complete XBase skill set (28 skills across 7 groups). They must not be distributed without the full XBase skill package.
