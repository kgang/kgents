---
path: interfaces/alethic-workbench
status: complete
progress: 112.5
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [interfaces/agent-cards, interfaces/cognitive-loom, interfaces/entropy-scanner]
session_notes: |
  ALETHIC WORKBENCH COMPLETE (112.5%)

  === Mechanical (100%) ===
  - All 17 primitives implemented
  - P5 GraphLayout: semantic/tree/force layouts (42 tests)
  - P11 Slider: h/l keys, 0-9 shortcuts (41 tests)
  - CockpitScreen (LOD 1): 38 tests
  - All LOD levels: FluxScreen (0), CockpitScreen (1), MRIScreen (2)
  - All screens have demo_mode
  - 988 tests passing in I-gent module

  === Robustness (+5%) ===
  - Mypy strict: 0 errors
  - All widgets handle None/empty gracefully
  - Boundary conditions tested

  === Polish (+5%) ===
  - Oblique Strategies easter eggs when entropy > 0.9
  - Heartbeat pulsing in DensityField
  - Materialization/dematerialization animations

  === Philosophy (+2.5%) ===
  - Docstrings include WHAT/WHY/HOW/FEEL
  - Code comments reference principles
  - Category-theoretic foundations honored
---

# The Alethic Workbench: A Generative TUI Framework

> *"Don't just look at the agent. Look through the agent."*

**Status**: Proposed
**Principle Alignment**: Generative (by construction), Tasteful, Heterarchical
**Cross-refs**: `docs/ux-flows-brainstorm.md`, `plans/agents/terrarium.md`, I-gent widgets

---

## Executive Summary

The original UX brainstorm proposed 8 flows. The critique proposed 1 more (Cognitive Loom). Rather than implementing 9 fixed screens, we design a **generative framework** where:

1. **Minimal primitives** compose into arbitrary interfaces
2. **Visual grammar** is isomorphic to semantic state (entropy = visual distortion)
3. **Agents emit VisualHints** that shape their own representation
4. **Navigation is topological**, not hierarchical (LOD zoom, branching history)

This document specifies the primitives. Implementation flows naturally.

---

## The Dashboard Fallacy (Diagnosis)

The original proposal treats agents as **servers to monitor**:
- CPU%, memory, logs
- Linear event streams
- Fixed panel layouts

But agents are **cognition in motion**:
- Decision trees with rejected branches (the Shadow)
- Uncertainty as first-class visual property
- Self-determined representation (heterarchical)

**Resolution**: The interface is a **Natural Transformation** from `AgentState` to `PixelState`, preserving structure (branching, uncertainty, entropy).

---

## Core Architecture: The Generative Triad

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE GENERATIVE TRIAD                              │
│                                                                      │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐       │
│   │  VISUAL       │    │  SEMANTIC     │    │  TEMPORAL     │       │
│   │  GRAMMAR      │───▶│  ZOOM         │───▶│  TOPOLOGY     │       │
│   │               │    │  (LOD)        │    │  (Loom)       │       │
│   └───────────────┘    └───────────────┘    └───────────────┘       │
│          │                    │                    │                 │
│          ▼                    ▼                    ▼                 │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │               WIDGET ALGEBRA                                 │   │
│   │  DensityField ⊕ FlowArrow ⊕ Waveform ⊕ ... = CompositeView  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │               VISUAL HINT PROTOCOL                           │   │
│   │  Agent yields VisualHint → I-gent renders dynamically       │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Visual Grammar: Entropy-Isomorphic Rendering

### The Principle

Visual distortion is **strictly isomorphic** to entropy. Not aesthetic—**signal**.

| Entropy Level | Visual Effect | Semantic Meaning |
|---------------|---------------|------------------|
| Low (certainty) | Crisp, high-contrast blocks | Agent is confident |
| Medium (exploring) | Slight dithering, softer edges | Agent is considering options |
| High (confusion) | Heavy dithering, jittering | Agent is uncertain/hallucinating |
| Void (entropy sink) | Glitch patterns, Zalgo | Agent drew from Accursed Share |

### The Functional Glitch Principle

> *"You can spot a hallucinating agent instantly not because it looks 'cool,' but because its boundaries are literally dissolving."*

```python
@dataclass
class EntropyVisualizer:
    """
    Maps entropy → visual distortion.

    The key insight: distortion is not decoration, it's signal.
    """

    def render_density(
        self,
        activity: float,
        entropy: float,  # 0.0 = certain, 1.0 = confused
        phase: Phase,
    ) -> str:
        """
        Render density field with entropy-based distortion.

        - Low entropy: DENSITY_CHARS only
        - Medium entropy: Add dithering
        - High entropy: Jittering + character substitution
        - Void: Full glitch
        """
        ...

    def edge_dissolution(
        self,
        border: str,
        entropy: float,
    ) -> str:
        """
        Dissolve borders as entropy increases.

        Sharp box → wavy box → broken box → no box
        """
        ...
```

### Existing Widget Mapping

| Widget | Entropy Expression |
|--------|-------------------|
| `DensityField` | Activity level + glitch intensity |
| `FlowArrow` | Connection type (HIGH→LOW→LAZY) |
| `Waveform` | LOGICAL/CREATIVE/ERROR patterns |
| `Glitch` | Zalgo depth, substitution rate |

---

## 2. Semantic Zoom (Level of Detail)

### The Principle

Replace discrete screens with **continuous zoom levels**. Mouse wheel (or `+/-`) zooms through:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SEMANTIC ZOOM LEVELS                              │
│                                                                      │
│  LOD 0: ORBIT         LOD 1: SURFACE         LOD 2: INTERNAL        │
│  ┌───────────┐        ┌───────────────┐      ┌───────────────┐      │
│  │░░░K░░░░░░░│        │ K-gent        │      │ Context Window│      │
│  │▁▂▃▂▁ 12t/m│        │ ────────────  │      │ ╔═══════════╗ │      │
│  └───────────┘        │ Phase: ACTIVE │      │ ║Token heat ║ │      │
│                       │ Temp: 0.67    │      │ ║map + attn ║ │      │
│  "Density Card"       │ Thoughts: ... │      │ ╚═══════════╝ │      │
│  Health at a glance   │ Semaphores: 2 │      │               │      │
│                       │               │      │ Vector store  │      │
│                       │ "Cockpit"     │      │ retrieval viz │      │
│                       │ Intervention  │      │               │      │
│                       └───────────────┘      │ "MRI Scan"    │      │
│                                              │ Debug internals│      │
│                                              └───────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation: LOD Functor

```python
class LODLevel(Enum):
    ORBIT = 0      # Density card
    SURFACE = 1    # Cockpit
    INTERNAL = 2   # MRI scan

@dataclass
class LODProjector:
    """
    Functor: AgentState × LODLevel → Widget

    Projects agent state to the appropriate widget at each LOD.
    """

    def project(
        self,
        state: AgentSnapshot,
        level: LODLevel,
    ) -> Widget:
        """Generate the widget for this LOD level."""
        match level:
            case LODLevel.ORBIT:
                return AgentCard(state)  # Existing
            case LODLevel.SURFACE:
                return CockpitView(state)  # Detailed
            case LODLevel.INTERNAL:
                return MRIView(state)  # Token-level
```

### Zoom Navigation

| Input | Action |
|-------|--------|
| `+` or scroll up | Zoom in (ORBIT → SURFACE → INTERNAL) |
| `-` or scroll down | Zoom out |
| `Enter` | Zoom in on focused agent |
| `Esc` | Zoom out |

---

## 3. Temporal Topology: The Cognitive Loom

### The Principle

Agent cognition is a **tree search**, not a linear log. The Loom visualizes:
- Main trunk: Selected actions
- Ghost branches: Rejected hypotheses (the Shadow)
- Potential futures: Forecasts

```
┌─ LOOM: K-gent ──────────────────────────────────────────────┐
│ Time  │ Path                                                │
│ 12:00 │ ○ Start                                             │
│       │ ├─○ Plan A (Reasoning: Efficient)                   │
│       │ │ │                                                 │
│       │ │ ├──○ Action: grep (Failed)                        │
│ 12:05 │ │ └──✖ Action: find (Rejected: unsafe)              │
│       │ │                                                   │
│       │ └─○ Plan B (Reasoning: Thorough) [SELECTED]         │
│ 12:06 │   │                                                 │
│       │   └──● CURRENT STATE                                │
│       │      :                                              │
│       │      :.. ○ Potential Future (Forecast)              │
└───────┴─────────────────────────────────────────────────────┘

Navigation:
  j/k: Move through time (up/down)
  h/l: Navigate branches (left/right)
  c:   Crystallize moment → D-gent memory
```

### The Branch Grammar

```python
@dataclass
class CognitiveBranch:
    """A node in the cognitive tree."""

    id: str
    timestamp: datetime
    content: str
    reasoning: str
    selected: bool  # Main trunk or ghost?
    children: list[CognitiveBranch]

    # Visual properties derived from state
    @property
    def glyph(self) -> str:
        if self.selected:
            return "●" if self == current else "○"
        return "✖"  # Rejected

    @property
    def opacity(self) -> float:
        """Ghost branches fade over time."""
        if self.selected:
            return 1.0
        age = (datetime.now() - self.timestamp).seconds
        return max(0.2, 1.0 - age / 3600)  # Fade over 1 hour
```

### Rendering with Box-Drawing

Uses the same patterns as `git log --graph`:

```python
LOOM_CHARS = {
    "trunk": "│",
    "branch_start": "├",
    "branch_end": "└",
    "arrow_right": "─",
    "arrow_down": "▼",
    "current": "●",
    "ghost": "○",
    "rejected": "✖",
    "forecast": ":",
}
```

---

## 4. Visual Hint Protocol (Generative UI)

### The Principle

The I-gent is a **browser** that renders agent-emitted layout hints. Agents define their own representation.

```python
@dataclass
class VisualHint:
    """
    Agents yield these to shape their TUI representation.

    The I-gent dynamically injects the corresponding widget.
    This makes the UI heterarchical—the agent, not the framework,
    decides how to be seen.
    """

    type: str  # "table", "graph", "density", "loom", "custom"
    data: dict[str, Any]  # Type-specific payload
    position: str = "main"  # "main", "sidebar", "overlay", "footer"
    priority: int = 0  # Higher = render first


# Example: B-gent (Banker) emits table
yield VisualHint(
    type="table",
    data={"Assets": 100, "Liabilities": 50, "Net": 50},
    position="sidebar"
)

# Example: Y-gent (Topology) emits graph
yield VisualHint(
    type="graph",
    nodes=["A", "B", "C"],
    edges=[("A", "B"), ("B", "C")],
    position="main"
)
```

### The Hint Registry

```python
class VisualHintRegistry:
    """
    Maps hint types to widget factories.

    Extensible: new agents can register new hint types.
    """

    _factories: dict[str, Callable[[VisualHint], Widget]] = {
        "table": lambda h: DataTable(h.data),
        "graph": lambda h: GraphWidget(h.data),
        "density": lambda h: DensityField(**h.data),
        "loom": lambda h: LoomWidget(h.data),
        "sparkline": lambda h: SparklineWidget(h.data),
    }

    def render(self, hint: VisualHint) -> Widget:
        factory = self._factories.get(hint.type)
        if factory:
            return factory(hint)
        return Static(f"Unknown hint type: {hint.type}")
```

---

## 5. Widget Algebra: The Composition Primitives

### Existing Primitives (Already Implemented)

| Primitive | File | Purpose |
|-----------|------|---------|
| `DensityField` | `widgets/density_field.py` | Agent as density cluster |
| `Glitch` | `widgets/glitch.py` | Entropy visualization |
| `FlowArrow` | `widgets/flow_arrow.py` | Connection bandwidth |
| `Waveform` | `widgets/waveform.py` | Processing pattern |
| `HealthBar` | `widgets/health_bar.py` | XYZ health |
| `MetricsPanel` | `widgets/metrics_panel.py` | Pressure/flow/temp |
| `AgentHUD` | `widgets/agentese_hud.py` | Path invocation display |

### New Primitives Required

| Primitive | Purpose | Composition Of |
|-----------|---------|----------------|
| `EntropyField` | Functional distortion | DensityField + entropy param |
| `BranchTree` | Git-graph style | Box-drawing + opacity |
| `Sparkline` | Inline history | Character bars |
| `Slider` | Direct manipulation | Input + state |
| `GraphWidget` | Node-edge layout | Points + FlowArrows |

### The Composition Algebra

```python
# Widgets compose via Textual's Container
AgentCard = DensityField + Sparkline + HealthBar
CockpitView = AgentPanel + SemaphorePanel + MetricsPanel
LoomScreen = BranchTree + Sparkline + TimelineBar

# Visual hints compose dynamically
def render_hints(hints: list[VisualHint]) -> Container:
    """Render all hints into a container."""
    widgets = [registry.render(h) for h in sorted(hints, key=lambda h: -h.priority)]
    return Container(*widgets)
```

---

## 6. The Nine Interfaces (Generated, Not Built)

With the primitives above, all 9 flows from the brainstorm emerge naturally:

| # | Flow | Generation |
|---|------|------------|
| 1 | Agent Cards | `LODProjector(ORBIT)` |
| 2 | Garden View | `GraphWidget` with semantic positions |
| 3 | Cockpit | `LODProjector(SURFACE)` |
| 4 | Agent Designer | Wizard screen + VisualHints |
| 5 | Arena | Multi-agent + observer mode |
| 6 | Conversation Hub | Chat widget + AgentCards |
| 7 | History Explorer | **Cognitive Loom** (BranchTree) |
| 8 | Autonomous Loop | Pipeline + Semaphore cards |
| 9 | MRI View | `LODProjector(INTERNAL)` + token heatmap |

**Plus countably infinite more**: Any agent can emit VisualHints to define custom interfaces.

---

## 7. Direct Manipulation Widgets

### Entropy Slider

```
┌─ ENTROPY ──────────────────┐
│ ○───────────────●──────────│  Temperature: 0.7
│ deterministic   creative   │
└────────────────────────────┘
```

Dragging updates agent temperature in real-time.

### Memory Forge

Select a Loom node → Press `c` → Crystallize to D-gent memory.

### Emergency Brake

`Space` globally pauses all Flux streams for inspection.

---

## 8. Implementation Phases

### Phase 1: Entropy-Isomorphic Density (Week 1)

**Goal**: Upgrade `DensityField` with functional entropy visualization.

**Tasks**:
1. Add `entropy: float` parameter to DensityField
2. Implement edge dissolution based on entropy
3. Connect to agent uncertainty metrics

**Exit Criteria**: High-entropy agents have visibly dissolving borders.

### Phase 2: Semantic Zoom (Week 2)

**Goal**: Implement LOD projection with +/- navigation.

**Tasks**:
1. Create `LODProjector` functor
2. Implement `CockpitView` (LOD 1)
3. Add zoom keybindings

**Exit Criteria**: Can zoom from card → cockpit → MRI.

### Phase 3: Cognitive Loom (Week 3)

**Goal**: Replace linear History Explorer with branching Loom.

**Tasks**:
1. Create `BranchTree` widget
2. Implement tree navigation (h/j/k/l)
3. Add crystallization (c → D-gent)

**Exit Criteria**: Can navigate decision tree, see rejected branches.

### Phase 4: Visual Hint Protocol (Week 4)

**Goal**: Agents can emit VisualHints to shape their UI.

**Tasks**:
1. Define `VisualHint` protocol
2. Create `VisualHintRegistry`
3. Wire FluxAgent to emit hints

**Exit Criteria**: B-gent emits table, I-gent renders it.

---

## 9. Keybinding Unification

### Global

| Key | Action | Context |
|-----|--------|---------|
| `q` | Quit / Back | Universal |
| `?` | Help overlay | Universal |
| `:` | Command mode | Universal |
| `/` | Search / Filter | Universal |
| `Space` | Emergency brake | Pause all streams |

### Navigation (Vim-style)

| Key | Action |
|-----|--------|
| `j/k` | Down/Up |
| `h/l` | Left/Right (also branch nav in Loom) |
| `+/-` | Zoom in/out (LOD) |
| `Enter` | Focus/zoom in |
| `Esc` | Back/zoom out |

### Agent Actions

| Key | Action |
|-----|--------|
| `d` | Describe (details) |
| `l` | Loom (history tree) |
| `e` | Edit config |
| `c` | Crystallize (memory) |
| `g` | Trigger glitch (demo) |

---

## 10. Principle Assessment

| Principle | How This Design Honors It |
|-----------|--------------------------|
| **Generative** | Primitives compose into arbitrary interfaces |
| **Tasteful** | Entropy = signal, not decoration |
| **Curated** | Minimal primitives, maximum expressivity |
| **Composable** | Widget algebra, VisualHint protocol |
| **Heterarchical** | Agents define their own representation |
| **Ethical** | Shadow branches visible (transparency) |
| **Joy-Inducing** | Dissolving borders, crystallization ritual |

---

## Cross-References

- **Critique source**: User message (2025-12-12)
- **Original flows**: `docs/ux-flows-brainstorm.md`
- **Existing widgets**: `impl/claude/agents/i/widgets/`
- **Existing screens**: `impl/claude/agents/i/screens/`
- **Data sources**: `impl/claude/agents/i/data/`
- **Terrarium integration**: `plans/agents/terrarium.md`

---

*"The interface is not a window—it is a membrane. Through it, we touch the agents."*
