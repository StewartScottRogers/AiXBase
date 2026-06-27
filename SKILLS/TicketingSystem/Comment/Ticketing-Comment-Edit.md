# Ticketing-Comment-Edit

Update the body of an existing comment.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| CommentId | int | yes | Comment to edit |
| EditorUserId | int | yes | User making the edit |
| Body | string | yes | New comment text |

## Outputs

```json
{
  "Success": true,
  "CommentId": 17,
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Comments where Id = CommentId and IsDeleted = 0; if no row found, return TICKETING_COMMENT_NOT_FOUND.
2. Call XBase-Record-Update on Comments setting Body = Body, UpdatedAt = now() where Id = CommentId.
3. Call XBase-Record-Insert on TicketHistory with TicketId = comment.TicketId, ChangedByUserId = EditorUserId, Action = CommentEdited, ChangedAt = now().
4. Return UpdatedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_COMMENT_NOT_FOUND | CommentId does not exist or is soft-deleted |

## Dependencies

- XBase-Record-Select
- XBase-Record-Update
- XBase-Record-Insert
