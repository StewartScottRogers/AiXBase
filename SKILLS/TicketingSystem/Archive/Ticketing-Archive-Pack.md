# Ticketing-Archive-Pack

Move archived tickets and all their related records out of the main ticketing database into a named archive XBase database, then hard-delete them from the main database. The archive database is a fully valid XBase ticketing database and can be queried with any Ticketing skill.

Call `Ticketing-Ticket-Archive` first to mark tickets as archived before packing.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active XBase connection alias for the main ticketing database |
| `SessionToken` | string | yes | Active session token |
| `ArchiveDatabaseName` | string | yes | Name of the target archive XBase database (e.g. `ticketing_2026`); created if it does not exist |
| `DatabaseRoot` | string | yes | Root directory under which the archive database will be created |
| `DryRun` | bool | no (default false) | Report what would be packed without writing anything |

## Outputs

```json
{
  "Success": true,
  "PackedCount": 87,
  "ArchiveDatabaseName": "ticketing_2026",
  "ArchiveDatabasePath": "C:/data/ticketing_2026",
  "DryRun": false,
  "PackedAt": "2026-06-28T20:00:00Z"
}
```

## Steps

1. Validate `ConnectionName` is registered. If not, return `XBASE_CONNECTION_INVALID`.
2. Select all tickets from `Tickets` where `IsArchived = 1` and `IsDeleted = 0`. If none, return `Success: true` with `PackedCount: 0`.
3. If `DryRun` is true, return `PackedCount` and `ArchiveDatabaseName` without writing.
4. Check whether the archive database directory `{DatabaseRoot}/{ArchiveDatabaseName}` exists:
   - If not: call `XBase-Database-Initialize` with `DatabaseRoot` and `DatabaseName = ArchiveDatabaseName`, then call `XBase-Schema-TableCreate` to create the same 11 Ticketing tables that exist in the main database (read the schema from the main database's `_schema.json` and replicate it).
5. Call `XBase-Database-Connect` with `DatabaseName = ArchiveDatabaseName` and a temporary `ConnectionName` alias (e.g. `_archive_pack`).
6. For each archived ticket:
   a. Collect the ticket's related records: all rows in `Comments`, `Attachments`, `TicketHistory`, and `TicketTags` where `TicketId` matches.
   b. Call `XBase-Record-Insert` on the archive database to insert the ticket row and all related rows, preserving all field values including original `Id` values.
   c. Call `XBase-Record-Delete` with `HardDelete: true` on the main database to permanently remove the ticket and all its related records.
7. Call `XBase-Database-Disconnect` on the temporary archive connection alias.
8. Return `PackedCount`, `ArchiveDatabaseName`, `ArchiveDatabasePath`, `DryRun: false`, `PackedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `TICKETING_ARCHIVE_PACK_INIT_FAILED` | The archive database could not be initialized or connected |

## Dependencies

- `XBase-Record-Select`
- `XBase-Record-Insert`
- `XBase-Record-Delete`
- `XBase-Database-Initialize`
- `XBase-Database-Connect`
- `XBase-Database-Disconnect`
- `XBase-Schema-TableCreate`
