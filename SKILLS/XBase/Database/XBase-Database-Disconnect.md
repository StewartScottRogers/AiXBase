# XBase-Database-Disconnect

Deregister a named connection alias from the session.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | The logical alias registered by `XBase-Database-Connect`. |

## Outputs

```json
{
  "Success": true
}
```

## Steps

1. Validate that `ConnectionName` is registered in the session; if not, return `XBASE_CONNECTION_INVALID`.
2. Deregister `ConnectionName` from the session mapping.
3. Return `Success: true`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
