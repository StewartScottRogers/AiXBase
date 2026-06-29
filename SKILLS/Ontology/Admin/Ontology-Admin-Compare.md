# Ontology-Admin-Compare

Diff two `OntologyDocument` objects and report what was added, removed, or changed between them. Useful for detecting schema drift after a database alter, verifying that FK annotations were applied correctly, or auditing ontology changes over time.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `BaseDocument` | object | yes | — | The reference `OntologyDocument` (e.g., a previous version or a saved snapshot) |
| `TargetDocument` | object | yes | — | The current `OntologyDocument` to compare against the base |
| `IncludeIndividuals` | bool | no | `false` | Whether to include Individual-level diff in the output |

## Outputs

```json
{
  "Success": true,
  "NamespaceMismatch": false,
  "AddedClasses": [
    { "IRI": "http://xbase.local/mydb#AuditLog", "Label": "AuditLog" }
  ],
  "RemovedClasses": [],
  "AddedProperties": [
    {
      "IRI": "http://xbase.local/mydb#Tickets_StatusId",
      "Type": "owl:ObjectProperty",
      "Domain": "http://xbase.local/mydb#Tickets",
      "Range": "http://xbase.local/mydb#Statuses"
    }
  ],
  "RemovedProperties": [],
  "ChangedProperties": [
    {
      "IRI": "http://xbase.local/mydb#Tickets_PriorityId",
      "Changes": [
        { "Field": "Type", "Before": "owl:DatatypeProperty", "After": "owl:ObjectProperty" },
        { "Field": "Range", "Before": "xsd:integer", "After": "http://xbase.local/mydb#Priorities" }
      ]
    }
  ],
  "AddedIndividuals": [],
  "RemovedIndividuals": [],
  "Summary": {
    "ClassesAdded": 1,
    "ClassesRemoved": 0,
    "PropertiesAdded": 1,
    "PropertiesRemoved": 0,
    "PropertiesChanged": 1,
    "IndividualsAdded": 0,
    "IndividualsRemoved": 0
  },
  "HasChanges": true
}
```

## Steps

1. Verify both `BaseDocument` and `TargetDocument` are present and contain `Classes` arrays; if either is missing return `ONTOLOGY_ADMIN_NO_DOCUMENT`.

2. Check for namespace mismatch: if `BaseDocument.Namespace.BaseIRI` ≠ `TargetDocument.Namespace.BaseIRI`, set `NamespaceMismatch = true`. This is not an error — emit a note and continue.

3. Build lookup maps keyed by IRI for the base:
   - `BaseClassMap`: IRI → Class object
   - `BasePropertyMap`: IRI → property object (combine DatatypeProperties and ObjectProperties, tagging each with its type)

4. Build lookup maps keyed by IRI for the target:
   - `TargetClassMap`: IRI → Class object
   - `TargetPropertyMap`: IRI → property object with type tag

5. **AddedClasses**: Class IRIs present in `TargetClassMap` but not in `BaseClassMap`.

6. **RemovedClasses**: Class IRIs present in `BaseClassMap` but not in `TargetClassMap`.

7. **AddedProperties**: Property IRIs present in `TargetPropertyMap` but not in `BasePropertyMap`. Include type, Domain, and Range from the target entry.

8. **RemovedProperties**: Property IRIs present in `BasePropertyMap` but not in `TargetPropertyMap`.

9. **ChangedProperties**: Property IRIs present in both maps. For each, compare `Type` (DatatypeProperty vs ObjectProperty), `Domain`, and `Range`. If any field differs, record a `Changes` array listing each differing field with `Before` and `After` values.

10. If `IncludeIndividuals = true`:
    - Build IRI sets from `BaseDocument.Individuals` and `TargetDocument.Individuals`.
    - **AddedIndividuals**: IRIs in Target not in Base.
    - **RemovedIndividuals**: IRIs in Base not in Target.
    If `IncludeIndividuals = false`, set both arrays to empty.

11. Build `Summary` counts from the above arrays.

12. Set `HasChanges = true` if any `Summary` count is non-zero.

13. Return the full comparison result.

## Error Codes

| Code | Condition |
|---|---|
| `ONTOLOGY_ADMIN_NO_DOCUMENT` | Either `BaseDocument` or `TargetDocument` is null or missing a `Classes` array |

## Dependencies

None — operates entirely on in-session `OntologyDocument` objects.
