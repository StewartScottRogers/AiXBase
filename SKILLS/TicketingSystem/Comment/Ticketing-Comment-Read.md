# Ticketing-Comment-Read

Fetch one comment by ID, or all comments on a ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `CommentId` | int | no | — | Specific comment; provide `CommentId` or `TicketId` |
| `TicketId` | int | no | — | Return all comments for this ticket |
| `IncludeDeleted` | bool | no | `false` | Include soft-deleted comments |

## Outputs

```json
{
  "Success": true,
  "Comments": [
    {
      "CommentId": 17,
      "TicketId": 42,
      "Author": "Alice",
      "Body": "...",
      "CreatedAt": "...",
      "UpdatedAt": "..."
    }
  ]
}
```

## Steps

1. Build filter: by `CommentId` or by `TicketId`
2. Unless `IncludeDeleted`, append `IsDeleted = 0` to filter
3. `XBase-Record-Select` → `Comments` joined to `Users` for author display name
4. Return `Comments` array (single element when fetching by `CommentId`)

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_COMMENT_NOT_FOUND` | `CommentId` specified but not found |

## Dependencies

- `XBase-Record-Select`
- `XBase-Query-Filter`
- `XBase-Query-Join`
