# Ticketing-Status-Transition

Move a ticket from one status to another, validating allowed transitions. Fires `Ticketing-Display-Complete` when the destination is terminal.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to transition |
| `ToStatusId` | int | yes | — | Target status |
| `ChangedByUserId` | int | yes | — | User making the change |
| `Comment` | string | no | — | Note recorded in history |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "FromStatus": "In Progress",
  "ToStatus": "Closed",
  "TransitionedAt": "<ISO-8601>"
}
```

## Steps

1. Fetch current `StatusId` from the ticket
2. Validate the transition exists in `StatusTransitions(FromStatusId, ToStatusId)` — bypass if user has admin role
3. `XBase-Transaction-Begin`
4. `XBase-Record-Update` → `Tickets` set `StatusId = ToStatusId`
5. `XBase-Record-Insert` → `TicketHistory` (action: `StatusChanged`, `FromValue`, `ToValue`)
6. `XBase-Transaction-Commit`
7. If `ToStatus.IsTerminal = 1`: call `Ticketing-Display-Complete`
8. Return `FromStatus`, `ToStatus`, `TransitionedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |
| `TICKETING_STATUS_NOT_FOUND` | `ToStatusId` does not exist |
| `TICKETING_STATUS_TRANSITION_INVALID` | Transition not permitted for non-admin users |

## Dependencies

- `XBase-Transaction-Begin/Commit`
- `XBase-Record-Update`
- `XBase-Record-Insert`
- `Ticketing-Display-Complete` — called on terminal transitions
