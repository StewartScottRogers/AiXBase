# Ontology-Admin-Inspect

Analyze an `OntologyDocument` and return a health and coverage report: class/property counts, FK coverage ratio, per-class property distribution, orphan properties (domain not matching any class), and isolated classes (no property domain or object-property range points to them).

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `OntologyDocument` | object | yes | — | The `OntologyDocument` to inspect |

## Outputs

```json
{
  "Success": true,
  "ClassCount": 12,
  "DatatypePropertyCount": 47,
  "ObjectPropertyCount": 16,
  "IndividualCount": 0,
  "FKCoverage": {
    "TotalProperties": 63,
    "ObjectProperties": 16,
    "CoveragePercent": 25.4
  },
  "PropertyDistribution": [
    {
      "ClassIRI": "http://xbase.local/tracking#Tickets",
      "ClassLabel": "Tickets",
      "DatatypePropertyCount": 9,
      "ObjectPropertyCount": 5
    }
  ],
  "OrphanProperties": [],
  "IsolatedClasses": [],
  "Issues": [],
  "IssueCount": 0,
  "IsHealthy": true
}
```

## Steps

1. Verify `OntologyDocument` is present and contains a non-empty `Classes` array; if not, return `ONTOLOGY_ADMIN_NO_DOCUMENT`.

2. Read `ClassCount`, `DatatypePropertyCount`, `ObjectPropertyCount`, and `IndividualCount` from the document (or recount from the arrays if the fields are stale).

3. Compute **FK coverage**:
   - `TotalProperties` = `DatatypePropertyCount` + `ObjectPropertyCount`
   - `ObjectProperties` = `ObjectPropertyCount`
   - `CoveragePercent` = (`ObjectPropertyCount` / `TotalProperties`) × 100, rounded to one decimal; set to 0 if `TotalProperties` is 0.

4. Compute **PropertyDistribution**: for each Class in `OntologyDocument.Classes`, count how many entries in `DatatypeProperties` have `Domain` equal to that Class IRI, and how many entries in `ObjectProperties` have `Domain` equal to that Class IRI. Build one record per class.

5. Compute **OrphanProperties**: collect all property entries (from both `DatatypeProperties` and `ObjectProperties`) whose `Domain` value does not match any IRI in `OntologyDocument.Classes`. Record each as `{ PropertyIRI, Domain }`.

6. Compute **IsolatedClasses**: collect all Class IRIs that satisfy both conditions:
   - No `DatatypeProperty` or `ObjectProperty` has `Domain` equal to that IRI.
   - No `ObjectProperty` has `Range` equal to that IRI.
   A class with no properties and no incoming object references has no semantic connections.

7. Build the `Issues` array:
   - For each orphan property: add `{ Severity: "Warning", Code: "ONTOLOGY_ADMIN_INSPECT_ORPHAN_PROPERTY", EntityIRI: <PropertyIRI>, Message: "Property domain does not resolve to a known class." }`
   - For each isolated class: add `{ Severity: "Info", Code: "ONTOLOGY_ADMIN_INSPECT_ISOLATED_CLASS", EntityIRI: <ClassIRI>, Message: "Class has no property domains and is not the range of any object property." }`

8. Set `IsHealthy` = true if `Issues` contains no `Error`-severity entries (Warnings and Info do not affect health).

9. Return the full inspection report.

## Error Codes

| Code | Condition |
|---|---|
| `ONTOLOGY_ADMIN_NO_DOCUMENT` | `OntologyDocument` is null, missing the `Classes` array, or has zero classes |
| `ONTOLOGY_ADMIN_INSPECT_ORPHAN_PROPERTY` | Emitted as a Warning inside `Issues`; not a top-level failure |
| `ONTOLOGY_ADMIN_INSPECT_ISOLATED_CLASS` | Emitted as Info inside `Issues`; not a top-level failure |

## Dependencies

None — operates entirely on the in-session `OntologyDocument` object.
