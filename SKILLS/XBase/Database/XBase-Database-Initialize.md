# XBase-Database-Initialize

Create a new database directory with metadata and an empty schema.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `DatabaseName` | string | Yes | Name of the directory to create under `{DatabaseRoot}/`. Must not contain `..`, `/`, `\`, or null bytes. |
| `OverwriteIfExists` | bool | No | Delete and recreate the directory if it already exists. Default: `false`. |

## Outputs

```json
{
  "Success": true,
  "DatabasePath": "{DatabaseRoot}/myapp",
  "CreatedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Validate `DatabaseName`: reject if empty or if it contains `..`, `/`, `\`, or null bytes — return `XBASE_DATABASE_PATH_INVALID`.
2. Resolve the target path: `{DatabaseRoot}/{DatabaseName}/`.
3. If the directory already exists and `OverwriteIfExists` is `false`, return `XBASE_DATABASE_EXISTS`.
4. If the directory already exists and `OverwriteIfExists` is `true`, delete it recursively using `delete-directory-recursive(path)`.
5. Create the directory using `create-directory(path)`.
6. Write `_meta.json` using `write-text-file(path, content)`: `{ "XBaseVersion": 1, "Name": "<DatabaseName>", "CreatedAt": "<now>", "UpdatedAt": "<now>" }`.
7. Write `_schema.json` using `write-text-file(path, content)`: `{ "Tables": [], "Indexes": [] }`.
8. Return `DatabasePath` and `CreatedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_DATABASE_PATH_INVALID` | `DatabaseName` contains illegal characters or path traversal sequences. |
| `XBASE_DATABASE_EXISTS` | Directory already exists and `OverwriteIfExists` is `false`. |

## Dependencies

- Writable local file system
