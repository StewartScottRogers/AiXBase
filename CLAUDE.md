# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiXBase is a .NET/C# project organized as a Visual Studio solution (`AiXBase.slnx`, modern `.slnx` format requiring Visual Studio 2022+). It uses **shared projects** (`.shproj`) rather than standalone build projects — shared projects have no output of their own and must be referenced by concrete `.csproj` heads to compile.

## Solution Structure

- `docs/docs.shproj` — documentation pages (`index.md`, `Summary.md`)
- `SKILLS/SKILLS.shproj` — all distributable AI skill files (the ZIP distribution root)
- `ProductRequirementsDocuments/ProductRequirementsDocuments.shproj` — all PRDs and requirements docs
- `XBaseFiles/XBaseFiles.shproj` — tracks all XBase database files; uses wildcard includes to automatically show files added by external applications
- `AiXBase.Tests/` — test project skeleton (in progress; no `.csproj` yet)
- `AiXBase/` and `data/` — runtime databases (gitignored; local state only)

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
│   ├── Database/    XBase-Database-*.md       (4 skills)
│   ├── Schema/      XBase-Schema-*.md         (5 skills)
│   ├── Record/      XBase-Record-*.md         (5 skills)
│   ├── Query/       XBase-Query-*.md          (5 skills)
│   ├── Index/       XBase-Index-*.md          (4 skills)
│   ├── Transaction/ XBase-Transaction-*.md    (4 skills)
│   ├── Backup/      XBase-Backup-*.md         (3 skills)
│   ├── Admin/       XBase-Admin-*.md          (4 skills)
│   └── Runtime/     XBase-Runtime-*.md        (1 skill)
└── TicketingSystem/
    ├── Ticket/      Ticketing-Ticket-*.md     (9 skills)
    ├── Comment/     Ticketing-Comment-*.md    (4 skills)
    ├── Attachment/  Ticketing-Attachment-*.md (3 skills)
    ├── Status/      Ticketing-Status-*.md     (2 skills)
    ├── Priority/    Ticketing-Priority-*.md   (2 skills)
    ├── Category/    Ticketing-{Category,Tag}-*.md (4 skills)
    ├── User/        Ticketing-User-*.md       (5 skills)
    ├── Report/      Ticketing-Report-*.md     (3 skills)
    └── Display/     Ticketing-Display-*.md    (3 skills)
```

**Total: 70 skills** across 2 bundles and 18 operation groups.

Every skill file follows the same format: Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list.

## Development Notes

- No `.csproj` build heads exist yet — add them when implementing features and reference the shared projects
- Every new file must be registered in `AiXBase.slnx` (root files) or the relevant `.projitems` (project files) — never leave VS out of sync with the file system
- PRDs go in `ProductRequirementsDocuments/`; skill files go in `SKILLS/` under the appropriate feature + operation subfolder
- `XBaseFiles/XBaseFiles.shproj` tracks all XBase database files; uses wildcard includes to automatically show files added by external applications
- The `AiXBase/` and `data/` directories are gitignored; databases there are local runtime state only
