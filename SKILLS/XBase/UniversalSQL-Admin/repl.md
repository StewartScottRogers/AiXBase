# XBase-UniversalSQL-Admin-REPL

Interactive SQL shell for XBase databases. Accepts one SQL statement at a time (or a plain-English description), validates, executes, and displays results in a formatted table. Maintains connection and transaction state across turns within a session.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SQL` | string | yes | A SQL statement to execute, or a plain-English description of the operation |
| `ConnectionName` | string | no | Active connection alias; if omitted and no connection is open, the skill will prompt for a database name |
| `TransactionName` | string | no | Route DML writes through this transaction workspace (carried forward automatically after a `BEGIN`) |

## Outputs

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

For DDL:
```
✓  Table "Products" created (5 columns)
```

For TCL:
```
✓  Transaction "tx1" started
```

For errors:
```
✗  XBASE_RECORD_CONSTRAINT_VIOLATION
   NOT NULL constraint failed on column "SKU"
```

## Steps

1. If no `ConnectionName` is supplied and no connection is currently open in the session, display `Database? (name or connection alias):` and call `XBase-Database-Connect` with the user-provided name.
2. If `SQL` does not begin with a SQL keyword (SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, BEGIN, COMMIT, ROLLBACK, SAVEPOINT, SHOW, DESCRIBE, BACKUP, RESTORE, EXPLAIN, EXIT, `\`), treat it as a plain-English description: infer the intended SQL statement from the description and display it to the user as `→ Running: {inferred SQL}` before proceeding.
3. Check for REPL special commands:
   - `EXIT` or `\q`: call `XBase-Database-Disconnect` on the current connection and end the session.
   - `\t {table}`: expand to `DESCRIBE {table}`.
   - `\l`: expand to `SHOW TABLES`.
   - `\history`: display the last 20 SQL statements from the current session history.
   - `!{n}`: re-execute the nth statement from history.
   - `\explain {SQL}`: call `XBase-UniversalSQL-Admin-Explain` on the given SQL without executing it; skip to step 8.
   - `\schema [{table}]`: call `XBase-UniversalSQL-Admin-Schema` for the current database; skip to step 8.
4. Call `XBase-UniversalSQL-Validate` with `ConnectionName` and `SQL`; if `Valid: false`, display each Error-severity issue as `✗  {Code}\n   {Message}` and return to the prompt without executing.
5. Call `XBase-UniversalSQL-Execute` with `ConnectionName`, `SQL`, and `TransactionName` (if set).
6. Track transaction state: if the statement was `BEGIN`, set `TransactionName` in session state; if `COMMIT` or `ROLLBACK`, clear `TransactionName`.
7. Append the executed SQL to the session history list (trim list to 20 entries).
8. Format and display the result:
   - `SELECT` / `SHOW TABLES` / `DESCRIBE`: render `Rows` as a Unicode box-drawing table with column headers derived from `ColumnNames`; append `{ReturnedCount} rows  (TotalCount: {TotalCount})`.
   - `INSERT`: display `✓  {InsertedCount} rows affected\n   LastInsertedId: {LastInsertedId}`.
   - `UPDATE` / `DELETE`: display `✓  {AffectedRows} rows affected`.
   - DDL: display `✓  {TableName or IndexName} {created|dropped|altered}`.
   - TCL: display `✓  Transaction "{TransactionName}" {started|committed|rolled back}`.
   - Errors: display `✗  {ErrorCode}\n   {Message}`.
9. Return to the SQL prompt. Repeat from step 2.

## Error Codes

All error codes from `XBase-UniversalSQL-Execute` and `XBase-UniversalSQL-Validate` are displayed inline; none terminate the session.

## Dependencies

- `XBase-Database-Connect` — session setup
- `XBase-Database-Disconnect` — session teardown on `EXIT`
- `XBase-UniversalSQL-Validate` — pre-execution validation
- `XBase-UniversalSQL-Execute` — statement execution
- `XBase-UniversalSQL-Admin-Explain` — `\explain` shortcut
- `XBase-UniversalSQL-Admin-Schema` — `\schema` shortcut
