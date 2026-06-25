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

1. Validate `UserId` exists and `IsActive = 1`
2. Validate `DeactivatedByUserId` has admin role
3. `XBase-Record-Update` → `Users` set `IsActive = 0`
4. Return `DeactivatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_USER_NOT_FOUND` | User does not exist |
| `TICKETING_USER_ALREADY_INACTIVE` | User is already deactivated |
| `TICKETING_PERMISSION_DENIED` | Requester does not have admin role |

## Dependencies

- `XBase-Record-Update`
- `XBase-Query-Filter`
