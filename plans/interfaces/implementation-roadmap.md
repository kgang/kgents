---
path: interfaces/implementation-roadmap
status: complete
progress: 100
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Concrete implementation steps for the Generative TUI Framework.
  Designed for parallel development - each flow can proceed independently.

  2025-12-12: ALL TRACKS COMPLETE (100%)
  - Track A (Entropy Primitives): COMPLETE
    - EntropyVisualizer, Sparkline, DensityField entropy param + heartbeat
  - Track B (Temporal Primitives): COMPLETE
    - CognitiveBranch, CognitiveTree with navigation
    - BranchTree widget with full rendering
    - Timeline widget with day grouping
  - Track C (Protocol Primitives): COMPLETE
    - VisualHint with validation
    - HintRegistry with BranchTree factory wired
    - HintContainer for heterarchical rendering
  - Track D (Garden View): COMPLETE
    - GraphLayout with semantic/tree/force layouts (42 tests)
    - CockpitScreen (LOD 1: SURFACE) with 38 tests
    - Slider widget with h/l keys (41 tests)
  - Joy-Inducing Polish: COMPLETE
    - Oblique Strategies easter eggs
    - Heartbeat pulsing for DensityField
    - demo_mode for all screens
  - All LOD levels: FluxScreen (0), CockpitScreen (1), MRIScreen (2)
  - Tests: 988 passing in I-gent module
---

# Implementation Roadmap: Generative TUI

> *"Design it to be generative by construct and constraint—it'll be literally impossible to fuss over them."*

This roadmap enables **parallel development** of all 9+ flows by first establishing the primitive layer.

---

## Parallel Development Strategy

```
Week 1-2: Primitives Layer (Foundation)
    │
    ├── Track A: Entropy Primitives (P10, P9 enhancement)
    ├── Track B: Temporal Primitives (P6, P7)
    └── Track C: Protocol Primitives (P16, P17)
    │
Week 3-4: Flow Implementation (All flows in parallel)
    │
    ├── Flow 1: Agent Cards (uses Track A)
    ├── Flow 2: Garden View (needs P5)
    ├── Flow 3: Cockpit (uses Track A)
    ├── Flow 4: Designer (needs P11)
    ├── Flow 5: Arena (existing primitives)
    ├── Flow 6: Chat Hub (existing primitives)
    ├── Flow 7: Loom (uses Track B)
    ├── Flow 8: Loop Monitor (existing primitives)
    └── Flow 9: MRI View (uses Track A)
```

---

## Track A: Entropy Primitives

### A1: EntropyVisualizer Module

**File**: `impl/claude/agents/i/widgets/entropy.py`

```python
"""
EntropyVisualizer - Maps uncertainty to visual distortion.

The key insight: distortion is signal, not decoration.
"""

from dataclasses import dataclass

@dataclass
class EntropyParams:
    """Visual parameters derived from entropy level."""
    edge_opacity: float      # 1.0 = crisp, 0.5 = fading
    dither_rate: float       # 0.0 = none, 0.4 = heavy
    jitter_amplitude: int    # 0 = stable, 3 = shaking
    glitch_intensity: float  # 0.0 = none, 0.6 = corrupted

def entropy_to_params(entropy: float) -> EntropyParams:
    """
    Map entropy level to visual parameters.

    Args:
        entropy: 0.0 (certain) to 1.0 (confused)

    Returns:
        EntropyParams for rendering
    """
    return EntropyParams(
        edge_opacity=1.0 - entropy * 0.5,
        dither_rate=entropy * 0.4,
        jitter_amplitude=int(entropy * 3),
        glitch_intensity=entropy * 0.6 if entropy > 0.7 else 0.0,
    )
```

### A2: DensityField Enhancement

**File**: `impl/claude/agents/i/widgets/density_field.py`

Add `entropy` parameter and use EntropyVisualizer:

```python
class DensityField(Widget):
    entropy: reactive[float] = reactive(0.0)

    def render(self) -> RenderResult:
        params = entropy_to_params(self.entropy)
        grid = generate_density_grid(
            ...,
            dither_rate=params.dither_rate,
            jitter=params.jitter_amplitude,
        )
        if params.glitch_intensity > 0:
            grid = [add_glitch_effect(line, params.glitch_intensity) for line in grid]
        return "\n".join(grid)
```

### A3: Sparkline Widget

**File**: `impl/claude/agents/i/widgets/sparkline.py`

```python
class Sparkline(Widget):
    """Inline sparkline visualization."""

    DEFAULT_CSS = """
    Sparkline {
        width: auto;
        height: 1;
    }
    """

    values: reactive[list[float]] = reactive([])
    width: reactive[int] = reactive(20)

    def render(self) -> RenderResult:
        return generate_sparkline(self.values, self.width)

def generate_sparkline(values: list[float], width: int = 20) -> str:
    """Generate sparkline string."""
    if not values:
        return "▁" * width

    values = values[-width:]
    min_v, max_v = min(values), max(values)
    range_v = max_v - min_v if max_v > min_v else 1

    chars = "▁▂▃▄▅▆▇█"
    result = []
    for v in values:
        idx = int(((v - min_v) / range_v) * (len(chars) - 1))
        result.append(chars[max(0, min(len(chars) - 1, idx))])

    return "".join(result).ljust(width, "▁")
```

---

## Track B: Temporal Primitives

### B1: CognitiveBranch Data Structure

**File**: `impl/claude/agents/i/data/loom.py`

```python
"""
Cognitive Loom data structures.

Represents agent cognition as a tree, not a log.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CognitiveBranch:
    """A node in the cognitive tree."""

    id: str
    timestamp: datetime
    content: str
    reasoning: str
    selected: bool = True  # Main trunk or ghost branch?
    children: list["CognitiveBranch"] = field(default_factory=list)
    parent_id: Optional[str] = None

    @property
    def glyph(self) -> str:
        """Visual glyph for this node."""
        if not self.selected:
            return "✖"
        return "●" if not self.children else "○"

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def depth(self) -> int:
        """Distance from root."""
        if self.parent_id is None:
            return 0
        # Would need tree context for full implementation
        return 0

@dataclass
class CognitiveTree:
    """The full cognitive history tree."""

    root: CognitiveBranch
    current_id: str  # Currently focused node

    def get_node(self, node_id: str) -> Optional[CognitiveBranch]:
        """Find a node by ID."""
        return self._find_node(self.root, node_id)

    def _find_node(self, node: CognitiveBranch, target_id: str) -> Optional[CognitiveBranch]:
        if node.id == target_id:
            return node
        for child in node.children:
            result = self._find_node(child, target_id)
            if result:
                return result
        return None

    def main_path(self) -> list[CognitiveBranch]:
        """Get the selected path from root to current."""
        path = []
        node = self.root
        while node:
            path.append(node)
            selected_children = [c for c in node.children if c.selected]
            node = selected_children[0] if selected_children else None
        return path
```

### B2: BranchTree Widget

**File**: `impl/claude/agents/i/widgets/branch_tree.py`

```python
"""
BranchTree Widget - Git-graph style cognitive history.

Renders the Cognitive Loom as navigable ASCII tree.
"""

from textual.reactive import reactive
from textual.widget import Widget

LOOM_CHARS = {
    "trunk": "│",
    "branch_start": "├",
    "branch_end": "└",
    "arrow": "─",
    "selected": "●",
    "ghost": "○",
    "rejected": "✖",
    "forecast": ":",
}

class BranchTree(Widget):
    """Render cognitive tree as navigable graph."""

    DEFAULT_CSS = """
    BranchTree {
        width: 100%;
        height: auto;
        padding: 1;
    }

    BranchTree .selected {
        color: #f5d08a;
        text-style: bold;
    }

    BranchTree .ghost {
        color: #6a6560;
    }

    BranchTree .rejected {
        color: #8b7ba5;
    }
    """

    tree: reactive[CognitiveTree | None] = reactive(None)
    show_ghosts: reactive[bool] = reactive(True)

    def render(self) -> RenderResult:
        if not self.tree:
            return "No cognitive history"

        lines = []
        self._render_node(self.tree.root, lines, prefix="", is_last=True)
        return "\n".join(lines)

    def _render_node(
        self,
        node: CognitiveBranch,
        lines: list[str],
        prefix: str,
        is_last: bool,
    ) -> None:
        """Recursively render a node and its children."""
        # Skip ghosts if not showing
        if not node.selected and not self.show_ghosts:
            return

        # Build the line
        connector = LOOM_CHARS["branch_end"] if is_last else LOOM_CHARS["branch_start"]
        glyph = node.glyph
        is_current = self.tree and node.id == self.tree.current_id

        line = f"{prefix}{connector}{LOOM_CHARS['arrow']}{glyph} {node.content[:40]}"
        if is_current:
            line = f"[bold]{line}[/bold]"

        lines.append(line)

        # Recurse into children
        child_prefix = prefix + ("  " if is_last else LOOM_CHARS["trunk"] + " ")
        for i, child in enumerate(node.children):
            self._render_node(
                child,
                lines,
                child_prefix,
                i == len(node.children) - 1,
            )
```

### B3: Timeline Widget

**File**: `impl/claude/agents/i/widgets/timeline.py`

```python
"""
Timeline Widget - Horizontal timeline with activity bars.
"""

from datetime import datetime
from textual.reactive import reactive
from textual.widget import Widget

class Timeline(Widget):
    """Horizontal timeline with activity bars."""

    DEFAULT_CSS = """
    Timeline {
        width: 100%;
        height: 3;
    }
    """

    events: reactive[list[tuple[datetime, float]]] = reactive([])
    cursor_index: reactive[int] = reactive(0)

    def render(self) -> RenderResult:
        if not self.events:
            return "No timeline data"

        # Group by day
        by_day = {}
        for ts, val in self.events:
            day = ts.strftime("%b %d")
            by_day.setdefault(day, []).append(val)

        # Build output
        days = list(by_day.keys())[-5:]  # Last 5 days
        header = " │ ".join(f"{d:^8}" for d in days)
        bars = " │ ".join(self._day_bar(by_day.get(d, [])) for d in days)
        cursor = " " * (self.cursor_index * 10 + 5) + "▲"

        return f"{header}\n{bars}\n{cursor}"

    def _day_bar(self, values: list[float]) -> str:
        """Generate bar for one day."""
        if not values:
            return "▁" * 8
        avg = sum(values) / len(values)
        chars = "▁▂▃▄▅▆▇█"
        idx = int(avg * (len(chars) - 1))
        return chars[idx] * 8
```

---

## Track C: Protocol Primitives

### C1: VisualHint Protocol

**File**: `impl/claude/agents/i/data/hints.py`

```python
"""
VisualHint Protocol - Agents emit these to shape their UI.

The I-gent is a browser that renders agent-emitted hints.
"""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class VisualHint:
    """
    A hint from an agent about how to render it.

    Agents yield these in their Flux output to customize
    their TUI representation.
    """

    type: str  # "density", "table", "graph", "loom", "sparkline", "custom"
    data: dict[str, Any] = field(default_factory=dict)
    position: str = "main"  # "main", "sidebar", "overlay", "footer"
    priority: int = 0  # Higher = render first
    agent_id: str = ""  # Which agent emitted this

    def __post_init__(self):
        # Validate type
        valid_types = {"density", "table", "graph", "loom", "sparkline", "text", "custom"}
        if self.type not in valid_types:
            raise ValueError(f"Unknown hint type: {self.type}. Valid: {valid_types}")
```

### C2: HintRegistry

**File**: `impl/claude/agents/i/data/hint_registry.py`

```python
"""
HintRegistry - Maps VisualHints to Widgets.

Extensible registry allowing agents to register custom hint types.
"""

from typing import Callable, Dict
from textual.widget import Widget
from textual.widgets import Static, DataTable

from .hints import VisualHint

# Type alias for factory functions
HintFactory = Callable[[VisualHint], Widget]

class HintRegistry:
    """Registry mapping hint types to widget factories."""

    def __init__(self):
        self._factories: Dict[str, HintFactory] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in hint types."""
        self.register("text", self._text_factory)
        self.register("table", self._table_factory)
        self.register("density", self._density_factory)
        self.register("sparkline", self._sparkline_factory)

    def register(self, hint_type: str, factory: HintFactory) -> None:
        """Register a factory for a hint type."""
        self._factories[hint_type] = factory

    def render(self, hint: VisualHint) -> Widget:
        """Render a hint to a widget."""
        factory = self._factories.get(hint.type)
        if factory:
            return factory(hint)
        return Static(f"Unknown hint type: {hint.type}")

    def _text_factory(self, hint: VisualHint) -> Widget:
        return Static(hint.data.get("text", ""))

    def _table_factory(self, hint: VisualHint) -> Widget:
        table = DataTable()
        table.add_columns("Key", "Value")
        for k, v in hint.data.items():
            table.add_row(str(k), str(v))
        return table

    def _density_factory(self, hint: VisualHint) -> Widget:
        from ..widgets.density_field import DensityField
        return DensityField(
            agent_id=hint.agent_id,
            activity=hint.data.get("activity", 0.5),
        )

    def _sparkline_factory(self, hint: VisualHint) -> Widget:
        from ..widgets.sparkline import Sparkline
        return Sparkline(values=hint.data.get("values", []))

# Global registry instance
_registry: HintRegistry | None = None

def get_hint_registry() -> HintRegistry:
    """Get the global hint registry."""
    global _registry
    if _registry is None:
        _registry = HintRegistry()
    return _registry
```

---

## Flow Implementations (Parallel)

Once tracks A, B, C are complete, all flows can be implemented in parallel:

### Flow 1: Agent Cards (Enhanced)

Use existing `AgentCard` + add entropy visualization:

```python
class EnhancedAgentCard(AgentCard):
    """AgentCard with entropy-aware rendering."""

    entropy: reactive[float] = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield DensityField(
            activity=self.snapshot.activity,
            entropy=self.entropy,  # NEW
        )
        yield Sparkline(values=self.history)
        yield CompactHealthBar(health=self.health)
```

### Flow 7: Cognitive Loom (New)

Create `LoomScreen`:

```python
class LoomScreen(Screen):
    """The Cognitive Loom - branching history visualization."""

    BINDINGS = [
        ("j", "nav_down", "Down"),
        ("k", "nav_up", "Up"),
        ("h", "nav_left", "Branch left"),
        ("l", "nav_right", "Branch right"),
        ("c", "crystallize", "Crystallize"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield BranchTree(id="loom")
        yield Timeline(id="timeline")
        yield Footer()

    def action_crystallize(self) -> None:
        """Crystallize current moment to D-gent memory."""
        current = self.tree.get_node(self.tree.current_id)
        if current:
            # Emit to D-gent
            self.app.crystallize_memory(current)
```

### Flow 9: MRI View (New)

Deep internal view with token heatmaps:

```python
class MRIView(Screen):
    """Internal view of agent cognition."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield TokenHeatmap(id="context-window")
            yield VectorStoreViz(id="retrieval")
        yield EntropyPanel(id="entropy")
        yield Footer()
```

---

## Test Strategy

Each primitive and flow needs tests:

```
impl/claude/agents/i/widgets/_tests/
├── test_sparkline.py          # P2
├── test_entropy.py            # P10
├── test_branch_tree.py        # P6
├── test_timeline.py           # P7

impl/claude/agents/i/data/_tests/
├── test_loom.py               # CognitiveBranch/Tree
├── test_hints.py              # P16
├── test_hint_registry.py      # P17

impl/claude/agents/i/screens/_tests/
├── test_loom_screen.py        # Flow 7
├── test_mri_view.py           # Flow 9
```

---

## Exit Criteria

### Phase 1 Complete (Primitives) ✓

- [x] EntropyVisualizer implemented and tested
- [x] Sparkline widget implemented and tested
- [x] DensityField enhanced with entropy parameter
- [x] BranchTree widget implemented and tested
- [x] Timeline widget implemented and tested
- [x] VisualHint protocol defined
- [x] HintRegistry implemented and tested
- [x] GraphLayout implemented with semantic/tree/force (42 tests)
- [x] Slider implemented with keyboard nav (41 tests)

### Phase 2 Complete (Flows) ✓

- [x] LOD 0: FluxScreen (Agent Cards)
- [x] LOD 1: CockpitScreen (Operational view, 38 tests)
- [x] LOD 2: MRIScreen (Deep inspection)
- [x] Zoom navigation (+/-) works
- [x] Loom navigation (h/j/k/l) works
- [x] VisualHints from agents render correctly
- [x] demo_mode for all screens

### Phase 3 Complete (Polish) ✓

- [x] Heartbeat pulsing in DensityField
- [x] Oblique Strategies easter eggs when entropy > 0.9
- [x] Mypy strict: 0 errors
- [x] 988 tests passing

---

## Cross-References

- **Framework spec**: `plans/interfaces/alethic-workbench.md`
- **Primitives spec**: `plans/interfaces/primitives.md`
- **Original brainstorm**: `docs/ux-flows-brainstorm.md`
- **Existing widgets**: `impl/claude/agents/i/widgets/`

---

*"Generative by construct and constraint."*
