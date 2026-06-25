# Ticketing-User-Register

Create a user account in the ticketing store.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Username` | string | yes | — | Unique login name (alphanumeric + underscore, 3–50 chars) |
| `DisplayName` | string | yes | — | Human-readable name shown in the UI |
| `Email` | string | yes | — | Email address |
| `CredentialHash` | string | yes | — | Pre-hashed credential; never accept plaintext |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "Username": "alice",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `Username` format
2. Check for an existing user with that `Username`; if found, return `TICKETING_USER_USERNAME_DUPLICATE`
3. `XBase-Record-Insert` → `Users` with `IsActive = 1`
4. Return `UserId`, `Username`, `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_USER_USERNAME_DUPLICATE` | Username is already registered |
| `TICKETING_USER_USERNAME_INVALID` | Username format does not meet requirements |

## Dependencies

- `XBase-Record-Insert`
- `XBase-Record-Select`
