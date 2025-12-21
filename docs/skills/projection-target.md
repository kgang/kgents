# Skill: Custom Projection Targets

> Register custom targets for the Projection Protocol.

**Difficulty**: Easy
**Prerequisites**: KgentsWidget basics
**Files**: `agents/i/reactive/projection/registry.py`, `agents/i/reactive/projection/targets.py`
**References**: `spec/protocols/projection.md`

---

## Overview

The Projection Protocol renders widgets to multiple surfaces (CLI, TUI, Web, etc.). Custom targets let you extend this to new surfaces without modifying widget code.

**Key insight**: Projectors are registered once, then any widget can use them.

---

## Quick Start

```python
from agents.i.reactive.projection import ProjectionRegistry

@ProjectionRegistry.register("webgl", fidelity=0.9)
def webgl_projector(widget):
    """Convert widget state to Three.js scene data."""
    return {
        "type": "scene",
        "objects": [{"mesh": "box", "value": widget.state.value}],
    }

# Use it
result = ProjectionRegistry.project(my_widget, "webgl")
```

---

## Registration API

### Decorator Syntax

```python
@ProjectionRegistry.register(
    name: str,                # Target name (e.g., "webgl", "audio")
    *,
    fidelity: float = 0.5,    # Information preservation (0.0-1.0)
    description: str = "",    # Human-readable description
)
def projector(widget: KgentsWidget) -> Any:
    ...
```

### Registration at Import Time

Register projectors at module import for thread safety:

```python
# my_projectors.py
from agents.i.reactive.projection import ProjectionRegistry

@ProjectionRegistry.register("vr", fidelity=0.95, description="VR headset rendering")
def vr_projector(widget):
    return widget.to_json()  # Placeholder until VR impl exists
```

Then import the module to activate:

```python
import my_projectors  # Registers "vr" target
```

---

## Fidelity Levels

Fidelity indicates information preservation (0.0 = maximum loss, 1.0 = lossless):

| Level | Range | Examples |
|-------|-------|----------|
| LOSSLESS | 1.0 | JSON (full state) |
| MAXIMUM | 0.9-1.0 | WebGL, WebXR (rich visualization) |
| HIGH | 0.7-0.9 | marimo, TUI (interactive but constrained) |
| MEDIUM | 0.4-0.7 | SSE (streaming, some loss) |
| LOW | 0.0-0.4 | CLI (text only) |

### Querying by Fidelity

```python
from agents.i.reactive.projection import ProjectionRegistry, FidelityLevel

# Get all high-fidelity targets
high_fidelity = ProjectionRegistry.by_fidelity(FidelityLevel.HIGH)
for p in high_fidelity:
    print(f"{p.name}: {p.fidelity}")
```

### Choosing Fidelity for Your Target

- **0.9+**: Full visual/interactive capability (3D, VR, rich editors)
- **0.7-0.9**: Interactive but 2D (notebooks, TUIs)
- **0.5-0.7**: Streaming or constrained (SSE, mobile)
- **0.2-0.5**: Text-based (CLI, logs, email)
- **<0.2**: Minimal (notifications, badges)

---

## Graceful Degradation

Unknown targets automatically fall back to JSON:

```python
# "unknown_target" not registered -> falls back to JSON
result = ProjectionRegistry.project(widget, "unknown_target")

# Custom fallback
result = ProjectionRegistry.project(widget, "unknown", fallback="cli")
```

### Implementing Fallback in Projectors

```python
@ProjectionRegistry.register("audio", fidelity=0.4)
def audio_projector(widget):
    # Check if widget has audio-specific method
    if hasattr(widget, "to_audio"):
        return widget.to_audio()

    # Fallback: sonify the value
    value = widget.state.value if hasattr(widget.state, "value") else 0.5
    return {"frequency": 220 + value * 440, "duration": 0.5}
```

---

## Patterns

### Pattern 1: Wrap Existing Method

When widgets already have the capability:

```python
@ProjectionRegistry.register("sse", fidelity=0.6)
def sse_projector(widget):
    if hasattr(widget, "to_sse"):
        return widget.to_sse()
    # Fallback: wrap JSON
    import json
    return f"data: {json.dumps(widget.to_json())}\n\n"
```

### Pattern 2: Transform State

When you need to reshape widget state:

```python
@ProjectionRegistry.register("prometheus", fidelity=0.3)
def prometheus_projector(widget):
    """Export widget state as Prometheus metrics."""
    state = widget.state
    metrics = []

    if hasattr(state, "value"):
        metrics.append(f"kgents_value{{widget=\"{type(widget).__name__}\"}} {state.value}")
    if hasattr(state, "entropy"):
        metrics.append(f"kgents_entropy{{widget=\"{type(widget).__name__}\"}} {state.entropy}")

    return "\n".join(metrics)
```

### Pattern 3: Composite Projection

When projecting composed widgets:

```python
@ProjectionRegistry.register("slack", fidelity=0.4)
def slack_projector(widget):
    """Convert widget to Slack Block Kit format."""
    from agents.i.reactive.composable import HStack, VStack

    if isinstance(widget, (HStack, VStack)):
        # Recursively project children
        children = [
            ProjectionRegistry.project(child, "slack")
            for child in widget.children
        ]
        return {"type": "section", "fields": children}

    # Single widget
    return {"type": "mrkdwn", "text": widget.project(RenderTarget.CLI)}
```

---

## Testing Custom Targets

```python
import pytest
from agents.i.reactive.projection import ProjectionRegistry

@pytest.fixture(autouse=True)
def reset_registry():
    """Ensure test isolation."""
    ProjectionRegistry.reset()
    yield
    ProjectionRegistry.reset()

def test_custom_target():
    @ProjectionRegistry.register("test_target", fidelity=0.5)
    def test_projector(widget):
        return {"custom": True, "value": widget.state.value}

    widget = BarWidget(BarState(value=0.75))
    result = ProjectionRegistry.project(widget, "test_target")

    assert result == {"custom": True, "value": 0.75}

def test_graceful_degradation():
    widget = GlyphWidget(GlyphState(phase="active"))

    # Unknown target falls back to JSON
    result = ProjectionRegistry.project(widget, "nonexistent")
    assert isinstance(result, dict)
    assert result["phase"] == "active"
```

---

## Built-in Targets

The registry ships with these targets:

| Target | Fidelity | Method |
|--------|----------|--------|
| `cli` | 0.2 | `widget.project(RenderTarget.CLI)` |
| `tui` | 0.5 | `widget.project(RenderTarget.TUI)` |
| `marimo` | 0.8 | `widget.project(RenderTarget.MARIMO)` |
| `json` | 1.0 | `widget.project(RenderTarget.JSON)` |
| `sse` | 0.6 | `widget.to_sse()` or JSON fallback |

Placeholder targets (not yet implemented):
- `webgl` (0.9)
- `webxr` (0.95)
- `audio` (0.4)

---

## Registry API Reference

```python
# Register a projector
@ProjectionRegistry.register("name", fidelity=0.5)
def projector(widget): ...

# Project a widget
result = ProjectionRegistry.project(widget, "target")
result = ProjectionRegistry.project(widget, ExtendedTarget.CLI)

# Query registry
ProjectionRegistry.supports("webgl")           # -> bool
ProjectionRegistry.all_targets()               # -> ["cli", "json", ...]
ProjectionRegistry.get("cli")                  # -> Projector | None
ProjectionRegistry.by_fidelity(FidelityLevel.HIGH)  # -> [Projector, ...]

# Test isolation
ProjectionRegistry.reset()  # Clear custom registrations
```

---

## Best Practices

### 1. Register at Import Time

```python
# Good: deterministic registration order
# my_targets.py
@ProjectionRegistry.register("custom")
def custom_projector(widget): ...

# main.py
import my_targets  # Registration happens here
```

### 2. Choose Accurate Fidelity

Don't overstate fidelity. CLI projection loses color, interactivity, and spatial layout - it's honestly 0.2, not 0.5.

### 3. Document Widget Requirements

```python
@ProjectionRegistry.register("audio", fidelity=0.4)
def audio_projector(widget):
    """
    Project widget to audio representation.

    Widget requirements:
        - state.value (float 0.0-1.0) -> frequency
        - state.phase (str) -> instrument selection

    Falls back to 440Hz sine wave if requirements not met.
    """
    ...
```

### 4. Handle Composition

Check for HStack/VStack and recurse:

```python
from agents.i.reactive.composable import ComposableWidget

if isinstance(widget, ComposableWidget):
    return [ProjectionRegistry.project(c, target) for c in widget.children]
```

---

## Related Skills

- [building-agent](building-agent.md) - Creating agents with projectable state
- [elastic-ui-patterns](elastic-ui-patterns.md) - Responsive UI patterns
- [3d-projection-patterns](3d-projection-patterns.md) - 3D visualization patterns

---

## Source Reference

- `agents/i/reactive/projection/registry.py` - ProjectionRegistry
- `agents/i/reactive/projection/targets.py` - ExtendedTarget, FidelityLevel
- `agents/i/reactive/projection/laws.py` - Functor law verification

---

*Skill created: 2025-12-16 | Projection Protocol Phase*
