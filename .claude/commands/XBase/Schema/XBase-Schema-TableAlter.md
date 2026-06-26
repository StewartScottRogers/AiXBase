# XBase-Schema-TableAlter

Add new columns to an existing table definition in `_schema.json`. Column removals and
renames are not supported — use a migration pattern (create new table, copy rows,
drop old table) for those operations.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to alter |
| `AddColumns` | array | no | `[]` | Column definition objects to add (same schema as `XBase-Schema-TableCreate`) |

## Outputs

```json
{
  "Success": true,
  "TableName": "<name>",
  "AddedColumns": ["<col1>", "<col2>"]
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. `File.ReadAllText(_schema.json)`; parse JSON
3. Locate the table entry where `Name == TableName`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`
4. For each column in `AddColumns`:
   - Validate the column definition (name, type); return `XBASE_SCHEMA_COLUMN_INVALID` on error
   - Check that no existing column has the same `Name`; return `XBASE_SCHEMA_COLUMN_EXISTS` if duplicate
   - Append the column definition to the table's `Columns` array
   - Record the column name in `AddedColumns`
5. `File.WriteAllText(_schema.json, updatedSchema)`
6. Return the list of `AddedColumns`

**Note:** Adding a column does not backfill existing rows in `{TableName}.ndjson`. Existing rows
return `null` (or the column's `Default`) when the field is absent from the stored JSON object.

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist in `_schema.json` |
| `XBASE_SCHEMA_COLUMN_EXISTS` | A column with that name already exists |
| `XBASE_SCHEMA_COLUMN_INVALID` | Column definition is malformed |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must already exist
