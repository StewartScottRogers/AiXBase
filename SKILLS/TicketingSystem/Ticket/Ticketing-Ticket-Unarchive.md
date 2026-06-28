# Ticketing-Ticket-Unarchive

Restore a single archived ticket to active status by clearing its `IsArchived` flag. The ticket remains in its current terminal status — unarchiving does not reopen the ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active XBase connection alias for the ticketing database |
| `SessionToken` | string | yes | Active session token |
| `TicketId` | int | yes | ID of the archived ticket to restore |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "TicketNumber": "TKT-0042",
  "UnarchivedAt": "2026-06-28T20:00:00Z"
}
```

## Steps

1. Validate `ConnectionName` is registered. If not, return `XBASE_CONNECTION_INVALID`.
2. Call `XBase-Record-Select` on `Tickets` where `Id = TicketId` and `IsDeleted = 0`. If no row is found, return `TICKETING_TICKET_NOT_FOUND`.
3. If the ticket's `IsArchived` value is already `0`, return `TICKETING_TICKET_NOT_ARCHIVED`.
4. Call `XBase-Record-Update` on `Tickets`:
   - Filter: `Id = TicketId`
   - Values: `{ IsArchived: 0, UpdatedAt: now() }`
5. Call `XBase-Record-Insert` on `TicketHistory`:
   - `TicketId`, `Action: "Unarchived"`, `ActorUserId` (resolved from `SessionToken`), `OldValue: "1"`, `NewValue: "0"`, `ChangedAt: now()`
6. Return `TicketId`, `TicketNumber`, `UnarchivedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `TICKETING_TICKET_NOT_FOUND` | No active ticket exists with the given ID |
| `TICKETING_TICKET_NOT_ARCHIVED` | The ticket's `IsArchived` flag is already `0` |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Update`
- `XBase-Record-Insert`
