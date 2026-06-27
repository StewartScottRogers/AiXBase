# Ticketing-User-Deactivate

Mark a user as inactive. Deactivated users cannot be assigned tickets or post comments.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| UserId | int | yes | User to deactivate |
| DeactivatedByUserId | int | yes | ID of the user performing the deactivation |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "DeactivatedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Call XBase-Record-Select on Users filtered by UserId; if no row is found, return TICKETING_USER_NOT_FOUND.
2. If the user's IsActive is already 0, return TICKETING_USER_NOT_FOUND.
3. Call XBase-Record-Update on Users where Id = UserId, setting IsActive = 0 and recording the DeactivatedAt timestamp.
4. Return UserId and DeactivatedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_USER_NOT_FOUND | User does not exist or is already inactive |
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Record-Select
- XBase-Record-Update
