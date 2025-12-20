---
path: protocols/servo-substrate
status: proposal
spec_type: protocol
category: projection
dependencies: [protocols/warp-primitives, protocols/projection]
enables: [services/servo-shell]
agentese_paths:
  - world.terrarium.view.*
projection_targets: [servo, marimo, tui, cli, json]
last_touched: 2025-12-20
touched_by: claude-opus-4
---

# Servo Projection Substrate Protocol

**Status:** Proposal
**Implementation:** `impl/claude/protocols/agentese/projection/servo.py` (0 tests)

> *"Servo is not 'a browser' inside kgents. It is the projection substrate that renders the ontology."*

---

## Purpose

Define Servo as the primary projection target for kgents, replacing the current webapp as the operational UI surface. Servo provides multi-webview heterarchy, WebGPU rendering, and Rust-native law enforcement.

---

## Core Insight

**The webapp is not the UI—it's the composition boundary.** Servo primitives supersede React/webapp logic for operational surfaces. The webapp becomes a shallow shell that composes projection outputs.

---

## Type Signatures

### ServoScene (Projection Output)

```python
@dataclass
class ServoScene:
    """Scene graph for Servo rendering."""
    id: SceneId
    nodes: list[ServoNode]
    edges: list[ServoEdge]
    layout: LayoutDirective
    style: StyleSheet
    animations: list[Animation]

@dataclass
class ServoNode:
    """Node in Servo scene graph."""
    id: NodeId
    kind: ServoNodeKind        # PANEL, TRACE, INTENT, OFFERING, COVENANT
    content: ServoContent
    position: Position | None  # If explicit
    style: NodeStyle
    interactions: list[Interaction]

class ServoNodeKind(Enum):
    """Semantic node types for Servo rendering."""
    PANEL = auto()             # Container with borders
    TRACE = auto()             # TraceNode visualization
    INTENT = auto()            # IntentTree node
    OFFERING = auto()          # Offering badge
    COVENANT = auto()          # Permission indicator
    WALK = auto()              # Walk timeline
    RITUAL = auto()            # Ritual state
```

### ServoShell (Host Process)

```python
@dataclass
class ServoShell:
    """Minimal host process for Servo composition."""
    views: dict[ViewId, TerrariumView]
    projection_registry: ProjectionRegistry
    router: IntentRouter
    covenant_overlay: CovenantOverlay

    def compose(self, scene: ServoScene) -> RenderedOutput:
        """Compose projection outputs into final render."""
        ...

    def route(self, intent: Intent) -> ViewId:
        """Navigate to view based on intent, not URL."""
        ...
```

### Servo Projection Target

```python
@ProjectionRegistry.register(
    "servo",
    fidelity=0.95,
    description="Servo browser engine substrate"
)
def servo_projector(widget: KgentsWidget) -> ServoScene:
    """Convert widget state to ServoScene graph."""
    return ServoScene(
        nodes=widget_to_servo_nodes(widget),
        layout=infer_layout(widget),
        style=get_servo_stylesheet(),
        ...
    )
```

### TerrariumView (Multi-Webview)

```python
@dataclass
class TerrariumView:
    """Independent webview with compositional lens."""
    id: ViewId
    webview: ServoWebview
    selection: TraceNodeQuery  # What TraceNodes to show
    lens: LensConfig           # How to transform
    fault_isolated: bool = True  # Crash doesn't collapse system

    def project(self, trace_stream: Stream[TraceNode]) -> ServoScene:
        """Apply lens to trace stream."""
        ...
```

---

## Laws/Invariants

### Servo Laws

```
Law 1 (Scene Composability): ServoScenes compose via overlay
Law 2 (Layout Determinism): Same input → same layout
Law 3 (Fault Isolation): Crashed view doesn't affect other views
Law 4 (Intent Routing): Navigation is a projection of intent, not URL
```

### Projection Laws

```
Law 1 (Fidelity Ordering): servo (0.95) > marimo (0.8) > tui (0.5) > cli (0.2)
Law 2 (Fallback Chain): servo → marimo → tui → cli → json
Law 3 (Completeness): Every AGENTESE node projects to servo
```

---

## Integration

### Servo Primitive Replacements

| Old Webapp Layer | Servo Primitive | Notes |
|------------------|-----------------|-------|
| Router + SPA pages | IntentTree navigation | Navigation is intent, not URL |
| React components | ServoNode graph | UI is a graph, not a DOM |
| CSS layouts | Servo layout primitives | Density-aware layouts in Rust |
| Frontend state | TraceNode / Walk streams | State is in the ledger |

### Elastic UI in Servo

From `elastic-ui-patterns.md`, implement in Servo primitives:

```python
class ServoLayoutMode(Enum):
    COMPACT = auto()      # Minimal, mobile-first
    COMFORTABLE = auto()  # Balanced, default
    SPACIOUS = auto()     # Rich, desktop

@dataclass
class ElasticServoLayout:
    """Servo-native elastic layout."""
    mode: ServoLayoutMode
    split: ElasticSplit
    sidebar: FloatingSidebar | None
    drawer: BottomDrawer | None

    @property
    def density_constants(self) -> DensityConstants:
        """Rust-enforced density constants."""
        return SERVO_DENSITY[self.mode]
```

### Crown Jewel Visual Contracts

Each jewel needs a servo-scene contract:

```python
@dataclass
class AtelierServoContract:
    """Atelier (Copper / Creative Forge) visual contract."""
    workshop_glow: Color = Color(copper=0.8)
    spectator_bids: list[LivingToken]
    creation_canvas: BreathingFrame
    breathing_surface: BreathingSurface  # 3-4s, 2-3% amplitude

@dataclass
class ParkServoContract:
    """Park (Sage / Immersive Inhabit) visual contract."""
    theater_mode: FirstPersonTheater
    consent_gauge: LivingGauge
    character_masks: list[OrbitingMask]
    flow_traces: list[VinePath]  # Data moves like water
```

---

## Crown Jewel UX Refinement (B → A Grade)

### Design Reference Inheritance

From `creative/crown-jewels-genesis-moodboard.md`:

| Reference | Servo Implementation |
|-----------|---------------------|
| Studio Ghibli | Warm, breathing machinery; organic motion |
| Matsu theme | Watercolor textures, hand-made softness |
| Organic Matter | Fluid shapes, living materials |
| Sleep No More | Participant-as-actor immersion |
| Ethical AI | Visible consent, human override |

### Required Servo Primitives

```python
@dataclass
class BreathingSurface:
    """Idle pulse on living panels."""
    period: timedelta = timedelta(seconds=3.5)  # 3-4s
    amplitude: float = 0.025  # 2-3%
    enabled: bool = True

@dataclass
class UnfurlingPanel:
    """Drawers open like leaves, not mechanical slides."""
    curve: EasingCurve = EasingCurve.ORGANIC_UNFURL
    duration: timedelta = timedelta(milliseconds=400)

@dataclass
class FlowTrace:
    """Data moves like water through vine paths."""
    path: VinePath
    flow_speed: float = 0.3
    particle_count: int = 12

@dataclass
class TextureLayer:
    """Subtle paper or grain (not flat glass)."""
    texture: Texture = Texture.WARM_PAPER
    opacity: float = 0.15

@dataclass
class TeachingOverlay:
    """Dense teacher callouts with opt-in visibility."""
    enabled: bool  # From useTeachingMode
    callouts: list[TeachingCallout]
    density: TeachingDensity = TeachingDensity.RICH
```

### Typography + Palette

```python
class ServoTypography:
    """Locked-in typography for Servo."""
    HEADING = "Nunito"         # Friendly, hand-made
    BODY = "Inter"             # Clean, readable
    CODE = "JetBrains Mono"    # Technical clarity

class LivingEarthPalette:
    """Warm earth palette for Servo."""
    SOIL = Color("#5D4037")
    LIVING_GREEN = Color("#7CB342")
    AMBER_GLOW = Color("#FFB300")
    SAGE = Color("#9CCC65")
    COPPER = Color("#D84315")
```

---

## Anti-Patterns

1. **Servo as "just a webview"**: It's the projection substrate, not a browser
2. **URL-based routing**: Navigation is intent, not URLs
3. **React component logic**: UI logic lives in Servo primitives
4. **Flat glass aesthetic**: Always use texture layer
5. **Mechanical animations**: Use organic unfurl, breathing surfaces
6. **Teaching overlays without toggle**: Always respect useTeachingMode

---

## Implementation Reference

See:
- `impl/claude/protocols/agentese/projection/servo.py` (ServoProjector)
- `impl/claude/protocols/agentese/projection/servo_primitives.py` (ServoNode, ServoScene)
- `impl/claude/web/servo-shell/` (ServoShell host)
- `impl/claude/web/src/components/servo/` (Servo-native components)

---

*"The webapp is not the UI. The webapp is the composition boundary."*
