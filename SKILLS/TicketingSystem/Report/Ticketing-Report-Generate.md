# Ticketing-Report-Generate

Produce a full detailed report for a date range with configurable groupings.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| FromDate | string | yes | ISO-8601 date, start of range inclusive |
| ToDate | string | yes | ISO-8601 date, end of range inclusive |
| GroupBy | array | no | Any combination of: Status, Priority, Assignee, Category (default: ["Status"]) |

## Outputs

```json
{
  "Success": true,
  "FromDate": "2026-06-01",
  "ToDate": "2026-06-27",
  "Summary": {
    "TotalTickets": 42,
    "ByStatus": [],
    "ByPriority": [],
    "ByAssignee": [],
    "ByCategory": []
  },
  "Tickets": [{ "TicketNumber": "TKT-0001" }],
  "GeneratedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Validate that FromDate is not after ToDate; if it is, return TICKETING_REPORT_DATE_RANGE_INVALID.
2. Call XBase-Query-Filter to produce a date range filter: CreatedAt >= FromDate AND CreatedAt <= ToDate.
3. Call XBase-Record-Select on Tickets applying the date filter.
4. For each dimension listed in GroupBy, call XBase-Query-Aggregate with the appropriate grouping field; call XBase-Query-Join with Statuses, Priorities, Users, or Categories as needed to resolve IDs to names.
5. Call XBase-Query-Join to enrich the Tickets result with Status name, Priority name, AssignedTo DisplayName, and Category name.
6. Assemble the Summary object with aggregates for each GroupBy dimension and set TotalTickets.
7. Return Summary, Tickets (full detail), FromDate, ToDate, and GeneratedAt = now().

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_REPORT_DATE_RANGE_INVALID | FromDate is after ToDate |
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Query-Aggregate
- XBase-Record-Select
- XBase-Query-Filter
- XBase-Query-Join
