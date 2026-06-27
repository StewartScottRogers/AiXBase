# Ticketing-Ticket-Assign

Assign or reassign the owner of a ticket and emit an assignment notification.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Ticket to assign |
| `AssignToUserId` | int | yes | User to assign the ticket to |
| `AssignedByUserId` | int | yes | User making the assignment |

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

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`; if no row is returned or `IsDeleted = 1`, return `TICKETING_TICKET_NOT_FOUND`; capture the current `AssignedToUserId` for use as `FromValue` in the history row
2. Call `XBase-Record-Select` on the `Users` table with filter `Id = AssignToUserId`; if no row is returned, return `TICKETING_USER_NOT_FOUND`; if `IsActive = 0`, return `TICKETING_USER_INACTIVE`; capture the user's `DisplayName`
3. Call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId` setting `AssignedToUserId = AssignToUserId` and `UpdatedAt = now()`
4. Call `XBase-Record-Insert` on the `TicketHistory` table with `TicketId`, `ChangedByUserId = AssignedByUserId`, `Action = 'Assigned'`, `FromValue = previous AssignedToUserId`, `ToValue = AssignToUserId`, `ChangedAt = now()`
5. Call `Ticketing-Display-Alert` with `Event = 'TICKET ASSIGNED'`, `TicketNumber`, and `Detail` set to the display name of the newly assigned user
6. Return `TicketId`, `AssignedToUserId = AssignToUserId`, `AssignedAt`

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is soft-deleted |
| `TICKETING_USER_NOT_FOUND` | `AssignToUserId` does not exist |
| `TICKETING_USER_INACTIVE` | `AssignToUserId` is deactivated |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Update`
- `XBase-Record-Insert`
- `Ticketing-Display-Alert`
