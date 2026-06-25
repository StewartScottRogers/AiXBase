# XBase-Query-Join

Build a JOIN clause combining two tables on a key expression, for use with `XBase-Record-Select`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `JoinType` | string | no | `INNER` | `INNER`, `LEFT`, `RIGHT`, or `FULL` |
| `TargetTable` | string | yes | — | The table to join to the primary table |
| `OnLeft` | string | yes | — | Column reference on the primary table, e.g. `Tickets.StatusId` |
| `OnRight` | string | yes | — | Column reference on the joined table, e.g. `Statuses.Id` |
| `Alias` | string | no | — | Optional alias for the joined table |

## Outputs

```json
{
  "Success": true,
  "Join": {
    "sql": "INNER JOIN Statuses ON Tickets.StatusId = Statuses.Id"
  }
}
```

## Steps

1. Validate `JoinType`, `TargetTable`, `OnLeft`, and `OnRight`
2. Build the `<JoinType> JOIN <TargetTable> [AS <Alias>] ON <OnLeft> = <OnRight>` fragment
3. Return the compiled join object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_JOIN_TYPE_INVALID` | `JoinType` is not one of the allowed values |
| `XBASE_JOIN_REFERENCE_INVALID` | `OnLeft` or `OnRight` is malformed |

## Dependencies

None — pure compilation, no database access.
