# XBase-Record-Delete

Delete records matching a filter. By default performs a soft delete (writes the `0x2A` deletion flag and sets `IsDeleted = 1`). Pass `HardDelete: true` to PACK the file, physically removing matching records.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Registered connection alias |
| `TableName` | string | yes | Target table name |
| `Filter` | object | yes | Compiled filter specification from `XBase-Query-Filter` — required to prevent unintentional full-table deletes |
| `HardDelete` | bool | no | If `true`, PACK the file by rewriting it without matched records (default `false`) |
| `TransactionName` | string | no | If supplied, execute within this transaction's workspace directory |

## Outputs

```json
{
  "Success": true,
  "DeletedCount": 1,
  "HardDelete": false
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Validate `Filter` is present and non-empty; if absent or empty, return `XBASE_RECORD_FILTER_REQUIRED`.
3. Resolve the active data directory: if `TransactionName` is supplied, verify `_txn_{TransactionName}/` exists (return `XBASE_TRANSACTION_NOT_OPEN` if not); if `{TableName}.dbf` is not yet present in the workspace, copy it lazily from the live directory; use workspace paths for all reads and writes. Otherwise use the live database directory.
4. read-text-file(`_schema.json`); locate the `TableName` entry in `Tables`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
5. read-binary-file(`{TableName}.dbf`); parse the DBF header (first 32 bytes) to obtain `HeaderSize`, `RecordSize`, `RecordCount`, and the field descriptor array; decode each active record from its fixed byte positions.
6. Evaluate the `Filter` specification against each active record. For each matching record, increment `DeletedCount` and apply the deletion mode:
   - **Soft delete** (`HardDelete: false`): seek to the record's byte offset (`HeaderSize + (RecordIndex × RecordSize)`); overwrite byte 0 of the record with `0x2A` (deleted flag); overwrite the `IsDeleted` field bytes with the encoded value `1`; overwrite the `UpdatedAt` field bytes with the current ISO-8601 UTC timestamp encoded to the declared field width. The record remains in the file at its original position.
   - **Hard delete / PACK** (`HardDelete: true`): collect the bytes of all records whose deletion flag is `0x20` and that do not match the filter. Rewrite the entire `.dbf` file: write the 32-byte header with `RecordCount` at bytes 4–7 updated to the retained count and the last-modified date at bytes 1–3 updated to today; write the field descriptor array and header terminator `0x0D`; write only the retained records' bytes in sequence; write the EOF marker `0x1A`.
7. If `HardDelete` is `true`, rebuild every `.ndx` B-tree index for this table from the retained record set.
8. Return `DeletedCount` and the `HardDelete` mode used.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_TRANSACTION_NOT_OPEN` | `TransactionName` supplied but workspace directory not found |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_RECORD_FILTER_REQUIRED` | `Filter` was empty or omitted |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — to build the required filter specification
- `XBase-Transaction-Begin` — if using a named transaction
