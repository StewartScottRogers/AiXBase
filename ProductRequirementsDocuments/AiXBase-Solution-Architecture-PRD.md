# AiXBase Solution Architecture PRD

## Purpose

This document describes the overall architecture of the AiXBase solution: what it is, how its parts relate, and the roadmap for growing it from a skill-only distribution into a compilable .NET solution.

---

## What AiXBase Is

AiXBase is a harness-agnostic AI skill library distributed as a ZIP of Markdown files. It provides two complete subsystems:

- **XBase** — a file-backed relational database engine implemented entirely as AI skills. No external database engine, no libraries, no network. Every byte it reads or writes goes through abstract file-system operations performed by the executing AI agent.
- **Ticketing System** — a full-featured issue-tracking system built on top of XBase skills. No direct file I/O; all data access routes through XBase.

Both subsystems are pure specifications: numbered prose steps that any AI agent or runtime can follow without modification.

---

## Solution Structure

The Visual Studio solution (`AiXBase.slnx`, `.slnx` format requiring VS 2022+) uses **shared projects** (`.shproj`) throughout. Shared projects have no build output of their own; they exist to give Visual Studio and source control visibility into the file sets.

| Shared Project | Path | Purpose |
|---|---|---|
| `docs` | `docs/docs.shproj` | Documentation pages |
| `SKILLS` | `SKILLS/SKILLS.shproj` | All distributable skill files (ZIP distribution root) |
| `ProductRequirementsDocuments` | `ProductRequirementsDocuments/ProductRequirementsDocuments.shproj` | All PRDs |
| `XBaseFiles` | `XBaseFiles/XBaseFiles.shproj` | XBase database files for demos and tests |
| `AiXBaseTracking` | `AiXBaseTracking/AiXBaseTracking.shproj` | Dogfood development ticketing database |

### No build heads yet

No `.csproj` projects currently exist. The solution compiles nothing. The first `.csproj` will be added when a concrete runtime implementation is started (see Roadmap). When added, it must be registered in `AiXBase.slnx` and reference the relevant shared projects.

---

## SKILLS Distribution

The `SKILLS/` folder is the GitHub ZIP release artifact. Its layout mirrors the skill naming convention exactly.

```
SKILLS/
├── XBase/
│   ├── Admin/       XBase-Admin-*.md, connect-dogfood.md     (4 files)
│   ├── Backup/      XBase-Backup-*.md                        (3 skills)
│   ├── Database/    XBase-Database-*.md                      (4 skills)
│   ├── Index/       XBase-Index-*.md                         (4 skills)
│   ├── Query/       XBase-Query-*.md                         (5 skills)
│   ├── Record/      XBase-Record-*.md                        (5 skills)
│   ├── Runtime/     XBase-Runtime-Detect.md                  (1 skill)
│   ├── Schema/      XBase-Schema-*.md                        (5 skills)
│   ├── Transaction/ XBase-Transaction-*.md                   (4 skills)
│   └── XBase.wiki.md
└── TicketingSystem/
    ├── Attachment/  Ticketing-Attachment-*.md                 (3 skills)
    ├── Category/    Ticketing-{Category,Tag}-*.md             (4 skills)
    ├── Comment/     Ticketing-Comment-*.md                    (4 skills)
    ├── Display/     Ticketing-Display-*.md                    (3 skills)
    ├── Priority/    Ticketing-Priority-*.md                   (2 skills)
    ├── Report/      Ticketing-Report-*.md                     (3 skills)
    ├── Status/      Ticketing-Status-*.md                     (2 skills)
    ├── Ticket/      Ticketing-Ticket-*.md                     (9 skills)
    ├── User/        Ticketing-User-*.md                       (5 skills)
    └── TicketingSystem.wiki.md
```

Every skill file follows the same four-section format: Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list.

---

## File Format: NDJSON over DBF extension

XBase stores all table data as **newline-delimited JSON** (NDJSON) in files with the `.dbf` extension. Each file begins with a UTF-8 BOM followed by a CRLF blank line, then one JSON object per record per line. Index files (`.ndx`) are also NDJSON: each line is `{"Key":"value","Id":N}`.

Schema and metadata are stored as standard JSON in `_schema.json` and `_meta.json`. This format was chosen because it allows AI agents to read, write, and update records using only text file operations — no binary encoding is required.

> **Note:** The wiki and skill documentation describe a dBASE III binary format. This is the logical specification inherited from the dBASE III heritage of the `.dbf` file extension. The actual files produced by the Claude Code harness are NDJSON. Any future compiled runtime must either produce NDJSON or update the skill specifications to match its chosen encoding.

---

## Dogfood Ticketing System

The development workflow for AiXBase itself is tracked using the Ticketing System skills against the `AiXBaseTracking/tracking/` database. This gives real-world exercise to the skills during active development.

- **DatabaseRoot:** `Z:\repos\AiXBase\AiXBaseTracking`
- **DatabaseName:** `tracking`
- **ConnectionName:** `ticketing` (required by all Ticketing skills)
- **Bootstrap skill:** `connect-dogfood` (handles Runtime-Detect + Database-Connect + User-Authenticate in one call)
- **Admin user:** `srogers` (Stewart Rogers)

---

## Roadmap

### Phase 1 — Skills (current)
All XBase and Ticketing skills are complete and tested. The dogfood tracking database is live.

### Phase 2 — First .csproj build head
Add `AiXBase.Core/AiXBase.Core.csproj` as the first compilable project. Likely a .NET 8 class library. Initial scope TBD (see TKT-0004).

### Phase 3 — XBase Runtime
Implement XBase as a compiled .NET library that executes the skill specifications programmatically. The library reads/writes the same NDJSON DBF format so it is fully compatible with agent-produced databases.

### Phase 4 — Integration Tests
`AiXBase.Tests/` project exercises the XBase runtime against real DBF files on disk. No mocking (see TKT-0005).

### Phase 5 — Ticketing Runtime
Implement the Ticketing System as a .NET layer on top of the XBase runtime. Expose a clean API matching the skill inputs/outputs.

---

## Development Rules

1. Every new file must be registered in `AiXBase.slnx` (root files) or the relevant `.projitems` (shared project files). Never leave VS out of sync with the file system.
2. PRDs go in `ProductRequirementsDocuments/` and must be registered in `ProductRequirementsDocuments.projitems`.
3. Skill files go in `SKILLS/` under the appropriate feature and operation subfolder and must be registered in `SKILLS.projitems`.
4. XBase database files for demos/tests go in `XBaseFiles/` and must be registered in `XBaseFiles.projitems`.
5. The dogfood tracking database lives in `AiXBaseTracking/tracking/` and is tracked in git.
6. Test XBase skill changes from `AiXBase/` (the designated test consumer directory).
7. Test Ticketing skill changes from `AiTicketing/` (the designated test consumer directory).
