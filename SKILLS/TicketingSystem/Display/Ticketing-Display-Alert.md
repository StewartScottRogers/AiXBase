# Ticketing-Display-Alert

Emit BEL characters then render a compact alert banner to stdout. Used for ticket assignment and escalation events.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Event | string | yes | Event label, e.g. TICKET ASSIGNED, TICKET ESCALATED |
| TicketNumber | string | yes | e.g. TKT-0042 |
| Detail | string | yes | One line of context, e.g. Assigned to: Alice |
| BellCount | int | no | Number of BEL characters to emit, default 1, max 10 |
| UseUnicode | bool | no | true = Unicode borders; false = plain-ASCII (default: true) |

## Outputs

```json
{
  "Success": true,
  "RenderedBanner": "<compact alert banner text>"
}
```

### Unicode Alert Template (UseUnicode = true)

```
╔══════════════════════════════════════════════╗
║  *** {Event} ***                             ║
║  {TicketNumber}  {Detail}                    ║
╚══════════════════════════════════════════════╝
```

### Plain-ASCII Alert Template (UseUnicode = false)

```
+------------------------------------------------+
|  *** {Event} ***                               |
|  {TicketNumber}  {Detail}                      |
+------------------------------------------------+
```

## Steps

1. Validate BellCount ≤ 10; if exceeded, return TICKETING_DISPLAY_BELL_COUNT_EXCEEDED.
2. Call Ticketing-Display-Bell with Count = BellCount to emit BEL characters (ASCII 7, `\a`) to stdout.
3. Select the alert template based on UseUnicode: if true, use the Unicode template; if false, use the plain-ASCII template.
4. Interpolate {Event}, {TicketNumber}, and {Detail} in the template.
5. Write the rendered banner to stdout and flush.
6. Return RenderedBanner containing the full text written to stdout.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_DISPLAY_STDOUT_UNAVAILABLE | stdout cannot be written |
| TICKETING_DISPLAY_BELL_COUNT_EXCEEDED | BellCount > 10 |

## Dependencies

- Ticketing-Display-Bell
