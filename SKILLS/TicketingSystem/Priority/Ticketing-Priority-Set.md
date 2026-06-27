# Ticketing-Priority-Set

Set or change the priority of a ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to update |
| NewPriorityId | int | yes | Priority to assign |
| ChangedByUserId | int | yes | User making the change |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "PreviousPriority": "Medium",
  "NewPriority": "High",
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Tickets where Id = TicketId and IsDeleted = 0; if no row found, return TICKETING_TICKET_NOT_FOUND. Capture the current PriorityId from the ticket row for use as FromValue.
2. Call XBase-Record-Select on Priorities where Id = NewPriorityId; if no row found, return TICKETING_PRIORITY_NOT_FOUND.
3. Call XBase-Record-Update on Tickets setting PriorityId = NewPriorityId, UpdatedAt = now() where Id = TicketId.
4. Call XBase-Record-Insert on TicketHistory with TicketId, ChangedByUserId, Action = PriorityChanged, FromValue = previous priority Name, ToValue = new priority Name, ChangedAt = now().
5. Return PreviousPriority, NewPriority, and UpdatedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | Ticket does not exist or is soft-deleted |
| TICKETING_PRIORITY_NOT_FOUND | NewPriorityId does not exist |

## Dependencies

- XBase-Record-Select
- XBase-Record-Update
- XBase-Record-Insert
