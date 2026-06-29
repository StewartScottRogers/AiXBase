# /schema — SQL DDL Extractor

Extract and display CREATE TABLE DDL for tables in an XBase database.

Follow the steps in `XBase-UniversalSQL-Admin-Schema`:

1. Parse `$ARGUMENTS`: optional database name or connection alias, optional table name(s).
2. Connect if needed (`XBase-Database-Connect`), or use the currently open connection.
3. Call `XBase-Schema-TableList`; filter to requested tables if specified.
4. For each table, call `XBase-Schema-ColumnList` and emit `CREATE TABLE IF NOT EXISTS {name} (...)`.
5. Call `XBase-Index-List` and emit `CREATE INDEX IF NOT EXISTS ...` for each index.
6. Prepend `-- XBase Schema: {db}  -- Generated: {timestamp}`.
7. Display the full DDL in a fenced `sql` code block.

$ARGUMENTS
