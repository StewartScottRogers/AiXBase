# Ticketing-Priority-Define

Create a named priority level with an ordinal weight for ordering.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Name | string | yes | Priority name, e.g. Low, Medium, High, Critical |
| Weight | int | yes | Ordinal weight; lower value means higher urgency (e.g. Critical = 1, Low = 4) |
| IsDefault | bool | no | When true, marks this as the system default for new tickets; clears the flag from any existing default |

## Outputs

```json
{
  "Success": true,
  "PriorityId": 2,
  "Name": "High",
  "Weight": 2
}
```

## Steps

1. Call XBase-Record-Select on Priorities where Name = Name; if a row is found, return TICKETING_PRIORITY_NAME_DUPLICATE.
2. If IsDefault is true: call XBase-Record-Update on Priorities setting IsDefault = 0 for all rows where IsDefault = 1.
3. Call XBase-Record-Insert on Priorities with Name, Weight, IsDefault.
4. Return PriorityId, Name, and Weight.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_PRIORITY_NAME_DUPLICATE | A priority with that name already exists |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
- XBase-Record-Update
