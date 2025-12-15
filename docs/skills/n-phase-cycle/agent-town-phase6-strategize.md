---
path: docs/skills/n-phase-cycle/agent-town-phase6-strategize
status: active
progress: 100
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables:
  - agents/town/demo_marimo.py
  - agents/i/marimo/widgets/scatter.py
  - agents/i/marimo/widgets/js/scatter.js
session_notes: |
  Phase 6: Live marimo notebook with eigenvector scatter and SSE updates.
  STRATEGIZE COMPLETE: All 3 contracts validated, 6-chunk backlog ordered, 4 tracks parallel-ready.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.07
  remaining: 0.03
---

# Agent Town Phase 6: STRATEGIZE

> Order implementation chunks for live marimo eigenvector scatter with SSE integration.

**Scope**: `agents/town/demo_marimo.py`, `agents/i/marimo/widgets/scatter.py`, `agents/i/marimo/widgets/js/scatter.js`
**Heritage**: DEVELOP complete — 3 contracts, 11 laws, ~950 lines drafted
**Prerequisite**: DEVELOP complete (see `agent-town-phase6-develop.md`)

---

## ATTACH

/hydrate

You are entering STRATEGIZE phase for Agent Town Phase 6 (AD-005 N-Phase Cycle).

## Context from DEVELOP

**Contracts Drafted**:
| File | Lines | Purpose |
|------|-------|---------|
| `scatter.py` | ~200 | EigenvectorScatterWidgetMarimo with traitlets |
| `scatter.js` | ~400 | ESM render with SVG + SSE EventSource |
| `demo_marimo.py` | ~350 | Interactive marimo notebook |

**Laws Established (11)**:
- L1-L3: Points serialization, SSE state sync, marimo cell reactivity
- L4-L8: SVG aspect ratio, CSS transitions, click→model, auto-reconnect, cleanup
- L9-L11: DAG cells, town_id→SSE, clicked→details

**Data Flow**:
```
API /events → EventSource → model.set() → SVG render
              ↓
         town.eigenvector.drift → Animate point transition
              ↓
         model.save_changes() → Traitlet sync → Marimo cell re-run
```

**Risks Mitigated**:
- SSE cleanup: ✓ Cleanup function in render()
- Marimo cell ordering: ✓ Explicit DAG
- Projection animation: ✓ CSS transitions

**Blockers**: None

---

## Your Mission

Order the implementation chunks to maximize leverage and minimize integration risk:

### 1. Prioritize by Leverage

Identify which contracts must land first based on:
- **Dependency graph**: scatter.py depends on visualization.py; scatter.js depends on scatter.py traitlets
- **Integration risk**: SSE connection is the riskiest piece — test early
- **Testability**: Widget can be tested without marimo notebook

### 2. Identify Parallel Tracks

| Track | Owner | Interface |
|-------|-------|-----------|
| Track A: Widget Python | Agent | scatter.py traitlet schema |
| Track B: Widget JS | Agent | scatter.js model.get/set contract |
| Track C: Notebook | Agent | demo_marimo.py cells |
| Track D: Integration | Agent | SSE + API wiring |

**Parallel opportunity**: Tracks A and B can proceed simultaneously if interface is stable.

### 3. Define Checkpoints

| Checkpoint | Criteria | Gate |
|------------|----------|------|
| CP1 | scatter.py imports cleanly, traitlets validate | ✓ → Continue |
| CP2 | scatter.js renders static points (no SSE) | ✓ → Continue |
| CP3 | SSE connects and receives events | ✓ → Continue |
| CP4 | Marimo notebook displays widget | ✓ → Continue |
| CP5 | Click flow triggers cell re-run | ✓ → IMPLEMENT complete |

### 4. Oblique Lookback

Before locking order, probe:
- What if we start with the hardest part (SSE integration)?
- What if we build notebook first and mock the widget?
- Are there hidden dependencies between tracks?

---

## Attention Budget

| Activity | Allocation |
|----------|------------|
| Dependency analysis | 30% |
| Parallel track identification | 25% |
| Checkpoint definition | 25% |
| Oblique lookback | 20% |

---

## Exit Criteria

- [x] Ordered backlog with dependencies and owners
- [x] Parallel tracks identified with interfaces
- [x] Checkpoints defined with pass/fail criteria
- [x] Decision gates for IMPLEMENT
- [x] Branch notes captured (if any deferred work)

---

## Ordered Backlog (VALIDATED)

| Order | Chunk | Dependencies | Owner | Checkpoint | Status |
|-------|-------|--------------|-------|------------|--------|
| 1 | Fix scatter.py imports and type hints | visualization.py | Agent | CP1 | ✅ PASS |
| 2 | Implement scatter.js static render | scatter.py | Agent | CP2 | ✅ PASS |
| 3 | Wire SSE EventSource in scatter.js | API /events | Agent | CP3 | ✅ PASS |
| 4 | Test widget in marimo notebook | scatter.py, scatter.js | Agent | CP4 | 🔄 READY |
| 5 | Implement click→cell flow | demo_marimo.py | Agent | CP5 | 🔄 READY |
| 6 | Integration tests | All | Agent | IMPLEMENT complete | 🔄 READY |

**Validation Results (2025-12-14)**:
- **CP1**: `scatter.py` imports cleanly, mypy passes (0 errors)
- **CP2**: `scatter.js` has complete render() with SVG structure (535 lines)
- **CP3**: `/v1/town/{id}/events` SSE endpoint exists in `protocols/api/town.py:428`
- **CP4-CP6**: Ready for IMPLEMENT phase

---

## Parallel Track Interfaces

### Interface A↔B: scatter.py ↔ scatter.js

```typescript
// Traitlet contract (Python → JS)
interface ScatterModel {
  town_id: string;
  api_base: string;
  points: ScatterPoint[];
  projection: string;
  selected_citizen_id: string;
  hovered_citizen_id: string;
  sse_connected: boolean;
  sse_error: string;
  clicked_citizen_id: string;  // JS → Python
  show_labels: boolean;
  show_coalition_colors: boolean;
  animate_transitions: boolean;
  show_evolving_only: boolean;
  archetype_filter: string[];
  coalition_filter: string;
}

interface ScatterPoint {
  citizen_id: string;
  citizen_name: string;
  archetype: string;
  eigenvectors: Record<string, number>;
  x: number;
  y: number;
  color: string;
  size: number;
  is_evolving: boolean;
  is_selected: boolean;
  coalition_ids: string[];
}
```

### Interface C↔D: Notebook ↔ API

```python
# API contract
POST /v1/town → TownResponse
GET /v1/town/{id}/scatter?projection=PAIR_WT → ScatterData
GET /v1/town/{id}/events → SSE stream
GET /v1/town/{id}/citizen/{name}?lod=2 → CitizenDetail
POST /v1/town/{id}/step → StepResponse
```

---

## Decision Gates

| Gate | Condition | Action if False |
|------|-----------|-----------------|
| G1 | scatter.py type-checks with mypy | Fix types before JS work |
| G2 | Static render works in marimo | Debug anywidget setup |
| G3 | SSE connects without errors | Check API CORS, endpoint |
| G4 | Click triggers clicked_citizen_id | Debug model.save_changes() |

---

## Branch Notes

| Branch | Status | Handle |
|--------|--------|--------|
| Point virtualization (>100) | Deferred | Future: Canvas fallback |
| PCA/t-SNE projection | Deferred | Future: sklearn integration |
| Coalition color legend | Deferred | Future: Add legend component |

---

## Accursed Share (Entropy Draw)

Reserve 0.01 for:
- Reverse-order experiment: What if we build notebook first?
- Risk probe: SSE integration is scariest — consider doing first
- Abort criteria: If anywidget doesn't work with marimo, need alternative

Draw: `void.entropy.sip(amount=0.01)`

---

## Exit Signifier (LAW)

Upon completing STRATEGIZE:

```
⟿[CROSS-SYNERGIZE]
/hydrate
handles: backlog=6_chunks; parallel=4_tracks; checkpoints=5; gates=4; interfaces=2; ledger={STRATEGIZE:touched}; branches=3_deferred
mission: hunt compositions/entanglements; probe widget+API synergy; test SSE→model flow
actions: enumerate morphisms (widget.map, scatter.with_state); micro-prototype EventSource; verify law composition
exit: chosen compositions + rationale; rejected paths noted; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT
```

Halt conditions:
```
⟂[BLOCKED:dependency_cycle] Circular dependencies in backlog
⟂[BLOCKED:interface_mismatch] Track A/B interfaces incompatible
⟂[ENTROPY_DEPLETED] Budget exhausted
```

---

Guard [phase=STRATEGIZE][entropy=0.04][law_check=true][minimal_output=true]

---

## Auto-Inducer

⟿[STRATEGIZE]
/hydrate
handles: contracts=scatter.py,scatter.js,demo_marimo.py; laws=11; files=3; lines=~950; risks=4_mitigated
mission: order implementation chunks; identify parallel tracks; define checkpoints and decision gates
actions: dependency analysis; parallel track interfaces; checkpoint criteria; oblique lookback
exit: ordered backlog + interfaces + checkpoints; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE

---

## Changelog

- 2025-12-14: Initial creation from DEVELOP phase completion
- 2025-12-14: STRATEGIZE COMPLETE — Backlog validated (CP1-CP3 pass), parallel tracks confirmed, ready for CROSS-SYNERGIZE
