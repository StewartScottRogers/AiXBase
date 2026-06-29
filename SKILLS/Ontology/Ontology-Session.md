# Ontology-Session

Drive a guided interactive ontology session in the conversation: present a text menu, dispatch the user's selection to the appropriate Ontology skill, render the result as readable markdown, and repeat until the user exits.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `ConnectionName` | string | Yes | — | Open XBase connection alias (used for Build and Populate). |
| `DatabaseName` | string | Yes | — | Database name; used to seed the default namespace. |

## Outputs

No structured JSON output — this skill produces conversational markdown and loops interactively until the user selects Exit.

## Steps

1. Call `Ontology-Namespace-Define` with `DatabaseName` and default IRI. Store the result as `Namespace`.
2. Initialize `OntologyDocument = null`.
3. Display the main menu:

   ```
   ═══════════════════════════════════════
    Ontology Session — {DatabaseName}
   ═══════════════════════════════════════
    [1] Build Schema          (→ owl:Class + Properties)
    [2] Populate Records      (→ owl:NamedIndividual)
    [3] Query                 (BGP pattern)
    [4] Describe Resource     (all triples for an IRI)
    [5] Validate Schema       (OWL consistency check)
    [6] Validate Individuals  (instance conformance check)
    [7] Export                (Turtle / JSON-LD / RDF-XML / N-Triples)
    [8] Namespace Settings    (change base IRI or prefix)
    [9] Exit
   ```

4. Read the user's selection and dispatch:

   **[1] Build Schema**
   - If `OntologyDocument` is already set, ask "Replace current OntologyDocument? (y/n)". If n, return to menu.
   - Call `Ontology-Build-Schema` with `ConnectionName` and `Namespace`.
   - Store the result as `OntologyDocument`.
   - Display summary: `Classes: {ClassCount} | DatatypeProperties: {DatatypePropertyCount} | ObjectProperties: {ObjectPropertyCount}`.

   **[2] Populate Records**
   - If `OntologyDocument` is null, display "Run Build Schema first." and return to menu.
   - Ask "Tables to populate (comma-separated, or Enter for all):".
   - Ask "Row limit per table (Enter for none):".
   - Call `Ontology-Populate-Records` with the supplied options.
   - Store the updated result as `OntologyDocument`.
   - Display: `Individuals added: {IndividualsAdded} | Total: {IndividualCount}`.

   **[3] Query**
   - If `OntologyDocument` is null, display "Run Build Schema first." and return to menu.
   - Present a brief guide to triple pattern syntax, then ask the user to enter patterns one per line (blank line to finish), and `SELECT` variables.
   - Parse the user's input into a `Patterns` array and `Select` array.
   - Call `Ontology-Query-Execute`.
   - Render bindings as a markdown table. Display `{ReturnedCount} of {TotalCount} results`.

   **[4] Describe Resource**
   - If `OntologyDocument` is null, display "Run Build Schema first." and return to menu.
   - Ask "Resource IRI (or prefixed name):".
   - Call `Ontology-Query-Describe`.
   - Render triples as a markdown table grouped by predicate.

   **[5] Validate Schema**
   - If `OntologyDocument` is null, display "Run Build Schema first." and return to menu.
   - Call `Ontology-Validate-Schema`.
   - If `Valid = true`, display "Schema is valid — no issues found."
   - If `Valid = false`, render issues as a markdown table with Severity, Code, and Message columns.

   **[6] Validate Individuals**
   - If `OntologyDocument` is null or `IndividualCount = 0`, display "Run Populate Records first." and return to menu.
   - Call `Ontology-Validate-Individuals`.
   - Render results the same way as Validate Schema.

   **[7] Export**
   - If `OntologyDocument` is null, display "Run Build Schema first." and return to menu.
   - Ask "Format (Turtle / JSON-LD / RDF-XML / N-Triples):".
   - Ask "Output file path (Enter to display inline):".
   - Call `Ontology-Export-Serialize`.
   - If inline: display the serialized text in a fenced code block.
   - If file: display "Written to {FilePath} ({ByteCount} bytes)."

   **[8] Namespace Settings**
   - Ask "Base IRI (Enter to keep '{current}'):".
   - Ask "Prefix (Enter to keep '{current}'):".
   - Call `Ontology-Namespace-Define` with the new values.
   - Update `Namespace`. Display "Namespace updated — rebuild schema to apply changes."

   **[9] Exit**
   - Display "Ontology session ended." and stop looping.

   **Unknown selection:**
   - Display "Unknown option — please enter 1–9." and return to menu.

5. After each dispatched action (except Exit), return to the main menu.

## Error Codes

None — errors from delegated skills are rendered as readable markdown messages before returning to the menu.

## Dependencies

- `Ontology-Namespace-Define`
- `Ontology-Build-Schema`
- `Ontology-Populate-Records`
- `Ontology-Query-Execute`
- `Ontology-Query-Describe`
- `Ontology-Validate-Schema`
- `Ontology-Validate-Individuals`
- `Ontology-Export-Serialize`
- `XBase-Database-Connect` (connection must be open before calling this skill)
