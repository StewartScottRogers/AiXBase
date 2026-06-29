# Ontology

The Ontology bundle maps any connected XBase database schema into RDF/OWL format on the fly, producing a standards-compliant ontology document that an AI or external tool can consume for semantic reasoning, schema discovery, or knowledge-graph integration.

No ontology files need to be authored in advance. The skills introspect a live XBase connection, translate its tables and columns into OWL classes and properties using a deterministic mapping, and either return the result in-session or write it to a file in a chosen serialization format.

---

## Mapping Rules

The mapping from XBase concepts to OWL/RDF is mechanistic and fully deterministic:

| XBase concept | OWL/RDF concept |
|---|---|
| Table | `owl:Class` — IRI is `{BaseIRI}{TableName}` |
| Non-PK column (no FK) | `owl:DatatypeProperty` — domain is the table class, range is the XSD type |
| Non-PK column with FK | `owl:ObjectProperty` — domain is the table class, range is the referenced table's class |
| Primary key column | Not emitted — the primary key value becomes the local identifier of an individual (used only when record population is added in a future version) |

### XBase Type → XSD Range

| XBase Type | XSD Range |
|---|---|
| `INTEGER` | `xsd:integer` |
| `TEXT` | `xsd:string` |
| `REAL` / `FLOAT` | `xsd:decimal` |
| `DOUBLE` | `xsd:double` |
| `BOOLEAN` | `xsd:boolean` |
| `DATE` | `xsd:date` |
| `DATETIME` / `TIMESTAMP` | `xsd:dateTime` |
| `BLOB` | `xsd:hexBinary` |
| *(unknown)* | `xsd:string` |

### Property IRI Convention

All properties follow `{BaseIRI}{TableName}_{ColumnName}`, making IRIs unambiguous across tables even when column names collide (for example, every table has a `CreatedAt` column).

---

## Skill Groups

### Namespace (1 skill)

`Ontology-Namespace-Define` configures the base IRI and prefix for the session. It builds the full `PrefixMap` including the four standard semantic-web prefixes (`owl`, `rdf`, `rdfs`, `xsd`) plus the user-defined prefix. Call this once before `Ontology-Build-Schema`. The resulting `Namespace` object is passed as an input to all downstream Ontology skills.

### Build (1 skill)

`Ontology-Build-Schema` calls `XBase-Schema-TableList` and then `XBase-Schema-ColumnList` for every table. It applies the mapping rules above and returns an `OntologyDocument` object — an in-session data structure containing `Classes`, `DatatypeProperties`, and `ObjectProperties` arrays. No files are written at this stage.

### Export (1 skill)

`Ontology-Export-Serialize` accepts an `OntologyDocument` and a `Format` and produces the serialized ontology text in one of four standard RDF interchange formats. The result can be returned inline as `Serialized` or written to a file at `OutputPath`.

---

## Supported Serialization Formats

| Format | File Extension | Notes |
|---|---|---|
| `Turtle` | `.ttl` | Human-readable, compact; the recommended format for inspection and diff |
| `JSON-LD` | `.jsonld` | JSON-native; well-suited for API consumption and JavaScript tooling |
| `RDF-XML` | `.owl` / `.rdf` | Maximum tool compatibility; required by many legacy OWL reasoners |
| `N-Triples` | `.nt` | Line-oriented; easiest to stream, parse, or import into triple stores |

---

## Typical Workflow

```
1. XBase-Database-Connect
   ConnectionName: "myapp"
   DatabaseName:   "myapp"

2. Ontology-Namespace-Define
   DatabaseName: "myapp"
   → returns Namespace

3. Ontology-Build-Schema
   ConnectionName: "myapp"
   Namespace:      <result from step 2>
   → returns OntologyDocument

4. Ontology-Export-Serialize
   OntologyDocument: <result from step 3>
   Format:           "Turtle"
   OutputPath:       "C:\\output\\myapp.ttl"
```

---

## v1 Scope (Schema-Only)

The current version maps schema structure only — tables become classes, columns become properties. Records are not mapped to `owl:NamedIndividual` instances. Record population is planned for a future version.

---

## Error Code Prefix

All Ontology error codes begin with `ONTOLOGY_`.
