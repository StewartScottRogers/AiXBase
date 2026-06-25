# XBase-Database-Connect

Open an existing SQLite database file and register a named connection handle for the session.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `DatabasePath` | string | yes | — | Path to the `.db` file (absolute or relative to `AiXBase/`) |
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

1. Resolve `DatabasePath` to absolute path
2. Verify the file exists; if not, return `XBASE_DATABASE_NOT_FOUND`
3. Open the SQLite file in read-write mode
4. Register the open connection under `ConnectionName` for the session lifetime
5. Return `ConnectionName` and `IsOpen: true`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DATABASE_NOT_FOUND` | The `.db` file does not exist at the resolved path |
| `XBASE_CONNECTION_NAME_IN_USE` | A connection with that name is already open |

## Dependencies

- `XBase-Database-Initialize` — must have been called first to create the file
