# XBase-Query-Aggregate

Compute aggregate functions (COUNT, SUM, AVG, MIN, MAX) over a table or result set.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Source table |
| `Aggregates` | array | yes | — | Array of aggregate definitions (see below) |
| `Filter` | object | no | — | Compiled filter from `XBase-Query-Filter` |
| `GroupBy` | array | no | `[]` | Column names to group by |

### Aggregate Definition Object

| Field | Type | Required | Description |
|---|---|---|---|
| `Function` | string | yes | `COUNT`, `SUM`, `AVG`, `MIN`, or `MAX` |
| `Column` | string | yes | Column to aggregate (`*` allowed for `COUNT`) |
| `Alias` | string | no | Output field name in the result |

## Outputs

```json
{
  "Success": true,
  "Results": [
    { "StatusName": "Open", "TicketCount": 14 },
    { "StatusName": "Closed", "TicketCount": 52 }
  ]
}
```

## Steps

1. Validate `ConnectionName` and `TableName`
2. Build `SELECT <aggregates> FROM <TableName> [WHERE <filter>] [GROUP BY <columns>]`
3. Execute the query
4. Return `Results` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_AGGREGATE_FUNCTION_UNKNOWN` | Function not in allowed set |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — optional
