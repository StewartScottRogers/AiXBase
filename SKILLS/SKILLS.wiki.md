# AiXBase SKILLS

A distributable collection of AI Skill files for [Claude Code](https://claude.ai/code). Each skill is a Markdown file that, when placed in your project's `.claude/commands/` directory, becomes an executable slash command.

---

## What Is a Skill?

A skill is a self-contained `.md` file that instructs Claude Code to perform a single, well-defined operation. Skills are invoked as slash commands:

```
/XBase-Database-Initialize DatabasePath:"AiXBase/myapp.db"
/XBase-Record-Insert TableName:"Users" Rows:[{"Name":"Alice"}]
/Ticketing-Ticket-Create Summary:"Login page crashes on mobile"
```

Each skill file defines:

| Section | Purpose |
|---|---|
| **Inputs** | Named parameters, types, defaults, and descriptions |
| **Outputs** | JSON example of what the skill returns |
| **Steps** | Numbered instructions Claude executes |
| **Error Codes** | Every failure mode and the code returned |
| **Dependencies** | Other skills this skill calls internally |

---

## Installation

### Option 1 — Full distribution (GitHub ZIP)

1. Download and unzip the `SKILLS` folder from the GitHub release
2. Copy its contents into your project's `.claude/commands/` directory, preserving the subfolder structure
3. Confirm the skills appear in Claude Code by typing `/` and browsing the command list

```
your-project/
└── .claude/
    └── commands/
        ├── XBase/
        │   ├── Database/
        │   │   └── XBase-Database-Initialize.md
        │   └── ...
        └── TicketingSystem/
            └── Ticket/
                └── Ticketing-Ticket-Create.md
```

### Option 2 — Individual skills

Copy only the skills you need. Skills that list dependencies require those dependencies to be present too.

### Runtime prerequisite

The XBase skills run on native file-system operations — no external database engine,
libraries, or binaries are required. The only runtime dependency is a supported
scripting environment, which `XBase-Runtime-Detect` identifies automatically:

- **Windows**: PowerShell 5+ (`powershell.exe`) or PowerShell 7+ (`pwsh`) — detected first
- **macOS / Linux**: bash or zsh
- **Any platform**: Python 3.6+ (stdlib only — no `pip` packages required)

Run `/XBase-Runtime-Detect` once at the start of any session to establish the context.

---

## Skill Naming Convention

```
[Feature]-[Operation]-[Subdivision]
```

| Segment | Example values |
|---|---|
| Feature | `XBase`, `Ticketing` |
| Operation | `Database`, `Schema`, `Record`, `Ticket`, `User` |
| Subdivision | `Initialize`, `Create`, `Insert`, `Close` |

---

## Feature Areas

### XBase

A lightweight native file-based database engine accessed entirely through skills. 29 skills across 8 operation groups.

See [XBase.wiki.md](XBase/XBase.wiki.md) for full documentation.

| Group | Skills | Purpose |
|---|---|---|
| Database | 4 | Lifecycle: initialize, connect, disconnect, drop |
| Schema | 5 | Table and column DDL |
| Record | 5 | CRUD + upsert |
| Query | 5 | Filters, sorts, joins, aggregates (in-memory, no SQL) |
| Index | 4 | Create, drop, rebuild, list indexes |
| Transaction | 4 | Begin, commit, rollback, savepoints |
| Backup | 3 | Create, restore, verify backups |
| Runtime | 1 | Environment detection and script-generation context |

### Ticketing System

A full helpdesk ticketing system built on top of XBase. 33 skills across 9 operation groups.

See [TicketingSystem.wiki.md](TicketingSystem/TicketingSystem.wiki.md) for full documentation.

| Group | Skills | Purpose |
|---|---|---|
| Ticket | 9 | Full ticket lifecycle |
| Comment | 4 | Threaded comments |
| Attachment | 3 | File attachment metadata |
| Status | 2 | Status definitions and transitions |
| Priority | 2 | Priority definitions and assignment |
| Category | 4 | Categories and tags |
| User | 5 | Registration, auth, management |
| Report | 3 | Summaries, generation, export |
| Display | 3 | Terminal banners and audible bell |

---

## Standard Error Envelope

Every skill returns this structure on failure:

```json
{
  "Success": false,
  "ErrorCode": "FEATURE_CATEGORY_REASON",
  "Message": "Human-readable description of what went wrong.",
  "SkillName": "XBase-Record-Insert"
}
```

Error codes are documented in the **Error Codes** section of each skill file. They never contain stack traces, internal paths, or credentials.

---

## Testing

Comprehensive test criteria for both feature areas are maintained as PRDs:

- `ProductRequirementsDocuments/XBase-Testing-PRD.md` — 278 test cases, 30 performance benchmarks, 14 stress tests, 14 security tests
- `ProductRequirementsDocuments/TicketingSystem-Testing-PRD.md` — 310 test cases, 21 performance benchmarks, 12 stress tests, 16 security tests

---

## Distribution

The `SKILLS/` folder is the GitHub ZIP distribution artifact. Its directory structure mirrors the skill naming convention exactly. Files are plain Markdown — no compiled output, no runtime dependencies beyond a scripting environment (PowerShell, bash, or Python).
