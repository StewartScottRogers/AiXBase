# Product Requirements Document: XBase

## Overview

XBase is a skill-based, file-backed database engine implemented exclusively through AI Skills. All database interactions — from schema management through record CRUD and transaction control — are exposed as discrete, composable Skills following the naming convention:

```
[Feature Name]-[Feature-Operation]-[Any Subdivision Needed]
```

Example: `XBase-Record-Insert`, `XBase-Transaction-Rollback`

**Storage engine: native file system only.** XBase reads and writes its own structured text files using file system primitives (`Directory.CreateDirectory`, `File.ReadAllText`, `File.WriteAllLines`, `File.Move`, `File.Copy`, `File.Delete`). No third-party database libraries, no SQLite binaries, no ORM, no ADO.NET providers.

---

## Native File Format

### Database = Directory

A database is a **named directory** stored under `AiXBase/`. Every file inside that directory is owned exclusively by XBase and managed through the skills.

```
AiXBase/
└── {DatabaseName}/
    ├── _meta.json                       Database metadata
    ├── _schema.json                     Table and index definitions
    ├── {TableName}.ndjson               Table data — one JSON object per line
    ├── {TableName}.{IndexName}.ndx      Index — sorted key→Id entries, one per line
    └── _txn_{TransactionName}/          Active transaction workspace (if any)
        ├── _schema.json                 Transaction-local schema copy
        ├── {TableName}.ndjson           Transaction-local data copy (lazy — only tables touched)
        └── sp_{SavepointName}/          Savepoint snapshot
            └── ...
```

### `_meta.json`

```json
{
  "XBaseVersion": 1,
  "Name": "myapp",
  "CreatedAt": "2026-06-25T12:00:00Z",
  "UpdatedAt": "2026-06-25T12:00:00Z"
}
```

### `_schema.json`

```json
{
  "Tables": [
    {
      "Name": "Users",
      "NextId": 3,
      "Columns": [
        { "Name": "Id",        "Type": "INTEGER", "PrimaryKey": true,  "AutoIncrement": true,  "Nullable": false, "Unique": true,  "Default": null, "ForeignKey": null },
        { "Name": "Username",  "Type": "TEXT",    "PrimaryKey": false, "AutoIncrement": false, "Nullable": false, "Unique": true,  "Default": null, "ForeignKey": null },
        { "Name": "Email",     "Type": "TEXT",    "PrimaryKey": false, "AutoIncrement": false, "Nullable": false, "Unique": true,  "Default": null, "ForeignKey": null },
        { "Name": "CreatedAt", "Type": "TEXT",    "Nullable": true,  "Default": null },
        { "Name": "UpdatedAt", "Type": "TEXT",    "Nullable": true,  "Default": null },
        { "Name": "IsDeleted", "Type": "INTEGER", "Nullable": false, "Default": 0    }
      ]
    }
  ],
  "Indexes": [
    {
      "Name": "idx_Users_Username",
      "TableName": "Users",
      "Columns": ["Username"],
      "Unique": true
    }
  ]
}
```

### `{TableName}.ndjson` — Table Data

Newline-Delimited JSON (NDJSON): one complete, self-contained JSON object per line, UTF-8, `\n`-terminated.

```
{"Id":1,"Username":"alice","Email":"alice@example.com","IsDeleted":0,"CreatedAt":"2026-06-25T12:00:00Z","UpdatedAt":"2026-06-25T12:00:00Z"}
{"Id":2,"Username":"bob","Email":"bob@example.com","IsDeleted":0,"CreatedAt":"2026-06-25T12:01:00Z","UpdatedAt":"2026-06-25T12:01:00Z"}
```

**Mutation model:**

| Operation | File action |
|---|---|
| Insert | `File.AppendAllText` — append one line per row |
| Update | Read all lines → modify matching → `File.WriteAllLines` (full rewrite) |
| Soft delete | Update `IsDeleted` to `1` — same as Update |
| Hard delete | Read all lines → omit matching → `File.WriteAllLines` (full rewrite) |

### `{TableName}.{IndexName}.ndx` — Index

Sorted ascending by Key. One entry per line. Used for O(log n) binary-search lookups.

```
{"Key":"alice","Id":1}
{"Key":"bob","Id":2}
```

For composite indexes, `Key` is a pipe-delimited concatenation of the column values: `"alice|active"`.

Index files are kept in sync on every insert, update, and delete that touches an indexed column. `XBase-Index-Rebuild` regenerates an index from scratch from the live `.ndjson` file.

### Constraints Enforcement

Without a database engine to enforce constraints, the skills enforce them explicitly:

| Constraint | Enforcement |
|---|---|
| `NOT NULL` | Skill checks field presence and non-null value before writing |
| `UNIQUE` | Skill reads the column's index (or full table scan if no index) before writing |
| `PRIMARY KEY` | Managed via `NextId` in `_schema.json`; never re-used |
| `FOREIGN KEY` | Skill reads `_schema.json` for the FK target, then reads the target table to verify the parent Id exists |
| `DEFAULT` | Skill injects the default value when the field is absent from the input |

---

## Transaction Model

Transactions use **directory snapshots** — no third-party lock managers.

### Begin

1. Create `_txn_{TransactionName}/` directory inside the database directory
2. Copy `_schema.json` into `_txn_{TransactionName}/_schema.json`
3. Table data files are copied **lazily**: only when a table is first written during the transaction

All subsequent reads and writes during the transaction operate on files inside `_txn_{TransactionName}/`. Live data files are untouched until Commit.

### During a Transaction

- **Reads**: if a table file exists in `_txn_{TransactionName}/`, read from there; otherwise read from the live directory
- **Writes**: copy the table file into `_txn_{TransactionName}/` if not already there (lazy copy), then write to the copy

### Commit

1. For each modified file in `_txn_{TransactionName}/`: move it over the corresponding live file (`File.Move` — atomic on the same volume)
2. Update `_meta.json` `UpdatedAt`
3. Delete `_txn_{TransactionName}/` directory

### Rollback

Delete `_txn_{TransactionName}/` and its contents. Live files were never modified.

### Savepoints

- `Transaction-Savepoint("sp1")`: copy the current `_txn_{TransactionName}/` state into `_txn_{TransactionName}/sp_sp1/`
- `Transaction-Rollback(ToSavepoint:"sp1")`: overwrite `_txn_{TransactionName}/` contents with `sp_sp1/` contents; delete `sp_sp1/`

---

## Skill Catalog

### Database Lifecycle

| Skill | Description |
|---|---|
| `XBase-Database-Initialize` | Create a new database directory with `_meta.json` and `_schema.json` |
| `XBase-Database-Connect` | Validate a database directory and register a named connection alias |
| `XBase-Database-Disconnect` | Deregister a connection alias |
| `XBase-Database-Drop` | Delete a database directory and all its contents |

### Schema Management

| Skill | Description |
|---|---|
| `XBase-Schema-TableCreate` | Add a table definition to `_schema.json` and create an empty `.ndjson` file |
| `XBase-Schema-TableAlter` | Add columns to a table definition in `_schema.json` |
| `XBase-Schema-TableDrop` | Remove a table from `_schema.json` and delete its `.ndjson` and `.ndx` files |
| `XBase-Schema-TableList` | Return all table names from `_schema.json` |
| `XBase-Schema-ColumnList` | Return column definitions for a table from `_schema.json` |

### Record Operations (CRUD)

| Skill | Description |
|---|---|
| `XBase-Record-Insert` | Append rows to a `.ndjson` file; enforce constraints; update indexes |
| `XBase-Record-Select` | Read `.ndjson`, apply filter/sort/pagination in memory; return matching rows |
| `XBase-Record-Update` | Read `.ndjson`, modify matching rows, rewrite file; update indexes |
| `XBase-Record-Delete` | Soft-delete (set `IsDeleted=1`) or hard-delete (rewrite without matching rows) |
| `XBase-Record-Upsert` | Insert or update based on conflict columns |

### Query Operations

| Skill | Description |
|---|---|
| `XBase-Query-Filter` | Compile a filter specification object (no file I/O) |
| `XBase-Query-Sort` | Compile a sort specification object (no file I/O) |
| `XBase-Query-Join` | Compile a join specification object (no file I/O) |
| `XBase-Query-Aggregate` | Compile an aggregate specification object (no file I/O) |
| `XBase-Query-Execute` | Execute a compound query specification against the database |

### Index Operations

| Skill | Description |
|---|---|
| `XBase-Index-Create` | Read `.ndjson`, build sorted `.ndx` file, register in `_schema.json` |
| `XBase-Index-Drop` | Delete `.ndx` file, remove from `_schema.json` |
| `XBase-Index-Rebuild` | Re-read `.ndjson`, rewrite `.ndx` file from scratch |
| `XBase-Index-List` | Return index definitions for a table from `_schema.json` |

### Transaction Control

| Skill | Description |
|---|---|
| `XBase-Transaction-Begin` | Create `_txn_{name}/` directory; lazy-copy schema |
| `XBase-Transaction-Commit` | Move transaction files to live; delete transaction directory |
| `XBase-Transaction-Rollback` | Delete transaction directory (all changes discarded) |
| `XBase-Transaction-Savepoint` | Snapshot current transaction state into `_txn_{name}/sp_{name}/` |

### Backup and Restore

| Skill | Description |
|---|---|
| `XBase-Backup-Create` | Copy the entire database directory to `AiXBase/backups/{name}_{timestamp}/` |
| `XBase-Backup-Restore` | Replace live database directory with a backup directory copy |
| `XBase-Backup-Verify` | Read `_meta.json`, `_schema.json`, and all `.ndjson` files; validate each JSON line |

---

## Skill Specifications

### XBase-Database-Initialize

**Inputs**
- `DatabaseName` (string) — name of the database directory to create under `AiXBase/`
- `OverwriteIfExists` (bool, default `false`)

**Outputs**
- `DatabasePath` (string) — absolute path to the created directory
- `CreatedAt` (ISO-8601)

**Steps**
1. Resolve `AiXBase/{DatabaseName}/` to an absolute path
2. If the directory already exists and `OverwriteIfExists` is `false`, return `XBASE_DATABASE_EXISTS`
3. If the directory already exists and `OverwriteIfExists` is `true`, delete it recursively
4. `Directory.CreateDirectory(DatabasePath)`
5. Write `_meta.json`: `{ XBaseVersion:1, Name, CreatedAt, UpdatedAt }`
6. Write `_schema.json`: `{ Tables:[], Indexes:[] }`
7. Return `DatabasePath` and `CreatedAt`

---

### XBase-Database-Connect

**Inputs**
- `DatabaseName` (string) — name of the database directory under `AiXBase/`
- `ConnectionName` (string) — logical alias for subsequent skill calls

**Outputs**
- `ConnectionName` (string)
- `IsOpen` (bool)

**Steps**
1. Resolve `AiXBase/{DatabaseName}/` to an absolute path
2. Verify directory exists; if not, return `XBASE_DATABASE_NOT_FOUND`
3. Read `_meta.json`; verify `XBaseVersion` field exists; if missing, return `XBASE_DATABASE_CORRUPT`
4. Register `ConnectionName → DatabasePath` mapping in the session
5. Return `ConnectionName` and `IsOpen: true`

---

### XBase-Schema-TableCreate

**Inputs**
- `ConnectionName` (string)
- `TableName` (string)
- `Columns` (array of `{ Name, Type, Nullable, Default, PrimaryKey, Unique, ForeignKey }`)
- `IfNotExists` (bool, default `true`)

**Outputs**
- `TableName` (string)
- `ColumnCount` (int)

**Steps**
1. Read `_schema.json`
2. If table already defined and `IfNotExists` is `true`, return `Success:true` (no-op)
3. If table already defined and `IfNotExists` is `false`, return `XBASE_SCHEMA_TABLE_EXISTS`
4. Prepend implicit `Id INTEGER PK AutoIncrement` column unless a `PrimaryKey:true` column is supplied
5. Append implicit `CreatedAt TEXT`, `UpdatedAt TEXT`, `IsDeleted INTEGER DEFAULT 0` columns unless already present
6. Validate no duplicate column names
7. Add table entry to `_schema.json` with `NextId:1`; write `_schema.json`
8. Write an empty `{TableName}.ndjson` file
9. Return `TableName` and `ColumnCount`

---

### XBase-Record-Insert

**Inputs**
- `ConnectionName` (string)
- `TableName` (string)
- `Rows` (array of key-value objects)
- `TransactionName` (string, optional)

**Outputs**
- `InsertedCount` (int)
- `LastInsertedId` (int)

**Steps**
1. Read `_schema.json` (from transaction workspace if `TransactionName` supplied, else live)
2. Locate target table; resolve `.ndjson` path (transaction workspace or live)
3. For each row:
   a. Enforce `NOT NULL` constraints; inject `Default` values for missing optional fields
   b. Enforce `UNIQUE` constraints: for each unique column, read its `.ndx` (if exists) or scan `.ndjson`
   c. Enforce `FOREIGN KEY` constraints: read target table to verify parent Id
   d. Assign `Id = NextId`; set `CreatedAt = UpdatedAt = now()`; set `IsDeleted = 0`
   e. Append serialised JSON line to `.ndjson`
   f. Update each affected `.ndx` file (insert sorted entry)
   g. Increment `NextId` in `_schema.json`
4. Write updated `_schema.json`
5. Return `InsertedCount` and `LastInsertedId`

---

### XBase-Record-Select

**Inputs**
- `ConnectionName` (string)
- `TableName` (string)
- `Columns` (array, default `["*"]`)
- `Filter` (filter specification from `XBase-Query-Filter`, optional)
- `Sort` (sort specification from `XBase-Query-Sort`, optional)
- `Limit` (int, optional)
- `Offset` (int, optional)
- `IncludeDeleted` (bool, default `false`)

**Outputs**
- `Rows` (array of objects)
- `TotalCount` (int) — matching count before Limit/Offset

**Steps**
1. Read all lines from `{TableName}.ndjson`; parse each line as JSON
2. Unless `IncludeDeleted`, discard rows where `IsDeleted = 1`
3. Apply `Filter` specification: for each row, evaluate each filter condition; keep rows where all conditions pass
4. `TotalCount` = count of rows passing filter
5. Apply `Sort` specification: sort in memory by specified fields and directions
6. Apply `Offset` (skip N rows) and `Limit` (take N rows)
7. Apply `Columns` projection: if not `["*"]`, keep only listed fields
8. Return `Rows` and `TotalCount`

---

### XBase-Query-Filter

Pure compilation step — **no file I/O**.

**Inputs**
- `Field` (string)
- `Operator` (`=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`)
- `Value` (scalar or array for `IN` / `NOT IN`)
- `LogicalOperator` (`AND` | `OR`, default `AND`) — how this filter chains to the previous one
- `Filters` (array of sub-filter objects, optional) — for nested groups

**Outputs**
- Compiled filter specification object passed to Record and Query skills

**Steps**
1. Validate `Field` is a safe identifier (letters, numbers, underscore only)
2. Validate `Operator` is in the allowed set
3. Validate `Value` is present for operators that require it; absent for `IS NULL` / `IS NOT NULL`
4. Return the filter specification object

---

### XBase-Query-Execute

Execute a **compound query specification** — a single structured operation combining filter, sort, join, and aggregate in one call. Use this when composing multiple query primitives into one round-trip.

**Inputs**
- `ConnectionName` (string)
- `Operation` (string) — `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- `TableName` (string)
- `Columns` (array, default `["*"]`) — for SELECT projections
- `Filter` (filter specification, optional)
- `Sort` (sort specification, optional)
- `Join` (join specification, optional)
- `Aggregate` (aggregate specification, optional)
- `Limit` (int, optional)
- `Offset` (int, optional)
- `Values` (object, optional) — field values for INSERT / UPDATE
- `TransactionName` (string, optional)

**Outputs**

For `SELECT`:
```json
{ "Success": true, "Rows": [...], "TotalCount": 5 }
```

For `INSERT`:
```json
{ "Success": true, "InsertedCount": 1, "LastInsertedId": 42 }
```

For `UPDATE` / `DELETE`:
```json
{ "Success": true, "AffectedRows": 3 }
```

**Steps**
1. Validate `ConnectionName` and `Operation`
2. Dispatch to the appropriate record operation based on `Operation`:
   - `SELECT` → apply Filter, Join, Aggregate, Sort, Limit, Offset to `.ndjson` data in memory
   - `INSERT` → enforce constraints, append to `.ndjson`, update indexes
   - `UPDATE` → read `.ndjson`, apply Filter, modify matching rows with `Values`, rewrite
   - `DELETE` → read `.ndjson`, apply Filter, soft or hard delete matching rows, rewrite

---

### XBase-Transaction-Begin

**Inputs**
- `ConnectionName` (string)
- `TransactionName` (string) — logical alias
- `IsolationLevel` (string, optional) — reserved for future use; currently ignored (all transactions use the directory-snapshot model)

**Outputs**
- `TransactionName` (string)
- `StartedAt` (ISO-8601)

**Steps**
1. Validate `ConnectionName`
2. If `_txn_{TransactionName}/` already exists in the database directory, return `XBASE_TRANSACTION_NAME_IN_USE`
3. `Directory.CreateDirectory(_txn_{TransactionName}/)`
4. Copy `_schema.json` into `_txn_{TransactionName}/_schema.json`
5. Register `TransactionName → DatabasePath` mapping in the session
6. Return `StartedAt`

---

### XBase-Transaction-Commit

**Steps**
1. Validate `TransactionName` is active
2. For each file in `_txn_{TransactionName}/` (excluding savepoint subdirectories):
   - `File.Move` it over the corresponding live file in the database directory
3. Update live `_meta.json` `UpdatedAt`
4. `Directory.Delete(_txn_{TransactionName}/, recursive:true)`
5. Deregister `TransactionName`

---

### XBase-Transaction-Rollback

**Steps**
1. Validate `TransactionName` is active
2. If `ToSavepoint` specified:
   a. Verify `_txn_{TransactionName}/sp_{ToSavepoint}/` exists
   b. Overwrite `_txn_{TransactionName}/` files with savepoint copies
   c. `Directory.Delete` the savepoint subdirectory
3. If no `ToSavepoint`:
   a. `Directory.Delete(_txn_{TransactionName}/, recursive:true)`
   b. Deregister `TransactionName`

---

### XBase-Backup-Create

**Steps**
1. Validate `ConnectionName`
2. Resolve source database directory
3. Ensure `AiXBase/backups/` exists; create if not
4. Generate destination name: `{DatabaseName}_{YYYYMMDDTHHmmss}[_{BackupLabel}]`
5. `Directory.Copy(source, AiXBase/backups/{dest}/)` — recursive file copy
6. Return `BackupPath` and `CreatedAt`

---

### XBase-Backup-Restore

**Steps**
1. Verify backup directory exists at `BackupPath`
2. Require `ConfirmRestore: true`; if absent, return `XBASE_RESTORE_NOT_CONFIRMED`
3. If `CreateBackupBeforeRestore`: run `XBase-Backup-Create` first; record `PreRestoreBackupPath`
4. Close all connections to the target database
5. `Directory.Delete(TargetDatabasePath, recursive:true)`
6. `Directory.Copy(BackupPath, TargetDatabasePath)`
7. Return `PreRestoreBackupPath` (if taken) and `RestoredAt`

---

### XBase-Backup-Verify

**Steps**
1. Verify directory exists at `BackupPath`; if not, return `XBASE_BACKUP_NOT_FOUND`
2. Read `_meta.json`; verify `XBaseVersion` field; if invalid, return `XBASE_BACKUP_CORRUPT`
3. Read `_schema.json`; verify `Tables` array is valid JSON; if invalid, return `XBASE_BACKUP_CORRUPT`
4. For each table in `_schema.json`:
   a. Verify `{TableName}.ndjson` exists
   b. Read every line; attempt `JSON.Parse(line)`; if any line fails, record the error
5. Return `IntegrityOk: true/false` and `Issues` array

---

## Data Model

All tables managed by XBase share these implicit conventions:

| Column | Type | Notes |
|---|---|---|
| `Id` | `INTEGER` | Primary key; value from `NextId` in `_schema.json`; never reused |
| `CreatedAt` | `TEXT` | ISO-8601; set on insert; never modified |
| `UpdatedAt` | `TEXT` | ISO-8601; set on insert and on every update |
| `IsDeleted` | `INTEGER` | `0` = active; `1` = soft-deleted; default `0` |

`XBase-Record-Select` automatically excludes rows where `IsDeleted = 1` unless `IncludeDeleted: true` is passed.

`XBase-Record-Delete` sets `IsDeleted = 1` by default. Pass `HardDelete: true` to physically remove the line from the `.ndjson` file.

---

## File System Primitives Used

All XBase skills are implemented using only these OS-level operations:

| Primitive | Usage |
|---|---|
| `Directory.CreateDirectory(path)` | Create database, transaction, backup directories |
| `Directory.Delete(path, recursive)` | Drop database, rollback transaction, clean up |
| `Directory.Copy(src, dest)` | Backup, restore, transaction commit |
| `Directory.GetFiles(path, pattern)` | List tables, list backups |
| `File.ReadAllText(path)` | Read `_meta.json`, `_schema.json` |
| `File.WriteAllText(path, content)` | Write `_meta.json`, `_schema.json` |
| `File.ReadAllLines(path)` | Read `.ndjson` and `.ndx` files |
| `File.WriteAllLines(path, lines)` | Rewrite `.ndjson` after update/delete |
| `File.AppendAllText(path, line)` | Append a new row to `.ndjson` |
| `File.Move(src, dest)` | Atomic commit of transaction files |
| `File.Copy(src, dest)` | Index rebuild copies, backup |
| `File.Delete(path)` | Drop table files, drop index files |
| `File.Exists(path)` | Guard checks throughout |

No SQLite, no NuGet packages, no ADO.NET, no P/Invoke.

---

## Error Handling

Every skill returns a standard error envelope on failure:

```json
{
  "Success": false,
  "ErrorCode": "XBASE_<CATEGORY>_<REASON>",
  "Message": "Human-readable description.",
  "SkillName": "XBase-Record-Insert"
}
```

### Error Code Catalog

| Code | Meaning |
|---|---|
| `XBASE_DATABASE_NOT_FOUND` | Database directory does not exist |
| `XBASE_DATABASE_EXISTS` | Directory already exists and `OverwriteIfExists` is `false` |
| `XBASE_DATABASE_PATH_INVALID` | Name escapes `AiXBase/` or contains illegal characters |
| `XBASE_DATABASE_CORRUPT` | `_meta.json` or `_schema.json` is missing or unparseable |
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_CONNECTION_NAME_IN_USE` | `ConnectionName` already registered |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_SCHEMA_TABLE_EXISTS` | Table already in `_schema.json` (non-IfNotExists path) |
| `XBASE_SCHEMA_COLUMN_MISSING` | Referenced column not defined for this table |
| `XBASE_SCHEMA_COLUMN_INVALID` | Column definition is malformed or duplicated |
| `XBASE_SCHEMA_COLUMN_EXISTS` | Column already defined (TableAlter) |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | NOT NULL / UNIQUE / FK violated |
| `XBASE_RECORD_FILTER_REQUIRED` | Update or Delete called with no Filter |
| `XBASE_FILTER_FIELD_INVALID` | Field name fails safe-identifier check |
| `XBASE_FILTER_OPERATOR_UNKNOWN` | Operator not in the allowed set |
| `XBASE_FILTER_VALUE_REQUIRED` | Operator requires a Value but none supplied |
| `XBASE_INDEX_NOT_FOUND` | `.ndx` file and schema entry not found |
| `XBASE_INDEX_EXISTS` | Index already defined (non-IfNotExists path) |
| `XBASE_TRANSACTION_NOT_OPEN` | No `_txn_{name}/` directory for the given name |
| `XBASE_TRANSACTION_NAME_IN_USE` | `_txn_{name}/` directory already exists |
| `XBASE_SAVEPOINT_NOT_FOUND` | Savepoint subdirectory does not exist |
| `XBASE_SAVEPOINT_NAME_IN_USE` | Savepoint subdirectory already exists |
| `XBASE_BACKUP_NOT_FOUND` | Backup directory does not exist |
| `XBASE_BACKUP_CORRUPT` | `_meta.json` invalid or one or more NDJSON lines fail to parse |
| `XBASE_BACKUP_IO_ERROR` | File system error during copy |
| `XBASE_RESTORE_NOT_CONFIRMED` | `ConfirmRestore` not `true` |
| `XBASE_DROP_NOT_CONFIRMED` | `ConfirmDrop` not `true` |
| `XBASE_SORT_DIRECTION_INVALID` | Direction not `ASC` or `DESC` |
| `XBASE_SORT_FIELD_INVALID` | Field name fails safe-identifier check |
| `XBASE_JOIN_TYPE_INVALID` | Join type not `INNER` or `LEFT` |
| `XBASE_JOIN_REFERENCE_INVALID` | Join column reference is malformed |
| `XBASE_AGGREGATE_FUNCTION_UNKNOWN` | Function not in `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` |

---

## Dependencies

- File system with read/write access to `AiXBase/`
- No external network dependencies
- No third-party libraries
- All skill inputs and outputs are serializable to JSON
