# Ontology-Namespace-Define

Configure the base IRI and prefix map used by all subsequent Ontology skills in the session.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `DatabaseName` | string | Yes | — | Name of the connected database; used to derive default IRI and prefix. |
| `BaseIRI` | string | No | `http://xbase.local/{DatabaseName}#` | Base IRI for the ontology namespace. Must end with `#` or `/`. |
| `Prefix` | string | No | `{DatabaseName}` lowercased, non-alphanumeric chars stripped | Short prefix token used in Turtle and SPARQL serializations. |
| `OntologyLabel` | string | No | `{DatabaseName} Ontology` | Human-readable `rdfs:label` for the `owl:Ontology` declaration. |

## Outputs

```json
{
  "Success": true,
  "Namespace": {
    "BaseIRI": "http://xbase.local/mydb#",
    "Prefix": "mydb",
    "OntologyLabel": "mydb Ontology",
    "PrefixMap": {
      "owl":  "http://www.w3.org/2002/07/owl#",
      "rdf":  "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
      "xsd":  "http://www.w3.org/2001/XMLSchema#",
      "mydb": "http://xbase.local/mydb#"
    }
  }
}
```

## Steps

1. If `BaseIRI` is supplied, validate that it is a syntactically legal IRI and ends with `#` or `/`; if not, return `ONTOLOGY_NAMESPACE_IRI_INVALID`.
2. If `BaseIRI` is omitted, set it to `http://xbase.local/{DatabaseName}#`.
3. If `Prefix` is omitted, derive it by lowercasing `DatabaseName` and stripping any character that is not `[a-z0-9_]`.
4. If `OntologyLabel` is omitted, set it to `{DatabaseName} Ontology`.
5. Build `PrefixMap` with the four standard semantic-web prefixes plus the user prefix:

   | Prefix | IRI |
   |--------|-----|
   | `owl`  | `http://www.w3.org/2002/07/owl#` |
   | `rdf`  | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
   | `rdfs` | `http://www.w3.org/2000/01/rdf-schema#` |
   | `xsd`  | `http://www.w3.org/2001/XMLSchema#` |
   | `{Prefix}` | `{BaseIRI}` |

6. Store the resulting `Namespace` object in the session as `OntologyNamespace` for use by subsequent Ontology skills.
7. Return `Namespace`.

## Error Codes

| Code | Condition |
|------|-----------|
| `ONTOLOGY_NAMESPACE_IRI_INVALID` | `BaseIRI` is not a legal IRI or does not end with `#` or `/`. |

## Dependencies

None — this is the entry-point skill for all Ontology operations.
