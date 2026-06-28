# Ticketing System

A full-featured issue-tracking system implemented exclusively as AI Skills. Every read and write routes through XBase skills — the Ticketing System performs no direct file I/O of its own. Any AI agent or runtime that has the XBase skill set installed can run the Ticketing System without modification.

---

## Dependency on XBase

All Ticketing skills require an active XBase-Database-Connect session named "ticketing". The connection must be established before any Ticketing skill is invoked. All data access — reads, writes, queries, and transactions — routes through XBase-Record-*, XBase-Query-*, and XBase-Transaction-* skills.

---

## Data Model

| Table | Description |
|-------|-------------|
| Tickets | Core ticket records including summary, description, status, priority, category, reporter, assignee, and timestamps |
| Comments | Threaded comments per ticket, with soft-delete and author tracking |
| Attachments | File attachment metadata per ticket; stores path and filename but not file content |
| Statuses | Configurable status definitions; terminal statuses (IsTerminal = 1) trigger the COMPLETE display banner |
| StatusTransitions | Allowed FromStatus to ToStatus pairs; enforces the workflow graph |
| Priorities | Configurable priority levels with a numeric Weight for ordering; one row is marked IsDefault |
| Categories | Ticket category definitions |
| Tags | Free-text tags associated with tickets via a TicketTags join table |
| Users | Registered user accounts with hashed credentials and active/inactive flag |
| Sessions | Active authentication sessions with SessionToken and ExpiresAt |
| TicketHistory | Append-only audit log; every mutation to a ticket appends a row recording the action, actor, old value, new value, and timestamp |

### Ticket Numbers

Tickets are assigned sequential human-readable numbers: TKT-0001, TKT-0002, and so on. The sequence never resets and never reuses deleted numbers. It expands naturally beyond TKT-9999 to TKT-10000.

---

## Skill Groups

### Ticket (9 skills)

Ticketing-Ticket-Create, Ticketing-Ticket-Read, Ticketing-Ticket-Update, Ticketing-Ticket-Delete, Ticketing-Ticket-Close, Ticketing-Ticket-Reopen, Ticketing-Ticket-Assign, Ticketing-Ticket-Escalate, Ticketing-Ticket-Query.

Create opens a new ticket and inserts the first TicketHistory row. Close transitions the ticket to a terminal status, updates ClosedAt, and calls Ticketing-Display-Complete. Assign and Escalate call Ticketing-Display-Alert after committing their changes.

### Comment (4 skills)

Ticketing-Comment-Add, Ticketing-Comment-Read, Ticketing-Comment-Edit, Ticketing-Comment-Delete.

Comments are soft-deleted. Edit and Delete are restricted to the comment author or an administrator.

### Attachment (3 skills)

Ticketing-Attachment-Add, Ticketing-Attachment-Read, Ticketing-Attachment-Remove.

Attachments store file metadata only — path, filename, uploader, and timestamp. Actual file content is managed by the caller outside of this skill set.

### Status (2 skills)

Ticketing-Status-Define, Ticketing-Status-Transition.

Ticketing-Status-Define creates or updates a status definition. Ticketing-Status-Transition moves a ticket between statuses, validates the transition against the StatusTransitions table, appends a TicketHistory row, and calls Ticketing-Display-Complete when the destination status is terminal.

### Priority (2 skills)

Ticketing-Priority-Define, Ticketing-Priority-Set.

Ticketing-Priority-Define creates a priority level with a numeric Weight for ordering. Ticketing-Priority-Set changes a ticket's priority explicitly. Ticketing-Ticket-Escalate raises priority by one level.

### Category (4 skills)

Ticketing-Category-Create, Ticketing-Category-Assign, Ticketing-Tag-Add, Ticketing-Tag-Remove.

Categories are hierarchical. Tags are free-text strings stored in a many-to-many join table. Ticketing-Tag-Add is idempotent.

### User (5 skills)

Ticketing-User-Register, Ticketing-User-Read, Ticketing-User-Update, Ticketing-User-Deactivate, Ticketing-User-Authenticate.

User management stores credentials as a secure one-way hash. CredentialHash is never returned in any output. Deactivated users cannot be assigned tickets or post comments.

### Report (3 skills)

Ticketing-Report-Summary, Ticketing-Report-Generate, Ticketing-Report-Export.

Report-Summary returns aggregate counts by status, priority, and assignee. Report-Generate produces a full record set for a date range with configurable groupings. Report-Export serializes a report object to CSV or JSON and writes it to a file.

### Display (3 skills)

Ticketing-Display-Complete, Ticketing-Display-Alert, Ticketing-Display-Bell.

Display skills write text and BEL characters to stdout. They have no database access and do not call XBase skills. They are leaf skills called by Ticket and Status skills at specific lifecycle events.

### Session (1 skill)

Ticketing-Session drives a guided interactive ticketing session in the conversation. It presents a six-item main menu (My Tickets, Browse, New Ticket, Work Ticket, Reports, Exit), dispatches each selection to the appropriate Ticketing skill, renders results as markdown, and loops until the user exits. All file I/O is delegated to the underlying Ticketing and XBase skills — Ticketing-Session contains no direct data access of its own. Inputs: `ConnectionName`, `SessionToken`, `UserId`, and optional `DisplayName`. It makes all common ticketing workflows discoverable without knowing individual skill names or parameters.

---

## Authentication

Ticketing-User-Authenticate accepts a plaintext Password. The skill computes a secure one-way hash of the input and compares it to the stored CredentialHash — the plaintext value is never persisted or returned. On success, the skill generates a cryptographically random 64-character hex SessionToken, inserts a row into the Sessions table with an ExpiresAt value 24 hours in the future, and returns SessionToken, ExpiresAt, and UserId. On failure, TICKETING_AUTH_FAILED is returned regardless of whether the failure was a missing user, inactive user, or wrong credential.

---

## Display and Notification

Display skills write BEL characters and text banners to stdout. A BEL character is ASCII 7 (`\a`). When emitted to a terminal, the system produces an audible alert. The Display skills are terminal-agnostic: they make no assumptions about the terminal type, operating system, or runtime.

Ticketing-Display-Bell emits N BEL characters (max 10) to stdout, one at a time with a flush after each, so the user hears distinct rings. No banner or other text is produced.

Ticketing-Display-Alert emits BEL characters and then writes a compact two-line bordered banner identifying the event, ticket number, and a detail string. Used for assignment and escalation events.

Ticketing-Display-Complete emits BEL characters, writes a blank line, and then writes a full-width block-letter COMPLETE banner with ticket metadata (TicketNumber, Summary, ClosedAt, ClosedByDisplayName). Pass UseUnicode = false for a plain-ASCII fallback compatible with all terminals.

---

## Initialization Sequence

When setting up a fresh Ticketing database, call skills in this order:

1. XBase-Database-Initialize — create a database named "ticketing" in {DatabaseRoot}/ticketing/
2. XBase-Database-Connect — ConnectionName: "ticketing"
3. XBase-Schema-TableCreate — create all 11 tables listed in the Data Model section above
4. XBase-Index-Create — create indexes on Tickets.StatusId, Tickets.AssignedToUserId, and Tickets.CreatedAt at minimum
5. Ticketing-Status-Define — seed default statuses: Open (IsDefault = 1), In Progress, Blocked, Closed (IsTerminal = 1)
6. XBase-Record-Insert on StatusTransitions — populate allowed transition pairs
7. Ticketing-Priority-Define — seed: Low, Medium (IsDefault = 1), High, Critical
8. Ticketing-User-Register — create the first administrator user account

---

## Getting Started

This walkthrough covers the complete lifecycle of a ticket from a freshly-initialized database. It assumes initialization is already done (see Initialization Sequence above) and an XBase connection named `"ticketing"` is active.

### Step 1 — Authenticate

```
Ticketing-User-Authenticate
  Username: "admin"
  Password: "yourpassword"
```

Returns a `SessionToken` and `ExpiresAt` (24 hours from now). Keep the `SessionToken` — pass it to skills that require it for actor tracking. On failure the skill always returns `TICKETING_AUTH_FAILED` regardless of the specific reason (wrong password, inactive user, unknown user) to prevent enumeration.

### Step 2 — Create a ticket

```
Ticketing-Ticket-Create
  SessionToken: "<token>"
  Summary: "Login page crashes on iOS 17"
  Description: "Confirmed crash on iPhone 14 and 15 Pro running iOS 17.4. Steps: open app, tap Login."
  PriorityId: 2
  CategoryId: 1
```

Returns `TicketNumber: "TKT-0001"`. XBase assigns the sequential number, sets `StatusId` to the default status (the one with `IsDefault: 1`), sets `ReporterUserId` from the session token, and writes the first `TicketHistory` row with `Action: "CREATED"`.

### Step 3 — Add a comment

```
Ticketing-Comment-Add
  SessionToken: "<token>"
  TicketId: 1
  Body: "Reproduced on my iPhone 15. Happens consistently on the password autofill path."
```

Returns `CommentId: 1`. Comments are threaded per ticket and soft-deleted (never physically removed).

### Step 4 — Assign the ticket

```
Ticketing-Ticket-Assign
  SessionToken: "<token>"
  TicketId: 1
  AssignedToUserId: 2
```

Updates `AssignedToUserId` on the ticket, appends a `TicketHistory` row, and fires `Ticketing-Display-Alert` to notify the assignee.

### Step 5 — Transition status

```
Ticketing-Status-Transition
  SessionToken: "<token>"
  TicketId: 1
  ToStatusId: 2
```

Validates the transition against the `StatusTransitions` table. If the `FromStatus → ToStatus` pair is not registered, returns `TICKETING_STATUS_TRANSITION_INVALID`. On success, updates `StatusId`, appends a `TicketHistory` row, and fires `Ticketing-Display-Complete` if the destination status is terminal.

### Step 6 — Query the backlog

```
Ticketing-Ticket-Query
  Filters:
    - { Field: "StatusId", Operator: "=", Value: 1 }
  SortBy: "CreatedAt"
  SortDirection: "ASC"
  PageSize: 25
```

Returns a paged list with resolved `Status`, `Priority`, and `AssignedTo` display names joined from their lookup tables.

### Step 7 — Close the ticket

```
Ticketing-Ticket-Close
  SessionToken: "<token>"
  TicketId: 1
  ToStatusId: 4
```

Sets `ClosedAt` to now, transitions to the specified terminal status, appends a final `TicketHistory` row, and fires the `COMPLETE` banner via `Ticketing-Display-Complete`.

---

## Error Handling

Ticketing skill errors follow the pattern TICKETING_CATEGORY_REASON and are returned in the standard XBase error envelope:

```json
{
  "Success": false,
  "ErrorCode": "TICKETING_USER_NOT_FOUND",
  "Message": "No user exists with the given identifier.",
  "SkillName": "Ticketing-User-Read"
}
```

Key error codes used by the skills in this release:

| Code | Meaning |
|------|---------|
| TICKETING_USER_NOT_FOUND | No user with the given ID or username |
| TICKETING_USER_INACTIVE | User exists but is deactivated |
| TICKETING_USER_IDENTIFIER_REQUIRED | Neither UserId nor Username was provided |
| TICKETING_USER_USERNAME_DUPLICATE | Username is already registered |
| TICKETING_AUTH_FAILED | Credential comparison failed (deliberately generic) |
| TICKETING_TICKET_NOT_FOUND | No ticket with the given ID |
| TICKETING_STATUS_TRANSITION_INVALID | Transition not in the StatusTransitions table |
| TICKETING_COMMENT_NOT_FOUND | Comment ID not found or soft-deleted |
| TICKETING_REPORT_DATE_RANGE_INVALID | FromDate is after ToDate |
| TICKETING_REPORT_FORMAT_UNKNOWN | Export format is not CSV or JSON |
| TICKETING_DISPLAY_STDOUT_UNAVAILABLE | stdout cannot be written |
| TICKETING_DISPLAY_BELL_COUNT_EXCEEDED | BellCount or Count > 10 |

XBase error codes (XBASE_CONNECTION_INVALID, XBASE_TABLE_NOT_FOUND, etc.) propagate from the underlying XBase skill calls without modification.
