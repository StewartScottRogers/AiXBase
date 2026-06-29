# Ontology-Validate-Schema

Check an OntologyDocument for OWL structural consistency: verify that every property's domain and range IRIs resolve to known classes, that no IRI is declared twice, and that all required fields are present.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `OntologyDocument` | object | Yes | — | Result of `Ontology-Build-Schema`. |

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
      "Code": "ONTOLOGY_SCHEMA_ORPHAN_DOMAIN",
      "EntityIRI": "http://xbase.local/mydb#Orders_CustomerId",
      "Message": "Domain IRI 'http://xbase.local/mydb#Orders' has no matching Class in OntologyDocument."
    }
  ],
  "IssueCount": 1
}
```

## Steps

1. Validate `OntologyDocument` is non-null and contains `Classes`, `DatatypeProperties`, and `ObjectProperties`; if missing return `ONTOLOGY_VALIDATE_DOCUMENT_INVALID`.
2. Build a set of all known class IRIs from `OntologyDocument.Classes[*].IRI`.
3. Build a set of all known property IRIs (union of `DatatypeProperties[*].IRI` and `ObjectProperties[*].IRI`).
4. Run the following checks and collect issues (each issue has `Severity`, `Code`, `EntityIRI`, `Message`):

   **Duplicate IRI check (Error):**
   - If any two Classes share the same `IRI`, emit `ONTOLOGY_SCHEMA_DUPLICATE_CLASS_IRI` for each duplicate.
   - If any two properties (across DatatypeProperties + ObjectProperties) share the same `IRI`, emit `ONTOLOGY_SCHEMA_DUPLICATE_PROPERTY_IRI`.

   **Required field check (Error):**
   - Each Class must have non-empty `IRI` and `Label`; if missing emit `ONTOLOGY_SCHEMA_CLASS_MISSING_FIELD`.
   - Each DatatypeProperty and ObjectProperty must have non-empty `IRI`, `Label`, `Domain`, and `Range`; if any is missing emit `ONTOLOGY_SCHEMA_PROPERTY_MISSING_FIELD`.

   **Domain resolution check (Error):**
   - For each DatatypeProperty and ObjectProperty, verify `Domain` is present in the known class IRI set; if not emit `ONTOLOGY_SCHEMA_ORPHAN_DOMAIN`.

   **Range resolution check (Error for ObjectProperty, Warning for DatatypeProperty):**
   - For each ObjectProperty, verify `Range` is present in the known class IRI set; if not emit `ONTOLOGY_SCHEMA_ORPHAN_OBJECT_RANGE` (Error).
   - For each DatatypeProperty, verify `Range` begins with `xsd:`; if not emit `ONTOLOGY_SCHEMA_UNKNOWN_DATATYPE_RANGE` (Warning).

5. Set `Valid = (no Error-severity issues found)`.
6. Return `Valid`, `Issues`, and `IssueCount`.

## Issue Codes

| Code | Severity | Meaning |
|------|----------|---------|
| `ONTOLOGY_SCHEMA_DUPLICATE_CLASS_IRI` | Error | Two classes share the same IRI |
| `ONTOLOGY_SCHEMA_DUPLICATE_PROPERTY_IRI` | Error | Two properties share the same IRI |
| `ONTOLOGY_SCHEMA_CLASS_MISSING_FIELD` | Error | A class is missing `IRI` or `Label` |
| `ONTOLOGY_SCHEMA_PROPERTY_MISSING_FIELD` | Error | A property is missing a required field |
| `ONTOLOGY_SCHEMA_ORPHAN_DOMAIN` | Error | A property's `Domain` IRI matches no class |
| `ONTOLOGY_SCHEMA_ORPHAN_OBJECT_RANGE` | Error | An ObjectProperty's `Range` IRI matches no class |
| `ONTOLOGY_SCHEMA_UNKNOWN_DATATYPE_RANGE` | Warning | A DatatypeProperty's `Range` is not an `xsd:` type |

## Error Codes

| Code | Condition |
|------|-----------|
| `ONTOLOGY_VALIDATE_DOCUMENT_INVALID` | `OntologyDocument` is null or missing required arrays. |

## Dependencies

- `Ontology-Build-Schema`
