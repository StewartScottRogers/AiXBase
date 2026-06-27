# Ticketing-Tag-Remove

Remove a tag from a ticket. Uses a hard delete since tags have no audit requirement.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to remove the tag from |
| TagName | string | yes | Tag value to remove |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "TagName": "backend"
}
```

## Steps

1. Call XBase-Record-Select on Tags where TicketId = TicketId and Name = TagName; if no row found, return XBASE_RECORD_CONSTRAINT_VIOLATION.
2. Call XBase-Record-Delete (hard delete) on Tags for the TagId found in step 1.
3. Return Success.

## Error Codes

| Code | Meaning |
|------|---------|
| XBASE_RECORD_CONSTRAINT_VIOLATION | No tag matching TagName found on this ticket |

## Dependencies

- XBase-Record-Select
- XBase-Record-Delete
