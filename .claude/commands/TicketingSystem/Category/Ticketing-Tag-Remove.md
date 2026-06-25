# Ticketing-Tag-Remove

Remove a tag from a ticket. Uses a hard delete since tags have no audit requirement.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketId` | int | yes | — | Ticket to untag |
| `Tag` | string | yes | — | Tag text to remove (matched after normalize: trim + lowercase) |
| `RemovedByUserId` | int | yes | — | User removing the tag |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "Tag": "backend",
  "Removed": true
}
```

`Removed` is `false` if the tag was not present (idempotent — not an error).

## Steps

1. Validate `TicketId` exists and `IsDeleted = 0`
2. Normalize `Tag`
3. `XBase-Record-Delete` (hard delete) → `TicketTags` where `TicketId` and `Tag` match
4. Return `Removed: true` if any rows were affected, `false` if none

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | Ticket does not exist or is deleted |

## Dependencies

- `XBase-Record-Delete`
- `XBase-Query-Filter`
