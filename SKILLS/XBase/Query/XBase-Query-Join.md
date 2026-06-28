# XBase-Query-Join

Compile and return a join specification object combining two tables on a key expression, for use with `XBase-Record-Select` or `XBase-Query-Execute`. No file I/O occurs — pure compilation step. Join evaluation is performed entirely in memory by the executing skill, which reads both tables' `.dbf` files and matches records row-by-row.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `JoinType` | string | no | `INNER` or `LEFT` (default `INNER`) |
| `TableName` | string | yes | The right-hand table to join |
| `OnLeft` | string | yes | Column reference on the primary table, e.g. `Tickets.StatusId` |
| `OnRight` | string | yes | Column reference on the joined table, e.g. `Statuses.Id` |
| `Joins` | array | no | Array of additional join specification objects for chaining multiple joins |

## Outputs

```json
{
  "Success": true,
  "Join": {
    "JoinType":  "INNER",
    "TableName": "Statuses",
    "OnLeft":    "Tickets.StatusId",
    "OnRight":   "Statuses.Id"
  }
}
```

## Steps

1. Validate `JoinType` is `INNER` or `LEFT`; return `XBASE_JOIN_TYPE_INVALID` if present but neither; default to `INNER` if omitted.
2. Validate `TableName` is a safe identifier: letters, numbers, and underscores only (`^[A-Za-z0-9_]+$`); return `XBASE_JOIN_TABLE_INVALID` if it contains any other character.
3. Validate `OnLeft` and `OnRight` each match the pattern `Table.Column` where both the table part and the column part contain only letters, numbers, and underscores; return `XBASE_JOIN_REFERENCE_INVALID` if either is malformed or missing either part.
4. If `Joins` is provided, validate each entry in the array by applying steps 1–3.
5. Return the compiled join specification object.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_JOIN_TYPE_INVALID` | `JoinType` is not `INNER` or `LEFT` |
| `XBASE_JOIN_TABLE_INVALID` | `TableName` contains characters outside letters, numbers, and underscores |
| `XBASE_JOIN_REFERENCE_INVALID` | `OnLeft` or `OnRight` does not match the `Table.Column` pattern with safe identifier parts |

## Dependencies

- None — pure compilation step with no file access.
