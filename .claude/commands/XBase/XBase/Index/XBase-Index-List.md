# XBase-Index-List

Return index definitions for a given table from `_schema.json`.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to inspect |

## Outputs

```json
{
  "Success": true,
  "TableName": "Products",
  "Indexes": [
    { "IndexName": "idx_Products_SKU",   "Unique": true,  "Columns": ["SKU"]   },
    { "IndexName": "idx_Products_Label", "Unique": false, "Columns": ["Label"] }
  ]
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`
2. `File.ReadAllText(_schema.json)`; parse JSON
3. Verify `TableName` exists in the `Tables` array; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`
4. Filter the `Indexes` array to entries where `TableName` matches the input
5. Return the filtered index definitions as the `Indexes` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist in `_schema.json` |

## Dependencies

- `XBase-Database-Connect`
