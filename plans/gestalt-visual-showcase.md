---
path: plans/gestalt-visual-showcase
status: active
progress: 0.75
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/gestalt-infrastructure-expansion
  - monetization/grand-initiative-monetization
parent: plans/core-apps/gestalt-architecture-visualizer
session_notes: |
  CHUNK 3 COMPLETE (2025-12-16): Edge Styling & Data Flow Animation
  - EdgeStyles.ts: 9 semantic edge types with color/width/animation config
  - AnimatedEdge.tsx: SmartEdge, AnimatedEdge, StaticEdge components
  - ViolationGlow: Pulsing glow effect for violation edges
  - FlowParticle: Particle animation along edges (selection-driven)
  - FilterPanel: Added "Flow" toggle for animation control
  - Tests: 33 new tests (90 total for gestalt)

  Files created/modified:
  - src/components/gestalt/{EdgeStyles,AnimatedEdge}.tsx (new)
  - src/components/gestalt/{types,index}.ts (extended with showAnimation)
  - src/components/gestalt/FilterPanel.tsx (added Flow toggle)
  - src/pages/Gestalt.tsx (integrated SmartEdge, removed DependencyEdgeComponent)
  - tests/unit/gestalt/edge-styling.test.ts (new)

  CHUNK 2 COMPLETE (2025-12-16): Interactive Legend & Tooltips
  - Legend.tsx: Collapsible legend with health colors, node sizes, edge types
  - NodeTooltip.tsx: 3D hover tooltip using drei's Html component
  - State management: HoverState with 300ms delay, localStorage persistence
  - Integration: Legend in top-right overlay, tooltip on node hover
  - Tests: 33 new tests (57 total for gestalt at that point)

  CHUNK 1 COMPLETE (2025-12-16): Enhanced Filter Panel
  - ViewPresets: 5 one-click view configurations
  - HealthFilter: Interactive grade toggles with distribution badges
  - ModuleSearch: Fuzzy search with keyboard navigation
  - Tests: 24 passing tests for filter logic

  Next: Chunk 4 (Module Search & Quick Navigation) - or pause for showcase
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: touched
  STRATEGIZE: complete
  CROSS-SYNERGIZE: pending
  IMPLEMENT: touched  # Chunks 1, 2 & 3 complete (75%)
  QA: pending
  TEST: touched  # 90 tests passing
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.06
  spent: 0.03
  returned: 0.0
---

# Gestalt Visual Showcase: Completing the Web Dashboard

> *"A beautiful interface is the first proof that the system works."*

**Master Plan**: `plans/core-apps/gestalt-architecture-visualizer.md` (Phase 4)
**Infrastructure Expansion**: `plans/gestalt-infrastructure-expansion.md` (future phases)
**Human Priority**: "VISUAL UIs/Refined interactions" (from `_focus.md`)

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Goal** | Polish Gestalt Web Dashboard to showcase-ready state |
| **Current State** | 60% complete - 3D topology rendering, responsive layout, basic controls |
| **Target State** | Visual showcase with refined filters, data flow visualization, legend |
| **Estimated Effort** | 3-4 focused chunks |
| **Key Constraint** | Build on existing elastic primitives (don't reinvent) |

---

## What Exists Today

### Already Implemented
- 3D force-directed graph (Three.js via react-three-fiber)
- Health-based node coloring (A+:green to F:red gradient)
- Node sizing by LOC and health score
- Dependency edges with violation highlighting
- Layer ring overlays (visual grouping)
- OrbitControls (zoom/pan/rotate, touch support)
- Module detail sidebar (health stats, dependencies, violations)
- Responsive layout via ElasticSplit (mobile drawers, tablet/desktop panels)
- Density-aware rendering (compact/comfortable/spacious)
- Max nodes slider (50-500)
- Layer filter dropdown
- Display toggles (edges, violations, labels)

### What's Missing for Visual Showcase
1. **Enhanced Filter Panel** - View presets, health grade filter, search
2. **Node Shape Differentiation** - Currently all spheres; prepare for infrastructure
3. **Edge Styling by Type** - Currently all gray lines; need semantic colors
4. **Interactive Legend** - Show what each color/shape means
5. **Data Flow Animation** - Animated pulses for read/write directions
6. **Module Search** - Quick jump to module by name
7. **Hover Tooltips** - Quick info without opening detail panel

---

## Implementation Chunks

### Chunk 1: Enhanced Filter Panel (Visual Polish)

**Goal**: Make the filter panel a visual showcase feature itself.

**Files**:
```
impl/claude/web/src/pages/Gestalt.tsx           # Extend ControlPanel
impl/claude/web/src/components/gestalt/         # New: extracted components
├── FilterPanel.tsx                              # New: dedicated filter component
├── ViewPresets.tsx                              # New: preset buttons
└── HealthFilter.tsx                             # New: grade toggles
```

**Features**:

```typescript
// View Presets - One-click common views
interface ViewPreset {
  name: string;
  icon: string;
  filters: Partial<FilterState>;
}

const VIEW_PRESETS: ViewPreset[] = [
  { name: 'All', icon: '🌐', filters: { showAll: true } },
  { name: 'Healthy', icon: '💚', filters: { minHealth: 'B+' } },
  { name: 'At Risk', icon: '⚠️', filters: { maxHealth: 'C' } },
  { name: 'Violations', icon: '🔴', filters: { violationsOnly: true } },
  { name: 'Core', icon: '⭐', filters: { layers: ['protocols', 'agents'] } },
];

// Health Grade Filter - Toggle by grade
interface HealthFilterProps {
  enabledGrades: Set<string>;
  onToggle: (grade: string) => void;
  distribution: Record<string, number>;
}

// Search - Module quick-jump
interface ModuleSearchProps {
  modules: CodebaseModule[];
  onSelect: (module: CodebaseModule) => void;
}
```

**Visual Design**:
```
┌─────────────────────────────────────────────────────────────────┐
│  FILTERS                                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔍 [Search modules...                               ]          │
│                                                                 │
│  VIEW PRESETS                                                   │
│  [🌐 All] [💚 Healthy] [⚠️ At Risk] [🔴 Violations] [⭐ Core]  │
│                                                                 │
│  HEALTH GRADES                                                  │
│  [✓ A+](15) [✓ A](42) [✓ B+](78) [✓ B](56)                    │
│  [✓ C+](23) [✓ C](12) [○ D](3) [○ F](1)                       │
│                                                                 │
│  LAYERS                                                         │
│  [▼ All layers               ]                                  │
│                                                                 │
│  DISPLAY                                                        │
│  [✓] Edges   [✓] Violations   [✓] Labels                       │
│                                                                 │
│  NODES: ──●────────── 150                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Exit Criteria**:
- [x] View presets implemented and responsive
- [x] Health grade filter with distribution badges
- [x] Module search with autocomplete
- [x] All controls use elastic CSS variables
- [x] Mobile: filter panel in bottom drawer with compact layout
- [x] 24 tests passing (search, grade distribution, filter application)

---

### Chunk 2: Interactive Legend & Tooltips

**Goal**: Make the visualization self-documenting.

**Files**:
```
impl/claude/web/src/components/gestalt/
├── Legend.tsx              # New: interactive legend
├── NodeTooltip.tsx         # New: hover tooltip
└── EdgeLegend.tsx          # New: edge type legend
```

**Legend Design**:
```
┌─────────────────────────────────────┐
│  LEGEND                     [−]     │
├─────────────────────────────────────┤
│                                     │
│  NODE HEALTH                        │
│  ● A+/A   ● B+/B   ● C+/C   ● D/F   │
│                                     │
│  NODE SIZE                          │
│  ◯ <100 LOC  ○ ~500 LOC  ● >1K LOC │
│                                     │
│  EDGES                              │
│  ─── Import   ─── Violation         │
│                                     │
│  RINGS = Architectural Layers       │
│                                     │
└─────────────────────────────────────┘
```

**Hover Tooltip**:
```
┌──────────────────────────────────┐
│  protocols.api.brain             │
│  ─────────────────────────────   │
│  Health: A (92%)                 │
│  Layer: api                      │
│  LOC: 245                        │
│  Dependencies: 12 │ Dependents: 5│
│  ─────────────────────────────   │
│  Click for details               │
└──────────────────────────────────┘
```

**Implementation**:

```typescript
// Legend component - collapsible, position configurable
interface LegendProps {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  collapsed?: boolean;
  nodeTypes: NodeKind[];  // For infrastructure expansion
  edgeTypes: EdgeKind[];  // For infrastructure expansion
  density: Density;
}

// Hover tooltip using drei's Html component
interface NodeTooltipProps {
  node: CodebaseModule;
  position: [number, number, number];
  visible: boolean;
}
```

**Exit Criteria**:
- [x] Legend component renders all current node/edge types
- [x] Legend is collapsible (remembers state)
- [x] Hover tooltip appears on node hover (300ms delay)
- [x] Tooltip follows camera rotation (via drei Html sprite mode)
- [x] Mobile: tooltip disabled (falls back to click-for-details pattern)
- [x] Legend extensible for infrastructure node types
- [x] 33 tests (rendering, interaction, position, state management)

---

### Chunk 3: Edge Styling & Data Flow Animation

**Goal**: Make dependencies visually informative and alive.

**Files**:
```
impl/claude/web/src/pages/Gestalt.tsx           # Update edge rendering
impl/claude/web/src/components/gestalt/
├── AnimatedEdge.tsx        # New: animated edge component
└── EdgeStyles.ts           # New: edge styling config
```

**Edge Styling**:

```typescript
// Edge style configuration (prepare for infrastructure expansion)
export const EDGE_STYLES: Record<string, EdgeStyle> = {
  // Current types
  import: { color: '#6b7280', dash: false, width: 1, opacity: 0.25 },
  violation: { color: '#ef4444', dash: false, width: 2.5, opacity: 0.9 },

  // Future infrastructure types (Phase 5 ready)
  reads: { color: '#3b82f6', dash: false, width: 2, opacity: 0.6 },
  writes: { color: '#ef4444', dash: false, width: 2, opacity: 0.6 },
  calls: { color: '#f97316', dash: true, width: 1.5, opacity: 0.5 },
  publishes: { color: '#8b5cf6', dash: false, width: 1.5, opacity: 0.5, animated: true },
  subscribes: { color: '#8b5cf6', dash: true, width: 1.5, opacity: 0.5 },
};

// Animated edge for data flow visualization
interface AnimatedEdgeProps {
  source: [number, number, number];
  target: [number, number, number];
  style: EdgeStyle;
  animationSpeed?: number;  // 0 = static, 1 = normal, 2 = fast
  direction?: 'forward' | 'reverse' | 'both';
}
```

**Animation Pattern**:
```
Static edge:     ─────────────────────────────
Animated edge:   ─●───────●───────●───────●───  (particles flowing)
Violation edge:  ══════════════════════════════  (thicker, red)
```

**Features**:
1. **Flow Particles**: Small dots traveling along edges
2. **Direction Indicator**: Arrow or particle direction shows data flow
3. **Violation Pulse**: Red edges pulse gently to draw attention
4. **Selection Highlight**: Selected node's edges glow brighter

**Exit Criteria**:
- [x] Edge styles differentiate import vs violation
- [x] Flow animation on selected node's edges
- [x] Violation edges have attention-drawing pulse
- [x] Animation performs well (SmartEdge only animates active/selected edges)
- [x] Animation can be toggled off (showAnimation in FilterState)
- [x] Edge styling is extensible for infrastructure types (9 types defined)
- [x] 33 tests (styling config, pulse functions, integration)

---

### Chunk 4: Module Search & Quick Navigation

**Goal**: Enable rapid exploration of large codebases.

**Files**:
```
impl/claude/web/src/components/gestalt/
├── ModuleSearch.tsx        # Combobox with fuzzy search
└── NavigationControls.tsx  # Zoom-to-fit, reset view
```

**Search Component**:

```typescript
interface ModuleSearchProps {
  modules: CodebaseModule[];
  onSelect: (module: CodebaseModule) => void;
  onFocus: (module: CodebaseModule) => void;  // Highlight without selecting
  density: Density;
}

// Search features:
// - Fuzzy matching (protocols.api.brain matches "api brain")
// - Recent searches (stored in localStorage)
// - Keyboard navigation (arrow keys, enter to select)
// - Preview on hover (camera zooms toward module)
```

**Visual Design**:
```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 [api brain                                            ] ×   │
├─────────────────────────────────────────────────────────────────┤
│  MATCHES (3)                                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  protocols.api.brain                        A (92%)  api   │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  protocols.api.models                       B+ (85%) api   │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  protocols.api.billing                      A (90%)  api   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  RECENT                                                         │
│  agents.town.coalitions • protocols.gestalt.analysis           │
└─────────────────────────────────────────────────────────────────┘
```

**Navigation Controls**:

```
┌─────────────────┐
│  [⊞] Fit All    │  Zoom to show all nodes
│  [⊚] Reset View │  Return to default camera position
│  [◎] Focus      │  Zoom to selected module
└─────────────────┘
```

**Exit Criteria**:
- [ ] Fuzzy search with <50ms response time
- [ ] Keyboard navigation (↑↓ to browse, Enter to select, Esc to close)
- [ ] Recent searches persisted (top 5)
- [ ] Camera smoothly animates to selected module
- [ ] Navigation controls in both panel and overlay
- [ ] Mobile: full-screen search modal
- [ ] 10+ tests (fuzzy matching, keyboard, camera animation)

---

## Integration with Infrastructure Expansion

This plan prepares the visual foundation for `plans/gestalt-infrastructure-expansion.md`:

| Visual Feature | Infrastructure Readiness |
|----------------|-------------------------|
| Edge styling | `EDGE_STYLES` includes reads/writes/calls types |
| Node shapes | Legend is extensible for NodeKind enum |
| Filter panel | Layer filter can expand to node kind filter |
| Search | Module search handles infrastructure nodes |
| Legend | Shows all node/edge types when available |

When infrastructure expansion begins (Phases 1-8), the visual layer is ready:

```typescript
// Phase 5 of infrastructure expansion adds:
const NODE_SHAPES: Record<NodeKind, NodeShape> = {
  MODULE: 'sphere',
  DATABASE: 'cylinder',
  QUEUE: 'torus',
  API: 'octahedron',
  STORAGE: 'box',
  SERVICE: 'dodecahedron',
  CONFIG: 'icosahedron',
  PIPELINE: 'cone',
};

// Filter panel gains:
// [✓] Modules  [✓] Databases  [✓] APIs  [✓] Services
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Filter interaction latency | <100ms | Time from click to graph update |
| Search response time | <50ms | Time from keystroke to results |
| Animation FPS | 60fps | Chrome DevTools performance panel |
| Tooltip display latency | <300ms | Time from hover to tooltip visible |
| Mobile usability | All features accessible | Manual testing on 320px viewport |

---

## User Flow: The Visual Showcase Demo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DEMO FLOW: "Explore kgents architecture in 60 seconds"                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. LANDING (0-5s)                                                           │
│     ├── 3D graph renders immediately with all modules visible               │
│     ├── Overall health grade shown: "B+ (86%)"                              │
│     └── Stats overlay: "1814 modules • 14226 edges"                         │
│                                                                              │
│  2. QUICK FILTER (5-15s)                                                     │
│     ├── Click [⚠️ At Risk] preset                                          │
│     ├── Graph filters to show only C/D/F modules                            │
│     ├── Remaining nodes pulse gently to draw attention                      │
│     └── "23 modules need attention"                                         │
│                                                                              │
│  3. SEARCH (15-25s)                                                          │
│     ├── Type "agentese" in search box                                       │
│     ├── Results dropdown shows matching modules                             │
│     ├── Hover over result → camera smoothly zooms toward it                 │
│     ├── Click result → camera centers, node selected, detail panel opens   │
│     └── Shows health breakdown, dependencies, violations                    │
│                                                                              │
│  4. DATA FLOW (25-40s)                                                       │
│     ├── With module selected, see animated edges flowing                    │
│     ├── Blue particles show imports coming in                               │
│     ├── Gray particles show exports going out                               │
│     └── Red edges pulse gently for violations                               │
│                                                                              │
│  5. LEGEND & EXPLORATION (40-60s)                                            │
│     ├── Collapse legend to free space                                       │
│     ├── Click reset view to zoom out                                        │
│     ├── Use layer filter to isolate "protocols"                             │
│     └── Rotate/zoom to explore the layered architecture                     │
│                                                                              │
│  RESULT: User has visually explored architecture, found risky modules,      │
│          understood dependencies, and learned the visualization language.   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| `impl/claude/web/src/components/elastic/` | Code | ElasticContainer, ElasticSplit patterns |
| `impl/claude/web/src/api/types.ts` | Code | CodebaseModule, DependencyLink types |
| `@react-three/drei` | Package | Html component for tooltips |
| `fuse.js` | Package | Fuzzy search (lightweight) |
| `framer-motion` | Package | Animation (already installed) |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 3D tooltip performance | Medium | Use drei's Html with sprite mode |
| Edge animation at scale | High | Use instanced geometry, animation shader |
| Search performance | Low | fuse.js is O(n log n), pre-index on load |
| Mobile touch precision | Medium | Larger hit areas, tap-to-select-then-drag |

---

## Testing Strategy

| Category | Count | Description |
|----------|-------|-------------|
| Unit tests (filter logic) | 15+ | Preset application, grade filtering, search matching |
| Unit tests (components) | 15+ | Legend, tooltip, search, edge styles |
| Integration tests | 10+ | Filter → graph update, search → camera animation |
| E2E tests | 5+ | Full demo flow, responsive breakpoints |
| Performance tests | 5+ | Animation FPS, search latency, render time |

---

## Chunk Execution Order

```
Chunk 1: Enhanced Filter Panel    ←── Start here (biggest visual impact)
    │
    ▼
Chunk 2: Legend & Tooltips        ←── Self-documenting visualization
    │
    ▼
Chunk 3: Edge Styling & Animation ←── Makes graph feel "alive"
    │
    ▼
Chunk 4: Search & Navigation      ←── Complete the exploration UX
    │
    ▼
[Ready for Infrastructure Expansion Phase 5: Visual Differentiation]
```

---

*"The best documentation is a visualization that explains itself."*
