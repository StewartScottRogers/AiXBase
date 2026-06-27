# Ticketing-Comment-Add

Append a comment to a ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to comment on |
| AuthorUserId | int | yes | User posting the comment |
| Body | string | yes | Comment text (NOT NULL) |

## Outputs

```json
{
  "Success": true,
  "CommentId": 17,
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Tickets where Id = TicketId and IsDeleted = 0; if no row found, return TICKETING_TICKET_NOT_FOUND.
2. Call XBase-Record-Select on Users where Id = AuthorUserId; if no row found, return TICKETING_USER_NOT_FOUND; if row found but IsActive = 0, return TICKETING_USER_INACTIVE.
3. Call XBase-Record-Insert on Comments with TicketId, AuthorUserId, Body, CreatedAt = now(), UpdatedAt = now(), IsDeleted = 0.
4. Call XBase-Record-Update on Tickets setting UpdatedAt = now() where Id = TicketId.
5. Call XBase-Record-Insert on TicketHistory with TicketId, ChangedByUserId = AuthorUserId, Action = CommentAdded, ChangedAt = now().
6. Return CommentId and CreatedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | Ticket does not exist or is soft-deleted |
| TICKETING_USER_NOT_FOUND | AuthorUserId does not exist |
| TICKETING_USER_INACTIVE | Author user is deactivated |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
- XBase-Record-Update
