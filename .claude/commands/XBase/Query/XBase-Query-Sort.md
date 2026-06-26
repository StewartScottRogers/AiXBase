# XBase-Query-Sort

Build a sort specification object for use with `XBase-Record-Select` or
`XBase-Query-Execute`. No file I/O occurs — pure compilation. The resulting object is
applied in memory by the executing skill.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Columns` | array | yes | — | Array of `{ Field, Direction }` objects |

### Sort Column Object

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `Field` | string | yes | — | Column name to sort by |
| `Direction` | string | no | `ASC` | `ASC` or `DESC` |

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

1. Validate each `Field` name — alphanumeric + underscore only; return `XBASE_SORT_FIELD_INVALID` on failure
2. Validate each `Direction` is `ASC` or `DESC`; return `XBASE_SORT_DIRECTION_INVALID` on failure
3. Default `Direction` to `ASC` if omitted
4. Return the compiled sort specification object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_SORT_FIELD_INVALID` | Field name contains illegal characters |
| `XBASE_SORT_DIRECTION_INVALID` | Direction is not `ASC` or `DESC` |

## Dependencies

None — pure compilation, no file access.
