# XBase-UniversalSQL-Parse

Parse a SQL statement into a structured abstract syntax tree and execution plan without executing any XBase skills.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SQL` | string | yes | The SQL statement to parse |
| `Parameters` | object | no | Named parameter bindings; substituted for `?name` placeholders before parsing |

## Outputs

```json
{
  "Success": true,
  "StatementType": "SELECT",
  "AST": {
    "Type": "SelectStatement",
    "Columns":    [{ "TableAlias": null, "ColumnName": "*" }],
    "From":       { "TableName": "Products", "Alias": "p" },
    "Joins":      [],
    "Where":      { "Field": "Price", "Operator": ">", "Value": 50 },
    "GroupBy":    [],
    "OrderBy":    [{ "Field": "Label", "Direction": "ASC" }],
    "Limit":      25,
    "Offset":     0
  },
  "ExecutionPlan": [
    { "Step": 1, "Skill": "XBase-Query-Filter",  "Parameters": { "Field": "Price", "Operator": ">", "Value": 50 } },
    { "Step": 2, "Skill": "XBase-Query-Sort",    "Parameters": { "Columns": [{ "Field": "Label", "Direction": "ASC" }] } },
    { "Step": 3, "Skill": "XBase-Record-Select", "Parameters": { "TableName": "Products", "Limit": 25, "Offset": 0 } }
  ]
}
```

## Steps

1. Substitute `Parameters` values into any `?name` placeholders in `SQL`; if any placeholder has no matching entry in `Parameters`, return `USQL_PARSE_PARAMETER_MISSING`.
2. Tokenise `SQL` into a stream of tokens: keywords (case-insensitive), quoted and unquoted identifiers, string literals (single-quoted), numeric literals, operators (`=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`, `*`), punctuation (`(`, `)`, `,`, `.`). Strip leading/trailing whitespace from the statement before tokenising.
3. Parse the token stream using the supported grammar:
   - `SELECT [DISTINCT] columns FROM table [JOIN ...] [WHERE ...] [GROUP BY ...] [ORDER BY ...] [LIMIT n] [OFFSET n]`
   - `INSERT INTO table [(columns)] VALUES (literals) [, ...]`
   - `INSERT INTO table [(columns)] SELECT ...`
   - `UPDATE table SET col = val [, ...] WHERE condition`
   - `DELETE FROM table WHERE condition`
   - `INSERT INTO table [(columns)] VALUES (literals) ON CONFLICT (columns) DO UPDATE SET col = excluded.col [, ...]`
   - `CREATE TABLE [IF NOT EXISTS] table (column_def [, ...])`
   - `DROP TABLE [IF EXISTS] table`
   - `ALTER TABLE table ADD COLUMN column_def`
   - `CREATE [UNIQUE] INDEX [IF NOT EXISTS] name ON table (columns)`
   - `DROP INDEX [IF EXISTS] name`
   - `BEGIN [TRANSACTION] [name]`
   - `COMMIT [name]`
   - `ROLLBACK [TRANSACTION [name] | TO SAVEPOINT name]`
   - `SAVEPOINT name`
   - `SHOW TABLES`
   - `DESCRIBE table` / `SHOW COLUMNS FROM table`
   - `BACKUP DATABASE name [LABEL label]`
   - `RESTORE DATABASE name FROM path [CONFIRM]`
   - `EXPLAIN statement`

   On any syntax error, return `USQL_PARSE_SYNTAX_ERROR` with `Position` (token index) and `Context` (surrounding tokens).
4. Verify the detected statement type is in the supported set; if not, return `USQL_PARSE_UNSUPPORTED_STATEMENT`.
5. Verify that all clauses present are supported combinations (e.g. `GROUP BY` only inside `SELECT`); return `USQL_PARSE_UNSUPPORTED_CLAUSE` for invalid combinations.
6. Map each AST node to an execution plan step using the SQL → XBase Skill Mapping:
   - `WHERE` → `XBase-Query-Filter`
   - `ORDER BY` → `XBase-Query-Sort`
   - `JOIN` → `XBase-Query-Join`
   - `GROUP BY` + aggregate → `XBase-Query-Aggregate`
   - `SELECT` → `XBase-Record-Select`
   - `INSERT … VALUES` → `XBase-Record-Insert`
   - `INSERT … SELECT` → `XBase-Record-Select` then `XBase-Record-Insert`
   - `UPDATE` → `XBase-Record-Update` + `XBase-Query-Filter`
   - `DELETE` → `XBase-Record-Delete` + `XBase-Query-Filter`
   - `INSERT … ON CONFLICT` → `XBase-Record-Upsert`
   - `CREATE TABLE` → `XBase-Schema-TableCreate`
   - `DROP TABLE` → `XBase-Schema-TableDrop`
   - `ALTER TABLE ADD COLUMN` → `XBase-Schema-TableAlter`
   - `CREATE INDEX` → `XBase-Index-Create`
   - `DROP INDEX` → `XBase-Index-Drop`
   - `SHOW TABLES` → `XBase-Schema-TableList`
   - `DESCRIBE` / `SHOW COLUMNS` → `XBase-Schema-ColumnList`
   - `BEGIN` → `XBase-Transaction-Begin`
   - `COMMIT` → `XBase-Transaction-Commit`
   - `ROLLBACK` → `XBase-Transaction-Rollback`
   - `SAVEPOINT` → `XBase-Transaction-Savepoint`
   - `BACKUP DATABASE` → `XBase-Backup-Create`
   - `RESTORE DATABASE` → `XBase-Backup-Restore`
   - `EXPLAIN` → recursive call to `XBase-UniversalSQL-Parse` on the inner statement; return the inner plan without executing
7. Return `StatementType`, `AST`, and `ExecutionPlan`.

## Error Codes

| Code | Meaning |
|------|---------|
| `USQL_PARSE_SYNTAX_ERROR` | Token sequence does not match any supported grammar rule |
| `USQL_PARSE_UNSUPPORTED_STATEMENT` | Statement type is not in the supported set |
| `USQL_PARSE_UNSUPPORTED_CLAUSE` | A clause within a supported statement is not supported |
| `USQL_PARSE_PARAMETER_MISSING` | A `?name` placeholder has no matching entry in `Parameters` |

## Dependencies

- None — `XBase-UniversalSQL-Parse` is pure in-memory tokenisation and AST construction; no XBase connection or file I/O is required
