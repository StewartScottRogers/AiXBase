# XBase-Query-Aggregate

Build an aggregate specification object for use with `XBase-Record-Select` or
`XBase-Query-Execute`. No file I/O occurs — pure compilation. Aggregation is evaluated
in memory against the matched row set by the executing skill.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Aggregates` | array | yes | — | Array of aggregate definition objects (see below) |
| `GroupBy` | array | no | `[]` | Column names to group rows by before aggregating |

### Aggregate Definition Object

| Field | Type | Required | Description |
|---|---|---|---|
| `Function` | string | yes | `COUNT`, `SUM`, `AVG`, `MIN`, or `MAX` |
| `Column` | string | yes | Column to aggregate (`*` allowed for `COUNT`) |
| `Alias` | string | no | Output field name in the result row |

## Outputs

```json
{
  "Success": true,
  "Aggregate": {
    "Functions": [
      { "Function": "COUNT", "Column": "*",      "Alias": "Total"    },
      { "Function": "AVG",   "Column": "Price",  "Alias": "AvgPrice" }
    ],
    "GroupBy": ["StatusName"]
  }
}
```

## Steps

1. Validate each `Function` is one of `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`; return `XBASE_AGGREGATE_FUNCTION_UNKNOWN` on failure
2. Validate each `Column` name — alphanumeric + underscore, or `*` for `COUNT` only
3. Validate each `GroupBy` name — alphanumeric + underscore only
4. Default `Alias` to `{Function}_{Column}` if not supplied (e.g. `COUNT_*` → `Count`, `SUM_Price` → `SumPrice`)
5. Return the compiled aggregate specification object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_AGGREGATE_FUNCTION_UNKNOWN` | Function not in the allowed set |

## Dependencies

None — pure compilation, no file access. Execution is performed by `XBase-Record-Select`
or `XBase-Query-Execute`.
