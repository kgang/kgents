---
path: docs/skills/n-phase-cycle/agent-town-phase6-cross-synergize
status: active
progress: 45
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables:
  - agents/town/demo_marimo.py
  - agents/i/marimo/widgets/scatter.py
  - agents/i/marimo/widgets/js/scatter.js
session_notes: |
  Phase 6: Live marimo notebook with eigenvector scatter and SSE updates.
  CROSS-SYNERGIZE COMPLETE: 6 compositions enumerated, 3 chosen, 3 deferred.
  Functor laws verified via test_visualization_contracts.py (lines 365-459).
  SSE→model→render flow traced through scatter.js lines 464-486.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.09
  remaining: 0.01
---

# Agent Town Phase 6: CROSS-SYNERGIZE

> Discover compositions and entanglements that unlock nonlinear value in the marimo scatter visualization.

**Scope**: `agents/town/demo_marimo.py`, `agents/i/marimo/widgets/scatter.py`, `agents/i/marimo/widgets/js/scatter.js`
**Heritage**: STRATEGIZE complete — 6-chunk backlog, 4 parallel tracks, CP1-CP3 validated
**Prerequisite**: STRATEGIZE complete (see `agent-town-phase6-strategize.md`)

---

## ATTACH

/hydrate

You are entering CROSS-SYNERGIZE phase for Agent Town Phase 6 (AD-005 N-Phase Cycle).

## Context from STRATEGIZE

**Validated Backlog (6 chunks)**:
| # | Chunk | Status |
|---|-------|--------|
| 1 | scatter.py imports/types | CP1 PASS |
| 2 | scatter.js static render | CP2 PASS |
| 3 | SSE EventSource wiring | CP3 PASS |
| 4 | marimo widget display | READY |
| 5 | click→cell flow | READY |
| 6 | Integration tests | READY |

**Parallel Tracks**:
- Track A: Widget Python (`scatter.py` - 224 lines)
- Track B: Widget JS (`scatter.js` - 535 lines)
- Track C: Notebook (`demo_marimo.py` - 534 lines)
- Track D: API integration (SSE endpoint at `town.py:428`)

**Interfaces Defined**:
- A↔B: ScatterModel traitlet contract (17 properties)
- C↔D: API contract (POST /town, GET /scatter, GET /events, GET /citizen)

**Branch Notes (Deferred)**:
- Point virtualization for >100 citizens
- PCA/t-SNE projection (sklearn integration)
- Coalition color legend component

---

## Your Mission

Hunt compositions and entanglements that could unlock 2x-10x value:

### 1. Enumerate Candidate Morphisms

| Composition | Description | Potential Value |
|-------------|-------------|-----------------|
| `scatter.map(filter) >> sparkline` | Filter scatter → project to sparkline | Ambient dashboard |
| `scatter.with_state(drift) >> SSE` | Drift events → model update → animate | Real-time viz |
| `notebook.cell >> scatter.clicked` | Click → cell re-run → details | Interactive exploration |
| `API.events >> NATS >> scatter` | SSE → NATS bridge → multi-client | Distributed visualization |
| `scatter >> k-gent.observe` | Scatter state → K-gent context | Soul-aware recommendations |

### 2. Probe Fast (Micro-Prototypes)

For each candidate, determine:
- Does it satisfy functor laws (identity, composition)?
- Does it violate Ethical/Tasteful constraints?
- What fixtures can test it without LLM burn?

**Priority Probes**:
1. **SSE → model.set() → render** (core data flow)
2. **clicked_citizen_id → cell re-run** (marimo reactivity)
3. **widget.map(f) ≡ widget.with_state(f(state))** (functor law)

### 3. Check Dormant Trees

Scan `plans/_forest.md` for compositions:
- `agentese-repl-crown-jewel` — Could scatter integrate with REPL?
- `reactive-substrate-unification` — Is scatter using the unified substrate?
- `monetization/grand-initiative` — Does visualization unlock monetization?

### 4. Select and Freeze

Choose compositions that:
- Pass law checks (identity, associativity)
- Don't violate Ethical/Tasteful
- Have clear implementation path in 6-chunk backlog

---

## Attention Budget

| Activity | Allocation |
|----------|------------|
| Morphism enumeration | 25% |
| Law verification probes | 35% |
| Dormant tree scan | 15% |
| Selection and freezing | 25% |

---

## Exit Criteria

- [x] Candidate compositions enumerated (at least 5) — 6 enumerated
- [x] Law checks performed (identity, composition) — All 3 laws verified via existing tests
- [x] Rejected paths documented with rationale — 3 deferred with rationale
- [x] Chosen compositions frozen for IMPLEMENT — 3 chosen
- [x] Branch notes updated if new work surfaced — No new branches needed

---

## CROSS-SYNERGIZE Results (2025-12-14)

### Chosen Compositions (Frozen for IMPLEMENT)

| # | Composition | Implementation Location | Law Verified |
|---|-------------|------------------------|--------------|
| 1 | SSE → model.set → render | scatter.js:464-486 | ✓ Identity |
| 2 | clicked_citizen_id → cell re-run | demo_marimo.py:371-416 | ✓ Composition |
| 3 | widget.map(f) ≡ widget.with_state(f(state)) | visualization.py:941-953 | ✓ State-Map |

### Deferred Compositions (with Rationale)

| Composition | Rationale | Target Phase |
|-------------|-----------|--------------|
| API.events >> NATS >> scatter | NATS multi-client requires additional consumer setup | Phase 7 |
| scatter >> k-gent.observe | K-gent coupling adds complexity; wait for stabilization | Phase 8 |
| scatter.map(filter) >> sparkline | Nice-to-have ambient dashboard; not core | Wave 8 |

### Law Verification Evidence

Tests found at:
- `test_visualization_contracts.py:365-459` — TestFunctorLaws (3 laws)
- `test_functor.py:128-154` — verify_all_functor_laws()
- `test_phase3_integration.py:218-220` — Integration law check

### SSE → Model → Render Data Flow

```
EventSource('town.eigenvector.drift')
    ↓ JSON.parse(e.data)
    ↓ points.map(p => p.citizen_id === data.citizen_id ? {...p, eigenvectors: data.new} : p)
    ↓ model.set('points', updatedPoints)
    ↓ model.save_changes()
    ↓ model.on('change:points', renderPoints)
    ↓ SVG circles transition (CSS 0.3s ease-out)
```

### Dormant Tree Compositions Identified

| Tree | Composition | Status |
|------|-------------|--------|
| agentese-repl-crown-jewel (85%) | sparkline handler exists | Available |
| reactive-substrate-unification (15%) | Not ready | Defer |
| monetization (0%) | Strategy only | Defer |

---

## Functor Law Verification Template

```python
# LAW 1: Identity
assert scatter.map(id) == scatter

# LAW 2: Composition
assert scatter.map(f).map(g) == scatter.map(lambda s: g(f(s)))

# LAW 3: State-Map Equivalence
assert scatter.map(f) == scatter.with_state(f(scatter.state.value))
```

---

## Accursed Share (Entropy Draw)

Reserve 0.03 for:
- Unexpected compositions (scatter + something that "shouldn't" work)
- Bounty board scan (`plans/_bounty.md`)
- Functor hunting in `FunctorRegistry`

Draw: `void.entropy.sip(amount=0.03)`

---

## Exit Signifier (LAW)

Upon completing CROSS-SYNERGIZE:

```
⟿[IMPLEMENT]
/hydrate
handles: compositions=SSE→model,click→cell,functor_law; interfaces=traitlet_contract,API_endpoints; rejected=NATS_multi_client(deferred),k-gent_observe(deferred); laws=identity_verified,composition_verified; ledger={CROSS-SYNERGIZE:touched}; branches=none_new
mission: write code + tests honoring laws/ethics; keep Minimal Output; start tests in background.
actions: TodoWrite chunks; implement CP4-CP6; run pytest watch; code/test slices; log metrics.
exit: code + tests ready; ledger.IMPLEMENT=touched; QA notes captured; continuation → QA.
```

Halt conditions:
```
⟂[BLOCKED:composition_conflict] Chosen compositions violate category laws
⟂[BLOCKED:no_viable_path] All candidate compositions rejected
⟂[ENTROPY_DEPLETED] Budget exhausted
```

---

Guard [phase=CROSS-SYNERGIZE][entropy=0.03][law_check=true][minimal_output=true]

---

## Auto-Inducer

⟿[CROSS-SYNERGIZE]
/hydrate
handles: backlog=6_chunks_validated; tracks=4_parallel; interfaces=2_contracts; laws=11_from_develop; ledger={STRATEGIZE:touched}; entropy=0.03
mission: hunt compositions/entanglements; verify functor laws; probe SSE→model flow; scan dormant trees
actions: enumerate morphisms; micro-prototype EventSource→render; verify widget.map(f)≡widget.with_state(f(state)); select+freeze
exit: chosen compositions + rationale; rejected paths noted; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT

---

## Changelog

- 2025-12-14: CROSS-SYNERGIZE complete. 6 compositions enumerated, 3 chosen, 3 deferred. Laws verified.
- 2025-12-14: Initial creation from STRATEGIZE phase completion

---

## Continuation Prompt (for IMPLEMENT)

```
⟿[IMPLEMENT]
/hydrate cat docs/skills/n-phase-cycle/agent-town-phase6-cross-synergize.md
handles: compositions=SSE→model(scatter.js:464),click→cell(demo_marimo.py:371),functor_law(visualization.py:941); interfaces=traitlet_17props,API_4endpoints; rejected=NATS_multi_client,k-gent_observe,sparkline_ambient; laws=identity✓,composition✓,state-map✓; ledger={CROSS-SYNERGIZE:touched}; branches=none_new
mission: write code + tests for CP4-CP6 (marimo widget display, click→cell flow, integration tests); keep Minimal Output; run pytest in background
actions: TodoWrite chunks; implement remaining checkpoints; verify marimo reactivity; measure render latency; emit metrics
exit: code + tests pass; mypy clean; ledger.IMPLEMENT=touched; QA notes captured; continuation → QA
```
