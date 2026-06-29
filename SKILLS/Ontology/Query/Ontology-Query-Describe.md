# Ontology-Query-Describe

Return all RDF triples in which a given IRI appears as the subject, providing a complete description of one resource in the OntologyDocument.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `OntologyDocument` | object | Yes | — | Result of `Ontology-Build-Schema` or `Ontology-Populate-Records`. |
| `ResourceIRI` | string | Yes | — | The fully expanded IRI of the resource to describe. Prefixed names (`mydb:Users`) are resolved using `OntologyDocument.Namespace.PrefixMap`. |

## Outputs

```json
{
  "Success": true,
  "ResourceIRI": "http://xbase.local/mydb#Users",
  "Triples": [
    {
      "Subject": "http://xbase.local/mydb#Users",
      "Predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
      "Object": "http://www.w3.org/2002/07/owl#Class",
      "ObjectIsLiteral": false
    },
    {
      "Subject": "http://xbase.local/mydb#Users",
      "Predicate": "http://www.w3.org/2000/01/rdf-schema#label",
      "Object": "Users",
      "ObjectIsLiteral": true
    }
  ],
  "TripleCount": 2
}
```

## Steps

1. Validate `OntologyDocument` is non-null and contains at least `Classes`; if missing return `ONTOLOGY_QUERY_DOCUMENT_INVALID`.
2. Resolve `ResourceIRI`: if the value contains a `:` and no `://`, attempt prefix expansion using `OntologyDocument.Namespace.PrefixMap`. If the prefix is not in the map, return `ONTOLOGY_DESCRIBE_IRI_UNRESOLVABLE`.
3. Flatten `OntologyDocument` into a triple set using the same rules as `Ontology-Query-Execute` step 3.
4. Collect all triples where `Subject = ResourceIRI`.
5. If no triples are found, return `ONTOLOGY_DESCRIBE_IRI_NOT_FOUND`.
6. Return `ResourceIRI`, `Triples`, and `TripleCount`.

## Error Codes

| Code | Condition |
|------|-----------|
| `ONTOLOGY_QUERY_DOCUMENT_INVALID` | `OntologyDocument` is null or missing `Classes`. |
| `ONTOLOGY_DESCRIBE_IRI_UNRESOLVABLE` | A prefix in `ResourceIRI` is not in `PrefixMap`. |
| `ONTOLOGY_DESCRIBE_IRI_NOT_FOUND` | No triples in the document have `ResourceIRI` as the subject. |

## Dependencies

- `Ontology-Build-Schema`
- `Ontology-Populate-Records` (required only if describing individuals)
