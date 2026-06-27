# XBase

XBase is a native file-based database engine accessed entirely through AI Skills. It provides connection management, schema DDL, full CRUD, composite queries, index management, transactions, and backup — each operation as a single slash command. There are no third-party database libraries: the AI reads and writes structured text files directly using OS file system primitives.

---

## Architecture

| Layer | Technology |
|---|---|
| Storage engine | Native file system — directories and DBF files |
| Script generation | Dynamic — PowerShell, bash, or Python chosen at runtime |
| Foreign key enforcement | Skill-level validation against `_schema.json` |
| Soft deletes | `IsDeleted INTEGER DEFAULT 0` on every table |
| Transactions | Directory snapshot workspace (`_txn_{name}/`) |
| Client library | None — OS file system primitives only |

### Runtime Environment Detection

Every XBase skill begins by detecting which script runtime is available and generates all file operations using that runtime's idioms:

| Priority | Runtime | Detection signal | File operation idioms |
|---|---|---|---|
| 1 | PowerShell (pwsh / Windows PS) | `$PSVersionTable` in scope | `New-Item`, `Get-Content`, `Set-Content`, `Add-Content`, `Move-Item`, `Remove-Item`, `Copy-Item` |
| 2 | bash / zsh | `$BASH_VERSION` or `$ZSH_VERSION` in env | `mkdir -p`, `cat`, `tee`, `mv`, `rm -rf`, `cp -r`, POSIX pipeline |
| 3 | Python 3 (fallback) | `python3` or `python` on PATH | `os`, `os.path`, `shutil`, `json` stdlib modules only |

No external packages, binaries, or database engines are installed. All logic runs with what is already present on the target machine.

### Native File Format

A database is a **named directory** under `XBaseFiles/`. Every piece of state is a plain text file inside that directory:

```
XBaseFiles/
└── myapp/
    ├── _meta.json                     Database metadata
    ├── _schema.json                   Table and index definitions
    ├── Products.dbf                Table data — fixed-length binary record
    ├── Products.idx_SKU.ndx           Index — sorted key→Id entries, one per line
    └── _txn_txn1/                     Active transaction workspace (if any)
        ├── _schema.json               Transaction-local schema copy
        └── Products.dbf            Transaction-local data copy (only tables touched)
```

**`_meta.json`** — database identity:
```json
{ "XBaseVersion": 1, "Name": "myapp", "CreatedAt": "2026-06-25T12:00:00Z", "UpdatedAt": "2026-06-25T12:00:00Z" }
```

**`_schema.json`** — all table and index definitions plus `NextId` counters.

**`{TableName}.dbf`** — one complete JSON object per line, UTF-8, `\n`-terminated:
```
{"Id":1,"SKU":"A001","Label":"Widget","Price":9.99,"IsDeleted":0,"CreatedAt":"2026-06-25T12:00:00Z","UpdatedAt":"2026-06-25T12:00:00Z"}
```

**`{TableName}.{IndexName}.ndx`** — sorted ascending by Key, used for binary-search lookups:
```
{"Key":"A001","Id":1}
{"Key":"A002","Id":2}
```

### Implicit Columns

Every table created through XBase automatically receives these columns:

| Column | Type | Notes |
|---|---|---|
| `Id` | `INTEGER` — auto-increment | Prepended unless a `PrimaryKey: true` column is supplied; value managed via `NextId` in `_schema.json` |
| `CreatedAt` | `TEXT` | ISO-8601 timestamp; set on insert, never changed |
| `UpdatedAt` | `TEXT` | ISO-8601 timestamp; refreshed on every update |
| `IsDeleted` | `INTEGER DEFAULT 0` | `0` = active, `1` = soft-deleted |

`XBase-Record-Select` automatically excludes rows where `IsDeleted = 1` unless `IncludeDeleted: true` is passed. `XBase-Record-Delete` sets `IsDeleted = 1` by default; pass `HardDelete: true` for physical line removal.

### Cross-Platform File Operations

All XBase skills express their I/O through the following logical operations. The table shows the equivalent in each supported runtime:

| Logical operation | PowerShell | bash | Python (stdlib) |
|---|---|---|---|
| Create directory | `New-Item -ItemType Directory` | `mkdir -p` | `os.makedirs` |
| Delete directory (recursive) | `Remove-Item -Recurse -Force` | `rm -rf` | `shutil.rmtree` |
| Copy directory (recursive) | `Copy-Item -Recurse` | `cp -r` | `shutil.copytree` |
| Read text file | `Get-Content -Raw` | `cat` | `open().read()` |
| Write text file | `Set-Content` | `tee` / redirect | `open('w').write()` |
| Read lines | `Get-Content` | `mapfile` / `while read` | `open().readlines()` |
| Rewrite lines | `Set-Content` | redirect `>` | `open('w').writelines()` |
| Append one line | `Add-Content` | `>>` redirect | `open('a').write()` |
| Atomic move | `Move-Item` | `mv` | `shutil.move` |
| Delete file | `Remove-Item` | `rm` | `os.remove` |
| File/dir exists | `Test-Path` | `[ -e path ]` | `os.path.exists` |

---

## Quick Start

```
# 1. Create and open a database
/XBase-Database-Initialize  DatabaseName:"myapp"
/XBase-Database-Connect     DatabaseName:"myapp"  ConnectionName:"main"

# 2. Create a table
/XBase-Schema-TableCreate
  ConnectionName:"main"
  TableName:"Products"
  Columns:[
    {"Name":"SKU",   "Type":"TEXT",    "Nullable":false, "Unique":true},
    {"Name":"Label", "Type":"TEXT",    "Nullable":false},
    {"Name":"Price", "Type":"REAL",    "Nullable":true}
  ]

# 3. Insert rows
/XBase-Record-Insert
  ConnectionName:"main"
  TableName:"Products"
  Rows:[
    {"SKU":"A001", "Label":"Widget", "Price":9.99},
    {"SKU":"A002", "Label":"Gadget", "Price":19.99}
  ]

# 4. Query
/XBase-Record-Select
  ConnectionName:"main"
  TableName:"Products"
  Filter:{"Field":"Price", "Operator":"<", "Value":15}
  Sort:[{"Field":"Price", "Direction":"ASC"}]
  Limit:25

# 5. Close
/XBase-Database-Disconnect  ConnectionName:"main"
```

---

## Operation Groups

### Runtime (1 skill)

| Skill | Purpose |
|---|---|
| `XBase-Runtime-Detect` | Detect the execution environment (PowerShell, bash, Python) and return the runtime context used by all subsequent skills |

### Database (4 skills)

| Skill | Purpose |
|---|---|
| `XBase-Database-Initialize` | Create a new database directory with `_meta.json` and empty `_schema.json` |
| `XBase-Database-Connect` | Validate an existing database and register it under a named alias |
| `XBase-Database-Disconnect` | Deregister a connection alias (optionally rolling back open transactions) |
| `XBase-Database-Drop` | Delete the entire database directory (`ConfirmDrop: true` required) |

### Schema (5 skills)

| Skill | Purpose |
|---|---|
| `XBase-Schema-TableCreate` | Add a table to `_schema.json` and create an empty `.dbf` file |
| `XBase-Schema-TableAlter` | Add columns to a table definition in `_schema.json` |
| `XBase-Schema-TableDrop` | Remove a table from `_schema.json` and delete its `.dbf` and `.ndx` files |
| `XBase-Schema-TableList` | Return all table names from `_schema.json` |
| `XBase-Schema-ColumnList` | Return column definitions for a table from `_schema.json` |

### Record (5 skills)

| Skill | Purpose |
|---|---|
| `XBase-Record-Insert` | Append rows to a `.dbf` file; enforce constraints; update indexes |
| `XBase-Record-Select` | Read `.dbf`, apply filter/sort/pagination in memory; return matching rows |
| `XBase-Record-Update` | Read `.dbf`, modify matching rows, rewrite file; update indexes |
| `XBase-Record-Delete` | Soft-delete (default) or hard-delete rows matching a filter |
| `XBase-Record-Upsert` | Insert or update based on conflict columns; returns `Action:"inserted"` or `"updated"` |

### Query (5 skills)

These skills compile reusable query components passed to `XBase-Record-Select` or `XBase-Query-Execute`. **No file I/O occurs at compile time** — they are pure specification builders.

| Skill | Purpose |
|---|---|
| `XBase-Query-Filter` | Compile a filter specification (`=`, `!=`, `<`, `>`, `<=`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`; AND/OR chaining) |
| `XBase-Query-Sort` | Compile a sort specification |
| `XBase-Query-Join` | Compile a join specification (INNER, LEFT) |
| `XBase-Query-Aggregate` | Compile an aggregate specification (COUNT, SUM, AVG, MIN, MAX; GROUP BY) |
| `XBase-Query-Execute` | Execute a compound query specification (filter + sort + join + aggregate in one call) |

Filters evaluate in memory against parsed DBF rows. All field names are validated as safe identifiers before use.

### Index (4 skills)

| Skill | Purpose |
|---|---|
| `XBase-Index-Create` | Read `.dbf`, build sorted `.ndx` file, register in `_schema.json` |
| `XBase-Index-Drop` | Delete `.ndx` file and remove from `_schema.json` |
| `XBase-Index-Rebuild` | Re-read `.dbf`, rewrite `.ndx` file from scratch |
| `XBase-Index-List` | Return index definitions for a table from `_schema.json` |

### Transaction (4 skills)

| Skill | Purpose |
|---|---|
| `XBase-Transaction-Begin` | Create `_txn_{name}/` workspace directory; copy `_schema.json` into it |
| `XBase-Transaction-Commit` | Move transaction workspace files over live files; delete workspace |
| `XBase-Transaction-Rollback` | Delete transaction workspace (all changes discarded); optionally roll back to a savepoint |
| `XBase-Transaction-Savepoint` | Snapshot current transaction state into `_txn_{name}/sp_{savepointName}/` |

Pass `TransactionName` to any Record or Query skill to operate within an open transaction. Changes remain in the workspace until `XBase-Transaction-Commit`.

### Backup (3 skills)

| Skill | Purpose |
|---|---|
| `XBase-Backup-Create` | Copy the database directory to `XBaseFiles/backups/{name}_{timestamp}/`; skips active transaction directories |
| `XBase-Backup-Restore` | Replace live database directory with a backup copy (`ConfirmRestore: true` required; optionally creates a pre-restore snapshot) |
| `XBase-Backup-Verify` | Read `_meta.json`, `_schema.json`, and all `.dbf` files; validate every JSON line; return `IntegrityOk` and `Issues` |

---

## Error Codes

All XBase error codes follow the pattern `XBASE_<CATEGORY>_<REASON>`.

| Category | Example Codes |
|---|---|
| `DATABASE` | `XBASE_DATABASE_NOT_FOUND`, `XBASE_DATABASE_EXISTS`, `XBASE_DATABASE_PATH_INVALID`, `XBASE_DATABASE_CORRUPT` |
| `CONNECTION` | `XBASE_CONNECTION_INVALID`, `XBASE_CONNECTION_NAME_IN_USE` |
| `SCHEMA` | `XBASE_SCHEMA_TABLE_NOT_FOUND`, `XBASE_SCHEMA_TABLE_EXISTS`, `XBASE_SCHEMA_COLUMN_MISSING`, `XBASE_SCHEMA_COLUMN_INVALID`, `XBASE_SCHEMA_COLUMN_EXISTS` |
| `RECORD` | `XBASE_RECORD_CONSTRAINT_VIOLATION`, `XBASE_RECORD_FILTER_REQUIRED` |
| `FILTER` | `XBASE_FILTER_FIELD_INVALID`, `XBASE_FILTER_OPERATOR_UNKNOWN`, `XBASE_FILTER_VALUE_REQUIRED` |
| `INDEX` | `XBASE_INDEX_EXISTS`, `XBASE_INDEX_NOT_FOUND` |
| `TRANSACTION` | `XBASE_TRANSACTION_NOT_OPEN`, `XBASE_TRANSACTION_NAME_IN_USE`, `XBASE_SAVEPOINT_NOT_FOUND`, `XBASE_SAVEPOINT_NAME_IN_USE` |
| `BACKUP` | `XBASE_BACKUP_NOT_FOUND`, `XBASE_BACKUP_CORRUPT`, `XBASE_BACKUP_IO_ERROR` |
| `DROP` | `XBASE_DROP_NOT_CONFIRMED`, `XBASE_RESTORE_NOT_CONFIRMED` |
| `AGGREGATE` | `XBASE_AGGREGATE_FUNCTION_UNKNOWN` |
| `SORT` | `XBASE_SORT_DIRECTION_INVALID`, `XBASE_SORT_FIELD_INVALID` |
| `JOIN` | `XBASE_JOIN_TYPE_INVALID`, `XBASE_JOIN_REFERENCE_INVALID` |

---

## Design Decisions

**Why directory-per-database instead of a single file?**
A directory-per-database lets each table be an independent file. Updates to one table never touch another table's file, minimising the blast radius of writes. Transactions are isolated by working in a subdirectory — rollback is a directory delete; commit is a file move.

**Why DBF instead of binary?**
DBF is human-readable, trivially diffable with `git diff`, and requires no parser beyond `JSON.Parse`. Any text editor can inspect or repair a table file. Backup verification reduces to checking that every line round-trips through JSON parse.

**Why soft deletes?**
Soft deletes preserve audit history and allow accidental-delete recovery. Hard deletes are opt-in via `HardDelete: true`.

**Why is `Filter` required for Update and Delete?**
Requiring an explicit filter prevents silent mass-updates or mass-deletes caused by omitting a condition. If you genuinely need to update all rows, pass `Filter: {"Field": "Id", "Operator": ">", "Value": 0}`.

**Why does `XBase-Query-Filter` touch no files?**
Keeping specification compilation separate from execution allows filters to be composed incrementally and reused across multiple queries without redundant file reads.

**How are concurrent writes handled?**
File system `File.Move` is atomic on the same volume, so transaction commits are atomic. Concurrent agents should coordinate at the skill level (one writer at a time per database). XBase does not implement advisory locks — that coordination is the caller's responsibility.
