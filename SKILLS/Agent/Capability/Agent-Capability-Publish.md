# Agent-Capability-Publish

Emit the discovery manifest for a composed application — what it provides, what it consumes, and its supervision role — so a supervisor can find it by capability rather than by name. Optionally types the capabilities against the application's state-store schema using the Ontology bundle, and optionally writes the manifest to a shared capability registry. This is the seam that makes teams discoverable.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `Application` | object | Yes | An `ApplicationDescriptor` produced by `Agent-Application-Compose`. |
| `IncludeOntology` | boolean | No | When true, describe the provided capabilities in ontology terms by introspecting the application's state-store schema. Default false. |
| `Registry` | string | No | Publish target. A named registry writes the manifest to a `capabilities` table keyed by `IdentityKey`; the literal `"InSession"` (default) keeps it in the current session only. |

## Outputs

```json
{
  "Success": true,
  "Capability": {
    "Application": "helpdesk",
    "IdentityKey": "app:helpdesk",
    "Provides": ["Ticketing-Ticket-Create", "Ticketing-Ticket-Query"],
    "Consumes": ["XBase-Query-Execute", "XBase-Query-Aggregate"],
    "SupervisionRole": "SubAgent",
    "Ontology": null,
    "PublishedTo": "InSession"
  },
  "SkillName": "Agent-Capability-Publish"
}
```

## Steps

1. Verify `Application` is a well-formed `ApplicationDescriptor`; if not, return `AGENT_PUBLISH_DESCRIPTOR_INVALID`. Extract `Behavior.PublicOperations` as `Provides` and `IdentityKey` from `State`.
2. Derive `Consumes` from `DelegationBoundary` — the deterministic skills the application delegates to — so a supervisor can see its dependencies, not just its surface.
3. If `IncludeOntology` is true: ensure the state store is connected and call `Ontology-Build-Schema` on it to type the capabilities against the store's schema; attach the resulting classes and properties as `Ontology`. Apply confidence tiers to any inferred capability typing, consistent with the Ontology bundle's contract. If the store is not XBase-backed or the ontology build fails, return `AGENT_PUBLISH_ONTOLOGY_FAILED`. When `IncludeOntology` is false, set `Ontology` to null.
4. Assemble the capability manifest: `Application`, `IdentityKey`, `Provides`, `Consumes`, `SupervisionRole`, and `Ontology`.
5. Publish. If `Registry` names a target, write the manifest via `XBase-Record-Upsert` into that registry's `capabilities` table, keyed by `IdentityKey` so re-publishing replaces the prior entry; if the write fails, return `AGENT_PUBLISH_REGISTRY_WRITE_FAILED`. Otherwise record it in-session and set `PublishedTo` to `"InSession"`.
6. Return the success envelope with the `Capability` manifest.

## Error Codes

| Code | Meaning |
|------|---------|
| `AGENT_PUBLISH_DESCRIPTOR_INVALID` | `Application` is not a well-formed `ApplicationDescriptor`. |
| `AGENT_PUBLISH_ONTOLOGY_FAILED` | `IncludeOntology` was requested but the state store is not introspectable or the ontology build failed. |
| `AGENT_PUBLISH_REGISTRY_WRITE_FAILED` | The manifest could not be written to the named capability registry. |

## Dependencies

- `Agent-Application-Compose` (produces the descriptor being published)
- `Ontology-Build-Schema` (when `IncludeOntology` is true)
- `XBase-Database-Connect` and `XBase-Record-Upsert` (when publishing to a registry)
- Consumed by `Agent-Team-Route`, which reads published manifests to select a sub-agent.
