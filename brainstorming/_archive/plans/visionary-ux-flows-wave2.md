---
path: plans/visionary-ux-flows-wave2
status: active
progress: 25
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/visionary-ux-flows-wave3
  - interfaces/composable-dashboard
session_notes: |
  Wave 2 RESEARCH complete.
  Key findings:
    1. Zero `>>` operator collision—safe to implement
    2. Three-tier composition (Pipeline >> Layout >> Widget) exists
    3. Theme propagates via ThemeProvider Signal + subscribe pattern
    4. Focus managed via AnimatedFocus + spring transitions
    5. FlexContainer and flex_row/flex_column already exist for Textual
  Recommendation: Add `>>` at widget level; reuse FlexLayout/FlexContainer internals.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.03
  spent: 0.03
  returned: 0.00
---

# Visionary UX Flows: Wave 2 PLAN (Widget Composition)

**Predecessor**: `plans/_epilogues/2025-12-14-visionary-ux-wave1-reflect.md`
**Phase**: PLAN (COMPLETE)
**Next Phase**: RESEARCH

---

## Research Findings

### Q1: Layout Algebra Composition

**Answer**: Layout algebra is NOT associative for mixed operations.

```
(a >> b).vertical() >> c ≠ a >> (b.vertical() >> c)
```

However, it IS associative within the same direction:
```
(a >> b >> c).horizontal() = a >> (b >> c).horizontal()
```

The existing `FlexLayout` and `GridLayout` in `pipeline/layout.py` handle this properly by:
1. Computing child sizes first
2. Then applying alignment/justification
3. Not mixing horizontal/vertical in same container

**Recommendation**: Don't try to make `>>` associative across layout modes. Instead:
- `>>` always means "horizontal composition" (row)
- `.vertical()` creates a new container wrapping children

### Q2: Signal Propagation

**Answer**: Already solved in Wave 1.

```python
# Signal.map() creates Computed that auto-invalidates
cpu_data = Signal.of((0.1, 0.2, 0.3))
derived = cpu_data.map(lambda vs: max(vs))
# derived.value recomputes when cpu_data changes
```

Widgets wrap Signals. When parent state changes:
1. Parent Signal notifies subscribers
2. Child widgets receive updated state via `.with_*()` methods (immutable pattern)
3. Child widgets can subscribe to parent Signal for reactive updates

**Key Pattern**: All widgets use immutable state + `with_*()` methods returning new widgets.

### Q3: Projection Consistency

**Answer**: Yes, with caveats.

```python
(a >> b).project(CLI) = a.project(CLI) + separator + b.project(CLI)
```

The separator depends on layout mode:
- Horizontal: "" (concatenation) or " " (space)
- Vertical: "\n" (newline)

This is already implemented in `CompositeWidget` pattern in `widget.py`.

### Q4: Scatter Special Case

**Answer**: Scatter is a **terminal widget** (sink), not a composable source.

Scatter consumes data but doesn't produce composable output. It's like a sparkline but 2D:
- `Signal[list[T]] → Scatter → Visual` (terminal)
- vs `Signal[T] → Sparkline → (Signal[str], Visual)` (composable)

**Recommendation**: Scatter composes BY PLACEMENT (layout), not BY DATA FLOW:
```python
# Compose by layout
dashboard = (sparklines.vertical() >> scatter)  # Side by side

# NOT by data flow (scatter doesn't emit)
# dashboard = sparklines >> scatter  # Wrong mental model
```

### Q5: Performance Budget

**Answer**: Already verified in Wave 1 tests.

From `plans/_epilogues/2025-12-14-visionary-ux-wave1-reflect.md`:
- `0.03ms p50` for 25-citizen scatter render
- At 60fps (16.67ms frame budget): `0.03ms * 3 sparklines * 25 citizens = 2.25ms`
- **Headroom**: 14.4ms per frame remaining

Rendering is NOT the bottleneck. Signal propagation and state updates dominate.

---

## Existing Architecture Analysis

### Three-Tier Composition (Already Exists)

| Tier | Abstraction | Composition Operator | Location |
|------|-------------|---------------------|----------|
| **Pipeline** | Data transformation | `>>` (not yet) | `pipeline/render.py` |
| **Layout** | Spatial arrangement | `FlexLayout`, `GridLayout` | `pipeline/layout.py` |
| **Widget** | State → Visual | `project()` | `widget.py` |

The `>>` operator should compose at the **Pipeline** tier, where:
- Input: `Computed[T]` or `Signal[T]`
- Output: `Computed[U]`
- Widgets are "leaves" that project pipeline output

### Existing Widget Patterns

| Widget | Composes From | Signal? | Immutable? |
|--------|---------------|---------|------------|
| `GlyphWidget` | (atomic) | Yes | Yes (with_*) |
| `SparklineWidget` | `GlyphWidget[]` | Yes | Yes (with_*) |
| `DensityFieldWidget` | `GlyphWidget[][]` | Yes | Yes (with_*) |
| `EigenvectorScatter` | (atomic, marimo) | Yes | Yes |

**Pattern**: All widgets follow the same structure:
1. `Signal[State]` as internal state holder
2. `project(RenderTarget)` as the functor application
3. `with_*(...)` methods for immutable updates

### Gap Identified

The `CompositeWidget` exists but isn't well-utilized. The missing piece is:
1. A `ComposedWidget[L, R]` that holds two widgets side-by-side
2. A `WidgetStack` that holds widgets vertically
3. A factory pattern for `from_signal()` construction

---

## Wave 2 Design

### ComposableWidget Protocol (Refined)

```python
from typing import Protocol, TypeVar, Callable, Any
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import RenderTarget

S = TypeVar("S", covariant=True)
T = TypeVar("T")

class ComposableWidget(Protocol[S]):
    """Widget that composes via layout operators."""

    @property
    def state(self) -> Signal[S]:
        """The reactive state signal."""
        ...

    def project(self, target: RenderTarget) -> Any:
        """Project to rendering target."""
        ...

    def with_state(self, new_state: S) -> "ComposableWidget[S]":
        """Create new widget with transformed state (functor lens)."""
        ...

    def map(self, f: Callable[[S], T]) -> "ComposableWidget[T]":
        """Functor map: transform widget via state transformation."""
        ...

    # --- Composition operators (layout) ---

    def __rshift__(self, other: "ComposableWidget[Any]") -> "HStack":
        """Horizontal composition: self >> other."""
        ...

    def __floordiv__(self, other: "ComposableWidget[Any]") -> "VStack":
        """Vertical composition: self // other."""
        ...
```

### HStack and VStack

```python
@dataclass
class HStack(ComposableWidget[tuple[Any, ...]]):
    """Horizontally composed widgets."""

    children: tuple[ComposableWidget[Any], ...]
    gap: int = 1

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                sep = " " * self.gap
                return sep.join(c.project(target) for c in self.children)
            case RenderTarget.JSON:
                return {
                    "type": "hstack",
                    "children": [c.project(target) for c in self.children],
                }
            # ... other targets

    def __rshift__(self, other: ComposableWidget[Any]) -> "HStack":
        return HStack((*self.children, other), gap=self.gap)


@dataclass
class VStack(ComposableWidget[tuple[Any, ...]]):
    """Vertically composed widgets."""

    children: tuple[ComposableWidget[Any], ...]
    gap: int = 0

    def project(self, target: RenderTarget) -> Any:
        match target:
            case RenderTarget.CLI:
                sep = "\n" * (1 + self.gap)
                return sep.join(c.project(target) for c in self.children)
            # ...
```

### from_signal Factory Pattern

```python
class SparklineWidget(KgentsWidget[SparklineState]):
    # ... existing code ...

    @classmethod
    def from_signal(
        cls,
        data: Signal[tuple[float, ...]],
        label: str | None = None,
    ) -> "SparklineWidget":
        """Create sparkline bound to a data signal.

        The widget's state updates when the data signal changes.
        """
        widget = cls(SparklineState(values=data.value, label=label))

        # Subscribe to data changes
        def update_values(new_values: tuple[float, ...]) -> None:
            widget.state.set(SparklineState(
                values=new_values,
                max_length=widget.state.value.max_length,
                label=label,
                # ... preserve other fields
            ))

        data.subscribe(update_values)
        return widget
```

---

## Refined Goals

1. **ComposableWidget protocol** - Define in `agents/i/reactive/composable.py`
2. **HStack / VStack containers** - Implement in same module
3. **`>>` and `//` operators** - On existing widgets via mixin
4. **`from_signal()` factory** - On SparklineWidget, GlyphWidget
5. **Functor laws tests** - Verify `map(f).map(g) == map(g ∘ f)`

---

## Implementation Sketch

### File Structure

```
agents/i/reactive/
├── composable.py      # NEW: ComposableWidget, HStack, VStack
├── widget.py          # UPDATE: Add ComposableMixin
├── primitives/
│   ├── glyph.py       # UPDATE: Add from_signal()
│   └── sparkline.py   # UPDATE: Add from_signal()
└── _tests/
    └── test_composable.py  # NEW: Composition and functor tests
```

### Example Usage (Target)

```python
from agents.i.reactive import Signal
from agents.i.reactive.primitives import SparklineWidget

# Create signals
cpu = Signal.of((0.1, 0.2, 0.3))
mem = Signal.of((0.5, 0.6, 0.4))
disk = Signal.of((0.2, 0.2, 0.3))

# Create widgets bound to signals
cpu_spark = SparklineWidget.from_signal(cpu, label="CPU")
mem_spark = SparklineWidget.from_signal(mem, label="Memory")
disk_spark = SparklineWidget.from_signal(disk, label="Disk")

# Compose horizontally
dashboard = cpu_spark >> mem_spark >> disk_spark

# Or compose vertically
dashboard_v = cpu_spark // mem_spark // disk_spark

# Single project renders all
print(dashboard.project(RenderTarget.CLI))
# Output: "CPU: ▁▂▃  Memory: ▄▅▃  Disk: ▂▂▃"

# Updating signal auto-updates widget
cpu.set((0.1, 0.2, 0.3, 0.9))
print(dashboard.project(RenderTarget.CLI))
# Output: "CPU: ▁▂▃█  Memory: ▄▅▃  Disk: ▂▂▃"
```

---

## Success Criteria (Updated)

- [ ] `ComposableWidget` protocol defined with `__rshift__` and `__floordiv__`
- [ ] `HStack` and `VStack` containers implemented
- [ ] `SparklineWidget >> SparklineWidget` works
- [ ] `SparklineWidget // SparklineWidget` works
- [ ] `from_signal()` factory on SparklineWidget
- [ ] Functor law: `widget.map(f).map(g) == widget.map(lambda x: g(f(x)))`
- [ ] Tests for composition patterns

---

## Entropy Return

Research revealed that the three-tier composition already exists. The design space is narrower than expected—this is a good entropy return (0.01).

---

## RESEARCH Phase Findings (2025-12-14)

### Q1: Pipeline Composition Pattern

**File**: `pipeline/render.py`

The `RenderPipeline` manages rendering through:
1. **Priority-based render queue** - Uses `heapq` with `RenderPriority` (CRITICAL → IDLE)
2. **Dirty checking** - Nodes marked dirty via `invalidate()`, skipped if clean
3. **Cascade invalidation** - Parent invalidation propagates to children via `_children` list
4. **Signal integration** - `connect_signal(signal, node_ids)` auto-invalidates nodes on signal change

**Key Pattern**: `RenderNode[T]` wraps widgets with:
- `id: str` - Unique identifier
- `priority: RenderPriority` - Render order
- `_dirty: bool` - Needs re-render flag
- `_children: list[str]` - Child node IDs for cascade
- `render()` - Delegates to widget's `.to_cli()` or `.render()`

**Composition happens via registration**, not operators:
```python
pipeline.register("header", header_widget, RenderPriority.HIGH)
pipeline.register("content", content_widget, RenderPriority.NORMAL, parent="header")
```

**Insight**: `>>` should create HStack/VStack at widget level, then the composed widget registers as single node.

### Q2: Theme Propagation Mechanism

**File**: `pipeline/theme.py`

Theme propagates via reactive Signal pattern:
1. `ThemeProvider` holds `Signal[Theme]`
2. `provider.subscribe(callback)` notifies on mode changes
3. `Theme.with_mode(mode)` creates immutable copy

**Key Pattern**: Widgets receive theme via:
- Direct injection: `widget.project(target, theme=theme)`
- Or Signal subscription: `theme_provider.subscribe(widget.on_theme_change)`

**Composed widgets inherit theme**: Parent widget passes theme to children during `project()`:
```python
def project(self, target, theme=None):
    header = self.slots["header"].project(target, theme=theme)
    body = self.slots["body"].project(target, theme=theme)
    ...
```

**HStack/VStack design**: Should accept optional `theme: Theme | None` in `project()` and pass to children.

### Q3: Focus Management Across Composed Widgets

**File**: `pipeline/focus.py`

Focus uses `AnimatedFocus` which wraps `FocusState` with spring transitions:
1. `focus.register(id, tab_index, position)` - Register focusable element
2. `focus.focus(id)` - Move focus with animation
3. `focus.move(FocusDirection.FORWARD)` - Tab navigation

**Composed widgets and focus**: Each focusable element registers separately:
```python
# In HStack compose setup
for i, child in enumerate(self.children):
    if hasattr(child, "focusable") and child.focusable:
        focus.register(f"hstack-{id}-child-{i}", tab_index=i)
```

**Insight**: Composed widgets don't inherit focus automatically. Focus is managed at the `AnimatedFocus` level. HStack/VStack should expose `.register_children(focus_manager)` method for opt-in focus management.

### Q4: `>>` Operator Collision Check

**Grep Result**: NO `__rshift__`, `__floordiv__`, or `__or__` operators defined in `agents/i/reactive/`.

**Verdict**: SAFE to implement `>>` and `//` operators.

### Q5: Textual Adapter Container Patterns

**File**: `adapters/textual_layout.py`

Already provides:
- `FlexContainer(layout)` - Wraps `FlexLayout`
- `ResponsiveFlexContainer` - Breakpoint-based direction switching
- `flex_row(gap, justify, align)` - Factory for horizontal
- `flex_column(gap, justify, align)` - Factory for vertical

**Key Pattern**: Maps FlexLayout semantics to Textual CSS:
```python
def get_css_styles(self) -> str:
    if self._layout.direction == FlexDirection.ROW:
        styles.append("layout: horizontal;")
    styles.append(f"grid-gutter: {self._layout.gap};")
    ...
```

**File**: `adapters/textual_widget.py`

`TextualAdapter` bridges KgentsWidget → Textual:
1. Subscribes to widget's `Signal` on mount
2. Calls `project(RenderTarget.TUI)` on state change
3. Uses `Static.update(output)` to refresh display

**HStack/VStack Textual integration**:
```python
class HStack(ComposableWidget):
    def to_textual(self) -> FlexContainer:
        layout = FlexLayout(direction=FlexDirection.ROW, gap=self.gap)
        container = FlexContainer(layout)
        # Children wrapped in TextualAdapter added during compose
        return container
```

---

## Summary

| Question | Answer | Integration Point |
|----------|--------|-------------------|
| Pipeline composition | Priority queue + dirty checking | Register composed widget as single node |
| Theme propagation | Signal + subscribe pattern | Pass theme through `project()` |
| Focus management | AnimatedFocus + spring transitions | Opt-in via `.register_children()` |
| `>>` collision | Zero collision | Safe to implement |
| Textual containers | FlexContainer + flex_row/flex_column exist | Wrap in `to_textual()` method |

---

## Continuation

⟿[DEVELOP]

All research questions answered. Next phase: implement `ComposableWidget` protocol with `>>` and `//` operators.

---

*Guard [phase=RESEARCH][entropy=0.03][law_check=true][wave=2]*
