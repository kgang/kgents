# Reactive Substrate Quickstart

Get from zero to widget in 5 minutes.

## Install

```bash
pip install kgents
# or
uv pip install kgents
```

## 1. Create a Widget

```python
from agents.i.reactive import AgentCardWidget, AgentCardState

# Define state (immutable dataclass)
card = AgentCardWidget(AgentCardState(
    name="My Agent",
    phase="active",        # 'active', 'waiting', 'idle', 'error'
    activity=(0.3, 0.5, 0.7, 0.9),  # sparkline values
    capability=0.85,       # 0.0 to 1.0
))
```

## 2. Render to Any Target

```python
# Terminal output
print(card.to_cli())
# Output:
# [●] My Agent
# ▁▃▅█
# [████████░░] 85%

# Textual TUI
widget = card.to_tui()

# Notebook HTML
html = card.to_marimo()

# API JSON
data = card.to_json()
# {'name': 'My Agent', 'phase': 'active', 'activity': [0.3, 0.5, 0.7, 0.9], ...}
```

**Same widget. Four targets. Zero rewrites.**

## 3. Try the Live Dashboard

```bash
# Demo mode with sample data
kg dashboard --demo

# Or the tutorial notebook
marimo run impl/claude/agents/i/reactive/demo/tutorial.py
```

## 4. Explore More Widgets

```python
from agents.i.reactive import (
    # Atomic
    GlyphWidget, GlyphState,

    # Composed
    BarWidget, BarState,
    SparklineWidget, SparklineState,
    DensityFieldWidget, DensityFieldState,

    # Cards
    AgentCardWidget, AgentCardState,
    YieldCardWidget, YieldCardState,
    ShadowCardWidget, ShadowCardState,
    DialecticCardWidget, DialecticCardState,

    # Reactive
    Signal, Computed, Effect,
)

# Progress bar
bar = BarWidget(BarState(value=0.75, width=20, label="Memory"))
print(bar.to_cli())  # Memory [███████████████░░░░░] 75%

# Time series
sparkline = SparklineWidget(SparklineState(
    values=(0.2, 0.4, 0.6, 0.8, 0.6, 0.9),
    label="CPU"
))
print(sparkline.to_cli())  # CPU ▂▄▆█▆█
```

## 5. Use Reactive Signals

```python
from agents.i.reactive import Signal, Computed

# Create observable state
count = Signal.of(0)

# Derive computed values
doubled = count.map(lambda x: x * 2)

# Subscribe to changes
count.subscribe(lambda v: print(f"Count changed: {v}"))

# Update triggers subscribers
count.set(5)  # prints "Count changed: 5"
print(doubled.value)  # 10
```

## Next Steps

- **Tutorial**: `marimo run impl/claude/agents/i/reactive/demo/tutorial.py`
- **API Reference**: See [README.md](README.md)
- **Source**: `impl/claude/agents/i/reactive/primitives/`
- **Tests**: `uv run pytest impl/claude/agents/i/reactive/ -v`

## Performance

All targets render at >4,000 renders/second:

```bash
python -m agents.i.reactive.demo.unified_app --benchmark
```

| Target | Renders/sec |
|--------|-------------|
| CLI | >10,000 |
| TUI | >4,000 |
| Marimo | >4,000 |
| JSON | >50,000 |

---

*Reactive Substrate v1.0.0*
