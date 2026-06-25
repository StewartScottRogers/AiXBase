# XBase-Database-Initialize

Create a new database directory with metadata and an empty schema.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `DatabaseName` | string | yes | — | Name of the directory to create under `AiXBase/` |
| `OverwriteIfExists` | bool | no | `false` | Delete and recreate if the directory already exists |

## Outputs

```json
{
  "Success": true,
  "DatabasePath": "<absolute path to the database directory>",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Resolve `AiXBase/{DatabaseName}/` to an absolute path; reject if the name contains `..`, `/`, `\`, or null bytes — return `XBASE_DATABASE_PATH_INVALID`
2. If the directory already exists and `OverwriteIfExists` is `false`, return `XBASE_DATABASE_EXISTS`
3. If the directory already exists and `OverwriteIfExists` is `true`, delete it recursively
4. `Directory.CreateDirectory(DatabasePath)`
5. Write `_meta.json`: `{ "XBaseVersion": 1, "Name": "<DatabaseName>", "CreatedAt": "<now>", "UpdatedAt": "<now>" }`
6. Write `_schema.json`: `{ "Tables": [], "Indexes": [] }`
7. Return `DatabasePath` and `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DATABASE_EXISTS` | Directory already exists and `OverwriteIfExists` is `false` |
| `XBASE_DATABASE_PATH_INVALID` | Name contains illegal characters or path traversal sequences |

## Dependencies

None — this is a root skill.
