# connect-dogfood

Bootstrap a session against the AiXBase dogfood ticketing database. Runs Runtime-Detect, Database-Connect, and User-Authenticate in sequence so all Ticketing skills are ready to use in one step.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Password` | string | yes | Plaintext password for the `srogers` admin account; never stored or logged |

## Outputs

```json
{
  "Success": true,
  "ConnectionName": "ticketing",
  "UserId": 1,
  "SessionToken": "...",
  "ExpiresAt": "2026-06-29T19:00:00Z",
  "DatabaseRoot": "Z:\\repos\\AiXBase\\AiXBaseTracking",
  "DatabasePath": "Z:\\repos\\AiXBase\\AiXBaseTracking\\tracking"
}
```

## Steps

1. Call `XBase-Runtime-Detect` with `DatabaseRoot = "Z:\repos\AiXBase\AiXBaseTracking"`. If `EnvironmentReady` is false, return `CONNECT_DOGFOOD_ENV_NOT_READY` with the `Issues` array from the result.
2. Call `XBase-Database-Connect` with `DatabaseName = "tracking"` and `ConnectionName = "ticketing"`. On any error, propagate the XBase error code unchanged.
3. Call `Ticketing-User-Authenticate` with `Username = "srogers"` and `Password` from inputs. On `TICKETING_AUTH_FAILED`, return that error — do not reveal whether the failure was a wrong password or an inactive account.
4. Return `ConnectionName = "ticketing"`, `UserId`, `SessionToken`, `ExpiresAt`, `DatabaseRoot`, and `DatabasePath`.

## Error Codes

| Code | Meaning |
|------|---------|
| `CONNECT_DOGFOOD_ENV_NOT_READY` | `XBase-Runtime-Detect` reported one or more environment capability gaps |

## Dependencies

- `XBase-Runtime-Detect`
- `XBase-Database-Connect`
- `Ticketing-User-Authenticate`
