# Product Requirements Document: Ticketing System

## Overview

The Ticketing System is a full-featured issue-tracking feature implemented exclusively through AI Skills. It has **no direct database access** — every read and write routes through XBase Skills. All Ticketing Skills follow the same naming convention:

```
[Feature Name]-[Feature-Operation]-[Any Subdivision Needed]
```

Example: `Ticketing-Ticket-Create`, `Ticketing-Comment-Edit`

**Dependency**: All Ticketing Skills require an active `XBase-Database-Connect` session named `ticketing`. The Ticketing System is harness-agnostic and system-agnostic: any AI agent or runtime that can invoke the XBase skill set and write BEL characters and text to stdout can run the Ticketing System without modification.

---

## Skill Catalog

### Ticket Lifecycle

| Skill | Description |
|---|---|
| `Ticketing-Ticket-Create` | Open a new ticket |
| `Ticketing-Ticket-Read` | Fetch a single ticket by ID |
| `Ticketing-Ticket-Update` | Edit summary, description, or metadata of a ticket |
| `Ticketing-Ticket-Delete` | Soft-delete a ticket (sets `IsDeleted = 1`) |
| `Ticketing-Ticket-Close` | Transition ticket to the `Closed` status |
| `Ticketing-Ticket-Reopen` | Transition a closed ticket back to `Open` |
| `Ticketing-Ticket-Assign` | Assign or reassign the ticket owner |
| `Ticketing-Ticket-Escalate` | Raise priority and notify assigned user |
| `Ticketing-Ticket-Query` | Search tickets with filter, sort, and pagination |

### Comment Operations

| Skill | Description |
|---|---|
| `Ticketing-Comment-Add` | Append a comment to a ticket |
| `Ticketing-Comment-Read` | Fetch one or all comments on a ticket |
| `Ticketing-Comment-Edit` | Update the body of an existing comment |
| `Ticketing-Comment-Delete` | Soft-delete a comment |

### Attachment Operations

| Skill | Description |
|---|---|
| `Ticketing-Attachment-Add` | Associate a file reference with a ticket |
| `Ticketing-Attachment-Read` | List or fetch attachment metadata |
| `Ticketing-Attachment-Remove` | Soft-delete an attachment reference |

### Status Workflow

| Skill | Description |
|---|---|
| `Ticketing-Status-Define` | Create a named status (e.g., Open, In Progress, Closed) |
| `Ticketing-Status-Transition` | Move a ticket from one status to another, validating allowed transitions |

### Priority Management

| Skill | Description |
|---|---|
| `Ticketing-Priority-Define` | Create a named priority level with an ordinal weight |
| `Ticketing-Priority-Set` | Set or change the priority of a ticket |

### Category and Tagging

| Skill | Description |
|---|---|
| `Ticketing-Category-Create` | Define a category (e.g., Bug, Feature, Question) |
| `Ticketing-Category-Assign` | Assign a category to a ticket |
| `Ticketing-Tag-Add` | Add a free-text tag to a ticket |
| `Ticketing-Tag-Remove` | Remove a tag from a ticket |

### User Management

| Skill | Description |
|---|---|
| `Ticketing-User-Register` | Create a user account in the ticketing store |
| `Ticketing-User-Read` | Fetch user profile by ID or username |
| `Ticketing-User-Update` | Modify user display name or email |
| `Ticketing-User-Deactivate` | Mark a user inactive (cannot own tickets) |
| `Ticketing-User-Authenticate` | Verify username and credential, return session token |

### Reporting

| Skill | Description |
|---|---|
| `Ticketing-Report-Summary` | Aggregate counts by status, priority, and assignee |
| `Ticketing-Report-Generate` | Produce a full report for a date range |
| `Ticketing-Report-Export` | Write report output to a file (CSV or JSON) |

### Display and Notification

| Skill | Description |
|---|---|
| `Ticketing-Display-Complete` | Emit BEL × 3 then render the full completion ASCII art banner to stdout |
| `Ticketing-Display-Alert` | Emit BEL × 1 then render a compact alert banner for assignment or escalation events |
| `Ticketing-Display-Bell` | Emit N BEL characters (ASCII 7, `\a`) to stdout — no banner |

---

## Skill Specifications

### Ticketing-Ticket-Create

**XBase Skills Called**
- `XBase-Transaction-Begin`
- `XBase-Record-Insert` (table: `Tickets`)
- `XBase-Record-Insert` (table: `TicketHistory`, action: `Created`)
- `XBase-Transaction-Commit`

**Inputs**
- `Summary` (string, required, max 200 chars)
- `Description` (string, optional)
- `ReportedByUserId` (int, required)
- `AssignedToUserId` (int, optional)
- `CategoryId` (int, optional)
- `PriorityId` (int, optional, defaults to system default priority)
- `Tags` (array of strings, optional)

**Outputs**
- `TicketId` (int)
- `TicketNumber` (string) — human-readable key, e.g. `TKT-0001`
- `CreatedAt` (ISO-8601)

---

### Ticketing-Ticket-Query

**XBase Skills Called**
- `XBase-Record-Select` (table: `Tickets`)
- `XBase-Query-Filter` (zero or more)
- `XBase-Query-Sort`
- `XBase-Query-Join` (with `Users`, `Statuses`, `Priorities` as needed)

**Inputs**
- `Filters` (array of `{ Field, Operator, Value }`)
- `SortBy` (string, default `CreatedAt`)
- `SortDirection` (`ASC` | `DESC`, default `DESC`)
- `Page` (int, default 1)
- `PageSize` (int, default 25, max 200)

**Outputs**
- `Tickets` (array of ticket summary objects)
- `TotalCount` (int)
- `Page` (int)
- `PageSize` (int)

---

### Ticketing-Ticket-Close

**XBase Skills Called**
- `XBase-Record-Select` (table: `Statuses`, find row where `IsTerminal = 1` and `Name = 'Closed'`)
- `Ticketing-Status-Transition` (to terminal `Closed` status)
- `XBase-Record-Update` (table: `Tickets`, set `ClosedAt`)

**Display Skills Called** (after successful commit)
- `Ticketing-Display-Complete`

**Inputs**
- `TicketId` (int)
- `ClosedByUserId` (int)
- `Comment` (string, optional) — closing note appended to history

**Outputs**
- `TicketId` (int)
- `TicketNumber` (string)
- `ClosedAt` (ISO-8601)

---

### Ticketing-Status-Transition

**XBase Skills Called**
- `XBase-Record-Select` (validate allowed transition exists in `StatusTransitions`)
- `XBase-Transaction-Begin`
- `XBase-Record-Update` (table: `Tickets`, set `StatusId`)
- `XBase-Record-Insert` (table: `TicketHistory`, action: `StatusChanged`)
- `XBase-Transaction-Commit`

**Display Skills Called** (after successful commit, only when `ToStatus.IsTerminal = 1`)
- `Ticketing-Display-Complete`

**Inputs**
- `TicketId` (int)
- `ToStatusId` (int)
- `ChangedByUserId` (int)
- `Comment` (string, optional)

**Behavior**
Rejects the transition if no matching row in `StatusTransitions(FromStatusId, ToStatusId)` exists, unless the user has admin role. When the destination status is terminal (`IsTerminal = 1`), calls `Ticketing-Display-Complete` after the commit.

---

### Ticketing-User-Authenticate

**XBase Skills Called**
- `XBase-Record-Select` (table: `Users`, filter by `Username`)
- `XBase-Record-Insert` (table: `Sessions`)

**Inputs**
- `Username` (string)
- `Password` (string) — plaintext; the skill hashes it internally using a secure hash function and compares against the stored hash; the plaintext password is never persisted or returned

**Outputs**
- `SessionToken` (string, 64-char hex)
- `ExpiresAt` (ISO-8601)
- `UserId` (int)

---

### Ticketing-Report-Generate

**XBase Skills Called**
- `XBase-Query-Aggregate` (multiple: counts by status, priority, assignee)
- `XBase-Record-Select` (table: `Tickets`, filtered by date range)
- `XBase-Query-Join` (with `Users`, `Statuses`, `Priorities`)

**Inputs**
- `FromDate` (ISO-8601 date)
- `ToDate` (ISO-8601 date)
- `GroupBy` (array: `Status` | `Priority` | `Assignee` | `Category`)

**Outputs**
- `Summary` (object with aggregates per grouping)
- `Tickets` (array, full detail within date range)
- `GeneratedAt` (ISO-8601)

---

### Ticketing-Display-Complete

Renders a full-screen ASCII art completion banner and rings the terminal bell three times. Called automatically by `Ticketing-Ticket-Close` and `Ticketing-Status-Transition` (terminal states only).

**Inputs**
- `TicketNumber` (string) — e.g. `TKT-0042`
- `Summary` (string)
- `ClosedByDisplayName` (string)
- `ClosedAt` (ISO-8601)
- `BellCount` (int, default `3`)
- `UseUnicode` (bool, default `true`) — `false` emits the plain-ASCII fallback banner

**Outputs**
- `RenderedBanner` (string) — the full text written to stdout

**Behavior**
1. Emit `BellCount` × BEL character (ASCII 7) to stdout — one character per ring, written sequentially so the user hears distinct rings
2. Write a blank line to stdout
3. Write the banner (see templates below) to stdout with `TicketNumber`, `Summary`, `ClosedByDisplayName`, and `ClosedAt` interpolated
4. Flush stdout

---

### Ticketing-Display-Alert

Renders a compact single-line-border alert banner and rings the bell once. Called by `Ticketing-Ticket-Assign` and `Ticketing-Ticket-Escalate`.

**Inputs**
- `Event` (string) — e.g. `TICKET ASSIGNED`, `TICKET ESCALATED`
- `TicketNumber` (string)
- `Detail` (string) — one line of context, e.g. assigned-to name or new priority
- `BellCount` (int, default `1`)
- `UseUnicode` (bool, default `true`)

**Outputs**
- `RenderedBanner` (string)

**Behavior**
1. Emit `BellCount` × BEL character (ASCII 7) to stdout
2. Render the compact alert template (see below) to stdout
3. Flush stdout

---

### Ticketing-Display-Bell

Emits BEL characters only — no banner, no output beyond the control characters.

**Inputs**
- `Count` (int, default `1`, max `10`)

**Outputs**
- `EmittedCount` (int)

**Behavior**
Emit exactly `Count` BEL characters (ASCII 7) to stdout, one at a time, flushing after each so the user hears distinct rings rather than a burst. No other output is produced.

---

## Display Templates

### Completion Banner — Unicode (UseUnicode = true)

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

### Completion Banner — Plain ASCII (UseUnicode = false)

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

### Alert Banner — Unicode (UseUnicode = true)

```
╔══════════════════════════════════════════════╗
║  *** {Event} ***                             ║
║  {TicketNumber}  {Detail}                    ║
╚══════════════════════════════════════════════╝
```

### Alert Banner — Plain ASCII (UseUnicode = false)

```
+------------------------------------------------+
|  *** {Event} ***                               |
|  {TicketNumber}  {Detail}                      |
+------------------------------------------------+
```

---

## Data Model

### Tables

**Tickets**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | Auto-increment |
| `TicketNumber` | TEXT UNIQUE | e.g. `TKT-0001` |
| `Summary` | TEXT NOT NULL | |
| `Description` | TEXT | |
| `StatusId` | INTEGER FK | → `Statuses.Id` |
| `PriorityId` | INTEGER FK | → `Priorities.Id` |
| `CategoryId` | INTEGER FK | → `Categories.Id` |
| `ReportedByUserId` | INTEGER FK | → `Users.Id` |
| `AssignedToUserId` | INTEGER FK | → `Users.Id` |
| `CreatedAt` | TEXT | ISO-8601 |
| `UpdatedAt` | TEXT | ISO-8601 |
| `ClosedAt` | TEXT | ISO-8601, nullable |
| `IsDeleted` | INTEGER | 0/1 |

**Comments**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | |
| `TicketId` | INTEGER FK | → `Tickets.Id` |
| `AuthorUserId` | INTEGER FK | → `Users.Id` |
| `Body` | TEXT NOT NULL | |
| `CreatedAt` | TEXT | |
| `UpdatedAt` | TEXT | |
| `IsDeleted` | INTEGER | |

**Statuses**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | |
| `Name` | TEXT UNIQUE | e.g. `Open`, `In Progress`, `Closed` |
| `IsTerminal` | INTEGER | 1 = closed state |

**StatusTransitions**

| Column | Type | Notes |
|---|---|---|
| `FromStatusId` | INTEGER FK | |
| `ToStatusId` | INTEGER FK | |

**Priorities**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | |
| `Name` | TEXT UNIQUE | e.g. `Low`, `Medium`, `High`, `Critical` |
| `Weight` | INTEGER | Lower = higher urgency |
| `IsDefault` | INTEGER | 1 for one row |

**Users**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | |
| `Username` | TEXT UNIQUE NOT NULL | |
| `DisplayName` | TEXT | |
| `Email` | TEXT | |
| `CredentialHash` | TEXT | |
| `IsActive` | INTEGER | 0/1 |
| `CreatedAt` | TEXT | |

**TicketHistory**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | |
| `TicketId` | INTEGER FK | |
| `ChangedByUserId` | INTEGER FK | |
| `Action` | TEXT | e.g. `Created`, `StatusChanged`, `Assigned` |
| `FromValue` | TEXT | nullable |
| `ToValue` | TEXT | nullable |
| `ChangedAt` | TEXT | ISO-8601 |

**Attachments**

| Column | Type | Notes |
|---|---|---|
| `Id` | INTEGER PK | |
| `TicketId` | INTEGER FK | |
| `FileName` | TEXT NOT NULL | |
| `FilePath` | TEXT NOT NULL | path relative to `{DatabaseRoot}/attachments/` (or an absolute path — consumer's convention) |
| `UploadedByUserId` | INTEGER FK | |
| `UploadedAt` | TEXT | |
| `IsDeleted` | INTEGER | |

---

## Initialization Sequence

When setting up a fresh Ticketing database, skills must be called in this order:

1. `XBase-Database-Initialize` — create a database named `ticketing` in the configured database root (e.g. `{DatabaseRoot}/ticketing/`)
2. `XBase-Database-Connect` — `DatabaseName:"ticketing"`, connection name `ticketing`
3. `XBase-Schema-TableCreate` × N — create all tables above
4. `XBase-Index-Create` — at minimum: `Tickets.StatusId`, `Tickets.AssignedToUserId`, `Tickets.CreatedAt`
5. `Ticketing-Status-Define` × N — seed default statuses: `Open`, `In Progress`, `Blocked`, `Closed`
6. Populate `StatusTransitions` via `XBase-Record-Insert`
7. `Ticketing-Priority-Define` × N — seed: `Low`, `Medium`, `High`, `Critical`
8. `Ticketing-User-Register` — create first admin user

---

## Error Handling

All errors use the standard XBase envelope extended with a ticketing prefix:

| Code | Meaning |
|---|---|
| `TICKETING_TICKET_NOT_FOUND` | No ticket with given ID |
| `TICKETING_STATUS_TRANSITION_INVALID` | Transition not allowed |
| `TICKETING_USER_NOT_FOUND` | No user with given ID or username |
| `TICKETING_USER_INACTIVE` | User exists but is deactivated |
| `TICKETING_AUTH_FAILED` | Credential hash did not match |
| `TICKETING_COMMENT_NOT_FOUND` | Comment ID not found or soft-deleted |
| `TICKETING_DISPLAY_STDOUT_UNAVAILABLE` | stdout cannot be written (redirected with no tty) |
| `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED` | BellCount > 10 |

---

## Dependencies

| Dependency | Provided By |
|---|---|
| Database storage | `XBase-Database-*` Skills |
| Schema management | `XBase-Schema-*` Skills |
| Record CRUD | `XBase-Record-*` Skills |
| Filtering / sorting | `XBase-Query-*` Skills |
| Transactions | `XBase-Transaction-*` Skills |
| Terminal bell + ASCII art | `Ticketing-Display-*` Skills (stdout + BEL character) |
