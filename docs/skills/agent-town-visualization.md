# Skill: Agent Town Visualization

> Visualize citizen eigenvectors, stream town events, and build real-time dashboards

**Difficulty**: Medium
**Prerequisites**: Understanding of Agent Town citizens, eigenvectors, coalitions
**Files Touched**: `agents/town/visualization.py`, API routes, dashboard components

---

## Overview

Agent Town visualization provides three main components:

1. **EigenvectorScatterWidget** - Project 7D citizen personality space to 2D scatter plots
2. **TownSSEEndpoint** - Stream town events to web clients via Server-Sent Events
3. **TownNATSBridge** - Publish/subscribe town events via NATS JetStream

All components follow functor laws and support graceful degradation.

---

## Quick Start

### ASCII Scatter Plot (CLI)

```python
from agents.town.visualization import (
    ScatterPoint,
    ScatterState,
    project_scatter_to_ascii,
)

# Create a point from citizen data
point = ScatterPoint(
    citizen_id="alice",
    citizen_name="Alice",
    archetype="builder",
    warmth=0.7,
    curiosity=0.8,
    trust=0.6,
    creativity=0.9,
    patience=0.5,
    resilience=0.4,
    ambition=0.3,
)

# Create state and render
state = ScatterState(points=(point,))
print(project_scatter_to_ascii(state))
```

Output:
```
+----------------------------------------------------------+
|                    Eigenvector Space (WT)                |
|                                                          |
|                    b                                     |
|                                                          |
+----------------------------------------------------------+
X: Warmth  |  Y: Trust
Legend: B=Builder
Citizens: 1/1
```

---

## EigenvectorScatterWidget

### Creating the Widget

```python
from agents.town.visualization import (
    EigenvectorScatterWidgetImpl,
    ProjectionMethod,
    ScatterState,
)

# Default state
widget = EigenvectorScatterWidgetImpl()

# With initial projection
widget = EigenvectorScatterWidgetImpl(
    initial_state=ScatterState(projection=ProjectionMethod.PCA)
)
```

### Loading Citizens

```python
from agents.town.citizen import Citizen
from agents.town.coalition import Coalition

# Load from existing citizen dict
widget.load_from_citizens(
    citizens={"alice": alice_citizen, "bob": bob_citizen},
    coalitions={"builders": builders_coalition},
    evolving_ids={"alice"},  # Mark evolving citizens
)
```

### Projecting to Targets

```python
from agents.i.reactive.widget import RenderTarget

# CLI (ASCII art)
ascii_output = widget.project(RenderTarget.CLI)

# JSON (for web APIs)
json_output = widget.project(RenderTarget.JSON)

# TUI (for Textual apps)
tui_output = widget.project(RenderTarget.TUI)
```

### State Mutations

```python
# Select a citizen (highlights in visualization)
widget.select_citizen("alice")

# Change projection method
widget.set_projection(ProjectionMethod.PAIR_CC)  # Curiosity vs Creativity

# Filter by archetype
widget.filter_by_archetype(("builder", "healer"))

# Toggle evolving-only view
widget.toggle_evolving_only()
```

### Functor Laws

The widget satisfies functor laws, enabling safe composition:

```python
# LAW 1: Identity
widget.map(lambda s: s)  # Returns identical widget

# LAW 2: Composition
f = lambda s: ScatterState(..., projection=ProjectionMethod.PCA)
g = lambda s: ScatterState(..., show_evolving_only=True)

# These are equivalent:
widget.map(f).map(g)
widget.map(lambda s: g(f(s)))

# LAW 3: State-Map Equivalence
widget.map(f) == widget.with_state(f(widget.state.value))
```

---

## Projection Methods

| Method | X Axis | Y Axis | Use Case |
|--------|--------|--------|----------|
| `PAIR_WT` | Warmth | Trust | Social dynamics |
| `PAIR_CC` | Curiosity | Creativity | Innovation potential |
| `PAIR_PR` | Patience | Resilience | Stability analysis |
| `PAIR_RA` | Resilience | Ambition | Growth trajectory |
| `PCA` | PC1 | PC2 | Maximum variance view |
| `TSNE` | t-SNE1 | t-SNE2 | Local structure |
| `CUSTOM` | User-defined | User-defined | Custom analysis |

---

## TownSSEEndpoint

Stream town events to web clients via Server-Sent Events.

### FastAPI Integration

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents.town.visualization import TownSSEEndpoint

app = FastAPI()

@app.get("/towns/{town_id}/events")
async def stream_events(town_id: str):
    endpoint = TownSSEEndpoint(town_id)
    return StreamingResponse(
        endpoint.generate(),
        media_type="text/event-stream",
    )
```

### Pushing Events

```python
endpoint = TownSSEEndpoint("town123")

# Push status updates
await endpoint.push_status({"day": 1, "phase": "MORNING"})

# Push eigenvector drift (for scatter animation)
await endpoint.push_eigenvector_drift(
    citizen_id="alice",
    old_eigenvectors={"warmth": 0.5, "trust": 0.5},
    new_eigenvectors={"warmth": 0.6, "trust": 0.6},
    drift_magnitude=0.14,
)

# Push coalition changes
await endpoint.push_coalition_change(coalition, "formed")
```

### SSE Event Format

```
event: town.status
data: {"day": 1, "phase": "MORNING"}

event: town.eigenvector.drift
data: {"citizen_id": "alice", "drift": 0.14, ...}

event: town.coalition.formed
data: {"coalition_id": "builders", "members": ["alice", "bob"]}
```

### Graceful Shutdown

```python
# Close endpoint when client disconnects
endpoint.close()
```

---

## TownNATSBridge

Publish/subscribe town events via NATS JetStream with memory fallback.

### Creating the Bridge

```python
from agents.town.visualization import TownNATSBridge

# Default (localhost:4222 with memory fallback)
bridge = TownNATSBridge()

# Custom servers
bridge = TownNATSBridge(
    servers=["nats://nats1:4222", "nats://nats2:4222"],
    fallback_to_memory=True,
)

# Connect
await bridge.connect()
```

### Context Manager

```python
async with TownNATSBridge() as bridge:
    await bridge.publish_status("town123", {"day": 1})
    # Auto-closes on exit
```

### Publishing Events

```python
# Status updates
await bridge.publish_status("town123", {"phase": "AFTERNOON"})

# Town events
await bridge.publish_town_event("town123", town_event)

# Eigenvector drift
await bridge.publish_eigenvector_drift(
    town_id="town123",
    citizen_id="alice",
    old_eigenvectors={"warmth": 0.5},
    new_eigenvectors={"warmth": 0.6},
)

# Coalition changes
await bridge.publish_coalition_change("town123", coalition, "formed")
```

### Subscribing

```python
# Subscribe to all events for a town
async for event in bridge.subscribe_town("town123"):
    print(event)

# Replay from beginning
async for event in bridge.subscribe_town("town123", from_beginning=True):
    print(event)
```

### NATS Subject Schema

```
town.{town_id}.{phase}.{operation}

Examples:
  town.abc123.morning.greet
  town.abc123.afternoon.trade
  town.abc123.status.phase_change
  town.abc123.coalition.formed
  town.abc123.eigenvector.drift

Wildcards:
  town.abc123.>         - All events for town
  town.abc123.morning.> - All morning events
  town.*.status.>       - Status events for all towns
```

### Memory Fallback

When NATS is unavailable, the bridge uses in-memory queues:

```python
bridge = TownNATSBridge(fallback_to_memory=True)
# Don't call connect() - stays in fallback mode

await bridge.publish_status("town123", {"test": True})
# Events queued in memory, accessible via subscribe_town()
```

---

## Visualization Characters

The ASCII scatter uses these characters:

| Character | Meaning |
|-----------|---------|
| `b`, `t`, `h`... | Archetype first letter (lowercase = unselected) |
| `B`, `T`, `H`... | Selected/hovered citizen (uppercase) |
| `○` | Bridge node (member of multiple coalitions) |
| `●` | Selected bridge node |
| `☆` | K-gent projection |
| `★` | Selected K-gent |

---

## Serialization

### ScatterPoint

```python
point = ScatterPoint(...)
d = point.to_dict()

# Reconstruct
restored = ScatterPoint(
    citizen_id=d["citizen_id"],
    citizen_name=d["citizen_name"],
    archetype=d["archetype"],
    warmth=d["eigenvectors"]["warmth"],
    # ... other eigenvectors
    x=d["x"],
    y=d["y"],
    color=d["color"],
    is_evolving=d["is_evolving"],
    coalition_ids=tuple(d["coalition_ids"]),
)
```

### ScatterState

```python
state = ScatterState(...)
d = state.to_dict()

# Contains:
# - type: "eigenvector_scatter"
# - points: list of point dicts
# - projection: enum name string
# - selected_citizen_id, filters, etc.
```

### ProjectionMethod Enum

```python
# Serialize
name = method.name  # "PAIR_CC"

# Deserialize
method = ProjectionMethod[name]
```

---

## Verification

```bash
# Run all visualization tests
uv run pytest agents/town/_tests/test_visualization_contracts.py -v

# Run law tests
uv run pytest agents/town/_tests/test_visualization_contracts.py -v -k "law"

# Run edge case tests
uv run pytest agents/town/_tests/test_visualization_contracts.py -v -k "SSE or NATS or Roundtrip"
```

---

## Common Pitfalls

1. **Forgetting to close SSE endpoints**: Always call `endpoint.close()` when clients disconnect to prevent resource leaks.

2. **Assuming NATS is available**: Use `fallback_to_memory=True` for graceful degradation in development/testing.

3. **Mutating frozen dataclasses**: `ScatterPoint` and `ScatterState` are frozen. Use `widget.map()` or create new instances.

4. **Ignoring projection bounds**: PCA/t-SNE coordinates may be outside [0,1]. The ASCII projection normalizes from [-2,2].

5. **Enum identity comparison**: After reload, use `method.value` or `method.name` for comparison, not `is`.

---

## Related Skills

- [building-agent](building-agent.md) - Creating Agent[A, B]
- [polynomial-agent](polynomial-agent.md) - State-dependent agents (CitizenPolynomial)
- [flux-agent](flux-agent.md) - Stream processing (TownFlux)

---

## Phase 6: Live Marimo Notebook (RESEARCH)

This section documents the technical research for implementing a live marimo notebook
with eigenvector scatter visualization and SSE updates.

### Anywidget Pattern: SVG Scatter

**Decision**: Use SVG over Canvas for the scatter plot.

**Rationale**:
- Native click handling per element (no hit-testing)
- CSS transitions work directly (`transition: all 0.3s ease-out`)
- Text elements for labels with proper anchoring
- `:hover` pseudo-class works on SVG elements
- Adequate performance for 25-100 citizens

**Structure**:
```javascript
function renderScatter(el, state) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 400 300");

  state.points.forEach(point => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", point.x * 380 + 10);
    circle.setAttribute("cy", (1 - point.y) * 280 + 10);
    circle.setAttribute("r", point.size * 8 + 4);
    circle.style.transition = "all 0.3s ease-out";
    circle.onclick = () => selectCitizen(point.citizen_id);
    svg.appendChild(circle);
  });
}
```

### SSE Client Pattern

**EventSource with typed events**:
```javascript
function connectSSE(model, townId) {
  const eventSource = new EventSource(`/v1/town/${townId}/events`);

  eventSource.addEventListener('town.eigenvector.drift', (e) => {
    const data = JSON.parse(e.data);
    updatePointPosition(model, data);
  });

  eventSource.addEventListener('town.status', (e) => {
    model.set('town_status', JSON.parse(e.data));
    model.save_changes();
  });

  // Browser auto-reconnects after ~3 seconds
  return () => eventSource.close();  // Cleanup function
}
```

### Marimo Notebook Structure

Marimo notebooks are **pure Python files**, not .ipynb:

```python
# agents/town/demo_marimo.py
import marimo
app = marimo.App()

@app.cell
def __():
    import marimo as mo
    from agents.i.marimo.widgets import EigenvectorScatterWidget
    return mo, EigenvectorScatterWidget

@app.cell
def __(mo, EigenvectorScatterWidget):
    scatter = EigenvectorScatterWidget(town_id="abc123")
    widget = mo.ui.anywidget(scatter)
    return widget

@app.cell
def __(widget):
    widget  # Display (reactive)

@app.cell
def __(mo):
    projection = mo.ui.dropdown(
        options=["PAIR_WT", "PAIR_CC", "PCA"],
        value="PAIR_WT"
    )
    return projection
```

### Integration File Map

| File | Purpose |
|------|---------|
| `agents/i/marimo/widgets/js/scatter.js` | SVG scatter ESM with SSE client |
| `agents/i/marimo/widgets/scatter.py` | EigenvectorScatterWidgetMarimo |
| `agents/town/demo_marimo.py` | Live notebook demo |

### SSE Event Flow

```
API (/v1/town/{id}/events)     scatter.js ESM           Python traitlets
         |                          |                          |
         |-- town.eigenvector.drift |                          |
         |                          | model.set('points', new) |
         |                          | model.save_changes()     |
         |                          |------------------------->|
         |                          |                          | marimo re-renders
```

### Sources

- [EventSource Basics (web.dev)](https://web.dev/articles/eventsource-basics)
- [SSE 2025 Patterns](https://portalzine.de/sses-glorious-comeback-why-2025-is-the-year-of-server-sent-events/)
- [mo.ui.anywidget API](https://docs.marimo.io/api/inputs/anywidget/)
- [anywidget Getting Started](https://anywidget.dev/en/getting-started/)

---

## Phase 6: Live Marimo Demo (EDUCATE)

This section documents the implemented live marimo visualization demo.

### Running the Demo

```bash
# Start the API server first (required for SSE)
uv run uvicorn protocols.api.app:app --reload

# Launch the marimo notebook
marimo edit agents/town/demo_marimo.py

# Or run as script
marimo run agents/town/demo_marimo.py
```

### Demo Features

| Feature | Description | Cell |
|---------|-------------|------|
| Town creation | Create Phase 3 or 4 towns via API | Cell 7 |
| Projection selection | Switch between PAIR_WT, PAIR_CC, PCA, etc. | Cell 5 |
| Citizen filtering | Filter by archetype, evolving status | Cell 6 |
| Live scatter | SVG plot with CSS transitions | Cell 11 |
| Click-to-details | Click citizen → fetch LOD 2 details | Cell 12 |
| Simulation stepping | Advance by 1-10 cycles | Cell 13 |
| SSE status | Connection indicator in footer | Cell 14 |

### Cell DAG (Law L1)

```
imports → widget_imports → create_widget → town_controls
                                        → projection_controls
                                        → filter_controls
                                        → simulation_controls
                                        → main_layout
```

Marimo enforces pure functions per cell. Circular dependencies are compile-time errors.

### Reactivity Laws

| Law | Trigger | Effect |
|-----|---------|--------|
| L2 | `town_id_input.value` change | Cell 8 re-runs → SSE reconnects |
| L3 | `widget.clicked_citizen_id` change | Cell 12 re-runs → details fetched |
| L4 | All async cells use `await` | No blocking; marimo handles concurrency |

### Widget Architecture

```
EigenvectorScatterWidgetMarimo (Python)
    ↓ traitlets.tag(sync=True)
scatter.js ESM (JavaScript)
    ↓ model.set() + model.save_changes()
marimo re-render
```

The widget bridges Python state to JavaScript via anywidget's traitlet sync protocol.

### SSE Integration

```javascript
// scatter.js handles SSE connection
eventSource.addEventListener('town.eigenvector.drift', (e) => {
  const data = JSON.parse(e.data);
  // Update point position → CSS transition animates
  model.set('points', updatedPoints);
  model.save_changes();
});
```

Browser auto-reconnects on disconnect (EventSource spec). The widget shows status via `sse_connected` traitlet.

### Teaching Example: Functor Laws in Tests

```python
# From test_functor.py — verification pattern

def test_identity_law_passes(self) -> None:
    """Test identity law: F(id) = id.

    The identity operation maps to SENSE (neutral phase).
    Applying the functor twice yields the same result.
    """
    result = verify_identity_law()
    assert result.status == LawStatus.PASSED

def test_composition_law_act_act(self) -> None:
    """Test composition: F(f >> g) = F(f) >> F(g).

    If greet and gossip both map to ACT,
    their composition must also be valid in ACT.
    """
    result = verify_composition_law("greet", "gossip")
    assert result.status == LawStatus.PASSED

def test_composition_law_reflect_act_fails(self) -> None:
    """Test invalid composition: REFLECT >> ACT fails.

    Phase transitions must be forward: SENSE → ACT → REFLECT.
    Going backward violates the N-Phase operad laws.
    """
    result = verify_composition_law("solo", "greet")
    assert result.status == LawStatus.FAILED
```

### Teaching Example: Widget State Map Equivalence

```python
# The functor law for widgets

def test_state_map_equivalence(widget: EigenvectorScatterWidgetImpl) -> None:
    """Test: widget.map(f) ≡ widget.with_state(f(state)).

    This law ensures that:
    1. Mapping a function over the widget
    2. Is the same as applying that function to state

    Enables filter composition without mutating widget.
    """
    f = lambda s: ScatterState(points=s.points, show_evolving_only=True)

    # These must be equivalent:
    result_via_map = widget.map(f)
    result_via_state = widget.with_state(f(widget.state.value))

    assert result_via_map.state.value == result_via_state.state.value
```

### Teaching Example: Graceful Degradation

```python
# From demo_marimo.py — handle API failures gracefully

async def connect_town(town_id_input, scatter, fetch_scatter_data):
    """Connect to existing town when town_id_input changes."""
    if town_id_input.value and town_id_input.value != scatter.town_id:
        try:
            scatter_data = await fetch_scatter_data(town_id_input.value)
            scatter.points = scatter_data.get("points", [])
            scatter.town_id = town_id_input.value
        except Exception:
            pass  # Silently fail for invalid town IDs
    return ()
```

The pattern: try the operation, catch exceptions, maintain previous state. Users see no crash; the widget simply doesn't update.

### Verification Commands

```bash
# Run all Phase 6 tests
uv run pytest agents/town/_tests/test_visualization_contracts.py -v
uv run pytest agents/town/_tests/test_functor.py -v
uv run pytest agents/town/_tests/test_marimo_integration.py -v

# Check functor laws specifically
uv run pytest agents/town/_tests/test_functor.py -v -k "law"

# Full town test suite
uv run pytest agents/town/_tests/ -v --tb=short
```

### Performance Baselines

| Metric | Value | Notes |
|--------|-------|-------|
| Render (25 citizens) | 0.03ms p50 | Measure before optimizing |
| SSE connection | <100ms | Localhost; production varies |
| CSS transition | 300ms | `ease-out` curve |
| Test suite | 1.36s | 529 tests |

---

## Changelog

- 2025-12-14: Phase 6 EDUCATE - Teaching examples, demo guide, verification commands
- 2025-12-14: Phase 6 RESEARCH - Live marimo notebook patterns
- 2025-12-14: Initial version (Phase 5 EDUCATE)
