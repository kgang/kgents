# N-Phase ⇄ Agent Town Runtime Hooks

This note records how to use the N-Phase compiler inside the REPL, via CLI, and how Agent Town exposes compressed phase (SENSE/ACT/REFLECT) state to SaaS dashboards.

## REPL shortcuts (agentese)
- `/nphase <definition.yaml>` → compile (defaults to `compile` when first arg is a path)
- `/nphase-validate <definition.yaml>` → validate only
- `/nphase-template <PHASE>` → print a phase template (e.g., PLAN, ACT)
- `/nphase-bootstrap <plan.md>` → bootstrap from a plan header then compile

## CLI usage
```bash
kgents nphase compile projects/my-feature.yaml -o prompts/my-feature.md
kgents nphase validate projects/my-feature.yaml
kgents nphase template ACT
kgents nphase bootstrap plans/crown-jewel-next.md -o prompts/crown-jewel-next.md
```

## Town runtime hook (SaaS)
- Citizens now carry `NPhaseState` (compressed SENSE/ACT/REFLECT). Advancing with `citizen.advance_nphase(...)` records ledger entries and cycle counts.
- Town flux can emit transitions: `TownFlux.emit_nphase_transition(town_id, citizen, target, nats=bridge, sse=endpoint, payload=meta)`.
- NATS subject: `town.{town_id}.nphase.transition` (payload includes `citizen_id`, `from`, `to`, `cycle`, `payload`, `timestamp`).
- SSE event: `town.nphase.transition` with the same ledger payload for dashboards.

## Worked example
1) Define project YAML:
```yaml
name: "Town Feature Rollout"
classification: "standard"
n_phases: 3
scope:
  goal: "Pilot a new greeting ritual across 3 regions"
  non_goals: ["economy changes"]
  parallel_tracks:
    A: "Citizen training"
    B: "Ritual instrumentation"
decisions:
  - id: D1
    choice: "Use compressed 3-phase cycle"
    rationale: "Fast feedback for pilot"
waves:
  - id: W1
    name: "Pilot"
    components: ["Ritual prompt", "Metrics hook"]
```
2) Compile from REPL: `/nphase projects/town-feature.yaml -o prompts/town-feature.md`
3) From a Town loop, advance a citizen and emit:
```python
await town_flux.emit_nphase_transition("demo-town", citizen, "ACT", nats=bridge, sse=sse)
```
Dashboards subscribed to NATS/SSE receive the ledger and can render a phase badge per citizen.
