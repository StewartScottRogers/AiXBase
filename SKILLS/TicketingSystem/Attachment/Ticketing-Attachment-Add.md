# Ticketing-Attachment-Add

Associate a file reference with a ticket. Does not copy or move the file; the caller is responsible for physically placing the file at FilePath before calling this skill.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket to attach the file to |
| FileName | string | yes | Original file name |
| FilePath | string | yes | Path to the file (relative to {DatabaseRoot}/attachments/ or absolute) |
| UploadedByUserId | int | yes | User adding the attachment |

## Outputs

```json
{
  "Success": true,
  "AttachmentId": 5,
  "UploadedAt": "<ISO-8601>"
}
```

## Steps

1. Call XBase-Record-Select on Tickets where Id = TicketId and IsDeleted = 0; if no row found, return TICKETING_TICKET_NOT_FOUND.
2. Call XBase-Record-Select on Users where Id = UploadedByUserId and IsActive = 1; if no active row found, return TICKETING_USER_NOT_FOUND.
3. Call XBase-Record-Insert on Attachments with TicketId, FileName, FilePath, UploadedByUserId, UploadedAt = now(), IsDeleted = 0.
4. Call XBase-Record-Insert on TicketHistory with TicketId, ChangedByUserId = UploadedByUserId, Action = AttachmentAdded, ChangedAt = now().
5. Return AttachmentId and UploadedAt.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | Ticket does not exist or is soft-deleted |
| TICKETING_USER_NOT_FOUND | UploadedByUserId does not exist or is inactive |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
