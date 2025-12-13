---
path: interfaces/primitives
status: active
progress: 100
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [interfaces/alethic-workbench]
session_notes: |
  Formal specification of the minimal primitive set for generative TUI.
  These primitives compose to generate the entire design space.
  Category-theoretic foundation: primitives are morphisms, composition is primary.

  2025-12-12: ALL PRIMITIVES COMPLETE (17/17)
  - P1 DensityField: COMPLETE with entropy parameter + heartbeat animation
  - P2 Sparkline: COMPLETE as widget
  - P5 GraphLayout: COMPLETE with semantic/tree/force layouts (42 tests)
  - P6 BranchTree: COMPLETE with full navigation
  - P7 Timeline: COMPLETE
  - P10 EntropyVisualizer: COMPLETE
  - P11 Slider: COMPLETE with keyboard nav + callbacks (41 tests)
  - P16 VisualHint: COMPLETE with validation
  - P17 HintRegistry: COMPLETE with loom factory wired to BranchTree
  - CockpitScreen: COMPLETE (LOD 1: SURFACE) with 38 tests
  - Joy-inducing: Oblique Strategies easter eggs, heartbeat pulsing
  - Tests: 988 passing in i-gent module
---

# Generative TUI Primitives

> *"The right amount of complexity is the minimum needed for the current task."*

This document specifies the **minimal complete set** of primitives that generate all possible kgents interfaces.

---

## The Completeness Criterion

A primitive set is **complete** if any reasonable agent interface can be composed from these primitives. We aim for:

1. **Minimal**: No redundant primitives
2. **Orthogonal**: Each primitive does one thing
3. **Composable**: Primitives combine freely
4. **Generative**: Novel interfaces emerge from composition

---

## Category 1: Density Primitives (Agent Representation)

These primitives render agent state as visual fields.

### P1: DensityField

**Existing**: `impl/claude/agents/i/widgets/density_field.py`

Maps `(activity: float, phase: Phase, entropy: float) → ASCII grid`

```
Parameters:
  activity: 0.0 (idle) → 1.0 (intense)
  phase: DORMANT | WAKING | ACTIVE | WANING | VOID
  entropy: 0.0 (certain) → 1.0 (confused)

Output:
  ░░░▒▒▓▓█░░░░░░   (low activity)
  ▓▓▓▓▓▓█▓▓▓▓▓▓   (high activity)
  ▚▞▛▜▙▟▚▞▛▜▙▟   (void/glitch)
```

**Enhancement needed**: Add `entropy` parameter for functional distortion.

### P2: Sparkline

Maps `list[float] → single-line bar chart`

```
Parameters:
  values: list[float]  # Time series
  width: int           # Character width

Output:
  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁   (token burn rate history)
```

**Status**: Partially implemented in `terrarium_tui.py:_sparkline()`, needs widget form.

### P3: ProgressBar

Maps `(value: float, max: float) → filled bar`

```
Parameters:
  value: float
  max: float
  width: int

Output:
  ████████░░░░░░░░   (50% full)
```

**Status**: Implemented in `terrarium_tui.py:_progress_bar()`.

---

## Category 2: Connection Primitives (Inter-Agent Relations)

These primitives render relationships between agents.

### P4: FlowArrow

**Existing**: `impl/claude/agents/i/widgets/flow_arrow.py`

Maps `(throughput: float, direction: Direction) → line with arrow`

```
Parameters:
  throughput: 0.0 → 1.0
  direction: HORIZONTAL | VERTICAL | DIAGONAL

Output (by throughput):
  ════════►   (HIGH, ≥0.7)
  ────────►   (MEDIUM, 0.3-0.7)
  ........►   (LOW, <0.3)
  : : : : ►   (LAZY, 0)
```

### P5: GraphLayout

**Existing**: `impl/claude/agents/i/widgets/graph_layout.py`

Maps `(nodes: list[str], edges: list[(str, str)]) → 2D layout`

Positions nodes and draws FlowArrows between them.

```
Parameters:
  nodes: list[str]
  edges: list[tuple[str, str]]
  layout_algorithm: "force" | "tree" | "semantic"

Output:
    ┌───────┐
    │  B    │←─────┐
    └───┬───┘      │
        │          │
    ┌───┴───┐  ┌───┴───┐
    │   L   │──│   D   │
    └───────┘  └───────┘
```

**Status**: ✓ Implemented with:
- Semantic layout (agent taxonomy: K at center)
- Tree layout (hierarchical)
- Force-directed layout (physics simulation)
- 42 passing tests

---

## Category 3: Temporal Primitives (History/Time)

These primitives render temporal structures.

### P6: BranchTree

Maps `CognitiveBranch tree → git-graph style visualization`

```
Parameters:
  root: CognitiveBranch
  current_id: str
  show_ghosts: bool

Output:
  │ ○ Start
  │ ├─○ Plan A (Efficient)
  │ │ └──✖ Rejected: unsafe
  │ └─○ Plan B [SELECTED]
  │   └──● CURRENT STATE
  :     :.. ○ Forecast
```

**Status**: Not yet implemented. Key new primitive.

### P7: Timeline

Maps `list[(timestamp, value)] → horizontal timeline with markers`

```
Parameters:
  events: list[tuple[datetime, float]]
  width: int

Output:
  │ Dec 12 │ Dec 11 │ Dec 10 │ Dec 9  │
  │ ▇▇▇▇▇▇ │ ▅▅▅▅▅▅ │ ▃▃▃▃▃▃ │ ▁▁▁▁▁▁ │
       ▲
    cursor
```

**Status**: Not yet implemented.

---

## Category 4: Waveform Primitives (Processing State)

These primitives render processing patterns.

### P8: Waveform

**Existing**: `impl/claude/agents/i/widgets/waveform.py`

Maps `OperationType → animated pattern`

```
Parameters:
  operation_type: LOGICAL | CREATIVE | WAITING | ERROR
  animating: bool
  offset: int

Output:
  LOGICAL:  ╭╮╭╮╭╮╭╮╭╮   (square wave)
  CREATIVE: ~∿~∿~∿~∿~∿   (noisy sine)
  WAITING:  ──────────   (flat line)
  ERROR:    ▓░▓░▓░▓░▓░   (glitch)
```

---

## Category 5: Entropy Primitives (Uncertainty Visualization)

These primitives make uncertainty visible.

### P9: GlitchEffect

**Existing**: `impl/claude/agents/i/widgets/glitch.py`

Maps `(text: str, intensity: float) → corrupted text`

```
Parameters:
  text: str
  intensity: 0.0 → 1.0
  glitch_type: ZALGO | SUBSTITUTE | DISTORT

Output:
  "Hello" → "H̸̢e̶͎l̷̰ļ̴o"   (ZALGO)
  "Hello" → "▚e▛▜o"          (SUBSTITUTE)
  "─────" → "═╲═╱═"          (DISTORT border)
```

### P10: EntropyVisualizer

Maps `entropy: float → visual distortion parameters`

```
Parameters:
  entropy: 0.0 (certain) → 1.0 (confused)

Output:
  {
    edge_opacity: 1.0 - entropy * 0.5,
    dither_rate: entropy * 0.4,
    jitter_amplitude: entropy * 3,
    glitch_intensity: entropy * 0.6 if entropy > 0.7 else 0
  }
```

**Status**: Not yet implemented. Composes with DensityField.

---

## Category 6: Interaction Primitives (Direct Manipulation)

These primitives enable parameter manipulation.

### P11: Slider

**Existing**: `impl/claude/agents/i/widgets/slider.py`

Maps `(value: float, min: float, max: float) → draggable control`

```
Parameters:
  value: float
  min_val: float
  max_val: float
  label: str
  on_change: callback

Output:
  Temperature: ○───────────●──────── 0.7
               deterministic  creative

Keyboard:
  h/left: Decrease by step
  l/right: Increase by step
  H: Jump to min
  L: Jump to max
  0-9: Set to 0-90%
```

**Status**: ✓ Implemented with:
- Reactive value updates
- Keyboard navigation (h/l or arrows)
- Numeric shortcuts (0-9)
- Value callbacks
- 41 passing tests

### P12: Button

Maps `label: str → clickable action`

```
Parameters:
  label: str
  action: str  # Action name to trigger
  style: "primary" | "danger" | "ghost"

Output:
  [Crystallize]  [Pause]  [✖ Delete]
```

**Status**: Textual provides this natively.

---

## Category 7: Container Primitives (Layout)

These primitives organize other primitives.

### P13: Card

Maps `content: Widget → bordered container with header`

```
Parameters:
  title: str
  content: Widget
  footer: Widget | None

Output:
  ┌─ AGENT: K-gent ────────────┐
  │ ░░░▒▒▓▓█░░░░░░             │
  │ ░░░░K░░░░░░░░░             │
  ├────────────────────────────┤
  │ ▁▂▃▄▅▆▇█ 12t/m             │
  └────────────────────────────┘
```

**Status**: Implemented as `AgentCard` in `screens/flux.py`.

### P14: Grid

Maps `list[Widget] → arranged grid`

```
Parameters:
  widgets: list[Widget]
  cols: int
  rows: int

Output:
  [Card1] [Card2] [Card3]
  [Card4] [Card5] [Card6]
```

**Status**: Textual provides `Grid` container.

### P15: Overlay

Maps `Widget → modal layer on top of screen`

```
Parameters:
  content: Widget
  dismissable: bool
  position: "center" | "bottom" | "right"

Output:
  (renders on top of current screen)
```

**Status**: Implemented in `screens/overlays/`.

---

## Category 8: Protocol Primitives (Agent Communication)

### P16: VisualHint

The agent-to-UI protocol.

```python
@dataclass
class VisualHint:
    type: str          # Widget type to render
    data: dict         # Type-specific payload
    position: str      # Where to place it
    priority: int      # Render order
```

**Status**: Not yet implemented. Key generative primitive.

### P17: HintRegistry

Maps `VisualHint → Widget`.

```python
class HintRegistry:
    def render(self, hint: VisualHint) -> Widget:
        factory = self._factories[hint.type]
        return factory(hint)
```

**Status**: Not yet implemented.

---

## Composition Rules

### Rule 1: Primitives compose via containment

```python
# AgentCard = Card containing (DensityField, Sparkline, HealthBar)
AgentCard = Card(
    title="K-gent",
    content=Vertical(
        DensityField(activity=0.6),
        Sparkline([1,2,3,4,5]),
        HealthBar(x=0.8, y=0.6, z=0.9),
    )
)
```

### Rule 2: Entropy propagates outward

When an inner primitive has high entropy, it affects containing primitives:

```python
# High entropy in DensityField → Card border dissolves
if density.entropy > 0.7:
    card.border_style = "dissolving"
```

### Rule 3: VisualHints override defaults

Agents can override their default representation:

```python
# B-gent prefers table view
class BGent:
    def render_hint(self) -> VisualHint:
        return VisualHint(type="table", data=self.ledger)
```

---

## The Complete Primitive Set

| # | Primitive | Category | Status |
|---|-----------|----------|--------|
| P1 | DensityField | Density | ✓ Implemented (with entropy + heartbeat) |
| P2 | Sparkline | Density | ✓ Implemented (widget form) |
| P3 | ProgressBar | Density | ✓ Implemented |
| P4 | FlowArrow | Connection | ✓ Implemented |
| P5 | GraphLayout | Connection | ✓ Implemented (semantic/tree/force, 42 tests) |
| P6 | BranchTree | Temporal | ✓ Implemented (with navigation) |
| P7 | Timeline | Temporal | ✓ Implemented |
| P8 | Waveform | Waveform | ✓ Implemented |
| P9 | GlitchEffect | Entropy | ✓ Implemented (with Oblique Strategies) |
| P10 | EntropyVisualizer | Entropy | ✓ Implemented |
| P11 | Slider | Interaction | ✓ Implemented (h/l keys, 0-9 shortcuts, 41 tests) |
| P12 | Button | Interaction | Native |
| P13 | Card | Container | ✓ Implemented |
| P14 | Grid | Container | Native |
| P15 | Overlay | Container | ✓ Implemented |
| P16 | VisualHint | Protocol | ✓ Implemented |
| P17 | HintRegistry | Protocol | ✓ Implemented (with loom factory) |

**Implemented**: 17/17 (100%) ✓
**All primitives complete!**

---

## Theorem: Completeness

**Claim**: The 17 primitives above can generate all 9+ proposed interfaces.

**Proof sketch**:

1. **Agent Cards** (Flow 1): P1 + P2 + P3 + P13
2. **Garden View** (Flow 2): P5 + P4 + P13
3. **Cockpit** (Flow 3): P1 + P2 + P8 + P13 + P14
4. **Agent Designer** (Flow 4): P11 + P12 + P15
5. **Arena** (Flow 5): P1 + P4 + P14
6. **Conversation Hub** (Flow 6): P1 + P13 + chat widget
7. **History Explorer** (Flow 7): P6 + P7 + P13
8. **Autonomous Loop** (Flow 8): P1 + P4 + P8 + P14
9. **MRI View**: P1 + P10 + heatmap

Additional interfaces generated by P16 (VisualHint) allowing agents to emit custom representations.

QED.

---

## Implementation Priority

### Phase 1: Core Entropy (Critical Path)

1. P10: EntropyVisualizer
2. P2: Sparkline (as widget)

These enable functional entropy visualization.

### Phase 2: Temporal Navigation

3. P6: BranchTree
4. P7: Timeline

These enable the Cognitive Loom.

### Phase 3: Generative Protocol

5. P16: VisualHint
6. P17: HintRegistry

These enable agent-driven UI.

### Phase 4: Direct Manipulation

7. P11: Slider
8. P5: GraphLayout

These enable advanced interaction.

---

## Cross-References

- **Parent plan**: `plans/interfaces/alethic-workbench.md`
- **Existing widgets**: `impl/claude/agents/i/widgets/`
- **Widget tests**: `impl/claude/agents/i/widgets/_tests/`
- **Category theory**: `spec/c-gents/` (composability)

---

*"Three similar lines of code is better than a premature abstraction."*
