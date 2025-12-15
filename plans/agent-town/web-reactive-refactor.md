# Web Reactive Refactor Plan

## Metadata

```yaml
plan_id: web-reactive-refactor
status: APPROVED
priority: HIGH
effort: 4
risk: MEDIUM
spec: spec/protocols/web-reactive.md
last_touched: 2025-12-15
```

## Overview

Refactor the Agent Town web frontend to build upon and re-utilize the reactive substrate and generative UI framework, eliminating duplicate state management and enabling "define once, render anywhere" for web targets.

## Current State Analysis

### What Exists

**Reactive Substrate (`impl/claude/agents/i/reactive/`)**:
- `Signal[T]`, `Computed[T]`, `Effect` - Core reactive primitives
- `KgentsWidget[S]` - Base widget class with `project()` method
- `HStack`/`VStack` - Composition containers via `>>` and `//`
- 9 widget primitives: Glyph, Bar, Sparkline, DensityField, AgentCard, YieldCard, ShadowCard, DialecticCard, CitizenCard
- `ColonyDashboard` - Full town visualization widget
- Adapters for CLI, TUI (Textual), marimo, JSON
- 559+ tests proving category laws

**Web Frontend (`impl/claude/web/`)**:
- React + Zustand state management (separate from reactive substrate)
- PixiJS-based Mesa canvas for town visualization
- SSE streaming via `useTownStream` hook
- Components: `Town.tsx`, `CitizenPanel.tsx`, `DemoPreview.tsx`, `Mesa.tsx`
- In-flight test infrastructure improvements (vitest)

### The Gap

| Aspect | Current | Target |
|--------|---------|--------|
| State management | Zustand stores | Signal bridges |
| Widget rendering | Custom React components | JSON projection consumers |
| Composition | Manual JSX | HStack/VStack from substrate |
| Type safety | Manual interfaces | Generated from Python |
| Laws verification | None | CategoryLawVerifier integration |

---

## Implementation Phases

### Phase 1: Foundation (Effort: 1)

**Goal**: Establish the bridge infrastructure without changing existing behavior.

#### 1.1 Create Reactive Bridge Module

```
impl/claude/web/src/reactive/
├── index.ts            # Re-exports
├── types.ts            # WidgetJSON union type
├── useWidgetState.ts   # Hook for JSON projection state
├── WidgetRenderer.tsx  # Dynamic widget renderer
└── context.tsx         # Theme/interaction context
```

**File: `types.ts`**

```typescript
// Core widget types derived from Python dataclasses
export interface GlyphJSON {
  type: 'glyph';
  char: string;
  phase: string;
  animation: string;
}

export interface BarJSON {
  type: 'bar';
  value: number;
  label: string;
  width: number;
}

export interface CitizenCardJSON {
  type: 'citizen_card';
  citizen_id: string;
  name: string;
  archetype: string;
  phase: 'IDLE' | 'SOCIALIZING' | 'WORKING' | 'REFLECTING' | 'RESTING';
  nphase: 'SENSE' | 'ACT' | 'REFLECT';
  activity: number[];
  capability: number;
  entropy: number;
  region: string;
  mood: string;
  eigenvectors: {
    warmth: number;
    curiosity: number;
    trust: number;
  };
}

export interface HStackJSON {
  type: 'hstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
}

export interface VStackJSON {
  type: 'vstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
}

export interface ColonyDashboardJSON {
  type: 'colony_dashboard';
  colony_id: string;
  phase: 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';
  day: number;
  metrics: {
    total_events: number;
    total_tokens: number;
    entropy_budget: number;
  };
  citizens: CitizenCardJSON[];
  grid_cols: number;
  selected_citizen_id: string | null;
}

export type WidgetJSON =
  | GlyphJSON
  | BarJSON
  | CitizenCardJSON
  | HStackJSON
  | VStackJSON
  | ColonyDashboardJSON;
```

**File: `useWidgetState.ts`**

```typescript
import { useState, useEffect, useCallback } from 'react';
import type { WidgetJSON } from './types';

interface UseWidgetStateOptions<T extends WidgetJSON> {
  initialState: T;
  onUpdate?: (state: T) => void;
}

export function useWidgetState<T extends WidgetJSON>(
  options: UseWidgetStateOptions<T>
) {
  const [state, setState] = useState<T>(options.initialState);

  const updateState = useCallback((updater: T | ((prev: T) => T)) => {
    setState(prev => {
      const next = typeof updater === 'function' ? updater(prev) : updater;
      options.onUpdate?.(next);
      return next;
    });
  }, [options.onUpdate]);

  return [state, updateState] as const;
}
```

**File: `WidgetRenderer.tsx`**

```typescript
import type { WidgetJSON } from './types';
import { CitizenCard } from '../widgets/CitizenCard';
import { HStack, VStack } from '../widgets/layout';
// ... other imports

interface WidgetRendererProps {
  widget: WidgetJSON;
  onSelect?: (id: string) => void;
}

export function WidgetRenderer({ widget, onSelect }: WidgetRendererProps) {
  switch (widget.type) {
    case 'citizen_card':
      return <CitizenCard {...widget} onSelect={onSelect} />;
    case 'hstack':
      return <HStack {...widget} onSelect={onSelect} />;
    case 'vstack':
      return <VStack {...widget} onSelect={onSelect} />;
    case 'colony_dashboard':
      return <ColonyDashboard {...widget} onSelect={onSelect} />;
    default:
      return <div>Unknown widget type: {(widget as any).type}</div>;
  }
}
```

#### 1.2 Tests

```typescript
// src/reactive/__tests__/WidgetRenderer.test.tsx
describe('WidgetRenderer', () => {
  it('renders citizen card from JSON', () => {
    const json: CitizenCardJSON = {
      type: 'citizen_card',
      citizen_id: 'alice',
      name: 'Alice',
      archetype: 'builder',
      phase: 'WORKING',
      nphase: 'ACT',
      activity: [0.3, 0.5, 0.7],
      capability: 0.85,
      entropy: 0.1,
      region: 'plaza',
      mood: 'focused',
      eigenvectors: { warmth: 0.7, curiosity: 0.8, trust: 0.6 },
    };

    render(<WidgetRenderer widget={json} />);
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('builder')).toBeInTheDocument();
  });

  it('renders nested composition', () => {
    const json: HStackJSON = {
      type: 'hstack',
      gap: 1,
      separator: null,
      children: [
        { type: 'citizen_card', ... },
        { type: 'citizen_card', ... },
      ],
    };

    render(<WidgetRenderer widget={json} />);
    expect(screen.getAllByTestId('citizen-card')).toHaveLength(2);
  });
});
```

---

### Phase 2: Widget Components (Effort: 1.5)

**Goal**: Create React components that consume JSON projections.

#### 2.1 Layout Primitives

```
impl/claude/web/src/widgets/
├── layout/
│   ├── HStack.tsx
│   ├── VStack.tsx
│   └── index.ts
├── CitizenCard.tsx
├── ColonyDashboard.tsx
├── ActivitySparkline.tsx
├── CapabilityBar.tsx
├── EigenvectorDisplay.tsx
└── index.ts
```

**File: `layout/HStack.tsx`**

```typescript
import type { HStackJSON } from '../../reactive/types';
import { WidgetRenderer } from '../../reactive/WidgetRenderer';

interface HStackProps extends Omit<HStackJSON, 'type'> {
  onSelect?: (id: string) => void;
  className?: string;
}

export function HStack({ gap, separator, children, onSelect, className }: HStackProps) {
  return (
    <div
      className={cn('kgents-hstack flex items-center', className)}
      style={{ gap: `${gap * 8}px` }}
    >
      {children.map((child, i) => (
        <Fragment key={i}>
          {i > 0 && separator && <span className="separator">{separator}</span>}
          <WidgetRenderer widget={child} onSelect={onSelect} />
        </Fragment>
      ))}
    </div>
  );
}
```

**File: `CitizenCard.tsx`**

```typescript
import type { CitizenCardJSON } from '../reactive/types';
import { ActivitySparkline } from './ActivitySparkline';
import { CapabilityBar } from './CapabilityBar';

const PHASE_GLYPHS: Record<string, string> = {
  IDLE: '○',
  SOCIALIZING: '◉',
  WORKING: '●',
  REFLECTING: '◐',
  RESTING: '◯',
};

interface CitizenCardProps extends Omit<CitizenCardJSON, 'type'> {
  onSelect?: (id: string) => void;
  isSelected?: boolean;
}

export function CitizenCard({
  citizen_id,
  name,
  archetype,
  phase,
  nphase,
  activity,
  capability,
  mood,
  onSelect,
  isSelected,
}: CitizenCardProps) {
  const glyph = PHASE_GLYPHS[phase] || '?';

  return (
    <div
      data-testid="citizen-card"
      data-citizen-id={citizen_id}
      className={cn(
        'kgents-citizen-card p-3 rounded-lg border transition-colors cursor-pointer',
        isSelected ? 'border-blue-500 bg-blue-500/10' : 'border-gray-200 bg-white hover:border-gray-300'
      )}
      onClick={() => onSelect?.(citizen_id)}
    >
      <div className="header flex items-center gap-2 mb-2">
        <span className="glyph text-xl">{glyph}</span>
        <span className="name font-bold">{name}</span>
        <span className="nphase text-gray-500 text-sm">[{nphase[0]}]</span>
      </div>
      <div className="archetype text-cyan-600 text-sm mb-2">{archetype}</div>
      {activity.length > 0 && <ActivitySparkline values={activity} />}
      <CapabilityBar value={capability} />
      <div className="mood text-gray-500 text-xs mt-2">{mood}</div>
    </div>
  );
}
```

#### 2.2 Composite Dashboard

**File: `ColonyDashboard.tsx`**

```typescript
import type { ColonyDashboardJSON } from '../reactive/types';
import { CitizenCard } from './CitizenCard';
import { HStack, VStack } from './layout';

interface ColonyDashboardProps extends Omit<ColonyDashboardJSON, 'type'> {
  onSelectCitizen?: (id: string) => void;
}

export function ColonyDashboard({
  colony_id,
  phase,
  day,
  metrics,
  citizens,
  grid_cols,
  selected_citizen_id,
  onSelectCitizen,
}: ColonyDashboardProps) {
  // Build grid rows
  const rows: CitizenCardJSON[][] = [];
  for (let i = 0; i < citizens.length; i += grid_cols) {
    rows.push(citizens.slice(i, i + grid_cols));
  }

  return (
    <div className="kgents-colony-dashboard border rounded-lg overflow-hidden" data-colony-id={colony_id}>
      {/* Header */}
      <div className="header flex justify-between items-center px-4 py-3 bg-gray-900 text-white">
        <span className="font-bold">AGENT TOWN DASHBOARD</span>
        <span className="text-gray-400">{phase} · Day {day}</span>
      </div>

      {/* Status bar */}
      <div className="status-bar flex gap-4 px-4 py-2 bg-gray-100 text-sm border-b">
        <span><strong>Colony:</strong> {colony_id.slice(0, 12)}</span>
        <span><strong>Citizens:</strong> {citizens.length}</span>
        <span><strong>Events:</strong> {metrics.total_events}</span>
      </div>

      {/* Citizen grid */}
      <div className="grid-container p-4">
        <VStack gap={1} separator={null} onSelect={onSelectCitizen}>
          {rows.map((row, i) => ({
            type: 'hstack' as const,
            gap: 1,
            separator: null,
            children: row.map(c => ({ ...c, type: 'citizen_card' as const })),
          }))}
        </VStack>
      </div>

      {/* Footer */}
      <div className="footer flex justify-between px-4 py-2 bg-gray-100 text-sm border-t">
        <span>Entropy: {metrics.entropy_budget.toFixed(2)}</span>
        <span>Tokens: {metrics.total_tokens}</span>
      </div>
    </div>
  );
}
```

---

### Phase 3: SSE Integration (Effort: 1)

**Goal**: Modify SSE streaming to emit JSON projections.

#### 3.1 Backend Enhancement

Add `live.state` event type that sends full widget JSON:

```python
# impl/claude/protocols/api/town.py

async def stream_town_events(town_id: str, speed: float = 1.0) -> AsyncGenerator[str, None]:
    """Stream town events as SSE."""
    flux = get_town_flux(town_id)
    dashboard = ColonyDashboard()

    yield sse_event('live.start', {'town_id': town_id})

    async for event in flux.run():
        # Emit individual event
        yield sse_event('live.event', event.to_dict())

        # Emit full state projection every N events or on significant changes
        if should_emit_state(event):
            state = ColonyState.from_flux(flux)
            dashboard_json = ColonyDashboard(state).to_json()
            yield sse_event('live.state', dashboard_json)

    yield sse_event('live.end', {'reason': 'complete'})
```

#### 3.2 Frontend Hook Enhancement

```typescript
// impl/claude/web/src/hooks/useTownStream.ts

export function useTownStream({ townId, speed = 1.0 }: UseTownStreamOptions) {
  const [dashboard, setDashboard] = useState<ColonyDashboardJSON | null>(null);
  const [events, setEvents] = useState<TownEvent[]>([]);

  useEffect(() => {
    if (!townId) return;

    const url = `/v1/town/${townId}/live?speed=${speed}`;
    const eventSource = new EventSource(url);

    // Handle state projection
    eventSource.addEventListener('live.state', (e) => {
      const state: ColonyDashboardJSON = JSON.parse(e.data);
      setDashboard(state);
    });

    // Handle individual events (for event feed)
    eventSource.addEventListener('live.event', (e) => {
      const event: TownEvent = JSON.parse(e.data);
      setEvents(prev => [event, ...prev.slice(0, 99)]);
    });

    return () => eventSource.close();
  }, [townId, speed]);

  return { dashboard, events };
}
```

---

### Phase 4: Migration (Effort: 1)

**Goal**: Migrate existing pages to use new widget components.

#### 4.1 Town Page

```typescript
// impl/claude/web/src/pages/Town.tsx (refactored)

export default function Town() {
  const { townId } = useParams<{ townId: string }>();
  const { dashboard, events } = useTownStream({ townId: townId || '' });
  const [selectedCitizenId, setSelectedCitizenId] = useState<string | null>(null);

  if (!dashboard) {
    return <LoadingState />;
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Town Header - derived from dashboard state */}
      <TownHeader
        phase={dashboard.phase}
        day={dashboard.day}
        citizenCount={dashboard.citizens.length}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Mesa - consumes citizen positions from dashboard */}
        <div className="flex-1 relative">
          <Mesa citizens={dashboard.citizens} selectedId={selectedCitizenId} />
        </div>

        {/* Sidebar - widget-based */}
        <div className="w-80 border-l flex flex-col">
          {selectedCitizenId ? (
            <CitizenPanel
              citizen={dashboard.citizens.find(c => c.citizen_id === selectedCitizenId)}
              onClose={() => setSelectedCitizenId(null)}
            />
          ) : (
            <ColonyDashboard
              {...dashboard}
              onSelectCitizen={setSelectedCitizenId}
            />
          )}

          <EventFeed events={events} />
        </div>
      </div>
    </div>
  );
}
```

#### 4.2 Deprecate Zustand Stores

Mark stores for deprecation but keep for backwards compatibility:

```typescript
// impl/claude/web/src/stores/townStore.ts

/**
 * @deprecated Use useTownStream hook instead.
 * This store will be removed in the next major version.
 */
export const useTownStore = create<TownState>()(...);
```

---

### Phase 5: Cleanup (Effort: 0.5)

**Goal**: Remove deprecated code and finalize.

#### 5.1 Remove Zustand Dependency

```bash
npm uninstall zustand immer
```

#### 5.2 Update Exports

```typescript
// impl/claude/web/src/index.ts
export * from './reactive';
export * from './widgets';
export * from './hooks/useTownStream';
```

#### 5.3 Documentation

Update `impl/claude/web/README.md` with new architecture.

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Type mismatches between Python/TS | Medium | High | Generate TS types from Python dataclasses |
| Performance regression from SSE state | Medium | Medium | Throttle state emissions, use delta updates |
| Breaking existing functionality | Low | High | Feature flags, parallel implementations |
| Mesa canvas incompatibility | Low | Medium | Keep JSON as intermediate format |

---

## Success Criteria

1. **Functional**: Town page renders correctly from JSON projections
2. **Performance**: No perceptible latency increase (<50ms)
3. **Tests**: 90%+ coverage on new reactive bridge code
4. **Types**: Zero `any` types in widget interfaces
5. **Laws**: CategoryLawVerifier passes for composition
6. **Migration**: All Zustand usage replaced

---

## Dependencies

- `spec/protocols/web-reactive.md` - Formal specification
- `spec/protocols/projection.md` - Projection protocol
- `impl/claude/agents/i/reactive/` - Reactive substrate
- `impl/claude/agents/i/reactive/colony_dashboard.py` - ColonyDashboard widget
- `impl/claude/agents/i/reactive/primitives/citizen_card.py` - CitizenWidget

---

## Timeline

This plan does not include time estimates per kgents principles. Phases should be executed sequentially, with each phase completing before the next begins.

---

## Verification Checklist

- [x] Phase 1: Bridge module created with types and renderer
- [x] Phase 1: Unit tests pass for WidgetRenderer (76 tests)
- [ ] Phase 2: Widget components render correctly
- [ ] Phase 2: Composition laws verified
- [ ] Phase 3: SSE emits `live.state` events
- [ ] Phase 3: Frontend consumes projections
- [ ] Phase 4: Town page migrated
- [ ] Phase 4: Feature parity with current implementation
- [ ] Phase 5: Zustand removed
- [ ] Phase 5: Documentation updated

---

*Last updated: 2025-12-15*
