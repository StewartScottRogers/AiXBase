# XBase-Schema-TableCreate

Add a table definition to `_schema.json` and create an empty dBASE III binary `.dbf` data file.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | Open connection alias. |
| `TableName` | string | Yes | Name of the table to create (alphanumeric and underscore only). |
| `Columns` | array | Yes | Array of column definition objects (see below). |
| `IfNotExists` | bool | No | Succeed silently when the table already exists. Default: `true`. |

### Column Definition Object

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Name` | string | Yes | Column name (alphanumeric and underscore only). |
| `Type` | string | Yes | `INTEGER`, `TEXT`, or `REAL`. |
| `PrimaryKey` | bool | No | Mark as the primary key column. Default: `false`. |
| `AutoIncrement` | bool | No | Auto-assign via `NextId` counter in `_schema.json`. Default: `false`. |
| `Nullable` | bool | No | If `false`, enforce NOT NULL on insert. Default: `true`. |
| `Unique` | bool | No | Enforce uniqueness on insert and update. Default: `false`. |
| `Default` | any | No | Value to use when the column is omitted on insert. |
| `ForeignKey` | string | No | `TableName.ColumnName` reference for FK validation. |

## Outputs

```json
{
  "Success": true,
  "TableName": "Users",
  "ColumnCount": 6
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` using `read-text-file(path)`.
3. If a table entry with the same `Name` already exists:
   a. If `IfNotExists` is `true`, return `Success: true` (no-op).
   b. If `IfNotExists` is `false`, return `XBASE_SCHEMA_TABLE_EXISTS`.
4. If no column in `Columns` has `PrimaryKey: true`, prepend an implicit column: `{ Name: "Id", Type: "INTEGER", PrimaryKey: true, AutoIncrement: true, Nullable: false, Unique: true, Default: null, ForeignKey: null }`.
5. Append these columns if not already present in `Columns`: `{ Name: "CreatedAt", Type: "TEXT" }`, `{ Name: "UpdatedAt", Type: "TEXT" }`, `{ Name: "IsDeleted", Type: "INTEGER", Default: 0 }`.
6. Validate all column definitions; return `XBASE_SCHEMA_COLUMN_INVALID` on any malformed entry or if duplicate column names exist.
7. Add the table entry to the `Tables` array with `NextId: 1`; write updated `_schema.json` using `write-text-file(path, content)`.
8. Write a valid empty dBASE III binary DBF file using `write-binary-file(path, bytes)`: version byte `0x03`, record count `0`, `HeaderSize` = 32 + (32 × FieldCount) + 1 bytes, `RecordSize` = 1 + sum(field widths), field descriptor array (32 bytes per field: bytes 0–10 = null-padded field name, byte 11 = type character, byte 16 = field width, byte 17 = decimal count, remaining bytes zeroed), header terminator `0x0D`, EOF marker `0x1A`. Type mapping: `INTEGER` → type `'N'`, width 10, decimal 0; `REAL` → type `'N'`, width 20, decimal 10; `TEXT` → type `'C'`, width = declared max length (default 255).
9. Return `TableName` and `ColumnCount` (total number of columns including implicit ones).

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |
| `XBASE_SCHEMA_TABLE_EXISTS` | Table already exists and `IfNotExists` is `false`. |
| `XBASE_SCHEMA_COLUMN_INVALID` | A column definition is malformed or duplicate column names exist. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
