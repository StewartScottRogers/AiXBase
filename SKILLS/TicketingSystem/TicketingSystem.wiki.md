# Ticketing System

A full helpdesk ticketing system implemented as AI Skills, built entirely on top of XBase. Covers the complete ticket lifecycle — creation, assignment, escalation, status transitions, comments, attachments, reporting, and a visual terminal display with audible bell notification.

---

## Architecture

| Layer | Technology |
|---|---|
| Storage | XBase native file engine (`AiXBase/ticketing/` directory) |
| Schema | 11 tables (see below) |
| Audit trail | `TicketHistory` table; every state change appends a row |
| Authentication | Session tokens stored in `Sessions`; generic error for all auth failures |
| Terminal display | Unicode block-art banners + ASCII BEL (`\a`) via Display skills |

### Database Tables

| Table | Purpose |
|---|---|
| `Tickets` | Core ticket records |
| `Comments` | Threaded comments per ticket |
| `Attachments` | File attachment metadata per ticket |
| `Statuses` | Configurable status definitions |
| `StatusTransitions` | Allowed `FromStatus → ToStatus` pairs |
| `Priorities` | Configurable priority definitions with numeric ordering |
| `Categories` | Hierarchical category tree |
| `Users` | Registered users with hashed passwords |
| `TicketHistory` | Append-only audit log of all ticket changes |
| `TicketTags` | Many-to-many tags per ticket |
| `Sessions` | Active authentication sessions with expiry |

### Ticket Number Format

Tickets are assigned sequential numbers: `TKT-0001`, `TKT-0002`, … The sequence never resets, never reuses deleted numbers, and expands naturally beyond `TKT-9999` to `TKT-10000`.

---

## Quick Start

```
# 1. Initialise the database (XBase prerequisite)
/XBase-Database-Initialize  DatabaseName:"ticketing"
/XBase-Database-Connect     DatabaseName:"ticketing"  ConnectionName:"ticketing"

# 2. Create the schema (run XBase-Schema-TableCreate for each of the 11 tables)

# 3. Seed statuses and transitions
/Ticketing-Status-Define  Name:"Open"        IsTerminal:false  IsDefault:true
/Ticketing-Status-Define  Name:"In Progress" IsTerminal:false
/Ticketing-Status-Define  Name:"Closed"      IsTerminal:true

# 4. Seed priorities
/Ticketing-Priority-Define  Name:"Critical"  NumericValue:1
/Ticketing-Priority-Define  Name:"High"      NumericValue:2
/Ticketing-Priority-Define  Name:"Medium"    NumericValue:3  IsDefault:true
/Ticketing-Priority-Define  Name:"Low"       NumericValue:4

# 5. Register the first admin user
/Ticketing-User-Register
  Username:"admin"
  Email:"admin@example.com"
  Password:"changeme"
  DisplayName:"Administrator"
  IsAdmin:true

# 6. Authenticate
/Ticketing-User-Authenticate  Username:"admin"  Password:"changeme"
# → SessionToken:"abc123..."

# 7. Create a ticket
/Ticketing-Ticket-Create
  Summary:"Login page crashes on mobile Safari"
  SubmittedByUserId:"<admin-user-id>"

# 8. Assign it
/Ticketing-Ticket-Assign
  TicketId:1
  AssigneeId:"<user-id>"
  AssignedByUserId:"<admin-user-id>"

# 9. Close it — triggers banner + bell × 3
/Ticketing-Ticket-Close
  TicketId:1
  ClosedByUserId:"<admin-user-id>"
```

---

## Operation Groups

### Ticket (9 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Ticket-Create` | Create a new ticket; auto-assigns number, default status, and default priority |
| `Ticketing-Ticket-Read` | Read a ticket by Id or TicketNumber; includes counts for comments and attachments |
| `Ticketing-Ticket-Update` | Update Summary, Description, or Category; Status changes must go through Status-Transition |
| `Ticketing-Ticket-Delete` | Soft-delete (default) or hard-delete a ticket |
| `Ticketing-Ticket-Close` | Transition ticket to a terminal status, emit the COMPLETE banner, ring bell × 3 |
| `Ticketing-Ticket-Reopen` | Move a terminal-status ticket back to Open |
| `Ticketing-Ticket-Assign` | Set or change the assignee; emits an alert banner |
| `Ticketing-Ticket-Escalate` | Raise the ticket's priority; emits an escalation alert |
| `Ticketing-Ticket-Query` | Search tickets with filters (status, priority, assignee, category, tag, date range, text) |

### Comment (4 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Comment-Add` | Add a comment to a ticket; supports `IsInternal` flag for staff-only notes |
| `Ticketing-Comment-Read` | Read all comments on a ticket or a single comment by Id |
| `Ticketing-Comment-Edit` | Edit a comment body; sets `EditedAt`; restricted to author or admin |
| `Ticketing-Comment-Delete` | Soft-delete a comment; restricted to author or admin |

### Attachment (3 skills)

Attachments store file **metadata** only — path, filename, size, uploader. Actual file storage is handled by the caller.

| Skill | Purpose |
|---|---|
| `Ticketing-Attachment-Add` | Record a file attachment on a ticket |
| `Ticketing-Attachment-Read` | List attachments on a ticket or read a single attachment by Id |
| `Ticketing-Attachment-Remove` | Soft-remove an attachment; restricted to uploader or admin |

### Status (2 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Status-Define` | Create or update a status; `IsTerminal:true` marks statuses that trigger the COMPLETE display |
| `Ticketing-Status-Transition` | Move a ticket between statuses; validates against `StatusTransitions` table; triggers Display-Complete when `IsTerminal = 1` |

Only transitions listed in the `StatusTransitions` table are permitted. Moving a ticket out of a terminal status must be done through `Ticketing-Ticket-Reopen`, not Status-Transition directly.

### Priority (2 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Priority-Define` | Create or update a priority level with a numeric value for ordering |
| `Ticketing-Priority-Set` | Set a ticket's priority; history record created |

`Ticketing-Ticket-Escalate` raises priority by one level. `Ticketing-Priority-Set` sets any priority explicitly.

### Category (4 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Category-Create` | Create a root or child category (hierarchical tree) |
| `Ticketing-Category-Assign` | Assign or clear a ticket's category |
| `Ticketing-Tag-Add` | Add a free-text tag to a ticket; idempotent |
| `Ticketing-Tag-Remove` | Remove a tag from a ticket; hard delete (tags have no audit requirement) |

### User (5 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-User-Register` | Register a new user; password hashed immediately; hash never returned |
| `Ticketing-User-Read` | Look up a user by Id, Username, or Email |
| `Ticketing-User-Update` | Update display name, email, or password |
| `Ticketing-User-Deactivate` | Deactivate a user; guards against deactivating the last admin |
| `Ticketing-User-Authenticate` | Verify credentials; returns a session token; all failure modes return the same generic error |

### Report (3 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Report-Summary` | Aggregate counts by status, priority, and assignee |
| `Ticketing-Report-Generate` | Generate a named report type (open, closed-in-period, by-assignee, overdue) |
| `Ticketing-Report-Export` | Export ticket data to CSV or JSON |

### Display (3 skills)

| Skill | Purpose |
|---|---|
| `Ticketing-Display-Complete` | Render a full COMPLETE banner to stdout and emit BEL characters |
| `Ticketing-Display-Alert` | Render a compact alert banner (assignment, escalation events) and emit BEL |
| `Ticketing-Display-Bell` | Emit N BEL characters (`\a`, ASCII 7) to stdout; max 10 |

---

## Terminal Display System

When a ticket reaches a terminal status (closed, cancelled), the system writes a full-width banner to stdout and rings the terminal bell so the completion is visible and audible from across the room.

### COMPLETE Banner (Unicode)

```
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗
██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝
██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗
██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝
╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗
 ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝

  Ticket  : {TicketNumber}
  Summary : {Summary}
  Closed  : {ClosedAt}
  By      : {ClosedByDisplayName}
```

Pass `UseUnicode: false` to any Display skill for the plain-ASCII fallback (compatible with all terminals).

### Bell Implementation

`Ticketing-Display-Bell` emits `Console.Write('\a')` once per ring — three separate calls for three audibly distinct rings. It does **not** use `Console.Beep()` (which blocks the thread and is unsupported on non-Windows platforms).

---

## Audit Trail

Every mutation to a ticket appends a row to `TicketHistory`:

| Column | Content |
|---|---|
| `TicketId` | The affected ticket |
| `ChangeType` | `"created"`, `"updated"`, `"status_changed"`, `"assigned"`, `"escalated"`, `"deleted"`, `"reopened"` |
| `ChangedByUserId` | The acting user |
| `OldValue` / `NewValue` | JSON representation of what changed |
| `Note` | Optional reason or comment |
| `ChangedAt` | ISO-8601 timestamp |

History is append-only and is never soft-deleted.

---

## Authentication Design

`Ticketing-User-Authenticate` returns the same `TICKETING_AUTH_FAILED` error for all three failure conditions — wrong password, non-existent username, and deactivated account — with identical wording and no timing difference. This prevents user-enumeration attacks.

---

## Error Codes

All Ticketing System error codes follow the pattern `TICKETING_<CATEGORY>_<REASON>`.

| Category | Example Codes |
|---|---|
| `TICKET` | `TICKETING_TICKET_NOT_FOUND`, `TICKETING_TICKET_ALREADY_CLOSED`, `TICKETING_TICKET_NOT_CLOSED`, `TICKETING_TICKET_SUMMARY_REQUIRED`, `TICKETING_TICKET_IDENTIFIER_REQUIRED` |
| `COMMENT` | `TICKETING_COMMENT_NOT_FOUND`, `TICKETING_COMMENT_BODY_REQUIRED`, `TICKETING_COMMENT_EDIT_FORBIDDEN`, `TICKETING_COMMENT_DELETE_FORBIDDEN` |
| `ATTACHMENT` | `TICKETING_ATTACHMENT_NOT_FOUND`, `TICKETING_ATTACHMENT_FILENAME_REQUIRED`, `TICKETING_ATTACHMENT_DUPLICATE`, `TICKETING_ATTACHMENT_REMOVE_FORBIDDEN` |
| `STATUS` | `TICKETING_STATUS_NOT_FOUND`, `TICKETING_STATUS_NAME_DUPLICATE`, `TICKETING_STATUS_NAME_REQUIRED`, `TICKETING_STATUS_TRANSITION_INVALID`, `TICKETING_STATUS_ALREADY_CURRENT`, `TICKETING_STATUS_IN_USE` |
| `PRIORITY` | `TICKETING_PRIORITY_NOT_FOUND`, `TICKETING_PRIORITY_NAME_DUPLICATE`, `TICKETING_PRIORITY_NAME_REQUIRED`, `TICKETING_PRIORITY_IN_USE`, `TICKETING_PRIORITY_ALREADY_MAX`, `TICKETING_PRIORITY_ESCALATION_INVALID`, `TICKETING_PRIORITY_VALUE_DUPLICATE` |
| `CATEGORY` | `TICKETING_CATEGORY_NOT_FOUND`, `TICKETING_CATEGORY_NAME_DUPLICATE`, `TICKETING_CATEGORY_NAME_REQUIRED` |
| `TAG` | `TICKETING_TAG_NAME_REQUIRED` |
| `USER` | `TICKETING_USER_NOT_FOUND`, `TICKETING_USER_INACTIVE`, `TICKETING_USER_EMAIL_DUPLICATE`, `TICKETING_USER_USERNAME_DUPLICATE`, `TICKETING_USER_EMAIL_INVALID`, `TICKETING_USER_USERNAME_INVALID`, `TICKETING_USER_EMAIL_REQUIRED`, `TICKETING_USER_USERNAME_REQUIRED`, `TICKETING_USER_LAST_ADMIN`, `TICKETING_USER_IDENTIFIER_REQUIRED`, `TICKETING_USER_DEACTIVATION_FORBIDDEN` |
| `AUTH` | `TICKETING_AUTH_FAILED` (one code for all auth failures) |
| `REPORT` | `TICKETING_REPORT_TYPE_UNKNOWN`, `TICKETING_REPORT_FORMAT_UNKNOWN` |
| `DISPLAY` | `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED`, `TICKETING_DISPLAY_STDOUT_UNAVAILABLE`, `TICKETING_DISPLAY_FIELD_REQUIRED` |
| `DELETE` | `TICKETING_DELETE_NOT_CONFIRMED` |
| `FIELD` | `TICKETING_FIELD_NOT_UPDATABLE` |

---

## Dependencies

The Ticketing System depends on XBase. The full dependency chain:

```
Ticketing-Ticket-Close
  └── Ticketing-Status-Transition
        └── Ticketing-Display-Complete
              └── Ticketing-Display-Bell
```

All XBase Database, Schema, Record, Query, Index, Transaction, and Backup skills must be installed before any Ticketing skill can function.
