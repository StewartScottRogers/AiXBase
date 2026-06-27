# Ticketing-Comment-Delete

Soft-delete a comment.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| CommentId | int | yes | Comment to delete |
| DeletedByUserId | int | yes | User requesting deletion |

## Outputs

```json
{
  "Success": true,
  "CommentId": 17,
  "DeletedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Comments where Id = CommentId and IsDeleted = 0; if no row found, return TICKETING_COMMENT_NOT_FOUND.
2. Call XBase-Record-Delete (soft delete) on Comments for CommentId, setting IsDeleted = 1 and UpdatedAt = now().
3. Call XBase-Record-Insert on TicketHistory with TicketId = comment.TicketId, ChangedByUserId = DeletedByUserId, Action = CommentDeleted, ChangedAt = now().
4. Return DeletedAt (the value of UpdatedAt set in step 2).

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_COMMENT_NOT_FOUND | CommentId does not exist or is already soft-deleted |

## Dependencies

- XBase-Record-Select
- XBase-Record-Delete
- XBase-Record-Insert
