# XBase-Admin-Execute

Execute any named XBase skill dynamically by passing its name and inputs as structured data.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| SkillName | string | yes | The exact name of the XBase skill to invoke (e.g. `XBase-Record-Insert`) |
| Inputs | object | yes | Key-value pairs to pass as inputs to the named skill |
| ConnectionName | string | no | A pre-validated connection alias to inject into the invoked skill's inputs if the skill accepts one |

## Outputs

```json
{
  "Success": true,
  "SkillName": "XBase-Record-Insert",
  "Result": { "InsertedCount": 1, "LastInsertedId": 42 },
  "ExecutedAt": "2026-06-27T14:00:00Z"
}
```

## Steps

1. Validate that `SkillName` is a recognized XBase or Ticketing skill name by checking it against the known skill catalog. If the name is not found, return `XBASE_ADMIN_SKILL_NOT_FOUND`.
2. If `ConnectionName` is supplied, verify that it is registered in the current session. If the named skill does not accept a `ConnectionName` input, emit a warning in the output but continue.
3. Merge `ConnectionName` (if supplied) into the `Inputs` object, then invoke the named skill with the merged inputs.
4. Capture the output returned by the invoked skill. Return it under `Result` along with `SkillName` and `ExecutedAt` set to the current ISO-8601 timestamp.

## Error Codes

| Code | Meaning |
|------|---------|
| `XBASE_ADMIN_SKILL_NOT_FOUND` | `SkillName` does not match any known skill in the catalog |
| `XBASE_CONNECTION_INVALID` | `ConnectionName` was supplied but is not registered in the current session |

## Dependencies

- All XBase skills (any skill may be invoked depending on the value of `SkillName`)
