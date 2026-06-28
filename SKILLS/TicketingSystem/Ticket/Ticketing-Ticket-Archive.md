# Ticketing-Ticket-Archive

Bulk-mark closed tickets as archived so they are excluded from default queries. Only tickets in a terminal status (IsTerminal = 1) may be archived. Archived tickets remain in the database and are fully recoverable via `Ticketing-Ticket-Unarchive`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active XBase connection alias for the ticketing database |
| `SessionToken` | string | yes | Active session token |
| `OlderThanDays` | int | no (default 30) | Archive only tickets whose `UpdatedAt` is older than this many days |
| `StatusNames` | array | no (default `["Done","Cancelled"]`) | Restrict to tickets in these named statuses; all must be terminal |
| `TicketIds` | array | no | If supplied, archive exactly these ticket IDs regardless of age or status filter |
| `DryRun` | bool | no (default false) | Report what would be archived without making changes |

## Outputs

```json
{
  "Success": true,
  "ArchivedCount": 42,
  "TicketNumbers": ["TKT-0001", "TKT-0002"],
  "DryRun": false,
  "ArchivedAt": "2026-06-28T20:00:00Z"
}
```

## Steps

1. Validate `ConnectionName` is registered. If not, return `XBASE_CONNECTION_INVALID`.
2. If `TicketIds` is supplied and non-empty, skip to step 5 using those IDs directly.
3. Look up the `Id` values from the `Statuses` table for each name in `StatusNames`. If any named status is not found, return `TICKETING_ARCHIVE_STATUS_NOT_FOUND`. If any resolved status has `IsTerminal = 0`, return `TICKETING_ARCHIVE_STATUS_NOT_TERMINAL`.
4. Compute the cutoff timestamp: `now() - OlderThanDays` days. Call `Ticketing-Ticket-Query` with:
   - Filter: `StatusId IN [resolved IDs]` AND `UpdatedAt < cutoff` AND `IsArchived = 0`
   - `IncludeArchived: false`
   - `PageSize: 200`
   Collect all matching ticket IDs and numbers. If `TotalCount > 200`, paginate until all are collected.
5. If no tickets match, return `Success: true` with `ArchivedCount: 0`.
6. If `DryRun` is true, return `ArchivedCount`, `TicketNumbers`, and `DryRun: true` without writing.
7. For each matching ticket, call `XBase-Record-Update` on the `Tickets` table:
   - Filter: `Id = <TicketId>`
   - Values: `{ IsArchived: 1, UpdatedAt: now() }`
8. Return `ArchivedCount`, `TicketNumbers`, `DryRun: false`, and `ArchivedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `TICKETING_ARCHIVE_STATUS_NOT_FOUND` | A name in `StatusNames` does not match any status in the database |
| `TICKETING_ARCHIVE_STATUS_NOT_TERMINAL` | A resolved status has `IsTerminal = 0`; only terminal statuses may be archived |

## Dependencies

- `XBase-Record-Update`
- `Ticketing-Ticket-Query`
