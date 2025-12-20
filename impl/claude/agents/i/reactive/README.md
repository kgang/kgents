# Reactive Substrate v1.0

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-1460%20passing-brightgreen)](../../)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](../../../pyproject.toml)
[![Performance](https://img.shields.io/badge/perf->4k%20renders%2Fsec-orange)](demo/unified_app.py)

Target-agnostic reactive widgets for agent visualization.

> **New?** Start with the [Quickstart](QUICKSTART.md) or run the [Tutorial](demo/tutorial.py).

## Quick Start

```python
from agents.i.reactive import AgentCardWidget, AgentCardState

# Define once
card = AgentCardWidget(AgentCardState(
    name="My Agent",
    phase="active",
    activity=(0.3, 0.5, 0.7, 0.9),
    capability=0.85,
))

# Render anywhere
print(card.to_cli())      # Terminal
card.to_tui()             # Textual app
card.to_marimo()          # Notebook
card.to_json()            # API response
```

## Architecture

The reactive substrate implements a **functor pattern**:

```
project : KgentsWidget[S] → Target → Renderable[Target]
```

Same widget state, different projections. Zero rewrites.

### Supported Targets

| Target | Method | Returns |
|--------|--------|---------|
| `CLI` | `to_cli()` | `str` (ASCII art) |
| `TUI` | `to_tui()` | Textual Widget / Rich Text |
| `MARIMO` | `to_marimo()` | HTML string / anywidget |
| `JSON` | `to_json()` | `dict` (serializable) |

## Core Abstractions

### Reactive Primitives

```python
from agents.i.reactive import Signal, Computed, Effect

# Signal: Observable state
count = Signal.of(0)
count.subscribe(lambda v: print(f"Count: {v}"))
count.set(1)  # prints "Count: 1"

# Computed: Derived state
doubled = count.map(lambda x: x * 2)
assert doubled.value == 2

# Effect: Side effects
effect = Effect.of(fn=lambda: print(count.value), sources=[count])
effect.run()
```

### Widget Classes

```python
from agents.i.reactive import KgentsWidget, CompositeWidget, RenderTarget

# KgentsWidget[S]: Single state widget
class MyWidget(KgentsWidget[MyState]):
    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return f"Value: {self.state.value.x}"
            case RenderTarget.JSON:
                return {"x": self.state.value.x}

# CompositeWidget[S]: Composes child widgets
class CardWidget(CompositeWidget[CardState]):
    def __init__(self, state: CardState):
        super().__init__(state)
        self.slots["header"] = GlyphWidget(...)
        self.slots["body"] = SparklineWidget(...)
```

## Widget Primitives

### Atomic (Wave 1)

- **GlyphWidget** - Single character with phase semantics, entropy distortion

### Composed (Wave 2)

- **BarWidget** - Progress/capacity bar (composes glyphs)
- **SparklineWidget** - Time-series mini-chart
- **DensityFieldWidget** - 2D grid with spatial coherence

### Cards (Wave 3)

- **AgentCardWidget** - Full agent: phase glyph + activity sparkline + capability bar
- **YieldCardWidget** - Function return value visualization
- **ShadowCardWidget** - H-gent shadow introspection
- **DialecticCardWidget** - Thesis/antithesis/synthesis visualization

## Adapters

### Textual (TUI)

```python
from agents.i.reactive import TextualAdapter, create_textual_adapter

# Wrap any widget for Textual
adapter = create_textual_adapter(my_widget)
# Use in Textual app
```

### Marimo (Notebooks)

```python
from agents.i.reactive import MarimoAdapter, is_anywidget_available

if is_anywidget_available():
    adapter = MarimoAdapter(my_widget)
    # Display in notebook
```

## Demos

```bash
# CLI mode (ASCII output)
python -m agents.i.reactive.demo.unified_app

# TUI mode (Textual)
python -m agents.i.reactive.demo.unified_app --target=tui

# System dashboard
kg dashboard           # Live metrics
kg dashboard --demo    # Demo mode
```

## Principles

1. **Pure Entropy Algebra** - No `random.random()` in render paths
2. **Time Flows Downward** - Parent provides `t` to children
3. **Projections Are Manifest** - `project()` IS `logos.invoke("manifest")`
4. **Glyph as Atomic Unit** - Everything composes from glyphs
5. **Deterministic Joy** - Same seed -> same personality, forever
6. **Slots/Fillers Composition** - Operad-like widget composition

## API Reference

### Core Exports

```python
from agents.i.reactive import (
    # Core
    Signal, Computed, Effect,
    KgentsWidget, CompositeWidget, RenderTarget,

    # Primitives
    GlyphWidget, GlyphState,
    BarWidget, BarState,
    SparklineWidget, SparklineState,
    DensityFieldWidget, DensityFieldState,
    AgentCardWidget, AgentCardState,
    YieldCardWidget, YieldCardState,
    ShadowCardWidget, ShadowCardState,
    DialecticCardWidget, DialecticCardState,

    # Adapters
    TextualAdapter, MarimoAdapter,

    # Meta
    __version__,  # "1.0.0"
)
```

## Testing

```bash
# Run all reactive tests
uv run pytest impl/claude/agents/i/reactive/ -v

# 1460+ tests, <3s runtime
```

## Performance

- CLI: >10,000 renders/sec
- TUI: >4,000 renders/sec
- Marimo: >4,000 renders/sec
- JSON: >50,000 renders/sec
