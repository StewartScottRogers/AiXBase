# Ticketing-Comment-Read

Fetch one comment by ID, or all comments on a ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket whose comments to retrieve |
| CommentId | int | no | When supplied, return only this comment |

## Outputs

```json
{
  "Success": true,
  "Comments": [
    {
      "CommentId": 17,
      "TicketId": 42,
      "AuthorUserId": 3,
      "AuthorDisplayName": "Alice",
      "Body": "...",
      "CreatedAt": "<ISO-8601>",
      "UpdatedAt": "<ISO-8601>"
    }
  ],
  "Count": 1
}
```

## Steps

1. Call XBase-Record-Select on Comments filtering by TicketId = TicketId; if CommentId is supplied, also filter by Id = CommentId.
2. Exclude any rows where IsDeleted = 1.
3. Call XBase-Query-Join with Users on AuthorUserId to resolve AuthorDisplayName.
4. Return Comments array and Count.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_COMMENT_NOT_FOUND | CommentId was supplied but no matching active comment was found |

## Dependencies

- XBase-Record-Select
- XBase-Query-Filter
- XBase-Query-Join
