# XBase-Schema-TableDrop

Remove a table and all its data from the database.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to drop |
| `ConfirmDrop` | bool | yes | — | Must be `true`; guards against accidental data loss |
| `IfExists` | bool | no | `true` | Use `DROP TABLE IF EXISTS` |

## Outputs

```json
{
  "Success": true,
  "TableName": "<name>",
  "DroppedAt": "<ISO-8601>"
}
```

## Steps

1. If `ConfirmDrop` is not `true`, return `XBASE_DROP_NOT_CONFIRMED`
2. Validate `ConnectionName`
3. Execute `DROP TABLE [IF EXISTS] <TableName>`
4. Return `DroppedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DROP_NOT_CONFIRMED` | `ConfirmDrop` was not `true` |
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist and `IfExists` is `false` |

## Dependencies

- `XBase-Database-Connect`
