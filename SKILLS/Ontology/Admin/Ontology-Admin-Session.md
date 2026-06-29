# Ontology-Admin-Session

Guided interactive administration loop for an `OntologyDocument`. Focused on inspection and maintenance operations rather than user-facing query workflows (those belong in `Ontology-Session`).

The session holds `OntologyDocument`, `Namespace`, `ConnectionName`, and optionally a `SavedDocument` (used as the base for Compare) across menu iterations.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Registered XBase connection (used for Rebuild) |
| `OntologyDocument` | object | no | — | An existing document to administer; if omitted, user must Rebuild before inspecting |
| `Namespace` | object | no | — | The `Namespace` object; required for Rebuild |

## Outputs

```json
{
  "Success": true,
  "ExitReason": "UserExit",
  "FinalDocument": { "...": "OntologyDocument as it stood when the user chose Exit" }
}
```

## Steps

### Initialization

1. Store `ConnectionName`, `OntologyDocument` (may be null), and `Namespace` (may be null) as session-local variables.
2. Set `SavedDocument = null` (used by Compare as the base snapshot).
3. Present a one-line status line:
   ```
   [Admin] Connection: {ConnectionName} | Document: {loaded / not loaded} | Individuals: {count}
   ```

### Menu Loop

4. Repeat until the user selects Exit:

   Present the menu, dimming unavailable options (marked `*` when no document is loaded):

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

   Read the user's numeric selection.

### Dispatch

**Option 1 — Inspect Document**
- Require document loaded; if not, print `No document loaded. Use option 4 (Rebuild) first.` and return to menu.
- Call `Ontology-Admin-Inspect` with current `OntologyDocument`.
- Render the report as a markdown table:
  ```
  Classes: {ClassCount}  |  Datatype Properties: {DatatypePropertyCount}
  Object Properties: {ObjectPropertyCount}  |  FK Coverage: {CoveragePercent}%
  Individuals: {IndividualCount}
  ```
- If `OrphanProperties` or `IsolatedClasses` are non-empty, list them.
- Print `IsHealthy: YES` or `IsHealthy: NO — see issues above`.

**Option 2 — Save Snapshot for Compare**
- Require document loaded.
- Set `SavedDocument = OntologyDocument` (deep copy).
- Print `Snapshot saved ({ClassCount} classes, {DatatypePropertyCount + ObjectPropertyCount} properties).`

**Option 3 — Compare with Saved Snapshot**
- Require document loaded and `SavedDocument` not null; if either missing, print appropriate message and return to menu.
- Ask: `Include individual-level diff? (y/n)` → set `IncludeIndividuals` accordingly.
- Call `Ontology-Admin-Compare` with `BaseDocument = SavedDocument`, `TargetDocument = OntologyDocument`.
- Render summary:
  ```
  Classes  added: {n}  removed: {n}
  Properties  added: {n}  removed: {n}  changed: {n}
  HasChanges: {yes/no}
  ```
- If `ChangedProperties` is non-empty, list each change.

**Option 4 — Rebuild from Live Schema**
- If `Namespace` is null, prompt: `Enter BaseIRI (or press Enter for default http://xbase.local/{ConnectionName}#):` and call `Ontology-Namespace-Define` to produce a `Namespace`.
- If document is already loaded, ask: `Preserve existing individuals? (y/n)` → set `PreserveIndividuals`.
  If no document loaded, set `PreserveIndividuals = false` and construct a minimal placeholder `OntologyDocument` with empty arrays for the Rebuild call.
- Call `Ontology-Admin-Rebuild` with `ConnectionName`, `OntologyDocument`, `Namespace`, `PreserveIndividuals`.
- Replace session `OntologyDocument` with the returned document.
- Print rebuild summary: classes added/removed, properties added/removed/changed, individuals preserved/discarded.

**Option 5 — Validate Schema**
- Require document loaded.
- Call `Ontology-Validate-Schema` with current `OntologyDocument`.
- Print `Valid: {yes/no}`. If issues exist, render them as a table (Severity, Code, EntityIRI, Message).

**Option 6 — Validate Individuals**
- Require document loaded and `IndividualCount > 0`; if no individuals, print `No individuals loaded. Use Ontology-Session → Populate Records first.` and return to menu.
- Call `Ontology-Validate-Individuals` with current `OntologyDocument`.
- Print results in the same format as option 5.

**Option 7 — Export Current Document**
- Require document loaded.
- Prompt: `Format? (Turtle / JSON-LD / RDF-XML / N-Triples):`
- Prompt: `Output path (or Enter to return inline):`
- Call `Ontology-Export-Serialize` with selections.
- Print `Serialized to {FilePath} ({ByteCount} bytes)` or render the inline `Serialized` text in a fenced code block.

**Option 8 — Exit**
- Set `ExitReason = "UserExit"`.
- Return `{ Success: true, ExitReason: "UserExit", FinalDocument: OntologyDocument }`.

## Error Codes

| Code | Condition |
|---|---|
| `ONTOLOGY_ADMIN_NO_DOCUMENT` | An option requiring a document was selected before any document was loaded |
| `ONTOLOGY_ADMIN_NO_SNAPSHOT` | Option 3 was selected before a snapshot was saved via option 2 |

## Dependencies

- `Ontology-Admin-Inspect`
- `Ontology-Admin-Compare`
- `Ontology-Admin-Rebuild`
- `Ontology-Validate-Schema`
- `Ontology-Validate-Individuals`
- `Ontology-Export-Serialize`
- `Ontology-Namespace-Define`
