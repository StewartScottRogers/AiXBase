# Ticketing-Ticket-Create

Open a new ticket in the ticketing database.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Summary` | string | yes | — | Short title, max 200 characters |
| `Description` | string | no | — | Full description |
| `ReportedByUserId` | int | yes | — | User ID of the reporter |
| `AssignedToUserId` | int | no | — | User ID of the assignee |
| `CategoryId` | int | no | — | Category FK |
| `PriorityId` | int | no | — | Priority FK; defaults to the row where `IsDefault = 1` |
| `Tags` | array | no | `[]` | Free-text tags to attach |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "TicketNumber": "TKT-0042",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ReportedByUserId` exists and `IsActive = 1`
2. If `PriorityId` omitted, select `Id` from `Priorities` where `IsDefault = 1`
3. Select the `Id` from `Statuses` where `Name = 'Open'`
4. `XBase-Transaction-Begin`
5. `XBase-Record-Insert` → `Tickets` with computed `TicketNumber` (`TKT-` + zero-padded next ID)
6. `XBase-Record-Insert` → `TicketHistory` (action: `Created`)
7. For each tag in `Tags`: `XBase-Record-Insert` → `TicketTags`
8. `XBase-Transaction-Commit`
9. Return `TicketId`, `TicketNumber`, `CreatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_USER_NOT_FOUND` | `ReportedByUserId` does not exist |
| `TICKETING_USER_INACTIVE` | Reporter is deactivated |

## Dependencies

- `XBase-Transaction-Begin/Commit`
- `XBase-Record-Insert`
