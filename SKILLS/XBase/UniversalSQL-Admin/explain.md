# XBase-UniversalSQL-Admin-Explain

Display the XBase execution plan for a SQL statement as a formatted markdown table — without executing the statement.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SQL` | string | yes | The SQL statement to explain |
| `ConnectionName` | string | no | If supplied, includes index coverage annotations from the live schema |
| `Parameters` | object | no | Named parameter bindings substituted before parsing |

## Outputs

```
Execution Plan for: SELECT * FROM Products WHERE Price > 10 ORDER BY Label LIMIT 25

Step │ SQL Clause                          │ XBase Skill           │ Notes
─────┼─────────────────────────────────────┼───────────────────────┼────────────────────────────────────
  1  │ WHERE Price > 10                    │ XBase-Query-Filter    │ Full table scan (no index on Price)
  2  │ ORDER BY Label ASC                  │ XBase-Query-Sort      │ In-memory sort after filter
  3  │ SELECT * FROM Products LIMIT 25     │ XBase-Record-Select   │ Reads Products.dbf; returns ≤ 25 rows

⚠  No index on column "Price" — consider: CREATE INDEX idx_price ON Products (Price)
```

## Steps

1. Call `XBase-UniversalSQL-Explain` with `SQL`, `ConnectionName` (if supplied), and `Parameters`; if the call fails, display the error and return.
2. Display the header line: `Execution Plan for: {SQL}`.
3. Render the `Plan` array as a plain-text table with box-drawing separators (Step, SQL Clause, XBase Skill, Notes columns), or output `ExplainText` directly if the caller prefers markdown.
4. For any steps where `Notes` contains a warning about missing indexes, append a `⚠` advisory line suggesting a `CREATE INDEX` statement.
5. If `XBase-UniversalSQL-Validate` (called internally by Explain) produced any Warning or Info issues, display them after the plan table.

## Error Codes

Propagates all error codes from `XBase-UniversalSQL-Explain`.

## Dependencies

- `XBase-UniversalSQL-Explain` — execution plan generation
