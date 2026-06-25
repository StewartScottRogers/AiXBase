# Product Requirements Document: Ticketing System Testing Criteria

## Overview

This document defines the complete set of acceptance tests, edge-case tests, error-condition tests, performance benchmarks, stress tests, and security tests required to certify that every Ticketing System Skill behaves correctly. A skill is considered **passing** only when every applicable test ID in this document produces the stated expected result.

Test IDs follow the pattern `TICK-<GROUP>-<NNN>` where group codes are:

| Code | Group |
|---|---|
| `TKT` | Ticket Operations |
| `CMT` | Comment Operations |
| `ATT` | Attachment Operations |
| `STA` | Status Operations |
| `PRI` | Priority Operations |
| `CAT` | Category / Tag Operations |
| `USR` | User Operations |
| `RPT` | Report Operations |
| `DSP` | Display Operations |
| `PERF` | Performance Benchmarks |
| `STRESS` | Stress Tests |
| `SEC` | Security Tests |

---

## Test Environment Requirements

| Requirement | Specification |
|---|---|
| SQLite version | ≥ 3.40.0 |
| XBase skills | All 28 XBase skills must pass their own test suite first |
| `AiXBase/ticketing.db` | Freshly initialised with full Ticketing schema for each test group unless noted |
| Seed data | At least 1 admin user (`admin`, hashed password), all seed statuses, all seed priorities present |
| Disk space | ≥ 5 GB for performance and stress suites |
| stdout | Writable (for Display group tests) |
| Clock | Stable; no large jumps during test run |

---

## Test Data Specifications

### Ticket Number Format

Tickets are numbered `TKT-{N}` where N is zero-padded to at minimum 4 digits: `TKT-0001`. At 9 999 the sequence must expand naturally to `TKT-10000` (5 digits) without resetting or erroring.

### Seed Statuses

| Name | IsTerminal | IsDefault |
|---|---|---|
| Open | 0 | 1 |
| In Progress | 0 | 0 |
| Pending | 0 | 0 |
| Resolved | 0 | 0 |
| Closed | 1 | 0 |
| Cancelled | 1 | 0 |

### Seed Status Transitions (valid paths)

`Open → In Progress`, `Open → Pending`, `Open → Cancelled`, `In Progress → Pending`, `In Progress → Resolved`, `In Progress → Closed`, `Pending → In Progress`, `Pending → Cancelled`, `Resolved → Closed`, `Resolved → In Progress` (re-check), `Closed → Open` (via Reopen only), `Cancelled → Open` (via Reopen only)

### Seed Priorities

| Name | NumericValue | IsDefault |
|---|---|---|
| Critical | 1 | 0 |
| High | 2 | 0 |
| Medium | 3 | 1 |
| Low | 4 | 0 |

### Data Scale Tiers

| Tier | Ticket Count | Label |
|---|---|---|
| S | 50 | Small |
| M | 1 000 | Medium |
| L | 10 000 | Large |
| XL | 100 000 | Extra-Large |

---

## Test Execution Standards

- Each test creates its own isolated database unless the test group is marked **shared state**
- Tests within a group that depend on each other are listed in order and marked with the prerequisite test ID
- A test **fails** if: wrong output, wrong error code, unhandled exception, audit record not created, or execution time exceeds the stated limit
- Performance tests must be repeated 3 times; the **median** value must meet the target
- All tests must pass with XBase `PRAGMA foreign_keys=ON` and `PRAGMA journal_mode=WAL`
- Every write operation (ticket create/update/close/assign/escalate/reopen) must produce a corresponding `TicketHistory` row; tests verify this unless the skill is read-only

---

## Test Cases: Ticket Operations

### Ticketing-Ticket-Create

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-001` | Happy path — required fields only | `Summary:"Bug in login"`, valid `SubmittedByUserId` | `Success: true`; `TicketNumber` = `TKT-0001`; `Status` = `Open`; `Priority` = `Medium` (defaults) |
| `TICK-TKT-002` | Happy path — all optional fields | + `Description`, `AssigneeId`, `CategoryId`, `PriorityId` | All fields persisted; returned in output |
| `TICK-TKT-003` | Ticket number auto-increments | Create 3 tickets in sequence | Numbers are `TKT-0001`, `TKT-0002`, `TKT-0003` |
| `TICK-TKT-004` | Ticket number does not reuse after delete | Create TKT-0001, soft-delete it, create again | Next ticket is `TKT-0002` (sequence never resets) |
| `TICK-TKT-005` | Sequence survives past TKT-9999 | Create enough to reach 9999th ticket, create one more | `TKT-10000` (5 digits); no overflow or reset |
| `TICK-TKT-006` | Default status is `Open` | No `StatusId` supplied | Ticket has the status whose `IsDefault = 1` |
| `TICK-TKT-007` | Default priority is `Medium` | No `PriorityId` supplied | Ticket has the priority whose `IsDefault = 1` |
| `TICK-TKT-008` | Explicit priority honoured | `PriorityId` = Critical | Ticket has Critical priority |
| `TICK-TKT-009` | Missing Summary | No `Summary` field | Returns `TICKETING_TICKET_SUMMARY_REQUIRED` |
| `TICK-TKT-010` | Empty Summary | `Summary:""` | Returns `TICKETING_TICKET_SUMMARY_REQUIRED` |
| `TICK-TKT-011` | Summary whitespace-only | `Summary:"   "` | Returns `TICKETING_TICKET_SUMMARY_REQUIRED` |
| `TICK-TKT-012` | Missing SubmittedByUserId | No user field | Returns `TICKETING_USER_NOT_FOUND` or validation error |
| `TICK-TKT-013` | Non-existent SubmittedByUserId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-TKT-014` | Non-existent AssigneeId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-TKT-015` | Non-existent CategoryId | Random integer | Returns `TICKETING_CATEGORY_NOT_FOUND` |
| `TICK-TKT-016` | Non-existent PriorityId | Random integer | Returns `TICKETING_PRIORITY_NOT_FOUND` |
| `TICK-TKT-017` | Long Summary (255 chars) | 255-character string | Accepted |
| `TICK-TKT-018` | Very long Summary (>255 chars) | 256-character string | Returns validation error or truncated per schema |
| `TICK-TKT-019` | Unicode Summary | `Summary:"支援リクエスト 🎫"` | Stored and returned correctly |
| `TICK-TKT-020` | HTML tags in Summary | `Summary:"<script>alert(1)</script>"` | Stored as literal text; not interpreted or stripped |
| `TICK-TKT-021` | CreatedAt auto-set | No `CreatedAt` in input | `CreatedAt` is valid ISO-8601 |
| `TICK-TKT-022` | History record created | Any valid create | `TicketHistory` row with `ChangeType:"created"` |
| `TICK-TKT-023` | Deactivated submitter | `SubmittedByUserId` belongs to deactivated user | Returns `TICKETING_USER_INACTIVE` |
| `TICK-TKT-024` | Assign to deactivated user | `AssigneeId` deactivated | Returns `TICKETING_USER_INACTIVE` |

---

### Ticketing-Ticket-Read

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-025` | Read by TicketId | Valid integer Id | Full ticket returned with status name, priority name, category name, assignee name |
| `TICK-TKT-026` | Read by TicketNumber | `TicketNumber:"TKT-0001"` | Same as by Id |
| `TICK-TKT-027` | Neither Id nor Number | No identifying input | Returns `TICKETING_TICKET_IDENTIFIER_REQUIRED` |
| `TICK-TKT-028` | Non-existent TicketId | Random integer | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-029` | Non-existent TicketNumber | `"TKT-9999"` on empty DB | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-030` | Soft-deleted ticket, IncludeDeleted false | Deleted ticket | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-031` | Soft-deleted ticket, IncludeDeleted true | `IncludeDeleted:true` | Ticket returned; `IsDeleted: true` in output |
| `TICK-TKT-032` | Comment count included | Ticket with 5 comments | `CommentCount: 5` in output |
| `TICK-TKT-033` | Attachment count included | Ticket with 3 attachments | `AttachmentCount: 3` in output |
| `TICK-TKT-034` | TicketNumber case-insensitive | `"tkt-0001"` | Returns same ticket (or documents case requirement) |

---

### Ticketing-Ticket-Update

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-035` | Update Summary | `Summary:"New summary"` | Persisted; `UpdatedAt` refreshed |
| `TICK-TKT-036` | Update Description | `Description:"New body"` | Persisted |
| `TICK-TKT-037` | Update Category | New valid `CategoryId` | Persisted |
| `TICK-TKT-038` | Clear Description | `Description:null` | Field set to NULL |
| `TICK-TKT-039` | No fields changed | Existing values repeated | `Success: true`; `UpdatedAt` still refreshed (or explicitly unchanged) |
| `TICK-TKT-040` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-041` | Soft-deleted ticket | Deleted Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-042` | History record created | Any field changed | `TicketHistory` row listing changed fields and old vs new values |
| `TICK-TKT-043` | UpdatedByUserId recorded in history | `UpdatedByUserId` supplied | History row has correct user |
| `TICK-TKT-044` | Status not updatable via this skill | `StatusId` in Updates | Returns `TICKETING_FIELD_NOT_UPDATABLE` (use Status-Transition) |

---

### Ticketing-Ticket-Delete

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-045` | Soft delete (default) | Valid TicketId | `IsDeleted = 1`; ticket still in DB |
| `TICK-TKT-046` | Hard delete with confirm | `HardDelete:true`, `ConfirmDelete:true` | Row removed; comments and attachments cascade-soft-deleted |
| `TICK-TKT-047` | Hard delete without confirm | `HardDelete:true`, no `ConfirmDelete` | Returns `TICKETING_DELETE_NOT_CONFIRMED` |
| `TICK-TKT-048` | Already soft-deleted | Delete again | `Success: true`; idempotent |
| `TICK-TKT-049` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-050` | History record on soft delete | Soft delete | `TicketHistory` row with `ChangeType:"deleted"` |

---

### Ticketing-Ticket-Close

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-051` | Happy path — Open → Closed | Open ticket, valid `ClosedByUserId` | `Status` = `Closed`; `ClosedAt` set; banner emitted; bell × 3 |
| `TICK-TKT-052` | Calls Status-Transition internally | Any close | `TicketHistory` contains transition record (proves Status-Transition fired) |
| `TICK-TKT-053` | Calls Display-Complete | Any close | Unicode banner written to stdout (or captured output) |
| `TICK-TKT-054` | Calls Display-Bell × 3 | Any close | BEL character emitted 3 times |
| `TICK-TKT-055` | Close already-closed ticket | Closed ticket | Returns `TICKETING_TICKET_ALREADY_CLOSED` |
| `TICK-TKT-056` | Close ticket in terminal status (Cancelled) | Cancelled ticket | Returns `TICKETING_TICKET_ALREADY_CLOSED` or appropriate error |
| `TICK-TKT-057` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-058` | Missing ClosedByUserId | No user field | Returns `TICKETING_USER_NOT_FOUND` or validation error |
| `TICK-TKT-059` | Non-existent ClosedByUserId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-TKT-060` | ClosedAt timestamp set | Successful close | `ClosedAt` is ISO-8601 ≥ `CreatedAt` |
| `TICK-TKT-061` | ClosedByDisplayName in banner | `ClosedByUserId` maps to display name | Banner interpolates correct `{ClosedByDisplayName}` |
| `TICK-TKT-062` | Soft-deleted ticket | Deleted Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-063` | UseUnicode false — ASCII banner | `UseUnicode:false` | Plain-ASCII COMPLETE banner emitted instead of Unicode |
| `TICK-TKT-064` | Close In-Progress ticket | Valid transition path | Succeeds if `In Progress → Closed` is in StatusTransitions |
| `TICK-TKT-065` | Close Pending ticket via invalid path | If `Pending → Closed` not in StatusTransitions | Returns `TICKETING_STATUS_TRANSITION_INVALID` |

---

### Ticketing-Ticket-Reopen

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-066` | Reopen from Closed | Closed ticket, valid `ReopenedByUserId` | Status = `Open`; `ClosedAt` cleared |
| `TICK-TKT-067` | Reopen from Cancelled | Cancelled ticket | Returns to `Open` (if `Cancelled → Open` is in transitions) |
| `TICK-TKT-068` | Reopen non-terminal ticket | `In Progress` ticket | Returns `TICKETING_TICKET_NOT_CLOSED` |
| `TICK-TKT-069` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-070` | Missing ReopenedByUserId | No user field | Validation error |
| `TICK-TKT-071` | History record created | Successful reopen | `TicketHistory` row with `ChangeType:"reopened"` |
| `TICK-TKT-072` | ReopenReason optional | `ReopenReason:"Recurrence"` | Stored in history note |
| `TICK-TKT-073` | Reopen + Close cycle × 3 | Full cycle repeated | Each close emits banner + bell; ticket ClosedAt updates each time |

---

### Ticketing-Ticket-Assign

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-074` | Assign to active user | Valid `AssigneeId` | `AssigneeId` updated; history record created |
| `TICK-TKT-075` | Reassign (change assignee) | Different valid `AssigneeId` | New assignee set; old and new in history |
| `TICK-TKT-076` | Self-assignment | `AssigneeId` = `AssignedByUserId` | Allowed; succeeds |
| `TICK-TKT-077` | Unassign (clear assignee) | `AssigneeId:null` | `AssigneeId` set to NULL |
| `TICK-TKT-078` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-079` | Non-existent AssigneeId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-TKT-080` | Deactivated assignee | Inactive user | Returns `TICKETING_USER_INACTIVE` |
| `TICK-TKT-081` | Assign closed ticket | Terminal status | Allowed or returns `TICKETING_TICKET_ALREADY_CLOSED` — document behaviour |
| `TICK-TKT-082` | History record created | Any assignment | `TicketHistory` with old assignee → new assignee |

---

### Ticketing-Ticket-Escalate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-083` | Escalate Medium → High | Medium ticket | Priority = High; history updated |
| `TICK-TKT-084` | Escalate High → Critical | High ticket | Priority = Critical |
| `TICK-TKT-085` | Already at highest priority (Critical) | Critical ticket | Returns `TICKETING_PRIORITY_ALREADY_MAX` |
| `TICK-TKT-086` | Target priority explicit | `ToPriorityId` specified | Uses that exact priority |
| `TICK-TKT-087` | Lower-than-current target priority | Priority numerically lower urgency | Returns `TICKETING_PRIORITY_ESCALATION_INVALID` (cannot de-escalate via Escalate) |
| `TICK-TKT-088` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-TKT-089` | Non-existent EscalatedByUserId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-TKT-090` | Alert emitted | Successful escalation | `Ticketing-Display-Alert` called; `TICKET ESCALATED` event in banner |
| `TICK-TKT-091` | Bell emitted on escalation | Any escalate | At least 1 BEL character on stdout |
| `TICK-TKT-092` | History record created | Any escalate | `TicketHistory` with old priority → new priority |
| `TICK-TKT-093` | EscalationReason optional | `EscalationReason:"SLA breach"` | Stored in history |

---

### Ticketing-Ticket-Query

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-TKT-094` | All tickets, no filter | No filter | All non-deleted tickets returned |
| `TICK-TKT-095` | Filter by StatusId | `StatusId` = Open | Only open tickets |
| `TICK-TKT-096` | Filter by PriorityId | `PriorityId` = Critical | Only critical tickets |
| `TICK-TKT-097` | Filter by AssigneeId | Specific user | Only their tickets |
| `TICK-TKT-098` | Filter by CategoryId | Specific category | Only that category |
| `TICK-TKT-099` | Filter by unassigned | `AssigneeId:null` | Only unassigned tickets |
| `TICK-TKT-100` | Full-text search on Summary | `SearchText:"login"` | Tickets whose Summary contains `login` (case-insensitive) |
| `TICK-TKT-101` | SearchText partial match | `SearchText:"log"` | Matches `login`, `logout`, `error logging` |
| `TICK-TKT-102` | CreatedAt date range | `CreatedAfter`, `CreatedBefore` | Only tickets in range |
| `TICK-TKT-103` | Multiple filters combined | Status + Priority + Assignee | Intersection |
| `TICK-TKT-104` | Pagination — page 1 | `Limit:10, Offset:0` | 10 tickets; `TotalCount` = full result count |
| `TICK-TKT-105` | Pagination — last page partial | `Limit:10, Offset:7` on 12-ticket set | 5 tickets |
| `TICK-TKT-106` | Sort by CreatedAt DESC | `Sort:"CreatedAt DESC"` | Newest first |
| `TICK-TKT-107` | Sort by Priority | `Sort:"Priority ASC"` (by NumericValue) | Critical first |
| `TICK-TKT-108` | No matching tickets | Filter produces no results | `Tickets:[]`, `TotalCount:0` |
| `TICK-TKT-109` | Include deleted | `IncludeDeleted:true` | Soft-deleted tickets appear |
| `TICK-TKT-110` | Tag filter | `Tag:"bug"` | Only tickets tagged `bug` |

---

## Test Cases: Comment Operations

### Ticketing-Comment-Add

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CMT-001` | Happy path | Valid `TicketId`, `AuthorId`, `Body` | `Success: true`; `CommentId` returned |
| `TICK-CMT-002` | Body with Unicode | `Body:"Thanks! 🙏 問題が解決しました"` | Stored and returned correctly |
| `TICK-CMT-003` | Very long body (10 000 chars) | `Body:"x" × 10 000` | Stored; no truncation |
| `TICK-CMT-004` | Empty body | `Body:""` | Returns `TICKETING_COMMENT_BODY_REQUIRED` |
| `TICK-CMT-005` | Whitespace-only body | `Body:"   "` | Returns `TICKETING_COMMENT_BODY_REQUIRED` |
| `TICK-CMT-006` | Non-existent TicketId | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-CMT-007` | Non-existent AuthorId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-CMT-008` | Comment on soft-deleted ticket | Deleted ticket | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-CMT-009` | Comment on closed ticket | Terminal status | Allowed (post-close comments permitted) |
| `TICK-CMT-010` | IsInternal flag | `IsInternal:true` | Stored with internal flag; excluded from external reads |
| `TICK-CMT-011` | CreatedAt auto-set | Any comment | `CreatedAt` is ISO-8601 |
| `TICK-CMT-012` | Deactivated author | Inactive user | Returns `TICKETING_USER_INACTIVE` |

---

### Ticketing-Comment-Read

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CMT-013` | All comments on ticket | `TicketId` with 5 comments | All 5 returned, sorted by `CreatedAt ASC` |
| `TICK-CMT-014` | Single comment by CommentId | `CommentId` | One comment returned |
| `TICK-CMT-015` | Non-existent CommentId | Random Id | Returns `TICKETING_COMMENT_NOT_FOUND` |
| `TICK-CMT-016` | Non-existent TicketId | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-CMT-017` | Soft-deleted comments excluded | Deleted comment | Not in results |
| `TICK-CMT-018` | Soft-deleted comments, IncludeDeleted | `IncludeDeleted:true` | Deleted comment returned |
| `TICK-CMT-019` | Internal comments excluded for non-admin | `IsInternal:true` comment, regular-user caller | Not in results |
| `TICK-CMT-020` | Internal comments visible for admin | Admin caller | Internal comment returned |
| `TICK-CMT-021` | Pagination | 100 comments, `Limit:10, Offset:20` | 10 comments; `TotalCount:100` |

---

### Ticketing-Comment-Edit

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CMT-022` | Edit body | New `Body` text | Updated; `EditedAt` set |
| `TICK-CMT-023` | EditedAt set on first edit | No `EditedAt` before | `EditedAt` = now after edit |
| `TICK-CMT-024` | EditedAt updated on re-edit | Comment edited twice | `EditedAt` is latest timestamp |
| `TICK-CMT-025` | Non-existent comment | Random Id | Returns `TICKETING_COMMENT_NOT_FOUND` |
| `TICK-CMT-026` | Soft-deleted comment | Deleted Id | Returns `TICKETING_COMMENT_NOT_FOUND` |
| `TICK-CMT-027` | Empty new body | `Body:""` | Returns `TICKETING_COMMENT_BODY_REQUIRED` |
| `TICK-CMT-028` | Edit by non-author | `EditorId` ≠ `AuthorId`, non-admin | Returns `TICKETING_COMMENT_EDIT_FORBIDDEN` |
| `TICK-CMT-029` | Edit by admin (any comment) | Admin `EditorId` | Allowed |
| `TICK-CMT-030` | Original body preserved | Pre- and post-edit read | `OriginalBody` field present (or history record); `Body` = new value |

---

### Ticketing-Comment-Delete

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CMT-031` | Soft delete | Valid CommentId | `IsDeleted = 1`; not in subsequent reads |
| `TICK-CMT-032` | Already soft-deleted | Delete again | `Success: true`; idempotent |
| `TICK-CMT-033` | Non-existent comment | Random Id | Returns `TICKETING_COMMENT_NOT_FOUND` |
| `TICK-CMT-034` | Delete by non-author | Non-admin, non-author | Returns `TICKETING_COMMENT_DELETE_FORBIDDEN` |
| `TICK-CMT-035` | Delete by admin | Admin caller | Allowed |

---

## Test Cases: Attachment Operations

### Ticketing-Attachment-Add

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-ATT-001` | Happy path | `TicketId`, `AttachedByUserId`, `FileName`, `FilePath` | `AttachmentId` returned; record in DB |
| `TICK-ATT-002` | FileName with spaces | `FileName:"my report.pdf"` | Stored as-is |
| `TICK-ATT-003` | FileName with Unicode | `FileName:"レポート.xlsx"` | Stored correctly |
| `TICK-ATT-004` | Missing FileName | No `FileName` | Returns validation error |
| `TICK-ATT-005` | Empty FileName | `FileName:""` | Returns `TICKETING_ATTACHMENT_FILENAME_REQUIRED` |
| `TICK-ATT-006` | Missing FilePath | No `FilePath` | Returns validation error |
| `TICK-ATT-007` | Duplicate filename on same ticket | Second attachment with identical `FileName` | Returns `TICKETING_ATTACHMENT_DUPLICATE` or allowed with disambiguation |
| `TICK-ATT-008` | Non-existent TicketId | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-ATT-009` | Non-existent AttachedByUserId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-ATT-010` | Deactivated user | Inactive `AttachedByUserId` | Returns `TICKETING_USER_INACTIVE` |
| `TICK-ATT-011` | FileSizeBytes optional | Supplied and omitted | Stored if supplied; NULL if omitted |
| `TICK-ATT-012` | CreatedAt auto-set | Any add | `CreatedAt` is ISO-8601 |
| `TICK-ATT-013` | Add to closed ticket | Terminal status | Allowed (attachments on closed tickets permitted) |

---

### Ticketing-Attachment-Read

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-ATT-014` | All attachments on ticket | `TicketId` with 3 attachments | All 3 returned |
| `TICK-ATT-015` | Single attachment by AttachmentId | `AttachmentId` | One record returned with all fields |
| `TICK-ATT-016` | Non-existent AttachmentId | Random Id | Returns `TICKETING_ATTACHMENT_NOT_FOUND` |
| `TICK-ATT-017` | Non-existent TicketId | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-ATT-018` | Soft-deleted excluded | Deleted attachment | Not in results |
| `TICK-ATT-019` | Ticket with no attachments | `TicketId` without any | `Attachments:[]`; no error |

---

### Ticketing-Attachment-Remove

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-ATT-020` | Soft remove | Valid AttachmentId | `IsDeleted = 1`; not in subsequent reads |
| `TICK-ATT-021` | Already removed | Remove again | `Success: true`; idempotent |
| `TICK-ATT-022` | Non-existent attachment | Random Id | Returns `TICKETING_ATTACHMENT_NOT_FOUND` |
| `TICK-ATT-023` | Remove by non-uploader | `RemovedByUserId` ≠ original uploader, non-admin | Returns `TICKETING_ATTACHMENT_REMOVE_FORBIDDEN` |
| `TICK-ATT-024` | Remove by admin | Admin `RemovedByUserId` | Allowed |

---

## Test Cases: Status Operations

### Ticketing-Status-Define

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-STA-001` | Create new status | `Name:"Under Review"`, `IsTerminal:false` | `StatusId` returned; in status list |
| `TICK-STA-002` | Create terminal status | `IsTerminal:true` | Closing a ticket via this status triggers Display-Complete |
| `TICK-STA-003` | Duplicate name | `Name:"Open"` (already exists) | Returns `TICKETING_STATUS_NAME_DUPLICATE` |
| `TICK-STA-004` | Name case sensitivity | `Name:"open"` vs `Name:"Open"` | Treated as duplicates (case-insensitive uniqueness) or distinct — document behaviour |
| `TICK-STA-005` | Empty name | `Name:""` | Returns `TICKETING_STATUS_NAME_REQUIRED` |
| `TICK-STA-006` | SortOrder honoured | `SortOrder:5` | Returned in order when listing statuses |
| `TICK-STA-007` | IsDefault flag — only one default | Set new status as `IsDefault:true` when one already exists | Old default cleared; new status is default |
| `TICK-STA-008` | Update existing status | `StatusId` + updated `Name` | Name changed; tickets referencing this status unaffected |
| `TICK-STA-009` | Delete status with no tickets | `ConfirmDelete:true` | Removed |
| `TICK-STA-010` | Delete status in use | Tickets have this status | Returns `TICKETING_STATUS_IN_USE` |

---

### Ticketing-Status-Transition

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-STA-011` | Valid transition | `Open → In Progress` (in StatusTransitions) | `Success: true`; ticket has new status; history record created |
| `TICK-STA-012` | Invalid transition | `Open → Closed` (not in StatusTransitions) | Returns `TICKETING_STATUS_TRANSITION_INVALID` |
| `TICK-STA-013` | Already at target status | Transition to current status | Returns `TICKETING_STATUS_ALREADY_CURRENT` |
| `TICK-STA-014` | Transition triggers Display-Complete | `ToStatus.IsTerminal = 1` | `Ticketing-Display-Complete` called; banner output |
| `TICK-STA-015` | Transition triggers Display-Bell | Terminal transition | BEL × 3 on stdout |
| `TICK-STA-016` | Transition does NOT trigger Display when non-terminal | `Open → In Progress` | No banner, no bell |
| `TICK-STA-017` | Non-existent TicketId | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-STA-018` | Non-existent ToStatusId | Random Id | Returns `TICKETING_STATUS_NOT_FOUND` |
| `TICK-STA-019` | Non-existent TransitionedByUserId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-STA-020` | Soft-deleted ticket | Deleted Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-STA-021` | History record created | Any valid transition | `TicketHistory` with `FromStatusId` and `ToStatusId` |
| `TICK-STA-022` | TransitionNote optional | Supplied note | Stored in history |
| `TICK-STA-023` | Transition from terminal status (other than via Reopen) | Closed → In Progress directly | Returns `TICKETING_STATUS_TRANSITION_INVALID` (must use Ticket-Reopen) |

---

## Test Cases: Priority Operations

### Ticketing-Priority-Define

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-PRI-001` | Create new priority | `Name:"Urgent"`, `NumericValue:0` | `PriorityId` returned |
| `TICK-PRI-002` | Duplicate name | `Name:"High"` (exists) | Returns `TICKETING_PRIORITY_NAME_DUPLICATE` |
| `TICK-PRI-003` | Empty name | `Name:""` | Returns `TICKETING_PRIORITY_NAME_REQUIRED` |
| `TICK-PRI-004` | IsDefault — only one default | New default set when one exists | Old default cleared |
| `TICK-PRI-005` | Duplicate NumericValue | Two priorities, same `NumericValue` | Returns `TICKETING_PRIORITY_VALUE_DUPLICATE` or documents allowed |
| `TICK-PRI-006` | Update existing priority | `PriorityId` + new `Name` | Name changed; existing tickets unaffected |
| `TICK-PRI-007` | Delete priority in use | Tickets have this priority | Returns `TICKETING_PRIORITY_IN_USE` |
| `TICK-PRI-008` | Delete priority not in use | `ConfirmDelete:true` | Removed |

---

### Ticketing-Priority-Set

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-PRI-009` | Set new priority | Valid `TicketId`, `PriorityId` | Ticket priority updated; history record |
| `TICK-PRI-010` | Set same priority | Same as current | `Success: true`; no-op or history record noting no change |
| `TICK-PRI-011` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-PRI-012` | Non-existent priority | Random Id | Returns `TICKETING_PRIORITY_NOT_FOUND` |
| `TICK-PRI-013` | SetByUserId recorded | Any valid call | History row has `SetByUserId` |
| `TICK-PRI-014` | Set on closed ticket | Terminal ticket | Allowed or returns error — document behaviour |

---

## Test Cases: Category / Tag Operations

### Ticketing-Category-Create

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CAT-001` | Root category | `Name:"Infrastructure"`, no `ParentCategoryId` | `CategoryId` returned; `ParentCategoryId = NULL` |
| `TICK-CAT-002` | Child category | `Name:"Networking"`, `ParentCategoryId` = Infrastructure.Id | `ParentCategoryId` set; hierarchy correct |
| `TICK-CAT-003` | Duplicate name at root | Same name, no parent | Returns `TICKETING_CATEGORY_NAME_DUPLICATE` |
| `TICK-CAT-004` | Duplicate name under same parent | Same name under same parent | Returns `TICKETING_CATEGORY_NAME_DUPLICATE` |
| `TICK-CAT-005` | Same name under different parent | Allowed (sibling paths differ) | Both created successfully |
| `TICK-CAT-006` | Empty name | `Name:""` | Returns `TICKETING_CATEGORY_NAME_REQUIRED` |
| `TICK-CAT-007` | Non-existent ParentCategoryId | Random Id | Returns `TICKETING_CATEGORY_NOT_FOUND` |
| `TICK-CAT-008` | Deep nesting | 5-level category tree | All levels created; full path resolvable |

---

### Ticketing-Category-Assign

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CAT-009` | Assign category to ticket | Valid `TicketId`, `CategoryId` | Ticket `CategoryId` updated |
| `TICK-CAT-010` | Reassign category | Different valid `CategoryId` | Updated; history record |
| `TICK-CAT-011` | Clear category | `CategoryId:null` | `CategoryId` set to NULL |
| `TICK-CAT-012` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-CAT-013` | Non-existent category | Random Id | Returns `TICKETING_CATEGORY_NOT_FOUND` |
| `TICK-CAT-014` | History record created | Any assignment | `TicketHistory` with old → new category |

---

### Ticketing-Tag-Add

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CAT-015` | Add tag | `TicketId`, `Tag:"bug"` | `TicketTags` row created |
| `TICK-CAT-016` | Idempotent — same tag twice | Call twice with same tag | Second call: `Success: true`; no duplicate row; `Action:"already_present"` |
| `TICK-CAT-017` | Multiple tags per ticket | Add `"bug"`, `"regression"`, `"ui"` separately | All 3 in `TicketTags` |
| `TICK-CAT-018` | Empty tag name | `Tag:""` | Returns `TICKETING_TAG_NAME_REQUIRED` |
| `TICK-CAT-019` | Whitespace-only tag | `Tag:"  "` | Returns `TICKETING_TAG_NAME_REQUIRED` |
| `TICK-CAT-020` | Tag name normalisation | `Tag:"BUG"` then `Tag:"bug"` | Treated as same tag (case-folded) or distinct — document |
| `TICK-CAT-021` | Tag with special characters | `Tag:"v2.0-fix"` | Stored as-is (hyphens and dots allowed) |
| `TICK-CAT-022` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |

---

### Ticketing-Tag-Remove

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-CAT-023` | Remove existing tag | `TicketId`, `Tag:"bug"` | Row deleted (hard delete; tags have no audit requirement) |
| `TICK-CAT-024` | Remove non-present tag | Tag not on ticket | `Success: true`; no-op (idempotent) |
| `TICK-CAT-025` | Non-existent ticket | Random Id | Returns `TICKETING_TICKET_NOT_FOUND` |
| `TICK-CAT-026` | Remove all tags one by one | Three tags, removed in sequence | After all three, ticket has no tags |

---

## Test Cases: User Operations

### Ticketing-User-Register

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-USR-001` | Happy path | `Username`, `Email`, `Password`, `DisplayName` | `UserId` returned; `IsActive:true`; password NOT returned |
| `TICK-USR-002` | Duplicate email | Email already registered | Returns `TICKETING_USER_EMAIL_DUPLICATE` |
| `TICK-USR-003` | Duplicate username | Username taken | Returns `TICKETING_USER_USERNAME_DUPLICATE` |
| `TICK-USR-004` | Email case-insensitive uniqueness | Register `User@Example.com` then `user@example.com` | Returns `TICKETING_USER_EMAIL_DUPLICATE` |
| `TICK-USR-005` | Invalid email format | `Email:"notanemail"` | Returns `TICKETING_USER_EMAIL_INVALID` |
| `TICK-USR-006` | Empty email | `Email:""` | Returns `TICKETING_USER_EMAIL_REQUIRED` |
| `TICK-USR-007` | Empty username | `Username:""` | Returns `TICKETING_USER_USERNAME_REQUIRED` |
| `TICK-USR-008` | Password hashed | Inspect DB after register | `PasswordHash` column is NOT plain text |
| `TICK-USR-009` | Password not in output | Response JSON | No `Password` or `PasswordHash` field in returned object |
| `TICK-USR-010` | IsAdmin flag | `IsAdmin:true` | User registered as admin |
| `TICK-USR-011` | IsAdmin defaults to false | No `IsAdmin` field | `IsAdmin: false` |
| `TICK-USR-012` | DisplayName Unicode | `DisplayName:"山田 太郎"` | Stored and returned correctly |
| `TICK-USR-013` | CreatedAt auto-set | Any register | `CreatedAt` is ISO-8601 |

---

### Ticketing-User-Read

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-USR-014` | Read by UserId | Valid UUID | Full user object returned |
| `TICK-USR-015` | Read by Username | `Username:"admin"` | Full user object returned |
| `TICK-USR-016` | Read by Email | `Email:"admin@example.com"` | Full user object returned |
| `TICK-USR-017` | No identifier supplied | No input fields | Returns `TICKETING_USER_IDENTIFIER_REQUIRED` |
| `TICK-USR-018` | Non-existent UserId | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-USR-019` | Deactivated user, default | Inactive user | Returned with `IsActive: false` |
| `TICK-USR-020` | Password / hash not in output | Any read | `PasswordHash` absent from returned object |

---

### Ticketing-User-Update

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-USR-021` | Update DisplayName | New display name | Persisted; `UpdatedAt` refreshed |
| `TICK-USR-022` | Update Email | New unique email | Persisted; case-normalised |
| `TICK-USR-023` | Update Email to duplicate | Email belonging to another user | Returns `TICKETING_USER_EMAIL_DUPLICATE` |
| `TICK-USR-024` | Update Password | New password | New hash stored; old credentials rejected after update |
| `TICK-USR-025` | Non-existent user | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-USR-026` | Deactivated user | Inactive UserId | Returns `TICKETING_USER_INACTIVE` |
| `TICK-USR-027` | No updatable fields supplied | Empty update | `Success: true`; no change (or validation error — document) |
| `TICK-USR-028` | Password not logged | Any update | Updated password not echoed in response |

---

### Ticketing-User-Deactivate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-USR-029` | Deactivate active user | Valid `UserId` | `IsActive: false`; `DeactivatedAt` set |
| `TICK-USR-030` | Already deactivated | Inactive user | `Success: true`; idempotent |
| `TICK-USR-031` | Non-existent user | Random UUID | Returns `TICKETING_USER_NOT_FOUND` |
| `TICK-USR-032` | Last admin guard | Only admin in system, deactivate that admin | Returns `TICKETING_USER_LAST_ADMIN` |
| `TICK-USR-033` | Non-last admin | Two admins; deactivate one | Succeeds |
| `TICK-USR-034` | Deactivated user's tickets remain | Deactivate user with open tickets | Tickets unaffected (not reassigned automatically) |
| `TICK-USR-035` | Deactivated user cannot authenticate | Post-deactivation authenticate attempt | Returns `TICKETING_AUTH_FAILED` (generic) |

---

### Ticketing-User-Authenticate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-USR-036` | Valid credentials | Correct `Username` + `Password` | `Success: true`; `SessionToken` returned; `ExpiresAt` set |
| `TICK-USR-037` | Wrong password | Correct username, wrong password | Returns `TICKETING_AUTH_FAILED` (no distinction from not-found) |
| `TICK-USR-038` | Non-existent username | Unknown username, any password | Returns `TICKETING_AUTH_FAILED` (same error as wrong password) |
| `TICK-USR-039` | Deactivated account | Inactive user, correct password | Returns `TICKETING_AUTH_FAILED` |
| `TICK-USR-040` | Generic error — no info leak | All three above error paths | All return exactly `TICKETING_AUTH_FAILED`; no hint about existence |
| `TICK-USR-041` | Empty username | `Username:""` | Returns `TICKETING_AUTH_FAILED` (not a special validation code) |
| `TICK-USR-042` | Empty password | `Password:""` | Returns `TICKETING_AUTH_FAILED` |
| `TICK-USR-043` | Session stored in Sessions table | Successful auth | Row in `Sessions` with `UserId`, `Token`, `ExpiresAt` |
| `TICK-USR-044` | Token is random / unpredictable | Two auths for same user | Two different `SessionToken` values |
| `TICK-USR-045` | Session expiry | `ExpiresAt` in output | `ExpiresAt > now`; skill documents the TTL |
| `TICK-USR-046` | Timing consistency | Compare auth time for existing-wrong vs non-existent-wrong | Response times within ±100 ms of each other (constant-time compare) |

---

## Test Cases: Report Operations

### Ticketing-Report-Summary

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-RPT-001` | Count by status | M-tier database | `ByStatus` array with count per status (including 0-count statuses) |
| `TICK-RPT-002` | Count by priority | M-tier database | `ByPriority` array with count per priority |
| `TICK-RPT-003` | Count by assignee | M-tier, mixed assignees | `ByAssignee` array; unassigned tickets counted separately |
| `TICK-RPT-004` | Total open vs closed | Any database | `TotalOpen`, `TotalClosed`, `TotalCancelled` |
| `TICK-RPT-005` | Date range filter | `CreatedAfter`, `CreatedBefore` | Summary reflects only tickets in range |
| `TICK-RPT-006` | Empty database | No tickets | All counts zero; no error |
| `TICK-RPT-007` | Soft-deleted tickets excluded | Deleted tickets in DB | Deleted tickets not counted in summary |

---

### Ticketing-Report-Generate

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-RPT-008` | Open tickets report | `ReportType:"open"` | All open tickets; sorted by priority then age |
| `TICK-RPT-009` | Closed-in-period report | `ReportType:"closed"`, date range | Only tickets closed in range |
| `TICK-RPT-010` | Assigned-to-user report | `ReportType:"by-assignee"`, `AssigneeId` | Only that user's tickets |
| `TICK-RPT-011` | Overdue report | `ReportType:"overdue"`, `DueDateField` | Tickets past due date |
| `TICK-RPT-012` | Unknown report type | `ReportType:"invalid"` | Returns `TICKETING_REPORT_TYPE_UNKNOWN` |
| `TICK-RPT-013` | Empty result set | Report with no matching tickets | `Tickets:[]`; `Success: true` |
| `TICK-RPT-014` | Pagination | L-tier, `Limit:25, Offset:0` | 25 rows; `TotalCount` = full count |

---

### Ticketing-Report-Export

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-RPT-015` | CSV export | `Format:"csv"` | Valid CSV with header row; all non-deleted tickets |
| `TICK-RPT-016` | JSON export | `Format:"json"` | Valid JSON array |
| `TICK-RPT-017` | CSV — Unicode in fields | Ticket with Unicode summary | CSV encoded as UTF-8 with BOM or documented encoding |
| `TICK-RPT-018` | CSV — commas in field values | Summary contains comma | Field quoted per RFC 4180 |
| `TICK-RPT-019` | CSV — line breaks in Description | Multiline Description | Field quoted with embedded newline |
| `TICK-RPT-020` | Filter applied before export | `StatusId` filter | Only matching tickets exported |
| `TICK-RPT-021` | Export path returned | Any export | `FilePath` in output; file exists at that path |
| `TICK-RPT-022` | Unknown format | `Format:"xlsx"` | Returns `TICKETING_REPORT_FORMAT_UNKNOWN` |
| `TICK-RPT-023` | Empty dataset export | No matching tickets | Empty CSV (header only) or `[]` JSON; no error |

---

## Test Cases: Display Operations

### Ticketing-Display-Complete

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-DSP-001` | Unicode banner — all fields | `TicketNumber:"TKT-0001"`, `Summary:"Fix login"`, `ClosedAt`, `ClosedByDisplayName:"Alice"` | Full Unicode block-art `COMPLETE` banner on stdout |
| `TICK-DSP-002` | ASCII fallback banner | `UseUnicode:false` | Plain-ASCII `COMPLETE` banner emitted |
| `TICK-DSP-003` | All interpolation fields present | Any call | `{TicketNumber}`, `{Summary}`, `{ClosedAt}`, `{ClosedByDisplayName}` all substituted |
| `TICK-DSP-004` | Long Summary truncated in banner | 200-char Summary | Banner truncates or wraps to fit fixed width; no layout broken |
| `TICK-DSP-005` | Unicode in Summary | `Summary:"修復 🛠"` | Banner renders correctly (no `?` placeholders) |
| `TICK-DSP-006` | Bell emitted | Any call | BEL character(s) on stdout |
| `TICK-DSP-007` | BellCount default | `BellCount` omitted | Defaults to 3 BEL characters |
| `TICK-DSP-008` | BellCount explicit | `BellCount:1` | Exactly 1 BEL |
| `TICK-DSP-009` | Missing TicketNumber | No `TicketNumber` | Returns `TICKETING_DISPLAY_FIELD_REQUIRED` |
| `TICK-DSP-010` | Missing ClosedByDisplayName | No name | Gracefully substitutes `"(unknown)"` or returns error — document |
| `TICK-DSP-011` | RenderedBanner in output | Any call | `RenderedBanner` field contains the emitted text |

---

### Ticketing-Display-Alert

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-DSP-012` | Assigned event | `Event:"TICKET ASSIGNED"`, `TicketNumber`, `Detail:"Assigned to: Bob"` | Unicode alert banner on stdout |
| `TICK-DSP-013` | Escalated event | `Event:"TICKET ESCALATED"` | Same structure, different event text |
| `TICK-DSP-014` | ASCII fallback | `UseUnicode:false` | Plain-ASCII border used |
| `TICK-DSP-015` | Bell emitted | Any call | BEL × `BellCount` on stdout |
| `TICK-DSP-016` | BellCount default | Omitted | Defaults to 1 |
| `TICK-DSP-017` | BellCount max | `BellCount:10` | 10 BEL characters |
| `TICK-DSP-018` | BellCount exceeded | `BellCount:11` | Returns `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED` |
| `TICK-DSP-019` | Missing Event | No `Event` field | Returns validation error |
| `TICK-DSP-020` | Long Detail truncated | Detail > banner width | Text fits banner; no layout overflow |

---

### Ticketing-Display-Bell

| ID | Description | Inputs | Expected Result |
|---|---|---|---|
| `TICK-DSP-021` | Default count | `Count` omitted | 1 BEL emitted; `EmittedCount:1` |
| `TICK-DSP-022` | Count 1 | `Count:1` | 1 BEL |
| `TICK-DSP-023` | Count 3 | `Count:3` | 3 distinct BEL characters |
| `TICK-DSP-024` | Count 10 (max) | `Count:10` | 10 BEL characters; `EmittedCount:10` |
| `TICK-DSP-025` | Count 11 | `Count:11` | Returns `TICKETING_DISPLAY_BELL_COUNT_EXCEEDED` |
| `TICK-DSP-026` | Count 0 | `Count:0` | Returns validation error (`Count` must be ≥ 1) |
| `TICK-DSP-027` | Negative count | `Count:-1` | Returns validation error |
| `TICK-DSP-028` | Non-integer count | `Count:"three"` | Returns validation error |
| `TICK-DSP-029` | Synchronous emission | `Count:3` | Three audibly distinct rings (not one burst); verified by timing: each `Console.Write('\a')` is a separate call |
| `TICK-DSP-030` | Does not use Console.Beep() | Code review / implementation note | Implementation verified to use `Console.Write('\a')` not `Console.Beep()` |
| `TICK-DSP-031` | No other output | Any valid count | stdout contains ONLY the BEL characters; no extra newlines, labels, or text |

---

## Performance Benchmarks

All benchmarks use a dedicated `AiXBase/perf-ticketing.db` with the full schema. Median of 3 runs must meet the target.

### Ticket Throughput

| ID | Description | Scale | Target |
|---|---|---|---|
| `TICK-PERF-001` | Create tickets sequentially | 1 000 tickets, one at a time | ≤ 30 s (≥ 33 tickets/sec) |
| `TICK-PERF-002` | Create tickets in single transaction | 10 000 tickets via XBase-Transaction | ≤ 20 s |
| `TICK-PERF-003` | Close 1 000 tickets | L-tier seeded, then bulk close | ≤ 60 s |
| `TICK-PERF-004` | Read ticket by TicketId | XL-tier, no index on Id (it's PK) | ≤ 5 ms per read |
| `TICK-PERF-005` | Read ticket by TicketNumber | XL-tier, index on TicketNumber | ≤ 10 ms per read |

### Query Throughput

| ID | Description | Scale | Target |
|---|---|---|---|
| `TICK-PERF-006` | Query by Status (indexed) | XL-tier, ~25% per status | ≤ 200 ms |
| `TICK-PERF-007` | Query by Assignee (indexed) | XL-tier, 10 assignees | ≤ 200 ms |
| `TICK-PERF-008` | Full-text search on Summary | L-tier, LIKE '%login%' | ≤ 2 s (no FTS index — documents expectation) |
| `TICK-PERF-009` | Combined filter: Status + Priority + Assignee | L-tier | ≤ 500 ms |
| `TICK-PERF-010` | Paginated query, deep offset | XL-tier, `LIMIT 25 OFFSET 90000` | ≤ 1 s |

### Comment and Attachment Throughput

| ID | Description | Scale | Target |
|---|---|---|---|
| `TICK-PERF-011` | Add 1 000 comments to one ticket | 1 000 comments, one ticket | ≤ 30 s |
| `TICK-PERF-012` | Read 1 000 comments on one ticket | 1 000-comment thread | ≤ 500 ms |
| `TICK-PERF-013` | Add 100 attachments to one ticket | Metadata only (no file I/O) | ≤ 5 s |

### Report Throughput

| ID | Description | Scale | Target |
|---|---|---|---|
| `TICK-PERF-014` | Summary report | XL-tier | ≤ 1 s |
| `TICK-PERF-015` | Generate open tickets report | XL-tier (50% open) | ≤ 2 s |
| `TICK-PERF-016` | Export 10 000 tickets to CSV | L-tier | ≤ 10 s |
| `TICK-PERF-017` | Export 100 000 tickets to JSON | XL-tier | ≤ 60 s |

### History Table Growth

| ID | Description | Scale | Target |
|---|---|---|---|
| `TICK-PERF-018` | TicketHistory row count after L-tier churn | Create + update + assign + close 10 000 tickets | ≥ 40 000 history rows; `integrity_check` passes |
| `TICK-PERF-019` | Query ticket history for one ticket | Ticket with 100 history rows | ≤ 20 ms |

### Authentication

| ID | Description | Scale | Target |
|---|---|---|---|
| `TICK-PERF-020` | Authenticate 1 000 users | 1 000 sequential auth calls (all valid) | ≤ 60 s (hashing cost expected) |
| `TICK-PERF-021` | Failed auth timing | 1 000 wrong-password attempts | No faster than valid auth (constant-time verify) |

---

## Stress Tests

| ID | Description | Setup | Pass Criterion |
|---|---|---|---|
| `TICK-STRESS-001` | 100 000 tickets end-to-end | Create 100 000 tickets with varied statuses, priorities, assignees | All created; `Summary report` counts correct; `integrity_check` passes |
| `TICK-STRESS-002` | Deep comment thread | 10 000 comments on a single ticket | All stored; paginated read works; no timeout |
| `TICK-STRESS-003` | Many tags per ticket | 500 distinct tags on one ticket | All stored; no FK or uniqueness errors |
| `TICK-STRESS-004` | High-volume transitions | Cycle 1 000 tickets through Open → In Progress → Resolved → Closed | All terminal; 4 000+ history rows; no lock errors |
| `TICK-STRESS-005` | Mass escalation | Escalate 10 000 tickets from Low → High | All priorities updated; alerts emitted (but stdout not checked for every line); no crash |
| `TICK-STRESS-006` | Concurrent ticket creation | 10 threads each creating 1 000 tickets | No duplicate ticket numbers; final count = 10 000; `integrity_check` passes |
| `TICK-STRESS-007` | Concurrent read + write | 5 readers querying while 1 writer creates tickets | Readers return consistent snapshots; no corruption |
| `TICK-STRESS-008` | Reopen/close cycle × 1 000 | Same ticket closed and reopened 1 000 times | 2 000+ history rows; `ClosedAt` reflects latest close; banner emitted each time |
| `TICK-STRESS-009` | Report on XL-tier with history | Generate all report types on 100 000-ticket DB with full history | All reports complete within 3× their PERF targets |
| `TICK-STRESS-010` | Large CSV export under memory pressure | Export 100 000 tickets with streaming | Process stays under 500 MB RSS; file written completely |
| `TICK-STRESS-011` | User registration at scale | Register 10 000 users with unique emails | No duplicate session tokens; no auth timing regressions |
| `TICK-STRESS-012` | Tag deduplication at scale | Add the same tag to 50 000 tickets | No duplicate `TicketTags` rows; all idempotent calls succeed |

---

## Security Tests

| ID | Description | Attack Vector | Pass Criterion |
|---|---|---|---|
| `TICK-SEC-001` | XSS in Summary | `Summary:"<img src=x onerror=alert(1)>"` | Stored as literal text; not interpreted on read |
| `TICK-SEC-002` | XSS in Comment body | `Body:"<script>...</script>"` | Stored as literal text |
| `TICK-SEC-003` | SQL injection via SearchText | `SearchText:"' OR 1=1--"` | Parameterised query; no extra rows returned |
| `TICK-SEC-004` | SQL injection via Username (Authenticate) | `Username:"admin'--"` | Returns `TICKETING_AUTH_FAILED`; no bypass |
| `TICK-SEC-005` | SQL injection via Tag name | `Tag:"'; DROP TABLE TicketTags--"` | Returns `TICKETING_TAG_NAME_REQUIRED` or validation error; no DROP |
| `TICK-SEC-006` | SQL injection via FileName | `FileName:"'; DELETE FROM Attachments--"` | Stored as literal or validation error; no DELETE |
| `TICK-SEC-007` | Path traversal in FilePath (Attachment) | `FilePath:"../../Windows/System32/hosts"` | Validation error or stored as literal (if path is metadata-only); no actual file written outside `AiXBase/` |
| `TICK-SEC-008` | Auth timing — existence oracle | Compare response time for non-existent vs wrong-password user | Within ±100 ms; no statistical distinguishability |
| `TICK-SEC-009` | Password in API response | Register + authenticate | `Password` and `PasswordHash` absent from all response objects |
| `TICK-SEC-010` | Session token entropy | 1 000 consecutive tokens for same user | No two identical; passes birthday-paradox check for 128-bit token space |
| `TICK-SEC-011` | Privilege escalation via Update | Regular user sets `IsAdmin:true` on own record via User-Update | `IsAdmin` not updatable via User-Update (admin-only field) |
| `TICK-SEC-012` | IDOR — read another user's internal comment | Non-admin `CallerId` reading `IsInternal:true` comment | Returns `TICKETING_COMMENT_NOT_FOUND` (comment excluded) |
| `TICK-SEC-013` | Mass assignment in Ticket-Create | Extra field `IsDeleted:0` forced in input | Ignored; `IsDeleted` defaults to 0 regardless |
| `TICK-SEC-014` | ConfirmDelete string spoofing | `ConfirmDelete:"true"` (string) | Rejected or coerced to false; delete not executed |
| `TICK-SEC-015` | Null byte in Username | `Username:"admin\x00"` | Validation error or null stripped; no truncation-based bypass |
| `TICK-SEC-016` | Extremely long password | `Password:"x" × 100 000` | Handled gracefully (capped at safe length for hashing); no DoS via bcrypt work factor |

---

## Integration Tests

These tests validate multi-skill workflows and cross-skill contracts.

| ID | Description | Skills Involved | Expected Result |
|---|---|---|---|
| `TICK-INT-001` | Full lifecycle: create → assign → comment → close | Ticket-Create, Ticket-Assign, Comment-Add, Ticket-Close | Banner + bell on close; 4+ history rows; comment readable after close |
| `TICK-INT-002` | Escalate triggers alert → verify history | Ticket-Create, Ticket-Escalate | Alert banner on stdout; priority history row |
| `TICK-INT-003` | Status-Transition → IsTerminal → Display-Complete | Status-Transition to Closed | Banner emitted by Status-Transition (not only by Ticket-Close) |
| `TICK-INT-004` | Ticket-Reopen after close → re-close | Ticket-Close, Ticket-Reopen, Ticket-Close | Two complete history cycles; two banners |
| `TICK-INT-005` | Report after lifecycle | Full lifecycle × M-tier, then Report-Summary | Summary counts match known state |
| `TICK-INT-006` | Export then verify file | Report-Export CSV | File is valid UTF-8 CSV; row count = total tickets |
| `TICK-INT-007` | Deactivate user → verify tickets unchanged | User-Deactivate on assignee | Assignee's tickets still show `AssigneeId`; not cleared |
| `TICK-INT-008` | Authenticate → use session | User-Authenticate, then skill call with `SessionToken` | Skill accepts token; user identity resolved |

---

## Acceptance Criteria

A build of the Ticketing System is considered **release-ready** when:

1. **All functional tests pass** — every `TICK-TKT-*`, `TICK-CMT-*`, `TICK-ATT-*`, `TICK-STA-*`, `TICK-PRI-*`, `TICK-CAT-*`, `TICK-USR-*`, `TICK-RPT-*`, `TICK-DSP-*`, `TICK-INT-*` test ID returns the stated expected result.

2. **All XBase tests pass first** — the Ticketing System is built on XBase; the full XBase test suite must pass before any Ticketing test is run.

3. **Every write produces a TicketHistory row** — for all skills that mutate a ticket (Create, Update, Close, Reopen, Assign, Escalate, Status-Transition, Priority-Set, Category-Assign), a corresponding `TicketHistory` row must exist. Auditors verify by counting history rows after each test.

4. **Bell fires correctly on terminal transitions** — `TICK-DSP-021` through `TICK-DSP-031` all pass, and `TICK-TKT-054`, `TICK-STA-015` confirm bell is triggered by the correct skills.

5. **All performance benchmarks pass** — median of 3 runs meets every target in `TICK-PERF-*`.

6. **All stress tests pass** — every `TICK-STRESS-*` test completes without process crash, data corruption, or unrecovered lock. `PRAGMA integrity_check` returns `ok` after each.

7. **All security tests pass** — every `TICK-SEC-*` test produces the stated pass criterion. No SQL injection, no auth bypass, no credential leakage, no path traversal.

8. **Error envelope conformance** — every error path returns `{ "Success": false, "ErrorCode": "TICKETING_...", "Message": "...", "SkillName": "..." }` with no stack traces or internal paths in `Message`.

9. **Generic auth error enforced** — `TICK-USR-036` through `TICK-USR-046` must confirm that wrong-password, non-existent-user, and deactivated-user all return identically-worded `TICKETING_AUTH_FAILED` with no distinguishing information in the message.

10. **Regression gate** — re-running the full suite after any skill file change must produce no new failures in either the Ticketing System suite or the XBase suite.
