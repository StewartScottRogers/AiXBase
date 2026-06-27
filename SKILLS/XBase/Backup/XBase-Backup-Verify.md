# XBase-Backup-Verify

Validate the integrity of a backup directory by inspecting its metadata files and verifying the binary structure of every `.dbf` data file.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `BackupPath` | string | yes | Path to the backup directory to verify |

## Outputs

```json
{
  "Success": true,
  "BackupPath": "<path>",
  "IntegrityOk": true,
  "Issues": [],
  "VerifiedAt": "<ISO-8601>"
}
```

When issues are found, `IntegrityOk` is `false` and `Issues` lists each problem with the file name and a description of the anomaly.

## Steps

1. Verify the backup directory exists at `BackupPath` using `directory-exists(BackupPath)`; if not, return `XBASE_BACKUP_NOT_FOUND`.
2. Read `_meta.json` using `read-text-file(BackupPath/_meta.json)`. Parse as JSON and verify the `XBaseVersion` field is present and is a positive integer; if the file is missing or unparseable, return `XBASE_BACKUP_CORRUPT`.
3. Read `_schema.json` using `read-text-file(BackupPath/_schema.json)`. Parse as JSON and verify the `Tables` array is present and valid; if invalid, add `"_schema.json: missing or malformed Tables array"` to `Issues`.
4. For each table entry in `_schema.json Tables`:
   a. Verify `{TableName}.dbf` exists at `BackupPath/{TableName}.dbf` using `file-exists(path)`; if absent, add `"{TableName}.dbf: file missing"` to `Issues` and skip to the next table.
   b. Read the binary content of `{TableName}.dbf` using `read-binary-file(path)`.
   c. Verify byte 0 equals `0x03` (dBASE III version marker); if not, add `"{TableName}.dbf: invalid version byte"` to `Issues`.
   d. Read `RecordCount` from bytes 4–7 (uint32, little-endian), `HeaderSize` from bytes 8–9 (uint16, little-endian), and `RecordSize` from bytes 10–11 (uint16, little-endian).
   e. Verify the field descriptor array starting at byte 32: read 32-byte field descriptors until the header terminator byte `0x0D` is reached; confirm that `HeaderSize` equals `32 + (32 × FieldCount) + 1`. If not, add `"{TableName}.dbf: HeaderSize mismatch"` to `Issues`.
   f. Verify the total file size equals `HeaderSize + (RecordCount × RecordSize) + 1` (the final `+1` is for the EOF `0x1A` marker); if not, add `"{TableName}.dbf: file size mismatch"` to `Issues`.
   g. For each record index `R` from `0` to `RecordCount − 1`, read the deletion flag byte at offset `HeaderSize + (R × RecordSize)`; if the byte is neither `0x20` (active) nor `0x2A` (deleted), add `"{TableName}.dbf: invalid deletion flag at record R"` to `Issues`.
5. Set `IntegrityOk: true` if `Issues` is empty; otherwise set `IntegrityOk: false`.
6. Return `IntegrityOk`, `Issues`, and `VerifiedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_BACKUP_NOT_FOUND` | Directory does not exist at `BackupPath` |
| `XBASE_BACKUP_CORRUPT` | `_meta.json` is missing, unreadable, or lacks a valid `XBaseVersion` field |

## Dependencies

None — reads files directly without requiring an open connection.
