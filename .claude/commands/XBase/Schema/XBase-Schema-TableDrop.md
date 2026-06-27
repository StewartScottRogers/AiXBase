# XBase-Schema-TableDrop

Remove a table from `_schema.json` and delete its `.dbf` data file and all associated
`.ndx` index files.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to drop |
| `ConfirmDrop` | bool | yes | — | Must be `true`; guards against accidental data loss |
| `IfExists` | bool | no | `true` | Succeed silently when the table does not exist |

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
2. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
3. `File.ReadAllText(_schema.json)`; parse JSON
4. Locate the table entry where `Name == TableName`:
   - If not found and `IfExists` is `true`: return `Success: true` immediately
   - If not found and `IfExists` is `false`: return `XBASE_SCHEMA_TABLE_NOT_FOUND`
5. Remove the table entry from the `Tables` array
6. Remove all index entries from the `Indexes` array where `TableName` matches
7. `File.WriteAllText(_schema.json, updatedSchema)`
8. `File.Delete({TableName}.dbf)` if the file exists
9. For each `{TableName}.*.ndx` file in the database directory: `File.Delete(path)`
10. Return `DroppedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DROP_NOT_CONFIRMED` | `ConfirmDrop` was not `true` |
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist and `IfExists` is `false` |

## Dependencies

- `XBase-Database-Connect`
