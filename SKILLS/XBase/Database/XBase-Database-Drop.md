# XBase-Database-Drop

Close all connections to a database and permanently delete the file.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `DatabasePath` | string | yes | — | Path to the `.db` file to delete |
| `ConfirmDrop` | bool | yes | — | Must be `true`; acts as an explicit acknowledgment of data loss |

## Outputs

```json
{
  "Success": true,
  "DatabasePath": "<absolute path>",
  "DroppedAt": "<ISO-8601>"
}
```

## Steps

1. If `ConfirmDrop` is not `true`, return `XBASE_DROP_NOT_CONFIRMED`
2. Resolve `DatabasePath` to absolute path
3. Close and deregister any open connections to this file (issuing `ROLLBACK` on any open transactions)
4. Delete the `.db` file, `.db-shm`, and `.db-wal` sidecar files if present
5. Return `DroppedAt`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_DROP_NOT_CONFIRMED` | `ConfirmDrop` was not `true` |
| `XBASE_DATABASE_NOT_FOUND` | File does not exist at the resolved path |

## Dependencies

- `XBase-Database-Connect` — any open connections are closed automatically before the drop
