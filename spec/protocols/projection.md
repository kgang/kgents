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

## Density Projection

The Projection Protocol extends beyond target (CLI/Web/marimo) to include **DENSITY** as an orthogonal dimension.

### The Density-Target Matrix

| Target | Density | Projection |
|--------|---------|------------|
| CLI | compact | Single-line summaries, sparklines |
| CLI | spacious | Full tables, verbose output |
| Web | compact | Drawer panels, floating actions, touch targets |
| Web | comfortable | Collapsible panels, hybrid layout |
| Web | spacious | Full sidebars, draggable dividers, legends |
| marimo | compact | Collapsed cells, summary widgets |
| marimo | spacious | Expanded cells, full visualizations |

### Density as Observer Capacity

Density is not merely screen size—it is the **capacity to receive**. This is the Projection Protocol's realization of AGENTESE observer-dependent perception:

```python
# Same widget, same target, different densities
widget.project(RenderTarget.WEB, density='compact')    # → Minimal chrome, drawers
widget.project(RenderTarget.WEB, density='spacious')   # → Full panels, legends
```

The widget's `layout` field provides hints, but the projection target makes the final density decision based on available space:

```typescript
interface WidgetLayoutHints {
  flex?: number;           // Flex grow factor
  minWidth?: number;       // Collapse threshold
  maxWidth?: number;       // Comfortable maximum
  priority?: number;       // Truncation order
  collapsible?: boolean;   // Can be hidden to save space
  collapseAt?: number;     // Viewport width threshold
}
```

### The Isomorphism

The key insight from the Gestalt Elastic refactor:

```
Screen Density ≅ Observer Umwelt ≅ Projection Target ≅ Content Detail Level
```

This is not metaphor—it is a categorical equivalence:

| AGENTESE Concept | Projection Concept |
|------------------|-------------------|
| Observer umwelt | Projection target + density |
| Affordance based on who grasps | Content based on available space |
| `manifest` yields observer-view | `project` yields density-view |

### Practical Application

The density dimension allows widgets to define **content degradation** gracefully:

```typescript
type ContentLevel = 'icon' | 'title' | 'summary' | 'full';

function getContentLevel(width: number): ContentLevel {
  if (width < 60) return 'icon';
  if (width < 150) return 'title';
  if (width < 280) return 'summary';
  return 'full';
}
```

Each level is a **lossy projection**—information removed predictably, matching the Galois connection principle.

---

## Layout Projection

> *"The sidebar and the drawer are the same panel. Only the observer's capacity to receive differs."*

Content projection is **lossy compression**—fewer labels, smaller numbers, truncated text. Layout projection is **structural isomorphism**—the same information, arranged differently for different interaction modalities.

### The Two Functors

The Projection Protocol operates through two distinct functors:

```
Content[D] : State → ContentDetail[D]      (lossy compression)
Layout[D]  : WidgetTree → Structure[D]     (structural isomorphism)

Where D ∈ {compact, comfortable, spacious}
```

| Functor | Domain | Operation | Example |
|---------|--------|-----------|---------|
| Content[D] | State → Detail | Removes information | 12 labels → 5 labels |
| Layout[D] | WidgetTree → Structure | Rearranges information | Sidebar → Drawer |

**Key Insight**: Content projection affects **fidelity** (how much to show). Layout projection affects **affordance** (how to interact).

### The Structural Isomorphism

Layout projection preserves information while transforming structure:

```
Layout[compact](Panel) ≅ Layout[spacious](Panel)

Desktop:  ┌─────────────┬────────────┐
          │   Canvas    │   Panel    │
          │             │ (sidebar)  │
          └─────────────┴────────────┘

Mobile:   ┌─────────────────────────┐
          │        Canvas           │
          │                    [⚙️]  │  ← Floating action
          └─────────────────────────┘
          ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐
          │    Panel (drawer)        │  ← Slides up on tap
          └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
```

The **same logical content** projects to **different interaction modalities**. The isomorphism is semantic: what the user can accomplish remains constant; how they accomplish it varies.

### Layout Primitives

The protocol defines three canonical layout primitives that compose to form all density-adaptive layouts:

| Primitive | Compact | Comfortable | Spacious |
|-----------|---------|-------------|----------|
| **Split** | Collapse secondary | Fixed-width panes | Resizable divider |
| **Panel** | Bottom drawer | Collapsible panel | Fixed sidebar |
| **Actions** | Floating FAB cluster | Inline button row | Full toolbar |

These primitives form the **basis** of the layout functor. All responsive layouts decompose into compositions of these primitives.

### The Three-Stage Layout Pattern

Layouts project through three canonical stages:

```
┌─────────────────────────────────────────────────────────────────────┐
│  SPACIOUS (Desktop >1024px)                                         │
│                                                                     │
│  ┌─────────────────────────────┬─────────────────┬────────────────┐ │
│  │      Primary Canvas         │  Control Panel  │ Detail Panel   │ │
│  │                           ↔ │                 │   (optional)   │ │
│  │     (resizable divider) →   │                 │                │ │
│  └─────────────────────────────┴─────────────────┴────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  COMFORTABLE (Tablet 768-1024px)                                    │
│                                                                     │
│  ┌─────────────────────────────┬─────────────────────────────────┐  │
│  │      Primary Canvas         │  Control/Detail Toggle          │  │
│  │                             │    (fixed width, no resize)     │  │
│  └─────────────────────────────┴─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  COMPACT (Mobile <768px)                                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      Full Canvas                          [⚙️] │  │
│  │                                                           [📋] │  │
│  │                                           Floating Actions → │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
│  │         Bottom Drawer (slides up on action tap)              │  │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Physical Constraints

Layout projection respects constraints from the physical world that do not scale:

| Constraint | Minimum | Applies To |
|------------|---------|------------|
| Touch target | 48px × 48px | Mobile interactive elements |
| Readable font | 14px | Compact text |
| Tap spacing | 8px | Adjacent touch targets |
| Drawer handle | 40px × 4px | Mobile drawer affordance |

These are **invariants**—they do not change with density. The layout functor ensures these constraints are satisfied regardless of projection target.

```
TouchTarget[D] ≥ 48px    ∀ D ∈ {compact, comfortable, spacious}
```

### Density-Parameterized Constants

Content-level density uses lookup tables rather than scattered conditionals:

```
Value[D] : Density → Number

NODE_SIZE     = { compact: 0.2,  comfortable: 0.25, spacious: 0.3  }
FONT_SIZE     = { compact: 14,   comfortable: 16,   spacious: 18   }
MAX_LABELS    = { compact: 15,   comfortable: 30,   spacious: 50   }
PANEL_WIDTH   = { compact: null, comfortable: 240,  spacious: 320  }
```

This is the **canonical pattern** for density-dependent values. The scattered conditional anti-pattern (`isMobile ? X : Y`) is replaced by explicit lookup.

### Composition Laws

Layout projection preserves widget composition under certain conditions:

**Vertical Composition (`//`)**:
```
Layout[D](A // B) = Layout[D](A) // Layout[D](B)

The vertical stack of two widgets projects to a vertical stack of their projections.
```

**Horizontal Composition (`>>`)**:
```
Layout[compact](A >> B) ≠ Layout[compact](A) >> Layout[compact](B)

In compact mode, horizontal composition may transform to vertical stacking
or tab/drawer navigation. This is NOT a failure—it's the structural isomorphism.
```

**The Transformation Rule**:
```
Layout[compact](SidePanel >> MainContent)
    → Layout[compact](MainContent) + FloatingAction(SidePanel)

The >> composition transforms to overlay composition in compact mode.
```

### Connection to AGENTESE

Layout projection is `manifest` specialized to physical capacity:

| AGENTESE | Layout Projection |
|----------|-------------------|
| Observer umwelt | Viewport density |
| Affordance for who grasps | Interaction modality for screen size |
| `manifest` yields observer-view | `Layout[D]` yields density-structure |

```python
# AGENTESE observer-dependent projection
await logos.invoke("world.panel.manifest", mobile_umwelt)
# → Drawer with floating action trigger

await logos.invoke("world.panel.manifest", desktop_umwelt)
# → Fixed sidebar with resizable divider
```

The observer's **capacity to receive** includes not just cognitive bandwidth (content projection) but also **physical modality** (layout projection). A mobile user cannot drag a resize handle—they tap floating actions instead.

### Component Density Propagation

Components receive density as a parameter and decide internally how to adapt:

```
Anti-pattern: {isMobile ? <CompactPanel /> : <FullPanel />}
Pattern:      <Panel density={density} />

// Inside Panel:
function Panel({ density }) {
  const isDrawer = density === 'compact';
  // Component owns its density interpretation
}
```

This encapsulation ensures:
1. Parent components remain density-agnostic
2. Components can be reused at any density
3. Testing targets density values, not scattered conditions

### Layout Hints

Widgets provide layout hints that inform projection decisions:

```typescript
interface LayoutHints {
  collapseAt?: number;        // Viewport width to collapse
  collapseTo?: 'drawer' | 'tab' | 'hidden';
  priority?: number;          // Truncation order (lower = keep longer)
  requiresFullWidth?: boolean; // Cannot share horizontal space
  minTouchTarget?: number;     // Physical minimum (default 48)
}
```

These hints guide the layout functor but do not determine it—the projection target makes the final decision based on available space.

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

## 3D Target Projection (WebGL/WebXR)

> *"Depth is not decoration—it is information."*

The Projection Protocol extends to 3D targets with an additional orthogonal dimension: **illumination quality**.

### The Illumination Quality Dimension

Just as density governs 2D layout projection, **illumination quality** governs 3D rendering fidelity:

```
Projection[3D] = (Density × IlluminationQuality) → 3D Scene

Where IlluminationQuality ∈ {minimal, standard, high, cinematic}
```

This is a **simplifying isomorphism** (AD-008): device capability checks are unified into a single named dimension.

| Quality | Shadows | Shadow Map | Use Case |
|---------|---------|------------|----------|
| `minimal` | None | N/A | Low-end mobile, battery saving |
| `standard` | Soft | 1024px | Most devices |
| `high` | PCF soft | 2048px | Desktop, high-end mobile |
| `cinematic` | VSM/CSM | 4096px | Presentation, screenshots |

### Canonical Principles for 3D Targets

1. **Consistent Lighting**: All 3D scenes use the same canonical lighting rig
2. **Shadows as Depth Cues**: Shadows are not decorative—they provide spatial information
3. **Quality Detection**: Illumination quality is detected from device capability, not configured
4. **Selective Shadow Casting**: Only objects that benefit from shadows cast them

### The Sun Pattern

The primary light is a **DirectionalLight** positioned upper-right-front to match the human "light from above" prior:

```
Sun position: [15, 20, 15] (relative to scene center)
```

This creates shadows that fall to the lower-left, matching cognitive expectations.

### Semiotic Depth Cues

3D projections leverage depth cues in order of perceptual strength:

| Cue | Provided By | Priority |
|-----|-------------|----------|
| Occlusion | WebGL z-buffer | Automatic |
| Shadows | DirectionalLight | Explicit (quality-dependent) |
| Size gradient | Perspective camera | Automatic |
| Motion parallax | OrbitControls | Interactive |
| Shading | PBR materials | Automatic |

**Key insight**: Shadows are the second-most-powerful depth cue after occlusion, yet often omitted due to performance concerns. Quality-dependent shadows solve this tradeoff.

### Connection to AGENTESE

3D projection is observer-dependent in two dimensions:

| AGENTESE Concept | 2D Manifestation | 3D Manifestation |
|------------------|------------------|------------------|
| Observer capacity | Viewport density | Device capability |
| `manifest` result | Content + Layout | Content + Layout + Illumination |
| Lossy compression | Fewer labels | Lower shadow fidelity |

### Implementation Guidance

See `docs/skills/3d-lighting-patterns.md` for implementation patterns and `plans/3d-visual-clarity.md` for the implementation plan.

---

## The Projection Gallery

The Projection Gallery is the canonical demonstration of the protocol. It renders **every widget** to **every target** in a single view, proving the protocol's guarantees hold in practice.

### Architecture

```
Pilot[State] ────► Gallery.render() ────► { CLI, HTML, JSON }
     │                    │                        │
     │                    │                        │
     └── Widget factory ──┴── Override injection ──┘
```

### Gallery Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `Pilot` | `protocols/projection/gallery/pilots.py` | Pre-configured widget demo |
| `Gallery` | `protocols/projection/gallery/runner.py` | Render orchestrator |
| `GalleryOverrides` | `protocols/projection/gallery/overrides.py` | Developer control injection |
| `GalleryAPI` | `protocols/api/gallery.py` | REST endpoint |
| `GalleryPage` | `web/src/pages/GalleryPage.tsx` | React frontend |

### The Pilot Pattern

A **Pilot** is a pre-configured widget demonstration:

```python
@dataclass
class Pilot:
    name: str                     # "glyph_idle", "agent_card_error"
    category: PilotCategory       # PRIMITIVES, CARDS, CHROME, etc.
    description: str              # One-line explanation
    widget_factory: Callable      # Creates widget with overrides
    tags: list[str]               # Searchable metadata
```

Pilots separate **what to show** from **how to show it**:

```python
# Define the demo
register_pilot(Pilot(
    name="glyph_entropy_sweep",
    category=PilotCategory.PRIMITIVES,
    description="Glyph with customizable entropy",
    widget_factory=lambda overrides: GlyphWidget(
        GlyphState(
            entropy=overrides.get("entropy", 0.5),
            phase="active",
        )
    ),
    variations=[{"entropy": e} for e in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]],
    tags=["glyph", "entropy", "sweep"],
))

# Gallery handles all projections
gallery = Gallery()
gallery.show("glyph_entropy_sweep", target=RenderTarget.CLI)
gallery.show("glyph_entropy_sweep", target=RenderTarget.MARIMO)
gallery.show("glyph_entropy_sweep", target=RenderTarget.JSON)
```

### Override Injection

The Gallery supports surgical state manipulation for rapid iteration:

```python
# Environment variables
export KGENTS_GALLERY_ENTROPY=0.5
export KGENTS_GALLERY_SEED=42

# CLI flags
python -m protocols.projection.gallery --entropy=0.8 --seed=123

# Programmatic
gallery = Gallery(GalleryOverrides(entropy=0.3, seed=999))

# Per-widget override
gallery.show("agent_card", overrides={"phase": "error", "breathing": False})
```

### Web Gallery API

The REST API serves projections for the web frontend:

```
GET /api/gallery                    # All pilots, all projections
GET /api/gallery?category=CARDS     # Filter by category
GET /api/gallery?entropy=0.5        # With overrides
GET /api/gallery/{pilot_name}       # Single pilot
GET /api/gallery/categories         # Category metadata
```

Response shape:
```json
{
  "pilots": [
    {
      "name": "glyph_idle",
      "category": "PRIMITIVES",
      "description": "Glyph in idle phase",
      "tags": ["glyph", "idle"],
      "projections": {
        "cli": "○",
        "html": "<span class=\"kgents-glyph\">○</span>",
        "json": {"type": "glyph", "char": "○", "phase": "idle"}
      }
    }
  ],
  "categories": ["PRIMITIVES", "CARDS", "CHROME", ...],
  "total": 25
}
```

### The Gallery as Protocol Proof

The Gallery proves the Projection Protocol's claims:

| Claim | Gallery Evidence |
|-------|------------------|
| **Design once** | 25 pilots, each renders to 3+ targets |
| **Batteries included** | No per-target code in pilots |
| **Lossy by design** | CLI shows less than marimo |
| **Deterministic** | Same seed → same output |
| **Composable** | HStack/VStack pilots compose primitives |

### Running the Gallery

```bash
# CLI gallery
cd impl/claude
python -m protocols.projection.gallery --all
python -m protocols.projection.gallery --widget=agent_card --entropy=0.5

# Web gallery
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

cd impl/claude/web
npm run dev
# Visit http://localhost:3000/gallery
```

---

*"The projection is not the territory. But a good projection makes the territory navigable."*
