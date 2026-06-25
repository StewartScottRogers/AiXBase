# Ticketing-Priority-Set

Set or change the priority of a ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to update |
| `PriorityId` | int | yes | — | New priority |
| `ChangedByUserId` | int | yes | — | User making the change |

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

1. Validate `TicketId` and `PriorityId` exist
2. Fetch current priority name
3. `XBase-Transaction-Begin`
4. `XBase-Record-Update` → `Tickets` set `PriorityId`
5. `XBase-Record-Insert` → `TicketHistory` (action: `PriorityChanged`, `FromValue`, `ToValue`)
6. `XBase-Transaction-Commit`
7. Return `PreviousPriority`, `NewPriority`, `UpdatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_PRIORITY_NOT_FOUND` | `PriorityId` does not exist |

## Dependencies

- `XBase-Transaction-Begin/Commit`
- `XBase-Record-Update`
- `XBase-Record-Insert`
