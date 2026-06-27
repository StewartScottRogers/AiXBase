# Ticketing-User-Authenticate

Verify a username and password, then issue a session token.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Username | string | yes | Login name |
| Password | string | yes | Plaintext password; the skill hashes it internally for comparison; never persisted or returned |

## Outputs

```json
{
  "Success": true,
  "SessionToken": "a3f1c8...64hexchars...b9c2d7",
  "ExpiresAt": "2026-06-28T10:00:00Z",
  "UserId": 3
}
```

## Steps

1. Call XBase-Record-Select on Users filtering by Username.
2. If no matching row is returned, return TICKETING_USER_NOT_FOUND.
3. If the returned user's IsActive = 0, return TICKETING_USER_INACTIVE.
4. Compute a secure one-way hash of the input Password using the same algorithm used in Ticketing-User-Register.
5. Compare the computed hash to the stored CredentialHash; if they do not match, return TICKETING_AUTH_FAILED.
6. Generate a cryptographically random 64-character hexadecimal SessionToken.
7. Set ExpiresAt = now() + 24 hours.
8. Call XBase-Record-Insert on the Sessions table with UserId, SessionToken, CreatedAt = now(), and ExpiresAt.
9. Return SessionToken, ExpiresAt, and UserId.
10. Never include Password or CredentialHash in outputs.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_USER_NOT_FOUND | No user exists with the given Username |
| TICKETING_USER_INACTIVE | User exists but has been deactivated |
| TICKETING_AUTH_FAILED | Credential comparison failed |
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
