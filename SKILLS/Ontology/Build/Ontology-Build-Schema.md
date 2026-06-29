# Ontology-Build-Schema

Introspect the schema of a connected XBase database and produce an in-session OWL ontology document: one `owl:Class` per table and one `owl:DatatypeProperty` or `owl:ObjectProperty` per non-primary-key column.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `ConnectionName` | string | Yes | — | Open XBase connection alias. |
| `Namespace` | object | Yes | — | Result of `Ontology-Namespace-Define`. |
| `IncludeForeignKeyProperties` | boolean | No | `true` | When `true`, columns with a `ForeignKey` value are emitted as `owl:ObjectProperty` pointing to the referenced class. When `false`, they are emitted as `owl:DatatypeProperty xsd:integer` like any plain integer column. |

## Outputs

```json
{
  "Success": true,
  "OntologyDocument": {
    "Namespace": {
      "BaseIRI": "http://xbase.local/mydb#",
      "Prefix": "mydb",
      "OntologyLabel": "mydb Ontology",
      "PrefixMap": {}
    },
    "Classes": [
      {
        "IRI": "http://xbase.local/mydb#Products",
        "Label": "Products",
        "Comment": "Represents a row in the XBase Products table."
      }
    ],
    "DatatypeProperties": [
      {
        "IRI": "http://xbase.local/mydb#Products_Name",
        "Label": "Name",
        "Domain": "http://xbase.local/mydb#Products",
        "Range": "xsd:string",
        "Nullable": true
      }
    ],
    "ObjectProperties": [
      {
        "IRI": "http://xbase.local/mydb#Sessions_UserId",
        "Label": "UserId",
        "Domain": "http://xbase.local/mydb#Sessions",
        "Range": "http://xbase.local/mydb#Users"
      }
    ],
    "ClassCount": 1,
    "DatatypePropertyCount": 1,
    "ObjectPropertyCount": 1
  }
}
```

## Steps

1. Validate `ConnectionName`; if not registered, return `XBASE_CONNECTION_INVALID`.
2. Validate `Namespace` contains `BaseIRI` and `PrefixMap`; if malformed, return `ONTOLOGY_BUILD_NAMESPACE_MISSING`.
3. Call `XBase-Schema-TableList` with `ConnectionName`. If it fails, propagate the error unchanged.
4. Initialize `Classes = []`, `DatatypeProperties = []`, `ObjectProperties = []`.
5. For each table name returned by step 3:
   a. Call `XBase-Schema-ColumnList` with `ConnectionName` and `TableName`. If it fails, propagate the error unchanged.
   b. Append to `Classes`:
      ```
      { IRI: BaseIRI + TableName, Label: TableName, Comment: "Represents a row in the XBase {TableName} table." }
      ```
   c. For each column in the `Columns` array:
      - If `PrimaryKey = true`: skip — the primary key is not represented as a property; it becomes the individual's local identifier.
      - If `ForeignKey` is non-null and `IncludeForeignKeyProperties = true`:
        - Parse `ForeignKey` (format `"ReferencedTable.ReferencedColumn"`) to extract `ReferencedTable`.
        - Append to `ObjectProperties`:
          ```
          { IRI: BaseIRI + TableName + "_" + ColumnName, Label: ColumnName, Domain: BaseIRI + TableName, Range: BaseIRI + ReferencedTable }
          ```
      - Otherwise: append to `DatatypeProperties`:
        ```
        { IRI: BaseIRI + TableName + "_" + ColumnName, Label: ColumnName, Domain: BaseIRI + TableName, Range: <xsd type from mapping below>, Nullable: column.Nullable }
        ```
6. XBase type → XSD range mapping:

   | XBase Type | XSD Range |
   |------------|-----------|
   | `INTEGER`  | `xsd:integer` |
   | `TEXT`     | `xsd:string` |
   | `REAL`     | `xsd:decimal` |
   | `FLOAT`    | `xsd:decimal` |
   | `DOUBLE`   | `xsd:double` |
   | `BOOLEAN`  | `xsd:boolean` |
   | `DATE`     | `xsd:date` |
   | `DATETIME` | `xsd:dateTime` |
   | `TIMESTAMP`| `xsd:dateTime` |
   | `BLOB`     | `xsd:hexBinary` |
   | *(unknown)*| `xsd:string` |

7. Build and return `OntologyDocument`:
   ```
   { Namespace, Classes, DatatypeProperties, ObjectProperties, ClassCount, DatatypePropertyCount, ObjectPropertyCount }
   ```

## Error Codes

| Code | Condition |
|------|-----------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered in the session. |
| `ONTOLOGY_BUILD_NAMESPACE_MISSING` | `Namespace` is absent or lacks required fields. |

## Dependencies

- `XBase-Schema-TableList`
- `XBase-Schema-ColumnList`
- `Ontology-Namespace-Define`
