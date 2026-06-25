# XBase-Index-Create

Create an index on one or more columns of a table to accelerate queries.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Table to index |
| `IndexName` | string | yes | — | Unique name for the index |
| `Columns` | array | yes | — | Ordered list of column names to include |
| `Unique` | bool | no | `false` | Create a `UNIQUE` index |
| `IfNotExists` | bool | no | `true` | Use `CREATE INDEX IF NOT EXISTS` |

## Outputs

```json
{
  "Success": true,
  "IndexName": "<name>",
  "SQL": "<generated DDL>"
}
```

## Steps

1. Validate `ConnectionName`, `TableName`, and `Columns`
2. Build `CREATE [UNIQUE] INDEX [IF NOT EXISTS] <IndexName> ON <TableName> (<columns>)`
3. Execute the DDL
4. Return `IndexName` and generated `SQL`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | Connection not open |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | Table does not exist |
| `XBASE_SCHEMA_COLUMN_MISSING` | A specified column does not exist |
| `XBASE_INDEX_EXISTS` | Index already exists and `IfNotExists` is `false` |

## Dependencies

- `XBase-Database-Connect`
- `XBase-Schema-TableCreate` — table must exist
