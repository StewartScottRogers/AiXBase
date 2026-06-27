# Ticketing-Ticket-Delete

Soft-delete a ticket by setting `IsDeleted = 1`. The ticket remains in the database for audit purposes.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Ticket to delete |
| `DeletedByUserId` | int | yes | User requesting the deletion |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "DeletedAt": "<ISO-8601>"
}
```

## Steps

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`; if no row is returned or `IsDeleted = 1`, return `TICKETING_TICKET_NOT_FOUND`
2. Call `XBase-Transaction-Begin`
3. Call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId` setting `IsDeleted = 1` and `UpdatedAt = now()`
4. Call `XBase-Record-Insert` on the `TicketHistory` table with `TicketId`, `ChangedByUserId = DeletedByUserId`, `Action = 'Deleted'`, `ChangedAt = now()`
5. Call `XBase-Transaction-Commit`
6. Return `TicketId` and `DeletedAt` (the timestamp from step 3)

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is already soft-deleted |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Transaction-Begin`
- `XBase-Transaction-Commit`
- `XBase-Record-Select`
- `XBase-Record-Update`
- `XBase-Record-Insert`
