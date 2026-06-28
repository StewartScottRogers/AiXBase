# Ticketing-Archive-Query

Search and list tickets stored in an archive database. Behaves identically to `Ticketing-Ticket-Query` but targets an archive XBase database rather than the live ticketing database. Connect to the archive database first with `XBase-Database-Connect` before calling this skill.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ArchiveConnectionName` | string | yes | Active XBase connection alias for the archive database |
| `Filters` | array | no | Array of `{ Field, Operator, Value }` filter objects |
| `SortBy` | string | no | Column to sort by; default `CreatedAt` |
| `SortDirection` | string | no | `ASC` or `DESC`; default `DESC` |
| `Page` | int | no | 1-based page number; default `1` |
| `PageSize` | int | no | Rows per page; default `25`, max `200` |

## Outputs

```json
{
  "Success": true,
  "ArchiveConnectionName": "ticketing_2026",
  "Tickets": [
    {
      "TicketId": 42,
      "TicketNumber": "TKT-0042",
      "Summary": "...",
      "Status": "Done",
      "Priority": "High",
      "AssignedTo": "Bob",
      "CreatedAt": "<ISO-8601>",
      "ClosedAt": "<ISO-8601>"
    }
  ],
  "TotalCount": 87,
  "Page": 1,
  "PageSize": 25
}
```

## Steps

1. Validate `ArchiveConnectionName` is registered. If not, return `XBASE_CONNECTION_INVALID`.
2. Call `Ticketing-Ticket-Query` using `ArchiveConnectionName` as the `ConnectionName`, passing through all `Filters`, `SortBy`, `SortDirection`, `Page`, and `PageSize` inputs. Pass `IncludeArchived: true` so that the archive database's tickets (all of which have `IsArchived = 1`) are visible.
3. Return the result with the addition of `ArchiveConnectionName` in the output envelope.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ArchiveConnectionName` is not registered |
| `TICKETING_QUERY_PAGE_SIZE_EXCEEDED` | `PageSize` is greater than 200 |

## Dependencies

- `Ticketing-Ticket-Query`
- `XBase-Database-Connect` (caller must connect to the archive database before calling this skill)
