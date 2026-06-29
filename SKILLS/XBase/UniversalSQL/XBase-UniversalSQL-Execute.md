# XBase-UniversalSQL-Execute

Parse and execute a SQL statement against a named XBase connection, returning results in a unified envelope.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active XBase connection alias (established via `XBase-Database-Connect`) |
| `SQL` | string | yes | The SQL statement to execute |
| `TransactionName` | string | no | Route all write operations through this transaction workspace |
| `Parameters` | object | no | Named parameter bindings; substituted for `?name` placeholders in `SQL` |

## Outputs

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

## Steps

1. Call `XBase-UniversalSQL-Validate` with `ConnectionName`, `SQL`, and `Parameters`; if `Valid: false`, return the first `Error`-severity issue code as the error and `Success: false`.
2. Substitute `Parameters` into any `?name` placeholders in `SQL`.
3. Call `XBase-UniversalSQL-Parse` with the substituted `SQL` to obtain `StatementType` and `ExecutionPlan`.
4. Dispatch each step in `ExecutionPlan` to its mapped XBase skill, passing `ConnectionName` and `TransactionName` (for write operations) where the step requires them. Execute steps in declared order; if any step returns `Success: false`, propagate the error immediately and halt execution.
5. Collect and unify results according to `StatementType`:
   - `SELECT` / `SHOW TABLES` / `DESCRIBE`: collect `Rows`, `TotalCount`, and derive `ColumnNames` from the first row's keys; set `ReturnedCount` to `Rows` length.
   - `INSERT`: collect `InsertedCount` and `LastInsertedId` from `XBase-Record-Insert`.
   - `UPDATE`: collect `AffectedRows` from `XBase-Record-Update`.
   - `DELETE`: collect `AffectedRows` from `XBase-Record-Delete`.
   - DDL: collect `TableName` or `IndexName` from the executed DDL skill.
   - TCL: echo `TransactionName` from the executed TCL skill.
   - `BACKUP DATABASE` / `RESTORE DATABASE`: propagate the result envelope from `XBase-Backup-Create` / `XBase-Backup-Restore`.
   - `EXPLAIN`: call `XBase-UniversalSQL-Explain` on the inner statement; return its result without executing the inner statement.
6. Return the unified result envelope.

## Error Codes

| Code | Meaning |
|------|---------|
| `USQL_EXECUTE_NO_CONNECTION` | `ConnectionName` not registered |
| `USQL_WHERE_REQUIRED` | `UPDATE` or `DELETE` submitted without a `WHERE` clause |
| `USQL_PARSE_SYNTAX_ERROR` | SQL could not be parsed — propagated from `XBase-UniversalSQL-Validate` |
| `USQL_PARSE_UNSUPPORTED_STATEMENT` | Statement type not supported |
| `USQL_VALIDATE_TABLE_NOT_FOUND` | Table does not exist in the schema |
| `USQL_VALIDATE_COLUMN_NOT_FOUND` | Column does not exist in the referenced table |

All error codes from the underlying XBase skill set (e.g. `XBASE_RECORD_CONSTRAINT_VIOLATION`, `XBASE_SCHEMA_TABLE_NOT_FOUND`) are propagated unchanged.

## Dependencies

- `XBase-Database-Connect` — connection must be established before calling Execute
- `XBase-UniversalSQL-Validate` — pre-execution validation
- `XBase-UniversalSQL-Parse` — statement parsing and execution plan
- `XBase-Record-Select` — `SELECT`
- `XBase-Record-Insert` — `INSERT`
- `XBase-Record-Update` — `UPDATE`
- `XBase-Record-Delete` — `DELETE`
- `XBase-Record-Upsert` — `INSERT … ON CONFLICT`
- `XBase-Query-Filter` — `WHERE` clause
- `XBase-Query-Sort` — `ORDER BY` clause
- `XBase-Query-Join` — `JOIN` clause
- `XBase-Query-Aggregate` — `GROUP BY` and aggregate functions
- `XBase-Schema-TableCreate` — `CREATE TABLE`
- `XBase-Schema-TableDrop` — `DROP TABLE`
- `XBase-Schema-TableAlter` — `ALTER TABLE ADD COLUMN`
- `XBase-Schema-TableList` — `SHOW TABLES`
- `XBase-Schema-ColumnList` — `DESCRIBE` / `SHOW COLUMNS`
- `XBase-Index-Create` — `CREATE INDEX`
- `XBase-Index-Drop` — `DROP INDEX`
- `XBase-Transaction-Begin` — `BEGIN`
- `XBase-Transaction-Commit` — `COMMIT`
- `XBase-Transaction-Rollback` — `ROLLBACK`
- `XBase-Transaction-Savepoint` — `SAVEPOINT`
- `XBase-Backup-Create` — `BACKUP DATABASE`
- `XBase-Backup-Restore` — `RESTORE DATABASE`
- `XBase-UniversalSQL-Explain` — `EXPLAIN` (inner statement plan only; no execution)
