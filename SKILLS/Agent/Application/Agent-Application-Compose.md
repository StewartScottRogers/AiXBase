# Agent-Application-Compose

Compose a set of skills into a single **composable application** — a behavior manifest, an external state store, a determinism boundary, and a supervision role — and return an `ApplicationDescriptor` plus the enactment loop an agent follows to run it. The application is never compiled to native code: it exists only as this descriptor and is enacted live by an emulating agent. This skill performs no domain I/O of its own; it resolves references, binds state, and assembles the descriptor.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ApplicationName` | string | Yes | Logical name and identity root of the composed application. |
| `Skills` | array | Yes | Behavior manifest. Each entry `{ Name, Public }` names a skill the application enacts; `Public: true` exposes it as one of the application's callable operations. |
| `StateStore` | object | Yes | External store that carries state and identity across calls: `{ Kind: "XBase" \| "File" \| "Memory", ConnectionName?, DatabaseName?, Location?, IdentityKey }`. `IdentityKey` is the stable handle by which this application is addressed over time. |
| `DeterministicDelegations` | array | No | The determinism boundary. Each entry `{ Operation, DelegateTo }` names a leaf operation that MUST route to a deterministic skill (`DelegateTo`) rather than be emulated. Correctness-critical operations (aggregation, join, arithmetic over records, authentication) default to delegation when omitted. |
| `SupervisionRole` | string | No | `"Standalone"` (default), `"Supervisor"`, or `"SubAgent"` — the application's place in a team. |
| `SubAgents` | array | No | When `SupervisionRole` is `Supervisor`: names of composed applications this one may delegate to. |
| `RoutingMode` | string | No | `"Static"` (default) resolves sub-agents from a fixed capability table; `"Emulated"` re-decides routing per request. Ignored unless `SupervisionRole` is `Supervisor`. |

## Outputs

```json
{
  "Success": true,
  "Application": {
    "Name": "helpdesk",
    "IdentityKey": "app:helpdesk",
    "Behavior": {
      "Skills": ["Ticketing-Ticket-Create", "Ticketing-Ticket-Query", "Ticketing-Report-Summary"],
      "PublicOperations": ["Ticketing-Ticket-Create", "Ticketing-Ticket-Query"]
    },
    "State": { "Kind": "XBase", "ConnectionName": "helpdesk", "IdentityKey": "app:helpdesk" },
    "DelegationBoundary": [
      { "Operation": "query", "DelegateTo": "XBase-Query-Execute" },
      { "Operation": "aggregate", "DelegateTo": "XBase-Query-Aggregate" }
    ],
    "Supervision": { "Role": "SubAgent", "Supervisor": null, "SubAgents": [], "RoutingMode": "Static" },
    "Capability": { "Provides": ["Ticketing-Ticket-Create", "Ticketing-Ticket-Query"], "Discoverable": true },
    "Enactment": {
      "Model": "emulate",
      "Loop": "receive -> load-state -> for-each-operation(delegate-if-on-boundary else emulate) -> persist-state -> respond"
    }
  },
  "SkillName": "Agent-Application-Compose"
}
```

## Steps

1. If `ApplicationName` is empty or missing, return `AGENT_COMPOSE_NAME_MISSING`.
2. If `Skills` is empty, return `AGENT_COMPOSE_NO_SKILLS`. Otherwise, for each entry, confirm the named skill is present in the skill directory; if any cannot be resolved, return `AGENT_COMPOSE_SKILL_UNRESOLVED` naming the first unresolved skill. Record the subset marked `Public: true` as `PublicOperations` (default to all skills if none are marked public).
3. Validate `StateStore`: `Kind` must be one of `XBase`, `File`, `Memory`, and `IdentityKey` must be non-empty; otherwise return `AGENT_COMPOSE_STATE_STORE_INVALID`. This store — not the skills — is what gives the application continuity and identity, so it is mandatory even for `Memory` (session-scoped) kinds.
4. Bind the state store. If `Kind` is `XBase`, ensure a live connection by calling `XBase-Database-Connect` with the supplied `ConnectionName`/`DatabaseName`; if the binding fails, return `AGENT_COMPOSE_STATE_BIND_FAILED`. For `File`, verify `Location` is writable. For `Memory`, allocate a session-scoped keyspace under `IdentityKey`.
5. Construct the determinism boundary. For each `DeterministicDelegations` entry, confirm `DelegateTo` resolves to a present skill; if not, return `AGENT_COMPOSE_DELEGATION_UNRESOLVED`. Then add default delegations for any correctness-critical leaf operation not already covered — aggregation, join, record arithmetic, and authentication — mapping each to its deterministic skill so these paths are executed, never emulated.
6. Assign the supervision role. If `SupervisionRole` is not one of `Standalone`, `Supervisor`, `SubAgent`, return `AGENT_COMPOSE_SUPERVISION_ROLE_INVALID`. If `Supervisor`, resolve each name in `SubAgents` to a composed application descriptor; if any cannot be resolved, return `AGENT_COMPOSE_SUBAGENT_UNRESOLVED`. Validate `RoutingMode` is `Static` or `Emulated`; otherwise return `AGENT_COMPOSE_ROUTING_MODE_INVALID`. Under `Static`, record the sub-agent capability table now; under `Emulated`, record only that routing is re-decided per request.
7. Emit the capability manifest: the set of `PublicOperations` this application exposes, marked `Discoverable`, so a supervisor can find it by capability rather than by name.
8. Assemble the `ApplicationDescriptor` (Behavior, State, DelegationBoundary, Supervision, Capability) and attach the enactment loop: on each inbound request the emulating agent (a) loads state from the store by `IdentityKey`, (b) resolves the target operation and, for every leaf step, delegates to the bound deterministic skill if the step is on the determinism boundary else emulates it from the skill's behavior, (c) persists updated state back to the store, and (d) returns the response. No compilation occurs at any point; the descriptor is the application.
9. Return the success envelope with the assembled `Application`.

## Error Codes

| Code | Meaning |
|------|---------|
| `AGENT_COMPOSE_NAME_MISSING` | `ApplicationName` was empty or absent. |
| `AGENT_COMPOSE_NO_SKILLS` | The behavior manifest contained no skills. |
| `AGENT_COMPOSE_SKILL_UNRESOLVED` | A skill named in `Skills` is not present in the skill directory. |
| `AGENT_COMPOSE_STATE_STORE_INVALID` | `StateStore.Kind` is unrecognized or `IdentityKey` is missing. |
| `AGENT_COMPOSE_STATE_BIND_FAILED` | The state store could not be bound (e.g. XBase connect failed or location not writable). |
| `AGENT_COMPOSE_DELEGATION_UNRESOLVED` | A `DelegateTo` target in the determinism boundary does not resolve to a present skill. |
| `AGENT_COMPOSE_SUPERVISION_ROLE_INVALID` | `SupervisionRole` was not `Standalone`, `Supervisor`, or `SubAgent`. |
| `AGENT_COMPOSE_SUBAGENT_UNRESOLVED` | A name in `SubAgents` does not resolve to a composed application. |
| `AGENT_COMPOSE_ROUTING_MODE_INVALID` | `RoutingMode` was not `Static` or `Emulated`. |

## Dependencies

- `XBase-Database-Connect` (when `StateStore.Kind` is `XBase`, to bind the persistent state store)
- Skills named in `Skills` and in `DeterministicDelegations.DelegateTo` are resolved from the skill directory at compose time and enacted at runtime; they are not hard build dependencies of this skill.
