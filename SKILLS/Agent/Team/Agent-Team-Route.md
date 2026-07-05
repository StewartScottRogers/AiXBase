# Agent-Team-Route

Select the sub-agent that should handle a request, on behalf of a supervisor application. Under static routing the choice is resolved from a fixed capability table; under emulated routing the choice is re-decided per request by reading each candidate's published capability manifest — so the team has a current structure rather than a permanent one. Returns the selected sub-agent; the caller then enacts the request against it with `Agent-Application-Enact`.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Supervisor` | object | Yes | A composed application whose `Supervision.Role` is `Supervisor`, carrying its `SubAgents` list and `RoutingMode`. |
| `Request` | object | Yes | The request to route: `{ Operation, Intent, Arguments }`. `Operation` drives static routing; `Intent` (a short description of what is needed) drives emulated routing. At least one of the two must be present. |
| `CapabilityIndex` | array | No | Published capability manifests (from `Agent-Capability-Publish`) for the candidate sub-agents. When omitted, the supervisor's recorded `SubAgents` table is used. |

## Outputs

```json
{
  "Success": true,
  "Supervisor": "desk-supervisor",
  "RoutingMode": "Emulated",
  "SelectedSubAgent": "helpdesk",
  "MatchedCapability": "Ticketing-Ticket-Create",
  "Confidence": "High",
  "Rationale": "Only helpdesk provides ticket-creation capabilities matching the request intent.",
  "SkillName": "Agent-Team-Route"
}
```

## Steps

1. Verify `Supervisor.Supervision.Role` is `Supervisor`; if not, return `AGENT_ROUTE_NOT_SUPERVISOR`.
2. Assemble the candidate set from `CapabilityIndex` if supplied, otherwise from `Supervisor.Supervision.SubAgents`. If the set is empty, return `AGENT_ROUTE_NO_CANDIDATES`. If a candidate names a sub-agent for which no capability manifest is available under either source, return `AGENT_ROUTE_CAPABILITY_MISSING`.
3. Read `Supervisor.Supervision.RoutingMode`; it must be `Static` or `Emulated`, else return `AGENT_ROUTE_MODE_INVALID`.
4. **Static routing.** Match `Request.Operation` against each candidate's `Provides` list. Select the sub-agent that exposes it. If none do, return `AGENT_ROUTE_NO_MATCH`. If more than one does, select the first and set `Confidence` to `Medium` to signal the ambiguity. Set `MatchedCapability` to the matched operation.
5. **Emulated routing.** Re-decide per request: read each candidate's published capability manifest (and, if present, its ontology typing) together with `Request.Intent`, choose the best-fit sub-agent, and assign a `Confidence` tier of `High`, `Medium`, or `Low` with a one-line `Rationale`. No fixed table is consulted; the decision is made fresh each call. If no candidate is a plausible fit, return `AGENT_ROUTE_NO_MATCH`.
6. Return the success envelope naming `SelectedSubAgent`, `MatchedCapability`, and — for emulated routing — `Confidence` and `Rationale`. The caller passes the request to `Agent-Application-Enact` on the selected sub-agent.

## Error Codes

| Code | Meaning |
|------|---------|
| `AGENT_ROUTE_NOT_SUPERVISOR` | `Supervisor` does not carry the `Supervisor` role. |
| `AGENT_ROUTE_NO_CANDIDATES` | No sub-agents are available to route to. |
| `AGENT_ROUTE_CAPABILITY_MISSING` | A candidate sub-agent has no published capability manifest to route against. |
| `AGENT_ROUTE_MODE_INVALID` | `RoutingMode` was neither `Static` nor `Emulated`. |
| `AGENT_ROUTE_NO_MATCH` | No candidate sub-agent matched the request. |

## Dependencies

- `Agent-Capability-Publish` (source of the capability manifests routed against)
- `Agent-Application-Compose` (produces the supervisor and its sub-agents)
- `Agent-Application-Enact` (invoked by the caller on the selected sub-agent after routing)
