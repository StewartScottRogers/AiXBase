# XBase-Schema-TableDrop

Remove a table from `_schema.json` and delete its `.dbf` data file and all associated `.ndx` index files.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | Open connection alias. |
| `TableName` | string | Yes | Name of the table to drop. |
| `IfExists` | bool | No | Succeed silently when the table does not exist. Default: `true`. |

## Outputs

```json
{
  "Success": true
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` using `read-text-file(path)`.
3. Locate the table entry where `Name` matches `TableName`:
   a. If not found and `IfExists` is `true`, return `Success: true` (no-op).
   b. If not found and `IfExists` is `false`, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. Remove the table entry from the `Tables` array.
5. Remove all index entries from the `Indexes` array where `TableName` matches.
6. Write updated `_schema.json` using `write-text-file(path, content)`.
7. If `{TableName}.dbf` exists, delete it using `delete-file(path)`.
8. For each file matching `{TableName}.*.ndx` in the database directory (discovered using `list-files(path, pattern)`), delete it using `delete-file(path)`.
9. Return `Success: true`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist and `IfExists` is `false`. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
