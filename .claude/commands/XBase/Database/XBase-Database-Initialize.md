# XBase-Database-Initialize

Create a new SQLite database file and configure it with standard pragmas.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `DatabasePath` | string | yes | — | Relative path under `data/` for the new `.db` file |
| `OverwriteIfExists` | bool | no | `false` | Delete and recreate if the file already exists |

## Outputs

```json
{
  "Success": true,
  "DatabasePath": "<absolute path>",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Resolve `DatabasePath` against the project `data/` directory to an absolute path
2. If the file already exists and `OverwriteIfExists` is `false`, return `XBASE_DATABASE_EXISTS`
3. If the file already exists and `OverwriteIfExists` is `true`, delete it
4. Create the SQLite file at the resolved path
5. Execute `PRAGMA journal_mode=WAL;`
6. Execute `PRAGMA foreign_keys=ON;`
7. Return `DatabasePath` (absolute) and `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DATABASE_EXISTS` | File already exists and `OverwriteIfExists` is `false` |
| `XBASE_DATABASE_PATH_INVALID` | Path escapes `data/` or contains illegal characters |

## Dependencies

None — this is a root skill.
