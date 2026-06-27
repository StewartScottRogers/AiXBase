# Ticketing-Ticket-Escalate

Raise a ticket's priority and emit an escalation notification.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Ticket to escalate |
| `EscalatedByUserId` | int | yes | User requesting escalation |
| `NewPriorityId` | int | yes | FK to the target priority; must have a lower `Weight` value (higher urgency) than the current priority |
| `Comment` | string | no | Reason for escalation, recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "PreviousPriority": "Medium",
  "NewPriority": "High",
  "EscalatedAt": "<ISO-8601>"
}
```

## Steps

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`; if no row is returned or `IsDeleted = 1`, return `TICKETING_TICKET_NOT_FOUND`; capture the current `PriorityId`
2. Call `XBase-Record-Select` on the `Priorities` table with filter `Id = current PriorityId`; capture the `Weight` and `Name` as `PreviousPriorityName`
3. Call `XBase-Record-Select` on the `Priorities` table with filter `Id = NewPriorityId`; capture the `Weight` and `Name` as `NewPriorityName`; confirm that `NewPriority.Weight` is lower than the current priority's `Weight` (lower Weight = higher urgency)
4. Call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId` setting `PriorityId = NewPriorityId` and `UpdatedAt = now()`
5. Call `XBase-Record-Insert` on the `TicketHistory` table with `TicketId`, `ChangedByUserId = EscalatedByUserId`, `Action = 'Escalated'`, `FromValue = PreviousPriorityName`, `ToValue = NewPriorityName`, `ChangedAt = now()`
6. If `Comment` is provided, call `Ticketing-Comment-Add` with `TicketId`, `AuthorUserId = EscalatedByUserId`, and the comment body
7. Call `Ticketing-Display-Alert` with `Event = 'TICKET ESCALATED'`, `TicketNumber`, and `Detail = NewPriorityName`
8. Return `TicketId`, `PreviousPriority`, `NewPriority`, `EscalatedAt`

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is soft-deleted |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Update`
- `XBase-Record-Insert`
- `Ticketing-Comment-Add`
- `Ticketing-Display-Alert`
