# XBase-Database-Drop

Delete a database directory and all its contents permanently.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | Open connection alias identifying the database to drop. |
| `ConfirmDrop` | bool | Yes | Must be `true`; guards against accidental data loss. |

## Outputs

```json
{
  "Success": true,
  "DroppedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Validate that `ConnectionName` is registered in the session; if not, return `XBASE_CONNECTION_INVALID`.
2. Verify `ConfirmDrop` is `true`; if not, return `XBASE_DROP_NOT_CONFIRMED`.
3. Resolve the database directory path from the `ConnectionName` session mapping.
4. Deregister all session connections whose `DatabasePath` matches this directory.
5. Delete the database directory and all its contents using `delete-directory-recursive(path)`.
6. Return `DroppedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |
| `XBASE_DROP_NOT_CONFIRMED` | `ConfirmDrop` was not `true`. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
