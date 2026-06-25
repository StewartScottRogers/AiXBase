# Ticketing-Ticket-Update

Edit the summary, description, or metadata of an existing ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to update |
| `ChangedByUserId` | int | yes | — | User making the change |
| `Summary` | string | no | — | New summary |
| `Description` | string | no | — | New description |
| `CategoryId` | int | no | — | New category |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate ticket exists and is not soft-deleted
2. Build the `Values` map from non-null inputs only
3. `XBase-Transaction-Begin`
4. `XBase-Record-Update` → `Tickets` where `Id = TicketId`
5. `XBase-Record-Insert` → `TicketHistory` for each changed field (action: `Updated`)
6. `XBase-Transaction-Commit`
7. Return `UpdatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |

## Dependencies

- `XBase-Transaction-Begin/Commit`
- `XBase-Record-Update`
- `XBase-Record-Insert`
