# Ticketing-Category-Create

Define a category for classifying tickets (e.g. Bug, Feature, Question).

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Name` | string | yes | — | Category name |
| `Description` | string | no | — | Optional explanation of when to use this category |

## Outputs

```json
{
  "Success": true,
  "CategoryId": 1,
  "Name": "Bug"
}
```

## Steps

1. `XBase-Record-Insert` → `Categories`
2. Return `CategoryId` and `Name`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_CATEGORY_EXISTS` | A category with that name already exists |

## Dependencies

- `XBase-Record-Insert`
