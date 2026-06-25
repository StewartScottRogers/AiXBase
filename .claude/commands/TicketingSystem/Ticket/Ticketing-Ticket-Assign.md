# Ticketing-Ticket-Assign

Assign or reassign the owner of a ticket and emit an alert notification.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to assign |
| `AssignedToUserId` | int | yes | — | User to assign the ticket to |
| `AssignedByUserId` | int | yes | — | User making the assignment |
| `Comment` | string | no | — | Optional note recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "AssignedToUserId": 7,
  "AssignedAt": "<ISO-8601>"
}
```

## Steps

1. Validate ticket exists and `IsDeleted = 0`
2. Validate `AssignedToUserId` exists and `IsActive = 1`
3. `XBase-Transaction-Begin`
4. `XBase-Record-Update` → `Tickets` set `AssignedToUserId`
5. `XBase-Record-Insert` → `TicketHistory` (action: `Assigned`, `FromValue`: previous assignee, `ToValue`: new assignee display name)
6. `XBase-Transaction-Commit`
7. `Ticketing-Display-Alert` (event: `TICKET ASSIGNED`, detail: new assignee display name)
8. Return `AssignedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_USER_NOT_FOUND` | Assignee user does not exist |
| `TICKETING_USER_INACTIVE` | Assignee is deactivated |

## Dependencies

- `XBase-Transaction-Begin/Commit`
- `XBase-Record-Update`
- `XBase-Record-Insert`
- `Ticketing-Display-Alert`
