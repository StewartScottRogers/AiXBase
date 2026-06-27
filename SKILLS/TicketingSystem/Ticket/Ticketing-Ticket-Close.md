# Ticketing-Ticket-Close

Transition a ticket to the terminal `Closed` status and emit a completion notification.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Ticket to close |
| `ClosedByUserId` | int | yes | User closing the ticket |
| `Comment` | string | no | Closing note appended to history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "TicketNumber": "TKT-0042",
  "ClosedAt": "<ISO-8601>"
}
```

## Steps

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`; if no row is returned or `IsDeleted = 1`, return `TICKETING_TICKET_NOT_FOUND`; if the ticket's current status is already terminal, return `TICKETING_TICKET_ALREADY_CLOSED`
2. Call `XBase-Record-Select` on the `Statuses` table with filters `IsTerminal = 1` and `Name = 'Closed'`; capture the returned `Id` as the target `StatusId`
3. Call `Ticketing-Status-Transition` with `TicketId`, `ToStatusId`, `ChangedByUserId = ClosedByUserId`, and `Comment`
4. Call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId` setting `ClosedAt = now()` and `UpdatedAt = now()`
5. If `Comment` is provided, call `Ticketing-Comment-Add` with `TicketId`, `AuthorUserId = ClosedByUserId`, and the comment body
6. Call `Ticketing-Display-Complete` with `TicketNumber`, `Summary`, `ClosedByDisplayName`, and `ClosedAt`
7. Return `TicketId`, `TicketNumber`, `ClosedAt`

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is soft-deleted |
| `TICKETING_TICKET_ALREADY_CLOSED` | Ticket is already in a terminal status |
| `TICKETING_STATUS_TRANSITION_INVALID` | No allowed transition from current status to Closed |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Update`
- `Ticketing-Status-Transition`
- `Ticketing-Comment-Add`
- `Ticketing-Display-Complete`
