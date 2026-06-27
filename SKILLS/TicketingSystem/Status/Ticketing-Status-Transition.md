# Ticketing-Status-Transition

Move a ticket from one status to another, validating allowed transitions. Fires Ticketing-Display-Complete when the destination status is terminal.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to transition |
| ToStatusId | int | yes | Target status |
| ChangedByUserId | int | yes | User making the change |
| Comment | string | no | Optional note to append as a comment |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "FromStatus": "In Progress",
  "ToStatus": "Closed",
  "TransitionedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Tickets where Id = TicketId and IsDeleted = 0 to fetch the current StatusId; if no row found, return TICKETING_TICKET_NOT_FOUND.
2. Call XBase-Record-Select on StatusTransitions where FromStatusId = current StatusId and ToStatusId = ToStatusId; if no matching row found, return TICKETING_STATUS_TRANSITION_INVALID.
3. Call XBase-Transaction-Begin.
4. Call XBase-Record-Update on Tickets setting StatusId = ToStatusId, UpdatedAt = now() where Id = TicketId.
5. Call XBase-Record-Insert on TicketHistory with TicketId, ChangedByUserId, Action = StatusChanged, FromValue = old status Name, ToValue = new status Name, ChangedAt = now().
6. If Comment is provided: call Ticketing-Comment-Add with TicketId, AuthorUserId = ChangedByUserId, Body = Comment.
7. Call XBase-Transaction-Commit.
8. Call XBase-Record-Select on Statuses where Id = ToStatusId; if IsTerminal = 1, call Ticketing-Display-Complete.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | Ticket does not exist or is soft-deleted |
| TICKETING_STATUS_NOT_FOUND | ToStatusId does not exist |
| TICKETING_STATUS_TRANSITION_INVALID | No allowed transition from the current status to ToStatusId |

## Dependencies

- XBase-Record-Select
- XBase-Record-Update
- XBase-Record-Insert
- XBase-Transaction-Begin
- XBase-Transaction-Commit
- Ticketing-Comment-Add
- Ticketing-Display-Complete
