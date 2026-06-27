# Ticketing-User-Register

Create a user account in the ticketing store.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Username | string | yes | Unique login name |
| DisplayName | string | no | Human-readable name shown in the UI |
| Email | string | no | Email address |
| Password | string | yes | Plaintext password; the skill hashes it internally before storing; never persisted or returned |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "Username": "alice",
  "CreatedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Call XBase-Record-Select on the Users table filtering by Username to verify uniqueness; if a matching row exists, return TICKETING_USER_USERNAME_DUPLICATE.
2. Compute a secure one-way hash of Password; do not store the plaintext value.
3. Call XBase-Record-Insert on Users with Username, DisplayName, Email, CredentialHash (from step 2), IsActive = 1, and CreatedAt = now().
4. Return UserId, Username, and CreatedAt.
5. Never include Password or CredentialHash in outputs.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_USER_USERNAME_DUPLICATE | Username is already registered |
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
