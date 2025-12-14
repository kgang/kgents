---
path: plans/reactive-substrate-unification
status: active
progress: 15
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [agentese-universal-protocol, marimo-integration, dashboard-textual-refactor]
session_notes: |
  CROWN JEWEL EXTENSION: Unified Reactive Substrate
  Key insight: Textual reactive, marimo DAG, React state are ISOMORPHIC
  One widget definition → any target (CLI, TUI, marimo, React, JSON)

  RESEARCH COMPLETE (2025-12-14):
  - Studied v0-ui-mock React architecture thoroughly
  - Extracted 6 key patterns (see plans/meta/v0-ui-learnings-synthesis.md)
  - Critical insight: Pure entropy algebra + time flows downward + deterministic joy
  - Glyph as atomic unit matches our categorical foundation
phase_ledger:
  PLAN: touched
  RESEARCH: complete
  DEVELOP: pending
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched  # Deep synergy with AUP!
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.03
  returned: 0.0
---

# Reactive Substrate Unification

> *"The widget is the state machine. The UI is merely a projection of that state into a rendering target."*

## The Isomorphism Discovery

An agent working on marimo integration discovered something profound:

> "The marimo DAG system is the same as the TEXTUAL event model where variable updates are pushed out to components!"

This isn't just similar—it's **categorically isomorphic**:

| Concept | Textual | Marimo | React | Our Abstraction |
|---------|---------|--------|-------|-----------------|
| Observable state | `reactive()` | Cell variable | `useState()` | `Signal[T]` |
| Derived state | `computed` | Dependent cell | `useMemo()` | `Computed[T]` |
| Side effects | `watch()` | Cell execution | `useEffect()` | `Effect` |
| State mutation | `self.x = y` | Variable reassign | `setState()` | `signal.set()` |
| Subscription | `on_mount()` | DAG edge | Mount/unmount | `subscribe()` |
| Rendering | `compose()` | Cell output | `render()` | `project()` |

**The same reactive graph can be projected to ANY target.**

---

## The Vision

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KGENTS REACTIVE SUBSTRATE                            │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    Widget Definition (Target-Agnostic)              │   │
│   │                                                                     │   │
│   │   class StigmergicField(KgentsWidget[FieldState]):                 │   │
│   │       """The field exists. How it renders is the target's job."""  │   │
│   │                                                                     │   │
│   │       state = Signal(FieldState.empty())                           │   │
│   │       entities = Computed(lambda s: s.entities)                    │   │
│   │       pheromones = Computed(lambda s: s.pheromones)                │   │
│   │                                                                     │   │
│   │       @effect                                                       │   │
│   │       def on_tick(self):                                           │   │
│   │           self.state.update(lambda s: s.tick())                    │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ project(target)                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         Target Projectors                           │   │
│   │                                                                     │   │
│   │   CLI Projector:     print(ascii_render(state))                    │   │
│   │   TUI Projector:     Textual Widget with reactive binding          │   │
│   │   Marimo Projector:  anywidget with traitlet sync                  │   │
│   │   JSON Projector:    AgenteseResponse for HTTP API                 │   │
│   │   React Projector:   TypeScript interface (their code)             │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Abstractions

### 1. Signal[T] - Observable Primitive

```python
from typing import TypeVar, Generic, Callable
from dataclasses import dataclass, field

T = TypeVar("T")

@dataclass
class Signal(Generic[T]):
    """
    The fundamental reactive primitive.

    A Signal holds a value and notifies subscribers when it changes.
    This is the shared abstraction across ALL targets.

    Equivalent to:
    - Textual: reactive() attribute
    - Marimo: Cell variable (implicitly)
    - React: useState() return value
    - Solid: createSignal()
    """

    _value: T
    _subscribers: list[Callable[[T], None]] = field(default_factory=list)

    @property
    def value(self) -> T:
        """Get current value (read-only)."""
        return self._value

    def set(self, new_value: T) -> None:
        """Set new value and notify subscribers."""
        if new_value != self._value:
            self._value = new_value
            for sub in self._subscribers:
                sub(new_value)

    def update(self, fn: Callable[[T], T]) -> None:
        """Update value via function."""
        self.set(fn(self._value))

    def subscribe(self, callback: Callable[[T], None]) -> Callable[[], None]:
        """Subscribe to changes. Returns unsubscribe function."""
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback)

    def map(self, fn: Callable[[T], "U"]) -> "Computed[U]":
        """Create derived signal (functor map)."""
        return Computed(lambda: fn(self._value), sources=[self])
```

### 2. Computed[T] - Derived State

```python
@dataclass
class Computed(Generic[T]):
    """
    Derived state that auto-updates when dependencies change.

    Equivalent to:
    - Textual: @computed property
    - Marimo: Dependent cell
    - React: useMemo()
    - Solid: createMemo()
    """

    _compute: Callable[[], T]
    _sources: list[Signal] = field(default_factory=list)
    _cached: T | None = None
    _dirty: bool = True

    @property
    def value(self) -> T:
        if self._dirty:
            self._cached = self._compute()
            self._dirty = False
        return self._cached  # type: ignore

    def _invalidate(self) -> None:
        self._dirty = True
```

### 3. Effect - Side Effect Container

```python
@dataclass
class Effect:
    """
    Side effect that runs when dependencies change.

    Equivalent to:
    - Textual: watch() decorator
    - Marimo: Cell with side effects
    - React: useEffect()
    """

    _fn: Callable[[], None]
    _sources: list[Signal] = field(default_factory=list)
    _cleanup: Callable[[], None] | None = None

    def run(self) -> None:
        if self._cleanup:
            self._cleanup()
        self._cleanup = self._fn() or None

    def dispose(self) -> None:
        if self._cleanup:
            self._cleanup()
```

### 4. KgentsWidget[S] - Base Widget Class

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from enum import Enum, auto

S = TypeVar("S")  # State type

class RenderTarget(Enum):
    """Supported rendering targets."""
    CLI = auto()      # Plain text / ASCII
    TUI = auto()      # Textual widget
    MARIMO = auto()   # anywidget
    JSON = auto()     # API response
    # Future: REACT, FLUTTER, etc.

class KgentsWidget(ABC, Generic[S]):
    """
    Base class for all kgents widgets.

    A widget is:
    1. A state machine (Signal[S])
    2. Derived computations (Computed[...])
    3. Side effects (Effect)
    4. A projection function per target

    The widget definition is TARGET-AGNOSTIC.
    Projectors handle target-specific rendering.
    """

    state: Signal[S]

    @abstractmethod
    def project(self, target: RenderTarget) -> Any:
        """
        Project this widget to a rendering target.

        Returns:
        - CLI: str (ASCII art)
        - TUI: textual.widget.Widget
        - MARIMO: anywidget.AnyWidget
        - JSON: dict (serializable)
        """
        ...

    def to_cli(self) -> str:
        """Convenience: project to CLI."""
        return self.project(RenderTarget.CLI)

    def to_tui(self) -> "Widget":
        """Convenience: project to Textual."""
        return self.project(RenderTarget.TUI)

    def to_marimo(self) -> "AnyWidget":
        """Convenience: project to marimo."""
        return self.project(RenderTarget.MARIMO)

    def to_json(self) -> dict:
        """Convenience: project to JSON (for API)."""
        return self.project(RenderTarget.JSON)
```

---

## Example: StigmergicField

```python
@dataclass
class FieldState:
    """Immutable state for stigmergic field."""
    entities: tuple[Entity, ...] = ()
    pheromones: tuple[Pheromone, ...] = ()
    entropy: float = 0.0
    tick_count: int = 0

    def tick(self) -> "FieldState":
        """Advance simulation by one tick."""
        # Brownian motion, pheromone decay, etc.
        return FieldState(
            entities=self._move_entities(),
            pheromones=self._decay_pheromones(),
            entropy=self.entropy * 0.99,
            tick_count=self.tick_count + 1,
        )

class StigmergicFieldWidget(KgentsWidget[FieldState]):
    """
    The stigmergic field widget.

    ONE definition. FOUR+ rendering targets.
    """

    def __init__(self, initial_state: FieldState | None = None):
        self.state = Signal(initial_state or FieldState())

        # Derived state
        self.entity_count = Computed(lambda: len(self.state.value.entities))
        self.heat = Computed(lambda: sum(p.intensity for p in self.state.value.pheromones))

        # Effects
        self._tick_effect = Effect(self._on_tick)

    def _on_tick(self) -> None:
        """Called every tick to update state."""
        self.state.update(lambda s: s.tick())

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                return self._render_cli()
            case RenderTarget.TUI:
                return self._render_tui()
            case RenderTarget.MARIMO:
                return self._render_marimo()
            case RenderTarget.JSON:
                return self._render_json()

    def _render_cli(self) -> str:
        """ASCII art rendering."""
        state = self.state.value
        lines = []
        lines.append(f"┌{'─' * 40}┐")
        lines.append(f"│ FIELD (tick {state.tick_count:05d}) │")
        lines.append(f"│ Entities: {len(state.entities):3d}  Entropy: {state.entropy:.2f} │")
        lines.append(f"└{'─' * 40}┘")

        # Simple ASCII grid
        grid = [[' ' for _ in range(40)] for _ in range(20)]
        for e in state.entities:
            x, y = int(e.x * 40), int(e.y * 20)
            if 0 <= x < 40 and 0 <= y < 20:
                grid[y][x] = e.glyph[0]

        for row in grid:
            lines.append('│' + ''.join(row) + '│')

        return '\n'.join(lines)

    def _render_tui(self) -> "Widget":
        """Textual widget with reactive binding."""
        from textual.widgets import Static
        from textual.reactive import reactive

        widget = self

        class StigmergicFieldTUI(Static):
            """Textual projection of StigmergicField."""

            field_state = reactive(widget.state.value)

            def __init__(self):
                super().__init__()
                # Subscribe to state changes
                widget.state.subscribe(self._on_state_change)

            def _on_state_change(self, new_state: FieldState) -> None:
                self.field_state = new_state

            def watch_field_state(self, new_state: FieldState) -> None:
                self.update(widget._render_cli())  # Reuse CLI render

        return StigmergicFieldTUI()

    def _render_marimo(self) -> "AnyWidget":
        """anywidget for marimo notebooks."""
        import anywidget
        import traitlets

        widget = self

        class StigmergicFieldAnyWidget(anywidget.AnyWidget):
            _esm = """
            export function render({ model, el }) {
                const canvas = document.createElement('canvas');
                // ... canvas rendering code ...
            }
            """

            entities = traitlets.List([]).tag(sync=True)
            pheromones = traitlets.List([]).tag(sync=True)
            entropy = traitlets.Float(0.0).tag(sync=True)

            def __init__(self):
                super().__init__()
                self._update_from_state(widget.state.value)
                widget.state.subscribe(self._update_from_state)

            def _update_from_state(self, state: FieldState) -> None:
                self.entities = [e.to_dict() for e in state.entities]
                self.pheromones = [p.to_dict() for p in state.pheromones]
                self.entropy = state.entropy

        return StigmergicFieldAnyWidget()

    def _render_json(self) -> dict:
        """JSON for API responses."""
        state = self.state.value
        return {
            "type": "stigmergic_field",
            "tick_count": state.tick_count,
            "entity_count": len(state.entities),
            "entropy": state.entropy,
            "entities": [e.to_dict() for e in state.entities],
            "pheromones": [p.to_dict() for p in state.pheromones],
        }
```

---

## Integration Points

### With AGENTESE Universal Protocol (AUP)

The JSON projector IS the API response:

```python
# In AgenteseBridge
async def invoke(self, handle: str, observer: ObserverContext, **kwargs):
    result = await self.logos.invoke(handle, umwelt, **kwargs)

    # If result is a KgentsWidget, project to JSON
    if isinstance(result, KgentsWidget):
        return AgenteseResponse(
            handle=handle,
            result=result.to_json(),  # Uses JSON projector!
            meta=ResponseMeta(...)
        )

    return AgenteseResponse(handle=handle, result=result, meta=...)
```

### With Marimo Integration

The marimo projector produces anywidgets:

```python
# In marimo notebook
@app.cell
def field_widget():
    from impl.claude.agents.i.widgets import StigmergicFieldWidget

    field = StigmergicFieldWidget()
    return field.to_marimo()  # Returns anywidget!
```

### With TUI Dashboard

The TUI projector produces Textual widgets:

```python
# In dashboard screen
class DashboardScreen(Screen):
    def compose(self):
        field = StigmergicFieldWidget()
        yield field.to_tui()  # Returns Textual widget!
```

### With CLI Commands

The CLI projector produces ASCII:

```bash
$ kg field --ascii
┌────────────────────────────────────────┐
│ FIELD (tick 00142)                     │
│ Entities:  12  Entropy: 0.73           │
└────────────────────────────────────────┘
│     K                                  │
│          R                    *        │
│                    J                   │
│        B                               │
...
```

---

## The Functor Structure

This is categorically beautiful:

```
Widget[S] : State → UI

where:
  Widget[S] is a Functor from the category of States to the category of UIs

  project : Widget[S] → Target → UI[Target]

  For any morphism f : S → S' (state transition):
    project(f(s)) = render(project(s), f)  # Naturality condition
```

**The state machine IS the widget. The rendering IS a functor application.**

---

## File Structure

```
impl/claude/agents/i/reactive/
├── __init__.py
├── signal.py           # Signal[T], Computed[T], Effect
├── widget.py           # KgentsWidget[S] base class
├── projectors/
│   ├── __init__.py
│   ├── cli.py          # ASCII rendering utilities
│   ├── tui.py          # Textual widget factories
│   ├── marimo.py       # anywidget factories
│   └── json.py         # JSON serialization
├── widgets/
│   ├── __init__.py
│   ├── stigmergic_field.py
│   ├── dialectic_panel.py
│   ├── timeline.py
│   └── garden.py       # Container widget
└── _tests/
    ├── test_signal.py
    ├── test_widget.py
    └── test_projectors.py
```

---

## Migration Path

### Phase 1: Core Abstractions
1. Implement `Signal[T]`, `Computed[T]`, `Effect`
2. Implement `KgentsWidget[S]` base class
3. Tests for reactive primitives

### Phase 2: First Widget
1. Implement `StigmergicFieldWidget` with all projectors
2. Verify CLI output matches expected
3. Verify TUI projection works in dashboard
4. Verify marimo projection works in notebook
5. Verify JSON projection works with AUP

### Phase 3: Migrate Existing Widgets
1. Refactor existing TUI widgets to use new base
2. Refactor existing marimo widgets to use new base
3. Ensure no regressions

### Phase 4: Full Unification
1. All widgets use unified substrate
2. Single source of truth for widget definitions
3. Projectors as pluggable adapters

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Widget definitions | Same code for all targets |
| State synchronization | Automatic via Signal subscription |
| Projector count | 4 (CLI, TUI, marimo, JSON) |
| Test coverage | Each widget × each projector |
| LOC reduction | 40%+ vs separate implementations |

---

## The Enlightenment

> "We've been building the same widget three times—once for Textual, once for marimo, once for the API. The reactive substrate unification means: **build once, project everywhere**."

This is the categorical completion of the UI vision:

1. **AGENTESE** defines what can be observed
2. **Logos** resolves handles to interactions
3. **KgentsWidget** defines the state machine
4. **Projectors** render to any target
5. **AUP** carries JSON projections over HTTP

The widget IS the state machine. The UI is merely a view.

---

*"The functor lifts the state into form. The form flows to the eye that deserves to see it."*
