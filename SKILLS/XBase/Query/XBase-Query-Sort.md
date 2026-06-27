# XBase-Query-Sort

Compile and return a sort specification object for use with `XBase-Record-Select` or `XBase-Query-Execute`. No file I/O occurs — pure compilation step.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Field` | string | yes | Primary column name to sort by |
| `Direction` | string | no | `ASC` or `DESC` for the primary column (default `ASC`) |
| `Sorts` | array | no | Array of additional `{ Field, Direction }` objects for multi-column sorting |

## Outputs

```json
{
  "Success": true,
  "Sort": {
    "Columns": [
      { "Field": "CreatedAt", "Direction": "DESC" },
      { "Field": "Id",        "Direction": "ASC"  }
    ]
  }
}
```

## Steps

1. Validate `Field` is a safe identifier: letters, numbers, and underscores only (`^[A-Za-z0-9_]+$`); return `XBASE_SORT_FIELD_INVALID` if it contains any other character.
2. Validate `Direction` is `ASC` or `DESC`; return `XBASE_SORT_DIRECTION_INVALID` if present but neither; default to `ASC` if omitted.
3. If `Sorts` is provided, validate each entry in the array by applying steps 1–2 to its `Field` and `Direction` values.
4. Assemble a `Columns` array: the primary `{ Field, Direction }` pair as the first entry, followed in order by any entries from `Sorts`.
5. Return the compiled sort specification object containing the `Columns` array.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_SORT_FIELD_INVALID` | A `Field` name contains characters outside letters, numbers, and underscores |
| `XBASE_SORT_DIRECTION_INVALID` | `Direction` is not `ASC` or `DESC` |

## Dependencies

- None — pure compilation step with no file access.
