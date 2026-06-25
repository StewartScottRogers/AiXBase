# XBase-Schema-ColumnList

Return column definitions for a given table.

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
      "Nullable": false,
      "DefaultValue": null,
      "PrimaryKey": true
    }
  ]
}
```

## Steps

1. Validate `ConnectionName` and that `TableName` exists
2. Execute: `PRAGMA table_info(<TableName>)`
3. Map each row to a column definition object (`cid`, `name`, `type`, `notnull`, `dflt_value`, `pk`)
4. Return the `Columns` array

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist |

## Dependencies

- `XBase-Database-Connect`
