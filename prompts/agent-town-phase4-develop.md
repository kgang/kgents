⟿[DEVELOP]

# Agent Town Phase 4: DEVELOP

## ATTACH

/hydrate

You are entering **DEVELOP** phase for Agent Town Phase 4.

handles: plan=`plans/agent-town/phase4-civilizational.md`; research=`plans/agent-town/phase4-research-findings.md`; chunks=4.1-4.8; scope=25_citizens+marimo_ui+api; ledger={PLAN:touched,RESEARCH:touched}; entropy=0.25/0.35

---

## Context from RESEARCH

### Decisions Made (High Confidence)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Technology | **marimo** | Reactive DAG maps to citizen state; Kent's "VISUAL UIs" intent |
| Coalition Algorithm | **k-clique percolation (k=3)** | Overlapping coalitions via CDlib |
| Reputation Model | **EigenTrust** | Trust weighted by assigner's reputation; converges |
| LLM Budget | **3-5 of 25** | Evolving citizens + archetype leaders only |

### Composable Components Identified

| Component | Location | Reuse For |
|-----------|----------|-----------|
| `GraphMemory` | `agents/town/memory.py` | Coalition graph storage |
| `Eigenvectors` | `agents/k/eigenvectors.py` | Extend to 7D |
| `NATSBridge` | `protocols/streaming/nats_bridge.py` | Town event streaming |
| `create_app` | `protocols/api/app.py` | Town API scaffold |
| `MeteringMiddleware` | `protocols/api/metering.py` | Per-citizen-turn billing |

### Files to Create

| File | Purpose |
|------|---------|
| `agents/town/eigenvectors.py` | 7D eigenvectors + 12 cosmotechnics |
| `agents/town/archetypes.py` | Builder, Trader, Healer, Scholar, Watcher |
| `agents/town/coalition.py` | k-clique detection + EigenTrust propagation |
| `agents/town/town_notebook.py` | marimo dashboard scaffold |
| `protocols/api/town.py` | API endpoints |
| `protocols/streaming/town_bridge.py` | Event bridge |

### Blockers: None

---

## Your Mission

Convert RESEARCH findings into **sharpened specs, APIs, and operable contracts**. Design compression: minimal specs that can regenerate code.

### Contracts to Define

#### 1. Extended Eigenvectors (7D)

```python
@dataclass
class CitizenEigenvectors:
    """7D personality eigenvectors for Phase 4 citizens."""
    warmth: float      # [0,1] - Existing
    curiosity: float   # [0,1] - Existing
    trust: float       # [0,1] - Existing
    creativity: float  # [0,1] - Existing
    patience: float    # [0,1] - Existing
    resilience: float  # [0,1] - NEW: ability to recover from setbacks
    ambition: float    # [0,1] - NEW: drive for status/influence

    def drift(self, other: "CitizenEigenvectors", max_drift: float = 0.1) -> float:
        """Calculate eigenvector drift (L2 distance). Must be ≤ max_drift per cycle."""
```

**Laws**:
- `drift(a, a) == 0` (identity)
- `drift(a, b) == drift(b, a)` (symmetry)
- `drift(a, c) <= drift(a, b) + drift(b, c)` (triangle inequality)

#### 2. Coalition Detection

```python
class CoalitionDetector:
    """k-clique percolation for coalition detection."""

    def detect(
        self,
        env: TownEnvironment,
        k: int = 3,
        min_weight: float = 0.5,
    ) -> list[Coalition]:
        """Find overlapping coalitions as k-cliques."""

@dataclass
class Coalition:
    """A group of citizens forming a coalition."""
    members: frozenset[str]  # Citizen IDs
    strength: float          # Average relationship weight
    formed_at: datetime
    purpose: str | None = None

    def overlaps(self, other: "Coalition") -> frozenset[str]:
        """Citizens in both coalitions."""
```

**Laws**:
- `|coalition.members| >= k` (minimum size)
- `strength ∈ [0, 1]` (bounded)
- Coalition membership can overlap (same citizen in multiple coalitions)

#### 3. EigenTrust Reputation

```python
class ReputationEngine:
    """EigenTrust-inspired reputation propagation."""

    def propagate(
        self,
        env: TownEnvironment,
        pre_trusted: dict[str, float] | None = None,
        alpha: float = 0.15,
        max_iter: int = 20,
    ) -> dict[str, float]:
        """
        Propagate reputation using personalized PageRank.

        trust[i] = α * pre_trusted[i] + (1-α) * Σ(trust[j] * local[j→i])
        """

    def update_eigenvectors(
        self,
        env: TownEnvironment,
        reputation: dict[str, float],
    ) -> None:
        """Apply reputation to citizen eigenvectors (trust axis)."""
```

**Laws**:
- `sum(reputation.values()) == 1.0` (normalized)
- Convergence: `||trust_n - trust_{n-1}|| < ε` for some n < max_iter
- Pre-trusted anchors prevent sybil dominance

#### 4. Town API

```python
# Endpoints (FastAPI)
POST /v1/town/create              → TownCreateResponse
POST /v1/town/{id}/step           → TownStepResponse
GET  /v1/town/{id}/citizens       → list[CitizenSummary]
GET  /v1/town/{id}/citizen/{name} → CitizenDetail (LOD 0-5)
GET  /v1/town/{id}/coalitions     → list[Coalition]
GET  /v1/town/{id}/events         → SSE stream
GET  /v1/town/{id}/reputation     → dict[str, float]

# Response Models
@dataclass
class TownCreateResponse:
    id: UUID
    name: str
    citizens: int
    regions: int
    tier: Literal["free", "pro", "enterprise"]

@dataclass
class TownStepResponse:
    cycle: int
    events: list[TownEvent]
    coalitions_formed: int
    reputation_delta: dict[str, float]
    tokens_used: int
```

**Laws**:
- LOD 0-5 follows existing pattern (strategy → forensic)
- SSE events include tracing span IDs
- Metering hooks for Pro/Enterprise tiers

#### 5. marimo Dashboard

```python
# marimo notebook structure (town_dashboard.py)

# Cell 1: State
env = mo.state(create_phase4_environment())

# Cell 2: Controls
step_button = mo.ui.button("Step Simulation")
citizen_selector = mo.ui.dropdown(citizens=[c.name for c in env.value.citizens.values()])

# Cell 3: Town Map (plotly)
def town_map(env: TownEnvironment) -> go.Figure:
    """Render citizens as nodes, relationships as edges."""

# Cell 4: Eigenvector Inspector
def eigenvector_radar(citizen: Citizen) -> go.Figure:
    """7D radar chart of personality."""

# Cell 5: Event Stream
events_log = mo.ui.table(columns=["timestamp", "actor", "action", "target"])

# Cell 6: Coalition View
def coalition_graph(coalitions: list[Coalition]) -> go.Figure:
    """Overlapping coalition visualization."""
```

**Laws**:
- Reactive: change citizen_selector → eigenvector_radar updates
- Pure cells: no side effects except through mo.state
- Export as standalone app via `marimo run`

---

## Actions

1. **Define 7D Eigenvector schema** with laws and drift function
2. **Specify Coalition dataclass** with k-clique detection contract
3. **Design EigenTrust propagation** with convergence guarantee
4. **Draft Town API spec** with OpenAPI/Pydantic models
5. **Sketch marimo dashboard** cell structure
6. **Enumerate risks**: marimo learning curve, CDlib dependency, LLM cost overrun
7. **Log metrics**: contracts defined, laws stated, examples drafted

---

## Exit Criteria

- [ ] 7D Eigenvector contract with 3 laws
- [ ] Coalition contract with k-clique invariants
- [ ] EigenTrust contract with convergence law
- [ ] Town API spec with 7 endpoints
- [ ] marimo dashboard sketch with 6 cells
- [ ] Risks documented (3+ items)
- [ ] ledger.DEVELOP=touched

---

## Entropy Draw

`void.entropy.sip(amount=0.07)` — design exploration budget.

---

## Continuation

Upon completing DEVELOP:

```
⟿[STRATEGIZE]
exit: contracts=5, laws=9, risks=3+, examples=per_contract
continuation → STRATEGIZE
```

OR

```
⟂[BLOCKED:law_violation] Proposed design violates category laws
⟂[BLOCKED:composition_failure] Contract cannot compose with existing agents
```

---

# Subsequent Phase Continuation Prompts

## STRATEGIZE Continuation (after DEVELOP)

```markdown
⟿[STRATEGIZE]

# Agent Town Phase 4: STRATEGIZE

## ATTACH

/hydrate

You are entering **STRATEGIZE** phase for Agent Town Phase 4.

handles: plan=`plans/agent-town/phase4-civilizational.md`; research=`plans/agent-town/phase4-research-findings.md`; contracts=`plans/agent-town/phase4-develop-contracts.md`; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched}; entropy=0.18/0.35

---

## Your Mission

Order chunks for **leverage**. Set owners, interfaces, checkpoints. Prep decision gates.

### Chunk Sequencing

| Chunk | Description | Depends On | Effort | Parallel Track |
|-------|-------------|------------|--------|----------------|
| 4.1 | 7D Eigenvectors + 12 Cosmotechnics | — | Low | Track A (Citizens) |
| 4.2 | 15 New Citizens (5 archetypes × 3) | 4.1 | Medium | Track A |
| 4.3 | Coalition + Reputation Mechanics | 4.2 | Medium | Track A |
| 4.4 | marimo Dashboard Scaffold | — | Medium | Track B (UI) |
| 4.5 | Event Bridge (NATS → marimo) | 4.4 | Low | Track B |
| 4.6 | Dashboard Panels (map, inspector, stream) | 4.5 | High | Track B |
| 4.7 | API Surface + Metering | 4.3 | Medium | Track A |
| 4.8 | Integration Tests + Demo | 4.6, 4.7 | High | Merge |

### Parallel Track Strategy

```
Track A (Citizens):  4.1 → 4.2 → 4.3 → 4.7
                                         \
                                          → 4.8 (Integration)
                                         /
Track B (UI):        4.4 → 4.5 → 4.6 ───┘
```

### Decision Gates

| Gate | Question | Options | Decision Point |
|------|----------|---------|----------------|
| G1 | marimo working? | Continue / Fallback to Textual | After 4.4 |
| G2 | CDlib compatible? | Use CDlib / Implement from scratch | After 4.3 start |
| G3 | LLM budget OK? | 5 citizens / 3 citizens | After 4.7 tests |

---

## Exit Criteria

- [ ] Chunks ordered with dependencies
- [ ] Parallel tracks identified
- [ ] Decision gates documented
- [ ] Leverage points noted
- [ ] ledger.STRATEGIZE=touched

---

## Continuation

⟿[CROSS-SYNERGIZE]
exit: chunks_ordered=8, parallel_tracks=2, decision_gates=3
continuation → CROSS-SYNERGIZE
```

---

## CROSS-SYNERGIZE Continuation (after STRATEGIZE)

```markdown
⟿[CROSS-SYNERGIZE]

# Agent Town Phase 4: CROSS-SYNERGIZE

## ATTACH

/hydrate

You are entering **CROSS-SYNERGIZE** phase for Agent Town Phase 4.

handles: plan=`plans/agent-town/phase4-civilizational.md`; strategy=`plans/agent-town/phase4-strategy.md`; ledger={...,STRATEGIZE:touched}; entropy=0.13/0.35

---

## Your Mission

Identify **compositions** with other plans and agents. Surface synergies. Prevent isolation.

### Cross-Synergy Candidates

| This Work | Synergizes With | Composition |
|-----------|-----------------|-------------|
| marimo dashboard | `plans/reactive-substrate-unification` | Unified widget protocol |
| EigenTrust | `agents/k/eigenvectors.py` | Shared eigenvector library |
| Coalition detection | `agents/d/graph.py` | Reuse BFS patterns |
| Town API | `protocols/api/sessions.py` | Consistent metering |
| Event bridge | `protocols/streaming/nats_bridge.py` | Extend, don't duplicate |

### Dormant Plans to Unblock

- `plans/k-terrarium-llm-agents` — Town provides live citizen demo
- `plans/agentese-universal-protocol` — Town as AGENTESE showcase

---

## Exit Criteria

- [ ] 5+ cross-synergies identified
- [ ] Dormant plans noted
- [ ] No conflicting implementations
- [ ] ledger.CROSS-SYNERGIZE=touched

---

## Continuation

⟿[IMPLEMENT]
exit: synergies=5+, conflicts=0, dormant_unblocked=2
continuation → IMPLEMENT (Track A: 4.1 first)
```

---

## IMPLEMENT Continuation (after CROSS-SYNERGIZE)

```markdown
⟿[IMPLEMENT]

# Agent Town Phase 4: IMPLEMENT (Chunk 4.1)

## ATTACH

/hydrate

You are entering **IMPLEMENT** phase for Agent Town Phase 4, Chunk 4.1.

handles: chunk=4.1; scope=7D_eigenvectors+12_cosmotechnics; contracts=`phase4-develop-contracts.md`; ledger={...,CROSS-SYNERGIZE:touched}; entropy=0.10/0.35

---

## Your Mission

Implement **7D Eigenvectors + 12 Cosmotechnics** per the DEVELOP contracts.

### Implementation Targets

1. `agents/town/eigenvectors.py` — CitizenEigenvectors dataclass
2. `agents/town/cosmotechnics.py` — 12 cosmotechnics constants
3. `agents/town/_tests/test_eigenvectors.py` — Property tests for drift laws

### Laws to Verify

- `drift(a, a) == 0` (identity)
- `drift(a, b) == drift(b, a)` (symmetry)
- Triangle inequality

---

## Exit Criteria

- [ ] `eigenvectors.py` created with 7D dataclass
- [ ] `cosmotechnics.py` with 12 constants
- [ ] Tests passing for drift laws
- [ ] ledger.IMPLEMENT=touched (chunk 4.1)

---

## Continuation

⟿[IMPLEMENT] (next chunk 4.2)
OR
⟿[QA] (if all Track A chunks done)

Loop through: 4.1 → 4.2 → 4.3 → 4.7 → QA → TEST
```

---

## QA Continuation (after IMPLEMENT)

```markdown
⟿[QA]

# Agent Town Phase 4: QA

## ATTACH

/hydrate

You are entering **QA** phase for Agent Town Phase 4.

handles: chunks_implemented=[4.1-4.7]; ledger={...,IMPLEMENT:touched}; entropy=0.05/0.35

---

## Your Mission

Run **lint, type, security** checklist. Fix or document all findings.

### Checklist

- [ ] `uv run ruff check impl/claude/agents/town/` → 0 errors
- [ ] `uv run mypy impl/claude/agents/town/` → 0 errors
- [ ] `uv run pytest impl/claude/agents/town/ -q` → all pass
- [ ] Security: no hardcoded secrets, no SQL injection in API
- [ ] Deprecation warnings addressed

---

## Continuation

⟿[TEST] if all pass
⟂[BLOCKED:mypy_errors] if type errors remain
⟂[BLOCKED:test_failures] if tests fail
```

---

## TEST Continuation (after QA)

```markdown
⟿[TEST]

# Agent Town Phase 4: TEST

## ATTACH

/hydrate

You are entering **TEST** phase for Agent Town Phase 4.

handles: qa_passed=true; ledger={...,QA:touched}; entropy=0.03/0.35

---

## Your Mission

Add/update **tests** for new functionality. Verify integration.

### Test Categories

| Category | Tests | Target |
|----------|-------|--------|
| Unit: Eigenvectors | drift laws, normalization | 10 |
| Unit: Coalition | k-clique detection, overlap | 15 |
| Unit: Reputation | convergence, pre-trust | 10 |
| Integration: API | endpoints, metering | 20 |
| Integration: marimo | reactive updates | 10 |
| E2E: Demo script | full simulation cycle | 5 |

---

## Continuation

⟿[EDUCATE] if tests pass
⟂[BLOCKED:test_failures] if failures
```

---

## EDUCATE Continuation (after TEST)

```markdown
⟿[EDUCATE]

# Agent Town Phase 4: EDUCATE

## ATTACH

/hydrate

You are entering **EDUCATE** phase for Agent Town Phase 4.

handles: tests_passing=true; ledger={...,TEST:touched}; entropy=0.02/0.35

---

## Your Mission

Write **user/maintainer notes**. Update docs.

### Artifacts

- [ ] `docs/skills/agent-town-phase4.md` — Usage guide
- [ ] `README.md` update — Agent Town section
- [ ] `CLAUDE.md` — Add Town to agent taxonomy
- [ ] marimo notebook comments — Inline documentation

---

## Continuation

⟿[MEASURE]
```

---

## MEASURE Continuation (after EDUCATE)

```markdown
⟿[MEASURE]

# Agent Town Phase 4: MEASURE

## ATTACH

/hydrate

You are entering **MEASURE** phase for Agent Town Phase 4.

handles: docs_updated=true; ledger={...,EDUCATE:touched}; entropy=0.01/0.35

---

## Your Mission

Hook **metrics**. Define observability.

### Metrics to Track

| Metric | Source | Dashboard |
|--------|--------|-----------|
| Citizens active | env.citizens count | marimo |
| Coalitions formed | CoalitionDetector.detect | marimo |
| LLM tokens/turn | MeteringMiddleware | API |
| Event stream lag | NATS bridge | ops |
| Test count | pytest | CI |

---

## Continuation

⟿[REFLECT]
```

---

## REFLECT Continuation (after MEASURE)

```markdown
⟿[REFLECT]

# Agent Town Phase 4: REFLECT

## ATTACH

/hydrate

You are entering **REFLECT** phase for Agent Town Phase 4.

handles: metrics_hooked=true; ledger={...,MEASURE:touched}; entropy=0.00/0.35

---

## Your Mission

Distill **learnings**. Seed next cycle. Write epilogue.

### Learnings Template

```
2025-12-XX  [atomic insight from this phase]
2025-12-XX  [another insight]
```

### Next Cycle Seeds

- Phase 5: Persistence (SQLite)
- Phase 5: Multi-tenancy
- Phase 6: Mobile UI

### Epilogue

Write to `plans/_epilogues/2025-12-XX-agent-town-phase4-complete.md`

---

## Continuation

⟂[DETACH:cycle_complete] Phase 4 scope exhausted. Await human for Phase 5 kickoff.

OR

⟿[PLAN] (Phase 5) if momentum continues.
```

---

*"The form is the function. Each prompt generates its successor by the same principles that generated itself."*
