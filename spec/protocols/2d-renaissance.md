# 2D Renaissance: Generative Visualization End-to-End

**Status:** Specification
**Date:** 2025-12-18
**Revision:** 2.0 (Expanded with Gardener UX + Living Earth Aesthetic)
**Principles:** *"Daring, bold, creative, opinionated but not gaudy"* — Tasteful > feature-complete

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> 3D was spectacle. 2D is truth.
> The garden tends itself, but only because we planted it together.

---

## Part I: Purpose & Core Insight

### 1.1 Why This Exists

The Three.js visualizers were impressive demos but hollow experiences:

| Component | Problem |
|-----------|---------|
| GestaltVisualization | 1060 lines of 3D complexity for a health dashboard |
| BrainCanvas | 1004 lines, WebGL dependency, no LLM integration |
| TownCanvas3D | 383 lines of pretty spheres with hardcoded positions |

These are **museums**—static exhibits that look nice but don't breathe. They don't invoke AGENTESE. They don't call LLMs. They don't generate end-to-end user journeys.

### 1.2 The Core Insight

> **The 2D primitives in gallery/{projection, layout} are generative. Use them.**

Mesa (PixiJS) + ElasticSplit + BottomDrawer + density-parameterized constants = everything needed for responsive, composable, generative visualizations.

The Three.js components will be mothballed (preserved for future use). The skills stay. The primitives in `components/three/` remain available. But Crown Jewel pages switch to 2D-first rendering with **real data flows** and **LLM-backed interactions**.

### 1.3 The Living Earth Aesthetic

> *"The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."*

Drawing from the Crown Jewels Genesis moodboard, all 2D redesigns adopt:

| Principle | Application |
|-----------|-------------|
| **Alive Workshop** | Elements breathe, unfurl, grow—not slide mechanically |
| **Living Earth Palette** | Warm earth tones (#4A3728 Bark, #6B4E3D Wood, #4A6B4A Sage) |
| **Dense Teacher** | Teaching callouts visible when enabled, full categorical transparency |
| **Organic Animation** | Breathing (3-4s pulse), Growing (seed→bloom), Unfurling (panels unfold like leaves) |

**Animation Constants**:
```typescript
const BREATHE = { period: '3.5s', amplitude: 0.02 };
const GROW = { duration: '400ms', easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)' };
const UNFURL = { duration: '400ms', easing: 'cubic-bezier(0.4, 0, 0.2, 1)' };
```

---

## Part II: The Mothballing Protocol

### 2.1 What Gets Mothballed

```
impl/claude/web/src/components/
├── gestalt/
│   ├── GestaltVisualization.tsx    → mothball
│   ├── OrganicNode.tsx             → mothball
│   ├── VineEdge.tsx                → mothball
│   └── AnimatedEdge.tsx            → mothball
│   # KEEP: FilterPanel, Legend, NodeTooltip, ModuleSearch, ViewPresets, HealthFilter
├── brain/
│   ├── BrainCanvas.tsx             → mothball (extract 2D PanelsView)
│   ├── OrganicCrystal.tsx          → mothball
│   └── CrystalVine.tsx             → mothball
│   # KEEP: CrystalDetail
├── town/
│   ├── TownCanvas3D.tsx            → mothball
│   # KEEP: Mesa, TownVisualization, CitizenPanel, TownTracePanel, all others
├── three/                          → KEEP ENTIRE DIRECTORY (skills + primitives)
```

### 2.2 Mothball Destination

```
impl/claude/web/src/components/_mothballed/
├── three-visualizers/
│   ├── gestalt/
│   │   ├── GestaltVisualization.tsx
│   │   ├── OrganicNode.tsx
│   │   └── ...
│   ├── brain/
│   │   ├── BrainCanvas.tsx
│   │   └── ...
│   └── town/
│       └── TownCanvas3D.tsx
└── README.md  # "Mothballed 2025-12-18. May revive for VR/AR projections."
```

### 2.3 What Stays

| Directory | Status | Why |
|-----------|--------|-----|
| `components/three/` | **KEEP** | Reusable primitives for any future 3D work |
| `components/three/primitives/` | **KEEP** | TopologyNode3D, TopologyEdge3D, etc. |
| `docs/skills/` | **KEEP ALL** | 3D skills remain useful |
| `utils/three/` | **KEEP** | Shadow bounds, layout math |

---

## Part III: The Gardener Renaissance

> *"The garden tends itself, but only because we planted it together."*

### 3.1 Current State Analysis

The existing Gardener has **two separate visualizations** that need unification:

| Component | Lines | Purpose | Problems |
|-----------|-------|---------|----------|
| `GardenVisualization.tsx` | 419 | Plot grid, seasons, gestures | Uses emojis, dark industrial feel, no breathing |
| `GardenerVisualization.tsx` | 331 | Polynomial state machine | Separate from garden metaphor, no earth tones |

Both are functional but lack:
- **Living Earth aesthetic** (Ghibli warmth, organic animation)
- **Unified experience** (garden metaphor + session state machine)
- **Dense Teacher mode** (categorical transparency on demand)
- **Mobile-first layout** (BottomDrawer, FloatingActions patterns)

### 3.2 The Unified Gardener Vision

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  [THE GARDENER]  Wave 1 Hero Path Implementation          SPROUTING         │
│  Session 4h 23m | Entropy: 2.3/5.0 remaining              ● ● ● ○ ○         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────┬─────────────┐  │
│  │                    THE GARDEN                           │  SESSION    │  │
│  │                                                         │  ═══════════ │  │
│  │   ╭────────────────────────────────────────────╮       │             │  │
│  │   │              SEASON: SPROUTING              │       │  Phase:     │  │
│  │   │                                             │       │  ┌─────────┐│  │
│  │   │    🌱 Plasticity: ████████░░ 78%            │       │  │  SENSE  ││  │
│  │   │    ⚡ Entropy:    1.5x cost                 │       │  │    ●    ││  │
│  │   │                                             │       │  └─────────┘│  │
│  │   ╰────────────────────────────────────────────╯       │      │      │  │
│  │                                                         │      ▼      │  │
│  │   PLOTS (3/5 active)                                   │  ┌─────────┐│  │
│  │   ┌─────────────────┐  ┌─────────────────┐             │  │   ACT   ││  │
│  │   │ Hero Path       │  │ Foundation      │             │  │    ○    ││  │
│  │   │ ████████░░ 65%  │  │ ██████████ 100% │             │  └─────────┘│  │
│  │   │ ACTIVE          │  │ COMPLETE        │             │      │      │  │
│  │   └─────────────────┘  └─────────────────┘             │      ▼      │  │
│  │   ┌─────────────────┐  ┌─────────────────┐             │  ┌─────────┐│  │
│  │   │ Atelier Rebuild │  │ Town Frontend   │             │  │ REFLECT ││  │
│  │   │ ██████░░░░ 45%  │  │ █████░░░░░ 40%  │             │  │    ○    ││  │
│  │   │ WAITING         │  │ DORMANT         │             │  └─────────┘│  │
│  │   └─────────────────┘  └─────────────────┘             │             │  │
│  │                                                         │  Advance ▶  │  │
│  │                                                         │             │  │
│  └─────────────────────────────────────────────────────────┴─────────────┘  │
│                                                                              │
├─────────────────────────────[GESTURE STREAM]─────────────────────────────────┤
│  [48] OBSERVE concept.gardener — "checking forest state"                    │
│  [47] WATER hero-path — "hydrating with tests"                              │
│  [46] GRAFT atelier → hero-path — "connecting BidQueue"                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 The Gardener2D Component Architecture

```
impl/claude/web/src/components/gardener/
├── Gardener2D.tsx              # Main unified visualization
├── GardenCanvas.tsx            # 2D plot visualization (PixiJS or pure SVG)
├── SeasonOrb.tsx               # Breathing season indicator with plasticity
├── PlotTile.tsx                # Organic plot card with progress vine
├── GestureStream.tsx           # Live gesture feed with tone indicators
├── SessionPolynomial.tsx       # Integrated SENSE→ACT→REFLECT diagram
├── TendingPalette.tsx          # Quick action buttons (water, prune, graft...)
├── TransitionSuggester.tsx     # Auto-Inducer banner with dismiss memory
└── index.ts
```

### 3.4 Gardener2D Design Details

#### A. The Season Orb (Replaces SeasonIndicator)

A **breathing orb** that pulses with the garden's rhythm:

```
╭────────────────────────────────────────────────────────────╮
│                                                            │
│                    ╭───────────────────╮                   │
│                    │                   │                   │
│                    │        ◉          │  ← Breathing      │
│                    │    SPROUTING      │     pulse         │
│                    │                   │     (3.5s cycle)  │
│                    ╰───────────────────╯                   │
│                                                            │
│    Plasticity: ████████░░ 78%     Entropy: 1.5x           │
│                                                            │
│    In season: 2h 15m              Next: BLOOMING?          │
│                                                            │
╰────────────────────────────────────────────────────────────╯
```

**Colors by Season** (Living Earth palette):

| Season | Orb Color | Accent | Metaphor |
|--------|-----------|--------|----------|
| DORMANT | `#6B4E3D` Wood | `#4A3728` Bark | Resting roots |
| SPROUTING | `#4A6B4A` Sage | `#8BAB8B` Sprout | New growth |
| BLOOMING | `#D4A574` Amber | `#C08552` Copper | Full flower |
| HARVEST | `#E8C4A0` Honey | `#8B5A2B` Bronze | Gathering |
| COMPOSTING | `#2E4A2E` Fern | `#1A2E1A` Moss | Returning |

#### B. Plot Tiles (Replaces PlotCard)

Organic tiles with **vine-like progress indicators**:

```
┌─────────────────────────────────────────┐
│                                         │
│   ╭ Hero Path ──────────────────╮      │
│   │                             │      │
│   │  ═══════════════════●═══    │      │  ← Progress vine
│   │                    65%      │      │    grows organically
│   │                             │      │
│   │  ACTIVE · brain, town       │      │  ← Crown jewel tags
│   │                             │      │
│   ╰─────────────────────────────╯      │
│                                         │
└─────────────────────────────────────────┘
```

**Plot States** (visual differentiation):

| State | Visual Treatment |
|-------|------------------|
| ACTIVE | Full saturation, slight glow, breathing |
| WAITING | Muted, gentle pulse, dashed border |
| DORMANT | Grayed out, no animation |
| COMPLETE | Golden accent, harvest icon |

#### C. Integrated Session Polynomial

The SENSE→ACT→REFLECT cycle lives **inside** the garden, not separate:

```
╭───────────────────────────────────────────────────────────╮
│                    SESSION CYCLE                          │
│                                                           │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐      │
│    │  SENSE   │ ───▶ │   ACT    │ ───▶ │ REFLECT  │      │
│    │    ◉     │      │    ○     │      │    ○     │      │
│    └──────────┘      └──────────┘      └──────────┘      │
│         │                                    │            │
│         ╰────────────────◀───────────────────╯            │
│                        cycle                              │
│                                                           │
│    Current: SENSE (gathering context)                     │
│    Valid: [ACT]                                           │
│                                                           │
│    [ Advance to ACT ]                                     │
│                                                           │
╰───────────────────────────────────────────────────────────╯
```

#### D. Gesture Stream (Replaces GestureHistory)

A **living stream** of recent tending operations:

```
┌─────────────────────────────────────────────────────────────┐
│  GESTURE STREAM                                   (live ●)  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OBSERVE  concept.gardener                      2m   │   │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   │
│  │ "checking forest state before starting work"        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ WATER    hero-path                             15m  │   │
│  │ ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   │
│  │ tone: nurturing (0.7)                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GRAFT    atelier → hero-path                   1h   │   │
│  │ ████████████████████████████░░░░░░░░░░░░░░░░░░░░ │   │
│  │ "connecting BidQueue component to shared state"     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Tone visualization**: Gestures have tone (0-1). Higher tone = warmer color gradient.

#### E. Tending Palette (Mobile-Friendly Actions)

**Desktop**: Contextual buttons on plot hover/selection
**Mobile**: FloatingActions at bottom

```
╭─────────────────────────────────────────────────────────────╮
│                    TENDING PALETTE                          │
│                                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│   │  Observe │  │  Water  │  │  Graft  │  │  Prune  │       │
│   │    👁️    │  │    💧   │  │    🌿   │  │    ✂️   │       │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│   ┌─────────┐  ┌─────────┐                                 │
│   │  Rotate │  │   Wait  │                                 │
│   │    🔄   │  │    ⏳   │                                 │
│   └─────────┘  └─────────┘                                 │
│                                                             │
│   Target: hero-path                                         │
╰─────────────────────────────────────────────────────────────╯
```

**Note**: Per visual-system.md, emojis are used sparingly for high-recognition actions. Consider Lucide icon alternatives if emoji rendering is inconsistent.

### 3.5 Gardener2D Mobile Layout

```
╔═══════════════════════════════════════╗
│      GARDENER          SPROUTING      │
│      ━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
╠═══════════════════════════════════════╣
│                                       │
│  ╭─────────────────────────────────╮ │
│  │                                 │ │
│  │         ◉ SPROUTING             │ │
│  │         78% plasticity          │ │
│  │                                 │ │
│  ╰─────────────────────────────────╯ │
│                                       │
│  SESSION: SENSE ● ──▶ ACT ○ ──▶ ...  │
│                                       │
│  PLOTS                                │
│  ┌─────────────────────────────────┐ │
│  │ Hero Path        ████████ 65%   │ │
│  │ Foundation       ██████████100% │ │
│  │ Atelier          ██████░░░ 45%  │ │
│  └─────────────────────────────────┘ │
│                                       │
╠═══════════════════════════════════════╣
│  [48] OBSERVE concept.gardener 2m    │
│  [47] WATER hero-path 15m            │
╠═══════════════════════════════════════╣
│ [👁️] [💧] [🌿] [✂️] [📖]             │ ← FloatingActions
╚═══════════════════════════════════════╝
        ▲
        │  Swipe up for detail drawer
```

**BottomDrawer** contains:
- Full gesture stream
- Plot detail view
- Tending action forms
- Teaching mode toggle

### 3.6 Gardener2D Teaching Mode

When Teaching Mode is ON, categorical structures become visible:

```
╔════════════════════════════════════════════════════════════════════════════╗
║  Teaching Mode: [●] ON                                                     ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  GARDEN POLYNOMIAL                                                         ║
║  ╭────────────────────────────────────────────────────────────────────╮   ║
║  │                                                                    │   ║
║  │  P[Season] ≅ Σ(s:Season) Y^(Gesture_s)                            │   ║
║  │                                                                    │   ║
║  │  At SPROUTING, valid gestures:                                    │   ║
║  │  {OBSERVE, WATER, GRAFT, PRUNE}                                   │   ║
║  │                                                                    │   ║
║  │  Cost multiplied by season_entropy_multiplier: 1.5x               │   ║
║  │                                                                    │   ║
║  ╰────────────────────────────────────────────────────────────────────╯   ║
║                                                                            ║
║  💡 TEACHING CALLOUT                                                       ║
║  ════════════════════════════════════════════════════════════════════     ║
║  GardenState owns GardenerSession. The session is the "current            ║
║  conversation"—ephemeral within the garden's longer lifecycle.            ║
║                                                                            ║
║  Season plasticity modulates how aggressively TextGRAD can reshape        ║
║  ideas. High plasticity (SPROUTING) = bold changes welcome.               ║
║  Low plasticity (DORMANT) = preserve what exists.                         ║
║                                                                            ║
║  Entropy is the "accursed share"—intentional scarcity that forces         ║
║  intentionality. When exhausted, the garden transitions to COMPOSTING.    ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## Part IV: The 2D Redesigns (Other Jewels)

### 4.1 Gestalt → Gestalt2D

**Philosophy**: A codebase health dashboard should feel like a living garden, not a 3D planetarium.

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Gestalt]  A | 147 modules | 312 deps | 3 violations              ⚙ │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │
│  │ LAYER: protocols            │  │ LAYER: services             │   │
│  │                             │  │                             │   │
│  │   [agentese] A+  [cli] A    │  │   [brain] A  [town] B+      │   │
│  │   [api] A       [proj] A    │  │   [atelier] A-  [park] B    │   │
│  │                             │  │                             │   │
│  └─────────────────────────────┘  └─────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │
│  │ LAYER: agents               │  │ LAYER: models               │   │
│  │                             │  │                             │   │
│  │   [poly] A+   [operad] A+   │  │   [core] A   [town] A-      │   │
│  │   [town] A    [flux] A      │  │                             │   │
│  │                             │  │                             │   │
│  └─────────────────────────────┘  └─────────────────────────────┘   │
│                                                                      │
├───────────────────────────────────[VIOLATIONS]───────────────────────┤
│  ⚠ services.park → agents.flux (layer violation)                    │
│  ⚠ protocols.cli → models.core (should go through service)          │
│  ⚠ services.town → services.brain (circular import risk)            │
└──────────────────────────────────────────────────────────────────────┘
```

**Components**:
- `Gestalt2D.tsx`: ElasticSplit layout with layer panels
- `LayerCard.tsx`: Health-colored cards with module list
- `ViolationFeed.tsx`: Streaming violation alerts
- `ModuleDetail.tsx`: Existing, reused from FilterPanel

**Data Flow**: `logos.invoke("self.gestalt.manifest")` → 2D projection

### 4.2 Brain → Brain2D

**Philosophy**: Memory isn't a starfield. It's a living library where crystals form, connect, and surface when needed.

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Brain]  healthy | 42 crystals | dimension: 768                   ⚙ │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────┐ ┌─────────────────┐ │
│  │              CRYSTAL CARTOGRAPHY            │ │   QUICK CAPTURE │ │
│  │                                             │ │                 │ │
│  │    ◆ categorical-theory                    │ │  [___________]  │ │
│  │       ├── ◇ operads                        │ │  [  Capture  ]  │ │
│  │       │     ├── ◇ composition              │ │                 │ │
│  │       │     └── ◇ laws                     │ ├─────────────────┤ │
│  │       └── ◇ polynomials                    │ │   GHOST SURFACE │ │
│  │                                             │ │                 │ │
│  │    ◆ agent-town                            │ │  [context____]  │ │
│  │       ├── ◇ citizens                       │ │  [  Surface  ]  │ │
│  │       └── ◇ coalitions                     │ │                 │ │
│  │                                             │ │  relevance: 87% │ │
│  │    ◆ k-gent-soul                           │ │  "Operads def.."│ │
│  │       └── ◇ eigenvectors                   │ │                 │ │
│  │                                             │ │                 │ │
│  └────────────────────────────────────────────┘ └─────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

**Components**:
- `Brain2D.tsx`: Tree-based crystal cartography + side panel
- `CrystalTree.tsx`: Hierarchical concept visualization
- `GhostSurface.tsx`: LLM-powered memory retrieval
- `CaptureForm.tsx`: Real capture → AGENTESE → persistence

**LLM Integration**: Ghost surfacing calls `logos.invoke("self.memory.ghost")` which invokes LLM to find semantic neighbors.

### 4.3 Town → Town2D (Existing Mesa, Enhanced)

**Philosophy**: The Mesa is already 2D. Remove the "demo" pretense. Make every interaction **real**.

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Town: demo]  Day 3 | AFTERNOON | 5 citizens                    ▶ 1x│
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────┐ ┌─────────────────┐ │
│  │                    MESA                     │ │ CITIZEN PANEL   │ │
│  │         Inn                                 │ │                 │ │
│  │           ○ L (Healer)                     │ │ ◆ Socrates      │ │
│  │                                             │ │   Scholar       │ │
│  │                          Plaza              │ │   Phase: WORK   │ │
│  │    Workshop    ◉ K (Scholar)               │ │                 │ │
│  │      ◆ H (Builder)     ◆ A (Builder)       │ │ > Ask Question  │ │
│  │                                             │ │ > View Beliefs  │ │
│  │               Library   ◇ M (Watcher)       │ │ > Journal Entry │ │
│  │                                             │ │                 │ │
│  │                    Market                   │ ├─────────────────┤ │
│  │                                             │ │ DIALOGUE        │ │
│  │                                             │ │                 │ │
│  │                                             │ │ You: What do    │ │
│  │                                             │ │ you think about │ │
│  │                                             │ │ coalitions?     │ │
│  │                                             │ │                 │ │
│  │                                             │ │ Socrates: The   │ │
│  │                                             │ │ strongest bonds │ │
│  │                                             │ │ form through... │ │
│  └────────────────────────────────────────────┘ └─────────────────┘ │
├───────────────────────────────[EVENT FEED]───────────────────────────┤
│  [42] Socrates greeted Marcus | [41] Hypatia built widget | ...     │
└──────────────────────────────────────────────────────────────────────┘
```

**Key Changes**:
1. **Remove "demo" framing**: This IS the experience
2. **LLM dialogue**: "Ask Question" → `logos.invoke("world.town.citizen.dialogue")` → LLM response
3. **Real beliefs**: Citizen beliefs come from M-gent memory
4. **Real events**: `logos.invoke("world.town.step")` triggers actual agent transitions

---

## Part V: Implementation Plans

### 5.1 Agent Alpha: Gardener2D Implementation

**Scope**: Unify garden and session visualizations into organic 2D experience

**Tasks**:
1. Create `Gardener2D.tsx` using ElasticSplit pattern
2. Create `SeasonOrb.tsx` with breathing animation
3. Create `PlotTile.tsx` with vine-style progress
4. Create `GestureStream.tsx` with tone visualization
5. Create `SessionPolynomial.tsx` (inline, not separate)
6. Create `TendingPalette.tsx` with mobile FloatingActions
7. Migrate `TransitionSuggestionBanner.tsx` as `TransitionSuggester.tsx`
8. Update `/gardener` page to use Gardener2D
9. Apply Living Earth palette throughout
10. Tests: Season orb breathing, plot rendering, gesture stream, mobile layout

**AGENTESE Integration**:
- `concept.gardener.manifest` → garden state
- `concept.gardener.session.manifest` → session state
- `concept.gardener.tend` → gesture submission
- `concept.gardener.transition` → season/phase transitions

**Density Behavior**:
- Compact: Vertical stack, BottomDrawer for detail
- Comfortable: Side-by-side garden + session
- Spacious: Full layout with inline teaching

### 5.2 Agent Beta: Gestalt2D Implementation

**Scope**: Replace GestaltVisualization with 2D equivalent

**Tasks**:
1. Create `Gestalt2D.tsx` using ElasticSplit pattern
2. Create `LayerCard.tsx` (health-colored, expandable)
3. Create `ViolationFeed.tsx` (streaming alerts)
4. Migrate FilterPanel, Legend, ModuleSearch as-is
5. Update `/gestalt` page to use Gestalt2D
6. Tests: Layer rendering, mobile collapse, violation updates

**AGENTESE Integration**:
- `self.gestalt.manifest` → topology data
- `self.gestalt.module.{id}` → module details
- `self.gestalt.scan` → trigger rescan

**Density Behavior**:
- Compact: Vertical stack of layer summaries
- Comfortable: 2x2 grid of layers
- Spacious: Full grid with inline violations

### 5.3 Agent Gamma: Brain2D Implementation

**Scope**: Replace BrainCanvas with tree-based 2D visualization

**Tasks**:
1. Create `Brain2D.tsx` using ElasticSplit
2. Create `CrystalTree.tsx` (hierarchical visualization)
3. Extract `GhostSurface.tsx` from existing panels
4. Wire to AGENTESE: `self.memory.capture`, `self.memory.ghost`
5. Add LLM call for ghost surfacing
6. Tests: Tree expansion, capture flow, ghost relevance

**LLM Integration**:
```python
@logos.node("self.memory.ghost")
async def ghost_surface(observer, context: str, limit: int = 5):
    # Embed context
    embedding = await embed(context)
    # Find neighbors
    neighbors = crystal_store.nearest(embedding, k=limit)
    # LLM enrichment (optional)
    if observer.wants_explanation:
        explanation = await llm.explain_relevance(context, neighbors)
        return GhostSurfaceResult(neighbors=neighbors, explanation=explanation)
    return GhostSurfaceResult(neighbors=neighbors)
```

### 5.4 Agent Delta: Town End-to-End

**Scope**: Remove demo scaffolding, make every interaction real

**Tasks**:
1. Delete hardcoded citizen data in TownVisualization
2. Wire citizen list to `world.town.citizens.manifest`
3. Implement `citizen.dialogue` AGENTESE node with LLM
4. Wire event feed to SSE EventBus subscription
5. Add consent checks via Park for citizen interactions
6. Tests: Real dialogue, event subscription, consent flow

**The Critical Path**:
```
User clicks citizen → CitizenPanel shows
User clicks "Ask Question" → DialogueModal opens
User types question → logos.invoke("world.town.citizen.{id}.dialogue", question)
Backend: Load citizen memory → Construct prompt → LLM call → Stream response
UI: Show streaming response → Store in citizen journal → Update beliefs
```

### 5.5 Agent Epsilon: Mothball Migration

**Scope**: Move Three.js visualizers to _mothballed without breaking anything

**Tasks**:
1. Create `_mothballed/three-visualizers/` structure
2. Move files with git history preservation
3. Update any imports that reference moved files (should be none)
4. Add README explaining mothball status
5. Verify build still succeeds
6. Verify no runtime errors on affected pages

---

## Part VI: AGENTESE Paths (New and Updated)

### 6.1 Gardener Paths

```
concept.gardener.*
  concept.gardener.manifest              # Full garden state (plots, season, metrics)
  concept.gardener.session.manifest      # Current session state (phase, intent, stats)
  concept.gardener.plot.{name}           # Plot details
  concept.gardener.tend                  # Submit gesture (verb, target, reasoning)
  concept.gardener.transition.suggest    # Auto-Inducer suggestion
  concept.gardener.transition.accept     # Accept suggested transition
  concept.gardener.transition.dismiss    # Dismiss suggestion (4h cooldown)
  concept.gardener.stream                # SSE subscription for garden events
```

### 6.2 Gestalt Paths

```
self.gestalt.*
  self.gestalt.manifest           # Topology overview (nodes, links, layers)
  self.gestalt.module.{id}        # Module details
  self.gestalt.scan               # Trigger rescan
  self.gestalt.violations         # Current violations
```

### 6.3 Brain Paths

```
self.memory.*
  self.memory.manifest            # Crystal cartography
  self.memory.capture             # Store new crystal (existing)
  self.memory.ghost               # Ghost surface with LLM enrichment
  self.memory.crystal.{id}        # Crystal details
  self.memory.tree                # Hierarchical view
```

### 6.4 Town Paths (Enhanced)

```
world.town.*
  world.town.manifest             # Town overview
  world.town.citizens.manifest    # Live citizen list
  world.town.citizen.{id}         # Citizen details
  world.town.citizen.{id}.dialogue # LLM dialogue (NEW)
  world.town.citizen.{id}.journal  # Journal entries
  world.town.citizen.{id}.beliefs  # Current beliefs
  world.town.step                 # Advance simulation
  world.town.stream               # SSE subscription
```

---

## Part VII: Living Earth Design Tokens

### 7.1 Color Palette

```typescript
export const LIVING_EARTH = {
  // Primary (Warm Earth)
  soil: '#2D1B14',
  bark: '#4A3728',
  wood: '#6B4E3D',
  clay: '#8B6F5C',
  sand: '#AB9080',

  // Secondary (Living Green)
  moss: '#1A2E1A',
  fern: '#2E4A2E',
  sage: '#4A6B4A',
  mint: '#6B8B6B',
  sprout: '#8BAB8B',

  // Accent (Ghibli Glow)
  lantern: '#F5E6D3',
  honey: '#E8C4A0',
  amber: '#D4A574',
  copper: '#C08552',
  bronze: '#8B5A2B',

  // Semantic
  healthy: '#4A6B4A',
  growing: '#D4A574',
  warning: '#C08552',
  urgent: '#8B4513',
  dormant: '#6B4E3D',
} as const;
```

### 7.2 Animation Primitives

```typescript
export const ORGANIC_MOTION = {
  breathe: {
    keyframes: { transform: ['scale(1)', 'scale(1.02)', 'scale(1)'] },
    options: { duration: 3500, iterations: Infinity, easing: 'ease-in-out' },
  },
  grow: {
    keyframes: { transform: ['scale(0)', 'scale(1.1)', 'scale(1)'] },
    options: { duration: 400, easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)' },
  },
  unfurl: {
    keyframes: { height: ['0', '100%'], opacity: ['0', '1'] },
    options: { duration: 400, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' },
  },
  flow: {
    keyframes: { transform: ['translateX(0)', 'translateX(100%)'] },
    options: { duration: 2000, iterations: Infinity, easing: 'linear' },
  },
} as const;
```

### 7.3 Typography (Organic Craft)

```typescript
export const TYPOGRAPHY = {
  headings: {
    fontFamily: 'Nunito, sans-serif',
    h1: { size: '32px', weight: 700, lineHeight: '40px' },
    h2: { size: '24px', weight: 600, lineHeight: '32px' },
    h3: { size: '18px', weight: 500, lineHeight: '24px' },
  },
  body: {
    fontFamily: 'Inter, sans-serif',
    normal: { size: '16px', weight: 400, lineHeight: '24px' },
    small: { size: '14px', weight: 400, lineHeight: '20px' },
  },
  code: {
    fontFamily: 'JetBrains Mono, monospace',
    normal: { size: '14px', weight: 400, lineHeight: '20px' },
  },
} as const;
```

---

## Part VIII: Anti-Patterns

### 8.1 What This Is NOT

- **Not a downgrade**: 2D is more honest, not less capable
- **Not WebGL-free**: PixiJS (Mesa) uses WebGL efficiently
- **Not anti-3D forever**: Mothballed components may revive for VR/AR
- **Not simplification**: LLM integration makes this MORE complex under the hood

### 8.2 Specific Traps

| Trap | Why It's Wrong |
|------|----------------|
| "Add Three.js for polish" | 3D was the polish. Now we want substance. |
| "Keep demo data as fallback" | Demo data prevents discovering real bugs |
| "LLM calls are expensive" | Pre-compute what you can, stream what you must |
| "2D is boring" | Mesa with good visual design is not boring |
| "Dark industrial is fine" | Living Earth warmth is the brand now |
| "Emojis are fine everywhere" | Use sparingly, prefer Lucide icons |

---

## Part IX: Success Criteria

### 9.1 Qualitative

| Criterion | Test |
|-----------|------|
| **Feels generative** | Clicking through should invoke real backends |
| **No dead ends** | Every UI element leads somewhere |
| **LLM feels natural** | Dialogue responses match citizen personality |
| **Density works** | Mobile → tablet → desktop all feel intentional |
| **Feels warm** | Living Earth palette visible, organic animations present |
| **Teaching is visible** | Dense Teacher mode reveals categorical structures |

### 9.2 Quantitative

| Metric | Target |
|--------|--------|
| Lines of code | < 400 per visualization (down from 1000+) |
| Bundle size | 30% smaller (no Three.js in main chunk) |
| First paint | < 500ms (no WebGL context creation) |
| LLM latency | < 2s for dialogue responses (streaming helps) |
| Gardener components | 8 files (unified from current 10+) |
| AGENTESE paths | 7 new paths for Gardener alone |

---

## Part X: Implementation Order

### Phase 1: Mothball (1 session)
Agent Epsilon executes §5.5. No functional changes, just file moves.

### Phase 2: Gardener2D (3 sessions)
Agent Alpha executes §5.1. The meta-jewel that enables all development. Highest priority.

### Phase 3: Gestalt2D (2 sessions)
Agent Beta executes §5.2. Simplest transformation—no LLM needed.

### Phase 4: Brain2D (2 sessions)
Agent Gamma executes §5.3. LLM integration for ghost surfacing.

### Phase 5: Town End-to-End (3 sessions)
Agent Delta executes §5.4. Most complex—full LLM dialogue system.

---

## Appendix A: Component Migration Map

### Gardener Components

```
BEFORE (10 files, 750+ lines)
├── garden/
│   ├── GardenVisualization.tsx (419 lines)
│   ├── SeasonIndicator.tsx (161 lines)
│   ├── PlotCard.tsx (~150 lines)
│   ├── GestureHistory.tsx (~100 lines)
│   └── TransitionSuggestionBanner.tsx (~80 lines)
└── gardener/
    └── GardenerVisualization.tsx (331 lines)

AFTER (8 files, ~600 lines target)
└── gardener/
    ├── Gardener2D.tsx (~150 lines)          # Main container
    ├── GardenCanvas.tsx (~100 lines)        # 2D plot visualization
    ├── SeasonOrb.tsx (~80 lines)            # Breathing season indicator
    ├── PlotTile.tsx (~80 lines)             # Organic plot card
    ├── GestureStream.tsx (~80 lines)        # Live gesture feed
    ├── SessionPolynomial.tsx (~60 lines)    # Inline state machine
    ├── TendingPalette.tsx (~60 lines)       # Action buttons
    └── TransitionSuggester.tsx (~50 lines)  # Auto-Inducer banner
```

### Gestalt Components

```
BEFORE (1060+ lines)
└── gestalt/
    └── GestaltVisualization.tsx (1060 lines) → mothball

AFTER (~400 lines target)
└── gestalt/
    ├── Gestalt2D.tsx (~150 lines)
    ├── LayerCard.tsx (~100 lines)
    ├── ViolationFeed.tsx (~80 lines)
    └── [KEEP: FilterPanel, Legend, ModuleSearch]
```

---

## Appendix B: The Gallery as Foundation

The `gallery/pilots.py` system (2769 lines) already demonstrates the pattern:

- Pilots are 2D-first
- Rich HTML output without Three.js
- Density-aware rendering
- Teaching callouts for explanation

The Crown Jewel pages should feel like **expanded pilots**—same philosophy, more depth.

---

## Appendix C: Existing Primitives to Reuse

| Primitive | Location | Use In |
|-----------|----------|--------|
| `ElasticSplit` | `elastic/` | All 2D pages |
| `BottomDrawer` | `elastic/` | Mobile layouts |
| `FloatingActions` | `elastic/` | Mobile FABs |
| `PolynomialDiagram` | `polynomial/` | SessionPolynomial |
| `PolynomialNode` | `polynomial/` | State machine nodes |
| `TeachingCallout` | `categorical/` | Dense Teacher mode |
| `TracePanel` | `categorical/` | Gesture/event history |
| `StateIndicator` | `categorical/` | Phase badges |
| `Breathe` | `joy/` | Organic animations |
| `celebrate` | `joy/` | Milestone celebrations |
| `Mesa` | `town/` | 2D canvas (PixiJS) |

---

*"The garden tends itself, but only because we planted it together."*

*Spec version: 2.0 | Date: 2025-12-18 | Gardener UX + Living Earth Edition*
