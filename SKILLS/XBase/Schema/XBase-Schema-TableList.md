# XBase-Schema-TableList

Return all user-defined table names from `_schema.json`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | Open connection alias. |

## Outputs

```json
{
  "Success": true,
  "Tables": ["Tickets", "Users", "Statuses"],
  "Count": 3
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` using `read-text-file(path)`.
3. Extract the `Name` field from each entry in the `Tables` array.
4. Return `Tables` (array of name strings) and `Count`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
