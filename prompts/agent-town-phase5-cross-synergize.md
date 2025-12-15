⟿[CROSS-SYNERGIZE]
/hydrate prompts/agent-town-phase5-cross-synergize.md
  handles:
    backlog: [A:CLI-ASCII, B:Widget-Signal, C:Marimo, D:SSE-Queue, E:FastAPI, F:NATS, G:SSE-over-NATS, H:Demo, I:Integration]
    parallel: {track1: [A,D,E], track2: [B,C,H], track3: [F,G,I]}
    checkpoints: tests-green, mypy-clean, graceful-degradation
    gates: [anywidget-available, nats-server-up]
    interfaces: [ScatterWidget, SSEEndpoint, NATSBridge]
    ledger: {STRATEGIZE: touched}
    entropy: 0.10
  mission: Hunt compositions; probe synergies with AGENTESE REPL, K-gent, marimo substrate; find 2x-10x multipliers
  actions: Enumerate morphisms; test identity/associativity; identify law-abiding pipelines; scan dormant plans
  exit: Chosen compositions + rationale; rejected paths documented; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT

---

# CROSS-SYNERGIZE: Agent Town Phase 5 Visualization/Streaming

This is the **CROSS-SYNERGIZE phase** for Agent Town Phase 5 (Visualization + Streaming).

## ATTACH

/hydrate

You are entering CROSS-SYNERGIZE of the N-Phase Cycle (AD-005).

## Context from STRATEGIZE

Ordered backlog from STRATEGIZE:

| Track | Chunks | Dependencies | Risk |
|-------|--------|--------------|------|
| **Track 1** (Core) | A:CLI-ASCII → D:SSE-Queue → E:FastAPI | None | Low |
| **Track 2** (Widget) | B:Widget-Signal → C:Marimo → H:Demo | anywidget | Med |
| **Track 3** (NATS) | F:NATS-Bridge → G:SSE-over-NATS → I:Integration | nats-py, NATS server | High |

**Parallel interfaces**: Tracks run independently until convergence at integration tests.

## Your Mission

Discover compositions and entanglements that unlock nonlinear value. Follow `docs/skills/n-phase-cycle/cross-synergize.md`.

Key questions:
1. **AGENTESE REPL synergy**: Can scatter widgets compose with existing REPL primitives?
2. **K-gent integration**: Does eigenvector projection reveal K-gent soul state?
3. **Marimo substrate**: Can we lift SSE streams to marimo reactive cells?
4. **Dormant plans**: What forgotten plans in `_forest.md` might compose?
5. **Functor registry**: What existing functors lift this work?

## Compositions to Probe

### Candidate Morphisms

| Composition | Components | Potential Lift | Law Check Needed |
|-------------|------------|----------------|------------------|
| `REPL.scatter >> Town.eigenvector` | REPL primitives + ScatterWidget | Visualize agent population in REPL | Functor laws |
| `K-gent.soul >> scatter.project(7D→2D)` | SoulPolynomial + ScatterWidget | Soul state as scatter point | Identity |
| `Town.citizen_stream >> SSE.generator` | CitizenPolynomial + TownSSEEndpoint | Live citizen updates | Composition |
| `marimo.cell >> SSE.consumer` | Marimo reactive + SSE | Reactive town dashboard | Associativity |
| `NATS.subject >> SSE.fallback` | TownNATSBridge + SSE | Graceful NATS degradation | Identity |
| `Forest.witness >> Town.trace` | N-gent trace + TownNATSBridge | Audit trail in NATS | Composition |

### Dormant Plan Scan

Review these for composition opportunities:
- `plans/devex/agentese-repl-*.md` — REPL waves might want town viz
- `plans/agent-town/` — Parent plans with unfinished threads
- `plans/meta.md` — Learnings that suggest compositions
- `_forest.md` — Canopy view for cross-pollination

### Functor Registry Check

Probe existing functors in `impl/claude/protocols/agentese/`:
- `FunctorRegistry` — What's registered?
- `PolyAgent` lifts — Can Town citizens lift to scatter?
- `FluxAgent` streams — Does SSE compose with Flux?

## Principles Alignment

From `spec/principles.md`:
- **Composable**: Agents are morphisms; composition is primary (AD-002)
- **Generative**: Define grammars, not lists (AD-003)
- **Heterarchical**: Multiple valid composition paths exist

## Verification Checklist

Before exiting:
- [ ] Candidate compositions enumerated
- [ ] Law checks run (identity, associativity)
- [ ] Chosen compositions documented with rationale
- [ ] Rejected paths documented with why
- [ ] Implementation-ready interfaces defined
- [ ] Branch candidates surfaced (blocking/parallel/deferred/void)

## Exit Criteria

1. **Chosen compositions** with rationale and constraints
2. **Rejected paths** noted (to avoid rework)
3. **Implementation interfaces** defined
4. **Law verifications** documented
5. **Branch notes** for new work surfaced
6. **Ledger updated**: `CROSS-SYNERGIZE: touched`

## Deliverables

Write to:
- `plans/agent-town/phase5-cross-synergize.md` — Compositions + rejected paths
- Update epilogue if significant discoveries

## Accursed Share (Entropy Budget)

Reserve 10% for exploration:
- **Dormant tree awakening**: Skim `_forest.md` for forgotten plans
- **Functor hunting**: What existing functors could lift this work?
- **Unexpected compositions**: Try composing with something that "shouldn't" work
- **Bounty board scan**: Does this resolve any open gripes?

Draw: `void.entropy.sip(amount=0.10)`

## Continuation Imperative

Upon completing this phase, emit:

```
⟿[IMPLEMENT]
/hydrate prompts/agent-town-phase5-implement.md
  handles:
    compositions: ${chosen_compositions}
    interfaces: ${implementation_interfaces}
    rejected: ${rejected_paths}
    laws: ${law_verifications}
    chunks: ${implementation_chunks}
    ledger: {CROSS-SYNERGIZE: touched}
    branches: ${branch_notes}
    entropy: 0.07
  mission: Write code + tests honoring laws/ethics; keep Minimal Output; ship value incrementally
  actions: TodoWrite chunks; run pytest watch; code/test slices; log metrics; graceful degradation first
  exit: Code + tests ready; ledger.IMPLEMENT=touched; QA notes captured; continuation → QA
```

Or halt with:
```
⟂[BLOCKED:composition_conflict] Chosen compositions violate category laws
⟂[BLOCKED:no_viable_path] All candidate compositions rejected
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

---

*This is the **CROSS-SYNERGIZE phase** for Agent Town Phase 5 Visualization/Streaming. The form is the function.*
