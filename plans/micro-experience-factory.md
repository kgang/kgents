---
path: plans/micro-experience-factory
status: active
progress: 0
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [interfaces/dashboard-overhaul, deployment/permanent-kgent-chatbot, agent-town-next]
session_notes: |
  PLAN phase complete. Micro-Experience Factory Crown Jewel: isometric foundry
  unifying Agent Town + AGENTESE REPL + Reactive UI. Thin skin over existing substrate.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched  # 2025-12-14: isometric.py, trace_bridge.py, 32 contract tests
  STRATEGIZE: touched  # 2025-12-14: 7-step integration sequence, fallbacks, kill switches
  CROSS-SYNERGIZE: touched  # 2025-12-14: 5 synergy tables, 4 laws verified
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.08
  spent: 0.02
  returned: 0.0
---

# Micro-Experience Factory: Crown Jewel Plan

> *"The isometric lattice where pipelines self-attach, citizens evolve, and slop blossoms bloom."*

## Mission

Fuse Agent Town, AGENTESE REPL, and the Reactive UI into a **Micro-Experience Factory**—a pixelated isometric foundry where agents-as-pipelines self-compose via operads, stream through TownFlux, project to multiple targets (CLI/TUI/marimo/JSON), and enable HITL perturbation without bypassing state.

## Scope

### MVP (This Phase)

| Chunk | Description | Dependencies | Effort |
|-------|-------------|--------------|--------|
| **C1: Trace Schema** | Define TraceEvent schema bridging REPL commands + TownEvents with independence relations | TraceMonoid exists | 2 |
| **C2: Isometric Skin** | Thin SVG layer over existing ScatterWidget + AgentCard state | visualization.py | 3 |
| **C3: Flux→Widget Wiring** | Wire TownFlux SSE stream into reactive widgets (CLI/TUI/marimo) | flux.py, widget.py | 2 |
| **C4: HITL Perturbation Pads** | Perturbation cards that post to AUP → Flux (no bypass) | aup.py, flux.py | 2 |
| **C5: Replay Scrubber** | Time-scrub trace monoid to replay TownFlux segments | trace_monoid.py, TownFlux | 2 |
| **C6: AUP Town Endpoints** | Expose TownFlux + trace via AUP HTTP/SSE/WS channels | aup.py, serializers.py | 2 |
| **C7: Demo Beat** | Vertical slice: init town → stream → scatter → perturb → replay | All above | 2 |

**Total MVP Effort**: ~15 story points

### Non-Goals (Deferred)

- Full 3D/Three.js rendering (use SVG isometric projection)
- Mobile-first UI (desktop/notebook first)
- Production NATS cluster (use mock/local)
- Complex braiding visualization (simple replay only)
- New agent archetypes (use existing 5)

## Exit Criteria

1. `kg town demo` boots isometric lattice with 5 citizens
2. TownFlux events stream to CLI/TUI/marimo projections
3. HITL card triggers `gossip` without bypassing Flux state
4. Replay scrubber rewinds 30s of trace monoid
5. AUP endpoint `/api/v1/world/town/flux` streams SSE
6. Functor law verified: `scatter.map(f) ≡ scatter.with_state(f(state))`
7. All tests pass, mypy clean
8. Demo beats in `brainstorming/_archive/docs/micro-experience-factory.md` executable

## Attention Budget

| Focus | % | Notes |
|-------|---|-------|
| Primary: C2+C3 (visualization + wiring) | 40% | The core value |
| Secondary: C4+C5 (HITL + replay) | 30% | The differentiator |
| Foundation: C1+C6 (trace schema + AUP) | 20% | Enable composability |
| Accursed Share | 10% | Slop blossoms, easter eggs |

## Dependencies

```
plans/agentese-universal-protocol (AUP impl)  ──enables──▶  C6 (AUP Town Endpoints)
agents/town (Phase 6 complete)               ──enables──▶  C3, C4, C5
agents/i/reactive (KgentsWidget)             ──enables──▶  C2, C3
weave/trace_monoid.py                        ──enables──▶  C1, C5
protocols/cli/repl.py                        ──enables──▶  C1 (trace schema)
```

## Risk Map

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SVG isometric complexity | Medium | Medium | Use 2.5D projection, not full 3D |
| SSE latency to marimo | Low | High | Test anywidget SSE bridge early |
| Trace replay correctness | Medium | High | Independence relations must be verified |
| Scope creep to full game | High | High | Strict non-goals; demo beats only |

## Branch Notes (Branching Protocol)

- **Potential**: `plans/isometric-game-engine` if scope expands to full game
- **Deferred**: `plans/nats-production-cluster` when ready for scale

## Chunking (Parallel vs Sequential)

```
C1 (Trace Schema) ───────────────────────────────┐
                                                  │
C2 (Isometric Skin) ─────────────────────────────┼──▶ C7 (Demo Beat)
                                                  │
C3 (Flux→Widget) ────────────────────────────────┤
                                                  │
C4 (HITL Pads)  ─────────────────────────────────┤
                       │                          │
                       └──▶ C5 (Replay) ──────────┤
                                                  │
C6 (AUP Endpoints) ──────────────────────────────┘
```

- **Parallel**: C1, C2, C3, C6 can proceed independently
- **Sequential**: C4 requires C3 (Flux wiring); C5 requires C4 (perturbation) + C1 (trace schema)
- **Integration**: C7 requires all above

## Key Insights (From Context Hydration)

1. **Existing substrate is rich**: KgentsWidget, TownFlux SSE, ScatterWidget, AUP router all exist. This is a wiring + skin job, not greenfield.

2. **TraceMonoid already done**: `weave/trace_monoid.py` has independence relations, append, and braiding. Wire it to TownEvent.

3. **AUP + GardenState aligned**: `plans/meta.md` confirms Agent Town GardenState ≡ AUP GardenState. No translation layer needed.

4. **SVG > Canvas for <100 elements**: `meta.md` learning. Citizens ≤ 25, so SVG is correct choice.

5. **Perturbation law inviolate**: Flux perturbation must inject, never bypass (spec/principles.md §6).

## Questions for RESEARCH

1. Which isometric SVG libs work with marimo anywidget? (d3-isometric? custom?)
2. What's the exact TownEvent → TraceEvent mapping for independence relations?
3. How does the REPL session wire to TownFlux for command tracing?
4. What's the marimo anywidget SSE subscription pattern?
5. Are there existing replay UI patterns in `agents/i/reactive/`?

---

## RESEARCH Decision Log

### Isometric Library: **CSS transforms (MVP)**
- Decision: Use simple CSS `transform: rotateX(60deg) rotateZ(-45deg)` for MVP
- Fallback: Upgrade to elchininet/isometric TypeScript lib if complexity grows
- Rationale: SVG > Canvas for <100 elements (meta.md), citizens ≤ 25

### SSE Infrastructure: **Already built**
- `TownSSEEndpoint` in `visualization.py:320-401`
- `/events` endpoint in `town.py:432-461`
- Wire to scatter widget state updates

### Trace Wiring: **TownTraceEvent wrapper**
- Independence: events from different citizens can commute
- Dependency: same-citizen events ordered

### marimo anywidget SSE: **Traitlet sync + ESM fetch**
- Use existing MarimoAdapter traitlet pattern
- SSE subscription via separate JS fetch in ESM module

---

## DEVELOP Artifacts

| Artifact | File | Tests |
|----------|------|-------|
| Isometric contracts | `agents/town/isometric.py` | 15 passing |
| Trace bridge | `agents/town/trace_bridge.py` | 17 passing |

---

## STRATEGIZE: Integration Sequence

### Sequence (Critical Path)

```
Step 1: Wire TownFlux → TownTrace
        - Append events to trace on TownFlux.step()
        - Test: independence relations computed correctly

Step 2: Wire TownTrace → ReplayState
        - ReplayState.current_tick → TownTrace.replay_range()
        - Test: scrubber selects correct event range

Step 3: Wire ScatterState → IsometricState
        - ScatterPoint positions map to IsometricCell grid
        - Test: citizens appear at correct grid cells

Step 4: Implement IsometricWidget.project()
        - CLI: ASCII grid with glyphs
        - JSON: IsometricState.to_dict()
        - TUI/marimo: delegate to MarimoAdapter

Step 5: Wire PerturbationPad → AUP → TownFlux
        - POST /api/v1/world/town/perturb {operation, participants}
        - Inject as priority event via Flux perturbation
        - Test: perturbation appears in trace without bypass

Step 6: Wire SSE → IsometricWidget updates
        - Subscribe to /api/v1/world/town/{id}/events
        - On event: update IsometricState, trigger re-render
        - Test: SSE event → widget state update < 100ms

Step 7: Demo beat integration
        - kg town demo → isometric lattice
        - Verify all beats from brainstorming/_archive/docs/micro-experience-factory.md
```

### Fallback Paths

| Risk | Fallback |
|------|----------|
| SVG isometric complexity | Fall back to flat 2D scatter |
| SSE → marimo latency | Use polling with 500ms interval |
| Trace replay correctness | Disable commutation, use strict ordering |
| AUP perturbation issues | Direct TownFlux.perturb() call |

### Kill Switches

- `KGENTS_ISOMETRIC_ENABLED=0` → disable isometric, show flat scatter
- `KGENTS_TRACE_REPLAY_ENABLED=0` → disable replay scrubber
- `KGENTS_PERTURBATION_ENABLED=0` → disable HITL pads

---

## CROSS-SYNERGIZE: Synergy Table

### System Mappings

| Micro-Experience Factory | Existing System | Synergy |
|--------------------------|-----------------|---------|
| IsometricWidget | KgentsWidget[S] | Same base class, functor laws |
| IsometricState.citizens | ScatterState.points | Direct mapping via tuple |
| PerturbationPad.operation | TownOperad.operations | Same operation names |
| TownTraceEvent | weave/Event | Compatible schema, wrap |
| ReplayState | REPL session state | Can share tick/scrubber |
| SSE events | TownSSEEndpoint | Wire directly |
| AUP /perturb endpoint | sessions.py pattern | Same router style |

### REPL Synergies (protocols/cli/repl.py)

| REPL Feature | Factory Feature | Bridge |
|--------------|-----------------|--------|
| `world.town.*` paths | Isometric rendering | Invoke triggers widget update |
| Pipeline `>>` composition | Pipeline segments in grid | Trace captures composition |
| Observer context | ScatterPoint colors | Same archetype mapping |
| Session persistence | Trace persistence | Both use JSON serialization |

### AUP Synergies (protocols/api/aup.py)

| AUP Feature | Factory Feature | Bridge |
|-------------|-----------------|--------|
| `/compose` endpoint | Pipeline execution | Same composition pipeline |
| SSE streaming | Widget updates | Wire TownSSEEndpoint |
| Observer headers | ScatterPoint.archetype | Same X-Observer-Archetype |
| WebSocket subscriptions | Live isometric updates | town:{id} channel |

### Reactive Substrate Synergies (agents/i/reactive/)

| Reactive Feature | Factory Feature | Bridge |
|------------------|-----------------|--------|
| Signal[S] | IsometricState signal | Same reactive pattern |
| RenderTarget.JSON | to_dict() methods | Direct JSON projection |
| MarimoAdapter | anywidget bridge | Wrap IsometricWidget |
| Animation combinators | Cell animation_phase | Use existing tween/spring |

### Agent Town Synergies (agents/town/)

| Town Feature | Factory Feature | Bridge |
|--------------|-----------------|--------|
| EigenvectorScatterWidget | IsometricWidget | Same scatter data, different skin |
| TownFlux.step() | TownTrace.append() | Wire on each step |
| TownSSEEndpoint | SSE subscription | Direct reuse |
| CoalitionManager | IsometricCell.coalition_ids | Coalition coloring |

### Laws Preserved

| Law | Verification | Source |
|-----|--------------|--------|
| Functor identity | `isometric.map(id) ≡ isometric` | spec/principles.md §5 |
| Functor composition | `isometric.map(f).map(g) ≡ isometric.map(f . g)` | spec/principles.md §5 |
| Perturbation principle | Pads inject, never bypass | spec/principles.md §6 |
| Independence commutation | `ab = ba` iff disjoint participants | weave/trace_monoid.py |

---

*Plan authored: 2025-12-14 | Current: CROSS-SYNERGIZE | Entropy: 0.08 planned, 0.04 spent*
