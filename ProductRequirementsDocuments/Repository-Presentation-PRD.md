# Product Requirements Document: GitHub Repository Presentation & AI-Discoverable SKILLS Distribution

## Overview

This PRD covers two tightly coupled surfaces:

1. **The GitHub repository itself** — structure, metadata, and content that make it useful when an AI agent discovers it via web search or crawl. The repo must be self-describing enough that an AI can understand the project, retrieve the SKILLS distribution, and install it without human guidance.

2. **A presentation landing page** — dual-format: `README.md` at the repo root for the GitHub view, and a GitHub Pages site (`docs/`) for a richer browsable version. Both surfaces share the same content hierarchy; the Pages site adds visual polish and navigation.

The governing design principle: **the repo is an AI-consumable skill registry first, a human-readable project page second.** Human discoverability and aesthetics are layered on top, not the foundation.

---

## Goals

- An AI agent that finds this repo via web search can, without human help: understand what the project is, identify which skills it wants, download the distribution, and emit correct installation instructions to its user.
- A human developer can install the full SKILLS distribution with a single copy-paste command.
- The SKILLS format and install contract are harness-agnostic and system-agnostic: no assumption about which AI runtime, operating system, or programming language the consumer uses.
- The distribution is versioned and the manifest format is stable and extensible across future skill sets and harnesses.
- Adding a new skill set to the repo requires only: add the skill files, add entries to `manifest.json`, and cut a new release.

---

## Non-Goals

- Building a custom registry server or API endpoint — GitHub Releases and raw file URLs are sufficient.
- Prescribing where skill files must be placed on the consumer's machine — that is the harness's concern.
- Providing a skill execution runtime — skills are markdown specifications; execution is the AI harness's responsibility.
- Implementing authentication, licensing enforcement, or telemetry.

---

## Design Principles

### Harness-Agnostic

Skills are plain markdown files. The format — Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list — is a human-readable specification contract, not code. Any AI harness that can read a markdown file and follow numbered steps can consume these skills. No SDK, no framework, no runtime binding.

### System-Agnostic

The install contract is: *download a ZIP, extract markdown files, tell your AI harness where they are.* No build step, no compiler, no OS-specific installer, no scripting language dependency. Install scripts provided for convenience are cross-platform and clearly labeled as optional.

### AI-First, Human-Secondary

The primary consumer is an AI agent. All structural decisions (manifest format, install instructions, page layout) optimize for machine readability first. Human usability is achieved by making the machine-readable layer clean enough to also be human-readable — not by building a separate layer.

### Future-Proof

- The manifest carries a `manifest_version` field. Consumers should check this and handle unknown versions gracefully.
- Skill namespaces (`XBase/Database`, `TicketingSystem/Ticket`) are the stable identity. File paths within the ZIP follow the namespace exactly and will not be reorganized without a major version bump.
- GitHub Releases provide immutable versioned artifacts. The `latest` release alias provides a stable URL for always-current installs.

---

## Surfaces

### Surface 1: `README.md` (Repo Root)

The `README.md` is the primary AI-discoverable surface. It is indexed by GitHub search, Google, and AI crawlers. It must contain everything an AI needs without requiring navigation to other pages.

**Required sections, in order:**

1. **Project identity block** — one paragraph: what AiXBase is, what problem it solves, what makes it unusual (AI Skills as the only interface, no runtime dependencies).
2. **AI Quick Install** — prominently placed, machine-readable install block (see §AI Discovery Protocol). This section must appear before any narrative prose.
3. **What is XBase** — brief summary of the file-backed database engine, its file format, and its skill groups. Link to `SKILLS/XBase/XBase.wiki.md`.
4. **What is the Ticketing System** — brief summary of the helpdesk feature built on XBase. Link to `SKILLS/TicketingSystem/TicketingSystem.wiki.md`.
5. **How TicketingSystem uses XBase** — the dependency chain in one diagram plus one paragraph (see §Content Requirements).
6. **Ticketing System usage examples** — 3–5 concrete skill invocation sequences (see §Content Requirements).
7. **Human Install** — one-liner commands plus link to GitHub Releases.
8. **SKILLS Catalog** — table listing all skill bundles with counts. Links to individual wiki files.
9. **Extending the Distribution** — one paragraph: how to add skill sets; link to this PRD.

### Surface 2: GitHub Pages (`docs/`)

A static site deployed from the `docs/` directory on `master`. Uses the simplest possible toolchain: plain HTML or a single-page Markdown-to-HTML renderer. No build pipeline, no JavaScript framework.

**Adds on top of README:**

- Navigation sidebar linking to each skill group's wiki
- Expandable usage examples with syntax highlighting
- A "Copy install command" button on the install block
- Visual dependency diagram (ASCII-art or SVG) for TicketingSystem → XBase
- A skills browser: filterable table of all 61 skills with name, group, and one-line description

### Surface 3: `llms.txt` (Repo Root)

A machine-readable site manifest following the emerging `llms.txt` convention. Placed at the repo root so AI crawlers find it at a predictable path. Format: structured markdown with one-line description, links to key resources, and a short capabilities statement.

```markdown
# AiXBase

> AI Skills distribution for file-backed database management and helpdesk ticketing.
> All operations are plain markdown skill files; no runtime, SDK, or build step required.

## Key Resources

- [Skill Manifest](manifest.json) — machine-readable catalog of all skills and bundles
- [XBase Wiki](SKILLS/XBase/XBase.wiki.md) — database engine skill reference
- [Ticketing Wiki](SKILLS/TicketingSystem/TicketingSystem.wiki.md) — ticketing system skill reference
- [Latest Release](https://github.com/StewartScottRogers/AiXBase/releases/latest) — versioned ZIP download

## Install Contract

Download the latest `skills.zip` from Releases. Extract it. Place the markdown files where your AI harness loads skill definitions. No other steps required.
```

### Surface 4: `manifest.json` (Repo Root)

The authoritative machine-readable skill catalog. Stable URL, versioned content, designed for AI consumption.

```json
{
  "manifest_version": "1",
  "name": "AiXBase Skills Distribution",
  "description": "AI Skill files for file-backed database management (XBase) and helpdesk ticketing (TicketingSystem). Skills are plain markdown; no runtime required.",
  "version": "1.0.0",
  "zip_url": "https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip",
  "bundles": [
    {
      "id": "xbase",
      "name": "XBase",
      "description": "Native file-backed database engine. Provides connection management, schema DDL, full CRUD, composite queries, index management, transactions with savepoints, and backup/restore.",
      "depends_on": [],
      "skill_count": 30,
      "wiki": "SKILLS/XBase/XBase.wiki.md",
      "groups": [
        { "id": "Database",    "path": "XBase/Database",    "count": 4 },
        { "id": "Schema",      "path": "XBase/Schema",      "count": 5 },
        { "id": "Record",      "path": "XBase/Record",      "count": 5 },
        { "id": "Query",       "path": "XBase/Query",       "count": 5 },
        { "id": "Index",       "path": "XBase/Index",       "count": 4 },
        { "id": "Transaction", "path": "XBase/Transaction", "count": 4 },
        { "id": "Backup",      "path": "XBase/Backup",      "count": 3 }
      ]
    },
    {
      "id": "ticketing",
      "name": "TicketingSystem",
      "description": "Full helpdesk ticketing system built entirely on XBase skills. Covers ticket lifecycle, comments, attachments, status workflows, priorities, categories, users, reporting, and terminal display.",
      "depends_on": ["xbase"],
      "skill_count": 31,
      "wiki": "SKILLS/TicketingSystem/TicketingSystem.wiki.md",
      "groups": [
        { "id": "Ticket",     "path": "TicketingSystem/Ticket",     "count": 9 },
        { "id": "Comment",    "path": "TicketingSystem/Comment",    "count": 4 },
        { "id": "Attachment", "path": "TicketingSystem/Attachment", "count": 3 },
        { "id": "Status",     "path": "TicketingSystem/Status",     "count": 2 },
        { "id": "Priority",   "path": "TicketingSystem/Priority",   "count": 2 },
        { "id": "Category",   "path": "TicketingSystem/Category",   "count": 4 },
        { "id": "User",       "path": "TicketingSystem/User",       "count": 5 },
        { "id": "Report",     "path": "TicketingSystem/Report",     "count": 3 },
        { "id": "Display",    "path": "TicketingSystem/Display",    "count": 3 }
      ]
    }
  ],
  "install": {
    "contract": "Download skills.zip, extract it, place the markdown files where your AI harness loads skill definitions.",
    "notes": "Skills are harness-agnostic. The file path within the ZIP mirrors the namespace: XBase/Database/XBase-Database-Initialize.md. You may install individual groups rather than the full distribution."
  }
}
```

---

## AI Discovery Protocol

### Discovery Path

1. An AI agent performs a web search and finds the repo URL or GitHub Pages URL.
2. The agent reads `README.md` (served by GitHub) or the Pages landing page.
3. The **AI Quick Install** section at the top of both surfaces contains: the `manifest.json` URL, the `skills.zip` URL, and a short install instruction the AI can relay to its user.
4. Optionally, the agent fetches `llms.txt` for a structured capabilities summary.
5. The agent fetches `manifest.json` to enumerate available bundles and select what to install.
6. The agent downloads `skills.zip` from the Releases URL in the manifest.
7. The agent instructs its user to extract the ZIP and configure their harness, or — if the harness supports it — performs the file placement itself.

### AI Quick Install Block

This block must appear verbatim near the top of `README.md` and the Pages landing page, inside a fenced code block with a preceding heading so AI agents can locate it by pattern:

```markdown
## AI Quick Install

Manifest: https://github.com/StewartScottRogers/AiXBase/raw/master/manifest.json
Download: https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip

Install contract: Download skills.zip, extract it, place the markdown files
where your AI harness loads skill definitions. No build step required.
Partial installs are supported — you may extract individual bundle folders.
The TicketingSystem bundle depends on the XBase bundle.
```

The block is intentionally plain text (not instructions to a specific harness) so it remains valid for any consumer now and in the future.

---

## Human Install Path

### One-liner (PowerShell)

```powershell
Invoke-WebRequest -Uri "https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip" -OutFile skills.zip; Expand-Archive skills.zip -DestinationPath .
```

### One-liner (bash/curl)

```bash
curl -L https://github.com/StewartScottRogers/AiXBase/releases/latest/download/skills.zip -o skills.zip && unzip skills.zip
```

### Manual

1. Go to the [Releases](https://github.com/StewartScottRogers/AiXBase/releases/latest) page.
2. Download `skills.zip`.
3. Extract to the directory your AI harness scans for skill definitions.

Both surfaces must show all three options. The PowerShell and bash one-liners are clearly labeled by platform. The manual path is always last.

---

## Content Requirements

### Project Description

> AiXBase is an AI Skills distribution that gives any AI harness a complete file-backed database engine (XBase) and a full helpdesk ticketing system (TicketingSystem) — implemented entirely as plain markdown skill files. There are no binaries, no SDKs, no runtime dependencies. The AI reads and writes structured files directly using OS file system primitives.

### How TicketingSystem Uses XBase

The dependency chain diagram for both surfaces:

```
User Request
    │
    ▼
Ticketing Skill          (e.g., Ticketing-Ticket-Create)
    │  reads _schema.json to validate, then delegates all I/O:
    ▼
XBase Record Skill       (XBase-Record-Insert)
    │  appends a JSON row to the .dbf file:
    ▼
OS File System           (append-binary-record → Tickets.dbf)
```

Prose summary: Every Ticketing skill is a workflow coordinator — it validates business rules (status transitions, permission checks, audit log entries) and then issues XBase skill calls for all file I/O. No Ticketing skill reads or writes files directly. This means any storage engine that implements the XBase skill contract can back the Ticketing system.

### Ticketing System Usage Examples

**Example 1 — Full ticket lifecycle**

```
# Setup (once)
/XBase-Database-Initialize  DatabaseName:"ticketing"
/XBase-Database-Connect     DatabaseName:"ticketing"  ConnectionName:"ticketing"
/Ticketing-Status-Define    Name:"Open"        IsTerminal:false  IsDefault:true
/Ticketing-Status-Define    Name:"In Progress" IsTerminal:false
/Ticketing-Status-Define    Name:"Closed"      IsTerminal:true
/Ticketing-Priority-Define  Name:"High"        NumericValue:2
/Ticketing-Priority-Define  Name:"Medium"      NumericValue:3  IsDefault:true
/Ticketing-User-Register    Username:"alice"   Email:"alice@example.com"  Password:"secret"  IsAdmin:true

# Daily operations
/Ticketing-User-Authenticate  Username:"alice"    Password:"secret"
# → SessionToken:"tok_abc"

/Ticketing-Ticket-Create
  Summary:"Checkout page times out on mobile"
  Description:"Reproducible on iOS 17, Safari 17. Occurs after entering card details."
  SubmittedByUserId:"<alice-id>"
# → TicketId:1  TicketNumber:"TKT-0001"

/Ticketing-Ticket-Assign
  TicketId:1  AssigneeId:"<alice-id>"  AssignedByUserId:"<alice-id>"

/Ticketing-Status-Transition
  TicketId:1  ToStatus:"In Progress"  ChangedByUserId:"<alice-id>"

/Ticketing-Comment-Add
  TicketId:1  AuthorUserId:"<alice-id>"
  Body:"Traced to a missing timeout on the payment gateway call. Fix in progress."

/Ticketing-Ticket-Close
  TicketId:1  ClosedByUserId:"<alice-id>"
  Resolution:"Added 30-second timeout on payment gateway; deployed to staging."

/Ticketing-Display-Complete  TicketNumber:"TKT-0001"
```

**Example 2 — Escalation workflow**

```
/Ticketing-Ticket-Escalate
  TicketId:2
  EscalatedByUserId:"<alice-id>"
  Reason:"Customer is blocked on production; SLA breach in 2 hours."
# Priority raised to High; assignee notified; history row appended

/Ticketing-Display-Alert
  Message:"TKT-0002 escalated to High — SLA breach imminent"
```

**Example 3 — Reporting**

```
/Ticketing-Ticket-Query
  Filter:{"Field":"Status", "Operator":"=", "Value":"Open"}
  Sort:[{"Field":"Priority.NumericValue", "Direction":"ASC"}]
  Limit:20
# Returns: open tickets ordered by priority

/Ticketing-Report-Summary
  DateFrom:"2026-01-01"  DateTo:"2026-06-30"
# Returns: ticket counts by status, average resolution time, escalation rate

/Ticketing-Report-Export
  Format:"CSV"  DateFrom:"2026-01-01"  DateTo:"2026-06-30"
```

**Example 4 — AI agent using the skills autonomously**

An AI agent discovering this repo can use this pattern to bootstrap the ticketing system in a new environment:

```
# Agent reads manifest.json → selects "ticketing" bundle (depends_on "xbase")
# Agent downloads skills.zip, extracts XBase/ and TicketingSystem/ folders
# Agent configures its harness to load the extracted skill files
# Agent then executes the setup sequence from Example 1
# The system is now operational with no human writing any code
```

---

## Distribution Packaging

### GitHub Releases

Each release publishes a single artifact: `skills.zip`. The ZIP contains the full `SKILLS/` folder structure, renamed to strip the `SKILLS/` prefix so bundle paths are at the root:

```
skills.zip
├── XBase/
│   ├── XBase.wiki.md
│   ├── Database/
│   │   ├── XBase-Database-Initialize.md
│   │   ├── XBase-Database-Connect.md
│   │   ├── XBase-Database-Disconnect.md
│   │   └── XBase-Database-Drop.md
│   ├── Schema/ ...
│   ├── Record/ ...
│   ├── Query/ ...
│   ├── Index/ ...
│   ├── Transaction/ ...
│   └── Backup/ ...
├── TicketingSystem/
│   ├── TicketingSystem.wiki.md
│   ├── Ticket/ ...
│   ├── Comment/ ...
│   ├── Attachment/ ...
│   ├── Status/ ...
│   ├── Priority/ ...
│   ├── Category/ ...
│   ├── User/ ...
│   ├── Report/ ...
│   └── Display/ ...
└── manifest.json
```

The manifest is included inside the ZIP so an offline consumer can enumerate what they installed.

### Versioning

Semantic versioning: `MAJOR.MINOR.PATCH`.

- `PATCH`: bug fixes to existing skill steps, clarifications, error code additions.
- `MINOR`: new skills added to an existing bundle; new optional inputs on existing skills.
- `MAJOR`: breaking changes to skill input/output contracts; removal of skills; ZIP structure changes.

The `manifest.json` at the repo root always reflects the latest release. Historical manifests are available inside each release's `skills.zip`.

### Release Checklist

1. Update version in `manifest.json`.
2. Verify all skills listed in the manifest exist in `SKILLS/`.
3. Build `skills.zip` from the `SKILLS/` folder (strip the `SKILLS/` prefix).
4. Copy `manifest.json` into the ZIP root.
5. Create a GitHub Release tagged `v{version}` with `skills.zip` as the release asset.
6. Update the `zip_url` in `manifest.json` if the release URL pattern changed.

A GitHub Actions workflow should automate steps 3–6 on tag push.

---

## Extensibility Model

### Adding a New Skill Bundle

1. Create a new folder under `SKILLS/` following the naming convention: `SKILLS/{BundleName}/{Group}/`.
2. Write skill files following the standard format (Inputs, JSON Outputs, numbered Steps, Error Codes, Dependencies).
3. Write a `{BundleName}.wiki.md` at `SKILLS/{BundleName}/`.
4. Add a new entry to the `bundles` array in `manifest.json`, listing `depends_on` if the bundle calls skills from another bundle.
5. Register all new files in `SKILLS.projitems`.
6. Cut a `MINOR` release.

### Adding Skills to an Existing Bundle

1. Add the skill file under the appropriate group folder.
2. Increment the `count` in the relevant group entry in `manifest.json`.
3. Increment `skill_count` on the bundle.
4. Register the file in `SKILLS.projitems`.
5. Cut a `MINOR` release.

### Skill File Format Contract

The skill file format is the stable interface contract. Any consumer (AI harness, documentation tool, skill browser) can depend on it. Format:

```markdown
# {Skill-Name}

{One-line description}

## Inputs

| Parameter | Type | Required | Description |
|---|---|---|---|
...

## Outputs

```json
{ ... example output ... }
```

## Steps

1. ...
2. ...

## Error Codes

| Code | Meaning |
|---|---|
...

## Dependencies

- {Other-Skill-Name}
```

This format must not be changed without a `MAJOR` version bump.

---

## Success Criteria

| Criterion | How to verify |
|---|---|
| An AI agent that has never seen this repo can install the full distribution after reading only `README.md` | Manual test: start a fresh AI session, provide only the repo URL, ask it to install the TicketingSystem skills |
| Human install completes in under 60 seconds from a fresh machine | Manual test: time the one-liner on a machine with no prior setup |
| Adding a new skill bundle requires no changes outside `SKILLS/`, `manifest.json`, and `SKILLS.projitems` | Review the extensibility checklist on the next new bundle addition |
| The manifest is valid JSON and all listed file paths exist in `skills.zip` | Automated check in GitHub Actions release workflow |
| The GitHub Pages site renders correctly on mobile and desktop | Visual check after first Pages deployment |
| `llms.txt` and `manifest.json` are findable at predictable root URLs | Verify `https://github.com/StewartScottRogers/AiXBase/raw/master/llms.txt` and `manifest.json` return correct content after first commit |
