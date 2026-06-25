# Ticketing-Display-Alert

Emit one terminal bell character then render a compact alert banner to stdout. Used for assignment and escalation events.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Event` | string | yes | — | Event label, e.g. `TICKET ASSIGNED`, `TICKET ESCALATED` |
| `TicketNumber` | string | yes | — | e.g. `TKT-0042` |
| `Detail` | string | yes | — | One line of context, e.g. `Assigned to: Bob` |
| `BellCount` | int | no | `1` | Number of BEL characters to emit (max 10) |
| `UseUnicode` | bool | no | `true` | `true` = Unicode borders; `false` = plain-ASCII |

## Outputs

```json
{
  "Success": true,
  "RenderedBanner": "<compact banner text>"
}
```

## Steps

1. Call `Ticketing-Display-Bell` with `Count = BellCount`
2. Select the alert template based on `UseUnicode`
3. Interpolate `{Event}`, `{TicketNumber}`, `{Detail}`
4. Write to stdout and flush
5. Return `RenderedBanner`

### Unicode Alert Template

```
╔══════════════════════════════════════════════╗
║  *** {Event} ***                             ║
║  {TicketNumber}  {Detail}                    ║
╚══════════════════════════════════════════════╝
```

### Plain-ASCII Alert Template

```
+------------------------------------------------+
|  *** {Event} ***                               |
|  {TicketNumber}  {Detail}                      |
+------------------------------------------------+
```

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_DISPLAY_STDOUT_UNAVAILABLE` | stdout cannot be written |
| `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED` | `BellCount` > 10 |

## Dependencies

- `Ticketing-Display-Bell`
