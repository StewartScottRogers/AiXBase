# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiXBase is a .NET/C# project organized as a Visual Studio solution (`AiXBase.slnx`, modern `.slnx` format requiring Visual Studio 2022+). It uses **shared projects** (`.shproj`) rather than standalone build projects — shared projects have no output of their own and must be referenced by concrete `.csproj` heads to compile.

## Solution Structure

- `AiXBase/AiXBase.shproj` — main shared project for source code
- `SKILLS/SKILLS.shproj` — all distributable AI skill files (the ZIP distribution root)
- `AiTicketing/AiTicketing.shproj` — ticketing test/consumer project; imports `SKILLS.projitems` to see all skills
- `ProductRequirementsDocuments/ProductRequirementsDocuments.shproj` — all PRDs and requirements docs go here
- `data/` — runtime SQLite databases (not tracked in git)

## Running Claude Code

A convenience script is included in the solution:

```cmd
Claude--dangerously-skip-permissions.cmd
```

This launches Claude Code with `--dangerously-skip-permissions --verbose` from the repository root.

## SKILLS Distribution

The `SKILLS/` folder is the GitHub ZIP distribution artifact. Its layout mirrors the skill naming convention exactly:

```
SKILLS/
├── XBase/
│   ├── Database/    XBase-Database-*.md   (4 skills)
│   ├── Schema/      XBase-Schema-*.md     (5 skills)
│   ├── Record/      XBase-Record-*.md     (5 skills)
│   ├── Query/       XBase-Query-*.md      (5 skills)
│   ├── Index/       XBase-Index-*.md      (4 skills)
│   ├── Transaction/ XBase-Transaction-*.md(4 skills)
│   └── Backup/      XBase-Backup-*.md     (3 skills)
└── TicketingSystem/
    ├── Ticket/      Ticketing-Ticket-*.md  (9 skills)
    ├── Comment/     Ticketing-Comment-*.md (4 skills)
    ├── Attachment/  Ticketing-Attachment-*.md (3 skills)
    ├── Status/      Ticketing-Status-*.md  (2 skills)
    ├── Priority/    Ticketing-Priority-*.md(2 skills)
    ├── Category/    Ticketing-{Category,Tag}-*.md (4 skills)
    ├── User/        Ticketing-User-*.md    (5 skills)
    ├── Report/      Ticketing-Report-*.md  (3 skills)
    └── Display/     Ticketing-Display-*.md (3 skills)
```

**Total: 61 skill files** across 2 features and 15 operation groups.

Every skill file follows the same format: Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list.

`AiTicketing.projitems` imports `SKILLS.projitems` so Visual Studio treats all skill files as part of the AiTicketing project for testing — without duplicating the files.

## Development Notes

- No `.csproj` build heads exist yet — add them when implementing features and reference the shared projects
- Every new file must be registered in `AiXBase.slnx` (root files) or the relevant `.projitems` (project files) — never leave VS out of sync with the file system
- PRDs go in `ProductRequirementsDocuments/`; skill files go in `SKILLS/` under the appropriate feature + operation subfolder
- The `data/` directory is gitignored; SQLite databases there are local runtime state only
