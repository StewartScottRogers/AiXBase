# XBase-UniversalSQL-Explain

Return a human-readable breakdown showing how each SQL clause maps to an XBase skill call, without executing the statement.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SQL` | string | yes | The SQL statement to explain |
| `ConnectionName` | string | no | If supplied, includes index coverage annotations from the live schema |
| `Parameters` | object | no | Named parameter bindings substituted before parsing |

## Outputs

```json
{
  "Success": true,
  "StatementType": "SELECT",
  "ExplainText": "| Step | SQL Clause | XBase Skill | Notes |\n|---|---|---|---|\n| 1 | WHERE Price > 50 | XBase-Query-Filter | Full table scan (no index on Price) |\n| 2 | ORDER BY Label ASC | XBase-Query-Sort | In-memory sort after filter |\n| 3 | SELECT * FROM Products LIMIT 25 | XBase-Record-Select | Reads Products.dbf; returns first 25 matching rows |",
  "Plan": [
    { "Step": 1, "Clause": "WHERE Price > 50",                       "Skill": "XBase-Query-Filter",  "Notes": "Full table scan (no index on Price)" },
    { "Step": 2, "Clause": "ORDER BY Label ASC",                     "Skill": "XBase-Query-Sort",    "Notes": "In-memory sort after filter" },
    { "Step": 3, "Clause": "SELECT * FROM Products LIMIT 25",        "Skill": "XBase-Record-Select", "Notes": "Reads Products.dbf; returns first 25 matching rows" }
  ]
}
```

`ExplainText` is `Plan` rendered as a markdown table, ready for direct display.

## Steps

1. Call `XBase-UniversalSQL-Parse` with `SQL` and `Parameters`; if parsing fails, propagate the error and return `Success: false`.
2. If `ConnectionName` is supplied: call `XBase-Schema-TableList` to enumerate available tables. For each table referenced in the execution plan, call `XBase-Schema-ColumnList` and `XBase-Index-List` to discover which columns have indexes.
3. For each step in `ExecutionPlan` from `XBase-UniversalSQL-Parse`:
   a. Extract the SQL clause text that drives this step (e.g. `WHERE Price > 50`, `ORDER BY Label ASC`).
   b. Identify the mapped XBase skill.
   c. Compose a `Notes` string:
      - For filter steps: note whether any filtered column has an index (`index scan on {col}`) or requires a full scan (`full table scan — no index on {col}`).
      - For sort steps: note `in-memory sort` (XBase always sorts in memory).
      - For join steps: note `in-memory join on {leftCol} = {rightCol}`.
      - For aggregate steps: note `in-memory grouping by {col}`.
      - For record-read steps: note the file name read and the effective row limit.
      - For write steps (insert/update/delete): note affected table and whether a transaction is involved.
      - For DDL and TCL steps: describe the structural change or transaction action.
4. Collect all plan steps into `Plan` array preserving step order.
5. Render `ExplainText` as a markdown table with columns: `Step`, `SQL Clause`, `XBase Skill`, `Notes`.
6. Return `StatementType`, `Plan`, and `ExplainText`.

## Error Codes

| Code | Meaning |
|------|---------|
| `USQL_PARSE_SYNTAX_ERROR` | SQL could not be parsed — propagated from `XBase-UniversalSQL-Parse` |
| `USQL_PARSE_UNSUPPORTED_STATEMENT` | Statement type not supported — propagated from `XBase-UniversalSQL-Parse` |

## Dependencies

- `XBase-UniversalSQL-Parse` — tokenisation and execution plan construction
- `XBase-Schema-TableList` — index annotation (requires `ConnectionName`)
- `XBase-Schema-ColumnList` — column type annotation (requires `ConnectionName`)
- `XBase-Index-List` — index coverage annotation (requires `ConnectionName`)
