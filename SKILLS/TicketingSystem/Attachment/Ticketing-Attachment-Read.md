# Ticketing-Attachment-Read

List or fetch attachment metadata for a ticket.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketId | int | yes | Ticket whose attachments to retrieve |
| AttachmentId | int | no | When supplied, return only this attachment |

## Outputs

```json
{
  "Success": true,
  "Attachments": [
    {
      "AttachmentId": 5,
      "TicketId": 42,
      "FileName": "screenshot.png",
      "FilePath": "{DatabaseRoot}/attachments/tkt42/screenshot.png",
      "UploadedByUserId": 3,
      "UploaderDisplayName": "Alice",
      "UploadedAt": "<ISO-8601>"
    }
  ],
  "Count": 1
}
```

## Steps

1. Call XBase-Record-Select on Attachments filtering by TicketId = TicketId; if AttachmentId is supplied, also filter by Id = AttachmentId.
2. Exclude any rows where IsDeleted = 1.
3. Call XBase-Query-Join with Users on UploadedByUserId to resolve UploaderDisplayName.
4. Return Attachments array and Count.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_TICKET_NOT_FOUND | TicketId does not exist |

## Dependencies

- XBase-Record-Select
- XBase-Query-Filter
- XBase-Query-Join
