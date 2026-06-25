# Ticketing-Status-Define

Create a named workflow status and optionally configure allowed transitions.

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `Name` | string | yes | — | Status name, e.g. `Open`, `In Progress`, `Closed` |
| `IsTerminal` | bool | no | `false` | If `true`, tickets in this status are considered closed |
| `AllowedFromStatusIds` | array | no | `[]` | IDs of statuses that may transition **to** this one; empty means unrestricted |

## Outputs

```json
{
  "Success": true,
  "StatusId": 3,
  "Name": "Closed"
}
```

## Steps

1. `XBase-Record-Insert` → `Statuses`
2. For each `FromStatusId` in `AllowedFromStatusIds`:
   - `XBase-Record-Insert` → `StatusTransitions` (`FromStatusId`, `ToStatusId: new StatusId`)
3. Return `StatusId` and `Name`

## Error Codes

| Code | Condition |
|---|---|
| `TICKETING_STATUS_EXISTS` | A status with that name already exists |

## Dependencies

- `XBase-Record-Insert`
