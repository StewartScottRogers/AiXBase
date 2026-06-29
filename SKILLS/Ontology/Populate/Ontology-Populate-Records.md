# Ontology-Populate-Records

Load rows from one or more XBase tables into an OntologyDocument as `owl:NamedIndividual` instances, adding property assertions for each field value.

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `ConnectionName` | string | Yes | — | Open XBase connection alias. |
| `OntologyDocument` | object | Yes | — | Result of `Ontology-Build-Schema`. Classes and properties must already be present. |
| `Tables` | array | No | all tables | List of table name strings to populate. If omitted, every table in `OntologyDocument.Classes` is populated. |
| `Filter` | object | No | none | A filter spec (same structure as `XBase-Query-Filter` output) applied to every selected table. Useful for limiting population to active records or a date range. |
| `Limit` | integer | No | none | Maximum number of rows to load per table. |

## Outputs

```json
{
  "Success": true,
  "OntologyDocument": {
    "Namespace": {},
    "Classes": [],
    "DatatypeProperties": [],
    "ObjectProperties": [],
    "Individuals": [
      {
        "IRI": "http://xbase.local/mydb#Users_1",
        "Type": "http://xbase.local/mydb#Users",
        "PropertyAssertions": [
          {
            "Property": "http://xbase.local/mydb#Users_Username",
            "Value": "srogers",
            "IsObjectProperty": false
          },
          {
            "Property": "http://xbase.local/mydb#Users_Email",
            "Value": "admin@example.com",
            "IsObjectProperty": false
          }
        ]
      }
    ],
    "ClassCount": 5,
    "DatatypePropertyCount": 20,
    "ObjectPropertyCount": 3,
    "IndividualCount": 1
  },
  "TablesPopulated": ["Users"],
  "IndividualsAdded": 1
}
```

## Steps

1. Validate `ConnectionName`; if not registered return `XBASE_CONNECTION_INVALID`.
2. Validate `OntologyDocument` has `Classes`, `DatatypeProperties`, and `ObjectProperties`; if missing return `ONTOLOGY_POPULATE_DOCUMENT_INVALID`.
3. Resolve `Tables`:
   - If `Tables` is supplied, validate each name exists in `OntologyDocument.Classes`; if any is absent return `ONTOLOGY_POPULATE_TABLE_NOT_IN_SCHEMA` with the unknown name.
   - If `Tables` is omitted, collect all `Label` values from `OntologyDocument.Classes`.
4. Initialize `Individuals = []` (or extend the existing array if `OntologyDocument.Individuals` is already present).
5. For each table name in the resolved list:
   a. Call `XBase-Record-Select` with `ConnectionName`, `TableName`, and any supplied `Filter` and `Limit`. If it fails, propagate the error unchanged.
   b. For each row returned:
      - Compute `IndividualIRI = BaseIRI + TableName + "_" + row.Id`.
      - Compute `TypeIRI = BaseIRI + TableName`.
      - Build `PropertyAssertions`:
        - For each field in the row where the field name is not `Id` and the value is not null:
          - Look up the field in `OntologyDocument.ObjectProperties` where `Label = FieldName` and `Domain = TypeIRI`.
          - If found (it is an object property / FK): emit `{ Property: property.IRI, Value: BaseIRI + ReferencedTable + "_" + fieldValue, IsObjectProperty: true }`.
          - Otherwise look it up in `OntologyDocument.DatatypeProperties`: emit `{ Property: property.IRI, Value: fieldValue (as string), IsObjectProperty: false }`.
          - If no matching property is found in either list, skip the field silently.
      - Append `{ IRI: IndividualIRI, Type: TypeIRI, PropertyAssertions }` to `Individuals`.
6. Set `OntologyDocument.Individuals = Individuals`.
7. Update `OntologyDocument.IndividualCount = Individuals.Count`.
8. Return updated `OntologyDocument`, `TablesPopulated`, and `IndividualsAdded`.

## Error Codes

| Code | Condition |
|------|-----------|
| `XBASE_CONNECTION_INVALID` | `ConnectionName` is not registered. |
| `ONTOLOGY_POPULATE_DOCUMENT_INVALID` | `OntologyDocument` is null or missing required arrays. |
| `ONTOLOGY_POPULATE_TABLE_NOT_IN_SCHEMA` | A name in `Tables` has no matching class in `OntologyDocument.Classes`. |

## Dependencies

- `XBase-Record-Select`
- `Ontology-Build-Schema`
