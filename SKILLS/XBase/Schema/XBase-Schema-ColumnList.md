# XBase-Schema-ColumnList

Return column definitions for a given table from `_schema.json`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | Open connection alias. |
| `TableName` | string | Yes | Name of the table to introspect. |

## Outputs

```json
{
  "Success": true,
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
  ],
  "Count": 6
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` using `read-text-file(path)`.
3. Locate the table entry where `Name` matches `TableName`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. Return the table's `Columns` array and `Count`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist in `_schema.json`. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
