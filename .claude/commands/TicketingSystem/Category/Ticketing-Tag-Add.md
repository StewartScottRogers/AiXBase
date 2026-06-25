# Ticketing-Tag-Add

Add a free-text tag to a ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to tag |
| `Tag` | string | yes | — | Tag text (trimmed, lowercased for storage) |
| `AddedByUserId` | int | yes | — | User adding the tag |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "Tag": "backend"
}
```

## Steps

1. Validate `TicketId` exists and `IsDeleted = 0`
2. Normalize `Tag`: trim whitespace and lowercase
3. Check `TicketTags` for an existing row with this `TicketId` + `Tag`; if found, return success (idempotent)
4. `XBase-Record-Insert` → `TicketTags`
5. Return `Tag`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |

## Dependencies

- `XBase-Record-Insert`
- `XBase-Record-Select`
