# Ticketing-Display-Bell

Emit N ASCII BEL characters (code 7, `\a`) to stdout. No banner, no other output.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Count` | int | no | `1` | Number of BEL characters to emit. Max `10`. |

## Outputs

```json
{
  "Success": true,
  "EmittedCount": 3
}
```

## Steps

1. Validate `Count` is between 1 and 10 inclusive
2. Loop `Count` times: write a single `\a` character (ASCII 7) to stdout — `Console.Write('\a')`
3. Each write is synchronous so the user hears distinct rings rather than a single burst
4. Return `EmittedCount`

## Implementation Note

In .NET: `Console.Write('\a')` per iteration.
In terminal escape sequences: `\007` or `\x07`.
Do **not** use `Console.Beep()` — it blocks the thread for the beep duration and is not supported on all platforms.

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED` | `Count` > 10 |
| `TICKETING_DISPLAY_STDOUT_UNAVAILABLE` | stdout is not writable |

## Dependencies

None — this is a leaf skill with no database or other skill calls.
