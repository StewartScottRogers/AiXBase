# Ticketing-Ticket-Update

Edit the summary, description, or category of an existing ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Ticket to update |
| `UpdatedByUserId` | int | yes | User making the change |
| `Summary` | string | no | New summary (max 200 characters) |
| `Description` | string | no | New description |
| `CategoryId` | int | no | New category FK |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`; if no row is returned or `IsDeleted = 1`, return `TICKETING_TICKET_NOT_FOUND`
2. Call `XBase-Transaction-Begin`
3. Call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId`, setting only the fields provided among `Summary`, `Description`, and `CategoryId`, plus `UpdatedAt = now()`
4. Call `XBase-Record-Insert` on the `TicketHistory` table with `TicketId`, `ChangedByUserId = UpdatedByUserId`, `Action = 'Updated'`, `ChangedAt = now()`
5. Call `XBase-Transaction-Commit`
6. Return `TicketId` and `UpdatedAt`

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is soft-deleted |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Transaction-Begin`
- `XBase-Transaction-Commit`
- `XBase-Record-Select`
- `XBase-Record-Update`
- `XBase-Record-Insert`
