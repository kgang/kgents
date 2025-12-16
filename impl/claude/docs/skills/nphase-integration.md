# N-Phase Integration Guide

This guide covers integrating N-Phase development cycle tracking into kgents applications.

## Overview

N-Phase provides a structured development cycle: **UNDERSTAND → ACT → REFLECT**

| Phase | Purpose | Town Mapping |
|-------|---------|--------------|
| UNDERSTAND | Gather context, analyze situation | MORNING, AFTERNOON |
| ACT | Execute actions, make changes | EVENING |
| REFLECT | Review outcomes, learn from results | NIGHT |

## Backend API

### Enabling N-Phase in Live Stream

Pass `nphase_enabled=true` to the town live endpoint:

```
GET /v1/town/{id}/live?speed=1.0&phases=4&nphase_enabled=true
```

### SSE Events

When N-Phase is enabled, the stream emits additional events:

#### `live.start`
```json
{
  "town_id": "abc123",
  "phases": 4,
  "speed": 1.0,
  "nphase_enabled": true,
  "nphase": {
    "session_id": "nphase-xyz",
    "current_phase": "UNDERSTAND",
    "cycle_count": 1,
    "checkpoint_count": 0,
    "handle_count": 0
  }
}
```

#### `live.nphase` (phase transitions)
```json
{
  "tick": 15,
  "from_phase": "UNDERSTAND",
  "to_phase": "ACT",
  "session_id": "nphase-xyz",
  "cycle_count": 1,
  "trigger": "town_phase:EVENING"
}
```

#### `live.state` (includes N-Phase context)
```json
{
  "colony_id": "town",
  "citizens": [...],
  "nphase": {
    "session_id": "nphase-xyz",
    "current_phase": "ACT",
    "cycle_count": 1,
    "checkpoint_count": 1,
    "handle_count": 3
  }
}
```

#### `live.end`
```json
{
  "town_id": "abc123",
  "total_ticks": 40,
  "status": "completed",
  "nphase_summary": {
    "session_id": "nphase-xyz",
    "final_phase": "REFLECT",
    "cycle_count": 1,
    "checkpoint_count": 2,
    "handle_count": 5,
    "ledger_entries": 12
  }
}
```

## Frontend Integration

### TypeScript Types

Import from `@/api/types`:

```typescript
import type {
  NPhaseType,
  NPhaseContext,
  NPhaseTransitionEvent,
  NPhaseState,
  NPhaseSummary,
} from '@/api/types';

import { NPHASE_CONFIG } from '@/api/types';
```

### React Hook: useNPhaseStream

Standalone hook for N-Phase SSE consumption:

```typescript
import { useNPhaseStream } from '@/hooks/useNPhaseStream';

function MyComponent() {
  const { nphase, transitions, isConnected, connect, disconnect } = useNPhaseStream({
    townId: 'abc123',
    enabled: true,
    speed: 1.0,
    phases: 4,
    autoConnect: true,
    onTransition: (transition) => {
      console.log(`Phase changed: ${transition.from_phase} → ${transition.to_phase}`);
    },
  });

  return (
    <div>
      <p>Current Phase: {nphase.currentPhase}</p>
      <p>Cycle: {nphase.cycleCount}</p>
      <p>Transitions: {transitions.length}</p>
    </div>
  );
}
```

### Hook: useTownStreamWidget

The main town stream hook now supports N-Phase:

```typescript
import { useTownStreamWidget } from '@/hooks/useTownStreamWidget';

const { dashboard, events } = useTownStreamWidget({
  townId: 'abc123',
  nphaseEnabled: true,  // New option
  speed: 1.0,
  phases: 4,
});

// N-Phase context is embedded in dashboard.nphase
```

### Components

#### PhaseIndicator

Full phase indicator with metrics:

```tsx
import { PhaseIndicator } from '@/components/town/PhaseIndicator';

<PhaseIndicator
  nphase={nphase}
  mode="full"    // 'full' | 'compact'
  animate={true}
/>
```

#### PhaseIndicatorCompact

Minimal indicator for headers:

```tsx
import { PhaseIndicatorCompact } from '@/components/town/PhaseIndicator';

<PhaseIndicatorCompact nphase={nphase} />
```

#### PhaseTimeline

Timeline visualization of transitions:

```tsx
import { PhaseTimeline } from '@/components/town/PhaseTimeline';

<PhaseTimeline
  nphase={nphase}
  currentTick={currentTick}
  height={100}
  onTransitionClick={(t) => console.log('Clicked:', t)}
/>
```

#### PhaseTimelineMini

Compact progress bar:

```tsx
import { PhaseTimelineMini } from '@/components/town/PhaseTimeline';

<PhaseTimelineMini nphase={nphase} />
```

## Visual Configuration

N-Phase colors and icons are defined in `NPHASE_CONFIG`:

```typescript
const NPHASE_CONFIG = {
  colors: {
    UNDERSTAND: '#3b82f6', // blue
    ACT: '#f59e0b',        // amber
    REFLECT: '#8b5cf6',    // purple
  },
  icons: {
    UNDERSTAND: '🔍',
    ACT: '⚡',
    REFLECT: '💭',
  },
  descriptions: {
    UNDERSTAND: 'Gathering context and analyzing the situation',
    ACT: 'Executing actions and making changes',
    REFLECT: 'Reviewing outcomes and learning',
  },
  townPhaseMapping: {
    MORNING: 'UNDERSTAND',
    AFTERNOON: 'UNDERSTAND',
    EVENING: 'ACT',
    NIGHT: 'REFLECT',
  },
};
```

## Phase Mapping Rules

Town phases map to N-Phase as follows:

| Town Phase | N-Phase | Rationale |
|------------|---------|-----------|
| MORNING | UNDERSTAND | Citizens wake, gather information |
| AFTERNOON | UNDERSTAND | Citizens continue learning/planning |
| EVENING | ACT | Citizens trade, collaborate, execute |
| NIGHT | REFLECT | Citizens rest, journal, process |

## Testing

### Unit Tests

```typescript
import { renderHook, act } from '@testing-library/react';
import { useNPhaseStream } from '@/hooks/useNPhaseStream';

test('should track phase transitions', async () => {
  const { result } = renderHook(() => useNPhaseStream({
    townId: 'test',
    enabled: true,
  }));

  // Initial state
  expect(result.current.nphase.currentPhase).toBe('UNDERSTAND');
});
```

### E2E Tests

```bash
cd impl/claude/web
npx playwright test nphase-integration
```

## Troubleshooting

### N-Phase not updating

1. Verify `nphase_enabled=true` in SSE URL
2. Check browser console for SSE connection status
3. Ensure backend is emitting `live.nphase` events

### Phase indicator not visible

1. Check `nphaseEnabled` state is true
2. Verify `nphase.enabled` is true in state
3. Check for CSS conflicts with visibility classes

### Transitions not appearing in timeline

1. Ensure at least one phase transition has occurred
2. Verify `transitions` array is populated
3. Check timeline height is sufficient (min 100px)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Town Page                             │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│ │ useTown     │  │ useNPhase   │  │                 │   │
│ │ StreamWidget│  │ Stream      │  │   Components    │   │
│ └──────┬──────┘  └──────┬──────┘  │                 │   │
│        │                │         │ PhaseIndicator  │   │
│        └───────┬────────┘         │ PhaseTimeline   │   │
│                │                  │                 │   │
│         nphase state              └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                Backend SSE Stream                        │
│                                                          │
│  /v1/town/{id}/live?nphase_enabled=true                 │
│                                                          │
│  Events: live.start, live.nphase, live.state, live.end  │
└─────────────────────────────────────────────────────────┘
```

## Related Files

| File | Purpose |
|------|---------|
| `api/types.ts` | N-Phase TypeScript types |
| `hooks/useNPhaseStream.ts` | SSE consumption hook |
| `hooks/useTownStreamWidget.ts` | Main town stream (w/ N-Phase) |
| `components/town/PhaseIndicator.tsx` | Phase status display |
| `components/town/PhaseTimeline.tsx` | Transition timeline |
| `protocols/nphase/session.py` | Backend session state |
| `protocols/api/town.py` | SSE endpoint with N-Phase |
