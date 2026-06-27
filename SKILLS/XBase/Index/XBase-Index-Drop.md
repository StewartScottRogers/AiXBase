# XBase-Index-Drop

Delete a named `.ndx` index file and remove its definition from `_schema.json`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Open connection alias |
| `TableName` | string | yes | Table that owns the index |
| `IndexName` | string | yes | Name of the index to drop |
| `IfExists` | bool | no (default `true`) | Succeed silently if the index does not exist |

## Outputs

```json
{
  "Success": true,
  "IndexName": "<name>",
  "DroppedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` from the database directory using `read-text-file(path)`. Search the `Indexes` array for an entry where `Name` equals `IndexName` and `TableName` matches the input:
   - If not found and `IfExists` is `true`: return `Success: true` immediately (no-op).
   - If not found and `IfExists` is `false`: return `XBASE_INDEX_NOT_FOUND`.
3. Delete the file `{TableName}.{IndexName}.ndx` from the database directory if it exists.
4. Remove the matching index entry from the `Indexes` array in `_schema.json`.
5. Write the updated `_schema.json` back to the database directory using `write-text-file(path, content)`.
6. Return `IndexName` and `DroppedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `XBASE_INDEX_NOT_FOUND` | Index does not exist and `IfExists` is `false` |

## Dependencies

- `XBase-Database-Connect`
