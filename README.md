# AiXBase

AiXBase is an AI Skills distribution that gives any AI harness a complete file-backed database engine (**XBase**) and a full helpdesk ticketing system (**TicketingSystem**) — implemented entirely as plain markdown skill files. There are no binaries, no SDKs, no runtime dependencies. The AI reads and writes structured binary files directly using OS file system primitives described in the skill steps.

---

## AI Quick Install

```
Manifest: https://github.com/StewartScottRogers/AiXBase/raw/master/manifest.json
Download: https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip

Install contract: Download skills.zip, extract it, place the markdown files
where your AI harness loads skill definitions. No build step required.
Partial installs are supported — you may extract individual bundle folders.
The TicketingSystem bundle depends on the XBase bundle.
```

---

## What is XBase

XBase is a skill-based, file-backed database engine. Every database operation — schema management, record CRUD, queries, indexes, transactions, backups — is a discrete markdown skill file. XBase stores data in **dBASE III binary format** (`.dbf` files and `.ndx` B-tree indexes) using only OS file system primitives.

**No external database engine. No ORM. No package dependencies.**

- 30 core skills across 7 groups (Database, Schema, Record, Query, Index, Transaction, Backup)
- 3 admin skills (Execute, Inspect, Maintain)
- 1 runtime environment verification skill

→ [XBase Skill Reference](SKILLS/XBase/XBase.wiki.md)

---

## What is the Ticketing System

The Ticketing System is a full-featured helpdesk issue tracker built entirely on XBase skills. It has no direct file I/O — every read and write routes through XBase skills.

- 35 skills across 9 groups (Ticket, Comment, Attachment, Status, Priority, Category, User, Report, Display)
- Full ticket lifecycle with history, assignments, escalation, and status workflows
- User authentication with internal credential hashing and session tokens
- Terminal display with BEL notifications and ASCII art completion banners

→ [TicketingSystem Skill Reference](SKILLS/TicketingSystem/TicketingSystem.wiki.md)

---

## How TicketingSystem Uses XBase

```
User Request
    │
    ▼
Ticketing Skill          (e.g., Ticketing-Ticket-Create)
    │  validates business rules, then delegates all I/O:
    ▼
XBase Record Skill       (XBase-Record-Insert)
    │  encodes and appends a binary DBF record:
    ▼
OS File System           (append-binary-record → Tickets.dbf)
```

Every Ticketing skill is a workflow coordinator: it validates business rules (status transitions, permission checks, audit log entries) and issues XBase skill calls for all file I/O. No Ticketing skill reads or writes files directly. This means any storage engine that implements the XBase skill contract can back the Ticketing system.

---

## Usage Examples

### Example 1 — Full ticket lifecycle

```
# Setup (once per environment)
XBase-Database-Initialize  DatabaseName:"ticketing"
XBase-Database-Connect     DatabaseName:"ticketing"  ConnectionName:"ticketing"

Ticketing-Status-Define    Name:"Open"         IsTerminal:false
Ticketing-Status-Define    Name:"In Progress"  IsTerminal:false
Ticketing-Status-Define    Name:"Closed"       IsTerminal:true

Ticketing-Priority-Define  Name:"High"    Weight:1
Ticketing-Priority-Define  Name:"Medium"  Weight:2  IsDefault:true

Ticketing-User-Register    Username:"alice"  Email:"alice@example.com"  Password:"secret"

# Authenticate
Ticketing-User-Authenticate  Username:"alice"  Password:"secret"
# → SessionToken, UserId

# Create a ticket
Ticketing-Ticket-Create
  Summary:"Checkout page times out on mobile"
  Description:"Reproducible on iOS 17 / Safari 17. Occurs after entering card details."
  ReportedByUserId:<alice-id>
# → TicketId:1  TicketNumber:"TKT-0001"

# Work the ticket
Ticketing-Ticket-Assign      TicketId:1  AssignToUserId:<alice-id>  AssignedByUserId:<alice-id>
Ticketing-Status-Transition  TicketId:1  ToStatusId:<in-progress-id>  ChangedByUserId:<alice-id>
Ticketing-Comment-Add        TicketId:1  AuthorUserId:<alice-id>
                              Body:"Traced to missing timeout on payment gateway. Fix in progress."

# Close the ticket — emits COMPLETE banner + 3 BEL characters
Ticketing-Ticket-Close       TicketId:1  ClosedByUserId:<alice-id>
                              Comment:"Added 30-second timeout; deployed to staging."
```

### Example 2 — Escalation

```
Ticketing-Ticket-Escalate
  TicketId:2
  EscalatedByUserId:<alice-id>
  NewPriorityId:<high-id>
  Comment:"Customer blocked on production; SLA breach in 2 hours."
# Priority raised; assignee notified; history row appended
# Emits ALERT banner + 1 BEL character
```

### Example 3 — Reporting

```
# Query open tickets ordered by priority
Ticketing-Ticket-Query
  Filters:[{Field:"StatusId", Operator:"=", Value:<open-id>}]
  SortBy:"PriorityId"
  SortDirection:"ASC"

# Summary report
Ticketing-Report-Summary

# Date-range report, exported to CSV
Ticketing-Report-Generate  FromDate:"2026-01-01"  ToDate:"2026-06-30"
Ticketing-Report-Export    Format:"CSV"  OutputPath:"report-h1-2026.csv"
```

### Example 4 — AI agent autonomous install

```
# Agent reads manifest.json → discovers two bundles; ticketing depends_on xbase
# Agent downloads skills.zip, extracts XBase/ and TicketingSystem/ folders
# Agent configures its harness to load the extracted skill files
# Agent runs Example 1 setup sequence above
# System is now operational — no human wrote any code
```

---

## Human Install

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip" -OutFile skills.zip; Expand-Archive skills.zip -DestinationPath .
```

**bash / curl:**
```bash
curl -L https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip -o skills.zip && unzip skills.zip
```

**Manual:**
1. Go to [Releases](https://github.com/StewartScottRogers/AiXBase/releases/latest).
2. Download `skills.zip`.
3. Extract to the directory your AI harness scans for skill definitions.

---

## SKILLS Catalog

| Bundle | Skills | Groups | Wiki |
|--------|--------|--------|------|
| XBase | 34 | Database, Schema, Record, Query, Index, Transaction, Backup, Admin, Runtime | [XBase.wiki.md](SKILLS/XBase/XBase.wiki.md) |
| TicketingSystem | 35 | Ticket, Comment, Attachment, Status, Priority, Category, User, Report, Display | [TicketingSystem.wiki.md](SKILLS/TicketingSystem/TicketingSystem.wiki.md) |

**Total: 69 skills** across 2 bundles and 18 operation groups.

Machine-readable catalog: [manifest.json](manifest.json)

---

## Extending the Distribution

Adding a new skill bundle requires only: create skill files under `SKILLS/{BundleName}/{Group}/`, write a `{BundleName}.wiki.md`, add an entry to `manifest.json`, register files in `SKILLS.projitems`, and cut a new release.

The skill file format — Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list — is the stable interface contract. Any consumer can depend on it. See [Repository-Presentation-PRD.md](ProductRequirementsDocuments/Repository-Presentation-PRD.md) for the full extensibility model.
