# Product Requirements Document: Ticketing System

## Overview

The Ticketing System is a full-featured issue-tracking feature implemented exclusively through AI Skills. It has **no direct database access** — every read and write routes through XBase Skills. All Ticketing Skills follow the same naming convention:

```
[Feature Name]-[Feature-Operation]-[Any Subdivision Needed]
```

Example: `Ticketing-Ticket-Create`, `Ticketing-Comment-Edit`

**Dependency**: All Ticketing Skills require an active `XBase-Database-Connect` session named `ticketing`.

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

### Ticketing-Status-Transition

**XBase Skills Called**
- `XBase-Record-Select` (validate allowed transition exists in `StatusTransitions`)
- `XBase-Transaction-Begin`
- `XBase-Record-Update` (table: `Tickets`, set `StatusId`)
- `XBase-Record-Insert` (table: `TicketHistory`, action: `StatusChanged`)
- `XBase-Transaction-Commit`

**Inputs**
- `TicketId` (int)
- `ToStatusId` (int)
- `ChangedByUserId` (int)
- `Comment` (string, optional)

**Behavior**
Rejects the transition if no matching row in `StatusTransitions(FromStatusId, ToStatusId)` exists, unless the user has admin role.

---

### Ticketing-User-Authenticate

**XBase Skills Called**
- `XBase-Record-Select` (table: `Users`, filter by `Username`)
- `XBase-Record-Insert` (table: `Sessions`)

**Inputs**
- `Username` (string)
- `CredentialHash` (string) — pre-hashed by the caller; never accept plaintext

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
| `FilePath` | TEXT NOT NULL | path relative to `data/attachments/` |
| `UploadedByUserId` | INTEGER FK | |
| `UploadedAt` | TEXT | |
| `IsDeleted` | INTEGER | |

---

## Initialization Sequence

When setting up a fresh Ticketing database, skills must be called in this order:

1. `XBase-Database-Initialize` — create `data/ticketing.db`
2. `XBase-Database-Connect` — connection name `ticketing`
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

---

## Dependencies

| Dependency | Provided By |
|---|---|
| Database storage | `XBase-Database-*` Skills |
| Schema management | `XBase-Schema-*` Skills |
| Record CRUD | `XBase-Record-*` Skills |
| Filtering / sorting | `XBase-Query-*` Skills |
| Transactions | `XBase-Transaction-*` Skills |
