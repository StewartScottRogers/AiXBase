# XBase-Schema-TableCreate

Define a new table in the connected database with typed columns and constraints.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Open connection alias |
| `TableName` | string | yes | — | Name of the table to create |
| `Columns` | array | yes | — | Array of column definitions (see below) |
| `IfNotExists` | bool | no | `true` | Use `CREATE TABLE IF NOT EXISTS` |

### Column Definition Object

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `Name` | string | yes | — | Column name |
| `Type` | string | yes | — | `INTEGER`, `TEXT`, `REAL`, `BLOB`, `NUMERIC` |
| `PrimaryKey` | bool | no | `false` | Mark as primary key |
| `AutoIncrement` | bool | no | `false` | Apply `AUTOINCREMENT` (only valid with INTEGER PK) |
| `Nullable` | bool | no | `true` | If `false`, adds `NOT NULL` |
| `Unique` | bool | no | `false` | Adds `UNIQUE` constraint |
| `DefaultValue` | string | no | — | SQL literal default, e.g. `'Open'` or `0` |
| `ForeignKey` | string | no | — | `TableName.ColumnName` reference |

## Outputs

```json
{
  "Success": true,
  "TableName": "<name>",
  "SQL": "<generated DDL>"
}
```

## Steps

1. Validate `ConnectionName` is open; if not, return `XBASE_CONNECTION_INVALID`
2. If no column has `PrimaryKey: true`, prepend an implicit `Id INTEGER PRIMARY KEY AUTOINCREMENT` column
3. Always append `CreatedAt TEXT`, `UpdatedAt TEXT`, and `IsDeleted INTEGER DEFAULT 0` if not already present
4. Generate the `CREATE TABLE [IF NOT EXISTS] ...` DDL
5. Execute the DDL against the connection
6. Return `TableName` and the generated `SQL`

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not open |
| `XBASE_SCHEMA_TABLE_EXISTS` | Table already exists and `IfNotExists` is `false` |
| `XBASE_SCHEMA_COLUMN_INVALID` | Column definition is malformed |

## Dependencies

- `XBase-Database-Connect`
