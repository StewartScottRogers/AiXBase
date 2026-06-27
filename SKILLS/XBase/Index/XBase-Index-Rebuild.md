# XBase-Index-Rebuild

Rebuild a specific index on a table by re-reading all active records from the `.dbf` file and rewriting the `.ndx` B-tree index from scratch.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Open connection alias |
| `TableName` | string | yes | Table whose index will be rebuilt |
| `IndexName` | string | yes | Name of the index to rebuild |

## Outputs

```json
{
  "Success": true,
  "IndexName": "<name>",
  "EntryCount": 42,
  "RebuildAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` from the database directory using `read-text-file(path)`. Verify the `Indexes` array contains an entry with `Name` equal to `IndexName` and `TableName` matching the input; if absent, return `XBASE_INDEX_NOT_FOUND`.
3. Retrieve the index definition to obtain the `Columns` list and `Unique` flag.
4. Read the binary content of `{TableName}.dbf` using `read-binary-file(path)`. Parse the DBF header (first 32 bytes) to obtain `HeaderSize` (bytes 8–9, uint16 little-endian), `RecordSize` (bytes 10–11, uint16 little-endian), `RecordCount` (bytes 4–7, uint32 little-endian), and the field descriptor array (32-byte descriptors beginning at byte 32). For each record index `R` from `0` to `RecordCount − 1`, seek to byte offset `HeaderSize + (R × RecordSize)`, read `RecordSize` bytes, and check the deletion flag byte: skip the record if it equals `0x2A` (deleted). Decode each active record's field values from their fixed-width byte positions as defined by the field descriptor array.
5. For each active record, compute the index key: single-column as the string value of the indexed field; multi-column as a pipe-delimited concatenation of field values in `Columns` order. Pair each key with its record offset `HeaderSize + (RecordIndex × RecordSize)`.
6. Sort all `(Key, RecordOffset)` pairs ascending by `Key` (lexicographic order).
7. Delete the existing `{TableName}.{IndexName}.ndx` file.
8. Write a new NDX B-tree index file at `{TableName}.{IndexName}.ndx` using `write-binary-file(path, bytes)`, containing the sorted `(Key, RecordOffset)` pairs in B-tree structure.
9. Return `IndexName`, `EntryCount` (the number of pairs written), and `RebuildAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `XBASE_INDEX_NOT_FOUND` | `IndexName` does not exist in `_schema.json` for the given table |

## Dependencies

- `XBase-Database-Connect`
