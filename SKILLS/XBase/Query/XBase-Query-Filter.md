# XBase-Query-Filter

Compile and return a filter specification object for use with Record and Query skills. No file I/O occurs — this is a pure in-memory validation and compilation step.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Field` | string | yes | Column name to filter on |
| `Operator` | string | yes | One of: `=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL` |
| `Value` | any | no | Scalar value, or array for `IN` / `NOT IN`; omit for `IS NULL` / `IS NOT NULL` |
| `LogicalOperator` | string | no | `AND` or `OR` — how this filter chains when nested (default `AND`) |
| `Filters` | array | no | Array of nested filter objects for grouped expressions |

## Outputs

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
      { "Field": "Price",  "Operator": "<", "Value": 100    },
      { "Field": "Status", "Operator": "=", "Value": "Open" }
    ]
  }
}
```

## Steps

1. Validate `Field` is a safe identifier: letters, numbers, and underscores only (`^[A-Za-z0-9_]+$`); return `XBASE_FILTER_FIELD_INVALID` if it contains any other character.
2. Validate `Operator` is in the allowed set (`=`, `!=`, `<`, `<=`, `>`, `>=`, `LIKE`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`); return `XBASE_FILTER_OPERATOR_UNKNOWN` if not.
3. For `IS NULL` and `IS NOT NULL`: `Value` is not required; set it to `null` in the compiled output.
4. For `IN` and `NOT IN`: `Value` must be a non-empty array; return `XBASE_FILTER_VALUE_REQUIRED` if it is absent or empty.
5. For all other operators: `Value` must be present and non-null; return `XBASE_FILTER_VALUE_REQUIRED` if absent.
6. If `Filters` is provided: recursively validate each sub-filter object by applying steps 1–5 to each entry; at the parent level, set `Field`, `Operator`, and `Value` to `null` (the parent is a logical grouping node only).
7. Return the compiled filter specification object.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_FILTER_FIELD_INVALID` | `Field` contains characters outside letters, numbers, and underscores |
| `XBASE_FILTER_OPERATOR_UNKNOWN` | `Operator` is not in the allowed set |
| `XBASE_FILTER_VALUE_REQUIRED` | `Operator` requires a `Value` but none was supplied |

## Dependencies

- None — pure compilation step with no file access.
