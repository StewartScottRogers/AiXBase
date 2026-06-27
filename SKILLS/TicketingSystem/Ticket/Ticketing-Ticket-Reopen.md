# Ticketing-Ticket-Reopen

Transition a closed ticket back to the `Open` status.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Ticket to reopen |
| `ReopenedByUserId` | int | yes | User requesting the reopen |
| `Comment` | string | no | Reason for reopening, recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "ReopenedAt": "<ISO-8601>"
}
```

## Steps

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`; if no row is returned or `IsDeleted = 1`, return `TICKETING_TICKET_NOT_FOUND`; if the ticket's current status is not terminal, return `TICKETING_TICKET_NOT_CLOSED`
2. Call `XBase-Record-Select` on the `Statuses` table with filter `Name = 'Open'`; capture the returned `Id` as the target `StatusId`
3. Call `Ticketing-Status-Transition` with `TicketId`, `ToStatusId`, and `ChangedByUserId = ReopenedByUserId`
4. Call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId` setting `ClosedAt = NULL` and `UpdatedAt = now()`
5. Call `XBase-Record-Insert` on the `TicketHistory` table with `TicketId`, `ChangedByUserId = ReopenedByUserId`, `Action = 'Reopened'`, `ChangedAt = now()`
6. If `Comment` is provided, call `Ticketing-Comment-Add` with `TicketId`, `AuthorUserId = ReopenedByUserId`, and the comment body
7. Return `TicketId` and `ReopenedAt` (the timestamp from step 4)

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is soft-deleted |
| `TICKETING_TICKET_NOT_CLOSED` | Ticket is not in a terminal status |
| `TICKETING_STATUS_TRANSITION_INVALID` | No allowed transition from current status to Open |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Update`
- `XBase-Record-Insert`
- `Ticketing-Status-Transition`
- `Ticketing-Comment-Add`
