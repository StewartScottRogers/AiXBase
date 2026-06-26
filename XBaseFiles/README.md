# XBaseFiles Project

This is a Shared Project (`.shproj`) that automatically tracks all XBase database files managed by external applications.

## Purpose

The XBaseFiles project provides visibility into XBase database directories without requiring manual file management. All files added or modified by external applications will automatically appear in Visual Studio's Solution Explorer.

## How It Works

The project uses **wildcard include patterns** in `XBaseFiles.projitems`:

```xml
<Content Include="$(MSBuildThisFileDirectory)**\*" />
```

This recursively includes all files in all subdirectories, making them visible in Visual Studio without needing manual refresh or project file updates.

## XBase Database Structure

XBase databases are stored as directories containing:

- `_meta.json` — Database metadata (name, version, timestamps)
- `_schema.json` — Table and index definitions
- `{TableName}.ndjson` — Table data (newline-delimited JSON, one record per line)
- `{TableName}.{IndexName}.ndx` — Index files (sorted key→Id entries)
- `_txn_{TransactionName}/` — Active transaction workspaces (if any)

## Usage

1. External applications create/modify XBase database directories inside this folder
2. Files automatically appear in Solution Explorer (no refresh needed)
3. View, edit, or track changes directly in Visual Studio

## Example Structure

```
XBaseFiles/
├── MyDatabase/
│   ├── _meta.json
│   ├── _schema.json
│   ├── Users.ndjson
│   ├── Users.idx_Username.ndx
│   └── Orders.ndjson
└── AnotherDatabase/
	├── _meta.json
	├── _schema.json
	└── Products.ndjson
```

## Notes

- This is a **Shared Project** — it has no build output of its own
- Project files (`.shproj`, `.projitems`, `README.md`) are excluded from the content list
- All other files are automatically tracked
- Compatible with Visual Studio 2022+ (uses modern `.slnx` solution format)
