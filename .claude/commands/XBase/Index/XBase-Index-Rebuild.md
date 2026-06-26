# XBase-Index-Rebuild

Rebuild one or all indexes on a table by re-reading the `.ndjson` file and rewriting
the `.ndx` files from scratch. Use after bulk data operations to ensure index
consistency.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | no | — | Table whose indexes to rebuild; required if `IndexName` is omitted |
| `IndexName` | string | no | — | Specific index to rebuild; omit to rebuild all indexes for `TableName` |

## Outputs

```json
{
  "Success": true,
  "RebuiltIndexes": ["idx_Products_SKU", "idx_Products_Label"]
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. `File.ReadAllText(_schema.json)`; parse JSON
3. Resolve which indexes to rebuild:
   - If `IndexName` provided: find the entry in `Indexes` where `Name == IndexName`; if absent, return `XBASE_INDEX_NOT_FOUND`; derive `TableName` from the entry
   - Else if `TableName` provided: collect all entries in `Indexes` where `TableName` matches; if none, return `XBASE_SCHEMA_TABLE_NOT_FOUND`
   - Else: collect all entries in `Indexes`
4. `File.ReadAllLines({TableName}.ndjson)`; parse each non-empty line; exclude rows where `IsDeleted == 1`
5. For each index to rebuild:
   a. Compute key for every active row (single-column: `String(row[col])`; multi-column: `|`-delimited)
   b. Sort all `{ Key, Id }` entries ascending by `Key`
   c. `File.WriteAllLines({TableName}.{IndexName}.ndx, serializedEntries)` — full overwrite
   d. Add `IndexName` to `RebuiltIndexes`
6. Return `RebuiltIndexes`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_INDEX_NOT_FOUND` | Specified `IndexName` does not exist |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Specified `TableName` has no indexes defined |

## Dependencies

- `XBase-Database-Connect`
