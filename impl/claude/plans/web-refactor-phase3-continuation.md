# Web Refactor Phase 3 Continuation Prompt

> Use with `/hydrate` to continue Phase 3 (User Flows) of the webapp refactor.

## Context from Previous Sessions

**Phase 1 (Elastic Primitives)**: **COMPLETE**
**Phase 2 (Interaction Patterns)**: **COMPLETE**

### Available Infrastructure

```
src/styles/globals.css           # Elastic system + historical mode + context menu CSS

src/components/elastic/
├── index.ts                     # Barrel export
├── ElasticContainer.tsx         # Self-arranging container (flow/grid/masonry/stack)
├── ElasticCard.tsx              # Priority-aware card with drag support
├── ElasticPlaceholder.tsx       # Loading/empty/error states with personality
└── ElasticSplit.tsx             # Two-pane responsive layout

src/components/dnd/
├── index.ts                     # Barrel export
├── types.ts                     # DragData, DropZoneConfig, Pipeline types
├── DndProvider.tsx              # App-level DnD context with sensors
├── DraggableAgent.tsx           # Draggable citizen card (grip/icon/card modes)
├── PipelineSlot.tsx             # Drop zone with validation feedback
└── DragPreview.tsx              # Visual feedback during drag

src/components/pipeline/
├── index.ts                     # Barrel export
├── usePipeline.ts               # State management with undo/redo
├── PipelineCanvas.tsx           # SVG canvas with pan/zoom/grid
├── PipelineNode.tsx             # Node with input/output ports
├── PipelineEdge.tsx             # Bezier curves with arrowheads
└── ContextMenu.tsx              # Right-click menus (NodeContextMenu, EdgeContextMenu)

src/components/timeline/
├── index.ts                     # Barrel export
└── TimelineScrubber.tsx         # Play controls, event markers, seek

src/hooks/
├── useLayoutContext.ts          # Layout measurement (ResizeObserver)
├── useHistoricalMode.ts         # Live/historical switching, snapshot cache
├── useKeyboardShortcuts.ts      # Global shortcuts with context awareness
└── useTouchGestures.ts          # Pinch-zoom, long-press, swipe gestures
```

### Key Types Available

```typescript
// DnD types (src/components/dnd/types.ts)
type DragItemType = 'agent' | 'pipeline-node' | 'widget' | 'archetype';
interface DragData<T = unknown> { type: DragItemType; id: string; sourceZone: string; payload: T; }
interface Pipeline { id: string; name: string; nodes: PipelineNodeData[]; edges: PipelineEdge[]; }

// Layout types (src/reactive/types.ts)
interface WidgetLayoutHints { flex?: number; minWidth?: number; priority?: number; collapsible?: boolean; }
interface LayoutContext { availableWidth: number; depth: number; parentLayout: 'flow' | 'grid' | 'masonry' | 'stack'; }

// History types (src/hooks/useHistoricalMode.ts)
type HistoryMode = 'live' | 'historical';

// Touch gesture types (src/hooks/useTouchGestures.ts)
interface PinchState { isPinching: boolean; scale: number; center: { x: number; y: number }; }
interface LongPressState { isPressing: boolean; progress: number; position: { x: number; y: number } | null; }
interface SwipeState { isSwiping: boolean; direction: 'left' | 'right' | 'up' | 'down' | null; distance: number; }
```

### CSS Classes Available

```css
/* Elastic primitives */
.elastic-flow, .elastic-grid, .elastic-masonry, .elastic-stack-v, .elastic-stack-h
.elastic-card, .elastic-button, .elastic-skeleton, .elastic-focus

/* Grids */
.town-grid, .workshop-grid  /* Named grid areas with responsive collapse */

/* Historical mode */
.historical-mode            /* Sepia overlay + "Viewing History" badge */
.interactive-element        /* Gets disabled in historical mode */
[data-always-interactive]   /* Stays interactive in historical mode */

/* Context menus */
.context-menu, .context-menu-item, .context-menu-separator, .context-menu-label

/* Touch gestures */
.touch-long-press, .pinch-zooming, .swipe-container, .swipe-actions
```

---

## Phase 3: User Flows

**Goal**: Four core flows completable in ≤3 clicks.
**Reference**: `plans/web-refactor/user-flows.md`

### Flow 1: Create Agent (`src/components/creation/`)

Build a wizard for agent creation:

```
ArchetypePalette → EigenvectorSliders → AgentPreview → Create
```

**Components to Build**:
- `AgentCreationWizard.tsx` — Modal with step navigation (simple/custom/advanced modes)
- `ArchetypePalette.tsx` — Visual cards for Scout 🔍 / Sage 🧙 / Spark ✨ / Steady ⚓ / Sync 🔗
- `EigenvectorSliders.tsx` — 7D slider controls (warmth, curiosity, trust, creativity, patience, resilience, ambition)
- `AgentPreview.tsx` — Live preview of config (name, archetype, eigenvectors)
- `AdvancedEditor.tsx` — JSON/YAML textarea for power users

**API Integration**: `POST /v1/town/{town_id}/citizen`

**Consumer flow** (3 clicks): New Agent → Select Archetype → Create
**Prosumer flow** (4 clicks): New Agent → Select Archetype → Adjust Sliders → Create
**Professional flow**: Advanced mode with full JSON editing

### Flow 2: Chat/Inhabit (`src/components/chat/`)

Enable direct agent interaction:

```
Select Agent → Open Chat → Send Message → See Response + Inner Voice
```

**Components to Build**:
- `ChatDrawer.tsx` — Slide-in panel (from right), resize-aware
- `ChatMessage.tsx` — Bubble with avatar, inner voice toggle, alignment indicator
- `MultiAgentChat.tsx` — Multiple agent participants with moderator injection
- `ChatInput.tsx` — Message input with send button, keyboard shortcuts

**API Integration**: Wire to existing INHABIT API (`/v1/town/{town_id}/inhabit/{citizen_id}`)

**Inner Voice Feature**: Toggle to show agent's internal monologue alongside responses

### Flow 3: Agent Details (Enhance `CitizenPanel`)

Deep dive into agent state:

```
Click Agent → See Overview → Navigate Tabs → Export
```

**Components to Build**:
- `AgentDetails.tsx` — Tabbed container (compact/expanded/full modes)
- `OverviewTab.tsx` — Phase, mood, activity sparkline
- `MetricsTab.tsx` — Charts for activity history, eigenvector drift
- `RelationshipsTab.tsx` — Relationship graph with other citizens
- `StateTab.tsx` — Full polynomial state, memory contents
- `HistoryTab.tsx` — Trace timeline
- `ExportButton.tsx` — Download state as JSON

**Detail Levels**:
- **Compact**: Hover card with phase + sparkline
- **Expanded**: Sidebar with eigenvector bars + tabs
- **Full**: Modal with full-width charts + JSON viewer

### Flow 4: Orchestrate (`src/components/orchestration/`)

Pipeline building flow:

```
Enter Build Mode → Drag Agents → Connect Ports → Execute
```

**Components to Build**:
- `OrchestrationCanvas.tsx` — Full-screen `PipelineCanvas` wrapper
- `ExecutionMonitor.tsx` — Live status during pipeline run
- `PipelineTemplates.tsx` — Pre-built templates:
  - **Exploration**: Scout >> Sage
  - **Build**: Sage >> Spark >> Steady
  - **Full Cycle**: Scout >> Sage >> Spark >> Steady >> Sync
  - **Parallel Research**: Scout // Scout >> Sage

**API Integration**: `POST /v1/town/{town_id}/pipeline`

---

## Implementation Strategy

Recommended order (complexity gradient):

1. **Flow 3: Agent Details** — Enhances existing CitizenPanel, lowest risk
2. **Flow 1: Create Agent** — Modal wizard, isolated component
3. **Flow 2: Chat** — Requires SSE/WebSocket for real-time
4. **Flow 4: Orchestrate** — Most complex, builds on Phase 2 pipeline work

---

## Key Patterns to Follow

1. **Use Elastic primitives**: Wrap in `ElasticContainer`, cards in `ElasticCard`
2. **Graceful loading**: `ElasticPlaceholder` for all async states
3. **Keyboard accessible**: Register shortcuts via `useKeyboardShortcuts`
4. **Touch-friendly**: Use `useTouchGestures` for mobile interactions
5. **Context menus**: Use `useContextMenu` from pipeline components
6. **Historical awareness**: Respect `.historical-mode` class (disable mutations)

---

## Quick Start

```bash
cd impl/claude/web

# Development
npm run dev

# Type check as you go
npm run typecheck

# Full validation before commit
npm run validate
```

---

## Success Criteria

| Flow | Target | Measurement |
|------|--------|-------------|
| Create Agent | ≤3 clicks | Archetype → name → create |
| Chat | ≤2 clicks | Select agent → send message |
| Details | ≤2 clicks | Click agent → see tabs |
| Orchestrate | ≤4 clicks | Build mode → drag → connect → execute |

---

## Files to Create

```
src/components/creation/
├── index.ts
├── AgentCreationWizard.tsx
├── ArchetypePalette.tsx
├── EigenvectorSliders.tsx
├── AgentPreview.tsx
└── AdvancedEditor.tsx

src/components/chat/
├── index.ts
├── ChatDrawer.tsx
├── ChatMessage.tsx
├── MultiAgentChat.tsx
└── ChatInput.tsx

src/components/details/
├── index.ts
├── AgentDetails.tsx
├── OverviewTab.tsx
├── MetricsTab.tsx
├── RelationshipsTab.tsx
├── StateTab.tsx
├── HistoryTab.tsx
└── ExportButton.tsx

src/components/orchestration/
├── index.ts
├── OrchestrationCanvas.tsx
├── ExecutionMonitor.tsx
└── PipelineTemplates.tsx
```

---

## Exit Criteria for Phase 3

- [ ] All 4 flows work end-to-end
- [ ] Type check passes (`npm run typecheck`)
- [ ] No console errors in dev mode
- [ ] Mobile-responsive (all flows work at 640px width)
- [ ] Keyboard navigable (Tab through all interactive elements)

Upon completion, generate prompt for **Phase 4: Performance**.

---

*"Three clicks from thought to action."*
