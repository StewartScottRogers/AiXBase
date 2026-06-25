# Ticketing-Display-Complete

Emit three terminal bell characters then render the full-screen ASCII art completion banner to stdout. Called automatically on ticket close and terminal status transitions.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `TicketNumber` | string | yes | — | e.g. `TKT-0042` |
| `Summary` | string | yes | — | Ticket summary line |
| `ClosedByDisplayName` | string | yes | — | Display name of the user who closed it |
| `ClosedAt` | string | yes | — | ISO-8601 timestamp |
| `BellCount` | int | no | `3` | Number of BEL characters to emit (max 10) |
| `UseUnicode` | bool | no | `true` | `true` = Unicode block art; `false` = plain-ASCII fallback |

## Outputs

```json
{
  "Success": true,
  "RenderedBanner": "<full banner text written to stdout>"
}
```

## Steps

1. Call `Ticketing-Display-Bell` with `Count = BellCount`
2. Write a blank line to stdout
3. Select the banner template based on `UseUnicode`
4. Interpolate `{TicketNumber}`, `{Summary}`, `{ClosedByDisplayName}`, `{ClosedAt}` into the template
5. Write the banner to stdout
6. Flush stdout
7. Return `RenderedBanner`

### Unicode Banner Template

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗     ║
║  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝     ║
║  ██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║        ║
║  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║        ║
║  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║        ║
║   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝        ║
║                                                                      ║
║  Ticket  : {TicketNumber}                                            ║
║  Summary : {Summary}                                                 ║
║  Closed  : {ClosedAt}                                                ║
║  By      : {ClosedByDisplayName}                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Plain-ASCII Fallback Template

```
+======================================================================+
|                                                                      |
|   #####   #####  #     # #####  #       #######  #####  #######    |
|  #     # #     # ##   ## #    # #       #       #     #    #        |
|  #       #     # # # # # #    # #       #       #          #        |
|  #       #     # #  #  # #####  #       #####    #####     #        |
|  #       #     # #     # #      #       #             #    #        |
|  #     # #     # #     # #      #       #       #     #    #        |
|   #####   #####  #     # #      ####### #######  #####     #        |
|                                                                      |
|  Ticket  : {TicketNumber}                                            |
|  Summary : {Summary}                                                 |
|  Closed  : {ClosedAt}                                                |
|  By      : {ClosedByDisplayName}                                     |
|                                                                      |
+======================================================================+
```

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_DISPLAY_STDOUT_UNAVAILABLE` | stdout cannot be written |
| `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED` | `BellCount` > 10 |

## Dependencies

- `Ticketing-Display-Bell`
