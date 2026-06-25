# Ticketing-Category-Assign

Assign or change the category of a ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to categorize |
| `CategoryId` | int | yes | — | Category to assign |
| `ChangedByUserId` | int | yes | — | User making the change |

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

1. Validate `TicketId` and `CategoryId` exist
2. `XBase-Record-Update` → `Tickets` set `CategoryId`
3. `XBase-Record-Insert` → `TicketHistory` (action: `CategoryChanged`)
4. Return `CategoryName` and `UpdatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_CATEGORY_NOT_FOUND` | `CategoryId` does not exist |

## Dependencies

- `XBase-Record-Update`
- `XBase-Record-Insert`
