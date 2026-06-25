# XBase-Record-Select

Retrieve rows from a table with optional column projection, filtering, sorting, and pagination.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Source table |
| `Columns` | array | no | `["*"]` | Column names to return |
| `Filter` | object | no | — | Compiled filter from `XBase-Query-Filter` |
| `Sort` | object | no | — | Compiled sort from `XBase-Query-Sort` |
| `Limit` | int | no | — | Maximum rows to return |
| `Offset` | int | no | `0` | Rows to skip before returning results |
| `IncludeDeleted` | bool | no | `false` | If `false`, appends `AND IsDeleted = 0` automatically |

## Outputs

```json
{
  "Success": true,
  "Rows": [ { "Id": 1, "Summary": "..." } ],
  "TotalCount": 57
}
```

`TotalCount` is the count without `LIMIT`/`OFFSET` (requires a second `COUNT(*)` query).

## Steps

1. Validate `ConnectionName` and `TableName`
2. Build `SELECT <columns> FROM <TableName>`
3. Append `WHERE` clause from `Filter` (plus `AND IsDeleted = 0` unless `IncludeDeleted`)
4. Append `ORDER BY` from `Sort`
5. Append `LIMIT` / `OFFSET`
6. Execute data query and count query in parallel
7. Return `Rows` and `TotalCount`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_SCHEMA_COLUMN_MISSING` | A requested column does not exist |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — optional
- `XBase-Query-Sort` — optional
