# Ticketing-Ticket-Escalate

Raise a ticket's priority by one level and emit an alert notification.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to escalate |
| `EscalatedByUserId` | int | yes | — | User requesting escalation |
| `Reason` | string | no | — | Reason, recorded in history |
| `TargetPriorityId` | int | no | — | Specific priority to set; omit to auto-raise by one weight level |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "PreviousPriority": "Medium",
  "NewPriority": "High",
  "EscalatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate ticket exists and `IsDeleted = 0`
2. Fetch current `PriorityId` and its `Weight`
3. If `TargetPriorityId` omitted: select the `Priorities` row with the next lower `Weight` (higher urgency)
4. If already at the highest priority, return `TICKETING_PRIORITY_ALREADY_MAX`
5. `Ticketing-Priority-Set` with the resolved `TargetPriorityId`
6. `XBase-Record-Insert` → `TicketHistory` (action: `Escalated`)
7. `Ticketing-Display-Alert` (event: `TICKET ESCALATED`, detail: new priority name)
8. Return `PreviousPriority`, `NewPriority`, `EscalatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_PRIORITY_ALREADY_MAX` | Ticket is already at the highest priority |

## Dependencies

- `Ticketing-Priority-Set`
- `Ticketing-Display-Alert`
- `XBase-Record-Insert`
