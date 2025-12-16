---
path: plans/web-refactor/performance
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: []
parent: plans/web-refactor/webapp-refactor-master
requires: []
session_notes: |
  Performance is parallel work—can proceed independently of feature development.
  Targets are aggressive but achievable with current React patterns.
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.0
---

# Performance Optimization

> *"Render sub-millisecond: measure before optimizing."*

## Performance Targets

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

## Bundle Analysis

### Current Bundle Composition (Estimated)

```
Total: ~450KB gzipped

├── React + ReactDOM:     ~45KB (10%)
├── React Router:         ~15KB (3%)
├── Zustand + Immer:      ~10KB (2%)
├── Axios:                ~15KB (3%)
├── DnD Kit (future):     ~20KB (4%)
├── Tailwind (CSS):       ~30KB (7%)
├── Application Code:     ~100KB (22%)
├── Third-party UI:       ~50KB (11%)
└── Other dependencies:   ~165KB (37%)
```

### Reduction Strategies

1. **Code Splitting**: Route-based lazy loading
2. **Tree Shaking**: Verify unused exports are eliminated
3. **Dependency Audit**: Replace heavy dependencies
4. **CSS Purge**: Ensure Tailwind purges unused classes

---

## Code Splitting Strategy

### Route-Based Splitting

```typescript
// App.tsx
import { lazy, Suspense } from 'react';

// Lazy load pages
const Town = lazy(() => import('./pages/Town'));
const Workshop = lazy(() => import('./pages/Workshop'));
const Inhabit = lazy(() => import('./pages/Inhabit'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

// Loading fallback
function PageLoader() {
  return (
    <div className="h-screen flex items-center justify-center">
      <div className="animate-pulse text-4xl">🏘️</div>
    </div>
  );
}

// Routes with Suspense
<Routes>
  <Route path="/town/:townId" element={
    <Suspense fallback={<PageLoader />}>
      <Town />
    </Suspense>
  } />
  {/* ... other routes */}
</Routes>
```

### Component-Based Splitting

Heavy components loaded on demand:

```typescript
// Heavy components
const PipelineCanvas = lazy(() => import('./components/PipelineCanvas'));
const MetricsChart = lazy(() => import('./components/MetricsChart'));
const AdvancedEditor = lazy(() => import('./components/AdvancedEditor'));

// Usage
{showPipeline && (
  <Suspense fallback={<ElasticPlaceholder for="chart" state="loading" />}>
    <PipelineCanvas {...props} />
  </Suspense>
)}
```

---

## Virtualization

### Problem

Town with 100+ citizens renders all cards, causing:
- Slow initial render
- High memory usage
- Janky scrolling

### Solution: Virtual List

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualizedCitizenList({ citizens }: { citizens: CitizenCardJSON[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: citizens.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120, // Estimated card height
    overscan: 5,
  });

  return (
    <div ref={parentRef} className="h-full overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
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

### Mesa Virtualization

For 2D canvas (Mesa), use spatial partitioning:

```typescript
function VirtualizedMesa({ citizens, viewport }: Props) {
  // Only render citizens visible in viewport + margin
  const visibleCitizens = useMemo(() => {
    const margin = 100; // Render 100px outside viewport
    return citizens.filter(citizen => {
      const pos = citizenToPosition(citizen);
      return (
        pos.x >= viewport.x - margin &&
        pos.x <= viewport.x + viewport.width + margin &&
        pos.y >= viewport.y - margin &&
        pos.y <= viewport.y + viewport.height + margin
      );
    });
  }, [citizens, viewport]);

  return (
    <svg>
      {visibleCitizens.map(citizen => (
        <CitizenNode key={citizen.citizen_id} citizen={citizen} />
      ))}
    </svg>
  );
}
```

---

## Memoization Strategy

### When to Memoize

| Component | Memoize? | Reason |
|-----------|----------|--------|
| Pure display widget | Yes | Props change rarely |
| List item | Yes | Parent re-renders often |
| Event handler | Depends | Use useCallback if passed down |
| Computed value | Yes | Use useMemo for expensive calculations |
| Form input | No | Changes frequently |

### Widget Memoization

```typescript
// All widgets should be memoized
export const CitizenCard = memo(function CitizenCard(props: CitizenCardProps) {
  // ...render
});

// Custom comparison for complex props
export const ColonyDashboard = memo(
  function ColonyDashboard(props: ColonyDashboardProps) {
    // ...render
  },
  (prev, next) => {
    // Only re-render if these change
    return (
      prev.colony_id === next.colony_id &&
      prev.phase === next.phase &&
      prev.citizens.length === next.citizens.length &&
      prev.selected_citizen_id === next.selected_citizen_id
    );
  }
);
```

### SSE Handler Memoization

Prevent stale closures:

```typescript
function useTownStream() {
  const [events, setEvents] = useState<TownEvent[]>([]);

  // Store handlers in ref to avoid stale closures
  const handlersRef = useRef({ setEvents });
  handlersRef.current = { setEvents };

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.addEventListener('event', (e) => {
      // Use ref to get fresh handler
      handlersRef.current.setEvents(prev => [JSON.parse(e.data), ...prev]);
    });

    return () => eventSource.close();
  }, [url]); // Only recreate when URL changes
}
```

---

## SSE Optimization

### Current Issues

1. Each event triggers full dashboard re-render
2. No batching of rapid events
3. Parsing happens synchronously

### Solutions

**1. Event Batching**

```typescript
function useBatchedEvents(onBatch: (events: TownEvent[]) => void, delay = 50) {
  const batchRef = useRef<TownEvent[]>([]);
  const timeoutRef = useRef<number>();

  const addEvent = useCallback((event: TownEvent) => {
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

**2. Web Worker Parsing**

```typescript
// sse-worker.ts
self.onmessage = (e: MessageEvent<string>) => {
  const parsed = JSON.parse(e.data);
  self.postMessage(parsed);
};

// Hook
const worker = useMemo(() => new Worker('./sse-worker.ts'), []);

useEffect(() => {
  worker.onmessage = (e) => {
    addEvent(e.data);
  };
}, [worker, addEvent]);

// In SSE handler
eventSource.addEventListener('event', (e) => {
  worker.postMessage(e.data); // Offload parsing
});
```

**3. Differential Updates**

Instead of replacing entire dashboard, apply patches:

```typescript
interface DashboardPatch {
  type: 'citizen_update' | 'phase_change' | 'metrics_update';
  payload: unknown;
}

function applyPatch(dashboard: ColonyDashboardJSON, patch: DashboardPatch) {
  switch (patch.type) {
    case 'citizen_update':
      return {
        ...dashboard,
        citizens: dashboard.citizens.map(c =>
          c.citizen_id === patch.payload.id
            ? { ...c, ...patch.payload.changes }
            : c
        ),
      };
    // ... other cases
  }
}
```

---

## Asset Optimization

### Images

- Use WebP format with PNG fallback
- Implement responsive images (`srcset`)
- Lazy load below-fold images

### Fonts

- Use `font-display: swap` to prevent FOIT
- Subset fonts to used characters only
- Preload critical fonts

### CSS

```css
/* Ensure Tailwind purges unused classes in production */
/* tailwind.config.js */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  // ...
};
```

---

## Monitoring & Profiling

### Core Web Vitals Tracking

```typescript
// reportWebVitals.ts
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals';

export function reportWebVitals() {
  onCLS(console.log);
  onFID(console.log);
  onLCP(console.log);
  onFCP(console.log);
  onTTFB(console.log);
}
```

### Performance Marks

```typescript
// Measure critical paths
performance.mark('town-stream-start');
// ... stream processing
performance.mark('town-stream-end');
performance.measure('town-stream', 'town-stream-start', 'town-stream-end');
```

---

## Implementation Tasks

### Phase 1: Analysis
- [ ] Run Lighthouse audit
- [ ] Analyze bundle with `vite-bundle-visualizer`
- [ ] Profile SSE event handling
- [ ] Measure render times for key components

### Phase 2: Code Splitting
- [ ] Add lazy loading to routes
- [ ] Split heavy components
- [ ] Verify tree shaking works
- [ ] Add loading states

### Phase 3: Virtualization
- [ ] Install @tanstack/react-virtual
- [ ] Virtualize citizen list
- [ ] Implement viewport-based Mesa rendering
- [ ] Test with 200+ citizens

### Phase 4: Memoization
- [ ] Audit all widget components
- [ ] Add React.memo where appropriate
- [ ] Fix stale closure issues in hooks
- [ ] Add custom comparison functions

### Phase 5: SSE Optimization
- [ ] Implement event batching
- [ ] Consider Web Worker for parsing
- [ ] Implement differential updates
- [ ] Test under high event rate

### Phase 6: Assets
- [ ] Convert images to WebP
- [ ] Optimize font loading
- [ ] Verify CSS purging
- [ ] Add preload hints

---

## Success Metrics

| Metric | Method | Frequency |
|--------|--------|-----------|
| FCP | Lighthouse | PR checks |
| LCP | Lighthouse | PR checks |
| Bundle size | CI check | Every build |
| Widget render time | React Profiler | Dev testing |
| SSE processing time | Performance API | Dev testing |
| Memory usage | Chrome DevTools | Manual |

---

*"Render sub-millisecond: 0.03ms p50 for 25-citizen scatter—measure before optimizing."*
