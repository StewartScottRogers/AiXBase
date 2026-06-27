# Ticketing-Display-Bell

Emit N BEL characters (ASCII 7, `\a`) to stdout. No banner, no other output.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Count | int | no | Number of BEL characters to emit, default 1, max 10 |

## Outputs

```json
{
  "Success": true,
  "EmittedCount": 1
}
```

## Steps

1. Validate Count is between 1 and 10 inclusive; if Count > 10, return TICKETING_DISPLAY_BELL_COUNT_EXCEEDED.
2. Emit exactly Count BEL characters (ASCII 7, `\a`) to stdout, one at a time, flushing stdout after each emission so the user hears distinct rings rather than a single burst.
3. Return EmittedCount = Count.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_DISPLAY_BELL_COUNT_EXCEEDED | Count > 10 |
| TICKETING_DISPLAY_STDOUT_UNAVAILABLE | stdout is not writable |

## Dependencies

- None — this is a leaf skill with no database or other skill calls.
