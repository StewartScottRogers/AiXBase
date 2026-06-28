# XBase

XBase is a file-backed database engine implemented exclusively as harness-agnostic AI Skills. All database interactions — connection management, schema DDL, full record CRUD, composite queries, index maintenance, transaction control, backup, and administration — are exposed as discrete, composable skills. XBase requires no external database engine, no third-party libraries, no package manager dependencies, and no network connectivity. Every byte it reads or writes goes through abstract file system operations performed by the executing AI agent.

---

## File Layout

A database is a named directory stored under the configured database root. Every file inside that directory is owned exclusively by XBase and managed through its skills. The directory structure for a database named `myapp` under `{DatabaseRoot}` looks like this:

- `{DatabaseRoot}/`
  - `myapp/` — the database directory
    - `_meta.json` — database identity and version metadata
    - `_schema.json` — all table definitions, column definitions, index definitions, and NextId counters
    - `Products.dbf` — table data in dBASE III binary format (one fixed-length record per row)
    - `Products.idx_SKU.ndx` — NDX B-tree index on the SKU column of Products
    - `_txn_batch-import/` — active transaction workspace (exists only while a transaction is open)
      - `_schema.json` — transaction-local copy of the schema
      - `Products.dbf` — transaction-local copy of the table (lazy: only tables touched during the transaction are copied)
      - `sp_checkpoint/` — savepoint snapshot directory
  - `backups/` — backup copies created by XBase-Backup-Create
    - `myapp_20260627T140000/` — a timestamped backup directory

The `_meta.json` file records the database name, XBase format version, creation timestamp, and last-updated timestamp. The `_schema.json` file records the full schema: a `Tables` array with column definitions and a `NextId` counter for each table, and an `Indexes` array with index names, target table names, and indexed column lists.

Every table created through XBase automatically includes four implicit columns: `Id` (integer primary key, auto-incremented via `NextId` in `_schema.json`), `CreatedAt` (ISO-8601 text, set on insert and never changed), `UpdatedAt` (ISO-8601 text, refreshed on every update), and `IsDeleted` (integer, 0 for active rows and 1 for soft-deleted rows). `XBase-Record-Select` excludes rows where `IsDeleted = 1` by default; pass `IncludeDeleted: true` to override.

---

## dBASE III Binary Format

### DBF Table Files

Each table is stored as a `.dbf` file in the dBASE III binary format. The file begins with a fixed-size header followed by a tightly-packed array of fixed-length records.

The header starts with a 1-byte version marker (`0x03`), a 3-byte last-updated date, a 4-byte record count stored as a uint32 little-endian integer at bytes 4–7, a 2-byte header size, and a 2-byte record size. After these fields comes the field descriptor array: one 32-byte descriptor per column, each recording the field name (null-padded to 11 bytes), field type character (`C` for text, `N` for numeric), field length, and decimal count. The header terminates with a single `0x0D` byte, and the file ends with a `0x1A` EOF marker.

Each record begins with a 1-byte deletion flag. The value `0x20` (an ASCII space character) marks an active record; the value `0x2A` (an ASCII asterisk) marks a soft-deleted record. Following the flag are the field bytes at positions defined by the field descriptor array — each field occupies a fixed-width byte range, with text fields padded to their declared maximum length and numeric fields stored as ASCII-encoded digits.

Skills read the header to determine record layout, then seek to each record at the byte offset `HeaderSize + (RecordIndex × RecordSize)` to read or overwrite individual records in place.

### NDX Index Files

Each index is stored as a `.ndx` file using the dBASE III NDX B-tree binary format. Each node entry in the B-tree associates a key value with the byte offset of the corresponding record in the `.dbf` file. For composite indexes, the key is formed by concatenating the column values with a pipe delimiter.

Index files are kept in sync on every insert, update, and delete that touches an indexed column. Skills use the NDX file for O(log n) lookups when a filter targets an indexed column, avoiding full-table scans. `XBase-Index-Rebuild` regenerates the NDX B-tree from scratch by reading all active records from the live `.dbf` file.

---

## Skill Groups

### Database (4 skills)

The Database group manages the lifecycle of a database directory. `XBase-Database-Initialize` creates the directory and writes the initial `_meta.json` and `_schema.json` files. `XBase-Database-Connect` validates an existing database directory and registers a named connection alias for use by all subsequent skills. `XBase-Database-Disconnect` deregisters a connection alias. `XBase-Database-Drop` deletes the entire database directory and all its contents; it requires explicit confirmation via `ConfirmDrop: true`.

### Schema (5 skills)

The Schema group manages table and column definitions stored in `_schema.json`. `XBase-Schema-TableCreate` adds a table entry to `_schema.json` and writes a valid empty `.dbf` file with the appropriate header and field descriptor array. `XBase-Schema-TableAlter` adds new columns to an existing table definition. `XBase-Schema-TableDrop` removes a table from `_schema.json` and deletes its `.dbf` and all associated `.ndx` files. `XBase-Schema-TableList` returns all table names. `XBase-Schema-ColumnList` returns the column definitions for a specific table.

### Record (5 skills)

The Record group performs all CRUD operations on table data. `XBase-Record-Insert` encodes rows as fixed-length dBASE III binary records, appends them to the `.dbf` file, updates the header record count and last-modified date, and updates all relevant NDX index files. `XBase-Record-Select` reads and decodes all records from the `.dbf` file, applies filter conditions, sorts, and pagination in memory, and returns the matching rows. `XBase-Record-Update` reads all records, seeks to each matching record's byte offset, and overwrites the relevant field bytes in place. `XBase-Record-Delete` performs a soft delete by default (writing the `0x2A` deletion flag and setting `IsDeleted = 1`); pass `HardDelete: true` to rewrite the `.dbf` file excluding the matching records entirely. `XBase-Record-Upsert` inserts a row if no matching record is found on the conflict columns, or updates the existing row if one is found.

All Record skills enforce constraints before writing: NOT NULL fields must be present and non-null; UNIQUE fields are checked against the column's NDX index or via a full-table scan if no index exists; FOREIGN KEY references are validated by reading the referenced table; DEFAULT values are injected for absent optional fields.

### Query (5 skills)

The Query group provides reusable specification builders. `XBase-Query-Filter`, `XBase-Query-Sort`, `XBase-Query-Join`, and `XBase-Query-Aggregate` each compile a specification object with no file I/O. These specification objects are passed to `XBase-Record-Select` or `XBase-Query-Execute` to drive filtering, ordering, joining, and aggregation in memory against decoded DBF rows. `XBase-Query-Execute` accepts a compound specification combining all four components and a target operation (`SELECT`, `INSERT`, `UPDATE`, or `DELETE`) in a single call.

Filter operators supported: `=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`. Filters may be chained with `AND` or `OR` and nested into groups. Field names are validated as safe identifiers before use.

### Index (4 skills)

The Index group manages NDX B-tree index files. `XBase-Index-Create` reads the live `.dbf` file, builds a sorted NDX B-tree, writes the `.ndx` file, and registers the index in `_schema.json`. `XBase-Index-Drop` deletes the `.ndx` file and removes the index entry from `_schema.json`. `XBase-Index-Rebuild` regenerates the `.ndx` file from scratch from the current live `.dbf` data without changing the schema definition. `XBase-Index-List` returns all index definitions for a given table from `_schema.json`.

### Transaction (4 skills)

The Transaction group implements isolation through directory snapshots — no external lock managers are used. `XBase-Transaction-Begin` creates a `_txn_{TransactionName}/` workspace directory inside the database directory and copies `_schema.json` into it. All subsequent reads and writes during the transaction operate on files inside that workspace; table `.dbf` files are copied into the workspace lazily, only when first written. `XBase-Transaction-Commit` atomically moves each modified workspace file over the corresponding live file using a same-volume file move, updates `_meta.json`, and deletes the workspace directory. `XBase-Transaction-Rollback` simply deletes the workspace directory — the live files were never touched. `XBase-Transaction-Savepoint` copies the current workspace state into a `sp_{SavepointName}/` subdirectory; rolling back to a savepoint overwrites the workspace with that snapshot.

Any Record or Query skill accepts an optional `TransactionName` input to direct its operations to the transaction workspace.

### Backup (3 skills)

The Backup group provides point-in-time copies of a database. `XBase-Backup-Create` recursively copies the database directory to `{DatabaseRoot}/backups/{DatabaseName}_{timestamp}[_{label}]/`, skipping active transaction workspaces. `XBase-Backup-Restore` replaces the live database directory with a backup copy; it requires `ConfirmRestore: true` and optionally takes a pre-restore safety backup before overwriting. `XBase-Backup-Verify` reads `_meta.json`, `_schema.json`, and every `.dbf` file in a target directory, validates the DBF header and record structure of each file, and returns `IntegrityOk` with an `Issues` array. Verify works on any valid XBase directory, not only backup copies.

### Admin (4 skills)

The Admin group provides orchestration-level operations that delegate all file I/O to the underlying skill layer. `XBase-Admin-Execute` invokes any named XBase skill dynamically: the caller supplies the skill name and a structured inputs object, and the skill dispatches the call and returns the result. `XBase-Admin-Inspect` reads a connected database's structure and reports tables, record counts, index counts, active transaction workspaces, and any anomalies found (missing `.dbf` files, header count mismatches, orphaned index files). `XBase-Admin-Maintain` performs routine housekeeping: packing soft-deleted records from tables, rebuilding all indexes, and verifying backup integrity — each operation individually switchable and all supporting a `DryRun` mode that reports what would be done without making changes. `XBase-Admin-Session` drives a guided interactive admin loop in the conversation: it presents a text menu, dispatches the user's selection to Execute, Inspect, or Maintain, renders the result as markdown, and repeats until the user exits — making all admin operations discoverable without knowing skill names or parameters.

### Runtime (1 skill)

The Runtime group contains one skill: `XBase-Runtime-Detect`. It verifies that the AI agent's execution environment can satisfy all the abstract file system primitive requirements for XBase, and confirms write access to the intended database root. It tests directory creation, text file write/read, binary file write/read, atomic file move, and directory copy, reporting each result as a boolean capability flag and collecting any gaps in an `Issues` array.

---

## Harness Agnostic

XBase skills are pure specifications: numbered prose steps that describe what to do in terms of abstract file operations, logical data transformations, and calls to other named skills. They do not assume any particular programming language, operating system, shell, or AI framework.

Any AI agent or runtime that can follow the numbered steps, invoke other skills by name, and perform the abstract file system operations listed below can implement XBase fully. The same skill files work identically whether the executing agent uses a Claude Code harness, a custom Python agent, a .NET host, or any other environment. No adaptation or rewriting of skill files is needed to change runtimes.

---

## Abstract File Operations

All XBase skills express file system interactions using the following abstract operations. Implementations map these to whatever concrete API the host environment provides.

| Abstract Operation | Purpose in XBase |
|--------------------|-----------------|
| `create-directory(path)` | Create database directories, transaction workspaces, backup destinations |
| `delete-directory-recursive(path)` | Drop a database, roll back a transaction, remove a savepoint snapshot |
| `copy-directory-recursive(src, dest)` | Create backups, restore from backup, snapshot savepoints |
| `list-files(path, pattern)` | Enumerate tables, list index files, find backup directories |
| `directory-exists(path)` | Guard checks before reads and writes |
| `file-exists(path)` | Verify `.dbf`, `.ndx`, and metadata files before access |
| `read-text-file(path)` | Read `_meta.json` and `_schema.json` |
| `write-text-file(path, content)` | Write `_meta.json` and `_schema.json` |
| `read-binary-file(path)` | Read an entire `.dbf` or `.ndx` file into memory for decoding |
| `write-binary-file(path, bytes)` | Write a new `.dbf` header or rewrite a file after a PACK or index rebuild |
| `append-binary-record(path, bytes)` | Append one fixed-length binary record to a `.dbf` file on insert |
| `move-file-atomic(src, dest)` | Atomically commit a transaction file over the live file (same-volume move) |
| `copy-file(src, dest)` | Copy individual files during backup or index operations |
| `delete-file(path)` | Remove table files, index files, and temporary test files |

---

## Getting Started

This walkthrough takes you from a blank environment to a working database with a table, records, a filter query, an index, and a clean disconnect. Every step maps to a single named XBase skill.

### Step 1 — Verify the environment

```
XBase-Runtime-Detect
  DatabaseRoot: "C:\data\myapp"
```

Check that `EnvironmentReady: true` in the result. If `Issues` is non-empty, the agent environment is missing a required file-system capability. Fix those before continuing. `DatabaseRoot` becomes the directory that holds all your database subdirectories for this session.

### Step 2 — Create the database

```
XBase-Database-Initialize
  DatabaseName: "inventory"
```

This creates `C:\data\myapp\inventory\` containing `_meta.json` (version and timestamps) and an empty `_schema.json`. The database is now on disk and ready to connect.

### Step 3 — Connect

```
XBase-Database-Connect
  DatabaseName: "inventory"
  ConnectionName: "inv"
```

From this point forward every skill that touches the database uses `ConnectionName: "inv"`. The connection is session-scoped — it is not persisted to disk.

### Step 4 — Create a table

```
XBase-Schema-TableCreate
  ConnectionName: "inv"
  TableName: "Products"
  Columns:
    - { Name: "SKU",      Type: "TEXT",    Nullable: false, Unique: true }
    - { Name: "Name",     Type: "TEXT",    Nullable: false }
    - { Name: "Price",    Type: "REAL",    Nullable: false, Default: 0 }
    - { Name: "Stock",    Type: "INTEGER", Nullable: false, Default: 0 }
```

XBase automatically prepends `Id` (auto-increment integer primary key) and appends `CreatedAt`, `UpdatedAt`, and `IsDeleted` to the column list. The result is a `Products.dbf` file in the database directory.

### Step 5 — Insert rows

```
XBase-Record-Insert
  ConnectionName: "inv"
  TableName: "Products"
  Rows:
    - { SKU: "WIDGET-01", Name: "Blue Widget", Price: 9.99,  Stock: 150 }
    - { SKU: "GADGET-07", Name: "Red Gadget",  Price: 24.50, Stock: 42  }
    - { SKU: "DOOHIC-03", Name: "Green Thing", Price: 3.75,  Stock: 0   }
```

XBase assigns sequential `Id` values, sets `CreatedAt` and `UpdatedAt` to now, and sets `IsDeleted: 0`. The result includes `InsertedCount: 3` and `LastInsertedId: 3`.

### Step 6 — Build a filter and query

```
XBase-Query-Filter
  Field: "Stock"
  Operator: ">"
  Value: 0

→ Filter: { Field: "Stock", Operator: ">", Value: 0 }

XBase-Record-Select
  ConnectionName: "inv"
  TableName: "Products"
  Filter: <result from above>
  Sort: { Columns: [{ Field: "Price", Direction: "ASC" }] }
```

Returns the two in-stock products sorted cheapest first. `TotalCount` reflects the count before any `Limit`/`Offset` are applied.

### Step 7 — Update a row

```
XBase-Record-Update
  ConnectionName: "inv"
  TableName: "Products"
  Filter: { Field: "SKU", Operator: "=", Value: "DOOHIC-03" }
  Values: { Stock: 25 }
```

Seeks to the matching record's byte offset in the `.dbf` file and overwrites the `Stock` field in place. `UpdatedAt` is refreshed automatically.

### Step 8 — Create an index

```
XBase-Index-Create
  ConnectionName: "inv"
  TableName: "Products"
  Columns: ["SKU"]
  IndexName: "idx_SKU"
```

Scans all active records, builds a sorted NDX B-tree on `SKU`, and registers `idx_SKU` in `_schema.json`. Subsequent `XBase-Record-Select` calls that filter on `SKU` will use this index for O(log n) lookup instead of a full scan.

### Step 9 — Soft-delete a row

```
XBase-Record-Delete
  ConnectionName: "inv"
  TableName: "Products"
  Filter: { Field: "SKU", Operator: "=", Value: "GADGET-07" }
```

Sets `IsDeleted: 1` on the matching record. The row remains on disk but is excluded from all future `XBase-Record-Select` results unless `IncludeDeleted: true` is passed. Pass `HardDelete: true` to physically rewrite the file without that row.

### Step 10 — Disconnect

```
XBase-Database-Disconnect
  ConnectionName: "inv"
```

Releases the session registration. The database files on disk are unaffected — reconnect any time with `XBase-Database-Connect`.

---

## Error Handling

Every XBase skill returns a standard error envelope on failure. The envelope always contains `Success: false`, an `ErrorCode` string following the pattern `XBASE_{CATEGORY}_{REASON}`, a human-readable `Message`, and the `SkillName` of the skill that produced the error.

| Field | Type | Description |
|-------|------|-------------|
| `Success` | bool | Always `false` on error |
| `ErrorCode` | string | Machine-readable code in the form `XBASE_{CATEGORY}_{REASON}` |
| `Message` | string | Human-readable description of the error and likely cause |
| `SkillName` | string | The name of the skill that returned this error |

Error code categories include `DATABASE`, `CONNECTION`, `SCHEMA`, `RECORD`, `FILTER`, `INDEX`, `TRANSACTION`, `BACKUP`, `RUNTIME`, and `ADMIN`. A full list of all error codes appears in the XBase PRD.

Admin skills surface the error envelopes of the underlying skills they invoke, adding context about which operation was in progress when the error occurred.
