# Ticketing-Report-Export

Write a generated report to a file in CSV or JSON format.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Report | object | yes | Output from Ticketing-Report-Generate or Ticketing-Report-Summary |
| Format | string | no | Output format: CSV or JSON (default: JSON) |
| OutputPath | string | yes | File path to write the report; e.g. {DatabaseRoot}/reports/report.json |

## Outputs

```json
{
  "Success": true,
  "OutputPath": "{DatabaseRoot}/reports/report_20260627T100000.json",
  "Format": "JSON",
  "WrittenAt": "2026-06-27T10:00:00Z",
  "RowCount": 42
}
```

## Steps

1. Validate Format is CSV or JSON; if not, return TICKETING_REPORT_FORMAT_UNKNOWN.
2. If Format is JSON, serialize Report to JSON text.
3. If Format is CSV, serialize Report.Tickets to comma-separated text with a header row; set RowCount to the number of ticket rows written.
4. Write the serialized content to OutputPath.
5. Return OutputPath, Format, WrittenAt = now(), and RowCount.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_REPORT_FORMAT_UNKNOWN | Format is not CSV or JSON |

## Dependencies

- Ticketing-Report-Generate (or Ticketing-Report-Summary — must be called first to produce the Report input)
