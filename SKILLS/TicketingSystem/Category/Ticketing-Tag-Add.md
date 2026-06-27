# Ticketing-Tag-Add

Add a free-text tag to a ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to tag |
| TagName | string | yes | Tag value to add |

## Outputs

```json
{
  "Success": true,
  "TagId": 7,
  "TicketId": 42,
  "TagName": "backend"
}
```

## Steps

1. Call XBase-Record-Select on Tickets where Id = TicketId and IsDeleted = 0; if no row found, return TICKETING_TICKET_NOT_FOUND.
2. Call XBase-Record-Select on Tags where TicketId = TicketId and Name = TagName; if a row is found, the tag already exists — return the existing TagId (idempotent).
3. Call XBase-Record-Insert on Tags with TicketId and Name = TagName.
4. Return TagId.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | Ticket does not exist or is soft-deleted |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
