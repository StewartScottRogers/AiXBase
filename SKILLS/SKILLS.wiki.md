# AiXBase SKILLS

A distributable collection of AI skill files for harness-agnostic issue tracking and file-based database access. Each skill is a self-contained Markdown file that any AI agent capable of reading Markdown and performing file system operations can execute — no specific AI platform, operating system, or runtime is required.

---

## What These Skills Are

Skills are plain Markdown files, each specifying a single well-defined operation. A skill file tells the executing agent what inputs to accept, what steps to perform in sequence, what outputs to return, and what errors to report. The agent reads the skill and follows its steps directly — no compilation, no runtime dependency beyond the ability to read and execute Markdown instructions.

Skills do not assume any specific AI platform. They work with any AI harness that can read Markdown skill files and invoke the steps described in them.

---

## Bundles

### Ontology (13 skills)

Generates an RDF/OWL ontology from any connected XBase database schema on the fly — no pre-authored `.owl` files required.

| Group | Skills | Purpose |
|-------|--------|---------|
| Admin | 4 | Inspect, compare, rebuild, and administer an OntologyDocument |
| Namespace | 1 | Configure base IRI and prefix map |
| Build | 1 | Introspect schema → OWL classes + properties |
| Populate | 1 | Load records as owl:NamedIndividual instances |
| Query | 2 | BGP pattern query and single-resource describe |
| Validate | 2 | OWL schema consistency and individual conformance checks |
| Export | 1 | Serialize ontology to Turtle / JSON-LD / RDF-XML / N-Triples |
| Session | 1 | Guided interactive ontology TUI |

See Ontology/Ontology.wiki.md for full documentation.

### XBase (35 skills)

A lightweight native file-based database engine accessed entirely through skills. No external database engine, library, or binary is required.

| Group | Skills | Purpose |
|-------|--------|---------|
| Database | 4 | Lifecycle: initialize, connect, disconnect, drop |
| Schema | 5 | Table and column DDL |
| Record | 5 | CRUD and upsert |
| Query | 5 | Filters, sorts, joins, aggregates |
| Index | 4 | Create, drop, rebuild, list indexes |
| Transaction | 4 | Begin, commit, rollback, savepoints |
| Backup | 3 | Create, restore, verify backups |
| Runtime | 1 | Environment detection |
| Admin | 4 | Administrative operations |

See XBase/XBase.wiki.md for full documentation.

### TicketingSystem (41 skills, depends on XBase)

A full helpdesk ticketing system built on top of XBase. Every read and write routes through XBase skills — no direct file I/O.

| Group | Skills | Purpose |
|-------|--------|---------|
| Ticket | 11 | Full ticket lifecycle and archiving |
| Comment | 4 | Threaded comments |
| Attachment | 3 | File attachment metadata |
| Status | 2 | Status definitions and transitions |
| Priority | 2 | Priority definitions and assignment |
| Category | 4 | Categories and tags |
| User | 5 | Registration, authentication, management |
| Report | 3 | Summaries, generation, export |
| Display | 3 | Terminal banners and audible bell |
| Archive | 3 | Cross-database archive pack, query, restore |
| Session | 1 | Guided interactive ticketing TUI |

See TicketingSystem/TicketingSystem.wiki.md for full documentation.

---

## Installation

### AI-Assisted Install

An AI agent can discover and install skills automatically by reading the manifest.json file at the root of this repository. The manifest lists each skill file, its path within the SKILLS/ directory, and the target location within the agent's skill directory. The agent reads manifest.json, downloads the SKILLS/ directory, and places files in the correct locations according to the manifest's install instructions.

### Manual Install

1. Download the repository ZIP from GitHub.
2. Extract the archive.
3. Copy the SKILLS/ folder (or the subset of skills you need) to your AI agent's skill directory. The exact location depends on your AI harness — consult its documentation for where to place skill files.
4. Preserve the subfolder structure. Skills that list dependencies require those dependency skill files to be present in the same skill directory.

---

## Skill Naming Convention

Skills follow the pattern:

```
{Feature}-{Group}-{Operation}
```

| Segment | Examples |
|---------|---------|
| Feature | XBase, Ticketing |
| Group | Database, Schema, Record, Ticket, User, Report, Display |
| Operation | Initialize, Create, Insert, Select, Close, Authenticate, Export |

Examples: XBase-Database-Initialize, XBase-Record-Insert, Ticketing-Ticket-Create, Ticketing-User-Authenticate.

---

## File Format

Each skill file is a Markdown document with five standard sections:

| Section | Purpose |
|---------|---------|
| Inputs | Named parameters with types, required flags, and descriptions |
| Outputs | JSON example of what the skill returns on success |
| Steps | Numbered instructions the agent executes in order |
| Error Codes | Every failure mode and the code returned |
| Dependencies | Other skills this skill calls internally |

Every skill returns either a success envelope or a failure envelope:

```json
{ "Success": true, ... }
```

```json
{
  "Success": false,
  "ErrorCode": "FEATURE_CATEGORY_REASON",
  "Message": "Human-readable description of what went wrong.",
  "SkillName": "XBase-Record-Insert"
}
```

Error codes never contain stack traces, internal paths, or credentials.

---

## XBase Quick Start

Initialize a database, create a table, and insert a record:

1. Call XBase-Database-Initialize
   - DatabaseName: "myapp"

2. Call XBase-Database-Connect
   - DatabaseName: "myapp"
   - ConnectionName: "myapp"

3. Call XBase-Schema-TableCreate
   - ConnectionName: "myapp"
   - TableName: "Users"
   - Columns: [ { Name: "Id", Type: "INTEGER", PrimaryKey: true, AutoIncrement: true }, { Name: "Username", Type: "TEXT", NotNull: true }, { Name: "Email", Type: "TEXT" } ]

4. Call XBase-Record-Insert
   - ConnectionName: "myapp"
   - TableName: "Users"
   - Rows: [ { Username: "alice", Email: "alice@example.com" } ]

---

## Ticketing Quick Start

Initialize the ticketing database, create a user, and open a ticket:

1. Call XBase-Database-Initialize
   - DatabaseName: "ticketing"

2. Call XBase-Database-Connect
   - DatabaseName: "ticketing"
   - ConnectionName: "ticketing"

3. Call XBase-Schema-TableCreate for each of the 11 Ticketing tables (see TicketingSystem.wiki.md for the full list).

4. Call Ticketing-Status-Define to seed statuses: Open (IsDefault: true), In Progress, Blocked, Closed (IsTerminal: true).

5. Call Ticketing-Priority-Define to seed priorities: Low, Medium (IsDefault: true), High, Critical.

6. Call Ticketing-User-Register
   - Username: "admin"
   - DisplayName: "Administrator"
   - Email: "admin@example.com"
   - Password: "your-password-here"

7. Call Ticketing-User-Authenticate
   - Username: "admin"
   - Password: "your-password-here"
   - Returns: SessionToken, UserId

8. Call Ticketing-Ticket-Create
   - Summary: "Login page crashes on mobile Safari"
   - ReportedByUserId: (UserId from step 7)

---

## Harness-Agnostic Design

Skills do not assume any specific AI, operating system, or runtime environment. Steps are expressed as abstract operations — call XBase-Record-Insert, emit a BEL character to stdout, write text to stdout — without referencing any particular programming language, library, or platform API. The executing agent is responsible for translating each step into the appropriate mechanism for its environment.

This design means the same skill files work identically whether the executing agent runs on Windows, macOS, or Linux, and whether it is driven by a command-line harness, an IDE plugin, or any other AI agent platform.
