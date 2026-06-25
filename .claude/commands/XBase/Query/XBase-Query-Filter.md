# XBase-Query-Filter

Build a parameterized WHERE clause expression for use with Record skills.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Field` | string | yes | — | Column name to filter on |
| `Operator` | string | yes | — | One of: `=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL` |
| `Value` | any | no | — | Scalar value, or array for `IN` / `NOT IN` |
| `LogicalOperator` | string | no | `AND` | `AND` or `OR` — how this filter chains with others |
| `Filters` | array | no | — | Nested array of filter objects for grouped expressions |

## Outputs

Returns a compiled filter object (not SQL text) passed directly into `XBase-Record-Select`, `XBase-Record-Update`, or `XBase-Record-Delete`.

```json
{
  "Success": true,
  "Filter": {
    "sql": "Field = ? AND IsDeleted = 0",
    "parameters": ["value"]
  }
}
```

## Steps

1. Validate `Field` name (alphanumeric + underscore only)
2. Validate `Operator` is in the allowed set
3. For `IS NULL` / `IS NOT NULL`, `Value` is ignored
4. For `IN` / `NOT IN`, `Value` must be an array
5. Build the parameterized SQL fragment and parameter list
6. If `Filters` array is provided, combine each sub-filter with the specified `LogicalOperator`
7. Return the compiled filter object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_FILTER_FIELD_INVALID` | Field name contains illegal characters |
| `XBASE_FILTER_OPERATOR_UNKNOWN` | Operator not in the allowed set |
| `XBASE_FILTER_VALUE_REQUIRED` | Operator requires a value but none provided |

## Dependencies

None — this is a pure compilation step with no database access.
