# Ticketing-Ticket-Delete

Soft-delete a ticket by setting `IsDeleted = 1`. The ticket remains in the database for audit purposes.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to delete |
| `DeletedByUserId` | int | yes | — | User requesting the deletion |
| `Reason` | string | no | — | Optional reason, recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "DeletedAt": "<ISO-8601>"
}
```

## Steps

1. Validate ticket exists and `IsDeleted = 0`
2. `XBase-Transaction-Begin`
3. `XBase-Record-Update` → `Tickets` set `IsDeleted = 1`, `UpdatedAt = now`
4. `XBase-Record-Insert` → `TicketHistory` (action: `Deleted`, `ToValue`: `Reason` if provided)
5. `XBase-Transaction-Commit`
6. Return `DeletedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist |
| `TICKETING_TICKET_ALREADY_DELETED` | Ticket already soft-deleted |

## Dependencies

- `XBase-Transaction-Begin/Commit`
- `XBase-Record-Update`
- `XBase-Record-Insert`
