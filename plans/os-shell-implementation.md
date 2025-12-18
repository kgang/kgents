# OS Shell Implementation Plan

**Status:** Planning
**Created:** 2025-12-17
**Specs:** `spec/protocols/os-shell.md`, `spec/protocols/projection.md`, `spec/protocols/agentese.md`
**Creative:** `docs/creative/` (all documents)

---

## Mission

Transform the kgents web interface from a collection of pages into an **operating system interface** for engaging in autopoiesis. This involves two parallel tracks:

1. **Track A: OS Shell Foundation** — Build the unified layout wrapper with three persistent layers
2. **Track B: Crown Jewel Creative Overhaul** — Refactor existing jewel pages to projection-first rendering

---

## Pre-Implementation Assessment

Before writing any code, assess the current state against specs:

### 1. Spec Alignment Audit

For each spec, verify understanding and identify gaps:

```
SPEC: spec/protocols/os-shell.md
- [ ] Observer Drawer requirements understood
- [ ] Navigation Tree auto-discovery requirements understood
- [ ] Terminal service requirements understood
- [ ] Density adaptation requirements understood
- [ ] PathProjection component requirements understood

SPEC: spec/protocols/projection.md
- [ ] Density-Content Isomorphism understood
- [ ] Layout primitives (Split, Panel, Actions) understood
- [ ] Content degradation levels understood
- [ ] Three-stage layout pattern understood

SPEC: spec/protocols/agentese.md
- [ ] Five contexts understood (world, self, concept, void, time)
- [ ] Gateway discovery endpoints understood
- [ ] Observer/Umwelt structure understood
- [ ] Path composition understood

CREATIVE: docs/creative/visual-system.md
- [ ] No-emoji policy understood (JEWEL_ICONS not JEWEL_EMOJI)
- [ ] OS Shell layout pattern understood
- [ ] Color semantic mapping understood
- [ ] Density breakpoints understood (640/768/1024)

CREATIVE: docs/creative/implementation-guide.md
- [ ] Projection-first page pattern understood
- [ ] Joy components usage understood
- [ ] Observer context usage understood
- [ ] Terminal integration understood
```

### 2. Current Implementation Inventory

Audit existing code to understand what exists:

```
INVENTORY: impl/claude/web/src/

Layout:
- [ ] Current Layout.tsx analyzed
- [ ] Current routing structure analyzed
- [ ] Current navigation pattern analyzed

Components:
- [ ] Elastic primitives inventory (ElasticSplit, ElasticCard, etc.)
- [ ] Gallery primitives inventory
- [ ] Joy components inventory (Breathe, Shake, Pop, Shimmer)
- [ ] Projection components inventory

Pages:
- [ ] Crown.tsx current state
- [ ] Brain.tsx current state and LOC
- [ ] Gestalt.tsx current state and LOC
- [ ] Gardener.tsx current state and LOC
- [ ] Atelier.tsx current state and LOC
- [ ] Town.tsx current state and LOC
- [ ] ParkScenario.tsx current state and LOC

API:
- [ ] AGENTESE gateway endpoints (/agentese/discover, etc.)
- [ ] Current API client patterns
- [ ] WebSocket/SSE usage patterns
```

### 3. Gap Analysis

Identify what needs to be built vs. what exists:

```
GAPS:

Shell Infrastructure (Track A):
- [ ] ShellProvider (density, observer context) — EXISTS / PARTIAL / MISSING
- [ ] ObserverDrawer component — EXISTS / PARTIAL / MISSING
- [ ] NavigationTree component — EXISTS / PARTIAL / MISSING
- [ ] Terminal component — EXISTS / PARTIAL / MISSING
- [ ] TerminalService — EXISTS / PARTIAL / MISSING
- [ ] PathProjection component — EXISTS / PARTIAL / MISSING

Creative Alignment (Track B):
- [ ] Emoji removal needed in: [list files]
- [ ] Icon system (JEWEL_ICONS) — EXISTS / PARTIAL / MISSING
- [ ] Pages needing projection-first refactor: [list pages]
- [ ] Gallery primitives coverage gaps: [list missing]
```

---

## Track A: OS Shell Foundation

### Phase A1: Shell Infrastructure

**Goal:** Create the shell wrapper that provides context to all children.

```
impl/claude/web/src/shell/
  ShellProvider.tsx       # Context for density, observer
  index.ts
```

**ShellProvider Requirements:**
- Provide density context (compact/comfortable/spacious)
- Provide observer context (archetype, capabilities)
- Provide trace collection for devex
- Wrap entire app in context

**Acceptance Criteria:**
- [ ] `useShell()` hook returns { density, observer, traces }
- [ ] Density updates on window resize
- [ ] Observer can be modified via drawer
- [ ] All children can access context

### Phase A2: Observer Drawer

**Goal:** Build the top-fixed observer context display.

```
impl/claude/web/src/shell/
  ObserverDrawer.tsx      # Top-fixed observer context
```

**Requirements:**
- Collapsed state (40px): Observer archetype, capabilities summary, tier
- Expanded state (200-400px): Full umwelt, traces, controls
- Toggle on click
- Never hidden, always present

**Acceptance Criteria:**
- [ ] Shows current observer archetype
- [ ] Shows capability badges
- [ ] Expands to show recent traces
- [ ] Provides controls to edit archetype
- [ ] Adapts to density (compact shows icon only)

### Phase A3: Navigation Tree

**Goal:** Build sidebar tree navigation from AGENTESE registry.

```
impl/claude/web/src/shell/
  NavigationTree.tsx      # Sidebar tree navigation
```

**Requirements:**
- Auto-populate from `/agentese/discover`
- Tree structure mirrors five contexts
- Crown Jewel shortcuts section
- Highlights current path
- Clicking navigates AND invokes manifest

**Acceptance Criteria:**
- [ ] Fetches paths from gateway on mount
- [ ] Renders tree with expandable context nodes
- [ ] Shows Crown Jewel shortcuts
- [ ] Current path highlighted
- [ ] Adapts to density (hamburger in compact)

### Phase A4: Terminal Layer

**Goal:** Build integrated AGENTESE terminal with persistence.

```
impl/claude/web/src/shell/
  Terminal.tsx            # Bottom terminal UI
  TerminalService.ts      # Terminal logic and persistence
```

**Requirements:**
- Full AGENTESE grammar support (paths, composition, queries)
- Tab completion from registry
- History persistence (localStorage, upgrade to D-gent)
- Collections (save/load request sets)
- Discovery tools (?, help, affordances)

**Acceptance Criteria:**
- [ ] Execute any AGENTESE path
- [ ] Tab completion works
- [ ] History survives refresh
- [ ] Can save/load collections
- [ ] Adapts to density (floating FAB in compact)

### Phase A5: PathProjection Component

**Goal:** Build generic path-to-projection wrapper.

```
impl/claude/web/src/shell/
  PathProjection.tsx      # Generic path->projection wrapper
  DynamicProjection.tsx   # Route-based projection
```

**Requirements:**
- Invoke AGENTESE path on mount
- Pass data and context to children
- Handle loading/error states
- Support streaming (SSE)
- Provide refetch capability

**Acceptance Criteria:**
- [ ] `<PathProjection path="world.town">` works
- [ ] Renders loading state (PersonalityLoading)
- [ ] Renders error state (EmpathyError)
- [ ] Passes density and observer to children
- [ ] Streaming updates work

### Phase A6: Shell Integration

**Goal:** Replace current Layout with Shell.

**Migration:**
1. Create Shell.tsx composing all layers
2. Update App.tsx to use Shell instead of Layout
3. Verify all routes work
4. Remove old Layout.tsx

**Acceptance Criteria:**
- [ ] All routes render within Shell
- [ ] Observer drawer visible on all pages
- [ ] Navigation tree populated
- [ ] Terminal accessible
- [ ] No visual regressions

---

## Track B: Crown Jewel Creative Overhaul

### Phase B1: Emoji Audit and Removal

**Goal:** Replace all emojis with Lucide icons per no-emoji policy.

**Files to audit:**
- `src/components/layout/Layout.tsx` — NavLink icons
- `src/components/synergy/types.ts` — JEWEL_INFO
- `src/components/joy/PersonalityLoading.tsx` — Loading messages
- All page files for emoji usage

**Create:**
```typescript
// src/constants/jewels.ts
import { Brain, Network, Leaf, Palette, Users, Theater, Building } from 'lucide-react';

export const JEWEL_ICONS = {
  brain: Brain,
  gestalt: Network,
  gardener: Leaf,
  atelier: Palette,
  coalition: Users,
  park: Theater,
  domain: Building,
} as const;
```

**Acceptance Criteria:**
- [ ] No emojis in navigation
- [ ] No emojis in jewel identifiers
- [ ] Icons used consistently
- [ ] PersonalityLoading updated

### Phase B2: Brain Page Refactor

**Goal:** Refactor Brain to projection-first pattern.

**Before:** Page with embedded fetch, state, handlers
**After:** PathProjection wrapper with visualization component

```tsx
// Target state
export default function BrainPage() {
  return (
    <PathProjection path="self.memory" aspect="manifest">
      {(data, { density }) => (
        <BrainVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

**Acceptance Criteria:**
- [ ] Page LOC < 50
- [ ] All visualization in BrainVisualization component
- [ ] BrainVisualization uses Gallery primitives
- [ ] Density adaptation works

### Phase B3: Gestalt Page Refactor

**Goal:** Refactor Gestalt to projection-first pattern.

```tsx
export default function GestaltPage() {
  return (
    <PathProjection path="world.gestalt" aspect="manifest">
      {(data, { density }) => (
        <GestaltVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

**Acceptance Criteria:**
- [ ] Page LOC < 50
- [ ] OrganicNode, VineEdge from Gallery
- [ ] FilterPanel density-aware
- [ ] Graph rendering uses existing primitives

### Phase B4: Gardener Page Refactor

**Goal:** Refactor Gardener to projection-first pattern.

```tsx
export default function GardenerPage() {
  return (
    <PathProjection path="concept.gardener" aspect="manifest">
      {(data, { density }) => (
        <GardenVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

**Acceptance Criteria:**
- [ ] Page LOC < 50
- [ ] SeasonIndicator, PlotCard from Gallery
- [ ] GestureHistory component reused

### Phase B5: Atelier Page Refactor

**Goal:** Refactor Atelier to projection-first pattern.

```tsx
export default function AtelierPage() {
  return (
    <PathProjection path="world.atelier" aspect="manifest">
      {(data, { density }) => (
        <AtelierVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

**Acceptance Criteria:**
- [ ] Page LOC < 50
- [ ] ArtisanGrid, PieceCard from Gallery
- [ ] Streaming commission uses PathProjection streaming

### Phase B6: Town/Coalition Page Refactor

**Goal:** Refactor Town to projection-first pattern.

```tsx
export default function TownPage() {
  return (
    <PathProjection path="world.town" aspect="manifest">
      {(data, { density }) => (
        <TownVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

**Acceptance Criteria:**
- [ ] Page LOC < 50
- [ ] Mesa, CitizenPanel from Gallery
- [ ] VirtualizedCitizenList reused

### Phase B7: Park Page Refactor

**Goal:** Refactor Park to projection-first pattern.

```tsx
export default function ParkPage() {
  return (
    <PathProjection path="world.park" aspect="manifest">
      {(data, { density }) => (
        <ParkVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
```

**Acceptance Criteria:**
- [ ] Page LOC < 50
- [ ] PhaseTransition, MaskSelector from Gallery
- [ ] ConsentMeter, TimerDisplay reused

---

## Integration Testing

### Visual Regression

- [ ] All pages render at compact density
- [ ] All pages render at comfortable density
- [ ] All pages render at spacious density
- [ ] Observer drawer functions at all densities
- [ ] Terminal functions at all densities
- [ ] Navigation tree functions at all densities

### Functional Testing

- [ ] Navigation tree reflects actual registry
- [ ] PathProjection invokes correct paths
- [ ] Terminal executes AGENTESE commands
- [ ] History persists across refresh
- [ ] Observer context affects projections

### Performance

- [ ] Shell adds < 50ms to initial render
- [ ] Navigation tree discovery cached
- [ ] Terminal completion responsive (< 100ms)
- [ ] Page transitions smooth

---

## Success Criteria

### Quantitative

| Metric | Target |
|--------|--------|
| Page LOC (average) | < 50 lines |
| Gallery primitive coverage | 100% of visualizations |
| Navigation paths auto-discovered | 100% |
| Terminal commands working | All AGENTESE grammar |
| Emoji count in kgents copy | 0 |

### Qualitative

- [ ] Opening any route shows Observer Drawer context
- [ ] Navigation tree reflects actual registry state
- [ ] Terminal works offline (cached discovery)
- [ ] Density adaptation feels natural
- [ ] No emojis in kgents-authored copy
- [ ] Power users feel "at home" in terminal
- [ ] New users can discover features via tree

---

## Prompt for Implementation

Use this prompt to guide implementation sessions:

```
You are implementing the kgents OS Shell and Crown Jewel creative overhaul.

SPECS TO FOLLOW:
- spec/protocols/os-shell.md — Unified layout wrapper specification
- spec/protocols/projection.md — Density and target projection
- spec/protocols/agentese.md — Gateway and path semantics

CREATIVE DIRECTION:
- docs/creative/visual-system.md — Colors, typography, NO EMOJIS
- docs/creative/philosophy.md — Principles to aesthetics
- docs/creative/implementation-guide.md — Practical patterns

KEY POLICIES:
1. NO EMOJIS in kgents-authored copy — use Lucide icons
2. PROJECTION-FIRST pages — delegate to PathProjection, < 50 LOC
3. GALLERY PRIMITIVES — all visualizations from /gallery components
4. THREE PERSISTENT LAYERS — Observer Drawer, Navigation Tree, Terminal
5. AUTO-DISCOVERY — Navigation from /agentese/discover

CURRENT TASK: [specify phase]

EXISTING CODE TO REFERENCE:
- impl/claude/web/src/components/elastic/ — Elastic primitives
- impl/claude/web/src/components/gallery/ — Gallery components
- impl/claude/web/src/components/joy/ — Joy components
- impl/claude/web/src/hooks/useLayoutContext.ts — Density hooks

OUTPUT:
- Working code following specs
- No emojis
- Density-aware components
- Integration with existing patterns
```

---

## Notes

- Start with Track A (Shell) as it enables Track B (Jewel refactors)
- Phase A5 (PathProjection) is critical — test thoroughly
- Emoji removal (B1) can happen in parallel with A phases
- Each jewel refactor is independent after B1

---

*"The shell is not a frame. It is the ground from which the garden grows."*
