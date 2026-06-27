# Ticketing-Report-Summary

Produce aggregate counts grouped by status, priority, and assignee for a quick dashboard view.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ConnectionName | string | no | XBase connection name (default: "ticketing") |

## Outputs

```json
{
  "Success": true,
  "ByStatus": [
    { "Status": "Open", "Count": 14 },
    { "Status": "In Progress", "Count": 5 }
  ],
  "ByPriority": [
    { "Priority": "Critical", "Count": 2 }
  ],
  "ByAssignee": [
    { "Assignee": "Alice Smith", "Count": 8 }
  ],
  "TotalOpen": 19,
  "TotalClosed": 7,
  "GeneratedAt": "2026-06-27T10:00:00Z"
}
```

## Steps

1. Call XBase-Query-Aggregate with Count grouped by StatusId on the Tickets table; call XBase-Query-Join with Statuses to resolve each StatusId to its Name; produce the ByStatus array.
2. Call XBase-Query-Aggregate with Count grouped by PriorityId on the Tickets table; call XBase-Query-Join with Priorities to resolve each PriorityId to its Name; produce the ByPriority array.
3. Call XBase-Query-Aggregate with Count grouped by AssignedToUserId on the Tickets table; call XBase-Query-Join with Users to resolve each AssignedToUserId to its DisplayName; produce the ByAssignee array.
4. Calculate TotalOpen as the sum of counts for all non-terminal statuses; calculate TotalClosed as the sum of counts for terminal statuses (IsTerminal = 1).
5. Return ByStatus, ByPriority, ByAssignee, TotalOpen, TotalClosed, and GeneratedAt = now().

## Error Codes

| Code | Meaning |
|------|---------|
| XBASE_CONNECTION_INVALID | No active XBase connection named "ticketing" |

## Dependencies

- XBase-Query-Aggregate
- XBase-Query-Join
