# Ticketing-User-Read

Fetch a user profile by ID or username.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| UserId | int | no | Numeric user ID; provide UserId or Username |
| Username | string | no | Login name; provide UserId or Username |

## Outputs

```json
{
  "Success": true,
  "User": {
    "UserId": 3,
    "Username": "alice",
    "DisplayName": "Alice Smith",
    "Email": "alice@example.com",
    "IsActive": 1,
    "CreatedAt": "2026-06-27T10:00:00Z"
  }
}
```

CredentialHash is never returned.

## Steps

1. Require at least one of UserId or Username; if neither is provided, return TICKETING_USER_IDENTIFIER_REQUIRED.
2. Call XBase-Record-Select on the Users table filtered by UserId or Username.
3. If no matching row is returned, return TICKETING_USER_NOT_FOUND.
4. Return the User object containing all columns except CredentialHash.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_USER_NOT_FOUND | No user matches the given ID or username |
| TICKETING_USER_IDENTIFIER_REQUIRED | Neither UserId nor Username was provided |
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Record-Select
- XBase-Query-Filter
