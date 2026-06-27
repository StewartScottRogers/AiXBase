# Product Requirements Document: XBase Administrative Console — Testing Criteria

## Overview

This document defines the acceptance tests, edge-case tests, error-condition tests, and security tests required to certify that all three XBase Administrative Console commands — Execute, Inspect, and Maintain — behave correctly across both delivery surfaces (`SKILLS/XBase/Admin/` and `.claude/commands/XBase/Admin/`).

A command is considered **passing** only when every applicable test ID in this document produces the stated expected result.

Test IDs follow the pattern `XBASE-<GROUP>-<NNN>` where group codes are:

| Code | Group |
|---|---|
| `DO` | Execute command (`execute.md` / `do.proompt.md`) |
| `THIS` | Inspect command (`Inspect.md` / `this.proompt.md`) |
| `THAT` | Maintain command (`maintain.md` / `that.proompt.md`) |
| `ADM-SEC` | Security tests across all three commands |

---

## Test Environment Requirements

| Requirement | Specification |
|---|---|
| Available disk space | ≥ 1 GB |
| `XBaseFiles/` directory | Writable, on a local drive |
| `XBaseFiles/backups/` | Created automatically by skills if absent |
| Pre-existing test databases | Each test creates and tears down its own database in `XBaseFiles/adm-test-<ID>/` |
| Baseline XBase skills | All 28 XBase skills installed and functional (XBase-Testing-PRD must pass) |

---

## Test Cases: Execute Command

Tests for `execute.md` (`/execute`) and `do.proompt.md` (`/do`). Behaviour is identical across both surfaces; run each test against both.

### Intent Recognition — Database Operations

| ID | Input phrase | Expected skill invoked | Key extracted parameters |
|---|---|---|---|
| `XBASE-DO-001` | `create a database called "adm-test-do"` | `XBase-Database-Initialize` | `DatabaseName:"adm-test-do"` |
| `XBASE-DO-002` | `initialise a new database named adm-test-do` | `XBase-Database-Initialize` | `DatabaseName:"adm-test-do"` |
| `XBASE-DO-003` | `connect to the adm-test-do database` | `XBase-Database-Connect` | `DatabaseName:"adm-test-do"` |
| `XBASE-DO-004` | `open adm-test-do as conn-main` | `XBase-Database-Connect` | `DatabaseName:"adm-test-do"`, `ConnectionName:"conn-main"` |
| `XBASE-DO-005` | `close the conn-main connection` | `XBase-Database-Disconnect` | `ConnectionName:"conn-main"` |
| `XBASE-DO-006` | `drop the adm-test-do database — I'm sure` | `XBase-Database-Drop` | `DatabaseName:"adm-test-do"`, `ConfirmDrop:true` |

### Intent Recognition — Schema Operations

| ID | Input phrase | Expected skill invoked | Key extracted parameters |
|---|---|---|---|
| `XBASE-DO-007` | `create a table called Products with columns SKU (text), Label (text), Price (real)` | `XBase-Schema-TableCreate` | `TableName:"Products"`, three column definitions |
| `XBASE-DO-008` | `add a Rating column to Products` | `XBase-Schema-TableAlter` | `TableName:"Products"`, `AddColumns:[{Name:"Rating"}]` |
| `XBASE-DO-009` | `drop the OldLogs table — I'm sure` | `XBase-Schema-TableDrop` | `TableName:"OldLogs"`, `ConfirmDrop:true` |
| `XBASE-DO-010` | `show all tables` | `XBase-Schema-TableList` | — |
| `XBASE-DO-011` | `list the columns in Products` | `XBase-Schema-ColumnList` | `TableName:"Products"` |

### Intent Recognition — Record Operations

| ID | Input phrase | Expected skill invoked | Key extracted parameters |
|---|---|---|---|
| `XBASE-DO-012` | `insert a product: SKU=P001, Label=Widget, Price=9.99` | `XBase-Record-Insert` | `TableName:"Products"`, `Rows:[{SKU:"P001",Label:"Widget",Price:9.99}]` |
| `XBASE-DO-013` | `show all products where Price > 50, sorted by Label ascending` | `XBase-Record-Select` + `XBase-Query-Filter` + `XBase-Query-Sort` | `TableName:"Products"`, filter `Price > 50`, sort `Label ASC` |
| `XBASE-DO-014` | `find all orders` | `XBase-Record-Select` | `TableName:"Orders"` |
| `XBASE-DO-015` | `update product P001, set Price to 12.99` | `XBase-Record-Update` | `TableName:"Products"`, filter `SKU=P001`, `Values:{Price:12.99}` |
| `XBASE-DO-016` | `delete product P001` | `XBase-Record-Delete` | `TableName:"Products"`, filter `SKU=P001` |
| `XBASE-DO-017` | `upsert product P001: Label=Widget, Price=9.99` | `XBase-Record-Upsert` | `TableName:"Products"`, conflict key includes `SKU` |

### Intent Recognition — Index, Transaction, and Backup Operations

| ID | Input phrase | Expected skill invoked | Key extracted parameters |
|---|---|---|---|
| `XBASE-DO-018` | `create an index on Products.SKU` | `XBase-Index-Create` | `TableName:"Products"`, `Columns:["SKU"]` |
| `XBASE-DO-019` | `drop the idx_SKU index` | `XBase-Index-Drop` | `IndexName:"idx_SKU"` |
| `XBASE-DO-020` | `rebuild all indexes` | `XBase-Index-Rebuild` | No `IndexName` or `TableName` (database-wide rebuild) |
| `XBASE-DO-021` | `list all indexes on Products` | `XBase-Index-List` | `TableName:"Products"` |
| `XBASE-DO-022` | `begin a transaction called batch-import` | `XBase-Transaction-Begin` | `TransactionName:"batch-import"` |
| `XBASE-DO-023` | `commit the batch-import transaction` | `XBase-Transaction-Commit` | `TransactionName:"batch-import"` |
| `XBASE-DO-024` | `rollback the batch-import transaction` | `XBase-Transaction-Rollback` | `TransactionName:"batch-import"` |
| `XBASE-DO-025` | `create a savepoint called before-insert` | `XBase-Transaction-Savepoint` | `SavepointName:"before-insert"` |
| `XBASE-DO-026` | `backup the adm-test-do database with label pre-migration` | `XBase-Backup-Create` | `DatabaseName:"adm-test-do"`, `BackupLabel:"pre-migration"` |
| `XBASE-DO-027` | `restore the adm-test-do database from XBaseFiles/backups/adm-test-do_20260625` | `XBase-Backup-Restore` | `BackupPath` set, asks for `ConfirmRestore` |
| `XBASE-DO-028` | `verify the backup at XBaseFiles/backups/adm-test-do_20260625` | `XBase-Backup-Verify` | `BackupPath:"XBaseFiles/backups/adm-test-do_20260625"` |

### Missing Parameter Prompts

| ID | Input phrase | Expected behaviour |
|---|---|---|
| `XBASE-DO-029` | `create a database` (no name) | Asks the user for `DatabaseName` before proceeding; does not call any skill until the name is supplied |
| `XBASE-DO-030` | `insert a record` (no table, no values) | Asks for `TableName` first; after receiving it, asks for field values; only then calls `XBase-Record-Insert` |
| `XBASE-DO-031` | `insert into Products` (no field values) | Asks the user what field values to insert; does not call the skill with an empty or partial row |
| `XBASE-DO-032` | `create a table` (no name, no columns) | Asks for `TableName` and at least one column definition before calling `XBase-Schema-TableCreate` |
| `XBASE-DO-033` | `connect` (no database name) | Asks for `DatabaseName` before calling `XBase-Database-Connect` |
| `XBASE-DO-034` | `backup` (no database name, no active connection) | Asks which database to back up before proceeding |

### Destructive Operation Confirmation Guard

| ID | Scenario | Expected behaviour |
|---|---|---|
| `XBASE-DO-035` | `drop the inventory database` (no confirmation phrase) | Asks the user to confirm before calling `XBase-Database-Drop`; does not drop |
| `XBASE-DO-036` | `drop the inventory database — I'm sure` | Proceeds directly; calls `XBase-Database-Drop` with `ConfirmDrop:true` |
| `XBASE-DO-037` | `drop the inventory database, confirm` | Proceeds directly; `ConfirmDrop:true` derived from "confirm" keyword |
| `XBASE-DO-038` | `drop the inventory database` → user replies "yes" | Drops after receiving confirmation in follow-up message |
| `XBASE-DO-039` | `drop the inventory database` → user replies "no" | Aborts; no skill called; reports that the operation was cancelled |
| `XBASE-DO-040` | `drop table OldLogs` (no confirmation phrase) | Asks for confirmation before calling `XBase-Schema-TableDrop` |
| `XBASE-DO-041` | `drop table OldLogs — I'm sure` | Proceeds directly; `ConfirmDrop:true` |
| `XBASE-DO-042` | `restore from backup/adm_20260625` (no confirmation phrase) | Asks for confirmation before calling `XBase-Backup-Restore`; reports that this will overwrite the target |
| `XBASE-DO-043` | `delete product P001` (soft delete — not destructive) | No confirmation prompt required; calls `XBase-Record-Delete` directly |

### Multi-Step Operations

| ID | Input phrase | Expected sequence |
|---|---|---|
| `XBASE-DO-044` | `create and connect to a database called adm-test-do` | Calls `XBase-Database-Initialize` then `XBase-Database-Connect` in that order |
| `XBASE-DO-045` | `begin a transaction called tx1, insert a product P001, then commit` | Calls `XBase-Transaction-Begin`, `XBase-Record-Insert` with `TransactionName:"tx1"`, then `XBase-Transaction-Commit` |
| `XBASE-DO-046` | `create table Products, then add a Rating column` | Calls `XBase-Schema-TableCreate` then `XBase-Schema-TableAlter` |

### Error Surfacing

| ID | Scenario | Expected output |
|---|---|---|
| `XBASE-DO-047` | Connect to a non-existent database | Reports `XBASE_DATABASE_NOT_FOUND` with plain-English explanation: "No database named '…' found in XBaseFiles/" |
| `XBASE-DO-048` | Insert into a table that does not exist | Reports `XBASE_SCHEMA_TABLE_NOT_FOUND` with plain-English explanation and suggested next step (list tables or create the table) |
| `XBASE-DO-049` | Commit a transaction name that is not open | Reports `XBASE_TRANSACTION_NOT_OPEN` with plain-English context |
| `XBASE-DO-050` | Create a database that already exists without "overwrite" | Reports `XBASE_DATABASE_EXISTS`; suggests adding "overwrite" to the request |

---

## Test Cases: Inspect Command

Tests for `Inspect.md` (`/inspect`) and `this.proompt.md` (`/this`). Behaviour is identical across both surfaces; run each test against both.

### Survey Mode (no DatabaseName)

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THIS-001` | Empty `XBaseFiles/` | No database directories | Reports "No databases found" |
| `XBASE-THIS-002` | Single database | One database directory with `_meta.json` and two tables | Displays one-row summary table showing name, table count (2), active row count, size, and UpdatedAt |
| `XBASE-THIS-003` | Multiple databases | Three database directories | All three appear in the summary table; output is sorted |
| `XBASE-THIS-004` | `backups/` directory excluded | `XBaseFiles/backups/` exists alongside two database directories | `backups/` not listed as a database |
| `XBASE-THIS-005` | `_txn_*/` directories excluded | A database directory has a `_txn_batch-import/` workspace | Transaction workspace not listed as a separate database |
| `XBASE-THIS-006` | Database with corrupt or missing `_meta.json` | Database directory exists but `_meta.json` is absent | Row in table shows `[corrupt — missing _meta.json]`; other databases still listed normally |
| `XBASE-THIS-007` | Backup count note | `XBaseFiles/backups/` contains 3 backup directories | Footer note reports how many backups exist |

### Detail Mode (DatabaseName provided)

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THIS-008` | Basic database | Two tables, standard rows | Displays database path, CreatedAt, UpdatedAt, table list with row counts, column counts, index counts |
| `XBASE-THIS-009` | Soft-deleted rows counted separately | Products table: 100 active rows, 10 soft-deleted | "100 rows (10 soft-deleted)" for Products; active count does not include soft-deleted rows |
| `XBASE-THIS-010` | Indexes counted per table | Products: 2 indexes, Orders: 0 indexes | "2 indexes" for Products, "0 indexes" for Orders |
| `XBASE-THIS-011` | Active connection listed | `conn-main` open on the database | Shows `Connections: conn-main` |
| `XBASE-THIS-012` | No active connections | Database has no open connections | Shows `Connections: none` |
| `XBASE-THIS-013` | Pending transaction listed | `_txn_batch-import/` directory present | Shows `Transactions: batch-import` |
| `XBASE-THIS-014` | No pending transactions | No `_txn_*/` directories | Shows `Transactions: none` |
| `XBASE-THIS-015` | Backup history listed | `XBaseFiles/backups/adm-test_20260625T183000/` exists | Shows most recent backup path and age |
| `XBASE-THIS-016` | No backups | No matching directories in `XBaseFiles/backups/` | Shows `Backups: none found` |
| `XBASE-THIS-017` | Non-existent database | DatabaseName does not exist | Reports `XBASE_DATABASE_NOT_FOUND` with suggested next step |

### Read-Only Guarantee

| ID | Description | Expected behaviour |
|---|---|---|
| `XBASE-THIS-018` | Survey mode leaves no modifications | Run survey on a set of databases; compare all file mtimes before and after | No file modification timestamps change; no new files created |
| `XBASE-THIS-019` | Detail mode cleans up temporary connection | After detail mode completes | The `admin-inspect` connection alias is deregistered; no open connection remains |

---

## Test Cases: Maintain Command

Tests for `maintain.md` (`/maintain`) and `that.proompt.md` (`/that`). Behaviour is identical across both surfaces; run each test against both.

### `report` Operation (default)

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THAT-001` | Clean database | Valid DBF, all index files present, recent backup | Report shows `Integrity: OK`, all indexes healthy, correct active and soft-deleted counts, backup timestamp |
| `XBASE-THAT-002` | No backup | Valid database, no entry in `XBaseFiles/backups/` | Report shows `Last Backup: NONE — recommend running: /that <name> backup` |
| `XBASE-THAT-003` | Stale backup | Most recent backup is older than 12 h | Report shows backup timestamp and age; recommendation section advises taking a new backup |
| `XBASE-THAT-004` | Missing index file | `_schema.json` lists an index but the `.ndx` file is absent | Report shows `{N} missing` in the Indexes line; recommendation advises running `rebuild-indexes` |
| `XBASE-THAT-005` | Soft-deleted rows counted correctly | Table with 200 active, 15 soft-deleted | `TotalSoftDeleted: 15` in report |
| `XBASE-THAT-006` | Temporary connection cleaned up | After report completes | `admin-report` connection alias deregistered |
| `XBASE-THAT-007` | Non-existent database | DatabaseName does not exist | Reports `XBASE_DATABASE_NOT_FOUND` with plain-English context and suggested next step (check name with `/this`) |

### `verify` Operation

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THAT-008` | All valid DBF | No corrupt rows | Displays "All DBF files are valid" |
| `XBASE-THAT-009` | Single corrupt line | Manually write `{invalid json}` on line 3 of `Products.dbf` | `IntegrityOk: false`; output lists `Products.dbf` and line number 3 |
| `XBASE-THAT-010` | Multiple corrupt files | Two `.dbf` files each have one bad line | Both files and their bad line numbers appear in the issues list |
| `XBASE-THAT-011` | Empty table file | `.dbf` file exists but is empty | No issues reported for that table |
| `XBASE-THAT-012` | Does not modify files | Run verify on clean database | No file modification timestamps change |

### `backup` Operation

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THAT-013` | Happy path — no label | Open database | Backup created; output shows `BackupPath` and timestamp |
| `XBASE-THAT-014` | With label | `BackupLabel` extracted from request | Backup directory name includes the label string |
| `XBASE-THAT-015` | Backup is a valid XBase directory | After backup | `_meta.json` and `_schema.json` present in backup; all `.dbf` files present |
| `XBASE-THAT-016` | Temporary connection cleaned up | After backup completes | `admin-backup` connection alias deregistered |

### `rebuild-indexes` Operation

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THAT-017` | Database with multiple indexes | Three indexes across two tables | Output lists all three in `RebuiltIndexes`; each `.ndx` file has been rewritten |
| `XBASE-THAT-018` | Database with no indexes | No index entries in `_schema.json` | Output shows `RebuiltIndexes: []`; no error |
| `XBASE-THAT-019` | Stale index rebuilt correctly | Manually delete one `.ndx` file before running | After rebuild, all `.ndx` files are present and correctly populated |
| `XBASE-THAT-020` | Temporary connection cleaned up | After rebuild completes | `admin-rebuild` connection alias deregistered |

### `vacuum` Operation

| ID | Description | Setup | Expected output |
|---|---|---|---|
| `XBASE-THAT-021` | Confirmed vacuum | Database has 15 soft-deleted rows; user confirms when prompted | `XBase-Record-Delete` called with `HardDelete:true` and `Filter:{IsDeleted=1}` per table; per-table summary shows rows removed |
| `XBASE-THAT-022` | Declined — user types "no" | Vacuum prompted; user replies "no" | Aborts immediately; no skill called; reports "Operation cancelled" |
| `XBASE-THAT-023` | Declined — no reply / timeout | No confirmation supplied | Does not proceed; does not assume confirmation |
| `XBASE-THAT-024` | No soft-deleted rows | All tables have `IsDeleted = 0` only | Per-table summary shows `0 rows removed` for each; no error |
| `XBASE-THAT-025` | Per-table summary accurate | Three tables: Products (5 soft-deleted), Orders (12), Customers (0) | Summary shows Products: 5, Orders: 12, Customers: 0; total = 17 |
| `XBASE-THAT-026` | Temporary connection cleaned up | After confirmed vacuum | `admin-vacuum` connection alias deregistered |

### Invalid Operation

| ID | Description | Expected behaviour |
|---|---|---|
| `XBASE-THAT-027` | Unrecognised operation name | `maintain adm-test-do analyze` (unknown op) | Prompts with the list of valid operations; does not call any skill |
| `XBASE-THAT-028` | No `DatabaseName` supplied | `/that report` with no database name | Asks for `DatabaseName` before proceeding |

---

## Security Tests

| ID | Description | Attack vector | Pass criterion |
|---|---|---|---|
| `XBASE-ADM-SEC-001` | Path traversal in extracted `DatabaseName` | `create a database called "../outside"` | Command extracts `DatabaseName:"../outside"` and passes it to `XBase-Database-Initialize`, which returns `XBASE_DATABASE_PATH_INVALID`; no directory created outside `XBaseFiles/` |
| `XBASE-ADM-SEC-002` | Path traversal in `TableName` | `insert into ../secret a record Code=X` | Command passes `TableName:"../secret"` to `XBase-Record-Insert`, which returns a validation error; no file accessed outside the database directory |
| `XBASE-ADM-SEC-003` | SQL-like injection in filter | `show products where Code = 'A; DROP TABLE Products--'` | Filter value treated as a literal string; `XBase-Query-Filter` returns rows matching that exact string; no unintended modification |
| `XBASE-ADM-SEC-004` | Injection in `DatabaseName` via detail inspect | `/this "../etc"` | `XBase-Database-Connect` returns `XBASE_DATABASE_PATH_INVALID`; no files read outside `XBaseFiles/` |
| `XBASE-ADM-SEC-005` | Injection in `TransactionName` | `begin a transaction called "../live"` | `XBase-Transaction-Begin` returns `XBASE_DATABASE_PATH_INVALID`; no workspace directory created outside the database directory |
| `XBASE-ADM-SEC-006` | Confirmation spoofing — string "true" instead of `ConfirmDrop` | `drop the inventory database, ConfirmDrop="true"` (string) | The command does not treat the string `"true"` as a confirmation phrase; prompts the user for explicit confirmation |
| `XBASE-ADM-SEC-007` | Vacuum without explicit confirmation | `/that inventory vacuum` with no follow-up | Does not hard-delete rows; waits for explicit "yes" before proceeding |
| `XBASE-ADM-SEC-008` | Restore without confirmation | `restore inventory from backups/inv_20260625` | Does not call `XBase-Backup-Restore` until user explicitly confirms; reports that the operation will overwrite the live database |
| `XBASE-ADM-SEC-009` | Null byte in extracted parameter | `create a database called "test\x00evil"` | Passed to `XBase-Database-Initialize`, which returns `XBASE_DATABASE_PATH_INVALID`; no directory created |
| `XBASE-ADM-SEC-010` | Injection in `BackupPath` | `verify backup at ../../Windows/System32` | Passed to `XBase-Backup-Verify`, which returns an error; no file read outside `XBaseFiles/` |

---

## Acceptance Criteria

An implementation of the XBase Administrative Console is considered **release-ready** when:

1. **All Execute tests pass** — every `XBASE-DO-*` test produces the stated expected result, including correct intent mapping, parameter prompting, confirmation guards, and error surfacing.

2. **All Inspect tests pass** — every `XBASE-THIS-*` test produces the correct display output, the read-only guarantee holds, and temporary connections are cleaned up.

3. **All Maintain tests pass** — every `XBASE-THAT-*` test produces the correct output for each of the five operations, vacuum confirmation guards are enforced, and temporary connections are cleaned up.

4. **All security tests pass** — every `XBASE-ADM-SEC-*` test produces the stated pass criterion; no path traversal, injection, or unauthorised destructive action occurs.

5. **Both surfaces pass** — every test above must pass for the SKILLS distributable files (`execute.md`, `Inspect.md`, `maintain.md`) **and** for the Claude Code slash commands (`do.proompt.md`, `this.proompt.md`, `that.proompt.md`).
