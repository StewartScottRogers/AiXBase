# Ticketing-Attachment-Read

List or fetch attachment metadata for a ticket.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `AttachmentId` | int | no | — | Specific attachment; provide `AttachmentId` or `TicketId` |
| `TicketId` | int | no | — | Return all attachments for this ticket |
| `IncludeDeleted` | bool | no | `false` | Include soft-deleted attachments |

## Outputs

```json
{
  "Success": true,
  "Attachments": [
    {
      "AttachmentId": 5,
      "TicketId": 42,
      "FileName": "screenshot.png",
      "FilePath": "data/attachments/tkt42/screenshot.png",
      "UploadedBy": "Alice",
      "UploadedAt": "..."
    }
  ]
}
```

## Steps

1. Build filter by `AttachmentId` or `TicketId`
2. Unless `IncludeDeleted`, append `IsDeleted = 0`
3. `XBase-Record-Select` → `Attachments` joined to `Users` for uploader display name
4. Return `Attachments` array

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_ATTACHMENT_NOT_FOUND` | `AttachmentId` specified but not found |

## Dependencies

- `XBase-Record-Select`
- `XBase-Query-Filter`
- `XBase-Query-Join`
