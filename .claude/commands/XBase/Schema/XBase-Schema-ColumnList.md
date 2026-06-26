# XBase-Schema-ColumnList

Return column definitions for a given table from `_schema.json`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to introspect |

## Outputs

```json
{
  "Success": true,
  "TableName": "<name>",
  "Columns": [
    {
      "Name": "Id",
      "Type": "INTEGER",
      "PrimaryKey": true,
      "AutoIncrement": true,
      "Nullable": false,
      "Unique": true,
      "Default": null,
      "ForeignKey": null
    }
  ]
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. Resolve the active `_schema.json` path (transaction workspace if active, otherwise live)
3. `File.ReadAllText(_schema.json)`; parse JSON
4. Locate the table entry where `Name == TableName`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`
5. Return the table's `Columns` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist in `_schema.json` |

## Dependencies

- `XBase-Database-Connect`
