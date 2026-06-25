# Ticketing-Ticket-Reopen

Transition a closed ticket back to the `Open` status.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to reopen |
| `ReopenedByUserId` | int | yes | — | User requesting the reopen |
| `Reason` | string | no | — | Reason for reopening, recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "ReopenedAt": "<ISO-8601>"
}
```

## Steps

1. Validate ticket exists and `IsDeleted = 0`
2. Verify the ticket is currently in a terminal status; if not, return `TICKETING_TICKET_NOT_CLOSED`
3. Look up `StatusId` for `Open`
4. `Ticketing-Status-Transition` (to `Open`, recording reason in `Comment`)
5. `XBase-Record-Update` → `Tickets` clear `ClosedAt` (set to `NULL`)
6. Return `ReopenedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist |
| `TICKETING_TICKET_NOT_CLOSED` | Ticket is not in a terminal status |
| `TICKETING_STATUS_TRANSITION_INVALID` | No allowed transition from current status to Open |

## Dependencies

- `Ticketing-Status-Transition`
- `XBase-Record-Update`
