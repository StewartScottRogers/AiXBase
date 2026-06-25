# Ticketing-Ticket-Query

Search and list tickets with filter, sort, and pagination.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Filters` | array | no | `[]` | Array of `{ Field, Operator, Value }` filter specs |
| `SortBy` | string | no | `CreatedAt` | Column to sort by |
| `SortDirection` | string | no | `DESC` | `ASC` or `DESC` |
| `Page` | int | no | `1` | 1-based page number |
| `PageSize` | int | no | `25` | Rows per page, max `200` |
| `IncludeDeleted` | bool | no | `false` | Include soft-deleted tickets |

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
      "CreatedAt": "..."
    }
  ],
  "TotalCount": 137,
  "Page": 1,
  "PageSize": 25
}
```

## Steps

1. Build filter expressions using `XBase-Query-Filter` for each entry in `Filters`
2. Build sort using `XBase-Query-Sort`
3. Build joins to `Statuses`, `Priorities`, `Users` (assignee) via `XBase-Query-Join`
4. `XBase-Record-Select` → `Tickets` with filters, joins, sort, LIMIT/OFFSET from `Page`/`PageSize`
5. Return paged results and `TotalCount`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_QUERY_PAGE_SIZE_EXCEEDED` | `PageSize` > 200 |

## Dependencies

- `XBase-Record-Select`
- `XBase-Query-Filter`
- `XBase-Query-Sort`
- `XBase-Query-Join`
