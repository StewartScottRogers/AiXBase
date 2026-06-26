# XBase-Database-Connect

Validate an existing database directory and register a named connection alias for the session.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `DatabaseName` | string | yes | — | Name of the database directory under `XBaseFiles/` |
| `ConnectionName` | string | yes | — | Logical alias used by all subsequent skills to identify this connection |

## Outputs

```json
{
  "Success": true,
  "ConnectionName": "<alias>",
  "IsOpen": true
}
```

## Steps

1. Resolve `XBaseFiles/{DatabaseName}/` to an absolute path
2. Verify the directory exists; if not, return `XBASE_DATABASE_NOT_FOUND`
3. Read `_meta.json`; verify it is valid JSON and contains `XBaseVersion`; if not, return `XBASE_DATABASE_CORRUPT`
4. Read `_schema.json`; verify it is valid JSON with `Tables` and `Indexes` arrays; if not, return `XBASE_DATABASE_CORRUPT`
5. If `ConnectionName` is already registered, return `XBASE_CONNECTION_NAME_IN_USE`
6. Register `ConnectionName → DatabasePath` mapping in the session
7. Return `ConnectionName` and `IsOpen: true`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DATABASE_NOT_FOUND` | The database directory does not exist at the resolved path |
| `XBASE_DATABASE_CORRUPT` | `_meta.json` or `_schema.json` is missing or contains invalid JSON |
| `XBASE_CONNECTION_NAME_IN_USE` | A connection with that alias is already registered |

## Dependencies

- `XBase-Database-Initialize` — must have been called first to create the database directory
