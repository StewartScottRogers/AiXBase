# Ticketing-Ticket-Query

Search and list tickets with filter, sort, and pagination.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Filters` | array | no | Array of `{ Field, Operator, Value }` filter objects; omit or pass empty to return all tickets |
| `SortBy` | string | no | Column to sort by; default `CreatedAt` |
| `SortDirection` | string | no | `ASC` or `DESC`; default `DESC` |
| `Page` | int | no | 1-based page number; default `1` |
| `PageSize` | int | no | Rows per page; default `25`, max `200` |
| `IncludeArchived` | bool | no | Include archived tickets (`IsArchived = 1`); default `false` |

## Outputs

```json
{
  "Success": true,
  "Tickets": [
    {
      "TicketId": 42,
      "TicketNumber": "TKT-0042",
      "Summary": "...",
      "Status": "Open",
      "Priority": "High",
      "AssignedTo": "Bob",
      "CreatedAt": "<ISO-8601>"
    }
  ],
  "TotalCount": 137,
  "Page": 1,
  "PageSize": 25
}
```

## Steps

1. If `IncludeArchived` is false (the default), prepend an implicit filter `IsArchived = 0` to the filter list before processing any caller-supplied filters.
2. For each entry in `Filters`, call `XBase-Query-Filter` with the specified `Field`, `Operator`, and `Value` to build the composite filter expression
3. Call `XBase-Query-Sort` with `SortBy` and `SortDirection`
4. Call `XBase-Query-Join` to join the `Tickets` table to `Statuses`, `Priorities`, and `Users` (assignee) as needed for display fields
5. Call `XBase-Record-Select` on the `Tickets` table with the compiled filter, sort, joins, `Limit = PageSize`, and `Offset = (Page - 1) * PageSize`
6. Return `Tickets` array, `TotalCount`, `Page`, `PageSize`

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_QUERY_PAGE_SIZE_EXCEEDED` | `PageSize` is greater than 200 |
| `XBASE_CONNECTION_INVALID` | No active connection named `ticketing` |

## Dependencies

- `XBase-Record-Select`
- `XBase-Query-Filter`
- `XBase-Query-Sort`
- `XBase-Query-Join`
