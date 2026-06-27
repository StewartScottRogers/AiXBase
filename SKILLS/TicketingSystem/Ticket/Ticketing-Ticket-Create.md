# Ticketing-Ticket-Create

Open a new ticket in the ticketing database.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Summary` | string | yes | Short title, max 200 characters |
| `Description` | string | no | Full description |
| `ReportedByUserId` | int | yes | User ID of the reporter |
| `AssignedToUserId` | int | no | User ID of the initial assignee |
| `CategoryId` | int | no | Category FK |
| `PriorityId` | int | no | Priority FK; defaults to the row where `IsDefault = 1` in the Priorities table |
| `Tags` | array | no | Free-text tags to attach; one row inserted per tag into the Tags table |

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

1. Call `XBase-Record-Select` on the `Users` table with filter `Id = ReportedByUserId`; if no row is returned, return `TICKETING_USER_NOT_FOUND`; if `IsActive = 0`, return `TICKETING_USER_INACTIVE`
2. If `PriorityId` is not provided, call `XBase-Record-Select` on the `Priorities` table with filter `IsDefault = 1`; use the returned `Id` as `PriorityId`
3. Call `XBase-Record-Select` on the `Statuses` table with filter `Name = 'Open'`; capture the returned `Id` as `StatusId`
4. Call `XBase-Transaction-Begin`
5. Call `XBase-Record-Insert` on the `Tickets` table with `Summary`, `Description`, `StatusId`, `PriorityId`, `CategoryId`, `ReportedByUserId`, `AssignedToUserId`, `CreatedAt = now()`, `UpdatedAt = now()`, `IsDeleted = 0`; capture the auto-increment `Id` returned by the insert
6. Compute `TicketNumber = 'TKT-' + Id` zero-padded to four digits (e.g. `TKT-0001`); call `XBase-Record-Update` on the `Tickets` table with filter `Id = TicketId` to write the computed `TicketNumber`
7. Call `XBase-Record-Insert` on the `TicketHistory` table with `TicketId`, `ChangedByUserId = ReportedByUserId`, `Action = 'Created'`, `ChangedAt = now()`
8. For each string in `Tags`, call `XBase-Record-Insert` on the `Tags` table with `TicketId` and the tag value
9. Call `XBase-Transaction-Commit`
10. Return `TicketId`, `TicketNumber`, `CreatedAt`

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_USER_NOT_FOUND` | `ReportedByUserId` does not exist |
| `TICKETING_USER_INACTIVE` | Reporter is deactivated |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Transaction-Begin`
- `XBase-Transaction-Commit`
- `XBase-Record-Insert`
- `XBase-Record-Select`
- `XBase-Record-Update`
