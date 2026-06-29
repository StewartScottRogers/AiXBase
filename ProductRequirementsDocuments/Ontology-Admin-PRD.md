# Product Requirements Document: Ontology Administrative Skills

## Overview

The Ontology Administrative Skills provide four composable operations for inspecting, comparing, rebuilding, and managing `OntologyDocument` objects — without requiring the user to know the full Ontology skill API.

All four skills operate on the in-session `OntologyDocument` object. No RDF files are read or written by the Admin skills themselves; serialization is delegated to `Ontology-Export-Serialize` when needed. No XBase connection is required for Inspect or Compare; Rebuild requires one.

```
Ontology-Admin-{Operation}
```

The Admin group is part of the distributable `SKILLS/Ontology/Admin/` package.

---

## Skill Summary

| Skill | File | Description |
|---|---|---|
| **Inspect** | `Ontology-Admin-Inspect.md` | Health and coverage report for an `OntologyDocument` |
| **Compare** | `Ontology-Admin-Compare.md` | Diff two `OntologyDocument` objects — added, removed, and changed entities |
| **Rebuild** | `Ontology-Admin-Rebuild.md` | Re-introspect live XBase schema and merge into existing document |
| **Session** | `Ontology-Admin-Session.md` | Guided interactive TUI loop for inspection and maintenance |

---

## Architecture

```
User input (document object or natural-language choice)
        │
        ▼
  Ontology-Admin-Session        (TUI loop — no direct file I/O)
        │
        ├── Ontology-Admin-Inspect     (in-memory analysis of OntologyDocument)
        ├── Ontology-Admin-Compare     (in-memory diff of two OntologyDocuments)
        ├── Ontology-Admin-Rebuild     ──► Ontology-Build-Schema ──► XBase skills
        ├── Ontology-Validate-Schema
        ├── Ontology-Validate-Individuals
        ├── Ontology-Export-Serialize  ──► write-text-file
        └── Ontology-Namespace-Define
```

Admin skills are **orchestration only**. They do not read or write OWL/RDF files directly.

---

## Skill Specifications

### Ontology-Admin-Inspect

Reports health and coverage statistics for an existing `OntologyDocument`.

**Inputs**

| Name | Type | Required |
|---|---|---|
| `OntologyDocument` | object | Yes |

**Outputs**

| Field | Type | Description |
|---|---|---|
| `ClassCount` | integer | Total `owl:Class` entries |
| `DatatypePropertyCount` | integer | Total `owl:DatatypeProperty` entries |
| `ObjectPropertyCount` | integer | Total `owl:ObjectProperty` entries |
| `IndividualCount` | integer | Total `owl:NamedIndividual` entries |
| `FKCoverage` | object | `{ TotalProperties, ObjectProperties, CoveragePercent }` |
| `PropertyDistribution` | array | Per-class property counts |
| `OrphanProperties` | array | Properties whose `Domain` matches no class |
| `IsolatedClasses` | array | Classes with no associated properties |
| `Issues` | array | `{ Severity, Code, EntityIRI, Message }` entries |
| `IssueCount` | integer | Count of issue entries |
| `IsHealthy` | boolean | `true` if no `Error`-severity issues |

**Steps**
1. Verify `OntologyDocument` has a non-empty `Classes` array; if not, return `ONTOLOGY_ADMIN_NO_DOCUMENT`.
2. Count all arrays; compute `FKCoverage.CoveragePercent = ObjectPropertyCount / (DatatypePropertyCount + ObjectPropertyCount) × 100`.
3. Build `PropertyDistribution`: for each class, count properties whose `Domain` equals the class IRI.
4. Find `OrphanProperties`: properties whose `Domain` IRI is not in the class set.
5. Find `IsolatedClasses`: class IRIs absent from every property `Domain` and every ObjectProperty `Range`.
6. Build `Issues`: orphan properties → `Warning / ONTOLOGY_ADMIN_INSPECT_ORPHAN_PROPERTY`; isolated classes → `Info / ONTOLOGY_ADMIN_INSPECT_ISOLATED_CLASS`.
7. Set `IsHealthy = (no Error-severity issues)`.
8. Return full report.

---

### Ontology-Admin-Compare

Diffs two `OntologyDocument` objects and returns a structured change set.

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `BaseDocument` | object | Yes | — |
| `TargetDocument` | object | Yes | — |
| `IncludeIndividuals` | boolean | No | `false` |

**Outputs**

| Field | Type | Description |
|---|---|---|
| `NamespaceMismatch` | boolean | `true` if `BaseIRI` differs between documents |
| `AddedClasses` | array | Class objects present in Target but not Base |
| `RemovedClasses` | array | Class objects present in Base but not Target |
| `AddedProperties` | array | Property objects added (with type tag) |
| `RemovedProperties` | array | Property objects removed (with type tag) |
| `ChangedProperties` | array | `{ IRI, Changes: [{ Field, Before, After }] }` |
| `AddedIndividuals` | array | Individual IRIs added (only if `IncludeIndividuals = true`) |
| `RemovedIndividuals` | array | Individual IRIs removed (only if `IncludeIndividuals = true`) |
| `Summary` | object | `{ ClassesAdded, ClassesRemoved, PropertiesAdded, PropertiesRemoved, PropertiesChanged, IndividualsAdded, IndividualsRemoved }` |
| `HasChanges` | boolean | `true` if any additions, removals, or changes were found |

**Steps**
1. Verify both documents are present; if either is missing return `ONTOLOGY_ADMIN_NO_DOCUMENT`.
2. Set `NamespaceMismatch = (BaseDocument.Namespace.BaseIRI ≠ TargetDocument.Namespace.BaseIRI)`.
3. Build IRI-keyed maps for both documents (classes and all properties).
4. Compute Added/Removed/Changed sets by IRI.
5. For `ChangedProperties`: compare `Type`, `Domain`, and `Range` fields.
6. If `IncludeIndividuals = true`: compute Individual IRI sets and diff.
7. Build `Summary`; set `HasChanges`.
8. Return result.

---

### Ontology-Admin-Rebuild

Re-introspects the live XBase schema and merges the result into an existing `OntologyDocument`, preserving or discarding individuals as directed.

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `ConnectionName` | string | Yes | — |
| `OntologyDocument` | object | Yes | — |
| `Namespace` | object | Yes | — |
| `PreserveIndividuals` | boolean | No | `true` |

**Outputs**

| Field | Type | Description |
|---|---|---|
| `OntologyDocument` | object | The refreshed document |
| `RebuildSummary` | object | `{ ClassesAdded, ClassesRemoved, ClassesUnchanged, PropertiesAdded, PropertiesRemoved, PropertiesChanged, IndividualsPreserved, IndividualsDiscarded }` |

**Steps**
1. Verify `ConnectionName` is registered; if not return `ONTOLOGY_ADMIN_REBUILD_NOT_CONNECTED`.
2. Verify `OntologyDocument` has a `Classes` array; if not return `ONTOLOGY_ADMIN_NO_DOCUMENT`.
3. Verify `Namespace` has `BaseIRI`; if not return `ONTOLOGY_ADMIN_NO_NAMESPACE`.
4. Call `Ontology-Build-Schema` → `FreshDocument`.
5. Call `Ontology-Admin-Compare` (`BaseDocument = OntologyDocument`, `TargetDocument = FreshDocument`) → `Diff`.
6. Derive `RebuildSummary` from `Diff.Summary`.
7. Apply `PreserveIndividuals`: copy existing `Individuals` into `FreshDocument` or discard; update counts.
8. Return `FreshDocument` as `OntologyDocument` with `RebuildSummary`.

---

### Ontology-Admin-Session

Guided interactive TUI loop for ontology inspection and maintenance. Focused on admin operations; user-facing query workflows belong in `Ontology-Session`.

**Inputs**

| Name | Type | Required |
|---|---|---|
| `ConnectionName` | string | Yes |
| `OntologyDocument` | object | No |
| `Namespace` | object | No |

**Outputs**
- `ExitReason` (string: `"UserExit"`)
- `FinalDocument` (the `OntologyDocument` as it stood at exit, or `null` if never loaded)

**Session state held across iterations:** `OntologyDocument`, `Namespace`, `ConnectionName`, `SavedDocument` (snapshot for Compare).

**Menu**

```
Ontology Admin
──────────────────────────────────────
1. Inspect Document         *
2. Save Snapshot for Compare
3. Compare with Saved Snapshot *
4. Rebuild from Live Schema
5. Validate Schema          *
6. Validate Individuals     *
7. Export Current Document  *
8. Exit
──────────────────────────────────────
Options marked * require a loaded document.
```

**Dispatch**

| Option | Action |
|---|---|
| 1 — Inspect | Call `Ontology-Admin-Inspect`; render counts and issue table |
| 2 — Save Snapshot | Deep-copy `OntologyDocument` → `SavedDocument`; print confirmation |
| 3 — Compare | Prompt for `IncludeIndividuals`; call `Ontology-Admin-Compare` with `Base = SavedDocument`; render summary |
| 4 — Rebuild | Prompt for `Namespace` if null; prompt for `PreserveIndividuals` if document loaded; call `Ontology-Admin-Rebuild`; print rebuild summary |
| 5 — Validate Schema | Call `Ontology-Validate-Schema`; render issue table |
| 6 — Validate Individuals | Require `IndividualCount > 0`; call `Ontology-Validate-Individuals`; render issue table |
| 7 — Export | Prompt for `Format` and `OutputPath`; call `Ontology-Export-Serialize`; print result |
| 8 — Exit | Return `{ ExitReason: "UserExit", FinalDocument }` |

---

## File Layout

```
SKILLS/Ontology/Admin/
├── Ontology-Admin-Inspect.md     Health and coverage report
├── Ontology-Admin-Compare.md     Two-document diff
├── Ontology-Admin-Rebuild.md     Live schema re-introspection
└── Ontology-Admin-Session.md     Interactive admin TUI
```

---

## Error Codes

### Skill-level errors

| Code | Condition |
|---|---|
| `ONTOLOGY_ADMIN_NO_DOCUMENT` | `OntologyDocument` is null, missing, or has no `Classes` array |
| `ONTOLOGY_ADMIN_NO_NAMESPACE` | `Namespace` is null or missing `BaseIRI` (Rebuild only) |
| `ONTOLOGY_ADMIN_REBUILD_NOT_CONNECTED` | `ConnectionName` is not registered (Rebuild only) |
| `ONTOLOGY_ADMIN_NO_SNAPSHOT` | Compare-with-snapshot selected before a snapshot was saved |

### Issue codes (returned inside `Issues` array from Inspect)

| Code | Severity | Meaning |
|---|---|---|
| `ONTOLOGY_ADMIN_INSPECT_ORPHAN_PROPERTY` | Warning | Property `Domain` IRI matches no class in the document |
| `ONTOLOGY_ADMIN_INSPECT_ISOLATED_CLASS` | Info | Class has no property domains and is not the range of any ObjectProperty |

### Propagated errors

| Code | Source |
|---|---|
| `XBASE_CONNECTION_INVALID` | Rebuild → `Ontology-Build-Schema` → XBase |
| `ONTOLOGY_BUILD_NAMESPACE_MISSING` | Rebuild → `Ontology-Build-Schema` |
| `ONTOLOGY_SCHEMA_*` | Session option 5 → `Ontology-Validate-Schema` |
| `ONTOLOGY_IND_*` | Session option 6 → `Ontology-Validate-Individuals` |
| `ONTOLOGY_EXPORT_*` | Session option 7 → `Ontology-Export-Serialize` |

---

## Non-Goals

- The Admin skills do not read or write RDF or OWL files directly — serialization is delegated to `Ontology-Export-Serialize`
- They do not add new XBase error codes — they surface existing envelopes with added context
- They do not provide a GUI or web interface — output is plain markdown text to stdout
- They are harness-agnostic — any AI agent that can follow the numbered steps can implement them

---

## Dependencies

| Dependency | Required by |
|---|---|
| `Ontology-Build-Schema` | Rebuild |
| `Ontology-Admin-Inspect` | Session (option 1) |
| `Ontology-Admin-Compare` | Rebuild (internal diff); Session (option 3) |
| `Ontology-Admin-Rebuild` | Session (option 4) |
| `Ontology-Validate-Schema` | Session (option 5) |
| `Ontology-Validate-Individuals` | Session (option 6) |
| `Ontology-Export-Serialize` | Session (option 7) |
| `Ontology-Namespace-Define` | Session (option 4, when Namespace is null) |
| XBase connection | Rebuild only — `Ontology-Build-Schema` requires an active connection |
