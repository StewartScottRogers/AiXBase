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

### Populate (1 skill)

`Ontology-Populate-Records` extends an existing `OntologyDocument` with `owl:NamedIndividual` instances. For each row returned by `XBase-Record-Select`, it constructs an individual whose IRI is `{BaseIRI}{TableName}_{Id}`, whose type is the table's class, and whose property assertions map each non-null field to its corresponding datatype or object property. Accepts an optional `Tables` filter (to populate a subset of tables) and an optional `Filter` and `Limit` (to restrict which rows are loaded). The returned `OntologyDocument` gains an `Individuals` array and an `IndividualCount`.

### Query (2 skills)

`Ontology-Query-Execute` evaluates a basic graph pattern (BGP) query over the flattened triple set of an `OntologyDocument`. The caller supplies `Select` variable names and a `Patterns` array of triple-pattern objects (`Subject`, `Predicate`, `Object`) where any term may be a variable (`?name`). The skill joins patterns sequentially, returns variable bindings for each solution, and supports `Limit` and `Offset`.

`Ontology-Query-Describe` returns all triples in the document where a given IRI is the subject — a convenient focused view without writing a full BGP query.

### Validate (2 skills)

`Ontology-Validate-Schema` checks OWL structural consistency: duplicate IRIs, missing required fields, property domains that don't resolve to a known class, object-property ranges that don't resolve to a known class, and datatype-property ranges that aren't `xsd:` types. Returns a `Valid` flag and an `Issues` array with severity, code, entity IRI, and message for each finding.

`Ontology-Validate-Individuals` checks every `owl:NamedIndividual` against the class schema: unknown types, property assertions whose predicates aren't declared in the schema, domain mismatches, and dangling object-property references (FK values pointing to individuals not in the document). Recommended to run after `Ontology-Validate-Schema`.

### Export (1 skill)

`Ontology-Export-Serialize` accepts an `OntologyDocument` and a `Format` and produces the serialized ontology text in one of four standard RDF interchange formats. The result can be returned inline as `Serialized` or written to a file at `OutputPath`. Individuals, if present, are serialized alongside classes and properties.

### Session (1 skill)

`Ontology-Session` drives a guided interactive loop in the conversation. It presents a numbered menu (Build Schema, Populate Records, Query, Describe Resource, Validate Schema, Validate Individuals, Export, Namespace Settings, Exit), dispatches the user's selection to the appropriate Ontology skill, and renders results as readable markdown. All state (the current `OntologyDocument` and `Namespace`) is held in-session across menu iterations.

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

### Schema-only (export)

```
1. XBase-Database-Connect        ConnectionName: "myapp", DatabaseName: "myapp"
2. Ontology-Namespace-Define     DatabaseName: "myapp"           → Namespace
3. Ontology-Build-Schema         ConnectionName, Namespace       → OntologyDocument
4. Ontology-Validate-Schema      OntologyDocument                → Valid + Issues
5. Ontology-Export-Serialize     OntologyDocument, Format: "Turtle", OutputPath: "myapp.ttl"
```

### Full population and query

```
1–3. (same as above)
4. Ontology-Populate-Records     ConnectionName, OntologyDocument         → OntologyDocument
5. Ontology-Validate-Individuals OntologyDocument                         → Valid + Issues
6. Ontology-Query-Execute        OntologyDocument,
                                 Select: ["?ind", "?label"],
                                 Patterns: [{ Subject: "?ind", Predicate: "rdf:type", Object: "myapp:Users" },
                                            { Subject: "?ind", Predicate: "myapp:Users_Username", Object: "?label" }]
7. Ontology-Export-Serialize     OntologyDocument, Format: "JSON-LD"
```

### Interactive exploration

```
1. XBase-Database-Connect        ConnectionName: "myapp", DatabaseName: "myapp"
2. Ontology-Session              ConnectionName: "myapp", DatabaseName: "myapp"
   → guided menu-driven loop
```

---

## Error Code Prefix

All Ontology error codes begin with `ONTOLOGY_`.
