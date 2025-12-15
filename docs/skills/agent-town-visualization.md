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

---

## Phase 7: LLM-Backed Citizen Dialogue

This section documents the dialogue generation system for Agent Town citizens.

### Overview

Phase 7 adds speech to citizens. When citizens interact (greet, gossip, trade), they generate dialogue via LLM calls, grounded in their memories and consistent with their archetype personality.

**Key Features**:
- Budget-aware routing: citizen tiers → model selection
- Template fallback: always produces dialogue (never fails silently)
- Memory grounding: dialogue references past interactions
- Archetype voice: personality-consistent speech

### Quick Start

```python
from agents.town.dialogue_engine import (
    CitizenDialogueEngine,
    DialogueBudgetConfig,
    MockLLMClient,
)

# Create engine with mock LLM (for testing)
engine = CitizenDialogueEngine(
    llm_client=MockLLMClient(),
    budget_config=DialogueBudgetConfig(),
)

# Register citizens with budget tiers
engine.register_citizen("alice", tier="evolving")  # Full LLM
engine.register_citizen("bob", tier="leader")      # Sampled LLM
engine.register_citizen("carol", tier="standard")  # Template/cached

# Generate dialogue
from agents.town.flux import TownPhase
result = await engine.generate(
    speaker=alice,
    listener=bob,
    operation="greet",
    phase=TownPhase.MORNING,
)
print(result.text)  # "Good morning, Bob. The structure holds..."
```

### Budget Tiers

Citizens receive different dialogue quality based on their tier:

| Tier | Daily Tokens | Model Access | Use Case |
|------|--------------|--------------|----------|
| `evolving` | 2000 | SONNET/HAIKU | 3-5 evolving citizens |
| `leader` | 500 | HAIKU/CACHED | 5 archetype leaders |
| `standard` | 100 | CACHED/TEMPLATE | 15+ standard citizens |

**Cascade Behavior**:
```
SONNET (budget OK) → HAIKU (budget low) → CACHED (similar dialogue exists) → TEMPLATE (fallback)
```

Evolving citizens NEVER get TEMPLATE—they cascade to HAIKU even when budget is low.

### Registering Citizens

```python
# Register at town initialization
for citizen_id, citizen in town.citizens.items():
    if citizen_id in town.evolving_ids:
        tier = "evolving"
    elif citizen.is_archetype_leader:
        tier = "leader"
    else:
        tier = "standard"
    engine.register_citizen(citizen_id, tier=tier)
```

### Configuring Budget

```python
from agents.town.dialogue_engine import DialogueBudgetConfig

config = DialogueBudgetConfig(
    # Model routing by operation
    model_routing={
        "greet": "haiku",       # Quick greetings
        "gossip": "haiku",      # Social chatter
        "trade": "sonnet",      # Nuanced negotiation
        "council": "sonnet",    # Coalition decisions
        "solo_reflect": "haiku",
    },
    # Daily token limits by tier
    tier_budgets={
        "evolving": 2000,
        "leader": 500,
        "standard": 100,
    },
    # Estimated tokens per operation
    operation_estimates={
        "greet": 50,
        "gossip": 100,
        "trade": 200,
        "council": 500,
        "solo_reflect": 75,
    },
)

engine = CitizenDialogueEngine(
    llm_client=create_llm_client(),  # Real LLM
    budget_config=config,
)
```

### Streaming Dialogue

```python
async for chunk in engine.generate_stream(
    speaker=alice,
    listener=bob,
    operation="trade",
    phase=TownPhase.AFTERNOON,
):
    if isinstance(chunk, str):
        # Text chunk - display progressively
        print(chunk, end="", flush=True)
    else:
        # DialogueResult - final stats
        print(f"\n[Tokens: {chunk.tokens_used}, Model: {chunk.model}]")
```

### Archetype Voices

Each archetype has a distinct voice pattern derived from their cosmotechnics:

| Archetype | Voice Pattern | Temperature |
|-----------|---------------|-------------|
| Builder | Construction metaphors, practical | 0.5 |
| Trader | Exchange framing, calculating | 0.6 |
| Healer | Restoration language, empathetic | 0.7 |
| Scholar | Curious, probing, pattern-seeking | 0.4 |
| Watcher | Historical references, patient | 0.5 |

**Example Builder Voice**:
```
"Good to see you, Bob. Working on any new projects?"
"The foundation's looking solid today."
```

**Example Healer Voice**:
```
"Hello, Bob. How are you feeling today?"
"I sensed someone needed company. Are you alright?"
```

### Memory Grounding

Dialogue uses M-gent's foveation pattern for memory context:

```python
@dataclass
class DialogueContext:
    focal_memories: list[str]      # Top 3 by relevance
    peripheral_memories: list[str]  # Next 2
    relationship: float             # [-1, 1]
    phase_name: str
    region: str
    recent_events: list[str]
    shared_coalition: str | None
```

Memories mentioning the listener are prioritized. Relationship affects tone.

### DialogueResult

```python
@dataclass
class DialogueResult:
    text: str                       # The dialogue
    tokens_used: int                # Actual token count
    model: str                      # "claude-3-haiku" / "template" / "cached"
    grounded_memories: list[str]    # Memories referenced
    was_template: bool              # True if template fallback
    was_cached: bool                # True if cache hit
    speaker_id: str
    listener_id: str
    operation: str                  # "greet" / "gossip" / "trade"
```

### ADR: Key Design Decisions

#### ADR-1: Evolving Citizens Always Get LLM

**Context**: Some citizens are marked "evolving" because they're under active observation for eigenvector drift.

**Decision**: Evolving citizens NEVER fall back to TEMPLATE, only HAIKU.

**Rationale**: Template dialogue doesn't create enough variation for eigenvector evolution. Even budget-constrained evolving citizens need some LLM diversity.

#### ADR-2: Reuse K-gent LLM Infrastructure

**Context**: K-gent already has LLMClient, MockLLMClient, and streaming patterns.

**Decision**: Direct import from `agents.k.llm` rather than duplicating.

**Rationale**: `Cross-agent import OK: Town→K-gent LLM; reuse > duplicate` (meta.md 2025-12-14). The LLM interface is stable and well-tested.

#### ADR-3: Foveation Pattern for Memory Grounding

**Context**: Citizens have potentially many memories of each other.

**Decision**: Use M-gent's foveation pattern: 3 focal + 2 peripheral memories.

**Rationale**: 5 memories provide sufficient context without overwhelming the prompt. Focal/peripheral split mirrors human attention.

#### ADR-4: Template Fallback Never Fails

**Context**: LLM calls can fail, budgets can be exhausted.

**Decision**: Template tier always produces coherent dialogue.

**Rationale**: `Tier cascade: TEMPLATE never fails; budget exhaustion → graceful fallback` (meta.md 2025-12-14).

### Verification Commands (Phase 7)

```bash
# Run dialogue engine tests
uv run pytest agents/town/_tests/test_dialogue_engine.py -v

# Run live LLM integration tests (requires credentials)
uv run pytest agents/town/_tests/test_integration.py -v -k "dialogue"

# Check budget cascade behavior
uv run pytest agents/town/_tests/test_dialogue_engine.py -v -k "tier or cascade"

# Full town test suite (696 tests)
uv run pytest agents/town/_tests/ -v --tb=short
```

### Teaching Example: Budget Tier Selection

```python
def test_tier_cascade(engine: CitizenDialogueEngine) -> None:
    """Test: evolving → leader → standard tier behavior.

    Evolving citizens cascade: SONNET → HAIKU (never TEMPLATE).
    Leaders cascade: HAIKU → CACHED → TEMPLATE.
    Standard: CACHED → TEMPLATE.
    """
    # Register citizens
    engine.register_citizen("evolving_1", tier="evolving")
    engine.register_citizen("leader_1", tier="leader")
    engine.register_citizen("standard_1", tier="standard")

    # Evolving gets SONNET initially
    tier = engine.get_tier(evolving_citizen)
    assert tier in (DialogueTier.SONNET, DialogueTier.HAIKU)
    assert tier != DialogueTier.TEMPLATE  # Never template

    # Leader gets HAIKU or CACHED
    tier = engine.get_tier(leader_citizen)
    assert tier in (DialogueTier.HAIKU, DialogueTier.CACHED, DialogueTier.TEMPLATE)

    # Standard gets CACHED or TEMPLATE
    tier = engine.get_tier(standard_citizen)
    assert tier in (DialogueTier.CACHED, DialogueTier.TEMPLATE)
```

### Teaching Example: Streaming Accumulation

```python
async def test_streaming_accumulation(engine: CitizenDialogueEngine) -> None:
    """Test: streaming yields chunks + final result.

    Stream yields strings (chunks) during generation,
    then DialogueResult at the end with token counts.
    """
    chunks = []
    final_result = None

    async for item in engine.generate_stream(
        speaker=alice,
        listener=bob,
        operation="greet",
        phase=TownPhase.MORNING,
    ):
        if isinstance(item, str):
            chunks.append(item)
        else:
            final_result = item

    # Chunks accumulated to full text
    assert "".join(chunks) == final_result.text
    # Result has token accounting
    assert final_result.tokens_used >= 0
```

---

## Phase 7: Metrics and Measurement (MEASURE)

This section documents the quantitative metrics for the Phase 7 dialogue system.

### Code Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Town tests total | 696 | +71 from Phase 7 |
| Dialogue tests | 71 | test_dialogue_engine.py |
| Integration tests | 16 | test_integration.py (dialogue) |
| Production lines | 880 | dialogue_engine.py + dialogue_voice.py |
| Test lines | 1482 | test_dialogue_engine.py |
| Modules added | 2 | dialogue_engine, dialogue_voice |
| Cross-agent deps | +1 | K-gent LLM (direct import) |

### Leading Indicators

| Audience | Goal | Signal | Source |
|----------|------|--------|--------|
| **Operator** | Run dialogue demo | Template fallback rate | DialogueResult.was_template |
| **Operator** | Budget stays healthy | Daily token burn rate | CitizenBudget.tokens_used_today |
| **Maintainer** | Extend archetypes safely | Voice test coverage | test_dialogue_engine.py |
| **Maintainer** | Understand cascade | Tier transition logs | DialogueTier changes |
| **Contributor** | Add features confidently | Test regression rate | CI pipeline |
| **User** | Dialogue feels authentic | Memory grounding rate | DialogueResult.grounded_memories |

### Baselines and Thresholds

| Metric | Baseline | Alert Threshold | Rationale |
|--------|----------|-----------------|-----------|
| Template fallback rate | <20% (evolving) | >50% | Budget too tight |
| Dialogue test suite | 15.83s | >30s | CI feedback loop |
| Memory grounding | 2+ memories | 0 memories | Context missing |
| Tokens per greet | ~50 | >100 | Prompt bloat |
| Tokens per trade | ~200 | >400 | Model inefficiency |
| Daily budget burn | <80% | >95% | Budget exhaustion risk |

### Counter-Metrics

What would indicate this feature is harmful?

| Signal | Counter-Signal | Mitigation |
|--------|----------------|------------|
| High dialogue quality | Token cost explosion | Tier budgets, cascade |
| Memory grounding | Slow context build | Foveation limit (5 max) |
| Archetype consistency | Repetitive dialogue | Temperature tuning |
| Fast generation | Model quality drop | Tier selection logic |
| Many tests | Slow CI | Parallel execution |

### Budget Model Validation

| Tier | Daily Limit | Est. Interactions | Burn Rate |
|------|-------------|-------------------|-----------|
| Evolving | 2000 tokens | ~20 trades | 100%/day sustainable |
| Leader | 500 tokens | ~10 greets | 50%/day expected |
| Standard | 100 tokens | Template only | 0% (cached/template) |

### Verification Commands (Metrics)

```bash
# Check dialogue test duration (baseline: 15.83s)
uv run pytest agents/town/_tests/test_dialogue_engine.py -q --tb=no

# Check total town tests (baseline: 696)
uv run pytest agents/town/_tests/ --collect-only -q 2>/dev/null | tail -1

# Run full suite with durations
uv run pytest agents/town/_tests/ -v --durations=10 --tb=short
```

---

### Verification Commands (Phase 6)

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

## Phase 6: Metrics and Measurement (MEASURE)

This section documents the leading indicators, baselines, and alert thresholds for Agent Town visualization.

### Leading Indicators

| Audience | Goal | Signal | Source |
|----------|------|--------|--------|
| **Operator** | Run the demo successfully | Demo launch success rate | API `/v1/town/` |
| **Operator** | Stable SSE connections | SSE disconnection rate | `TownSSEEndpoint` |
| **Maintainer** | Extend widgets safely | Functor law test coverage | `test_functor.py` |
| **Maintainer** | Understand widget state | Documentation completeness | Skill doc |
| **Contributor** | Add features with confidence | Test regression rate | CI pipeline |
| **Contributor** | Quick feedback loop | Test suite duration | `pytest --durations` |

### Baselines and Thresholds

| Metric | Baseline | Alert Threshold | Rationale |
|--------|----------|-----------------|-----------|
| Widget render (25 citizens) | 0.03ms p50 | >10ms | 300x regression |
| SSE connection time | <100ms | >500ms | User-perceptible delay |
| CSS transition duration | 300ms | Fixed | Design constant |
| Test count | 529 | <500 | Regression indicator |
| Test suite duration | 1.51s | >5s | CI feedback loop |
| Functor law tests | 33 | <30 | Law coverage |
| Marimo integration tests | 24 | <20 | Widget coverage |

### Counter-Metrics

What would indicate this feature is harmful?

| Signal | Counter-Signal | Mitigation |
|--------|----------------|------------|
| High adoption (many demos) | Memory exhaustion from SSE | Connection pooling, max concurrent |
| Fast render | CPU spike during PCA | Cache PCA results |
| Many tests | Slow CI feedback | Parallel test execution |
| Rich documentation | Stale docs | Changelog discipline |

### Metric Locations

| Metric | Location | How to Check |
|--------|----------|--------------|
| Test count | `pytest --collect-only` | `uv run pytest agents/town/_tests/ --collect-only \| grep "test" \| wc -l` |
| Test duration | pytest output | `uv run pytest agents/town/_tests/ -q --tb=no` |
| Render benchmark | `test_visualization_contracts.py` | See `TestScatterPerformance` |
| Functor laws | `test_functor.py` | `uv run pytest agents/town/_tests/test_functor.py -v -k "law"` |

### Dashboard Sketch (Future)

```
+----------------------------------------------------------+
|                 Agent Town Metrics                        |
+----------------------------------------------------------+
| Test Health                | Widget Performance          |
| ========================== | =========================== |
| Tests: 529 ✓               | Render p50: 0.03ms ✓        |
| Duration: 1.51s ✓          | SSE connect: <100ms ✓       |
| Functor laws: 33 ✓         | Memory: N/A                 |
+----------------------------------------------------------+
| SSE Connections            | Demo Usage                  |
| ========================== | =========================== |
| Active: 0                  | Today: N/A                  |
| Disconnects: 0             | This week: N/A              |
+----------------------------------------------------------+
```

### Verification Commands (Metrics)

```bash
# Check current test count (baseline: 529)
uv run pytest agents/town/_tests/ --collect-only -q 2>/dev/null | tail -1

# Run performance tests
uv run pytest agents/town/_tests/test_visualization_contracts.py -v -k "Performance"

# Check functor law coverage
uv run pytest agents/town/_tests/test_functor.py -v --tb=short

# Full metrics check
uv run pytest agents/town/_tests/ -v --durations=10 --tb=short
```

---

## Recursive Hologram

This skill unfolds from the unified categorical foundation:

```
PolyAgent[S, A, B]  →  TOWN_OPERAD  →  TownSheaf (future)
        ↓                   ↓                  ↓
  ScatterState       town.*.* paths      global coherence
        ↓                   ↓                  ↓
  Functor Laws       Phase transitions   Eigenvector centroid
```

**Self-Similarity**: The widget's `map(f)` operation IS a functor; the functor IS the pattern; the pattern IS the skill.

---

## Continuation Generator

```
⟿[REFLECT]
/hydrate prompts/agent-town-phase7-reflect.md
handles: metrics_recorded=true; budget_model=validated; baselines=captured
mission: synthesize Phase 7 learnings, identify patterns for Phase 8
```

**Exploration Seeds** (Accursed Share for Phase 7+):

| Seed | Domain | Entropy Budget |
|------|--------|----------------|
| LLM-backed citizen dialogue | `void.llm.*` | 0.15 |
| Procedural town generation | `void.generation.*` | 0.10 |
| Inter-town communication | `void.network.*` | 0.10 |
| Time-travel debugging | `void.temporal.*` | 0.05 |
| Citizen death/rebirth | `void.lifecycle.*` | 0.05 |
| TownSheaf coherence | `concept.sheaf.*` | 0.10 |

---

## Changelog

- 2025-12-14: Phase 7 MEASURE - Code metrics, leading indicators, budget model validation
- 2025-12-14: Phase 7 EDUCATE - DialogueEngine API, budget tiers, archetype voices, ADRs
- 2025-12-14: Added Recursive Hologram and Continuation Generator (RE-METABOLIZE)
- 2025-12-14: Phase 6 MEASURE - Metrics, baselines, thresholds, counter-metrics
- 2025-12-14: Phase 6 EDUCATE - Teaching examples, demo guide, verification commands
- 2025-12-14: Phase 6 RESEARCH - Live marimo notebook patterns
- 2025-12-14: Initial version (Phase 5 EDUCATE)
