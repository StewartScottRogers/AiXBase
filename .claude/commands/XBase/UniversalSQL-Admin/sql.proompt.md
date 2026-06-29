# /sql — Interactive SQL Shell

Run a SQL statement (or plain-English description of an operation) against an XBase database.

Follow the steps in `XBase-UniversalSQL-Admin-REPL`:

1. If no XBase connection is currently open, ask: `Database? (name or connection alias):` then call `XBase-Database-Connect`.
2. If the input is not SQL (no SQL keyword at the start), infer the SQL and show it: `→ Running: {inferred SQL}`.
3. Handle REPL shortcuts: `EXIT`/`\q` disconnect and end; `\t {table}` → `DESCRIBE {table}`; `\l` → `SHOW TABLES`; `\history` → list last 20; `!n` → re-execute nth; `\explain {SQL}` → plan only; `\schema [{table}]` → DDL extract.
4. Validate with `XBase-UniversalSQL-Validate`; display issues without executing if `Valid: false`.
5. Execute with `XBase-UniversalSQL-Execute`; track `TransactionName` state across `BEGIN`/`COMMIT`/`ROLLBACK`.
6. Display results as a Unicode box-drawing table for SELECT, `✓ N rows affected` for writes, `✓ created/dropped` for DDL, `✗ ErrorCode\n   Message` for errors.
7. Stay in the SQL prompt loop; repeat from step 2.

$ARGUMENTS
