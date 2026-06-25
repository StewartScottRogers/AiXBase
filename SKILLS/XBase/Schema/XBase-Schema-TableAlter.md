# XBase-Schema-TableAlter

Add new columns to an existing table. (SQLite does not support renaming or dropping columns natively; use migration patterns for those.)

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

1. Validate `ConnectionName` and that `TableName` exists
2. For each column in `AddColumns`:
   - Execute `ALTER TABLE <TableName> ADD COLUMN <definition>`
   - Record the column name in `AddedColumns`
3. Return the list of added columns

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist |
| `XBASE_SCHEMA_COLUMN_EXISTS` | A column with that name already exists |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must already exist
