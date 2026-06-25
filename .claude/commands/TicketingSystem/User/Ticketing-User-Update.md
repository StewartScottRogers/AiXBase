# Ticketing-User-Update

Modify a user's display name or email address.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `UserId` | int | yes | — | User to update |
| `DisplayName` | string | no | — | New display name |
| `Email` | string | no | — | New email address |

## Outputs

```json
{
  "Success": true,
  "UserId": 3,
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `UserId` exists
2. Build `Values` from non-null inputs only
3. `XBase-Record-Update` → `Users` where `Id = UserId`
4. Return `UpdatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_USER_NOT_FOUND` | User does not exist |

## Dependencies

- `XBase-Record-Update`
- `XBase-Query-Filter`
