# XBase-Index-Drop

Delete a named `.ndx` index file and remove its definition from `_schema.json`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `IndexName` | string | yes | — | Name of the index to drop |
| `IfExists` | bool | no | `true` | Succeed silently if the index does not exist |

## Outputs

```json
{
  "Success": true,
  "IndexName": "<name>",
  "DroppedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. `File.ReadAllText(_schema.json)`; parse JSON; find the index entry where `Name == IndexName`:
   - If not found and `IfExists` is `true`: return `Success: true` immediately
   - If not found and `IfExists` is `false`: return `XBASE_INDEX_NOT_FOUND`
3. Identify `TableName` from the index entry; resolve `{TableName}.{IndexName}.ndx`
4. `File.Delete({TableName}.{IndexName}.ndx)` if the file exists
5. Remove the index entry from `_schema.json Indexes`
6. `File.WriteAllText(_schema.json, updatedSchema)`
7. Return `DroppedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_INDEX_NOT_FOUND` | Index does not exist and `IfExists` is `false` |

## Dependencies

- `XBase-Database-Connect`
