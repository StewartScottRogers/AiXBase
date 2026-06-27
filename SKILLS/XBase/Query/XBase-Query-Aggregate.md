# XBase-Query-Aggregate

Compile and return an aggregate specification object for use with `XBase-Record-Select` or `XBase-Query-Execute`. No file I/O occurs — pure compilation step. Aggregation is evaluated in memory against the matched row set by the executing skill.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Function` | string | yes | Aggregate function: `COUNT`, `SUM`, `AVG`, `MIN`, or `MAX` |
| `Field` | string | yes | Column to aggregate; `*` is allowed only for `COUNT` |
| `Alias` | string | no | Output field name in the result row; defaults to `{Function}_{Field}` |
| `GroupBy` | array | no | Column names to group rows by before aggregating |

## Outputs

```json
{
  "Success": true,
  "Aggregate": {
    "Functions": [
      { "Function": "COUNT", "Field": "*",     "Alias": "Total"    },
      { "Function": "AVG",   "Field": "Price", "Alias": "AvgPrice" }
    ],
    "GroupBy": ["StatusName"]
  }
}
```

## Steps

1. Validate `Function` is one of `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`; return `XBASE_AGGREGATE_FUNCTION_UNKNOWN` if not.
2. Validate `Field` is a safe identifier (letters, numbers, and underscores only) or the literal `*`. `*` is valid only when `Function` is `COUNT`; return `XBASE_FILTER_FIELD_INVALID` if `Field` contains any illegal character or if `*` is used with a function other than `COUNT`.
3. If `Alias` is omitted, derive a default from `{Function}_{Field}` (for example, `COUNT_*` becomes `Count` and `SUM_Price` becomes `SumPrice`).
4. If `GroupBy` is supplied, validate each entry is a safe identifier (letters, numbers, and underscores only).
5. Return the compiled aggregate specification object.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_AGGREGATE_FUNCTION_UNKNOWN` | `Function` is not `COUNT`, `SUM`, `AVG`, `MIN`, or `MAX` |
| `XBASE_FILTER_FIELD_INVALID` | `Field` contains illegal characters or `*` used with non-`COUNT` function |

## Dependencies

- None — pure compilation step with no file access.
