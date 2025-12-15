---
path: docs/skills/n-phase-cycle/agent-town-phase6-develop
status: active
progress: 60
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables:
  - agents/town/demo_marimo.py
  - agents/i/marimo/widgets/scatter.py
  - agents/i/marimo/widgets/js/scatter.js
session_notes: |
  Phase 6: Live marimo notebook with eigenvector scatter and SSE updates.
  DEVELOP COMPLETE: All three contracts drafted with implementation code.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.06
  remaining: 0.04
---

# Agent Town Phase 6: DEVELOP

> Design contracts for live marimo eigenvector scatter with SSE integration.

**Scope**: `agents/town/demo_marimo.py`, `agents/i/marimo/widgets/scatter.py`, ESM module
**Heritage**: S1=visualization.py, S2=stigmergic_field.js, S3=marimo_widget.py, S4=town.py API
**Prerequisite**: RESEARCH complete (see `docs/skills/agent-town-visualization.md` Phase 6)

---

## ATTACH

/hydrate

You are entering DEVELOP phase for Agent Town Phase 6 (AD-005 N-Phase Cycle).

## Context from RESEARCH

**Files Mapped**:
- `agents/town/visualization.py` — ScatterState, ScatterPoint, EigenvectorScatterWidgetImpl, TownSSEEndpoint
- `agents/i/reactive/adapters/marimo_widget.py` — MarimoAdapter pattern
- `agents/i/marimo/widgets/base.py` — KgentsWidget base class
- `agents/i/marimo/widgets/js/stigmergic_field.js` — Canvas + entity layer pattern
- `protocols/api/town.py` — /events SSE endpoint, /scatter JSON endpoint

**Key Decisions from RESEARCH**:
1. **SVG over Canvas**: Native click handling, CSS transitions, adequate for 25-100 points
2. **EventSource API**: Browser auto-reconnects, typed event listeners
3. **Marimo structure**: Pure Python `.py` files with `@app.cell` decorators
4. **Traitlet sync**: `model.set()` + `model.save_changes()` for JS→Python

**Invariants Discovered**:
- `mo.ui.anywidget(widget)` wraps for marimo reactivity
- ESM must export `{ render }` as default
- State via `model.get("property")` / `model.on("change:property", cb)`
- Cleanup function returned from `render()` for EventSource close

**Blockers**: None identified

---

## Your Mission

Design three contracts that compose to deliver live scatter visualization:

### Contract 1: EigenvectorScatterWidgetMarimo

```python
class EigenvectorScatterWidgetMarimo(KgentsWidget):
    """Live scatter plot with SSE integration for marimo."""

    _esm = Path(__file__).parent / "js" / "scatter.js"

    # Connection
    town_id: Unicode        # Town to connect to
    api_base: Unicode       # API base URL (default: /v1/town)

    # Scatter state (synced to JS)
    points: List[Dict]      # ScatterPoint.to_dict() for each citizen
    projection: Unicode     # ProjectionMethod name
    selected_citizen_id: Unicode
    hovered_citizen_id: Unicode

    # SSE status
    sse_connected: Bool
    sse_error: Unicode

    # Interaction (set from JS)
    clicked_citizen_id: Unicode

    # Methods
    def connect_to_town(self, town_id: str) -> None: ...
    def set_projection(self, method: ProjectionMethod) -> None: ...
    def load_from_widget(self, impl: EigenvectorScatterWidgetImpl) -> None: ...
```

**Laws**:
- L1: `widget.points` serialization matches `ScatterPoint.to_dict()` schema
- L2: `sse_connected` reflects actual EventSource state
- L3: `clicked_citizen_id` update triggers marimo cell re-run

### Contract 2: scatter.js ESM Module

```javascript
// Export signature
export default { render };

// Render function signature
function render({ model, el }) {
  // Returns cleanup function for EventSource
  return () => { eventSource.close(); };
}

// State properties accessed
model.get("town_id")           // → connect SSE
model.get("api_base")          // → construct URL
model.get("points")            // → render SVG circles
model.get("projection")        // → axis labels
model.get("selected_citizen_id")
model.get("hovered_citizen_id")

// State properties set
model.set("clicked_citizen_id", id)
model.set("sse_connected", bool)
model.set("sse_error", msg)
model.save_changes()

// Event subscriptions
model.on("change:points", renderPoints)
model.on("change:projection", renderAxes)
model.on("change:selected_citizen_id", updateSelection)
```

**Laws**:
- L1: SVG viewBox maintains aspect ratio (400x300)
- L2: Point transitions animate via CSS (`transition: all 0.3s ease-out`)
- L3: Click → `model.set("clicked_citizen_id")` → `model.save_changes()`
- L4: SSE disconnect → auto-reconnect by browser EventSource

### Contract 3: demo_marimo.py Notebook

```python
# Cell 1: Imports
import marimo as mo
from agents.i.marimo.widgets import EigenvectorScatterWidgetMarimo
from agents.town.visualization import ProjectionMethod

# Cell 2: Create widget
scatter = EigenvectorScatterWidgetMarimo(town_id="", api_base="/v1/town")
widget = mo.ui.anywidget(scatter)

# Cell 3: Town selector
towns = await fetch_available_towns()
town_select = mo.ui.dropdown(options=towns, label="Town")

# Cell 4: Projection selector
projection = mo.ui.dropdown(
    options=[m.name for m in ProjectionMethod],
    value="PAIR_WT",
    label="Projection"
)

# Cell 5: Reactive connection (depends on town_select)
scatter.connect_to_town(town_select.value)

# Cell 6: Reactive projection (depends on projection)
scatter.set_projection(ProjectionMethod[projection.value])

# Cell 7: Display scatter
widget

# Cell 8: Citizen details (depends on widget.clicked_citizen_id)
if widget.clicked_citizen_id:
    details = await fetch_citizen_details(widget.clicked_citizen_id)
    mo.md(f"**{details['name']}** ({details['archetype']})")
```

**Laws**:
- L1: Cells form DAG (no circular dependencies)
- L2: `town_select.value` change → Cell 5 re-runs → SSE reconnects
- L3: `widget.clicked_citizen_id` change → Cell 8 re-runs

---

## Attention Budget

| Component | Allocation |
|-----------|------------|
| scatter.py contract | 30% |
| scatter.js ESM contract | 40% |
| demo_marimo.py structure | 20% |
| Edge cases / error handling | 10% |

---

## Exit Criteria

- [x] EigenvectorScatterWidgetMarimo contract with traitlets defined
- [x] scatter.js ESM contract with render signature and state protocol
- [x] demo_marimo.py cell structure with reactive dependencies
- [x] Laws stated for each contract
- [x] SVG structure documented (viewBox, layers, transitions)
- [x] SSE event→model update flow documented
- [x] Risks/unknowns captured

---

## SSE → Model → Render Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          SSE → MODEL → RENDER FLOW                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐        ┌──────────────┐        ┌─────────────────┐     │
│  │   API       │  SSE   │   scatter.js │ model. │   SVG           │     │
│  │   /events   │───────▶│   EventSource│───────▶│   renderPoints()│     │
│  └─────────────┘        └──────────────┘  set() └─────────────────┘     │
│        │                       │                        │               │
│        │                       │                        ▼               │
│        │                       │                 ┌─────────────┐        │
│        │                       │                 │ <circle>    │        │
│        │                       │                 │ CSS animate │        │
│        │                       │                 └─────────────┘        │
│        │                       │                        │               │
│        │                       ▼                        │               │
│        │               ┌──────────────┐                 │               │
│        │               │ Traitlet     │                 │               │
│        │               │ sync to      │◀────────────────┘               │
│        │               │ Python       │ model.save_changes()            │
│        │               └──────────────┘                                 │
│        │                       │                                        │
│        │                       ▼                                        │
│        │               ┌──────────────┐                                 │
│        │               │ Marimo cell  │                                 │
│        │               │ re-execution │                                 │
│        │               └──────────────┘                                 │
│        │                                                                │
└────────┴────────────────────────────────────────────────────────────────┘

Event Types:
  town.eigenvector.drift → Update point coordinates → Animate transition
  town.status            → Update status bar
  town.coalition.*       → Re-color affected points

Click Flow:
  1. User clicks SVG circle
  2. scatter.js: model.set("clicked_citizen_id", id)
  3. scatter.js: model.save_changes()
  4. Traitlet syncs to Python scatter.clicked_citizen_id
  5. Marimo detects change, re-runs dependent cells
  6. Citizen details cell fetches and displays data
```

---

## Consolidated Laws

| Module | Law | Description |
|--------|-----|-------------|
| scatter.py | L1 | `points` serialization matches ScatterPoint.to_dict() schema |
| scatter.py | L2 | `sse_connected` reflects actual EventSource state |
| scatter.py | L3 | `clicked_citizen_id` update triggers marimo cell re-run |
| scatter.js | L4 | SVG viewBox maintains 400x300 aspect ratio |
| scatter.js | L5 | Point transitions animate via CSS (0.3s ease-out) |
| scatter.js | L6 | Click → model.set() → model.save_changes() |
| scatter.js | L7 | SSE disconnect → browser auto-reconnect via EventSource |
| scatter.js | L8 | Cleanup function closes EventSource on unmount |
| demo_marimo.py | L9 | Cells form DAG (no circular dependencies) |
| demo_marimo.py | L10 | town_id change → SSE reconnects |
| demo_marimo.py | L11 | clicked_citizen_id change → details cell re-runs |

---

## Risks Captured

| Risk | Mitigation | Status |
|------|------------|--------|
| SSE cleanup on widget close | Cleanup function returned from render() | ✓ Implemented |
| Marimo cell ordering | Explicit cell dependency via variable access | ✓ Implemented |
| Point count scaling (>100) | SVG adequate for 25-100; virtualize if needed later | Deferred |
| Projection animation | CSS transitions on cx/cy attributes | ✓ Implemented |

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `agents/i/marimo/widgets/scatter.py` | ~200 | Widget contract with traitlets |
| `agents/i/marimo/widgets/js/scatter.js` | ~400 | ESM render with SVG + SSE |
| `agents/town/demo_marimo.py` | ~350 | Marimo notebook structure |

---

## Actions Completed

1. ✓ Draft `EigenvectorScatterWidgetMarimo` class with traitlets
2. ✓ Draft `scatter.js` render function with SVG structure
3. ✓ Draft `demo_marimo.py` cell structure
4. ✓ Document SSE→model→render data flow
5. ✓ State laws and verify composability with existing widgets
6. ✓ Log metrics

---

## Exit Signifier (LAW)

Upon completing DEVELOP:

```
⟿[STRATEGIZE]
/hydrate
handles: contracts=scatter.py,scatter.js,demo_marimo.py; laws=9; risks=4; ledger={DEVELOP:touched}; entropy=0.04
mission: order implementation chunks; identify parallel tracks; set checkpoints
actions: dependency graph; owner assignment; interface contracts for parallel work
exit: ordered backlog + checkpoints; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE
```

Halt conditions:
```
⟂[BLOCKED:composition_failure] Widget cannot compose with existing MarimoAdapter
⟂[BLOCKED:sse_incompatible] EventSource pattern incompatible with anywidget lifecycle
⟂[ENTROPY_DEPLETED] Budget exhausted
```

---

Guard [phase=DEVELOP][entropy=0.07][law_check=true][minimal_output=true]

---

## Auto-Inducer

⟿[STRATEGIZE]
/hydrate
handles: contracts=scatter.py,scatter.js,demo_marimo.py; laws=11; risks=4; files=3; lines=~950
mission: order implementation chunks; identify parallel tracks; set checkpoints for IMPLEMENT
actions: dependency graph; integration test plan; widget init wiring
exit: ordered backlog + checkpoints; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE

---

## Changelog

- 2025-12-14: Initial creation from RESEARCH phase completion
- 2025-12-14: DEVELOP complete — 3 contracts drafted with implementation code, 11 laws, 4 risks mitigated
