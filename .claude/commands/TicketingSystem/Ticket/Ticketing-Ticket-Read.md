# Ticketing-Ticket-Read

Fetch a single ticket by ID with full related data.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | no | — | Numeric ticket ID |
| `TicketNumber` | string | no | — | Human-readable key, e.g. `TKT-0042`; provide one of `TicketId` or `TicketNumber` |
| `IncludeComments` | bool | no | `false` | Include the comments array in the response |
| `IncludeHistory` | bool | no | `false` | Include the change history array |

## Outputs

```json
{
  "Success": true,
  "Ticket": {
    "TicketId": 42,
    "TicketNumber": "TKT-0042",
    "Summary": "...",
    "Description": "...",
    "Status": "Open",
    "Priority": "High",
    "Category": "Bug",
    "ReportedBy": "Alice",
    "AssignedTo": "Bob",
    "Tags": ["backend", "urgent"],
    "CreatedAt": "...",
    "UpdatedAt": "...",
    "Comments": [],
    "History": []
  }
}
```

## Steps

1. Look up by `TicketId` or `TicketNumber` (error if neither provided)
2. `XBase-Record-Select` → `Tickets` joined to `Statuses`, `Priorities`, `Categories`, `Users` (reporter + assignee)
3. `XBase-Record-Select` → `TicketTags` for the ticket
4. If `IncludeComments`: `XBase-Record-Select` → `Comments` where `TicketId` matches and `IsDeleted = 0`
5. If `IncludeHistory`: `XBase-Record-Select` → `TicketHistory` where `TicketId` matches
6. Assemble and return the `Ticket` object

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | No ticket matches the given ID or number |

## Dependencies

- `XBase-Record-Select`
- `XBase-Query-Filter`
- `XBase-Query-Join`
