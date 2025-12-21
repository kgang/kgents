# Projection Protocol (UI)

> *"Developers design agents. Projections are batteries included."*

**Status:** Canonical
**Implementation:** `impl/claude/agents/i/reactive/` (37+ tests)
**Related:** [`alethic-projection.md`](alethic-projection.md) (Agent Compilation)

---

## Two Projection Protocols

kgents distinguishes **two projection domains**:

| Protocol | Document | Functor | Purpose |
|----------|----------|---------|---------|
| **UI Projection** | This document | `State → Renderable[T]` | Display agent state |
| **Agent Compilation** | [`alethic-projection.md`](alethic-projection.md) | `(Nucleus, Halo) → Executable[T]` | Deploy agents |

This document covers **UI Projection**—how agent state renders to CLI, Web, marimo, etc.

---

## Purpose

The Projection Protocol defines how kgents content renders to any target medium. Developers write agents and their state machines. The projection layer handles rendering—whether output goes to ASCII terminal, JSON API, marimo notebook, WebGL, or VR headset. This is not mere convenience—it is a **categorical guarantee**: the same agent definition, projected through different functors, produces semantically equivalent views.

## Core Insight

*"State is design. Projection is mechanical. Targets are isomorphic within fidelity."*

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

This formalizes the insight: projection is fundamentally **lossy**. Different targets have different fidelity. A marimo heatmap captures more than an ASCII sparkline. The category theory ensures we lose information predictably.

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

### The Isomorphism

The key insight:

```
Screen Density ≅ Observer Umwelt ≅ Projection Target ≅ Content Detail Level
```

This is not metaphor—it is a categorical equivalence:

| AGENTESE Concept | Projection Concept |
|------------------|-------------------|
| Observer umwelt | Projection target + density |
| Affordance based on who grasps | Content based on available space |
| `manifest` yields observer-view | `project` yields density-view |

### Content Degradation Levels

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

## Layout Projection

> *"The sidebar and the drawer are the same panel. Only the observer's capacity to receive differs."*

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

Three canonical layout primitives compose to form all density-adaptive layouts:

| Primitive | Compact | Comfortable | Spacious |
|-----------|---------|-------------|----------|
| **Split** | Collapse secondary | Fixed-width panes | Resizable divider |
| **Panel** | Bottom drawer | Collapsible panel | Fixed sidebar |
| **Actions** | Floating FAB cluster | Inline button row | Full toolbar |

These primitives form the **basis** of the layout functor. All responsive layouts decompose into compositions of these primitives.

### The Three-Stage Layout Pattern

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

### Canonical Density Breakpoints

These breakpoints are the **single source of truth** for all implementations:

| Density | Range | Device Class |
|---------|-------|--------------|
| **compact** | < 768px | Mobile phones |
| **comfortable** | 768px – 1023px | Tablets |
| **spacious** | ≥ 1024px | Desktop/laptop |

```typescript
// CANONICAL VALUES - all implementations must align
BREAKPOINT_COMPACT_MAX = 767    // < 768 is compact
BREAKPOINT_COMFORTABLE_MAX = 1023  // 768-1023 is comfortable
// ≥ 1024 is spacious
```

**Implementations that must align**:
- Python: `agents/design/types.py` → `Density.from_width()`
- TypeScript: `useDesignPolynomial.ts` → `densityFromWidth()`
- CSS: `elastic/types.ts` → `DENSITY_BREAKPOINTS`

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

## AD-008 Applied: Isomorphism Detection

> *"When the same conditional appears three times, you've found a dimension hiding in plain sight."*

### The Core Insight

**AD-008** (Simplifying Isomorphisms): When you see the same concept expressed in multiple forms, recognize the isomorphism and factor it out.

Applied to UI: scattered boolean conditionals (`isMobile`, `isCompact`, `isAdmin`) are **dimensions in disguise**. The extraction algorithm:

1. **Name the dimension** — Give the hidden axis an explicit name
2. **Define values** — Exhaustive, mutually exclusive enum values
3. **Create context** — Provide the dimension at appropriate level
4. **Parameterize constants** — Replace scattered values with lookup tables
5. **Internal adaptation** — Components adapt internally, not externally

### Common Isomorphisms

| Hidden in... | Revealed as... | Context |
|--------------|----------------|---------|
| `isMobile`, `isTablet`, `isDesktop` | `density: 'compact' \| 'comfortable' \| 'spacious'` | `useWindowLayout()` |
| `isViewer`, `isEditor`, `isAdmin` | `role: Role` | `RoleContext` |
| `isLoading`, `hasError` | `loadState: LoadState` | Component state |
| Observer-specific rendering | `umwelt: Umwelt` | AGENTESE |

### The Categorical Perspective

Isomorphism detection is **functor discovery**:

```
Functor F: Condition → Behavior

Before: Many scattered F₁, F₂, F₃ (each conditional)
After:  One F (parameterized by dimension)
```

When you name the dimension, you're naming the functor's **domain**. When you create parameterized constants, you're defining the functor's **action**.

### Signs You've Found an Isomorphism

1. **Repeated Conditionals** — Same `if` condition in 3+ places
2. **Parallel Structures** — Same structure, different values per case
3. **Configuration Explosion** — Too many boolean/enum props
4. **Cross-Cutting Concerns** — Same logic at multiple component levels

### Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| Premature extraction | Single use doesn't warrant dimension | Wait for 3+ occurrences |
| Over-abstraction | Not every boolean is a dimension | Simple toggles stay boolean |
| Leaky abstractions | Components still check original condition | Components only know dimension |
| Scattered conditionals | Unmaintainable | Density-parameterized constants |

**Skill Reference**: `docs/skills/ui-isomorphism-detection.md` for audit workflow and templates.

---

## 3D Target Projection (WebGL/WebXR)

> *"Depth is not decoration—it is information."*

### The 3D Projection Functor

The complete 3D projection functor:

```
P[3D] : State × Theme × Quality → Three.js Scene

Full Composition:
  Scene = SceneLighting ∘ SceneEffects ∘ LOD[Budget](Nodes ∘ Edges) ∘ Touch

Where:
  - LOD[Budget] : (nodeCount, cameraDistance) → renderComplexity
  - Touch : isTouchDevice → touchTargetMultiplier
  - Theme : crystal | forest | (custom)
```

### The Illumination Quality Dimension

Just as density governs 2D layout projection, **illumination quality** governs 3D rendering fidelity:

```
Projection[3D] = (Density × IlluminationQuality) → 3D Scene

Where IlluminationQuality ∈ {minimal, standard, high, cinematic}
```

| Quality | Shadows | Shadow Map | Use Case |
|---------|---------|------------|----------|
| `minimal` | None | N/A | Low-end mobile, battery saving |
| `standard` | Soft | 1024px | Most devices |
| `high` | PCF soft | 2048px | Desktop, high-end mobile |
| `cinematic` | VSM/CSM | 4096px | Presentation, screenshots |

### The LOD Functor

LOD (Level of Detail) is a budget-aware functor for scaling rendering complexity:

```
LOD : (NodeCount × CameraDistance × Budget) → LODLevel

LODLevel = {
  full:    segments=32, labels=true,  animation=true,  particles=true
  reduced: segments=16, labels=true,  animation=true,  particles=false
  minimal: segments=8,  labels=false, animation=false, particles=false
  culled:  (not rendered - frustum culled)
}

Budget modulation:
  nodeCount < 50  → budget = 1.0 (normal distances)
  nodeCount < 100 → budget = 0.75 (25% closer thresholds)
  nodeCount ≥ 100 → budget = 0.5 (aggressive culling)
```

This ensures 60fps with 100+ nodes by dynamically reducing detail at distance.

### 3D Primitives

The unified primitive system provides theme-agnostic building blocks:

| Primitive | Purpose | Theme Input |
|-----------|---------|-------------|
| `TopologyNode3D` | Nodes (spheres with glow, labels, rings) | `ThemePalette` |
| `TopologyEdge3D` | Edges (curved lines with particles) | `ThemePalette` |
| `SelectionRing` | Selection indicator | Color |
| `HoverRing` | Hover indicator | Color |
| `FlowParticles` | Edge animation | Color |
| `NodeLabel3D` | Billboarded text | Color |
| `GrowthRings` | Forest theme rings | Color |

Domain wrappers (OrganicCrystal, OrganicNode, etc.) are thin—they only provide domain-specific tier and size calculations.

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

Layout projection is `manifest` specialized to physical capacity:

| AGENTESE | Layout Projection |
|----------|-------------------|
| Observer umwelt | Viewport density |
| Affordance for who grasps | Interaction modality for screen size |
| `manifest` yields observer-view | `Layout[D]` yields density-structure |

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

## The marimo Integration

marimo notebooks are a special case of the Projection Protocol. The reactive DAG model of marimo maps directly to the Signal/Computed/Effect model of kgents widgets.

**Key insight**: marimo LogosCell pattern IS AgenteseBridge pattern—direct mapping, no adapter layer needed.

```python
@app.cell
def agent_view(mo, agent_state):
    """Render agent state as marimo HTML."""
    widget = AgentWidget(agent_state)
    mo.Html(widget.to_marimo())
```

## Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| `{isMobile ? <CompactPanel /> : <FullPanel />}` | Scatters density logic | `<Panel density={density} />` |
| Custom rendering per agent | Breaks DRY | Extend existing widget base |
| Projection in business logic | Violates separation | State is pure, projection is separate layer |
| Fidelity assumptions | Breaks target-independence | Accept lossy compression |
| Scattered density conditionals | Unmaintainable | Density-parameterized constants table |

## Principles (Summary)

| Principle | Meaning |
|-----------|---------|
| **Design Over Plumbing** | Developers define state, not rendering |
| **Batteries Included** | All targets work out of the box |
| **Lossy by Design** | Fidelity varies by target; this is explicit |
| **Composable** | Widgets compose via `>>` and `//` |
| **Observable** | Same state → same output (determinism) |
| **Extensible** | New targets registered without changing agents |

## The Projection Gallery

The Projection Gallery demonstrates the protocol by rendering **every widget** to **every target** in a single view. Developers create **Pilots**—pre-configured widget demonstrations with variations—and the Gallery handles all projections. Full implementation at `impl/claude/protocols/projection/gallery/` with REST API at `/api/gallery` and React frontend at `web/src/pages/GalleryPage.tsx`.

## Future Targets

| Target | Status | Notes |
|--------|--------|-------|
| CLI | ✓ Shipped | ASCII art, box drawing |
| TUI | ✓ Shipped | Textual widgets |
| marimo | ✓ Shipped | anywidget + mo.Html |
| JSON | ✓ Shipped | API responses |
| SSE | ✓ Shipped | Streaming events |
| WebGL | ✓ Shipped | Three.js primitives (TopologyNode3D, TopologyEdge3D, LOD, themes) |
| WebXR | Future | VR/AR experiences |
| Audio | Future | Sonification of state |

## Implementation Reference

- Widget base: `impl/claude/agents/i/reactive/widget.py`
- Target registry: `impl/claude/agents/i/reactive/targets.py`
- Projectors: `impl/claude/system/projector/` (local, k8s)
- Gallery: `impl/claude/protocols/projection/gallery/`
- Widget primitives: `impl/claude/web/src/widgets/primitives/`
- Three.js utils: `impl/claude/web/src/utils/three/`
- Touch gestures: `impl/claude/web/src/hooks/useTouchGestures.ts`
- Quality detection: `impl/claude/web/src/hooks/useIlluminationQuality.ts`
- Skill guide: `docs/skills/3d-projection-patterns.md`

---

## Implementation Learnings (Town Visualizer Renaissance)

> *Battle-tested patterns from the Town Crown Jewel implementation.*

### Teaching Mode Pattern

Teaching Mode provides a toggle-able pedagogical layer that explains categorical concepts without cluttering the UI:

```typescript
// Hook with localStorage persistence
const { enabled, toggle } = useTeachingMode();

// Conditional wrapper
<WhenTeaching>
  <TeachingCallout title="Polynomial State">
    Citizens transition through phases via PolyAgent[S,A,B].
  </TeachingCallout>
</WhenTeaching>

// Toggle component with aria-label for accessibility
<TeachingToggle compact />
```

**Key Insight**: Teaching callouts should use `aria-label="Teaching Mode: ON"` pattern for testability and accessibility.

### AGENTESE E2E Testing

AGENTESE endpoints require special mocking—they're POST requests through a gateway, not REST resources:

```typescript
// WRONG: REST-style mock
await page.route('**/v1/town/*/citizens', ...);

// CORRECT: AGENTESE gateway mock
await page.route('**/agentese/world/town/citizen.list', async (route) => {
  await route.fulfill({
    body: JSON.stringify({
      path: 'world.town',
      aspect: 'citizen.list',
      result: { citizens: mockCitizens, total: mockCitizens.length },
    }),
  });
});
```

### Three-Bus Event Architecture

The event-driven architecture uses three layered buses with clear responsibilities:

```
DataBus (L1 persistence)
    ↓ wire_data_to_synergy()
SynergyBus (L2 cross-jewel routing with wildcards)
    ↓ wire_synergy_to_event()
EventBus (L3 UI fan-out)
```

**Cross-Jewel Handlers**: SynergyBus enables loose coupling between Crown Jewels:
- `town.citizen.*` → K-gent handlers (personality/dialogue)
- `town.gossip.*` → Atelier handlers (social graph visualization)
- `town.relationship.*` → M-gent handlers (memory crystallization)

### E2E Selector Stability

Stable selectors for Playwright tests, in order of preference:

1. **aria-label** - `button[aria-label="Teaching Mode: ON"]`
2. **data-testid** - `[data-testid="citizen-panel"]`
3. **Specific role + name** - `getByRole('heading', { name: /Coalition Graph/i })`
4. **Structural** - `h2:has-text("Coalitions")` with context
5. **Text content (last resort)** - `getByText(/Alice/)`

**Anti-Pattern**: Never use bare `getByText()` for words that appear multiple times on the page.

### Density-Aware Stat Cards

The stat card pattern with navigation and content degradation:

```typescript
<div
  onClick={() => navigate(route)}
  className={`cursor-pointer hover:bg-gray-800/50 ${densityPadding}`}
>
  <p className="text-sm text-gray-400">{label}</p>
  <p className="text-2xl font-bold">{value}</p>
  <span className="text-xs text-violet-400">View details →</span>
</div>
```

**Density Values**:
- `compact`: p-3, text-xl
- `comfortable`: p-4, text-2xl
- `spacious`: p-5, text-3xl

---

*"The projection is not the territory. But a good projection makes the territory navigable."*
