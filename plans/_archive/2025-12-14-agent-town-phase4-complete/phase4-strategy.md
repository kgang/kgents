---
path: plans/agent-town/phase4-strategy
status: active
progress: 100
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables:
  - agent-town/phase4-civilizational
session_notes: |
  STRATEGIZE phase complete. 8 chunks ordered across 2 parallel tracks.
  3 decision gates defined. Leverage points identified.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
entropy:
  planned: 0.08
  spent: 0.03
  returned: 0.0
---

# Agent Town Phase 4: STRATEGIZE

> *"Strategy is compression of execution space into leverage points."*

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Chunks | 8 (4.1-4.8) |
| Parallel Tracks | 2 (Citizens, UI) |
| Decision Gates | 3 (G1-G3) |
| Critical Path | 4.1 → 4.2 → 4.3 → 4.7 → 4.8 |
| Estimated Tests | ~210 new |

---

## Chunk Sequencing

### Dependency Graph

```
4.1 (Eigenvectors)
 │
 ▼
4.2 (15 New Citizens)
 │
 ▼
4.3 (Coalition + Reputation) ──────┐
 │                                  │
 ▼                                  │
4.7 (API + Metering) ──────────────┼──► 4.8 (Integration)
                                    │       ▲
4.4 (marimo Scaffold) ─────────────┘       │
 │                                          │
 ▼                                          │
4.5 (Event Bridge)                          │
 │                                          │
 ▼                                          │
4.6 (Dashboard Panels) ────────────────────┘
```

### Chunk Details

| Chunk | Description | Depends On | Effort | Tests | Owner |
|-------|-------------|------------|--------|-------|-------|
| **4.1** | 7D Eigenvectors + 12 Cosmotechnics | — | Low | 25 | Track A |
| **4.2** | 15 New Citizens (5 archetypes × 3) | 4.1 | Medium | 35 | Track A |
| **4.3** | Coalition + Reputation Mechanics | 4.2 | Medium | 30 | Track A |
| **4.4** | marimo Dashboard Scaffold | — | Medium | 15 | Track B |
| **4.5** | Event Bridge (NATS → marimo) | 4.4 | Low | 15 | Track B |
| **4.6** | Dashboard Panels (map, inspector, stream) | 4.5 | High | 25 | Track B |
| **4.7** | API Surface + Metering | 4.3 | Medium | 30 | Track A |
| **4.8** | Integration Tests + Demo | 4.6, 4.7 | High | 35 | Merge |

---

## Parallel Track Strategy

### Track A: Citizens (Core Engine)

```
4.1 ──► 4.2 ──► 4.3 ──► 4.7 ──┐
                               │
                               ▼
                             4.8
                               ▲
                               │
4.4 ──► 4.5 ──► 4.6 ──────────┘
```

**Track A Focus**: Data model, algorithms, API
- **4.1**: Foundation—must be rock solid
- **4.2**: Citizen factory with archetype templates
- **4.3**: Coalition detection + EigenTrust—algorithmic core
- **4.7**: API surface—connects to existing `protocols/api/app.py`

### Track B: UI (Visualization)

**Track B Focus**: marimo dashboard, event streaming
- **4.4**: marimo scaffold—new dependency, decision gate G1
- **4.5**: Event bridge—reuse existing `NATSBridge`
- **4.6**: Dashboard panels—highest effort, most visible

### Merge Point: 4.8

**Integration Requirements**:
- API endpoints serve real data from TownEnvironment
- marimo dashboard connects via HTTP/SSE
- Full simulation cycle: create → step → observe → repeat
- Demo script showcasing coalition formation and reputation

---

## Decision Gates

### G1: marimo Working? (After 4.4)

| Option | Trigger | Action |
|--------|---------|--------|
| **Continue** | marimo scaffold renders, reactive updates work | Proceed to 4.5 |
| **Fallback** | Import errors, reactivity broken | Switch to Textual TUI |

**Decision Criteria**:
- [ ] `marimo run town_dashboard.py` starts without error
- [ ] State changes propagate to dependent cells
- [ ] plotly figures render in browser

**Fallback Plan**: Use existing `agents/i/screens/` patterns with Textual

### G2: CDlib Compatible? (During 4.3)

| Option | Trigger | Action |
|--------|---------|--------|
| **Use CDlib** | `pip install cdlib` succeeds, kclique works | Use CDlib |
| **Pure Python** | Version conflicts, import errors | Use NetworkX fallback |

**Decision Criteria**:
- [ ] `from cdlib.algorithms import kclique` imports
- [ ] `kclique(G, k=3)` returns communities
- [ ] Performance acceptable (<100ms for 25 nodes)

**Fallback Plan**: `networkx.algorithms.community.k_clique_communities`

### G3: LLM Budget OK? (After 4.7 Tests)

| Option | Trigger | Action |
|--------|---------|--------|
| **5 LLM citizens** | Cost per cycle < $0.01 | Keep 5 |
| **3 LLM citizens** | Cost per cycle > $0.01 | Reduce to 3 evolving only |

**Decision Criteria**:
- [ ] Token usage per step < 5000 tokens
- [ ] Cost per 10-cycle simulation < $0.10
- [ ] Response latency < 3s per LLM citizen

**Fallback Plan**: Only Hana, Igor, Juno (3 evolving) are LLM-backed

---

## Leverage Points

### L1: Eigenvector Foundation (4.1)

**Why Leverage**: Every subsequent chunk depends on 7D eigenvectors.

**Investment**: Extra 20% effort on property tests.

**Payoff**: Zero rework in 4.2, 4.3, 4.6.

### L2: Coalition Algorithm (4.3)

**Why Leverage**: Coalition detection drives:
- UI visualization (4.6)
- API responses (4.7)
- Demo narrative (4.8)

**Investment**: Dual implementation (CDlib + NetworkX fallback).

**Payoff**: Robustness, no single point of failure.

### L3: Event Bridge Pattern (4.5)

**Why Leverage**: Event streaming enables:
- Real-time dashboard updates
- SSE endpoint for API
- Future mobile UI

**Investment**: Reuse `NATSBridge`, add town-specific events.

**Payoff**: Consistent eventing across CLI, API, marimo.

### L4: marimo Cell Structure (4.4)

**Why Leverage**: Cell structure is the UI skeleton.

**Investment**: Get reactive DAG right early.

**Payoff**: 4.5 and 4.6 plug into existing structure.

---

## Interface Definitions

### 4.1 → 4.2: Eigenvector Factory

```python
# 4.1 exports
from agents.town.eigenvectors import CitizenEigenvectors

# 4.2 uses
def create_archetype_citizen(
    archetype: Literal["Builder", "Trader", "Healer", "Scholar", "Watcher"],
    name: str,
    region: str,
) -> Citizen:
    """Factory using CitizenEigenvectors with archetype bias."""
```

### 4.2 → 4.3: Environment with Citizens

```python
# 4.2 exports
from agents.town.environment import create_phase4_environment

# 4.3 uses
env = create_phase4_environment()  # 25 citizens
coalitions = detector.detect(env, k=3)
reputation = engine.propagate(env)
```

### 4.3 → 4.7: Coalition/Reputation Data

```python
# 4.3 exports
from agents.town.coalition import Coalition, KCliqueCoalitionDetector
from agents.town.reputation import EigenTrustEngine

# 4.7 uses (API endpoints)
@router.get("/v1/town/{id}/coalitions")
async def get_coalitions(id: UUID) -> list[Coalition]:
    detector = KCliqueCoalitionDetector()
    return detector.detect(get_env(id))
```

### 4.5 → 4.6: Event Stream

```python
# 4.5 exports
from agents.town.bridge import TownEventBridge, TownEvent

# 4.6 uses (marimo)
bridge = TownEventBridge()
events = bridge.subscribe("town.*")
```

### 4.6, 4.7 → 4.8: Full Integration

```python
# 4.8 integration test
async def test_full_simulation():
    # Create via API
    response = await client.post("/v1/town/create", json={"template": "phase4"})
    town_id = response.json()["id"]

    # Step simulation
    for _ in range(10):
        step = await client.post(f"/v1/town/{town_id}/step")
        assert step.status_code == 200

    # Verify coalitions formed
    coalitions = await client.get(f"/v1/town/{town_id}/coalitions")
    assert len(coalitions.json()) >= 1

    # Verify reputation converged
    rep = await client.get(f"/v1/town/{town_id}/reputation")
    assert abs(sum(rep.json().values()) - 1.0) < 0.01
```

---

## Checkpoints

| Checkpoint | After | Criteria | Rollback |
|------------|-------|----------|----------|
| **CP1** | 4.1 | 25 eigenvector tests pass | N/A (foundation) |
| **CP2** | 4.2 | 25 citizens instantiate, manifest() works | Revert to Phase 3 env |
| **CP3** | 4.3 | Coalitions detected in test env | Disable coalition UI |
| **CP4** | 4.4 | marimo runs (G1 gate) | Switch to Textual |
| **CP5** | 4.6 | Dashboard renders all panels | Minimal dashboard |
| **CP6** | 4.7 | All 7 API endpoints pass tests | Stub endpoints |
| **CP7** | 4.8 | E2E demo completes | Document known issues |

---

## Risk-Adjusted Schedule

### Optimistic Path (All Gates Pass)

```
Track A: 4.1 → 4.2 → 4.3 → 4.7
Track B: 4.4 → 4.5 → 4.6
Merge:   4.8
```

### Pessimistic Path (G1 Fails)

```
Track A: 4.1 → 4.2 → 4.3 → 4.7
Track B: 4.4 → [FALLBACK: Textual] → 4.6'
Merge:   4.8
```

### Catastrophic Path (G2 + G3 Fail)

```
Track A: 4.1 → 4.2 → 4.3' (NetworkX only) → 4.7 (3 LLM citizens)
Track B: 4.4 → 4.5 → 4.6
Merge:   4.8 (reduced scope)
```

---

## Exit Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Chunks ordered with dependencies | ✓ | Dependency graph |
| Parallel tracks identified | ✓ | Track A, Track B |
| Decision gates documented | ✓ | G1, G2, G3 |
| Leverage points noted | ✓ | L1-L4 |
| ledger.STRATEGIZE=touched | ✓ | Frontmatter |

---

## Process Metrics

| Metric | Value |
|--------|-------|
| Phase | STRATEGIZE |
| Chunks ordered | 8 |
| Parallel tracks | 2 |
| Decision gates | 3 |
| Leverage points | 4 |
| Checkpoints | 7 |
| Entropy sip | 0.03 |

---

## Continuation

```
⟿[CROSS-SYNERGIZE]
exit: chunks_ordered=8, parallel_tracks=2, decision_gates=3
continuation → CROSS-SYNERGIZE for composition with other plans
```

---

*"The strategy is the map. Execution is the territory."*
