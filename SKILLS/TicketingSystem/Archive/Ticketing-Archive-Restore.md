# Ticketing-Archive-Restore

Move a single ticket and all its related records from an archive database back into the main ticketing database, then hard-delete it from the archive. The ticket is restored with `IsArchived = 0` so it appears in normal queries immediately.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active XBase connection alias for the main ticketing database |
| `ArchiveConnectionName` | string | yes | Active XBase connection alias for the archive database |
| `SessionToken` | string | yes | Active session token |
| `TicketId` | int | yes | ID of the ticket to restore from the archive |

## Outputs

```json
{
  "Success": true,
  "TicketId": 42,
  "TicketNumber": "TKT-0042",
  "RestoredAt": "2026-06-28T20:00:00Z"
}
```

## Steps

1. Validate `ConnectionName` is registered. If not, return `XBASE_CONNECTION_INVALID`.
2. Validate `ArchiveConnectionName` is registered. If not, return `TICKETING_ARCHIVE_CONNECTION_INVALID`.
3. Call `XBase-Record-Select` on the archive database's `Tickets` table where `Id = TicketId` and `IsDeleted = 0`. If not found, return `TICKETING_TICKET_NOT_FOUND`.
4. Check whether a ticket with the same `Id` already exists in the main database's `Tickets` table. If it does, return `TICKETING_ARCHIVE_RESTORE_CONFLICT` — the caller must resolve the ID collision before restoring.
5. Collect the ticket's related records from the archive database: all rows in `Comments`, `Attachments`, `TicketHistory`, and `TicketTags` where `TicketId` matches.
6. Call `XBase-Record-Insert` on the main database to insert the ticket row with `IsArchived = 0` and all related rows, preserving all other original field values.
7. Call `XBase-Record-Delete` with `HardDelete: true` on the archive database to permanently remove the ticket and all its related records.
8. Call `XBase-Record-Insert` on `TicketHistory` in the main database:
   - `TicketId`, `Action: "RestoredFromArchive"`, `ActorUserId` (resolved from `SessionToken`), `ChangedAt: now()`
9. Return `TicketId`, `TicketNumber`, `RestoredAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `TICKETING_ARCHIVE_CONNECTION_INVALID` | `ArchiveConnectionName` is not registered |
| `TICKETING_TICKET_NOT_FOUND` | No ticket with the given ID exists in the archive database |
| `TICKETING_ARCHIVE_RESTORE_CONFLICT` | A ticket with the same ID already exists in the main database |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Insert`
- `XBase-Record-Delete`
