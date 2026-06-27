# Ticketing-Category-Create

Define a category for classifying tickets.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Name | string | yes | Category name, e.g. Bug, Feature, Question |
| Description | string | no | Optional explanation of when to use this category |

## Outputs

```json
{
  "Success": true,
  "CategoryId": 1,
  "Name": "Bug"
}
```

## Steps

1. Call XBase-Record-Select on Categories where Name = Name; if a row is found, return TICKETING_CATEGORY_NAME_DUPLICATE.
2. Call XBase-Record-Insert on Categories with Name and Description.
3. Return CategoryId and Name.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_CATEGORY_NAME_DUPLICATE | A category with that name already exists |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
