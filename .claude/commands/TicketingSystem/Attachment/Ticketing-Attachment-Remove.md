# Ticketing-Attachment-Remove

Soft-delete an attachment record. The physical file is not deleted.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `AttachmentId` | int | yes | — | Attachment to remove |
| `RemovedByUserId` | int | yes | — | User requesting removal |

## Outputs

```json
{
  "Success": true,
  "AttachmentId": 5,
  "RemovedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `AttachmentId` exists and `IsDeleted = 0`
2. `XBase-Record-Update` → `Attachments` set `IsDeleted = 1`
3. Return `RemovedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_ATTACHMENT_NOT_FOUND` | Attachment does not exist or is already removed |

## Dependencies

- `XBase-Record-Update`
- `XBase-Query-Filter`
