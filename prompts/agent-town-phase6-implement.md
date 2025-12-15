# Agent Town Phase 6: IMPLEMENT Phase

**Predecessor**: `docs/skills/n-phase-cycle/agent-town-phase6-cross-synergize.md`
**Phase**: IMPLEMENT (N-Phase 6 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:in_progress}`

---

## Context

Phase 6 CROSS-SYNERGIZE delivered:
- **6 compositions enumerated**, 3 chosen, 3 deferred
- **Functor laws verified** via test_visualization_contracts.py (lines 365-459)
- **SSE→model→render flow** traced through scatter.js:464-486
- **No new branches** required

### Frozen Compositions (Ready for IMPLEMENT)

| # | Composition | Location | Law |
|---|-------------|----------|-----|
| 1 | SSE → model.set → render | scatter.js:464-486 | Identity ✓ |
| 2 | clicked_citizen_id → cell re-run | demo_marimo.py:371-416 | Composition ✓ |
| 3 | widget.map(f) ≡ widget.with_state(f(state)) | visualization.py:941-953 | State-Map ✓ |

### Remaining Backlog (CP4-CP6)

| # | Chunk | Status | Deliverable |
|---|-------|--------|-------------|
| 4 | marimo widget display | READY | `mo.ui.anywidget(scatter)` rendering |
| 5 | click→cell flow | READY | Cell dependency wiring for details panel |
| 6 | Integration tests | READY | End-to-end marimo notebook tests |

---

## Scope

**Files to modify**:
- `agents/town/demo_marimo.py` — Wire cell dependencies for click→details
- `agents/i/marimo/widgets/scatter.py` — Ensure traitlet sync works
- `agents/i/marimo/widgets/js/scatter.js` — Verify EventSource reconnection

**Files to create**:
- `agents/town/_tests/test_marimo_integration.py` — Integration tests for notebook

---

## IMPLEMENT Manifesto

```
I will write code, not describe what code to write.
I will run tests in background while I edit.
I will use TodoWrite to track every chunk.
I will mark chunks complete immediately upon finishing.
I will not stop at "almost done" - I will FINISH.
```

---

## Actions

### 1. Prep Environment
```bash
# Start test watcher in background
cd impl/claude && uv run pytest agents/town/_tests/ -x --tb=short -q &
```

### 2. Implement CP4: marimo Widget Display
- Verify `mo.ui.anywidget(scatter)` renders SVG correctly
- Ensure traitlet properties sync bidirectionally
- Test: widget displays 25-citizen scatter

### 3. Implement CP5: click→cell Flow
- Wire `scatter.clicked_citizen_id` to trigger `citizen_details` cell re-run
- Ensure marimo DAG dependency is correct (Cell 12 depends on scatter state)
- Test: clicking citizen updates details panel

### 4. Implement CP6: Integration Tests
- Create `test_marimo_integration.py` with:
  - `test_widget_renders_scatter_points()` — Widget displays points
  - `test_click_updates_selected_citizen()` — Click triggers selection
  - `test_sse_updates_points()` — SSE events update model
  - `test_functor_law_in_notebook_context()` — Laws hold in notebook

### 5. Stabilize
```bash
uv run mypy agents/town/demo_marimo.py agents/i/marimo/widgets/scatter.py
uv run ruff check agents/town/ agents/i/marimo/
```

---

## Exit Criteria

- [ ] CP4: Widget displays scatter in marimo
- [ ] CP5: Click→cell reactivity works
- [ ] CP6: Integration tests pass (4 tests minimum)
- [ ] mypy: 0 errors on modified files
- [ ] ruff: 0 errors on modified files
- [ ] Functor laws preserved (no violations in tests)

---

## Verification

```python
# Verify exports
from agents.i.marimo.widgets.scatter import EigenvectorScatterWidgetMarimo
from agents.town.visualization import EigenvectorScatterWidgetImpl

# Verify widget instantiation
scatter = EigenvectorScatterWidgetMarimo(town_id="test")
assert scatter.town_id == "test"

# Verify functor law (State-Map equivalence)
impl = EigenvectorScatterWidgetImpl()
f = lambda s: s  # identity
assert impl.map(f).state.value == impl.with_state(f(impl.state.value)).state.value
```

---

## Branch Candidates

- **Parallel**: Performance benchmarking (defer to MEASURE)
- **Deferred**: NATS multi-client (Phase 7), K-gent integration (Phase 8)

---

## Entropy Budget

- Allocated: 0.05
- Draw: `void.entropy.sip(amount=0.05)`
- Purpose: Wiring experiments, marimo edge cases

---

## Continuation

On success: `⟿[QA]` — Gate quality before broader testing
On failure: `⟂[IMPLEMENT:blocked]` — Fix issues before proceeding

---

*Guard [phase=IMPLEMENT][entropy=0.05][law_check=true][minimal_output=true]*

---

## Auto-Inducer

⟿[IMPLEMENT]
/hydrate prompts/agent-town-phase6-implement.md
handles: scope=agent-town-phase6-marimo-scatter; compositions=SSE→model(scatter.js:464),click→cell(demo_marimo.py:371),functor_law(visualization.py:941); backlog=CP4-CP6; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:in_progress}; entropy=0.05
mission: code CP4-CP6 (marimo widget display, click→cell flow, integration tests); tests running in background; TodoWrite tracking.
actions: TodoWrite(chunks); Edit(demo_marimo.py:cell_dependencies); Edit(scatter.py:traitlet_sync); Write(test_marimo_integration.py); Bash(uv run pytest); Bash(uv run mypy).
exit: all checkpoints pass + tests green → ledger.IMPLEMENT=touched; QA notes captured; continuation → QA | any chunk incomplete → ⟂[IMPLEMENT:blocked].

---

**LAW**: This prompt auto-continues. The signifier `⟿[IMPLEMENT]` triggers immediate execution without human intervention. Halt conditions: implementation incomplete, tests failing, mypy errors, or `⟂[HUMAN_INTERRUPT]`.
