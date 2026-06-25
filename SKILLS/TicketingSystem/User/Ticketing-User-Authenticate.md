# Ticketing-User-Authenticate

Verify a username and credential hash and issue a session token.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Username` | string | yes | — | Login name |
| `CredentialHash` | string | yes | — | Pre-hashed credential; never accept plaintext |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "SessionToken": "<64-char hex>",
  "ExpiresAt": "<ISO-8601>"
}
```

## Steps

1. `XBase-Record-Select` → `Users` where `Username` matches and `IsActive = 1`
2. If no row found, return `TICKETING_AUTH_FAILED` (do not distinguish user-not-found from wrong credential)
3. Compare `CredentialHash` to the stored hash; if mismatch, return `TICKETING_AUTH_FAILED`
4. Generate a 64-character cryptographically random hex token
5. `XBase-Record-Insert` → `Sessions` (`UserId`, `Token`, `ExpiresAt`: now + 8 hours)
6. Return `UserId`, `SessionToken`, `ExpiresAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_AUTH_FAILED` | Username not found, user inactive, or credential mismatch (deliberately generic) |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Insert`
- `XBase-Query-Filter`
