# Ticketing-Attachment-Remove

Soft-delete an attachment record. The physical file is not deleted.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| AttachmentId | int | yes | Attachment to remove |
| RemovedByUserId | int | yes | User requesting removal |

## Outputs

```json
{
  "Success": true,
  "AttachmentId": 5,
  "RemovedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Attachments where Id = AttachmentId and IsDeleted = 0; if no row found, return XBASE_RECORD_CONSTRAINT_VIOLATION.
2. Call XBase-Record-Delete (soft delete) on Attachments for AttachmentId, setting IsDeleted = 1.
3. Call XBase-Record-Insert on TicketHistory with TicketId = attachment.TicketId, ChangedByUserId = RemovedByUserId, Action = AttachmentRemoved, ChangedAt = now().
4. Return RemovedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| XBASE_RECORD_CONSTRAINT_VIOLATION | AttachmentId does not exist or is already soft-deleted |

## Dependencies

- XBase-Record-Select
- XBase-Record-Delete
- XBase-Record-Insert
