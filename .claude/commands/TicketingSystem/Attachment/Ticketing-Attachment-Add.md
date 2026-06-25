# Ticketing-Attachment-Add

Associate a file reference with a ticket and record its metadata.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to attach the file to |
| `UploadedByUserId` | int | yes | — | User adding the attachment |
| `FileName` | string | yes | — | Original file name |
| `FilePath` | string | yes | — | Path relative to `AiXBase/attachments/` where the file is stored |

## Outputs

```json
{
  "Success": true,
  "AttachmentId": 5,
  "UploadedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `TicketId` exists and `IsDeleted = 0`
2. Validate `UploadedByUserId` exists and `IsActive = 1`
3. Verify the physical file exists at the resolved `FilePath`
4. `XBase-Record-Insert` → `Attachments`
5. Return `AttachmentId` and `UploadedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist |
| `TICKETING_ATTACHMENT_FILE_NOT_FOUND` | Physical file not found at `FilePath` |

## Dependencies

- `XBase-Record-Insert`
