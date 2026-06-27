# XBase-Admin-Execute

Execute any XBase database operation described in natural language.

## Usage

```
/execute <plain-English description of what you want to do>
```

Provide a plain-English description. This command parses the intent, collects any missing parameters, maps the request to the appropriate XBase skill(s), executes them, and returns a human-readable summary.

---

## Intent-to-Skill Map

| If the request mentions… | Invoke… |
|---|---|
| create / initialise / new database | `XBase-Database-Initialize` |
| connect / open / use database | `XBase-Database-Connect` |
| close / disconnect | `XBase-Database-Disconnect` |
| drop / delete / remove database | `XBase-Database-Drop` |
| create / add table | `XBase-Schema-TableCreate` |
| alter / add column | `XBase-Schema-TableAlter` |
| drop / remove table | `XBase-Schema-TableDrop` |
| list / show tables | `XBase-Schema-TableList` |
| list / show columns | `XBase-Schema-ColumnList` |
| insert / add / create record(s) | `XBase-Record-Insert` |
| select / query / show / find / get records | `XBase-Record-Select` + `XBase-Query-Filter` + `XBase-Query-Sort` |
| update / change / set record(s) | `XBase-Record-Update` |
| delete / remove / soft-delete record(s) | `XBase-Record-Delete` |
| upsert / insert-or-update | `XBase-Record-Upsert` |
| create / add index | `XBase-Index-Create` |
| drop / remove index | `XBase-Index-Drop` |
| rebuild index | `XBase-Index-Rebuild` |
| list / show indexes | `XBase-Index-List` |
| begin / start transaction | `XBase-Transaction-Begin` |
| commit transaction | `XBase-Transaction-Commit` |
| rollback / undo transaction | `XBase-Transaction-Rollback` |
| savepoint | `XBase-Transaction-Savepoint` |
| backup | `XBase-Backup-Create` |
| restore backup | `XBase-Backup-Restore` |
| verify backup | `XBase-Backup-Verify` |

---

## Steps

1. Read the user's natural-language request
2. Identify the primary operation type using the Intent-to-Skill Map above
3. Extract parameters from the request (DatabaseName, TableName, column definitions, filter values, etc.)
4. If any **required** parameter is missing, ask the user for it before proceeding
5. If the operation is **destructive** (Drop, HardDelete, Restore, OverwriteIfExists), confirm with the user unless the request already contains a confirmation phrase such as "I'm sure", "yes", "confirm", or `ConfirmDrop: true`
6. Execute the identified skill(s) in the correct order (e.g. Initialize then Connect; Begin then Insert then Commit)
7. Present the result as a plain-text summary:
   - On success: what was done, key output values (e.g. `InsertedCount`, `DatabasePath`, `BackupPath`)
   - On error: the `ErrorCode` and `Message` from the skill's error envelope, with a plain-English explanation and suggested next step

---

## Parameter Extraction Examples

| Request | Extracted parameters |
|---|---|
| `create a database called "inventory"` | `DatabaseName:"inventory"` |
| `show all products where price > 50 sorted by name` | `TableName:"Products"`, Filter `Price > 50`, Sort `Name ASC` |
| `insert SKU=P001, Label=Widget, Price=9.99` | `Rows:[{SKU:"P001",Label:"Widget",Price:9.99}]` |
| `backup the inventory database with label pre-migration` | `DatabaseName:"inventory"`, `BackupLabel:"pre-migration"` |
| `drop table OldLogs — I'm sure` | `TableName:"OldLogs"`, `ConfirmDrop:true` |

---

## Error Handling

Surface the XBase error code and message with plain-English context:

```
Error: XBASE_DATABASE_EXISTS
The database "inventory" already exists. To overwrite it, add "overwrite" to your request.
```

---

## Dependencies

All 28 XBase skills. This command performs no direct file I/O.
