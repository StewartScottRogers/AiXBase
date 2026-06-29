# Ontology-Query-Execute

Evaluate a basic graph pattern (BGP) query against an in-session OntologyDocument and return variable bindings for each matching solution.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `OntologyDocument` | object | Yes | — | Result of `Ontology-Build-Schema` or `Ontology-Populate-Records`. |
| `Select` | array | Yes | — | Variable names to return, each prefixed with `?` (e.g. `["?class", "?label"]`). Use `["*"]` to return all bound variables. |
| `Patterns` | array | Yes | — | Array of triple pattern objects; see format below. |
| `Limit` | integer | No | none | Maximum number of result rows to return. |
| `Offset` | integer | No | `0` | Number of result rows to skip before returning. |

### Triple Pattern Format

Each element of `Patterns` is an object with three fields:

| Field | Value |
|-------|-------|
| `Subject` | An IRI string, a prefixed name (`mydb:Users`), or a variable (`?s`) |
| `Predicate` | An IRI, prefixed name, or variable (`?p`) |
| `Object` | An IRI, prefixed name, literal string, or variable (`?o`) |

Supported predicate IRIs and their aliases:

| Alias | Expands to |
|-------|-----------|
| `rdf:type` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#type` |
| `rdfs:label` | `http://www.w3.org/2000/01/rdf-schema#label` |
| `rdfs:domain` | `http://www.w3.org/2000/01/rdf-schema#domain` |
| `rdfs:range` | `http://www.w3.org/2000/01/rdf-schema#range` |
| `rdfs:comment` | `http://www.w3.org/2000/01/rdf-schema#comment` |
| `owl:Class` | `http://www.w3.org/2002/07/owl#Class` |
| `owl:DatatypeProperty` | `http://www.w3.org/2002/07/owl#DatatypeProperty` |
| `owl:ObjectProperty` | `http://www.w3.org/2002/07/owl#ObjectProperty` |
| `owl:NamedIndividual` | `http://www.w3.org/2002/07/owl#NamedIndividual` |

## Outputs

```json
{
  "Success": true,
  "Bindings": [
    { "class": "http://xbase.local/mydb#Users", "label": "Users" },
    { "class": "http://xbase.local/mydb#Products", "label": "Products" }
  ],
  "TotalCount": 2,
  "ReturnedCount": 2
}
```

Variable names in `Bindings` appear without the `?` prefix.

## Steps

1. Validate `OntologyDocument` is non-null and contains at least `Classes`; if missing return `ONTOLOGY_QUERY_DOCUMENT_INVALID`.
2. Validate each element of `Patterns` has `Subject`, `Predicate`, and `Object` fields; if any is malformed return `ONTOLOGY_QUERY_PATTERN_INVALID`.
3. Flatten `OntologyDocument` into an in-memory triple set. Each entity produces the following triples:

   **Per Class entry:**
   - `(Class.IRI, rdf:type, owl:Class)`
   - `(Class.IRI, rdfs:label, Class.Label)`
   - `(Class.IRI, rdfs:comment, Class.Comment)`

   **Per DatatypeProperty entry:**
   - `(DP.IRI, rdf:type, owl:DatatypeProperty)`
   - `(DP.IRI, rdfs:label, DP.Label)`
   - `(DP.IRI, rdfs:domain, DP.Domain)`
   - `(DP.IRI, rdfs:range, DP.Range)`

   **Per ObjectProperty entry:**
   - `(OP.IRI, rdf:type, owl:ObjectProperty)`
   - `(OP.IRI, rdfs:label, OP.Label)`
   - `(OP.IRI, rdfs:domain, OP.Domain)`
   - `(OP.IRI, rdfs:range, OP.Range)`

   **Per Individual entry (if present):**
   - `(Ind.IRI, rdf:type, owl:NamedIndividual)`
   - `(Ind.IRI, rdf:type, Ind.Type)`
   - For each PropertyAssertion: `(Ind.IRI, Assertion.Property, Assertion.Value)`

4. Evaluate `Patterns` against the triple set using standard BGP join semantics:
   - Start with a single empty solution mapping `{}`.
   - For each pattern in order, extend each current solution by unifying the pattern's terms against triples: IRIs and literals match only equal values; variables match any value and bind that variable in the solution. Discard solutions where unification fails or where a variable would need to bind two different values.
   - The result is the set of all complete solution mappings after processing every pattern.
5. Project each solution to the variables listed in `Select` (dropping unselected variables). If `Select` is `["*"]`, retain all bound variables.
6. Apply `Offset` and `Limit` to the projected solution list.
7. Strip `?` prefix from variable names in the output bindings.
8. Return `Bindings`, `TotalCount` (before offset/limit), and `ReturnedCount`.

## Error Codes

| Code | Condition |
|------|-----------|
| `ONTOLOGY_QUERY_DOCUMENT_INVALID` | `OntologyDocument` is null or missing `Classes`. |
| `ONTOLOGY_QUERY_PATTERN_INVALID` | A triple pattern is missing `Subject`, `Predicate`, or `Object`. |

## Dependencies

- `Ontology-Build-Schema`
- `Ontology-Populate-Records` (required only if querying individuals)
