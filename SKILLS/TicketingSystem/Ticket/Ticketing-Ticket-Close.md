# Ticketing-Ticket-Close

Transition a ticket to the terminal `Closed` status and ring the completion bell.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to close |
| `ClosedByUserId` | int | yes | — | User closing the ticket |
| `Comment` | string | no | — | Closing note recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "TicketNumber": "TKT-0042",
  "ClosedAt": "<ISO-8601>"
}
```

## Steps

1. Validate ticket exists, is not deleted, and is not already closed
2. Look up `StatusId` for the `Closed` status (`IsTerminal = 1`, `Name = 'Closed'`)
3. `Ticketing-Status-Transition` (to `Closed`, with `Comment`)
4. `XBase-Record-Update` → `Tickets` set `ClosedAt = now`
5. `Ticketing-Display-Complete` (passes `TicketNumber`, `Summary`, `ClosedByDisplayName`, `ClosedAt`)

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_TICKET_ALREADY_CLOSED` | Ticket is already in a terminal status |
| `TICKETING_STATUS_TRANSITION_INVALID` | No allowed transition from current status to Closed |

## Dependencies

- `Ticketing-Status-Transition`
- `Ticketing-Display-Complete`
- `XBase-Record-Update`
