# XBase-Query-Join

Build a join specification object combining two tables on a key expression, for use
with `XBase-Record-Select` or `XBase-Query-Execute`. No file I/O occurs — pure
compilation.

Join evaluation in XBase is performed entirely in memory: both tables are read from
their `.dbf` files and matched row-by-row on the specified key expression by the
executing skill.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `JoinType` | string | no | `INNER` | `INNER` or `LEFT` |
| `TargetTable` | string | yes | — | The table to join to the primary table |
| `OnLeft` | string | yes | — | Column reference on the primary table, e.g. `Tickets.StatusId` |
| `OnRight` | string | yes | — | Column reference on the joined table, e.g. `Statuses.Id` |
| `Alias` | string | no | — | Optional prefix for joined table fields in the merged row |

## Outputs

```json
{
  "Success": true,
  "Join": {
    "JoinType":    "INNER",
    "TargetTable": "Statuses",
    "OnLeft":      "Tickets.StatusId",
    "OnRight":     "Statuses.Id",
    "Alias":       null
  }
}
```

## Steps

1. Validate `JoinType` is `INNER` or `LEFT`; return `XBASE_JOIN_TYPE_INVALID` if not
2. Validate `TargetTable` name — alphanumeric + underscore only
3. Validate `OnLeft` and `OnRight` match the pattern `TableName.ColumnName` (both parts alphanumeric + underscore); return `XBASE_JOIN_REFERENCE_INVALID` if malformed
4. Return the compiled join specification object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_JOIN_TYPE_INVALID` | `JoinType` is not `INNER` or `LEFT` |
| `XBASE_JOIN_REFERENCE_INVALID` | `OnLeft` or `OnRight` is malformed |

## Dependencies

None — pure compilation, no file access.
