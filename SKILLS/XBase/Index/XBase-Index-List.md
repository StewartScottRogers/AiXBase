# XBase-Index-List

Return index definitions for a given table from `_schema.json`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Open connection alias |
| `TableName` | string | yes | Table to inspect |

## Outputs

```json
{
  "Success": true,
  "TableName": "Products",
  "Indexes": [
    { "Name": "idx_Products_SKU",   "Columns": ["SKU"],   "Unique": true  },
    { "Name": "idx_Products_Label", "Columns": ["Label"], "Unique": false }
  ],
  "Count": 2
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` from the database directory using `read-text-file(path)`.
3. Verify `TableName` exists in the `Tables` array; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. Filter the `Indexes` array to entries where `TableName` matches the input value.
5. Return the filtered list as `Indexes` and set `Count` to the number of entries returned.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist in `_schema.json` |

## Dependencies

- `XBase-Database-Connect`
