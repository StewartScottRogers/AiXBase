# XBase-Schema-TableAlter

Add new columns to an existing table definition in `_schema.json` and migrate the `.dbf` data file to include the new fields.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | Yes | Open connection alias. |
| `TableName` | string | Yes | Name of the table to alter. |
| `AddColumns` | array | Yes | Column definition objects to add (same schema as XBase-Schema-TableCreate). |

## Outputs

```json
{
  "Success": true,
  "TableName": "Users",
  "AddedColumnCount": 2
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Read `_schema.json` using `read-text-file(path)`.
3. Locate the table entry where `Name` matches `TableName`; if absent, return `XBASE_SCHEMA_TABLE_NOT_FOUND`.
4. For each column in `AddColumns`:
   a. Validate the column definition (name, type); return `XBASE_SCHEMA_COLUMN_INVALID` on error.
   b. Verify no existing column in the table has the same `Name`; return `XBASE_SCHEMA_COLUMN_EXISTS` if duplicate.
5. Read the existing `.dbf` file using `read-binary-file(path)`: parse the current header, field descriptor array, record count, and all existing records.
6. Build a new field descriptor array that includes all existing fields followed by the new columns.
7. For each existing record, extend the fixed-length byte sequence with zero-padded or space-padded bytes for each new column (using the column's `Default` value encoded to the appropriate field type if non-null, otherwise zeros for numeric fields or spaces for character fields).
8. Write the updated `.dbf` file using `write-binary-file(path, bytes)` with the new header (recalculated `HeaderSize`, `RecordSize`, and field descriptor array) and all migrated records.
9. Append the new column definitions to the table's `Columns` array in `_schema.json`; write updated `_schema.json` using `write-text-file(path, content)`.
10. Return `TableName` and `AddedColumnCount`.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |
| `XBASE_SCHEMA_TABLE_NOT_FOUND` | `TableName` does not exist in `_schema.json`. |
| `XBASE_SCHEMA_COLUMN_EXISTS` | A column with that name already exists in the table. |
| `XBASE_SCHEMA_COLUMN_INVALID` | A column definition is malformed. |

## Dependencies

- Writable local file system
- XBase-Database-Connect
- XBase-Schema-TableCreate (table must already exist)
