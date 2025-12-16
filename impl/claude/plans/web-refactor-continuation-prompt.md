# Web Refactor Continuation Prompt

> Use with `/hydrate` to continue phases 2-4 of the webapp refactor.
> **Note**: For Phase 3 specifically, see `web-refactor-phase3-continuation.md`.

## Context

Phase 1 (Elastic Primitives Foundation) is **complete**.
Phase 2 (Interaction Patterns) is **complete**.

The following infrastructure exists:

### Created Files (Phase 1: Elastic Primitives)

```
src/styles/globals.css          # Extended with elastic CSS custom properties
src/components/elastic/
├── index.ts                    # Barrel export
├── ElasticContainer.tsx        # Self-arranging container (flow/grid/masonry/stack)
├── ElasticCard.tsx             # Priority-aware card with drag support (+ style prop)
├── ElasticPlaceholder.tsx      # Loading/empty/error states with personality
└── ElasticSplit.tsx            # Two-pane responsive layout

src/hooks/useLayoutContext.ts   # Layout measurement hook (ResizeObserver)
src/reactive/types.ts           # Extended with WidgetLayoutHints, LayoutContext
```

### Created Files (Phase 2: Interaction Patterns - 100%)

```
src/components/dnd/
├── index.ts                    # Barrel export
├── types.ts                    # DragData, DropZone, Pipeline types
├── DndProvider.tsx             # App-level DnD context with sensors
├── DraggableAgent.tsx          # Draggable citizen (grip/icon/card modes)
├── PipelineSlot.tsx            # Drop zone with validation feedback
└── DragPreview.tsx             # Visual feedback during drag

src/components/pipeline/
├── index.ts                    # Barrel export
├── usePipeline.ts              # State management with undo/redo
├── PipelineCanvas.tsx          # SVG canvas with pan/zoom/grid
├── PipelineNode.tsx            # Node with input/output ports
├── PipelineEdge.tsx            # Bezier curves with arrowheads
└── ContextMenu.tsx             # Right-click menus for nodes/edges

src/components/timeline/
├── index.ts                    # Barrel export
└── TimelineScrubber.tsx        # Play controls, event markers, seek

src/hooks/useHistoricalMode.ts  # Live/historical switching, snapshot cache
src/hooks/useKeyboardShortcuts.ts # Global shortcuts with context awareness
src/hooks/useTouchGestures.ts   # Pinch-zoom, long-press, swipe gestures
```

### Dependencies Added (Phase 2)

```json
"@dnd-kit/core": "^6.x",
"@dnd-kit/sortable": "^8.x",
"@dnd-kit/utilities": "^3.x"
```

### CSS Classes Available

- `.town-grid`, `.workshop-grid` — Named grid areas with responsive collapse
- `.elastic-flow`, `.elastic-grid`, `.elastic-masonry`, `.elastic-stack-v`, `.elastic-stack-h`
- `.elastic-card`, `.elastic-button` — Micro-interaction transitions
- `.elastic-skeleton`, `.elastic-focus` — Loading and accessibility

### Types Available

```typescript
// From src/reactive/types.ts
interface WidgetLayoutHints {
  flex?: number;
  minWidth?: number;
  maxWidth?: number;
  priority?: number;
  aspectRatio?: number;
  collapsible?: boolean;
  collapseAt?: number;
}

interface LayoutContext {
  availableWidth: number;
  availableHeight: number;
  depth: number;
  parentLayout: 'flow' | 'grid' | 'masonry' | 'stack';
  isConstrained: boolean;
  density: 'compact' | 'comfortable' | 'spacious';
}
```

---

## Phases 2-4 Implementation Guide

### Phase 2: Interaction Patterns (100% Complete)

**Goal**: Enable drag-drop agent composition and pipeline building.

**Reference**: `plans/web-refactor/interaction-patterns.md`

**Completed**:
- [x] Install DnD library (`@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`)
- [x] DnD infrastructure (`DndProvider`, `DraggableAgent`, `PipelineSlot`, `DragPreview`)
- [x] Pipeline Canvas (`PipelineCanvas`, `PipelineNode`, `PipelineEdge`, `usePipeline`)
- [x] Historical Mode (`TimelineScrubber`, `useHistoricalMode`)
- [x] Keyboard shortcuts (`useKeyboardShortcuts`)
- [x] Undo/redo for pipeline edits
- [x] Visual differentiation CSS (sepia overlay, badge, disabled interactions)
- [x] Touch gestures (`useTouchGestures`: pinch-zoom, long-press, swipe)
- [x] Context menus (`ContextMenu`, `NodeContextMenu`, `EdgeContextMenu`)

### Phase 3: User Flows

**Goal**: Four core flows completable in ≤3 clicks.

**Reference**: `plans/web-refactor/user-flows.md`

**Tasks**:

1. **Create Agent Flow** (`src/components/creation/`)
   - `AgentCreationWizard.tsx` — Modal wizard with steps
   - `ArchetypePalette.tsx` — Visual archetype selection (Scout/Sage/Spark/Steady/Sync)
   - `EigenvectorSliders.tsx` — Customize warmth/curiosity/trust
   - `AgentPreview.tsx` — Live preview of agent config
   - `AdvancedEditor.tsx` — JSON/YAML direct editing

2. **Chat Flow** (`src/components/chat/`)
   - `ChatDrawer.tsx` — Slide-in chat panel
   - `ChatMessage.tsx` — Message bubble with inner voice toggle
   - `MultiAgentChat.tsx` — Multiple participants mode
   - Wire to existing INHABIT API

3. **Details Flow** — Enhance existing CitizenPanel
   - `AgentDetails.tsx` — Tabbed detail view
   - Tabs: Overview, Metrics, Relationships, State, History
   - Export functionality

4. **Orchestrate Flow** (`src/components/orchestration/`)
   - `OrchestrationCanvas.tsx` — Full-screen pipeline builder
   - `ExecutionMonitor.tsx` — Live execution status
   - Pipeline templates (Exploration, Build, Full Cycle)

### Phase 4: Performance

**Goal**: <1.5s FCP, <300KB bundle, 60fps rendering.

**Reference**: `plans/web-refactor/performance.md`

**Tasks**:

1. **Analysis**
   ```bash
   npm install -D vite-bundle-visualizer
   npm run build -- --analyze
   ```
   Run Lighthouse, profile SSE handling

2. **Code Splitting**
   - Lazy load routes in `App.tsx`
   - Split heavy components (PipelineCanvas, MetricsChart)
   - Add Suspense boundaries with ElasticPlaceholder fallbacks

3. **Virtualization**
   ```bash
   npm install @tanstack/react-virtual
   ```
   - `VirtualizedCitizenList.tsx` — For sidebar lists
   - Viewport-based Mesa rendering

4. **Memoization Audit**
   - Add `React.memo` to all widget components
   - Fix stale closures in SSE hooks (use refs)
   - Custom comparison functions for complex props

5. **SSE Optimization**
   - Event batching with debounce
   - Consider Web Worker for JSON parsing
   - Differential updates (patches vs full replace)

---

## Quick Start Commands

```bash
# Navigate to web directory
cd impl/claude/web

# Install new dependencies (Phase 2)
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities

# Install performance tools (Phase 4)
npm install @tanstack/react-virtual
npm install -D vite-bundle-visualizer

# Development
npm run dev

# Type check
npm run typecheck

# Full validation
npm run validate
```

---

## Key Patterns to Follow

1. **Elastic-first**: New components should use ElasticContainer/ElasticCard
2. **Layout hints**: Pass `layout` prop through widget hierarchy
3. **Graceful degradation**: ElasticPlaceholder for all loading/error states
4. **Projection Protocol**: Same widget state → multiple render targets
5. **Personality**: Friendly error messages (see ElasticPlaceholder)

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Drag latency | <16ms | Performance.mark in DnD handler |
| 3-click flows | 100% | Manual testing all 4 flows |
| FCP | <1.5s | Lighthouse |
| Bundle size | <300KB | Build output |
| Widget render | <16ms | React Profiler |

---

## Plan Files

- `plans/web-refactor/webapp-refactor-master.md` — Master plan (40% complete)
- `plans/web-refactor/elastic-primitives.md` — Phase 1 (100% complete)
- `plans/web-refactor/interaction-patterns.md` — Phase 2 (100% complete)
- `plans/web-refactor/user-flows.md` — Phase 3 (0%)
- `plans/web-refactor/performance.md` — Phase 4 (0%)
- `plans/web-refactor/polish-and-delight.md` — Phase 5 (0%)

## Continuation Prompts

- `impl/claude/plans/web-refactor-continuation-prompt.md` — This file (general)
- `impl/claude/plans/web-refactor-phase3-continuation.md` — Phase 3 specific

---

*"The form that generates forms is itself a form."* — AD-006
