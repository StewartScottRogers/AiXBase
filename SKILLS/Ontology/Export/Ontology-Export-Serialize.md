# Ontology-Export-Serialize

Serialize an in-session OWL ontology document to one of four RDF interchange formats (Turtle, JSON-LD, RDF-XML, N-Triples) and optionally write the result to a file.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `OntologyDocument` | object | Yes | — | Result of `Ontology-Build-Schema`. |
| `Format` | string | Yes | — | Serialization format: `Turtle`, `JSON-LD`, `RDF-XML`, or `N-Triples`. |
| `OutputPath` | string | No | — | Absolute path to write the serialized ontology. If omitted the result is returned inline as `Serialized`. |

## Outputs

When `OutputPath` is supplied:

```json
{
  "Success": true,
  "Format": "Turtle",
  "FilePath": "C:\\output\\mydb.ttl",
  "ByteCount": 4832
}
```

When `OutputPath` is omitted:

```json
{
  "Success": true,
  "Format": "Turtle",
  "Serialized": "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n..."
}
```

## Steps

1. Validate `OntologyDocument` is non-null and contains `Namespace`, `Classes`, `DatatypeProperties`, and `ObjectProperties`. If any field is missing, return `ONTOLOGY_EXPORT_DOCUMENT_INVALID`.
2. Validate `Format` is one of `Turtle`, `JSON-LD`, `RDF-XML`, `N-Triples`. If not, return `ONTOLOGY_EXPORT_FORMAT_UNKNOWN`.
3. Expand all IRIs: the local portion of each IRI is the segment after the last `#` or `/` in `Namespace.BaseIRI`. Prefixed names such as `xsd:integer` are expanded using `Namespace.PrefixMap`.
4. Serialize according to `Format`:

   **Turtle** (`.ttl`):
   - Emit `@prefix` lines for every entry in `PrefixMap`.
   - Emit an `owl:Ontology` declaration block using `BaseIRI` as the ontology IRI and `OntologyLabel` as `rdfs:label`.
   - Emit one block per `Classes` entry:
     ```turtle
     <IRI> a owl:Class ; rdfs:label "{Label}" ; rdfs:comment "{Comment}" .
     ```
   - Emit one block per `DatatypeProperties` entry:
     ```turtle
     <IRI> a owl:DatatypeProperty ; rdfs:label "{Label}" ; rdfs:domain <Domain> ; rdfs:range <Range> .
     ```
   - Emit one block per `ObjectProperties` entry:
     ```turtle
     <IRI> a owl:ObjectProperty ; rdfs:label "{Label}" ; rdfs:domain <Domain> ; rdfs:range <Range> .
     ```

   **JSON-LD** (`.jsonld`):
   - Emit a `@context` object built from `PrefixMap`.
   - Emit a `@graph` array. Each Class entry becomes `{"@id": IRI, "@type": "owl:Class", "rdfs:label": Label, "rdfs:comment": Comment}`. Each DatatypeProperty becomes `{"@id": IRI, "@type": "owl:DatatypeProperty", "rdfs:domain": {"@id": Domain}, "rdfs:range": {"@id": Range}}`. Same pattern for ObjectProperty.

   **RDF-XML** (`.owl` or `.rdf`):
   - Emit an XML declaration and `rdf:RDF` root element with namespace declarations from `PrefixMap`.
   - Emit one `owl:Class` element per class, one `owl:DatatypeProperty` element per datatype property, one `owl:ObjectProperty` element per object property, each with `rdf:about`, `rdfs:label`, and relevant `rdfs:domain`/`rdfs:range` child elements.

   **N-Triples** (`.nt`):
   - Emit one triple per RDF statement with fully expanded IRIs in angle brackets.
   - One type assertion triple per class/property (`<IRI> <rdf:type> <owl:Class> .`).
   - One `rdfs:label` triple, one `rdfs:domain` triple, one `rdfs:range` triple per property.

5. If `OutputPath` is supplied: write the serialized text to the file at `OutputPath` using `write-text-file(OutputPath, serialized)`. Return `FilePath` and `ByteCount`.
6. If `OutputPath` is omitted: return the serialized text as `Serialized`.

## Error Codes

| Code | Condition |
|------|-----------|
| `ONTOLOGY_EXPORT_DOCUMENT_INVALID` | `OntologyDocument` is null or missing required fields. |
| `ONTOLOGY_EXPORT_FORMAT_UNKNOWN` | `Format` is not one of `Turtle`, `JSON-LD`, `RDF-XML`, `N-Triples`. |
| `ONTOLOGY_EXPORT_WRITE_FAILED` | File write to `OutputPath` failed (permission denied, path not found, etc.). |

## Dependencies

- `Ontology-Build-Schema`
