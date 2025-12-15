⟿[STRATEGIZE]
/hydrate prompts/agent-town-phase5-strategize.md
  handles:
    contracts: visualization.py (ScatterWidget, SSEEndpoint, NATSBridge)
    tests: test_visualization_contracts.py (27 passing)
    schemas: ScatterPoint, ScatterState, SSEEvent, TownNATSSubject, TownEventType
    laws: scatter.map(f) ≡ scatter.with_state(f(state)); identity; composition
    deps_optional: [anywidget, sse-starlette, plotly, nats-py]
    ledger: {RESEARCH: touched, DEVELOP: touched}
    entropy: 0.18
  mission: Sequence implementation chunks by leverage; identify parallel tracks; set checkpoints
  actions:
    - Prioritize: SSE (no deps) vs Widget (anywidget opt) vs NATS (nats-py opt)
    - Parallel tracks: CLI projection can run alongside SSE endpoint
    - Checkpoints: tests green at each chunk; mypy passes; graceful degradation verified
    - Risk probe: NATS requires external service—fallback queue tested first
  exit: Ordered backlog with owners + deps; parallel interfaces; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE

---

# STRATEGIZE: Agent Town Phase 5 Visualization/Streaming

This is the **STRATEGIZE phase** for Agent Town Phase 5 (Visualization + Streaming).

## ATTACH

/hydrate

You are entering STRATEGIZE of the N-Phase Cycle (AD-005).

## Context from DEVELOP

Contracts defined in `agents/town/visualization.py`:

| Contract | Purpose | Optional Deps |
|----------|---------|---------------|
| `EigenvectorScatterWidget` | 7D scatter plot with project() | anywidget, plotly |
| `TownSSEEndpoint` | Async SSE generator | sse-starlette (optional) |
| `TownNATSBridge` | NATS subject schema | nats-py |

**Tests**: 27 passing in `test_visualization_contracts.py`
**Mypy**: Clean
**Laws**: Functor laws expressed and tested

## Your Mission

Translate the contracts into an **ordered implementation backlog** that maximizes leverage and minimizes risk. Follow `docs/skills/n-phase-cycle/strategize.md`.

Key questions:
1. **Leverage**: What delivers most value soonest?
2. **Risk**: What requires external deps that might not be available?
3. **Parallelism**: What can run independently?
4. **Graceful degradation**: What fallbacks exist when deps unavailable?

## Implementation Chunks to Sequence

| Chunk | Description | Deps | Risk |
|-------|-------------|------|------|
| A | `project_scatter_to_ascii()` CLI impl | None | Low |
| B | `EigenvectorScatterWidget` full impl | Signal | Low |
| C | `MarimoAdapter` scatter integration | anywidget | Med |
| D | `TownSSEEndpoint` impl (asyncio.Queue) | None | Low |
| E | SSE FastAPI route integration | FastAPI | Low |
| F | `TownNATSBridge` impl | nats-py | High |
| G | SSE over NATS fallback path | F complete | Med |
| H | Scatter widget marimo demo | C complete | Low |
| I | NATS integration tests | NATS server | High |

## Principles Alignment

From `spec/principles.md`:
- **Graceful Degradation**: Features work without optional deps
- **Composable**: Chunks are morphisms that compose
- **Tasteful**: Ship value incrementally, not all-or-nothing
- **Heterarchical**: Different tracks can have different owners

## Exit Criteria

1. **Ordered backlog** with dependency graph
2. **Parallel tracks** identified with interfaces
3. **Checkpoints** defined (what passes at each gate)
4. **Risk mitigation** for high-risk chunks (F, I)
5. **Owner/agent assignment** per chunk
6. **Ledger updated**: `STRATEGIZE: touched`

## Deliverables

Write to:
- `plans/agent-town/phase5-strategize.md` — Ordered backlog + parallel tracks
- Update `HYDRATE.md` with agent-town progress if needed

## Accursed Share (Entropy Budget)

Reserve 5% for exploration:
- Try reverse order: what if NATS first?
- Risk probe: what's the scariest chunk? (NATS integration)
- Parallel discovery: A and D are secretly independent
- Abort criteria: If anywidget unavailable, fallback to JSON-only

Draw: `void.entropy.sip(amount=0.05)`

## Continuation Imperative

Upon completing this phase, emit:

```
⟿[CROSS-SYNERGIZE]
/hydrate prompts/agent-town-phase5-cross-synergize.md
  handles:
    backlog: ${ordered_chunks}
    parallel: ${parallel_tracks}
    checkpoints: ${checkpoints}
    gates: ${decision_gates}
    interfaces: ${track_interfaces}
    ledger: {STRATEGIZE: touched}
    branches: ${branch_notes}
  mission: Hunt compositions; probe synergies with existing AGENTESE REPL, K-gent, marimo substrate
  actions: Enumerate morphisms; test identity/associativity; identify law-abiding pipelines
  exit: Chosen compositions + rationale; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT
```

Or halt with:
```
⟂[BLOCKED:dependency_unavailable] Cannot proceed without ${dep}
⟂[BLOCKED:no_safe_order] Circular dependencies detected
```

---

*This is the **STRATEGIZE phase** for Agent Town Phase 5 Visualization/Streaming. The form is the function.*
