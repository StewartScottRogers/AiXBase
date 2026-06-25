# Ticketing-User-Read

Fetch a user profile by ID or username.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `UserId` | int | no | — | Numeric user ID; provide `UserId` or `Username` |
| `Username` | string | no | — | Login name |

## Outputs

```json
{
  "Success": true,
  "User": {
    "UserId": 3,
    "Username": "alice",
    "DisplayName": "Alice Smith",
    "Email": "alice@example.com",
    "IsActive": true,
    "CreatedAt": "..."
  }
}
```

`CredentialHash` is never returned.

## Steps

1. Build filter by `UserId` or `Username`
2. `XBase-Record-Select` → `Users`, project all columns except `CredentialHash`
3. Return `User` object

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_USER_NOT_FOUND` | No user matches the given ID or username |

## Dependencies

- `XBase-Record-Select`
- `XBase-Query-Filter`
