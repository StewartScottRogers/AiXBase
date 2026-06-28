---
layout: default
title: AiXBase — AI Skills Distribution
---

# AiXBase

AiXBase is an AI Skills distribution that gives any AI harness a complete file-backed database engine (**XBase**) and a full helpdesk ticketing system (**TicketingSystem**) — implemented entirely as plain markdown skill files. No binaries, no SDKs, no runtime dependencies.

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

## Skill Bundles

### XBase — File-Backed Database Engine

35 skills across 9 groups. Stores data in dBASE III binary format (`.dbf` + `.ndx`). No external database engine required.

| Group | Skills | Description |
|-------|--------|-------------|
| Database | 4 | Initialize, Connect, Disconnect, Drop |
| Schema | 5 | TableCreate, TableAlter, TableDrop, TableList, ColumnList |
| Record | 5 | Insert, Select, Update, Delete, Upsert |
| Query | 5 | Filter, Sort, Join, Aggregate, Execute |
| Index | 4 | Create, Drop, Rebuild, List |
| Transaction | 4 | Begin, Commit, Rollback, Savepoint |
| Backup | 3 | Create, Restore, Verify |
| Admin | 4 | Execute, Inspect, Maintain, Session |
| Runtime | 1 | Detect (environment capability verification) |

→ [XBase Skill Reference](../SKILLS/XBase/XBase.wiki.md)

### TicketingSystem — Helpdesk Built on XBase

41 skills across 11 groups. All file I/O routes through XBase skills — no direct file access.

| Group | Skills | Description |
|-------|--------|-------------|
| Ticket | 11 | Create, Read, Update, Delete, Close, Reopen, Assign, Escalate, Query, Archive, Unarchive |
| Comment | 4 | Add, Read, Edit, Delete |
| Attachment | 3 | Add, Read, Remove |
| Status | 2 | Define, Transition |
| Priority | 2 | Define, Set |
| Category | 4 | Create (category), Assign, Tag-Add, Tag-Remove |
| User | 5 | Register, Read, Update, Deactivate, Authenticate |
| Report | 3 | Summary, Generate, Export |
| Display | 3 | Complete (banner + BEL ×3), Alert (banner + BEL ×1), Bell |
| Archive | 3 | Pack (move archived tickets to named archive DB), Query, Restore |
| Session | 1 | Guided interactive ticketing session with menu-driven UI |

→ [TicketingSystem Skill Reference](../SKILLS/TicketingSystem/TicketingSystem.wiki.md)

---

## Dependency Architecture

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

Every Ticketing skill is a workflow coordinator. It validates business rules and issues XBase skill calls for all file I/O — no Ticketing skill touches the file system directly.

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

**Manual:** Download `skills.zip` from [Releases](https://github.com/StewartScottRogers/AiXBase/releases/latest) and extract to your AI harness's skill directory.

---

## Harness Agnostic Design

Skills are plain markdown files. The format — Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list — is a human-readable specification contract, not code. Any AI harness that can read a markdown file and follow numbered steps can use these skills.

No specific AI platform. No specific operating system. No specific programming language.

---

[View on GitHub](https://github.com/StewartScottRogers/AiXBase) · [manifest.json](../manifest.json) · [llms.txt](../llms.txt)
