# Ticketing-Comment-Delete

Soft-delete a comment by setting `IsDeleted = 1`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `CommentId` | int | yes | — | Comment to delete |
| `DeletedByUserId` | int | yes | — | Must match `AuthorUserId` or be an admin |

## Outputs

```json
{
  "Success": true,
  "CommentId": 17,
  "DeletedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `CommentId` exists and `IsDeleted = 0`
2. Validate `DeletedByUserId` is the comment author or has admin role
3. `XBase-Record-Update` → `Comments` set `IsDeleted = 1`, `UpdatedAt`
4. Return `DeletedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_COMMENT_NOT_FOUND` | Comment does not exist or is already deleted |
| `TICKETING_COMMENT_DELETE_FORBIDDEN` | Requester is neither the author nor an admin |

## Dependencies

- `XBase-Record-Update`
- `XBase-Query-Filter`
