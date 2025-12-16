# Web Refactor Phase 4 Continuation Prompt

> Use with `/hydrate` to continue Phase 4 (Performance) of the webapp refactor.

## Context from Previous Sessions

**Phase 1 (Elastic Primitives)**: **COMPLETE**
**Phase 2 (Interaction Patterns)**: **COMPLETE**
**Phase 3 (User Flows)**: **COMPLETE**

### What Was Built in Phase 3

All four user flows are now implemented with TypeScript compilation passing:

```
src/components/creation/           # Flow 1: Create Agent
├── index.ts
├── AgentCreationWizard.tsx        # Modal wizard (simple/custom/advanced)
├── ArchetypePalette.tsx           # Visual archetype cards
├── EigenvectorSliders.tsx         # 7D slider controls with presets
├── AgentPreview.tsx               # Live preview before creation
└── AdvancedEditor.tsx             # JSON/YAML editor for power users

src/components/chat/               # Flow 2: Chat/Inhabit
├── index.ts
├── ChatDrawer.tsx                 # Slide-in panel for INHABIT mode
├── ChatMessage.tsx                # Message bubbles with inner voice
├── ChatInput.tsx                  # Input with suggest/force/apologize
└── MultiAgentChat.tsx             # Group conversations

src/components/details/            # Flow 3: Agent Details
├── index.ts
├── AgentDetails.tsx               # Tabbed container (compact/expanded/full)
├── OverviewTab.tsx                # Phase, mood, sparkline
├── MetricsTab.tsx                 # Charts, eigenvector radar
├── RelationshipsTab.tsx           # List/graph relationship views
├── StateTab.tsx                   # Tree/JSON/table state views
├── HistoryTab.tsx                 # Event timeline with filtering
└── ExportButton.tsx               # Export to JSON/YAML/CSV

src/components/orchestration/      # Flow 4: Orchestration
├── index.ts
├── OrchestrationCanvas.tsx        # Full-screen pipeline builder
├── ExecutionMonitor.tsx           # Live execution status display
└── PipelineTemplates.tsx          # Pre-built pipeline templates
```

### Available Infrastructure from Phases 1-2

```
src/components/elastic/            # Elastic primitives
├── ElasticContainer.tsx           # Self-arranging container
├── ElasticCard.tsx                # Priority-aware card with drag
├── ElasticPlaceholder.tsx         # Loading/empty/error states
└── ElasticSplit.tsx               # Two-pane responsive layout

src/components/dnd/                # Drag and drop
├── DndProvider.tsx                # App-level DnD context
├── DraggableAgent.tsx             # Draggable citizen card
├── PipelineSlot.tsx               # Drop zone with validation
└── DragPreview.tsx                # Visual drag feedback

src/components/pipeline/           # Pipeline building
├── usePipeline.ts                 # State management with undo/redo
├── PipelineCanvas.tsx             # SVG canvas with pan/zoom/grid
├── PipelineNode.tsx               # Node with input/output ports
├── PipelineEdge.tsx               # Bezier curves with arrowheads
└── ContextMenu.tsx                # Right-click menus

src/hooks/
├── useLayoutContext.ts            # Layout measurement
├── useHistoricalMode.ts           # Live/historical switching
├── useKeyboardShortcuts.ts        # Global shortcuts
└── useTouchGestures.ts            # Pinch-zoom, long-press, swipe
```

---

## Phase 4: Performance Optimization

**Goal**: Meet all performance targets for production readiness.
**Reference**: `plans/web-refactor/performance.md`

### Performance Targets

| Metric | Target | Current Estimate | Priority |
|--------|--------|------------------|----------|
| **First Contentful Paint** | <1.5s | ~2.5s | High |
| **Largest Contentful Paint** | <2.5s | ~3.5s | High |
| **Time to Interactive** | <3.0s | ~4.0s | High |
| **SSE Event Processing** | <10ms/event | ~15ms | Medium |
| **Widget Render** | <16ms | ~8ms | Low (already good) |
| **Bundle Size (gzipped)** | <300KB | ~450KB | High |
| **Memory (100 citizens)** | <50MB | ~80MB | Medium |

---

## Implementation Tasks

### Task 1: Bundle Analysis & Baseline

Before optimizing, establish baselines:

```bash
# Install bundle analyzer
npm install -D rollup-plugin-visualizer

# Add to vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

// In plugins array:
visualizer({
  filename: 'dist/bundle-stats.html',
  open: true,
  gzipSize: true,
})
```

**Deliverables**:
- Bundle visualization screenshot
- Lighthouse audit results (save as JSON)
- Identified top 5 largest dependencies

### Task 2: Route-Based Code Splitting

Implement lazy loading for all page routes:

```typescript
// App.tsx
import { lazy, Suspense } from 'react';

const Town = lazy(() => import('./pages/Town'));
const Workshop = lazy(() => import('./pages/Workshop'));
const Inhabit = lazy(() => import('./pages/Inhabit'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

// PageLoader component for Suspense fallback
function PageLoader() {
  return (
    <div className="h-screen flex items-center justify-center bg-town-bg">
      <div className="animate-pulse text-4xl">🏘️</div>
      <span className="ml-3 text-gray-400">Loading...</span>
    </div>
  );
}
```

**Files to Modify**:
- `src/App.tsx` — Add lazy imports and Suspense boundaries
- `src/pages/*.tsx` — Ensure they're default exports

### Task 3: Component-Level Code Splitting

Split heavy components loaded on demand:

```typescript
// Heavy components to lazy load
const PipelineCanvas = lazy(() => import('@/components/pipeline/PipelineCanvas'));
const OrchestrationCanvas = lazy(() => import('@/components/orchestration/OrchestrationCanvas'));
const MetricsTab = lazy(() => import('@/components/details/MetricsTab'));
const AdvancedEditor = lazy(() => import('@/components/creation/AdvancedEditor'));
const MultiAgentChat = lazy(() => import('@/components/chat/MultiAgentChat'));
```

**Usage Pattern**:
```typescript
{showPipeline && (
  <Suspense fallback={<ElasticPlaceholder for="chart" state="loading" />}>
    <PipelineCanvas {...props} />
  </Suspense>
)}
```

### Task 4: Virtualization for Large Lists

Install and implement virtualization:

```bash
npm install @tanstack/react-virtual
```

**Files to Create/Modify**:
- `src/components/town/VirtualizedCitizenList.tsx` — New virtualized list component
- `src/components/town/Mesa.tsx` — Add viewport-based citizen filtering

**VirtualizedCitizenList Implementation**:
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualizedCitizenList({ citizens }: { citizens: CitizenCardJSON[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: citizens.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120,
    overscan: 5,
  });

  return (
    <div ref={parentRef} className="h-full overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <CitizenCard {...citizens[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Task 5: Widget Memoization Audit

Audit all widget components and add React.memo where appropriate:

**Files to Audit**:
```
src/widgets/cards/CitizenCard.tsx
src/widgets/cards/EigenvectorDisplay.tsx
src/widgets/primitives/Bar.tsx
src/widgets/primitives/Sparkline.tsx
src/widgets/dashboards/ColonyDashboard.tsx
src/components/details/*Tab.tsx (all tabs)
```

**Pattern**:
```typescript
export const CitizenCard = memo(function CitizenCard(props: CitizenCardProps) {
  // ... render
});

// For complex props, add custom comparison
export const ColonyDashboard = memo(
  function ColonyDashboard(props: ColonyDashboardProps) {
    // ... render
  },
  (prev, next) => {
    return (
      prev.colony_id === next.colony_id &&
      prev.phase === next.phase &&
      prev.citizens.length === next.citizens.length
    );
  }
);
```

### Task 6: SSE Event Batching

Implement event batching to reduce render frequency:

**File to Create**: `src/hooks/useBatchedEvents.ts`

```typescript
export function useBatchedEvents<T>(
  onBatch: (events: T[]) => void,
  delay = 50
) {
  const batchRef = useRef<T[]>([]);
  const timeoutRef = useRef<number>();

  const addEvent = useCallback((event: T) => {
    batchRef.current.push(event);

    if (!timeoutRef.current) {
      timeoutRef.current = window.setTimeout(() => {
        onBatch(batchRef.current);
        batchRef.current = [];
        timeoutRef.current = undefined;
      }, delay);
    }
  }, [onBatch, delay]);

  return addEvent;
}
```

**Integrate with**: `src/hooks/useTownStreamWidget.ts`

### Task 7: Performance Monitoring Setup

Add Core Web Vitals tracking:

**File to Create**: `src/lib/reportWebVitals.ts`

```typescript
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals';

export function reportWebVitals(onPerfEntry?: (metric: any) => void) {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    onCLS(onPerfEntry);
    onFID(onPerfEntry);
    onLCP(onPerfEntry);
    onFCP(onPerfEntry);
    onTTFB(onPerfEntry);
  }
}
```

**Install**: `npm install web-vitals`

---

## Implementation Strategy

Recommended order (impact vs. effort):

1. **Bundle Analysis** — Understand current state (1 hour)
2. **Route Code Splitting** — Biggest bundle impact (2 hours)
3. **Component Splitting** — Further bundle reduction (2 hours)
4. **Memoization Audit** — Render performance (3 hours)
5. **Virtualization** — Memory/render for large towns (4 hours)
6. **SSE Batching** — Event processing optimization (2 hours)
7. **Web Vitals Monitoring** — Ongoing measurement (1 hour)

---

## Key Files to Reference

```
plans/web-refactor/performance.md      # Detailed performance plan
src/hooks/useTownStreamWidget.ts       # SSE streaming hook
src/reactive/WidgetRenderer.tsx        # Widget dispatch
src/widgets/*                          # Widget components to memoize
src/pages/Town.tsx                     # Main page to optimize
```

---

## Validation Commands

```bash
# Type check
npm run typecheck

# Build and analyze bundle
npm run build
# Open dist/bundle-stats.html

# Run tests
npm run test -- --run

# Lighthouse audit (requires serve)
npm install -g serve
serve -s dist
# Then run Lighthouse in Chrome DevTools
```

---

## Success Criteria

- [ ] Bundle size reduced to <300KB gzipped
- [ ] All routes lazy-loaded with Suspense
- [ ] Heavy components (Pipeline, Metrics, AdvancedEditor) split
- [ ] All widget components memoized
- [ ] Virtualization working for 100+ citizens
- [ ] SSE batching reduces renders by 50%+
- [ ] Web Vitals: FCP <1.5s, LCP <2.5s, TTI <3.0s
- [ ] TypeScript compilation passes
- [ ] All tests pass

---

## Exit Criteria for Phase 4

Upon completion:
- [ ] All performance targets met
- [ ] Bundle analysis saved to `docs/performance-baseline.md`
- [ ] Lighthouse scores: Performance >90
- [ ] No console errors in production build

Generate prompt for **Phase 5: Polish & Delight** upon completion.

---

*"Render sub-millisecond: measure before optimizing."*
