# Agent SKILLS

The Agent bundle is the composition layer of AiXBase. It turns a set of skills into a single **composable application** — a live unit that an AI enacts by emulation rather than compiling to native code. The same primitive is at once an application, an agent, and a component: a behavior manifest of skills, an external state store that carries its identity, a determinism boundary that keeps correctness-critical work exact, and a supervision role that lets units compose into teams.

Depends on the **XBase** bundle (for the default state store and the capability registry). Composes over *any* bundle — XBase, Ontology, TicketingSystem, or another Agent application.

---

## The Model

A composed application is three parts working together:

- **Behavior** — the skills it enacts. Skills are the "source": substrate-independent specifications the emulating agent follows directly.
- **State store** — an external, persistent store addressed by a stable `IdentityKey`. The model is stateless between calls, so this store — not the skills — is what gives the application continuity and identity over time. Without it you have a one-shot function; with it you have a standing entity.
- **Emulator** — the AI. On each request it loads state, enacts the required behavior, persists the new state, and responds. Nothing is compiled; the descriptor *is* the application.

Two design controls shape how far the emulation reaches:

- **Determinism boundary** — leaf operations that must not be hallucinated (aggregation, join, record arithmetic, authentication) are delegated to deterministic skills the way a program calls a syscall. The emulator still enacts all control flow and judgment; only the exact operations are handed off.
- **Supervision role** — every composed unit exposes a discoverable capability manifest and can take the role `Standalone`, `Supervisor`, or `SubAgent`. Because each unit is already a peer, a supervisor is just another unit delegating downward, so teams fall out for free. `RoutingMode` decides whether a supervisor resolves sub-agents from a fixed capability table (`Static`) or re-decides routing per request (`Emulated`) — i.e. whether the team has a fixed structure or only ever a current one.

---

## Skills

| Group | Skills | Purpose |
|-------|--------|---------|
| Application | 2 | Compose a descriptor, and enact a single request against it |
| Capability | 1 | Publish an application's discovery manifest |
| Team | 2 | Route a request to a sub-agent, and run a guided interactive supervisor session |

### Agent-Application-Compose

Assembles the four parts — behavior, state store, determinism boundary, supervision role — into an `ApplicationDescriptor` and attaches the enactment loop `receive → load-state → delegate-or-emulate → persist → respond`. Resolves every named skill and delegation target, binds the state store (calling `XBase-Database-Connect` for an XBase store), assigns the supervision role, and emits the capability manifest.

### Agent-Application-Enact

Runs the enactment loop **once**: loads state by `IdentityKey`, resolves the requested operation, delegates-or-emulates each leaf step, persists the new state, and returns the response. Delegated results from the determinism boundary are used verbatim and never re-emulated; a delegated failure is surfaced, not masked; an unpersisted mutation is never reported as done. This is how a composed application is actually run — live, with no compiled artifact.

### Agent-Capability-Publish

Emits an application's discovery manifest — its `Provides` (public operations), `Consumes` (deterministic skills it delegates to), and supervision role — so a supervisor can find it by capability rather than by name. Optionally types the capabilities against the state-store schema via `Ontology-Build-Schema` (with confidence tiers), and optionally writes the manifest to a shared capability registry keyed by `IdentityKey`. This is the seam between the Agent and Ontology bundles.

### Agent-Team-Route

Selects the sub-agent that should handle a request on behalf of a supervisor. Under `Static` routing the choice comes from a fixed capability table; under `Emulated` routing it is re-decided per request from each candidate's published manifest, with a `High`/`Medium`/`Low` confidence tier and a one-line rationale. Returns the selected sub-agent; the caller then hands the request to `Agent-Application-Enact`.

### Agent-Team-Session

Runs a guided interactive supervisor session over a team. It lists sub-agents and their published capabilities, routes a described request to the best-fit sub-agent, confirms, and enacts it, looping until the user exits. Like the other bundles' `*-Session` skills it performs no file I/O directly, delegating to `Agent-Team-Route`, `Agent-Application-Enact`, and `Agent-Capability-Publish`.

---

## The Runtime Loop

The four skills form a closed loop. Compose builds a descriptor; Publish advertises it; Route selects among advertised sub-agents; Enact runs a turn against the chosen one:

```
Agent-Application-Compose   →  ApplicationDescriptor (behavior + state + boundary + role)
Agent-Capability-Publish    →  capability manifest (Provides / Consumes / role)  →  registry
Agent-Team-Route            →  SelectedSubAgent  (static table or emulated per-request)
Agent-Application-Enact     →  Response          (load-state → delegate-or-emulate → persist)
```

---

## Quick Start

Compose two domain applications, publish their capabilities, compose a supervisor over them, then route and enact a request:

1. Ensure the state database exists and is connected (see the XBase Quick Start).

2. Call **Agent-Application-Compose**
   - ApplicationName: `"helpdesk"`
   - Skills: `[ { Name: "Ticketing-Ticket-Create", Public: true }, { Name: "Ticketing-Ticket-Query", Public: true } ]`
   - StateStore: `{ Kind: "XBase", ConnectionName: "helpdesk", DatabaseName: "ticketing", IdentityKey: "app:helpdesk" }`
   - DeterministicDelegations: `[ { Operation: "query", DelegateTo: "XBase-Query-Execute" }, { Operation: "aggregate", DelegateTo: "XBase-Query-Aggregate" } ]`
   - SupervisionRole: `"SubAgent"`

3. Call **Agent-Capability-Publish** for `helpdesk` (and each other sub-agent)
   - Application: `<descriptor from step 2>`
   - IncludeOntology: `true`
   - Registry: `"team"`

4. Call **Agent-Application-Compose** for the supervisor
   - ApplicationName: `"desk-supervisor"`
   - Skills: `[ ]`
   - StateStore: `{ Kind: "Memory", IdentityKey: "app:desk-supervisor" }`
   - SupervisionRole: `"Supervisor"`
   - SubAgents: `[ "helpdesk", "billing", "reports" ]`
   - RoutingMode: `"Emulated"`

5. Call **Agent-Team-Route**
   - Supervisor: `<descriptor from step 4>`
   - Request: `{ Intent: "open a new support ticket for a login failure", Arguments: { Summary: "Login fails on mobile Safari" } }`
   - Returns: `SelectedSubAgent: "helpdesk"`, `Confidence: "High"`.

6. Call **Agent-Application-Enact**
   - Application: `"app:helpdesk"`
   - Request: `{ Operation: "Ticketing-Ticket-Create", Arguments: { Summary: "Login fails on mobile Safari" } }`
   - Returns the created ticket and the persisted state reference. No compilation occurred at any step.

---

## File Format

Agent skills follow the same five-section contract as every AiXBase skill: Inputs table, JSON Outputs example, numbered Steps, Error Codes table, Dependencies list. Every skill returns a success envelope (`{ "Success": true, ... }`) or a failure envelope with an `ErrorCode` of the form `AGENT_CATEGORY_REASON`. Error codes never contain stack traces, internal paths, or credentials.
