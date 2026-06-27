# Ticketing-Display-Complete

Emit BEL characters then render the full-screen ASCII art completion banner to stdout. Called automatically by Ticketing-Ticket-Close and Ticketing-Status-Transition on terminal status transitions.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| TicketNumber | string | yes | e.g. TKT-0042 |
| Summary | string | yes | Ticket summary line |
| ClosedByDisplayName | string | yes | Display name of the user who closed the ticket |
| ClosedAt | string | yes | ISO-8601 timestamp |
| BellCount | int | no | Number of BEL characters to emit, default 3, max 10 |
| UseUnicode | bool | no | true = Unicode box-drawing banner; false = plain-ASCII fallback (default: true) |

## Outputs

```json
{
  "Success": true,
  "RenderedBanner": "<full banner text written to stdout>"
}
```

### Unicode Banner Template (UseUnicode = true)

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

### Plain-ASCII Banner Template (UseUnicode = false)

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

## Steps

1. Validate BellCount ≤ 10; if exceeded, return TICKETING_DISPLAY_BELL_COUNT_EXCEEDED.
2. Call Ticketing-Display-Bell with Count = BellCount to emit BEL characters (ASCII 7, `\a`) to stdout one at a time, flushing after each.
3. Write a blank line to stdout.
4. Select the banner template based on UseUnicode: if true, use the Unicode template; if false, use the plain-ASCII template.
5. Interpolate {TicketNumber}, {Summary}, {ClosedByDisplayName}, and {ClosedAt} in the template.
6. Write the rendered banner to stdout.
7. Flush stdout.
8. Return RenderedBanner containing the full text written to stdout.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_DISPLAY_STDOUT_UNAVAILABLE | stdout cannot be written |
| TICKETING_DISPLAY_BELL_COUNT_EXCEEDED | BellCount > 10 |

## Dependencies

- Ticketing-Display-Bell
