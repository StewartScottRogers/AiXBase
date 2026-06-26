# XBase-Query-Filter

Build a filter specification object for use with Record and Query skills. No file I/O
occurs — this is a pure in-memory compilation step. The resulting object is evaluated
row-by-row against parsed NDJSON data by the executing skill.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Field` | string | yes | — | Column name to filter on |
| `Operator` | string | yes | — | One of: `=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL` |
| `Value` | any | no | — | Scalar value, or array for `IN` / `NOT IN` |
| `LogicalOperator` | string | no | `AND` | `AND` or `OR` — how this filter chains when nested |
| `Filters` | array | no | — | Nested filter objects for grouped expressions |

## Outputs

Returns a compiled filter specification object (not a SQL string) passed directly to
`XBase-Record-Select`, `XBase-Record-Update`, `XBase-Record-Delete`, or `XBase-Query-Execute`.

```json
{
  "Success": true,
  "Filter": {
    "Field": "Price",
    "Operator": "<",
    "Value": 15,
    "LogicalOperator": "AND"
  }
}
```

Nested filter example:

```json
{
  "Success": true,
  "Filter": {
    "LogicalOperator": "AND",
    "Filters": [
      { "Field": "Price",  "Operator": "<",  "Value": 100     },
      { "Field": "Status", "Operator": "=",  "Value": "Open"  }
    ]
  }
}
```

## Steps

1. Validate `Field` name — alphanumeric + underscore only (`^[A-Za-z0-9_]+$`); return `XBASE_FILTER_FIELD_INVALID` if invalid
2. Validate `Operator` is in the allowed set; return `XBASE_FILTER_OPERATOR_UNKNOWN` if not
3. For `IS NULL` / `IS NOT NULL`: ignore `Value`; set it to `null` in the output
4. For `IN` / `NOT IN`: `Value` must be a non-empty array; return `XBASE_FILTER_VALUE_REQUIRED` if not
5. For all other operators: `Value` must be provided; return `XBASE_FILTER_VALUE_REQUIRED` if absent
6. If `Filters` array is provided: recursively validate each sub-filter; `Field` / `Operator` / `Value` are set to `null` at the parent level
7. Return the compiled filter specification object

## Error Codes

| Code | Condition |
|---|---|
| `XBASE_FILTER_FIELD_INVALID` | Field name contains illegal characters |
| `XBASE_FILTER_OPERATOR_UNKNOWN` | Operator not in the allowed set |
| `XBASE_FILTER_VALUE_REQUIRED` | Operator requires a value but none provided |

## Dependencies

None — pure compilation step with no file access.
