# Ticketing-Report-Generate

Produce a full detailed report for a date range with configurable groupings.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `FromDate` | string | yes | — | ISO-8601 date, start of range (inclusive) |
| `ToDate` | string | yes | — | ISO-8601 date, end of range (inclusive) |
| `GroupBy` | array | no | `["Status"]` | Any combination of: `Status`, `Priority`, `Assignee`, `Category` |

## Outputs

```json
{
  "Success": true,
  "FromDate": "2026-06-01",
  "ToDate": "2026-06-25",
  "Summary": {
    "TotalTickets": 42,
    "ByStatus": [],
    "ByPriority": [],
    "ByAssignee": [],
    "ByCategory": []
  },
  "Tickets": [ { "TicketNumber": "TKT-0001", "..." : "..." } ],
  "GeneratedAt": "<ISO-8601>"
}
```

## Steps

1. Build date range filter: `CreatedAt >= FromDate AND CreatedAt <= ToDate + 'T23:59:59'`
2. For each dimension in `GroupBy`: `XBase-Query-Aggregate` with appropriate join
3. `XBase-Record-Select` → full ticket list within range (joins to `Statuses`, `Priorities`, `Users`, `Categories`)
4. Assemble `Summary` and `Tickets` array
5. Return full report

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_REPORT_DATE_RANGE_INVALID` | `FromDate` is after `ToDate` |

## Dependencies

- `XBase-Query-Aggregate`
- `XBase-Record-Select`
- `XBase-Query-Filter`
- `XBase-Query-Join`
