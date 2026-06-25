# Ticketing-Report-Summary

Produce aggregate counts grouped by status, priority, and assignee for a quick dashboard view.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `IncludeDeleted` | bool | no | `false` | Include soft-deleted tickets in counts |

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
    { "Assignee": "Bob", "Count": 8 }
  ],
  "GeneratedAt": "<ISO-8601>"
}
```

## Steps

1. `XBase-Query-Aggregate` (COUNT by `StatusId`, joined to `Statuses.Name`)
2. `XBase-Query-Aggregate` (COUNT by `PriorityId`, joined to `Priorities.Name`)
3. `XBase-Query-Aggregate` (COUNT by `AssignedToUserId`, joined to `Users.DisplayName`)
4. Assemble and return the three result arrays

## Error Codes

None beyond standard XBase connection errors.

## Dependencies

- `XBase-Query-Aggregate`
- `XBase-Query-Join`
