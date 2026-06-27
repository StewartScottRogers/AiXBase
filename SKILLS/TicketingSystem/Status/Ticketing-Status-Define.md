# Ticketing-Status-Define

Create a named workflow status.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| Name | string | yes | Status name, e.g. Open, In Progress, Closed |
| IsTerminal | bool | no | When true, tickets in this status are considered closed; defaults to false |

## Outputs

```json
{
  "Success": true,
  "StatusId": 3,
  "Name": "Closed"
}
```

## Steps

1. Call XBase-Record-Select on Statuses where Name = Name; if a row is found, return TICKETING_STATUS_NAME_DUPLICATE.
2. Call XBase-Record-Insert on Statuses with Name, IsTerminal (0 if not supplied).
3. Return StatusId and Name.

## Error Codes

| Code | Meaning |
|------|---------|
| TICKETING_STATUS_NAME_DUPLICATE | A status with that name already exists |

## Dependencies

- XBase-Record-Select
- XBase-Record-Insert
