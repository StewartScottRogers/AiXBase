# Ticketing-Comment-Add

Append a comment to a ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to comment on |
| `AuthorUserId` | int | yes | — | User posting the comment |
| `Body` | string | yes | — | Comment text |

## Outputs

```json
{
  "Success": true,
  "CommentId": 17,
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `TicketId` exists and `IsDeleted = 0`
2. Validate `AuthorUserId` exists and `IsActive = 1`
3. `XBase-Record-Insert` → `Comments`
4. Return `CommentId` and `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_USER_NOT_FOUND` | Author user does not exist |

## Dependencies

- `XBase-Record-Insert`
