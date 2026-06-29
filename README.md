# AiXBase

AiXBase is an AI Skills distribution — 96 plain markdown skill files that give any AI harness a file-backed database engine (**XBase**), a SQL translation layer (**XBase UniversalSQL**), a full helpdesk ticketing system (**TicketingSystem**), and an on-the-fly RDF/OWL ontology generator (**Ontology**). There are no binaries, no SDKs, no runtime dependencies. The AI reads and writes structured binary files directly using OS file system primitives described in the skill steps.

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

## What is XBase UniversalSQL

XBase UniversalSQL is a SQL translation layer that sits above the 35 XBase skills. It accepts a standard SQL statement as plain text, parses it into an AST, maps it to one or more XBase skill calls, and returns results in a unified envelope — no new file I/O primitives, no storage engine changes.

- 7 skills across 2 groups (UniversalSQL core, UniversalSQL-Admin)
- Supports SELECT, INSERT, UPDATE, DELETE, DDL, TCL, SHOW TABLES, DESCRIBE, EXPLAIN, BACKUP/RESTORE
- Named parameter binding (`?name` placeholders), transaction routing, pre-execution validation
- Admin skills: interactive SQL REPL, execution plan inspector, SQL DDL extractor
- Claude Code slash commands: `/sql`, `/explain`, `/schema`

Depends on the XBase bundle. → [XBase UniversalSQL Skill Reference](SKILLS/XBase/UniversalSQL/XBase-UniversalSQL.wiki.md)

---

## What is Ontology

The Ontology bundle maps any connected XBase database into RDF/OWL format on the fly — no pre-authored `.owl` files required. It introspects a live schema, applies deterministic OWL mapping rules, and returns an in-session `OntologyDocument` that can be queried, validated, and serialized.

- 13 skills across 8 groups (Admin, Namespace, Build, Populate, Query, Validate, Export, Session)
- Tables → `owl:Class`; FK columns → `owl:ObjectProperty`; other columns → `owl:DatatypeProperty`
- Admin skills: inspect document health, diff two documents, rebuild from live schema, guided admin session
- BGP query evaluation; OWL schema and individual conformance validation
- Export to Turtle, JSON-LD, RDF-XML, N-Triples

Depends on the XBase bundle. → [Ontology Skill Reference](SKILLS/Ontology/Ontology.wiki.md)

---

## What is XBase

XBase is a skill-based, file-backed database engine. Every database operation — schema management, record CRUD, queries, indexes, transactions, backups — is a discrete markdown skill file. XBase stores data in **dBASE III binary format** (`.dbf` files and `.ndx` B-tree indexes) using only OS file system primitives.

**No external database engine. No ORM. No package dependencies.**

- 35 skills across 9 groups (Database, Schema, Record, Query, Index, Transaction, Backup, Admin, Runtime)
- Full DDL, CRUD, composite queries, transactions with savepoints, backup/restore
- 4 admin skills: dynamic dispatch, health inspection, maintenance, guided interactive session

→ [XBase Skill Reference](SKILLS/XBase/XBase.wiki.md)

---

## What is the Ticketing System

The Ticketing System is a full-featured helpdesk issue tracker built entirely on XBase skills. It has no direct file I/O — every read and write routes through XBase skills.

- 41 skills across 11 groups (Ticket, Comment, Attachment, Status, Priority, Category, User, Report, Display, Archive, Session)
- Full ticket lifecycle with history, assignments, escalation, and status workflows
- Two-tier archiving: pack archived tickets to a named archive database; restore on demand
- User authentication with internal credential hashing and session tokens
- Terminal display with BEL notifications and ASCII art completion banners

Depends on the XBase bundle. → [TicketingSystem Skill Reference](SKILLS/TicketingSystem/TicketingSystem.wiki.md)

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
  ReporterUserId:<alice-id>
# → TicketId:1  TicketNumber:"TKT-0001"

# Work the ticket
Ticketing-Ticket-Assign      TicketId:1  AssignToUserId:<alice-id>  AssignedByUserId:<alice-id>
Ticketing-Status-Transition  TicketId:1  ToStatusId:<in-progress-id>  ActorUserId:<alice-id>
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

### Example 4 — Ontology from a live database

```
# Connect to an existing XBase database
XBase-Database-Connect   DatabaseName:"ticketing"  ConnectionName:"ticketing"

# Define the namespace
Ontology-Namespace-Define  DatabaseName:"ticketing"
# → Namespace object: BaseIRI, Prefix, PrefixMap

# Build the schema ontology
Ontology-Build-Schema   ConnectionName:"ticketing"  Namespace:<above>
# → OntologyDocument with Classes, DatatypeProperties, ObjectProperties

# Validate and export
Ontology-Validate-Schema   OntologyDocument:<above>
Ontology-Export-Serialize  OntologyDocument:<above>  Format:"Turtle"  OutputPath:"ticketing.ttl"
```

### Example 5 — AI agent autonomous install

```
# Agent reads manifest.json → discovers three bundles; ontology and ticketing depend_on xbase
# Agent downloads skills.zip, extracts all three bundle folders
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
| XBase UniversalSQL | 7 | UniversalSQL, UniversalSQL-Admin | [XBase-UniversalSQL.wiki.md](SKILLS/XBase/UniversalSQL/XBase-UniversalSQL.wiki.md) |
| Ontology | 13 | Admin, Namespace, Build, Populate, Query, Validate, Export, Session | [Ontology.wiki.md](SKILLS/Ontology/Ontology.wiki.md) |
| XBase | 35 | Database, Schema, Record, Query, Index, Transaction, Backup, Admin, Runtime | [XBase.wiki.md](SKILLS/XBase/XBase.wiki.md) |
| TicketingSystem | 41 | Ticket, Comment, Attachment, Status, Priority, Category, User, Report, Display, Archive, Session | [TicketingSystem.wiki.md](SKILLS/TicketingSystem/TicketingSystem.wiki.md) |

**Total: 96 skills** across 4 bundles and 30 operation groups.

Machine-readable catalog: [manifest.json](manifest.json)

---

## Extending the Distribution

Adding a new skill bundle requires only: create skill files under `SKILLS/{BundleName}/{Group}/`, write a `{BundleName}.wiki.md`, add an entry to `manifest.json`, register files in `SKILLS.projitems`, and cut a new release. See the Ontology bundle as a worked example of a bundle that depends on XBase.

The skill file format — Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list — is the stable interface contract. Any consumer can depend on it. See [Repository-Presentation-PRD.md](ProductRequirementsDocuments/Repository-Presentation-PRD.md) for the full extensibility model.
