# Ontology-Admin-Rebuild

Re-introspect a live XBase schema and merge the result into an existing `OntologyDocument`. New classes and properties are added; removed ones are flagged. Existing `Individuals` are optionally preserved. Returns the refreshed document and a summary of what changed.

Use this skill after running `XBase-Schema-TableAlter` (to add FK annotations or new columns), after `_schema.json` is updated externally, or whenever schema drift may have occurred.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `ConnectionName` | string | yes | — | Registered XBase connection to introspect |
| `OntologyDocument` | object | yes | — | The existing `OntologyDocument` to rebuild |
| `Namespace` | object | yes | — | The `Namespace` object (BaseIRI, Prefix, PrefixMap) used for IRI generation |
| `PreserveIndividuals` | bool | no | `true` | Whether to carry over the existing `Individuals` array into the rebuilt document |

## Outputs

```json
{
  "Success": true,
  "OntologyDocument": {
    "Namespace": { "...": "same as input" },
    "Classes": [ "..." ],
    "DatatypeProperties": [ "..." ],
    "ObjectProperties": [ "..." ],
    "Individuals": [ "..." ],
    "ClassCount": 12,
    "DatatypePropertyCount": 31,
    "ObjectPropertyCount": 17,
    "IndividualCount": 0
  },
  "RebuildSummary": {
    "ClassesAdded": 0,
    "ClassesRemoved": 0,
    "ClassesUnchanged": 12,
    "PropertiesAdded": 16,
    "PropertiesRemoved": 0,
    "PropertiesChanged": 1,
    "IndividualsPreserved": 0,
    "IndividualsDiscarded": 0
  }
}
```

## Steps

1. Verify `ConnectionName` is registered in the session; if not, return `ONTOLOGY_ADMIN_REBUILD_NOT_CONNECTED`.

2. Verify `OntologyDocument` is present with a `Classes` array; if missing, return `ONTOLOGY_ADMIN_NO_DOCUMENT`.

3. Verify `Namespace` is present with a `BaseIRI`; if missing, return `ONTOLOGY_ADMIN_NO_NAMESPACE`.

4. Call **`Ontology-Build-Schema`** with `ConnectionName` and `Namespace` → `FreshDocument`.
   If `Ontology-Build-Schema` fails, propagate its error and stop.

5. Call **`Ontology-Admin-Compare`** with `BaseDocument = OntologyDocument`, `TargetDocument = FreshDocument`, `IncludeIndividuals = false` → `Diff`.

6. Build `RebuildSummary` from `Diff.Summary`:
   - `ClassesAdded` = `Diff.Summary.ClassesAdded`
   - `ClassesRemoved` = `Diff.Summary.ClassesRemoved`
   - `ClassesUnchanged` = `FreshDocument.ClassCount` − `ClassesAdded`
   - `PropertiesAdded` = `Diff.Summary.PropertiesAdded`
   - `PropertiesRemoved` = `Diff.Summary.PropertiesRemoved`
   - `PropertiesChanged` = `Diff.Summary.PropertiesChanged`

7. Apply `PreserveIndividuals`:
   - If `true` and `OntologyDocument.Individuals` is non-empty: copy `OntologyDocument.Individuals` and `IndividualCount` into `FreshDocument`. Set `IndividualsPreserved = OntologyDocument.IndividualCount`, `IndividualsDiscarded = 0`.
   - If `false` or `OntologyDocument.Individuals` is empty: leave `FreshDocument.Individuals` empty. Set `IndividualsPreserved = 0`, `IndividualsDiscarded = OntologyDocument.IndividualCount`.

8. Return `FreshDocument` as `OntologyDocument` together with `RebuildSummary`.

## Error Codes

| Code | Condition |
|---|---|
| `ONTOLOGY_ADMIN_NO_DOCUMENT` | `OntologyDocument` is null or missing its `Classes` array |
| `ONTOLOGY_ADMIN_NO_NAMESPACE` | `Namespace` is null or missing `BaseIRI` |
| `ONTOLOGY_ADMIN_REBUILD_NOT_CONNECTED` | `ConnectionName` is not registered in the current session |

## Dependencies

- `Ontology-Build-Schema`
- `Ontology-Admin-Compare`
