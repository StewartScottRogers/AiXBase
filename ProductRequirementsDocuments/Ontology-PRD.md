# Product Requirements Document: Ontology

## Overview

The Ontology bundle maps any connected XBase database into RDF/OWL format on the fly. Given an open XBase connection, the skills introspect the schema and optionally the records, produce a standards-compliant in-session `OntologyDocument`, and either return it for downstream query and validation or serialize it to one of four RDF interchange formats.

No ontology files need to be authored in advance. No RDF libraries or triple-store engines are required. All work is expressed as abstract in-session data transformations and, for export, a single text-file write.

**Naming convention:**

```
Ontology-{Group}-{Operation}
```

Examples: `Ontology-Build-Schema`, `Ontology-Query-Execute`, `Ontology-Validate-Schema`

The session skill is an exception: `Ontology-Session` (no group segment, placed at the bundle root).

---

## OntologyDocument — Central Data Structure

The `OntologyDocument` is the in-session object that all Ontology skills read from and write to. It is passed explicitly between skills as a JSON-serializable object — it is never written to disk automatically.

```json
{
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
  },
  "Classes": [
    {
      "IRI":     "http://xbase.local/mydb#Users",
      "Label":   "Users",
      "Comment": "Represents a row in the XBase Users table."
    }
  ],
  "DatatypeProperties": [
    {
      "IRI":      "http://xbase.local/mydb#Users_Username",
      "Label":    "Username",
      "Domain":   "http://xbase.local/mydb#Users",
      "Range":    "xsd:string",
      "Nullable": false
    }
  ],
  "ObjectProperties": [
    {
      "IRI":    "http://xbase.local/mydb#Sessions_UserId",
      "Label":  "UserId",
      "Domain": "http://xbase.local/mydb#Sessions",
      "Range":  "http://xbase.local/mydb#Users"
    }
  ],
  "Individuals": [
    {
      "IRI":  "http://xbase.local/mydb#Users_1",
      "Type": "http://xbase.local/mydb#Users",
      "PropertyAssertions": [
        {
          "Property":       "http://xbase.local/mydb#Users_Username",
          "Value":          "srogers",
          "IsObjectProperty": false
        }
      ]
    }
  ],
  "ClassCount":             1,
  "DatatypePropertyCount":  1,
  "ObjectPropertyCount":    1,
  "IndividualCount":        1
}
```

`Individuals` and `IndividualCount` are absent until `Ontology-Populate-Records` is called.

---

## XBase → OWL Mapping Specification

### Schema Mapping (`Ontology-Build-Schema`)

| XBase concept | OWL/RDF concept | IRI pattern |
|---|---|---|
| Table | `owl:Class` | `{BaseIRI}{TableName}` |
| Non-PK column, no FK | `owl:DatatypeProperty` | `{BaseIRI}{TableName}_{ColumnName}` |
| Non-PK column with FK | `owl:ObjectProperty` | `{BaseIRI}{TableName}_{ColumnName}` |
| Primary key column | Not emitted | — (primary key value becomes the individual's local ID suffix) |

### XBase Type → XSD Range

| XBase Type | XSD Range |
|---|---|
| `INTEGER` | `xsd:integer` |
| `TEXT` | `xsd:string` |
| `REAL` | `xsd:decimal` |
| `FLOAT` | `xsd:decimal` |
| `DOUBLE` | `xsd:double` |
| `BOOLEAN` | `xsd:boolean` |
| `DATE` | `xsd:date` |
| `DATETIME` | `xsd:dateTime` |
| `TIMESTAMP` | `xsd:dateTime` |
| `BLOB` | `xsd:hexBinary` |
| *(unknown)* | `xsd:string` |

### ObjectProperty Range Derivation

When a column has `ForeignKey = "ReferencedTable.ReferencedColumn"`, the property `Range` is set to `{BaseIRI}{ReferencedTable}`. The referenced column (always `Id`) is not included in the range IRI — the range is the class, not the column.

**Important — FK declaration required:** `Ontology-Build-Schema` emits an `owl:ObjectProperty` **only** for columns that carry an explicit `ForeignKey` field in `_schema.json`. Columns that reference other tables by name convention (e.g. `StatusId`) but lack a `"ForeignKey"` declaration are emitted as `owl:DatatypeProperty` with range `xsd:integer`. Ensure every relationship column in `_schema.json` has `"ForeignKey": "Table.Column"` for the ontology to represent it accurately. The `XBase-Schema-TableCreate` and `XBase-Schema-TableAlter` skills accept a `ForeignKey` property on column definitions; it must be supplied at table-creation time or added via alter.

### Property IRI Convention

All properties follow `{BaseIRI}{TableName}_{ColumnName}`. This approach is deliberately mechanical:

- It is unambiguous across tables even when column names repeat (e.g. every table has `CreatedAt`).
- It does not require semantic judgment about shared concepts.
- It is fully reversible: given a property IRI, the source table and column can always be recovered by splitting at the last `_` that separates a known table name from the column name.

### Record Mapping (`Ontology-Populate-Records`)

| XBase concept | OWL/RDF concept | IRI pattern |
|---|---|---|
| Row | `owl:NamedIndividual` | `{BaseIRI}{TableName}_{Id}` |
| Non-null field value | Datatype property assertion | `(IndividualIRI, PropertyIRI, value)` |
| Non-null FK field value | Object property assertion | `(IndividualIRI, PropertyIRI, {BaseIRI}{ReferencedTable}_{value})` |
| Null field value | Not emitted | — |
| `Id` field | Not emitted as property | — (encoded in the individual's IRI suffix) |

---

## RDF Serialization Formats

`Ontology-Export-Serialize` supports four formats. All four convey identical semantic content.

### Turtle (`.ttl`)

Human-readable, compact. Recommended for inspection and diff. Prefixed names are used throughout; `@prefix` declarations appear at the top of the file.

```turtle
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix mydb: <http://xbase.local/mydb#> .

<http://xbase.local/mydb#>
    a owl:Ontology ;
    rdfs:label "mydb Ontology" .

mydb:Users
    a owl:Class ;
    rdfs:label "Users" ;
    rdfs:comment "Represents a row in the XBase Users table." .

mydb:Users_Username
    a owl:DatatypeProperty ;
    rdfs:label "Username" ;
    rdfs:domain mydb:Users ;
    rdfs:range xsd:string .

mydb:Users_1
    a owl:NamedIndividual, mydb:Users ;
    mydb:Users_Username "srogers" .
```

### JSON-LD (`.jsonld`)

JSON-native. Well-suited for API consumption and JavaScript tooling. The `@context` object maps prefix tokens to their IRI expansions; the `@graph` array contains one object per class, property, and individual.

```json
{
  "@context": {
    "owl":  "http://www.w3.org/2002/07/owl#",
    "rdf":  "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":  "http://www.w3.org/2001/XMLSchema#",
    "mydb": "http://xbase.local/mydb#"
  },
  "@graph": [
    {
      "@id": "http://xbase.local/mydb#Users",
      "@type": "owl:Class",
      "rdfs:label": "Users",
      "rdfs:comment": "Represents a row in the XBase Users table."
    },
    {
      "@id": "http://xbase.local/mydb#Users_Username",
      "@type": "owl:DatatypeProperty",
      "rdfs:label": "Username",
      "rdfs:domain": { "@id": "http://xbase.local/mydb#Users" },
      "rdfs:range":  { "@id": "http://www.w3.org/2001/XMLSchema#string" }
    },
    {
      "@id": "http://xbase.local/mydb#Users_1",
      "@type": ["owl:NamedIndividual", "http://xbase.local/mydb#Users"],
      "http://xbase.local/mydb#Users_Username": "srogers"
    }
  ]
}
```

### RDF-XML (`.owl` / `.rdf`)

Maximum tool compatibility; required by many legacy OWL reasoners and editors. Namespace declarations appear as attributes on the `rdf:RDF` root element. Each entity is a child element.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
  xmlns:owl="http://www.w3.org/2002/07/owl#"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
  xmlns:mydb="http://xbase.local/mydb#">

  <owl:Ontology rdf:about="http://xbase.local/mydb#">
    <rdfs:label>mydb Ontology</rdfs:label>
  </owl:Ontology>

  <owl:Class rdf:about="http://xbase.local/mydb#Users">
    <rdfs:label>Users</rdfs:label>
    <rdfs:comment>Represents a row in the XBase Users table.</rdfs:comment>
  </owl:Class>

  <owl:DatatypeProperty rdf:about="http://xbase.local/mydb#Users_Username">
    <rdfs:label>Username</rdfs:label>
    <rdfs:domain rdf:resource="http://xbase.local/mydb#Users"/>
    <rdfs:range  rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
  </owl:DatatypeProperty>

  <owl:NamedIndividual rdf:about="http://xbase.local/mydb#Users_1">
    <rdf:type rdf:resource="http://xbase.local/mydb#Users"/>
    <mydb:Users_Username>srogers</mydb:Users_Username>
  </owl:NamedIndividual>

</rdf:RDF>
```

### N-Triples (`.nt`)

Line-oriented; one triple per line with fully expanded IRIs. Easiest to stream, parse, or bulk-import into a triple store. Literals are quoted strings; IRIs are in angle brackets.

```
<http://xbase.local/mydb#Users> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .
<http://xbase.local/mydb#Users> <http://www.w3.org/2000/01/rdf-schema#label> "Users" .
<http://xbase.local/mydb#Users> <http://www.w3.org/2000/01/rdf-schema#comment> "Represents a row in the XBase Users table." .
<http://xbase.local/mydb#Users_Username> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .
<http://xbase.local/mydb#Users_Username> <http://www.w3.org/2000/01/rdf-schema#label> "Username" .
<http://xbase.local/mydb#Users_Username> <http://www.w3.org/2000/01/rdf-schema#domain> <http://xbase.local/mydb#Users> .
<http://xbase.local/mydb#Users_Username> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#string> .
<http://xbase.local/mydb#Users_1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#NamedIndividual> .
<http://xbase.local/mydb#Users_1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xbase.local/mydb#Users> .
<http://xbase.local/mydb#Users_1> <http://xbase.local/mydb#Users_Username> "srogers" .
```

---

## Triple Flattening Model

`Ontology-Query-Execute` and `Ontology-Query-Describe` operate on a flattened triple set derived from the `OntologyDocument`. The flattening rules are:

**Per Class:**

| Subject | Predicate | Object |
|---|---|---|
| `Class.IRI` | `rdf:type` | `owl:Class` |
| `Class.IRI` | `rdfs:label` | `Class.Label` (literal) |
| `Class.IRI` | `rdfs:comment` | `Class.Comment` (literal) |

**Per DatatypeProperty:**

| Subject | Predicate | Object |
|---|---|---|
| `DP.IRI` | `rdf:type` | `owl:DatatypeProperty` |
| `DP.IRI` | `rdfs:label` | `DP.Label` (literal) |
| `DP.IRI` | `rdfs:domain` | `DP.Domain` (IRI) |
| `DP.IRI` | `rdfs:range` | `DP.Range` (IRI) |

**Per ObjectProperty:**

| Subject | Predicate | Object |
|---|---|---|
| `OP.IRI` | `rdf:type` | `owl:ObjectProperty` |
| `OP.IRI` | `rdfs:label` | `OP.Label` (literal) |
| `OP.IRI` | `rdfs:domain` | `OP.Domain` (IRI) |
| `OP.IRI` | `rdfs:range` | `OP.Range` (IRI) |

**Per Individual:**

| Subject | Predicate | Object |
|---|---|---|
| `Ind.IRI` | `rdf:type` | `owl:NamedIndividual` |
| `Ind.IRI` | `rdf:type` | `Ind.Type` (IRI) |
| `Ind.IRI` | `Assertion.Property` | `Assertion.Value` (IRI if `IsObjectProperty`, else literal) |

---

## Skill Catalog

| Group | Skill | Description |
|---|---|---|
| Admin | `Ontology-Admin-Inspect` | Health and coverage report for an OntologyDocument |
| Admin | `Ontology-Admin-Compare` | Diff two OntologyDocuments — added, removed, and changed entities |
| Admin | `Ontology-Admin-Rebuild` | Re-introspect live schema and merge into existing document |
| Admin | `Ontology-Admin-Session` | Guided interactive admin TUI for inspection and maintenance |
| Namespace | `Ontology-Namespace-Define` | Configure base IRI and prefix map |
| Build | `Ontology-Build-Schema` | Introspect XBase schema → `owl:Class` + properties |
| Populate | `Ontology-Populate-Records` | Load XBase rows → `owl:NamedIndividual` instances |
| Query | `Ontology-Query-Execute` | BGP pattern query → variable bindings |
| Query | `Ontology-Query-Describe` | Return all triples for a given resource IRI |
| Validate | `Ontology-Validate-Schema` | OWL structural consistency check |
| Validate | `Ontology-Validate-Individuals` | Instance conformance check against class schema |
| Export | `Ontology-Export-Serialize` | Serialize to Turtle / JSON-LD / RDF-XML / N-Triples |
| Session | `Ontology-Session` | Guided interactive TUI over the full bundle |

---

## Skill Specifications

### Ontology-Admin-Inspect

**Inputs**

| Name | Type | Required |
|---|---|---|
| `OntologyDocument` | object | Yes |

**Outputs**
- `ClassCount`, `DatatypePropertyCount`, `ObjectPropertyCount`, `IndividualCount` (integers).
- `FKCoverage`: `{ TotalProperties, ObjectProperties, CoveragePercent }`.
- `PropertyDistribution`: array of `{ ClassIRI, ClassLabel, DatatypePropertyCount, ObjectPropertyCount }`.
- `OrphanProperties`: array of `{ PropertyIRI, Domain }` — properties whose `Domain` matches no class.
- `IsolatedClasses`: array of class IRIs that appear as neither `Domain` of any property nor `Range` of any ObjectProperty.
- `Issues`: array of `{ Severity, Code, EntityIRI, Message }`.
- `IssueCount` (integer).
- `IsHealthy` (boolean) — `true` if `Issues` contains no `Error`-severity entries.

**Steps**
1. Verify `OntologyDocument` has a non-empty `Classes` array; if not, return `ONTOLOGY_ADMIN_NO_DOCUMENT`.
2. Count all arrays; compute `FKCoverage`: `CoveragePercent = ObjectPropertyCount / (DatatypePropertyCount + ObjectPropertyCount) × 100`.
3. Build `PropertyDistribution`: for each class, count properties whose `Domain` equals the class IRI.
4. Find `OrphanProperties`: properties whose `Domain` IRI is not in the class set.
5. Find `IsolatedClasses`: class IRIs not present as `Domain` in any property and not present as `Range` in any ObjectProperty.
6. Build `Issues`: orphan properties → `Warning / ONTOLOGY_ADMIN_INSPECT_ORPHAN_PROPERTY`; isolated classes → `Info / ONTOLOGY_ADMIN_INSPECT_ISOLATED_CLASS`.
7. Set `IsHealthy = (no Error-severity issues)`.
8. Return full report.

---

### Ontology-Admin-Compare

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `BaseDocument` | object | Yes | — |
| `TargetDocument` | object | Yes | — |
| `IncludeIndividuals` | boolean | No | `false` |

**Outputs**
- `NamespaceMismatch` (boolean).
- `AddedClasses`, `RemovedClasses`: arrays of class objects.
- `AddedProperties`, `RemovedProperties`: arrays of property objects with type tag.
- `ChangedProperties`: array of `{ IRI, Changes: [{ Field, Before, After }] }`.
- `AddedIndividuals`, `RemovedIndividuals`: arrays of individual IRIs (empty unless `IncludeIndividuals = true`).
- `Summary`: `{ ClassesAdded, ClassesRemoved, PropertiesAdded, PropertiesRemoved, PropertiesChanged, IndividualsAdded, IndividualsRemoved }`.
- `HasChanges` (boolean).

**Steps**
1. Verify both documents are present; if either missing return `ONTOLOGY_ADMIN_NO_DOCUMENT`.
2. Set `NamespaceMismatch = (BaseDocument.Namespace.BaseIRI ≠ TargetDocument.Namespace.BaseIRI)`.
3. Build IRI-keyed maps for both documents (classes and all properties).
4. Compute Added/Removed/Changed sets by IRI.
5. For `ChangedProperties`: compare `Type`, `Domain`, and `Range` fields.
6. If `IncludeIndividuals = true`: compute Individual IRI sets and diff.
7. Build `Summary`; set `HasChanges`.
8. Return result.

---

### Ontology-Admin-Rebuild

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `ConnectionName` | string | Yes | — |
| `OntologyDocument` | object | Yes | — |
| `Namespace` | object | Yes | — |
| `PreserveIndividuals` | boolean | No | `true` |

**Outputs**
- `OntologyDocument`: the refreshed document.
- `RebuildSummary`: `{ ClassesAdded, ClassesRemoved, ClassesUnchanged, PropertiesAdded, PropertiesRemoved, PropertiesChanged, IndividualsPreserved, IndividualsDiscarded }`.

**Steps**
1. Verify `ConnectionName` is registered; if not return `ONTOLOGY_ADMIN_REBUILD_NOT_CONNECTED`.
2. Verify `OntologyDocument` has a `Classes` array; if not return `ONTOLOGY_ADMIN_NO_DOCUMENT`.
3. Verify `Namespace` has `BaseIRI`; if not return `ONTOLOGY_ADMIN_NO_NAMESPACE`.
4. Call `Ontology-Build-Schema` → `FreshDocument`.
5. Call `Ontology-Admin-Compare` (`BaseDocument = OntologyDocument`, `TargetDocument = FreshDocument`) → `Diff`.
6. Derive `RebuildSummary` from `Diff.Summary`.
7. Apply `PreserveIndividuals`: copy existing `Individuals` into `FreshDocument` or discard; update counts.
8. Return `FreshDocument` as `OntologyDocument` with `RebuildSummary`.

---

### Ontology-Admin-Session

**Inputs**

| Name | Type | Required |
|---|---|---|
| `ConnectionName` | string | Yes |
| `OntologyDocument` | object | No |
| `Namespace` | object | No |

**Outputs**
- `ExitReason` (string: `"UserExit"`).
- `FinalDocument` (the `OntologyDocument` as it stood at exit, or null if never loaded).

**Menu**
```
[1] Inspect Document
[2] Save Snapshot for Compare
[3] Compare with Saved Snapshot
[4] Rebuild from Live Schema
[5] Validate Schema
[6] Validate Individuals
[7] Export Current Document
[8] Exit
```

Options 1–3, 5–7 require a loaded document; option 4 can both create and replace the current document. The session holds `OntologyDocument`, `Namespace`, and `SavedDocument` (snapshot for Compare) across iterations. All delegated skill errors are rendered as readable markdown before returning to the menu.

---

### Ontology-Namespace-Define

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `DatabaseName` | string | Yes | — |
| `BaseIRI` | string | No | `http://xbase.local/{DatabaseName}#` |
| `Prefix` | string | No | `{DatabaseName}` lowercased, non-alphanumeric stripped |
| `OntologyLabel` | string | No | `{DatabaseName} Ontology` |

**Outputs**
- `Namespace` object (as shown in the OntologyDocument structure above)

**Steps**
1. If `BaseIRI` supplied, validate it is a legal IRI ending with `#` or `/`; if not, return `ONTOLOGY_NAMESPACE_IRI_INVALID`.
2. If `BaseIRI` omitted, set to `http://xbase.local/{DatabaseName}#`.
3. If `Prefix` omitted, derive by lowercasing `DatabaseName` and stripping `[^a-z0-9_]`.
4. If `OntologyLabel` omitted, set to `{DatabaseName} Ontology`.
5. Build `PrefixMap` with `owl`, `rdf`, `rdfs`, `xsd`, and `{Prefix}` entries.
6. Store result as `OntologyNamespace` in session.
7. Return `Namespace`.

---

### Ontology-Build-Schema

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `ConnectionName` | string | Yes | — |
| `Namespace` | object | Yes | — |
| `IncludeForeignKeyProperties` | boolean | No | `true` |

**Outputs**
- `OntologyDocument` with `Classes`, `DatatypeProperties`, `ObjectProperties`, and counts.

**Steps**
1. Validate `ConnectionName`; if not registered return `XBASE_CONNECTION_INVALID`.
2. Validate `Namespace` has `BaseIRI` and `PrefixMap`; if not return `ONTOLOGY_BUILD_NAMESPACE_MISSING`.
3. Call `XBase-Schema-TableList`.
4. For each table name:
   a. Call `XBase-Schema-ColumnList`.
   b. Emit `owl:Class` entry: `{ IRI: BaseIRI+TableName, Label: TableName, Comment: "Represents a row in the XBase {TableName} table." }`.
   c. For each non-PK column:
      - If `ForeignKey` is non-null and `IncludeForeignKeyProperties = true`: emit `owl:ObjectProperty` with `Range = BaseIRI + ReferencedTable`.
      - Otherwise: emit `owl:DatatypeProperty` with `Range` from the XBase→XSD mapping table.
5. Return `OntologyDocument`.

---

### Ontology-Populate-Records

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `ConnectionName` | string | Yes | — |
| `OntologyDocument` | object | Yes | — |
| `Tables` | array of string | No | All tables in `Classes` |
| `Filter` | filter spec | No | none |
| `Limit` | integer | No | none |

**Outputs**
- Updated `OntologyDocument` with `Individuals` array and `IndividualCount`.
- `TablesPopulated` (array of table names).
- `IndividualsAdded` (integer).

**Steps**
1. Validate `ConnectionName` and `OntologyDocument`.
2. Resolve `Tables`; validate each against `OntologyDocument.Classes`.
3. For each table: call `XBase-Record-Select` with optional `Filter` and `Limit`.
4. For each row: construct `IndividualIRI = BaseIRI + TableName + "_" + row.Id`; build `PropertyAssertions` by matching each non-null, non-Id field against `ObjectProperties` (FK columns) or `DatatypeProperties` (other columns).
5. Append all individuals; update `OntologyDocument.Individuals` and `IndividualCount`.
6. Return updated `OntologyDocument`, `TablesPopulated`, `IndividualsAdded`.

---

### Ontology-Query-Execute

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `OntologyDocument` | object | Yes | — |
| `Select` | array of string | Yes | — |
| `Patterns` | array of `{Subject, Predicate, Object}` | Yes | — |
| `Limit` | integer | No | none |
| `Offset` | integer | No | `0` |

**Outputs**
- `Bindings` — array of solution mapping objects (variable name → value, without `?` prefix).
- `TotalCount` — total solutions before `Offset`/`Limit`.
- `ReturnedCount` — solutions returned after `Offset`/`Limit`.

**Steps**
1. Validate `OntologyDocument` and `Patterns`.
2. Flatten `OntologyDocument` to a triple set per the Triple Flattening Model.
3. Evaluate BGP: start with one empty solution; for each pattern, extend solutions by unifying against matching triples; discard inconsistent solutions.
4. Project to `Select` variables; apply `Offset` and `Limit`; strip `?` from variable names.
5. Return `Bindings`, `TotalCount`, `ReturnedCount`.

**Supported predicate aliases**

| Alias | Expands to |
|---|---|
| `rdf:type` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#type` |
| `rdfs:label` | `http://www.w3.org/2000/01/rdf-schema#label` |
| `rdfs:domain` | `http://www.w3.org/2000/01/rdf-schema#domain` |
| `rdfs:range` | `http://www.w3.org/2000/01/rdf-schema#range` |
| `rdfs:comment` | `http://www.w3.org/2000/01/rdf-schema#comment` |
| `owl:Class` | `http://www.w3.org/2002/07/owl#Class` |
| `owl:DatatypeProperty` | `http://www.w3.org/2002/07/owl#DatatypeProperty` |
| `owl:ObjectProperty` | `http://www.w3.org/2002/07/owl#ObjectProperty` |
| `owl:NamedIndividual` | `http://www.w3.org/2002/07/owl#NamedIndividual` |

---

### Ontology-Query-Describe

**Inputs**

| Name | Type | Required |
|---|---|---|
| `OntologyDocument` | object | Yes |
| `ResourceIRI` | string | Yes |

**Outputs**
- `ResourceIRI` (string, expanded).
- `Triples` — array of `{ Subject, Predicate, Object, ObjectIsLiteral }`.
- `TripleCount` (integer).

**Steps**
1. Validate `OntologyDocument`.
2. Resolve `ResourceIRI` using `PrefixMap` if it contains a prefix.
3. Flatten `OntologyDocument` to a triple set.
4. Collect all triples where `Subject = ResourceIRI`; if none, return `ONTOLOGY_DESCRIBE_IRI_NOT_FOUND`.
5. Return `ResourceIRI`, `Triples`, `TripleCount`.

---

### Ontology-Validate-Schema

**Inputs**

| Name | Type | Required |
|---|---|---|
| `OntologyDocument` | object | Yes |

**Outputs**
- `Valid` (boolean) — `true` if no Error-severity issues found.
- `Issues` — array of `{ Severity, Code, EntityIRI, Message }`.
- `IssueCount` (integer).

**Checks performed**

| Check | Severity | Issue Code |
|---|---|---|
| Duplicate class IRI | Error | `ONTOLOGY_SCHEMA_DUPLICATE_CLASS_IRI` |
| Duplicate property IRI | Error | `ONTOLOGY_SCHEMA_DUPLICATE_PROPERTY_IRI` |
| Class missing `IRI` or `Label` | Error | `ONTOLOGY_SCHEMA_CLASS_MISSING_FIELD` |
| Property missing required field | Error | `ONTOLOGY_SCHEMA_PROPERTY_MISSING_FIELD` |
| Property `Domain` IRI not in class set | Error | `ONTOLOGY_SCHEMA_ORPHAN_DOMAIN` |
| ObjectProperty `Range` IRI not in class set | Error | `ONTOLOGY_SCHEMA_ORPHAN_OBJECT_RANGE` |
| DatatypeProperty `Range` not `xsd:*` | Warning | `ONTOLOGY_SCHEMA_UNKNOWN_DATATYPE_RANGE` |

---

### Ontology-Validate-Individuals

**Inputs**

| Name | Type | Required |
|---|---|---|
| `OntologyDocument` | object | Yes |

**Outputs**
- `Valid` (boolean).
- `Issues` — array of `{ Severity, Code, IndividualIRI, Message }`.
- `IssueCount` (integer).

**Checks performed**

| Check | Severity | Issue Code |
|---|---|---|
| Individual `Type` IRI not in class set | Error | `ONTOLOGY_IND_UNKNOWN_TYPE` |
| Property assertion predicate not in schema | Error | `ONTOLOGY_IND_UNKNOWN_PROPERTY` |
| Property domain does not match individual type | Warning | `ONTOLOGY_IND_DOMAIN_MISMATCH` |
| Object property value IRI not a known individual | Warning | `ONTOLOGY_IND_DANGLING_OBJECT_REF` |

Run `Ontology-Validate-Schema` first. Individual validation assumes a valid schema.

---

### Ontology-Export-Serialize

**Inputs**

| Name | Type | Required | Default |
|---|---|---|---|
| `OntologyDocument` | object | Yes | — |
| `Format` | string | Yes | — |
| `OutputPath` | string | No | inline |

**Outputs**

If `OutputPath` supplied: `{ Format, FilePath, ByteCount }`.
If `OutputPath` omitted: `{ Format, Serialized }`.

**Supported formats**

| `Format` value | Extension | Notes |
|---|---|---|
| `Turtle` | `.ttl` | `@prefix` declarations + one block per entity |
| `JSON-LD` | `.jsonld` | `@context` + `@graph` array |
| `RDF-XML` | `.owl` / `.rdf` | `rdf:RDF` root + child elements |
| `N-Triples` | `.nt` | One `<S> <P> <O> .` line per triple |

**Steps**
1. Validate `OntologyDocument` and `Format`.
2. Expand all IRI references via `PrefixMap`.
3. Serialize per format rules in the RDF Serialization Formats section.
4. Write to `OutputPath` or return inline.

---

### Ontology-Session

**Inputs**

| Name | Type | Required |
|---|---|---|
| `ConnectionName` | string | Yes |
| `DatabaseName` | string | Yes |

**Outputs**
Conversational markdown. No structured JSON output.

**Menu**

```
[1] Build Schema           → Ontology-Build-Schema
[2] Populate Records       → Ontology-Populate-Records
[3] Query                  → Ontology-Query-Execute
[4] Describe Resource      → Ontology-Query-Describe
[5] Validate Schema        → Ontology-Validate-Schema
[6] Validate Individuals   → Ontology-Validate-Individuals
[7] Export                 → Ontology-Export-Serialize
[8] Namespace Settings     → Ontology-Namespace-Define
[9] Exit
```

State held across iterations: `Namespace` object and current `OntologyDocument`. All delegated skill errors are rendered as readable markdown before returning to the menu.

---

## Error Code Catalog

### Admin (skill-level)

| Code | Condition |
|---|---|
| `ONTOLOGY_ADMIN_NO_DOCUMENT` | `OntologyDocument` is null, missing, or has no `Classes` array |
| `ONTOLOGY_ADMIN_NO_NAMESPACE` | `Namespace` is null or missing `BaseIRI` (Rebuild only) |
| `ONTOLOGY_ADMIN_REBUILD_NOT_CONNECTED` | `ConnectionName` is not registered in the session (Rebuild only) |
| `ONTOLOGY_ADMIN_NO_SNAPSHOT` | Compare-with-snapshot selected in Admin Session before a snapshot was saved |

### Admin (issue codes returned inside `Issues` array from Inspect)

| Code | Severity | Meaning |
|---|---|---|
| `ONTOLOGY_ADMIN_INSPECT_ORPHAN_PROPERTY` | Warning | Property `Domain` IRI matches no class in the document |
| `ONTOLOGY_ADMIN_INSPECT_ISOLATED_CLASS` | Info | Class has no property domains and is not the range of any ObjectProperty |

### Namespace

| Code | Condition |
|---|---|
| `ONTOLOGY_NAMESPACE_IRI_INVALID` | `BaseIRI` is not a legal IRI or does not end with `#` or `/` |

### Build

| Code | Condition |
|---|---|
| `ONTOLOGY_BUILD_NAMESPACE_MISSING` | `Namespace` input is null or missing required fields |

### Populate

| Code | Condition |
|---|---|
| `ONTOLOGY_POPULATE_DOCUMENT_INVALID` | `OntologyDocument` is null or missing required arrays |
| `ONTOLOGY_POPULATE_TABLE_NOT_IN_SCHEMA` | A name in `Tables` has no matching class in `OntologyDocument.Classes` |

### Query

| Code | Condition |
|---|---|
| `ONTOLOGY_QUERY_DOCUMENT_INVALID` | `OntologyDocument` is null or missing `Classes` |
| `ONTOLOGY_QUERY_PATTERN_INVALID` | A triple pattern is missing `Subject`, `Predicate`, or `Object` |
| `ONTOLOGY_DESCRIBE_IRI_UNRESOLVABLE` | A prefix in `ResourceIRI` is not in `PrefixMap` |
| `ONTOLOGY_DESCRIBE_IRI_NOT_FOUND` | No triples have `ResourceIRI` as their subject |

### Validate (skill-level)

| Code | Condition |
|---|---|
| `ONTOLOGY_VALIDATE_DOCUMENT_INVALID` | `OntologyDocument` is null or missing required arrays |

### Validate (issue codes returned inside `Issues` array)

| Code | Severity | Meaning |
|---|---|---|
| `ONTOLOGY_SCHEMA_DUPLICATE_CLASS_IRI` | Error | Two classes share the same IRI |
| `ONTOLOGY_SCHEMA_DUPLICATE_PROPERTY_IRI` | Error | Two properties share the same IRI |
| `ONTOLOGY_SCHEMA_CLASS_MISSING_FIELD` | Error | A class is missing `IRI` or `Label` |
| `ONTOLOGY_SCHEMA_PROPERTY_MISSING_FIELD` | Error | A property is missing a required field |
| `ONTOLOGY_SCHEMA_ORPHAN_DOMAIN` | Error | Property `Domain` IRI matches no class |
| `ONTOLOGY_SCHEMA_ORPHAN_OBJECT_RANGE` | Error | ObjectProperty `Range` IRI matches no class |
| `ONTOLOGY_SCHEMA_UNKNOWN_DATATYPE_RANGE` | Warning | DatatypeProperty `Range` is not an `xsd:` type |
| `ONTOLOGY_IND_UNKNOWN_TYPE` | Error | Individual `Type` IRI matches no class |
| `ONTOLOGY_IND_UNKNOWN_PROPERTY` | Error | Property assertion predicate not in schema |
| `ONTOLOGY_IND_DOMAIN_MISMATCH` | Warning | Property domain does not match individual type |
| `ONTOLOGY_IND_DANGLING_OBJECT_REF` | Warning | Object property value is not a known individual |

### Export

| Code | Condition |
|---|---|
| `ONTOLOGY_EXPORT_DOCUMENT_INVALID` | `OntologyDocument` is null or missing required fields |
| `ONTOLOGY_EXPORT_FORMAT_UNKNOWN` | `Format` is not one of the four supported values |
| `ONTOLOGY_EXPORT_WRITE_FAILED` | File write to `OutputPath` failed |

### Propagated XBase errors

| Code | Condition |
|---|---|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` not registered (Build, Populate) |

---

## Dependencies

- An open XBase connection (`XBase-Database-Connect` already called) is required before `Ontology-Build-Schema`, `Ontology-Populate-Records`, and `Ontology-Admin-Rebuild`.
- All other Ontology skills operate on the in-session `OntologyDocument` — no XBase connection is needed once the document is built.
- `Ontology-Admin-Rebuild` calls `Ontology-Build-Schema` and `Ontology-Admin-Compare` internally.
- `Ontology-Admin-Session` calls `Ontology-Admin-Inspect`, `Ontology-Admin-Compare`, `Ontology-Admin-Rebuild`, `Ontology-Validate-Schema`, `Ontology-Validate-Individuals`, `Ontology-Export-Serialize`, and `Ontology-Namespace-Define`.
- No external RDF libraries, triple-store engines, SPARQL processors, or network connectivity are required.
- All skill inputs and outputs are JSON-serializable.
- Harness-agnostic: any AI agent that can follow the numbered skill steps and perform a single `write-text-file` operation can implement the full bundle.
