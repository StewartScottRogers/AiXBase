# XBase-Index-Create

Read all active records from a table's `.dbf` file, build a sorted NDX B-tree index, write it to a `.ndx` file, and register the index definition in `_schema.json`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Open connection alias |
| `TableName` | string | yes | Table to index |
| `IndexName` | string | yes | Name for the new index (e.g. `idx_Products_SKU`) |
| `Columns` | array of string | yes | Ordered list of column names to include in the index key |
| `Unique` | bool | no (default `false`) | Enforce uniqueness of key values across all active records |
| `IfNotExists` | bool | no (default `true`) | Succeed silently if the index is already defined |

## Outputs

```json
{
  "Success": true,
  "IndexName": "<name>",
  "CreatedAt": "<ISO-8601>"
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` from the database directory. Locate the table entry with name equal to `TableName`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
3. Verify every name in `Columns` exists in the table's column definitions; if any is missing, return `XBASE_SCHEMA_COLUMN_MISSING`.
4. Check the `Indexes` array in `_schema.json` for an entry whose `Name` equals `IndexName`:
   - If found and `IfNotExists` is `true`: return `Success: true` immediately (no-op).
   - If found and `IfNotExists` is `false`: return `XBASE_INDEX_EXISTS`.
5. Read the binary content of `{TableName}.dbf` using `read-binary-file(path)`. Parse the DBF header (first 32 bytes) to obtain `HeaderSize` (bytes 8–9, uint16 little-endian), `RecordSize` (bytes 10–11, uint16 little-endian), `RecordCount` (bytes 4–7, uint32 little-endian), and the field descriptor array (32-byte descriptors starting at byte 32). For each record index `R` from `0` to `RecordCount − 1`, seek to byte offset `HeaderSize + (R × RecordSize)`, read `RecordSize` bytes, and check the first (deletion flag) byte: skip the record if it equals `0x2A` (deleted). Decode each active record's field values from their fixed-width byte positions as defined by the field descriptor array.
6. For each active record, compute the index key:
   - Single-column index: `Key = string value of the Columns[0] field`.
   - Multi-column index: `Key = pipe-delimited concatenation of column values in Columns order`.
   Pair each key with its record offset `HeaderSize + (RecordIndex × RecordSize)`.
7. If `Unique` is `true`, verify no two active records produce the same key; if duplicates exist, return `XBASE_RECORD_CONSTRAINT_VIOLATION`.
8. Sort all `(Key, RecordOffset)` pairs ascending by `Key` (lexicographic order).
9. Write the new NDX B-tree index file at `{TableName}.{IndexName}.ndx` using `write-binary-file(path, bytes)`, storing the sorted `(Key, RecordOffset)` entries in B-tree structure to support O(log n) lookup.
10. Append an index definition to the `Indexes` array in `_schema.json`: `{ "Name": IndexName, "TableName": TableName, "Columns": Columns, "Unique": Unique }`.
11. Write the updated `_schema.json` back to the database directory using `write-text-file(path, content)`.
12. Return `IndexName` and `CreatedAt`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist in `_schema.json` |
| `XBASE_SCHEMA_COLUMN_MISSING` | A name in `Columns` does not match any column defined for the table |
| `XBASE_INDEX_EXISTS` | Index already defined and `IfNotExists` is `false` |
| `XBASE_RECORD_CONSTRAINT_VIOLATION` | `Unique` is `true` but duplicate key values exist in active records |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must exist before indexing
