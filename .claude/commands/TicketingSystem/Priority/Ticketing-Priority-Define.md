# Ticketing-Priority-Define

Create a named priority level with an ordinal weight for ordering.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Name` | string | yes | — | Priority name, e.g. `Low`, `Medium`, `High`, `Critical` |
| `Weight` | int | yes | — | Ordinal weight; **lower value = higher urgency** (e.g. `Critical = 1`, `Low = 4`) |
| `IsDefault` | bool | no | `false` | Mark as the system default for new tickets; clears the flag from any existing default |

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

1. If `IsDefault` is `true`: `XBase-Record-Update` → `Priorities` set `IsDefault = 0` for all rows
2. `XBase-Record-Insert` → `Priorities`
3. Return `PriorityId`, `Name`, `Weight`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_PRIORITY_EXISTS` | A priority with that name already exists |
| `TICKETING_PRIORITY_WEIGHT_IN_USE` | Another priority already has the same `Weight` |

## Dependencies

- `XBase-Record-Insert`
- `XBase-Record-Update`
