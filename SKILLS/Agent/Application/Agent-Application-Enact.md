# Agent-Application-Enact

Run a single request against a composed `ApplicationDescriptor` by executing its enactment loop once: load state, resolve the requested operation, delegate-or-emulate each leaf step, persist the new state, and return the response. This is how a composed application is *run* — live, by emulation, with no compiled artifact. Correctness-critical steps on the descriptor's determinism boundary are executed by their bound deterministic skills and never re-emulated.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Application` | object | Yes | An `ApplicationDescriptor` produced by `Agent-Application-Compose` (or the `IdentityKey` of one already registered in the session). |
| `Request` | object | Yes | The inbound request: `{ Operation, Arguments }`. `Operation` must be one of the application's `PublicOperations`. |
| `StateOverride` | object | No | An explicit state snapshot to enact against instead of loading from the store. Used for replay and testing; when supplied, the loaded store state is ignored for this call. |

## Outputs

```json
{
  "Success": true,
  "Application": "helpdesk",
  "Operation": "Ticketing-Ticket-Create",
  "Response": { "TicketId": 42, "TicketNumber": "TKT-0042" },
  "State": { "IdentityKey": "app:helpdesk", "Persisted": true, "Version": 7 },
  "Enactment": { "Path": "emulated", "DelegatedTo": null },
  "SkillName": "Agent-Application-Enact"
}
```

## Steps

1. Resolve `Application`. If a descriptor object, verify it carries `Behavior`, `State`, `DelegationBoundary`, and `Supervision`; if a string, look up the registered descriptor by `IdentityKey`. If neither resolves to a well-formed descriptor, return `AGENT_ENACT_DESCRIPTOR_INVALID`.
2. Validate `Request.Operation` is present and appears in `Application.Behavior.PublicOperations`; if it is absent or not exposed, return `AGENT_ENACT_OPERATION_NOT_EXPOSED`.
3. Load state. If `StateOverride` is supplied, use it. Otherwise read the state addressed by `Application.State.IdentityKey` from the bound store — for an XBase store this reads through the connection established at compose time. If the store cannot be read, return `AGENT_ENACT_STATE_LOAD_FAILED`. A `Memory` store with no prior state begins empty.
4. Resolve `Operation` to its skill; if it cannot be resolved to a present skill, return `AGENT_ENACT_OPERATION_UNRESOLVED`. Enact the operation: for each leaf step, if the step matches an entry on `Application.DelegationBoundary`, invoke the bound deterministic skill with the step's arguments and use its result verbatim — never re-emulate a delegated result; otherwise emulate the step from the skill's behavior. Record whether the top-level path was `delegated` or `emulated` and, if delegated, which skill was called.
5. If any delegated skill returns a failure envelope, do not mask it: return `AGENT_ENACT_DELEGATE_FAILED` and carry the underlying error code in the message.
6. If the operation mutates state, compute the new state and write it back to the store under `IdentityKey`, incrementing `Version`. If the write fails, return `AGENT_ENACT_STATE_PERSIST_FAILED` and do not report success — an unpersisted mutation must not be reported as done.
7. Return the success envelope with `Response`, the persisted `State` reference, and the `Enactment` path.

## Error Codes

| Code | Meaning |
|------|---------|
| `AGENT_ENACT_DESCRIPTOR_INVALID` | `Application` did not resolve to a well-formed `ApplicationDescriptor`. |
| `AGENT_ENACT_OPERATION_NOT_EXPOSED` | `Request.Operation` is missing or is not one of the application's `PublicOperations`. |
| `AGENT_ENACT_OPERATION_UNRESOLVED` | The operation's skill is not present in the skill directory. |
| `AGENT_ENACT_STATE_LOAD_FAILED` | State could not be read from the bound store. |
| `AGENT_ENACT_DELEGATE_FAILED` | A deterministic skill on the determinism boundary returned a failure envelope. |
| `AGENT_ENACT_STATE_PERSIST_FAILED` | The mutated state could not be written back to the store. |

## Dependencies

- `Agent-Application-Compose` (produces the `ApplicationDescriptor` this skill consumes)
- `XBase-Database-Connect` and the XBase record/query skills (when the state store or a boundary delegation is XBase-backed)
- The skills named in the descriptor's `Behavior` and `DelegationBoundary` are resolved and invoked at enactment time.
