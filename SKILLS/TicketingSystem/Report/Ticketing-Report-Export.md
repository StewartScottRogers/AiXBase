# Ticketing-Report-Export

Write a generated report to a file in CSV or JSON format.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Report` | object | yes | — | Output from `Ticketing-Report-Generate` |
| `Format` | string | no | `JSON` | `JSON` or `CSV` |
| `OutputPath` | string | no | — | File path relative to `AiXBase/reports/`; auto-generated if omitted |

## Outputs

```json
{
  "Success": true,
  "OutputPath": "AiXBase/reports/report_20260625T143201.json",
  "Format": "JSON",
  "ExportedAt": "<ISO-8601>"
}
```

## Steps

1. Ensure `AiXBase/reports/` directory exists
2. If `OutputPath` omitted, generate filename: `report_<YYYYMMDDTHHmmss>.<ext>`
3. Serialize `Report` to the requested format:
   - JSON: pretty-printed with 2-space indent
   - CSV: one row per ticket in `Report.Tickets`, headers on first row
4. Write to `OutputPath`
5. Return `OutputPath`, `Format`, `ExportedAt`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_REPORT_FORMAT_UNKNOWN` | `Format` is not `JSON` or `CSV` |
| `TICKETING_REPORT_IO_ERROR` | File system error writing the output |

## Dependencies

- `Ticketing-Report-Generate` — must be called first to produce the `Report` input
