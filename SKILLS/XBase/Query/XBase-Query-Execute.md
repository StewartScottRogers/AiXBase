# XBase-Query-Execute

Execute a compound query specification against the database in a single call. Use this skill when you need to combine filter, sort, join, and aggregate into one round-trip, or when you need a typed write operation with complex conditions.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `Operation` | string | yes | — | `SELECT`, `INSERT`, `UPDATE`, or `DELETE` |
| `TableName` | string | yes | — | Target table |
| `Columns` | array | no | `["*"]` | Column projection for `SELECT` |
| `Filter` | object | no | — | Filter specification from `XBase-Query-Filter` |
| `Sort` | array | no | — | Sort specification from `XBase-Query-Sort` |
| `Join` | object | no | — | Join specification from `XBase-Query-Join` |
| `Aggregate` | object | no | — | Aggregate specification from `XBase-Query-Aggregate` |
| `Limit` | int | no | — | Maximum rows to return (SELECT) |
| `Offset` | int | no | `0` | Rows to skip before returning results (SELECT) |
| `Values` | object | no | — | Field values for INSERT or UPDATE |
| `IncludeDeleted` | bool | no | `false` | Include soft-deleted rows in SELECT |
| `HardDelete` | bool | no | `false` | Physically remove rows (DELETE); default is soft-delete |
| `TransactionName` | string | no | — | Execute within this named transaction |

## Outputs

For `SELECT`:
```json
{
  "Success": true,
  "Rows": [ { "Id": 1, "Label": "..." } ],
  "TotalCount": 5
}
```

For `INSERT`:
```json
{
  "Success": true,
  "InsertedCount": 1,
  "LastInsertedId": 42
}
```

For `UPDATE` / `DELETE`:
```json
{
  "Success": true,
  "AffectedRows": 3
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. Validate `Operation` is one of `SELECT`, `INSERT`, `UPDATE`, `DELETE`; else return validation error
3. Resolve the active data directory (transaction workspace or live, based on `TransactionName`)
4. Read `_schema.json` to locate the table definition; if not found, return `XBASE_SCHEMA_TABLE_NOT_FOUND`
5. Dispatch by `Operation`:
   - **SELECT**: Read all lines from `{TableName}.ndjson`; parse each as JSON; apply `IncludeDeleted` filter; apply `Filter` and `Join` specifications; compute `TotalCount`; apply `Aggregate` (if supplied); apply `Sort`; apply `Offset` and `Limit`; project `Columns`; return `Rows` and `TotalCount`
   - **INSERT**: Enforce NOT NULL, UNIQUE, and FK constraints; assign `Id` from `NextId`; set `CreatedAt`, `UpdatedAt`, `IsDeleted`; append JSON line to `.ndjson`; update index `.ndx` files; write updated `_schema.json`; return `InsertedCount` and `LastInsertedId`
   - **UPDATE**: Require `Filter`; read `.ndjson`; apply Filter to find matching rows; apply `Values` to each match; enforce constraints; set `UpdatedAt`; rewrite `.ndjson`; update index `.ndx` files; return `AffectedRows`
   - **DELETE**: Require `Filter`; read `.ndjson`; apply Filter; if `HardDelete` remove matching lines else set `IsDeleted=1` and refresh `UpdatedAt`; rewrite `.ndjson`; update index `.ndx` files; return `AffectedRows`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection alias not registered |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not defined in `_schema.json` |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | NOT NULL, UNIQUE, or FK constraint violated during INSERT or UPDATE |
| `XBASE_RECORD_FILTER_REQUIRED` | UPDATE or DELETE called without a Filter |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but no such transaction workspace exists |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — to build the `Filter` specification
- `XBase-Query-Sort` — to build the `Sort` specification
- `XBase-Query-Join` — to build the `Join` specification
- `XBase-Query-Aggregate` — to build the `Aggregate` specification
- `XBase-Transaction-Begin` — if using a transaction
