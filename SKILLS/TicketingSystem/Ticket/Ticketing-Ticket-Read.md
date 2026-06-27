# Ticketing-Ticket-Read

Fetch a single ticket by ID.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `TicketId` | int | yes | Numeric ticket ID |

## Outputs

```json
{
  "Success": true,
  "Ticket": {
    "TicketId": 42,
    "TicketNumber": "TKT-0042",
    "Summary": "...",
    "Description": "...",
    "StatusId": 1,
    "PriorityId": 2,
    "CategoryId": 3,
    "ReportedByUserId": 5,
    "AssignedToUserId": 7,
    "CreatedAt": "<ISO-8601>",
    "UpdatedAt": "<ISO-8601>",
    "ClosedAt": null,
    "IsDeleted": 0
  }
}
```

## Steps

1. Call `XBase-Record-Select` on the `Tickets` table with filter `Id = TicketId`
2. If no row is returned, return `TICKETING_TICKET_NOT_FOUND`
3. Return the full ticket row

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_TICKET_NOT_FOUND` | No ticket with the given ID |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Record-Select`
