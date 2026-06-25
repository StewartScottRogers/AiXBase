# Ticketing-Comment-Edit

Update the body of an existing comment.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `CommentId` | int | yes | — | Comment to edit |
| `EditedByUserId` | int | yes | — | Must match `AuthorUserId` or be an admin |
| `Body` | string | yes | — | New comment text |

## Outputs

```json
{
  "Success": true,
  "CommentId": 17,
  "UpdatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `CommentId` exists and `IsDeleted = 0`
2. Validate `EditedByUserId` is the comment author or has admin role
3. `XBase-Record-Update` → `Comments` set `Body`, `UpdatedAt`
4. Return `UpdatedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_COMMENT_NOT_FOUND` | Comment does not exist or is deleted |
| `TICKETING_PERMISSION_DENIED` | Editor is neither the author nor an admin |

## Dependencies

- `XBase-Record-Update`
- `XBase-Query-Filter`
