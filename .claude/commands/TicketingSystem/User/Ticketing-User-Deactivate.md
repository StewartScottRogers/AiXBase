# Ticketing-User-Deactivate

Mark a user as inactive. Deactivated users cannot be assigned tickets or post comments.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `UserId` | int | yes | — | User to deactivate |
| `DeactivatedByUserId` | int | yes | — | Admin user making the request |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "DeactivatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `UserId` exists; if not, return `TICKETING_USER_NOT_FOUND`
2. Validate `DeactivatedByUserId` has admin role; if not, return `TICKETING_USER_DEACTIVATION_FORBIDDEN`
3. If the user's `IsActive` is already `0`, return `TICKETING_USER_NOT_FOUND` (deactivated users are treated as not found)
4. `XBase-Record-Update` → `Users` set `IsActive = 0`
5. Return `DeactivatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_USER_NOT_FOUND` | User does not exist or is already inactive |
| `TICKETING_USER_DEACTIVATION_FORBIDDEN` | Requester does not have admin role |

## Dependencies

- `XBase-Record-Update`
- `XBase-Query-Filter`
