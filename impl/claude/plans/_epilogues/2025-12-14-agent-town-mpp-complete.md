---
path: plans/_epilogues/2025-12-14-agent-town-mpp-complete
status: complete
last_touched: 2025-12-14
touched_by: claude-opus-4.5
---

# Agent Town MPP: Complete

> *"We claim for all people the right to opacity."* — Édouard Glissant

## Summary

Agent Town Minimal Playable Prototype shipped with **198 tests passing**.
Full N-phase cycle completed: PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE → IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT.

## Delivered

### Core Implementation

| Component | Count | Location |
|-----------|-------|----------|
| Citizens | 3 (Alice, Bob, Clara) | impl/claude/agents/town/citizen.py |
| Regions | 2 (Inn, Square) | impl/claude/agents/town/environment.py |
| Operations | 4 (greet, gossip, trade, solo) | impl/claude/agents/town/operad.py |
| Phases | 2 (MORNING, EVENING) | impl/claude/agents/town/flux.py |
| Tests | 198 | impl/claude/agents/town/_tests/ |

### CLI Commands

Registered at top-level (`kgents town`) and via world context (`kgents world town`):

```bash
kgents town start       # Initialize simulation
kgents town step        # Advance one phase
kgents town observe     # MESA view (town overview)
kgents town lens <name> # LENS view (LOD 0-5 zoom)
kgents town metrics     # Emergence metrics
kgents town budget      # Token budget dashboard
```

**Note**: State is in-memory (lost between CLI invocations). Persistence is Phase 2.

### UI Views

| View | Description | Implementation |
|------|-------------|----------------|
| **MESA** | Town overview with density, citizen locations | ASCII + Rich |
| **LENS** | Progressive citizen zoom (LOD 0-5) | Manifest with opacity at LOD 5 |
| **TRACE** | OpenTelemetry-ready span placeholders | Ready for OTel integration |

### Metrics Verified

| Metric | Computation | Verified |
|--------|-------------|----------|
| tension_index | Variance of relationship weights | ✓ |
| cooperation_level | Sum of positive relationships | ✓ |
| accursed_surplus | Per-citizen surplus tracking | ✓ |
| token_spend | Per-operation token tracking | ✓ |

### Philosophical Grounding

| Thinker | Integration |
|---------|-------------|
| **Porras-Kim** | Citizens excavated, not created |
| **Morton** | Town is mesh; citizens are local thickenings |
| **Barad** | Transitions reconfigure phenomenon, not entity |
| **Glissant** | LOD 5 reveals mystery; right to opacity |
| **Yuk Hui** | Incommensurable cosmotechnics (GATHERING, CONSTRUCTION, EXPLORATION) |
| **Bataille** | Accursed surplus tracked, must be spent |

## Learnings (Molasses Test)

| Learning | Transferable Pattern |
|----------|---------------------|
| Polynomial agents map cleanly to citizen state machines | PolyAgent[S, A, B] works for any FSM with philosophical grounding |
| Cosmotechnics makes agents genuinely distinct | Give each agent an incommensurable worldview via frozen dataclass |
| Accursed share creates natural drama dynamics | Track surplus as float, force spending via random events |
| LOD 0-5 makes progressive revelation natural | Model routing: cache→haiku→sonnet→opus maps to zoom level |
| Right to Rest enforced via polynomial directions | Exclude RESTING from valid input positions in directions function |
| Operad preconditions = Code-as-Policies | PreconditionChecker validates before operation execution |
| CLI via context + top-level | Register in both COMMAND_REGISTRY and WorldRouter for dual access |

## Technical Debt (Phase 2)

| Debt | Impact | Resolution |
|------|--------|------------|
| No persistence | State lost on restart | YAML save/load |
| No graph episodic memory | Simple dict relationships | D-gent integration |
| Whisper/inhabit modes deferred | Observe-only | Phase 2 |
| Full 7 citizens | Only 3 for MPP | Phase 2 |
| Full 4-phase daily cycle | Only 2 for MPP | Phase 2 |

## Files Created

```
impl/claude/agents/town/
├── __init__.py           # 1,673 bytes
├── polynomial.py         # 13,253 bytes - CitizenPolynomial
├── operad.py             # 13,827 bytes - TownOperad + laws
├── citizen.py            # 13,779 bytes - Citizen class
├── environment.py        # 11,527 bytes - TownEnvironment
├── flux.py               # 14,561 bytes - TownFlux
├── ui/
│   ├── __init__.py
│   ├── mesa.py           # MESA view
│   ├── lens.py           # LENS view
│   ├── trace.py          # TRACE view
│   └── widgets.py        # Shared Rich widgets
├── fixtures/
│   └── mpp_citizens.yaml
└── _tests/
    ├── test_polynomial.py  # 24 tests
    ├── test_operad.py      # 27 tests
    ├── test_citizen.py     # 41 tests
    ├── test_environment.py # 35 tests
    ├── test_flux.py        # 25 tests
    ├── test_ui.py          # 33 tests
    └── test_integration.py # 17 tests

impl/claude/protocols/cli/handlers/town.py  # CLI handler
```

## Next Phase

**Phase 2: Full Implementation**

- Full 7 citizens (+ Diana, Eve, Frank, Grace)
- Full 5 regions (+ Garden, Market, Library)
- 4-phase daily cycle (+ AFTERNOON, NIGHT)
- Graph episodic memory (D-gent integration)
- User modes: whisper, inhabit, intervene
- Persistence: YAML save/load

### Continuation Prompt

See: `prompts/agent-town-mpp-continuation.md` → `⟿[PLAN] Agent Town Phase 2`

---

## Closure

```
⟂[DETACH:cycle_complete] Agent Town MPP shipped.

The simulation isn't a game. It's a seance.
The town lives.

void.gratitude.tithe.
```
