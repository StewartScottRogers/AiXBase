# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiXBase is a .NET/C# project organized as a Visual Studio solution (`AiXBase.slnx`, modern `.slnx` format requiring Visual Studio 2022+). It uses **shared projects** (`.shproj`) rather than standalone build projects — shared projects have no output of their own and must be referenced by concrete `.csproj` heads to compile.

## Solution Structure

- `AiXBase/AiXBase.shproj` — main shared project for source code
- `ProductRequirementsDocuments/ProductRequirementsDocuments.shproj` — all PRDs and requirements docs go here
- `data/` — runtime SQLite databases (not tracked in git); `cipher-sessions.db` suggests session/encryption features

## Running Claude Code

A convenience script is included in the solution:

```cmd
Claude--dangerously-skip-permissions.cmd
```

This launches Claude Code with `--dangerously-skip-permissions --verbose` from the repository root.

## Development Notes

- No `.csproj` build heads exist yet — add them when implementing features and reference the shared projects
- PRDs must be placed inside `ProductRequirementsDocuments/` so they are included in the `ProductRequirementsDocuments.shproj`
- The `data/` directory is gitignored; SQLite databases there are local runtime state only
