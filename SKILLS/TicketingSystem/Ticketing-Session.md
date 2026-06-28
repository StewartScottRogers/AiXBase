# Ticketing-Session

Run an interactive guided ticketing session. Presents a text menu in the conversation, accepts a selection, executes the corresponding Ticketing skill, displays the result, and loops until the user exits. No file I/O occurs in this skill directly — all operations delegate to the underlying Ticketing and XBase skills.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ConnectionName` | string | yes | Active XBase connection alias for the ticketing database |
| `SessionToken` | string | yes | Active session token from `Ticketing-User-Authenticate` |
| `UserId` | int | yes | User ID of the authenticated caller |
| `DisplayName` | string | no | Human-readable name shown in the header; falls back to `UserId` if omitted |

## Outputs

The skill produces no structured JSON output. All interaction is conversational: menus are rendered as markdown, results are displayed inline, and the session ends when the user selects Exit or types `q` / `quit` / `exit`.

## Steps

1. Validate that `ConnectionName` is registered in the current session; if not, return `TICKETING_CONNECTION_INVALID`.
2. Validate that `SessionToken` is present and non-empty; if not, return `TICKETING_SESSION_INVALID`.
3. Set `HeaderUser` to `DisplayName` if supplied, otherwise `UserId`.
4. Display the main menu:

   ```
   ═══════════════════════════════════════════════
    Ticketing  ·  <ConnectionName>  ·  <HeaderUser>
   ═══════════════════════════════════════════════
    1  My Tickets   — open tickets assigned to me
    2  Browse       — search with optional filters
    3  New Ticket   — create a ticket
    4  Work Ticket  — view, comment, transition
    5  Reports      — summary and export
    6  Exit
   ═══════════════════════════════════════════════
   Select [1-6]:
   ```

5. Wait for user input. Normalize: strip whitespace, map `q`/`quit`/`exit` to `6`.
6. Dispatch on the selection:

   **Selection 1 — My Tickets:**
   a. Call `Ticketing-Ticket-Query` with `ConnectionName`, `SessionToken`, and a filter `AssignedToUserId = UserId`; exclude tickets whose status is terminal (`IsTerminal = 1`); sort by `UpdatedAt DESC`; `PageSize: 25`.
   b. If `TotalCount = 0`, display `No open tickets assigned to you.`
   c. Otherwise render a markdown table with columns: `Ticket | Status | Priority | Summary`.
   d. If `TotalCount > 25`, display `Showing 25 of <TotalCount>. Use Browse to paginate.`
   e. Return to the main menu (step 4).

   **Selection 2 — Browse:**
   a. Display a sub-prompt:
      ```
       Filter by status? Enter name or press Enter for all:
      ```
   b. If the user provides a status name, look up its `StatusId` from the Statuses table; if not found, display `Unknown status — showing all tickets.`
   c. Prompt: `Page number [1]:` — default to 1 on empty input.
   d. Call `Ticketing-Ticket-Query` with `ConnectionName`, `SessionToken`, and any status filter; `SortBy: CreatedAt`, `SortDirection: DESC`, `PageSize: 25`, `Page` from input.
   e. Render a markdown table: `Ticket | Status | Priority | Assigned To | Summary`.
   f. Display `Page <N> of <TotalPages> — <TotalCount> total tickets.`
   g. Return to the main menu (step 4).

   **Selection 3 — New Ticket:**
   a. Prompt: `Summary (required):` — if empty, display `Summary is required.` and re-prompt up to 3 times; if still empty, return to the main menu.
   b. Prompt: `Description (optional, Enter to skip):` — accept any string; default to empty.
   c. Display the available priorities (read from the Priorities table: Id and Name) and prompt: `Priority ID [Enter for default]:` — default to the row where `IsDefault = 1` on empty input; if the user enters a value, validate it exists in the Priorities table.
   d. Call `Ticketing-Ticket-Create` with `ConnectionName`, `SessionToken`, `Summary`, `Description` (if provided), `ReportedByUserId: UserId`, and `PriorityId`.
   e. Display `Created: <TicketNumber>`.
   f. Return to the main menu (step 4).

   **Selection 4 — Work Ticket:**
   a. Prompt: `Ticket number or ID (e.g. TKT-0010 or 10):` — accept either format; normalize a bare integer to `TKT-<zero-padded>`.
   b. Call `Ticketing-Ticket-Read` with `ConnectionName` and the resolved ticket identifier.
   c. If `TICKETING_TICKET_NOT_FOUND`, display `Ticket not found.` and return to the main menu.
   d. Display the ticket details as a markdown block:
      - Header: `# <TicketNumber> — <Summary>`
      - Fields table: Status, Priority, Reporter, Assigned To, Created, Updated, Closed (if set).
      - Description block (if present).
      - Comments section: for each comment, `**<AuthorDisplayName>** (<CreatedAt>): <Body>`.
   e. Display the work sub-menu:
      ```
       a  Add comment
       b  Transition status
       c  Assign to user
       d  Back
      ```
   f. Wait for sub-menu input. Dispatch:
      - **a — Add comment:** Prompt `Comment:`. Call `Ticketing-Comment-Add` with `ConnectionName`, `SessionToken`, `TicketId`, and `Body`. Display `Comment added.`. Return to sub-menu (step 6d-e).
      - **b — Transition status:** Display available statuses. Prompt `To status ID:`. Call `Ticketing-Status-Transition` with `ConnectionName`, `SessionToken`, `TicketId`, and `ToStatusId`. Display the new status or the error code if the transition is invalid. Return to sub-menu (step 6d-e).
      - **c — Assign:** Prompt `Assign to user ID:`. Call `Ticketing-Ticket-Assign` with `ConnectionName`, `SessionToken`, `TicketId`, and `AssignedToUserId`. Display `Assigned.` or the error. Return to sub-menu (step 6d-e).
      - **d — Back:** Return to the main menu (step 4).
      - Unrecognized: display `Enter a, b, c, or d.` and re-display the sub-menu.

   **Selection 5 — Reports:**
   a. Call `Ticketing-Report-Summary` with `ConnectionName` and `SessionToken`.
   b. Display the summary as a markdown table: by status (Name, Count) and by priority (Name, Count).
   c. Prompt: `Export report? [y/N]:` — default to N.
   d. If yes: prompt `Format [csv/json]:` — validate; prompt `Output file path:`; call `Ticketing-Report-Export` with the chosen format and path. Display `Exported to <path>.`
   e. Return to the main menu (step 4).

   **Selection 6 — Exit:**
   a. Display `Session ended.` and return.

   **Unrecognized input:**
   a. Display `Unrecognized selection. Please enter 1–6.` and re-display the main menu (step 4).

## Error Codes

| Code | Meaning |
|------|---------|
| `TICKETING_CONNECTION_INVALID` | `ConnectionName` is not registered in the current session |
| `TICKETING_SESSION_INVALID` | `SessionToken` is missing or empty |

## Dependencies

- `Ticketing-Ticket-Query`
- `Ticketing-Ticket-Create`
- `Ticketing-Ticket-Read`
- `Ticketing-Comment-Add`
- `Ticketing-Status-Transition`
- `Ticketing-Ticket-Assign`
- `Ticketing-Report-Summary`
- `Ticketing-Report-Export`
