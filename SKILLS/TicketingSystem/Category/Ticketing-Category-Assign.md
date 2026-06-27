# Ticketing-Category-Assign

Assign a category to a ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to categorize |
| CategoryId | int | yes | Category to assign |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "CategoryName": "Bug",
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Tickets where Id = TicketId and IsDeleted = 0; if no row found, return TICKETING_TICKET_NOT_FOUND.
2. Call XBase-Record-Select on Categories where Id = CategoryId; if no row found, return TICKETING_CATEGORY_NOT_FOUND.
3. Call XBase-Record-Update on Tickets setting CategoryId = CategoryId, UpdatedAt = now() where Id = TicketId.
4. Call XBase-Record-Insert on TicketHistory with TicketId, Action = CategoryAssigned, ToValue = category Name, ChangedAt = now().
5. Return CategoryName and UpdatedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | Ticket does not exist or is soft-deleted |
| TICKETING_CATEGORY_NOT_FOUND | CategoryId does not exist |

## Dependencies

- XBase-Record-Select
- XBase-Record-Update
- XBase-Record-Insert
