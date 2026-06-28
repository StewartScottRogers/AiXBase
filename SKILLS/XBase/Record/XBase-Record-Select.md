# XBase-Record-Select

Read rows from a binary DBF file and return those matching the supplied filter, sort, and pagination specifications, evaluated entirely in memory.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Registered connection alias |
| `TableName` | string | yes | Source table name |
| `Columns` | array | no | Column names to project; `["*"]` returns all columns (default `["*"]`) |
| `Filter` | object | no | Compiled filter specification from `XBase-Query-Filter` |
| `Sort` | object | no | Compiled sort specification from `XBase-Query-Sort` |
| `Join` | object | no | Compiled join specification from `XBase-Query-Join` |
| `Aggregate` | object | no | Compiled aggregate specification from `XBase-Query-Aggregate` |
| `Limit` | int | no | Maximum number of rows to return after pagination |
| `Offset` | int | no | Number of rows to skip before returning results (default `0`) |
| `IncludeDeleted` | bool | no | If `false` (default), exclude rows where the deletion flag is `0x2A` or `IsDeleted = 1` |
| `TransactionName` | string | no | If supplied, read from this transaction's workspace directory |

## Outputs

```json
{
  "Success": true,
  "Rows": [ { "Id": 1, "Summary": "..." } ],
  "TotalCount": 57
}
```

`TotalCount` is the count of all matching rows before `Limit` and `Offset` are applied.

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Resolve the active data directory: if `TransactionName` is supplied, use the transaction workspace (reading from the live directory for any table file not yet present in the workspace); otherwise use the live database directory.
3. read-text-file(`_schema.json`); locate the `TableName` entry in `Tables`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. If `Columns` is not `["*"]`: validate each name is a safe identifier (`^[A-Za-z0-9_]+$`); return `XBASE_SCHEMA_COLUMN_MISSING` immediately for any name that fails this check. Then validate each safe name against the table's column definitions in `_schema.json`; return `XBASE_SCHEMA_COLUMN_MISSING` for any name not present in the schema.
5. read-binary-file(`{TableName}.dbf`); parse the DBF header (first 32 bytes) to obtain `HeaderSize`, `RecordSize`, `RecordCount`, and the field descriptor array. The field descriptor array begins immediately after byte 32 and consists of 32-byte entries — one per field — terminated by byte `0x0D`.
6. Decode each record: compute byte offset `HeaderSize + (R × RecordSize)` for record index R (zero-based); read `RecordSize` bytes at that offset; inspect byte 0 (deletion flag). Parse each field value from its fixed byte position using the field descriptor array: `N`-type fields are ASCII numeric strings (trim spaces, convert to number); `C`-type fields are ASCII strings (trim trailing spaces); `D`-type fields are 8-character ASCII date strings.
7. Unless `IncludeDeleted` is `true`, discard any record whose deletion flag is `0x2A` or whose `IsDeleted` field value is `1`.
8. Apply the `Filter` specification in memory: for each remaining record, evaluate every filter condition recursively. Supported operators: `=`, `!=`, `<`, `<=`, `>`, `>=` (type-coerced comparison); `LIKE` (`%` matches any characters, `_` matches one character, case-insensitive); `IN` / `NOT IN` (membership check against the `Value` array); `IS NULL` / `IS NOT NULL` (presence and nullness of the field). Combine nested `Filters` entries with their `LogicalOperator` (`AND` or `OR`). Discard records that do not pass.
9. Apply the `Join` specification in memory (if supplied): read-binary-file the joined table's `.dbf`; decode its records; exclude soft-deleted rows. For `INNER`, keep only primary records that have at least one matching record in the joined table on `OnLeft == OnRight`, and merge the joined table's fields into each retained row. For `LEFT`, keep all primary records and merge joined fields where a match exists, using `null` for fields from unmatched rows.
10. Apply the `Aggregate` specification in memory (if supplied): group the row set by `GroupBy` column values; compute `COUNT`, `SUM`, `AVG`, `MIN`, or `MAX` per group; replace the row set with the aggregated result rows.
11. Set `TotalCount` to the count of rows remaining after steps 7–10.
12. Apply the `Sort` specification: sort the row set in memory by each specified field in the specified direction (`ASC` or `DESC`), processing sort columns in the declared order.
13. Apply `Offset`: discard the first `Offset` rows.
14. Apply `Limit`: retain at most `Limit` rows (if `Limit` is supplied).
15. Apply `Columns` projection: if `Columns` is not `["*"]`, remove all fields not listed from each row.
16. Return `Rows` and `TotalCount`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table not in `_schema.json` |
| `XBASE_SCHEMA_COLUMN_MISSING` | A requested column name is not defined for this table |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Query-Filter` — optional, to build a filter specification
- `XBase-Query-Sort` — optional, to build a sort specification
- `XBase-Query-Join` — optional, to build a join specification
- `XBase-Query-Aggregate` — optional, to build an aggregate specification
