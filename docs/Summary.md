# AiXBase

AiXBase is a demonstration of **Ai Polymorphic Services**: software capabilities expressed as AI Skills rather than fixed API endpoints, where the AI dynamically selects, composes, and adapts behaviors based on context rather than traversing a rigid call graph.

The repository ships five fully realised bundles — XBase, XBase UniversalSQL, Ontology, the Ticketing System, and Agent — alongside 101 distributable Skill files that any Claude Code project can install and invoke as slash commands.

---

## What Is an Ai Skill?

A Skill is a self-contained Markdown file that instructs Claude Code to perform one well-defined operation. It specifies inputs, JSON outputs, numbered steps, error codes, and dependencies. Claude executes those steps against real files when you invoke it as a slash command:

```
/XBase-Database-Initialize  DatabaseName:"myapp"
/XBase-Record-Insert        ConnectionName:"main"  TableName:"Products"  Rows:[...]
/Ticketing-Ticket-Close     TicketId:1  ClosedByUserId:"admin-id"
```

Skills are **portable** — copy a `.md` file and the capability moves with it. They are **composable** — skills call other skills through their declared dependency list. They are **harness-agnostic** — the same specification runs under PowerShell, bash, or Python, with the runtime detected automatically at execution time.

---

## Agent

The composition layer of AiXBase. It turns a set of skills into a single **composable application** — a live unit an AI enacts by emulation rather than compiling to native code. The same primitive is at once an application, an agent, and a component: a behavior manifest of skills, an external state store that carries its identity across stateless calls, a determinism boundary that hands correctness-critical leaf operations to deterministic skills, and a supervision role that lets units compose into teams of sub-agents.

**5 skills across 3 operation groups:**

| Group | Skills | Scope |
|---|:---:|---|
| Application | 2 | Compose a descriptor from behavior + state store + determinism boundary + role; enact a single request against it |
| Team | 2 | Route a request to a sub-agent; run a guided interactive supervisor session |
| Capability | 1 | Publish an application's discovery manifest |

Depends on the XBase bundle (default state store and capability registry); composes over any bundle.

---

## XBase UniversalSQL

A SQL translation layer that sits above the 35 XBase skills. It accepts a standard SQL statement as plain text, parses it into an AST, maps it to one or more XBase skill calls, and returns results in a unified envelope — no new file I/O, no storage engine changes.

**7 skills across 2 operation groups:**

| Group | Skills | Scope |
|---|:---:|---|
| UniversalSQL | 4 | Parse (AST + execution plan), Validate (syntax + semantic), Explain (annotated plan), Execute (full pipeline) |
| UniversalSQL-Admin | 3 | REPL (interactive SQL shell), Explain (plan display), Schema (DDL extractor) |

Supports SELECT, INSERT, UPDATE, DELETE, DDL (CREATE/DROP/ALTER TABLE, CREATE/DROP INDEX), TCL (BEGIN/COMMIT/ROLLBACK/SAVEPOINT), SHOW TABLES, DESCRIBE, EXPLAIN, BACKUP DATABASE, RESTORE DATABASE. Named parameter binding (`?name` placeholders). Transaction routing via `TransactionName`.

Claude Code slash commands: `/sql` (interactive shell), `/explain` (execution plan), `/schema` (DDL extractor).

Depends on the XBase bundle.

---

## Ontology

The Ontology bundle maps any connected XBase database into RDF/OWL format on the fly. Given an open XBase connection, the skills introspect the schema and optionally the records, produce a standards-compliant `OntologyDocument`, and either return it for downstream query and validation or serialize it to one of four RDF interchange formats.

**13 skills across 8 operation groups:**

| Group | Skills | Scope |
|---|:---:|---|
| Admin | 4 | Inspect document health; compare two documents; rebuild from live schema; guided admin session |
| Namespace | 1 | Configure base IRI and prefix map |
| Build | 1 | Schema introspection → OWL classes and properties |
| Populate | 1 | Load records as owl:NamedIndividual instances |
| Query | 2 | BGP pattern evaluation; single-resource describe |
| Validate | 2 | OWL schema consistency; individual conformance |
| Export | 1 | Serialize to Turtle / JSON-LD / RDF-XML / N-Triples |
| Session | 1 | Guided interactive ontology TUI |

Tables become `owl:Class`. Non-PK columns without a declared `ForeignKey` become `owl:DatatypeProperty` with an XSD range. Non-PK columns with `ForeignKey` become `owl:ObjectProperty` with the referenced table as range. Rows become `owl:NamedIndividual`.

Depends on the XBase bundle.

---

## XBase

XBase is a lightweight, file-based database engine with no external runtime dependencies. A database is a named directory; tables are stored as **dBASE III binary `.dbf` files** (fixed-length binary records); indexes are `.ndx` B-tree files; and transactions are directory snapshot workspaces that commit atomically via a same-volume file move.

**35 skills across 9 operation groups:**

| Group | Skills | Scope |
|---|:---:|---|
| Database | 4 | Initialize, connect, disconnect, drop |
| Schema | 5 | Table and column DDL |
| Record | 5 | Insert, select, update, delete, upsert |
| Query | 5 | Filter, sort, join, aggregate, compound execute |
| Index | 4 | Create, drop, rebuild, list |
| Transaction | 4 | Begin, commit, rollback, savepoints |
| Backup | 3 | Create, restore, verify |
| Admin | 4 | Execute (dynamic dispatch), Inspect (health report), Maintain (pack + rebuild + verify), Session (guided interactive admin TUI) |
| Runtime | 1 | Environment detection — verifies all required file system primitives |

Every table receives implicit `Id` (auto-increment), `CreatedAt`, `UpdatedAt`, and `IsDeleted` columns. Soft deletes are the default; hard deletes are opt-in via `HardDelete: true`. A filter is required on Update and Delete to prevent accidental mass mutations.

The storage format is **dBASE III binary**: every row is a fixed-length binary record with a 1-byte deletion flag, making databases compact and seek-addressable by record index without any external engine.

---

## Ticketing System

A full helpdesk ticketing system built entirely on top of XBase. It covers the complete ticket lifecycle — creation, assignment, escalation, status transitions, comments, attachments, reporting, two-tier archiving, and a terminal display with audible bell notification on completion.

**41 skills across 11 operation groups:**

| Group | Skills | Scope |
|---|:---:|---|
| Ticket | 11 | Create, read, update, delete, close, reopen, assign, escalate, query, archive, unarchive |
| Comment | 4 | Threaded comments; `IsInternal` flag for staff-only notes |
| Attachment | 3 | File attachment metadata — path, filename, size, uploader |
| Status | 2 | Configurable statuses and a validated transition graph |
| Priority | 2 | Configurable priorities with numeric ordering |
| Category | 4 | Hierarchical category tree and free-text tags |
| User | 5 | Registration, authentication, update, deactivation |
| Report | 3 | Aggregate summaries, named report types, CSV/JSON export |
| Display | 3 | Unicode COMPLETE banner, alert banners, audible bell |
| Archive | 3 | Pack (move IsArchived tickets to a named archive DB), query archive, restore to main |
| Session | 1 | Guided interactive ticketing session with six-item menu, dispatches to all Ticketing skills |

The system maintains 11 database tables. `TicketHistory` is append-only and records every mutation — status changes, assignments, escalations, reopens — making the full audit trail always available. Authentication deliberately returns a single generic error (`TICKETING_AUTH_FAILED`) for wrong password, unknown username, and deactivated account alike, preventing user enumeration.

When a ticket closes, the system writes a full-width Unicode block-art COMPLETE banner to stdout and rings the terminal bell three times — audible from across the room.

---

## Ai Polymorphic Services

Traditional software routes a request to a fixed handler. An Ai Polymorphic Service routes **intent** to a dynamically selected skill composition. The same high-level goal — "resolve this issue", "summarize open work", "triage new requests" — can trigger different service pathways depending on data shape, operational mode, or user role.

XBase and the Ticketing System demonstrate this in practice: a data-access layer and a business-logic application layer, each expressed entirely as Skills, composable without recompilation, portable across runtimes, and adaptive by design. The AI behaves less like a rigid endpoint and more like a self-orchestrating service that selects the right path from the available skill surface.

---

## Distribution

The `SKILLS/` folder is the GitHub ZIP distribution artifact. Drop its contents into any project's `.claude/commands/` directory — preserving the subfolder structure — and every command becomes available immediately in Claude Code. No build step, no package manager, no runtime installation required.

```
your-project/
└── .claude/
    └── commands/
        ├── XBase/
        │   ├── Database/   XBase-Database-*.md
        │   ├── Schema/     XBase-Schema-*.md
        │   ├── Record/     XBase-Record-*.md
        │   ├── Admin/      XBase-Admin-*.md
        │   └── ...
        └── TicketingSystem/
            ├── Ticket/     Ticketing-Ticket-*.md
            ├── User/       Ticketing-User-*.md
            └── ...
```

All 101 skills are plain Markdown files. Database operations are performed through OS file system primitives; the required mechanism is generated dynamically by the AI at execution time based on what the deployment environment provides.
