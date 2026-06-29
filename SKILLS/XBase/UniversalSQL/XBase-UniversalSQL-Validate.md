# XBase-UniversalSQL-Validate

Check a SQL statement for syntax errors and semantic errors against the live schema without executing any data operations.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SQL` | string | yes | The SQL statement to validate |
| `ConnectionName` | string | no | If supplied, semantic validation checks tables and columns against the live `_schema.json` |
| `Parameters` | object | no | Named parameter bindings substituted before parsing |

## Outputs

```json
{
  "Success": true,
  "Valid": false,
  "Issues": [
    {
      "Severity": "Error",
      "Code": "USQL_VALIDATE_COLUMN_NOT_FOUND",
      "Position": 12,
      "Message": "Column 'Bogus' not found in table 'Products'"
    }
  ],
  "IssueCount": 1
}
```

`Valid` is `true` when `Issues` contains no `Error`-severity entries. `Success` refers to the skill call itself, not to `Valid`.

## Steps

1. Call `XBase-UniversalSQL-Parse` with `SQL` and `Parameters`; collect any parse errors. If `USQL_PARSE_SYNTAX_ERROR` or `USQL_PARSE_UNSUPPORTED_STATEMENT` is returned, add an `Error`-severity issue and skip remaining steps (semantic checks require a valid AST).
2. Check for unsupported clause combinations in the AST (e.g. `GROUP BY` without `SELECT`, `HAVING` clause present); add an `Error`-severity issue with code `USQL_PARSE_UNSUPPORTED_CLAUSE` for each violation.
3. If `ConnectionName` is supplied and the parse produced a valid AST:
   a. For each table referenced in `FROM`, `JOIN`, `UPDATE`, `DELETE`, `INSERT`, or DDL clauses: call `XBase-Schema-TableList` and verify the table name exists; if not, add `Error` issue `USQL_VALIDATE_TABLE_NOT_FOUND`.
   b. For each valid table reference: call `XBase-Schema-ColumnList` and validate every explicitly named column; if a column is not found, add `Error` issue `USQL_VALIDATE_COLUMN_NOT_FOUND`.
   c. For queries with `JOIN`: check that column references used in `ON` conditions and `SELECT` projections are unambiguous across joined tables; if a column name appears in two or more tables without a table qualifier, add `Error` issue `USQL_VALIDATE_AMBIGUOUS_COLUMN`.
   d. For each literal value assigned to or compared against a typed column: verify type compatibility (e.g. a string literal compared to an `INTEGER` column); add `Warning` issue `USQL_VALIDATE_TYPE_MISMATCH` on mismatch.
4. Safety checks (apply regardless of `ConnectionName`):
   a. `UPDATE` or `DELETE` without a `WHERE` clause: add `Warning` issue `USQL_WHERE_REQUIRED`.
   b. `DROP TABLE` or `DROP INDEX` without `IF EXISTS`: add `Info` issue `USQL_DROP_NO_IF_EXISTS`.
5. Return `Valid` (`true` if no `Error`-severity issues), `Issues` (all collected issues), and `IssueCount`.

## Error Codes

| Code | Severity | Condition |
|------|----------|-----------|
| `USQL_PARSE_SYNTAX_ERROR` | Error | Token sequence does not match supported grammar |
| `USQL_PARSE_UNSUPPORTED_STATEMENT` | Error | Statement type not in the supported set |
| `USQL_PARSE_UNSUPPORTED_CLAUSE` | Error | Clause combination not allowed |
| `USQL_VALIDATE_TABLE_NOT_FOUND` | Error | Table name does not exist in `_schema.json` |
| `USQL_VALIDATE_COLUMN_NOT_FOUND` | Error | Column name not defined in the referenced table |
| `USQL_VALIDATE_AMBIGUOUS_COLUMN` | Error | Column name is ambiguous across joined tables |
| `USQL_VALIDATE_TYPE_MISMATCH` | Warning | Literal value is incompatible with the column's XBase type |
| `USQL_WHERE_REQUIRED` | Warning | `UPDATE` or `DELETE` has no `WHERE` clause |
| `USQL_DROP_NO_IF_EXISTS` | Info | `DROP TABLE` or `DROP INDEX` lacks `IF EXISTS` guard |

## Dependencies

- `XBase-UniversalSQL-Parse` — tokenisation and AST construction
- `XBase-Schema-TableList` — semantic table existence check (requires `ConnectionName`)
- `XBase-Schema-ColumnList` — semantic column existence check (requires `ConnectionName`)
