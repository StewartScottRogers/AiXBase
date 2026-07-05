# Agent-Team-Session

Run an interactive guided supervisor session over a team of composed applications. Presents a text menu in the conversation, accepts a selection, routes and enacts requests across sub-agents, and loops until the user exits. No file I/O occurs in this skill directly — every operation delegates to `Agent-Team-Route`, `Agent-Application-Enact`, and `Agent-Capability-Publish`, which in turn delegate to the underlying domain and XBase skills.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Supervisor` | object | Yes | A composed application whose `Supervision.Role` is `Supervisor` (or the `IdentityKey` of one registered in the session). |
| `Registry` | string | No | Capability registry to read sub-agent manifests from. Defaults to `"InSession"`. |
| `DisplayName` | string | No | Human-readable name shown in the header; falls back to the supervisor's `ApplicationName`. |

## Outputs

The skill produces no structured JSON output. All interaction is conversational: menus are rendered as markdown, results are displayed inline, and the session ends when the user selects Exit or types `q` / `quit` / `exit`.

## Steps

1. Resolve `Supervisor`; if it does not resolve to a descriptor, return `AGENT_SESSION_SUPERVISOR_UNRESOLVED`. If its `Supervision.Role` is not `Supervisor`, return `AGENT_SESSION_NOT_SUPERVISOR`.
2. Set `HeaderName` to `DisplayName` if supplied, otherwise the supervisor's `ApplicationName`. Read `RoutingMode` from the supervisor.
3. Display the main menu:

   ```
   ═══════════════════════════════════════════════
    Team  ·  <HeaderName>  ·  routing: <RoutingMode>
   ═══════════════════════════════════════════════
    1  Team       — list sub-agents and capabilities
    2  Ask        — route a request and enact it
    3  Publish    — (re)publish a sub-agent's capabilities
    4  Routing    — inspect or switch Static / Emulated
    5  Exit
   ═══════════════════════════════════════════════
   Select [1-5]:
   ```

4. Wait for user input. Normalize: strip whitespace, map `q`/`quit`/`exit` to `5`.
5. Dispatch on the selection:

   **Selection 1 — Team:**
   a. For each sub-agent in `Supervision.SubAgents`, read its capability manifest from `Registry` (or in-session). If a sub-agent has no published manifest, mark it `(unpublished)`.
   b. Render a markdown table with columns: `Sub-Agent | Role | Provides | Consumes`.
   c. Return to the main menu (step 3).

   **Selection 2 — Ask:**
   a. Prompt: `What do you need? (describe the request):` — capture as `Intent`.
   b. Optionally prompt: `Specific operation? (Enter to let the supervisor decide):` — capture as `Operation` if provided.
   c. Call `Agent-Team-Route` with `Supervisor`, and `Request: { Operation, Intent }`. If it returns `AGENT_ROUTE_NO_MATCH`, display `No sub-agent matched that request.` and return to the main menu.
   d. Display the routing result: `Routed to <SelectedSubAgent>` and, for emulated routing, `Confidence: <Confidence> — <Rationale>`.
   e. Prompt: `Enact on <SelectedSubAgent>? [Y/n]:` — default Yes.
   f. If yes, prompt for any required `Arguments`, then call `Agent-Application-Enact` with `Application: <SelectedSubAgent IdentityKey>` and `Request: { Operation: <MatchedCapability>, Arguments }`. Display the `Response` and the persisted state `Version`. If it returns `AGENT_ENACT_DELEGATE_FAILED`, display the underlying error code plainly and do not present the action as completed.
   g. Return to the main menu (step 3).

   **Selection 3 — Publish:**
   a. Display the sub-agents and prompt: `Publish which sub-agent?:`
   b. Prompt: `Include ontology typing? [y/N]:` — default No.
   c. Call `Agent-Capability-Publish` with that sub-agent's descriptor, `IncludeOntology` per the answer, and `Registry`. Display `Published <Application>: <Provides count> operations.` If it returns `AGENT_PUBLISH_ONTOLOGY_FAILED`, display the message and offer to retry without ontology typing.
   d. Return to the main menu (step 3).

   **Selection 4 — Routing:**
   a. Display the current `RoutingMode` and a one-line reminder: `Static resolves a fixed capability table; Emulated re-decides per request.`
   b. Prompt: `Switch to [static/emulated] or Enter to keep:` — if a valid value is entered, update the supervisor's `RoutingMode` for the remainder of the session; otherwise leave unchanged. This session-scoped change does not rewrite the stored descriptor unless the supervisor is later re-composed.
   c. Return to the main menu (step 3).

   **Selection 5 — Exit:**
   a. Display `Session ended.` and return.

   **Unrecognized input:**
   a. Display `Unrecognized selection. Please enter 1–5.` and re-display the main menu (step 3).

## Error Codes

| Code | Meaning |
|------|---------|
| `AGENT_SESSION_SUPERVISOR_UNRESOLVED` | `Supervisor` did not resolve to a composed application descriptor. |
| `AGENT_SESSION_NOT_SUPERVISOR` | The resolved application does not carry the `Supervisor` role. |

## Dependencies

- `Agent-Team-Route`
- `Agent-Application-Enact`
- `Agent-Capability-Publish`
- `Agent-Application-Compose` (source of the supervisor and sub-agent descriptors)
