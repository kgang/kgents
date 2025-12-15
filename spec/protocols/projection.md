# Projection Protocol

> *"Developers design agents. Projections are batteries included."*

## Overview

The Projection Protocol defines how kgents content renders to any target medium. Developers write agents and their associated state machines. The projection layer handles the rest—whether output goes to ASCII terminal, JSON API, marimo notebook, WebGL, or VR headset.

This is not mere convenience. It is a **categorical guarantee**: the same agent definition, projected through different functors, produces semantically equivalent views.

```
Agent[S, A, B] ────────────► Projection[Target] ────────────► View[Target]
     │                              │                              │
     │                              │                              │
     └── Design once ───────────────┴── Batteries included ────────┘
```

---

## Mathematical Foundation

### The Projection Functor

A projection is a **natural transformation** from Agent State to Renderable Output:

```
P[T] : State → Renderable[T]

Where:
- State is the agent's internal state (polynomial position)
- T is the target medium (CLI, JSON, marimo, VR, etc.)
- Renderable[T] is the target-specific output type
```

### Naturality Condition

For all state morphisms `f : S₁ → S₂`, the following commutes:

```
        S₁ ─────f────→ S₂
        │               │
    P[T]│               │P[T]
        ↓               ↓
   R[T](S₁) ──R[T](f)─→ R[T](S₂)
```

**Translation**: If state changes, the projection changes consistently. Developers don't think about this—it just works.

### The Galois Connection

Projections form a Galois connection with their targets:

```
compress ⊣ embed

compress(embed(view)) ≤ view
state ≤ embed(compress(state))
```

This formalizes the insight from `projector.py`: projection is fundamentally **lossy**. Different targets have different fidelity. A marimo heatmap captures more than an ASCII sparkline. The category theory ensures we lose information predictably.

---

## The Projection Stack

### Layer 1: State (Agent Definition)

Developers define agents with state machines. This is where creativity happens.

```python
@dataclass(frozen=True)
class TownState:
    citizens: tuple[CitizenState, ...]
    phase: TownPhase
    entropy: float
```

### Layer 2: Widget (State + Semantics)

Widgets bind state to meaning. They know what the state *means*, not how to show it.

```python
class TownWidget(KgentsWidget[TownState]):
    """A town is a collection of citizens in phases."""

    @property
    def health(self) -> float:
        """Emergent property from citizen states."""
        return sum(c.vitality for c in self.state.value.citizens) / len(...)
```

### Layer 3: Projection (Widget + Target)

Projections produce target-specific output. Developers rarely touch this layer.

```python
# Built-in projections (batteries included)
TownWidget(...).to_cli()     # ASCII scatter plot
TownWidget(...).to_marimo()  # Interactive HTML/anywidget
TownWidget(...).to_json()    # API response
TownWidget(...).to_vr()      # Future: WebXR scene
```

---

## Target Registry

The projection system is extensible via the Target Registry:

| Target | Type | Fidelity | Interactive |
|--------|------|----------|-------------|
| CLI | `str` | Low | No |
| TUI | `rich.Text / textual.Widget` | Medium | Yes |
| JSON | `dict[str, Any]` | Lossless* | No |
| marimo | `anywidget / mo.Html` | High | Yes |
| SSE | `str` (event stream) | Streaming | Async |
| VR | `WebXR scene` | Maximum | Yes |

*JSON is lossless for data but loses presentation semantics.

### Registering New Targets

```python
from protocols.projection import ProjectionRegistry, RenderTarget

@ProjectionRegistry.register("webgl")
class WebGLTarget(RenderTarget):
    name = "webgl"
    type_hint = "three.Scene"
    fidelity = 0.95

    def project(self, widget: KgentsWidget) -> Any:
        """Convert widget to Three.js scene."""
        ...
```

---

## The Three Truths

### 1. State Is Design

Developers design the state machine. Everything else follows.

```python
# Developer writes THIS:
@dataclass(frozen=True)
class AgentCardState:
    name: str
    phase: str
    activity: tuple[float, ...]
    capability: float

# Developer gets ALL OF THESE for free:
card.to_cli()      # ┌─ Agent ──────────┐
card.to_tui()      # │ ▓▓▓░░ 60%       │
card.to_marimo()   # [Interactive card with hover]
card.to_json()     # {"name": "...", "phase": "...", ...}
```

### 2. Projection Is Mechanical

Once state is defined, projection is deterministic. Same state → same output per target.

```python
# This is a pure function:
project : State × Target → Output

# No side effects, no randomness in render paths
# (Entropy for personality is in STATE, not in projection)
```

### 3. Targets Are Isomorphic (Within Fidelity)

All targets represent the same underlying information, modulo fidelity loss.

```python
# These are semantically equivalent:
json_data = widget.to_json()
cli_output = widget.to_cli()

# The CLI output is a "compressed" view of the JSON data
# But no information is added—only removed
```

---

## Integration with AGENTESE

The Projection Protocol IS the `manifest` aspect operationalized:

```python
# AGENTESE path
await logos.invoke("world.agent.manifest", umwelt)

# Is implemented as:
AgentWidget(state).project(umwelt.preferred_target)
```

### Observer-Dependent Projection

Different observers get different projections—not because the data differs, but because their *capacity to receive* differs:

```python
# CLI user (low bandwidth)
await logos.invoke("world.town.manifest", cli_umwelt)
# → ASCII scatter plot, 80 chars wide

# marimo user (high bandwidth)
await logos.invoke("world.town.manifest", marimo_umwelt)
# → Interactive HTML with hover, click, zoom
```

This is NOT cheating. The underlying state is identical. The projection adapts to the observer's medium.

---

## Widget Composition

### Horizontal Composition (`>>`)

Chain widgets in sequence:

```python
# Input flows left-to-right
pipeline = GlyphWidget >> BarWidget >> CardWidget
```

### Vertical Composition (`//`)

Stack widgets in parallel:

```python
# Outputs combine
dashboard = header // main_content // footer
```

### Slot/Filler Pattern

Composite widgets define slots; fillers provide content:

```python
class DashboardWidget(CompositeWidget):
    slots = {
        "header": KgentsWidget,    # Any widget fits
        "sidebar": KgentsWidget,
        "main": KgentsWidget,
    }

# Fill the slots
dashboard = DashboardWidget()
dashboard.slots["header"] = HeaderWidget(...)
dashboard.slots["sidebar"] = NavWidget(...)
dashboard.slots["main"] = TownWidget(...)
```

---

## Implementation Guide

### For Agent Developers (Design Layer)

1. Define your state as a frozen dataclass
2. Create a widget class extending `KgentsWidget[YourState]`
3. Implement `project()` if you need custom rendering; otherwise, derive from existing widgets

```python
from agents.i.reactive import KgentsWidget, RenderTarget

@dataclass(frozen=True)
class MyState:
    value: int
    label: str

class MyWidget(KgentsWidget[MyState]):
    def project(self, target: RenderTarget) -> Any:
        s = self.state.value
        match target:
            case RenderTarget.CLI:
                return f"[{s.label}] {s.value}"
            case RenderTarget.JSON:
                return {"label": s.label, "value": s.value}
            case _:
                return f"{s.label}: {s.value}"
```

### For Framework Developers (Projection Layer)

Implement new targets by extending `RenderTarget` and registering with the registry.

### For Users (Zero Code)

Users invoke agents. Projections happen automatically based on context:
- Terminal → CLI projection
- API call → JSON projection
- Notebook → marimo projection

---

## The marimo Integration

marimo notebooks are a special case of the Projection Protocol. The reactive DAG model of marimo maps directly to the Signal/Computed/Effect model of kgents widgets.

### LogosCell Pattern

A marimo cell that hosts AGENTESE:

```python
@app.cell
def agent_view(mo, agent_state):
    """Render agent state as marimo HTML."""
    widget = AgentWidget(agent_state)

    # Last expression = displayed output
    mo.Html(widget.to_marimo())
```

### No Adapter Layer Needed

The key insight from `meta.md`:
> marimo LogosCell pattern IS AgenteseBridge pattern—direct mapping, no adapter layer needed

This means:
1. AGENTESE paths work directly in marimo cells
2. Widget projections render as mo.Html
3. Reactivity (Signal dependencies) maps to marimo's cell dependencies

---

## Principles (Summary)

| Principle | Meaning |
|-----------|---------|
| **Design Over Plumbing** | Developers define state, not rendering |
| **Batteries Included** | All targets work out of the box |
| **Lossy by Design** | Fidelity varies by target; this is explicit |
| **Composable** | Widgets compose via `>>` and `//` |
| **Observable** | Same state → same output (determinism) |
| **Extensible** | New targets registered without changing agents |

---

## Connection to Spec Principles

| Principle | Projection Manifestation |
|-----------|--------------------------|
| Tasteful | Widget API is minimal: define state, get rendering |
| Curated | Four core targets (CLI, TUI, marimo, JSON); others by registration |
| Ethical | Projections are transparent—no hidden information |
| Joy-Inducing | marimo renders ARE joy; ASCII has personality |
| Composable | `>>` and `//` operators for widget composition |
| Heterarchical | Any widget can project to any target |
| Generative | State defines the space of possible views |

---

## Future Targets

| Target | Status | Notes |
|--------|--------|-------|
| CLI | ✓ Shipped | ASCII art, box drawing |
| TUI | ✓ Shipped | Textual widgets |
| marimo | ✓ Shipped | anywidget + mo.Html |
| JSON | ✓ Shipped | API responses |
| SSE | ✓ Shipped | Streaming events |
| WebGL | Planned | Three.js scenes |
| WebXR | Future | VR/AR experiences |
| Audio | Future | Sonification of state |

---

*"The projection is not the territory. But a good projection makes the territory navigable."*
