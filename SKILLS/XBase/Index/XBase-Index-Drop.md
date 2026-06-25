# XBase-Index-Drop

Drop a named index from the database.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `IndexName` | string | yes | — | Name of the index to drop |
| `IfExists` | bool | no | `true` | Use `DROP INDEX IF EXISTS` |

## Outputs

```json
{
  "Success": true,
  "IndexName": "<name>",
  "DroppedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`
2. Execute `DROP INDEX [IF EXISTS] <IndexName>`
3. Return `DroppedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_INDEX_NOT_FOUND` | Index does not exist and `IfExists` is `false` |

## Dependencies

- `XBase-Database-Connect`
