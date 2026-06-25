# XBase-Query-Sort

Build an ORDER BY expression for use with `XBase-Record-Select`.

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
    "sql": "CreatedAt DESC, Id ASC"
  }
}
```

## Steps

1. Validate each `Field` name
2. Validate each `Direction` is `ASC` or `DESC`
3. Concatenate into `Field1 DIR1, Field2 DIR2, ...`
4. Return the compiled sort object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_SORT_FIELD_INVALID` | Field name contains illegal characters |
| `XBASE_SORT_DIRECTION_INVALID` | Direction is not `ASC` or `DESC` |

## Dependencies

None — pure compilation, no database access.
