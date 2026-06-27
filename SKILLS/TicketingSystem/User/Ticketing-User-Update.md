# Ticketing-User-Update

Modify a user's display name or email address.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| UserId | int | yes | User to update |
| DisplayName | string | no | New display name |
| Email | string | no | New email address |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "UpdatedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Call XBase-Record-Select on Users filtered by UserId; if no row is found, return TICKETING_USER_NOT_FOUND.
2. Build the update values from the supplied inputs, including only the fields that were provided.
3. Call XBase-Record-Update on Users where Id = UserId, setting the supplied fields and UpdatedAt = now().
4. Return UserId and UpdatedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_USER_NOT_FOUND | User does not exist |
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Record-Select
- XBase-Record-Update
