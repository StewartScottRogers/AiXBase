# Ontology-Validate-Individuals

Check every `owl:NamedIndividual` in an OntologyDocument against the class schema: verify that each individual's type resolves to a known class, that every property assertion's predicate is declared in the schema with the correct domain, and that object-property values reference existing individuals.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `OntologyDocument` | object | Yes | — | Result of `Ontology-Populate-Records`. Must contain `Individuals`. |

## Outputs

```json
{
  "Success": true,
  "Valid": true,
  "Issues": [],
  "IssueCount": 0
}
```

On failure:

```json
{
  "Success": true,
  "Valid": false,
  "Issues": [
    {
      "Severity": "Error",
      "Code": "ONTOLOGY_IND_UNKNOWN_TYPE",
      "IndividualIRI": "http://xbase.local/mydb#Orders_99",
      "Message": "Individual type 'http://xbase.local/mydb#Orders' has no matching Class in OntologyDocument."
    }
  ],
  "IssueCount": 1
}
```

## Steps

1. Validate `OntologyDocument` is non-null and contains `Classes`, `DatatypeProperties`, `ObjectProperties`, and `Individuals`; if missing return `ONTOLOGY_VALIDATE_DOCUMENT_INVALID`.
2. Build lookup sets:
   - `ClassIRIs`: set of all `Classes[*].IRI`.
   - `DPMap`: map of `DatatypeProperty.IRI → DatatypeProperty` for all datatype properties.
   - `OPMap`: map of `ObjectProperty.IRI → ObjectProperty` for all object properties.
   - `IndividualIRIs`: set of all `Individuals[*].IRI`.
3. For each individual in `OntologyDocument.Individuals`:

   **Type check (Error):**
   - If `Individual.Type` is not in `ClassIRIs`, emit `ONTOLOGY_IND_UNKNOWN_TYPE`.

   **Property assertion checks:**
   - For each `PropertyAssertion` in `Individual.PropertyAssertions`:
     - If `IsObjectProperty = true`:
       - If `Assertion.Property` is not in `OPMap`, emit `ONTOLOGY_IND_UNKNOWN_PROPERTY` (Error).
       - Else if `OPMap[Assertion.Property].Domain ≠ Individual.Type`, emit `ONTOLOGY_IND_DOMAIN_MISMATCH` (Warning).
       - Else if `Assertion.Value` is not in `IndividualIRIs`, emit `ONTOLOGY_IND_DANGLING_OBJECT_REF` (Warning — the referenced individual was not populated, possibly due to a `Tables` or `Filter` restriction).
     - If `IsObjectProperty = false`:
       - If `Assertion.Property` is not in `DPMap`, emit `ONTOLOGY_IND_UNKNOWN_PROPERTY` (Error).
       - Else if `DPMap[Assertion.Property].Domain ≠ Individual.Type`, emit `ONTOLOGY_IND_DOMAIN_MISMATCH` (Warning).

4. Set `Valid = (no Error-severity issues found)`.
5. Return `Valid`, `Issues`, and `IssueCount`.

## Issue Codes

| Code | Severity | Meaning |
|------|----------|---------|
| `ONTOLOGY_IND_UNKNOWN_TYPE` | Error | Individual's `Type` IRI matches no class |
| `ONTOLOGY_IND_UNKNOWN_PROPERTY` | Error | A property assertion's predicate IRI is not in the schema |
| `ONTOLOGY_IND_DOMAIN_MISMATCH` | Warning | Property's declared domain does not match the individual's type |
| `ONTOLOGY_IND_DANGLING_OBJECT_REF` | Warning | Object property value IRI is not a known individual (partial population) |

## Error Codes

| Code | Condition |
|------|-----------|
| `ONTOLOGY_VALIDATE_DOCUMENT_INVALID` | `OntologyDocument` is null or missing `Individuals`. |

## Dependencies

- `Ontology-Populate-Records`
- `Ontology-Validate-Schema` (recommended first — individual validation assumes a valid schema)
