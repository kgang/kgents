# Phase 3: SSE Integration - Continuation Prompt

## Context

**Previous Phases Complete:**
- Phase 1: Foundation (76 tests) - types.ts, useWidgetState.ts, WidgetRenderer.tsx, context.tsx
- Phase 2: Widget Components (109 tests) - /widgets/ directory with primitives/, layout/, cards/, dashboards/

**Goal:** Modify SSE streaming to emit `live.state` events containing full `ColonyDashboardJSON` widget projections, enabling the frontend to render from JSON rather than reconstructing state from individual events.

---

## Current State Analysis

### Backend (`impl/claude/protocols/api/town.py`)

The `/v1/town/{id}/live` endpoint already emits:
- `live.start` - `{"town_id": "...", "phases": 4, "speed": 1.0}`
- `live.event` - Individual TownEvent with tick, phase, operation, participants, dialogue
- `live.phase` - Phase transitions `{"tick": N, "phase": "MORNING"}`
- `live.end` - `{"town_id": "...", "total_ticks": N, "status": "completed"}`

**Missing:** `live.state` event with full `ColonyDashboardJSON`

### Python Widget (`impl/claude/agents/i/reactive/colony_dashboard.py`)

The `ColonyDashboard` widget exists and has a `to_json()` method that returns:
```python
{
    "type": "colony_dashboard",
    "colony_id": str,
    "phase": "MORNING" | "AFTERNOON" | "EVENING" | "NIGHT",
    "day": int,
    "metrics": {"total_events": int, "total_tokens": int, "entropy_budget": float},
    "citizens": [CitizenCardJSON, ...],
    "grid_cols": int,
    "selected_citizen_id": str | None
}
```

### Frontend (`impl/claude/web/src/hooks/useTownStream.ts`)

Currently:
- Uses `useTownStore` (Zustand) to manage state
- Listens for `live.event`, `live.phase`, `live.start`, `live.end`
- Builds UI state incrementally from events
- Does NOT handle `live.state` event

**Target:** Use `ColonyDashboardJSON` from `live.state` to drive rendering

---

## Implementation Tasks

### Task 1: Backend - Add `live.state` Event Emission

**File:** `impl/claude/protocols/api/town.py`

Modify the `stream_live` endpoint to emit `live.state` events:

```python
# In stream_live() generate() function

from agents.i.reactive.colony_dashboard import ColonyDashboard

# After sending live.event, emit full state periodically
if should_emit_state(tick, event):  # Every N events or on significant changes
    dashboard = build_colony_dashboard(env, flux, tick)
    state_json = dashboard.to_json()
    yield f"event: live.state\ndata: {json.dumps(state_json)}\n\n"
```

**Helper functions to add:**

```python
def should_emit_state(tick: int, event: TownEvent) -> bool:
    """Determine if we should emit a full state projection."""
    # Emit every 5 events, or on phase change, or on significant events
    return (
        tick % 5 == 0 or
        event.operation in ('evolve', 'coalition_formed', 'coalition_dissolved')
    )

def build_colony_dashboard(env, flux, tick: int) -> ColonyDashboard:
    """Build ColonyDashboard widget from current environment state."""
    from agents.i.reactive.colony_dashboard import ColonyDashboard
    from agents.i.reactive.primitives.citizen_card import CitizenWidget

    # Convert citizens to CitizenWidget cards
    citizen_cards = []
    for citizen in env.citizens.values():
        card = CitizenWidget.from_citizen(citizen)
        citizen_cards.append(card)

    return ColonyDashboard(
        colony_id=env.name or "town",
        phase=flux.current_phase.name,
        day=flux.day,
        metrics={
            "total_events": tick,
            "total_tokens": env.total_token_spend,
            "entropy_budget": flux.entropy_budget if hasattr(flux, 'entropy_budget') else 1.0,
        },
        citizens=citizen_cards,
        grid_cols=5,  # Or compute from citizen count
        selected_citizen_id=None,
    )
```

### Task 2: Frontend - Add `live.state` Event Handler

**File:** `impl/claude/web/src/hooks/useTownStream.ts`

Add state for the dashboard JSON:

```typescript
import type { ColonyDashboardJSON } from '@/reactive/types';

// In useTownStream hook:
const [dashboard, setDashboard] = useState<ColonyDashboardJSON | null>(null);

// Add event listener for live.state
eventSource.addEventListener('live.state', (e) => {
  const state: ColonyDashboardJSON = JSON.parse(e.data);
  console.log('[SSE] State update:', state.citizens.length, 'citizens');
  setDashboard(state);
});

// Return dashboard in hook result
return {
  connect,
  disconnect,
  isConnected: ...,
  dashboard,  // NEW
};
```

### Task 3: Create `useTownStreamWidget` Hook

**File:** `impl/claude/web/src/hooks/useTownStreamWidget.ts` (NEW)

A cleaner hook that focuses on widget JSON:

```typescript
import { useState, useEffect, useRef, useCallback } from 'react';
import type { ColonyDashboardJSON } from '@/reactive/types';
import type { TownEvent } from '@/api/types';

interface UseTownStreamWidgetOptions {
  townId: string;
  speed?: number;
  phases?: number;
  autoConnect?: boolean;
  onEvent?: (event: TownEvent) => void;
}

interface UseTownStreamWidgetResult {
  dashboard: ColonyDashboardJSON | null;
  events: TownEvent[];
  isConnected: boolean;
  isPlaying: boolean;
  connect: () => void;
  disconnect: () => void;
}

export function useTownStreamWidget({
  townId,
  speed = 1.0,
  phases = 4,
  autoConnect = false,
  onEvent,
}: UseTownStreamWidgetOptions): UseTownStreamWidgetResult {
  const [dashboard, setDashboard] = useState<ColonyDashboardJSON | null>(null);
  const [events, setEvents] = useState<TownEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!townId || eventSourceRef.current) return;

    const url = `/v1/town/${townId}/live?speed=${speed}&phases=${phases}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onopen = () => setIsConnected(true);
    es.onerror = () => {
      setIsConnected(false);
      setIsPlaying(false);
    };

    es.addEventListener('live.start', () => setIsPlaying(true));
    es.addEventListener('live.end', () => setIsPlaying(false));

    es.addEventListener('live.state', (e) => {
      const state: ColonyDashboardJSON = JSON.parse(e.data);
      setDashboard(state);
    });

    es.addEventListener('live.event', (e) => {
      const event: TownEvent = JSON.parse(e.data);
      setEvents((prev) => [event, ...prev.slice(0, 99)]);
      onEvent?.(event);
    });
  }, [townId, speed, phases, onEvent]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setIsConnected(false);
    setIsPlaying(false);
  }, []);

  useEffect(() => {
    if (autoConnect) connect();
    return () => disconnect();
  }, [autoConnect, connect, disconnect]);

  return { dashboard, events, isConnected, isPlaying, connect, disconnect };
}
```

### Task 4: Tests

**File:** `impl/claude/web/tests/unit/hooks/useTownStreamWidget.test.ts` (NEW)

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTownStreamWidget } from '@/hooks/useTownStreamWidget';

// Mock EventSource
class MockEventSource {
  static instances: MockEventSource[] = [];
  url: string;
  listeners: Map<string, ((e: MessageEvent) => void)[]> = new Map();
  onopen: (() => void) | null = null;
  onerror: ((e: Event) => void) | null = null;
  readyState = EventSource.CONNECTING;

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: (e: MessageEvent) => void) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type)!.push(listener);
  }

  emit(type: string, data: unknown) {
    const event = { data: JSON.stringify(data) } as MessageEvent;
    this.listeners.get(type)?.forEach((l) => l(event));
  }

  simulateOpen() {
    this.readyState = EventSource.OPEN;
    this.onopen?.();
  }

  close() {
    this.readyState = EventSource.CLOSED;
  }
}

describe('useTownStreamWidget', () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal('EventSource', MockEventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('initializes with null dashboard', () => {
    const { result } = renderHook(() =>
      useTownStreamWidget({ townId: 'test-town' })
    );
    expect(result.current.dashboard).toBeNull();
    expect(result.current.isConnected).toBe(false);
  });

  it('connects when connect() is called', () => {
    const { result } = renderHook(() =>
      useTownStreamWidget({ townId: 'test-town' })
    );

    act(() => result.current.connect());

    expect(MockEventSource.instances).toHaveLength(1);
    expect(MockEventSource.instances[0].url).toContain('test-town');
  });

  it('updates dashboard when live.state event received', async () => {
    const { result } = renderHook(() =>
      useTownStreamWidget({ townId: 'test-town', autoConnect: true })
    );

    const es = MockEventSource.instances[0];
    act(() => es.simulateOpen());

    const mockDashboard = {
      type: 'colony_dashboard',
      colony_id: 'test-town',
      phase: 'MORNING',
      day: 1,
      metrics: { total_events: 10, total_tokens: 100, entropy_budget: 1.0 },
      citizens: [],
      grid_cols: 5,
      selected_citizen_id: null,
    };

    act(() => es.emit('live.state', mockDashboard));

    await waitFor(() => {
      expect(result.current.dashboard).toEqual(mockDashboard);
    });
  });

  it('accumulates events from live.event', async () => {
    const { result } = renderHook(() =>
      useTownStreamWidget({ townId: 'test-town', autoConnect: true })
    );

    const es = MockEventSource.instances[0];
    act(() => es.simulateOpen());

    act(() => {
      es.emit('live.event', { tick: 1, operation: 'greet', participants: ['a', 'b'] });
      es.emit('live.event', { tick: 2, operation: 'trade', participants: ['b', 'c'] });
    });

    await waitFor(() => {
      expect(result.current.events).toHaveLength(2);
      expect(result.current.events[0].tick).toBe(2); // Most recent first
    });
  });

  it('sets isPlaying on live.start/live.end', async () => {
    const { result } = renderHook(() =>
      useTownStreamWidget({ townId: 'test-town', autoConnect: true })
    );

    const es = MockEventSource.instances[0];
    act(() => es.simulateOpen());

    expect(result.current.isPlaying).toBe(false);

    act(() => es.emit('live.start', { town_id: 'test-town' }));
    await waitFor(() => expect(result.current.isPlaying).toBe(true));

    act(() => es.emit('live.end', { status: 'completed' }));
    await waitFor(() => expect(result.current.isPlaying).toBe(false));
  });
});
```

### Task 5: Backend Tests

**File:** `impl/claude/protocols/api/_tests/test_town_live_state.py` (NEW)

```python
"""Tests for live.state SSE event emission."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from protocols.api.town import build_colony_dashboard, should_emit_state


class TestShouldEmitState:
    """Tests for should_emit_state logic."""

    def test_emits_every_5_ticks(self) -> None:
        mock_event = MagicMock(operation="greet")
        assert should_emit_state(5, mock_event) is True
        assert should_emit_state(10, mock_event) is True
        assert should_emit_state(3, mock_event) is False

    def test_emits_on_significant_operations(self) -> None:
        for op in ["evolve", "coalition_formed", "coalition_dissolved"]:
            mock_event = MagicMock(operation=op)
            assert should_emit_state(1, mock_event) is True


class TestBuildColonyDashboard:
    """Tests for dashboard building from environment."""

    def test_builds_valid_dashboard_json(self) -> None:
        # Create mock environment
        mock_citizen = MagicMock()
        mock_citizen.id = "alice-123"
        mock_citizen.name = "Alice"
        mock_citizen.archetype = "builder"
        mock_citizen.phase.name = "WORKING"
        mock_citizen.region = "plaza"

        mock_env = MagicMock()
        mock_env.name = "testville"
        mock_env.citizens = {"alice-123": mock_citizen}
        mock_env.total_token_spend = 500

        mock_flux = MagicMock()
        mock_flux.current_phase.name = "MORNING"
        mock_flux.day = 3
        mock_flux.entropy_budget = 0.95

        dashboard = build_colony_dashboard(mock_env, mock_flux, tick=25)
        json_output = dashboard.to_json()

        assert json_output["type"] == "colony_dashboard"
        assert json_output["colony_id"] == "testville"
        assert json_output["phase"] == "MORNING"
        assert json_output["day"] == 3
        assert json_output["metrics"]["total_events"] == 25
        assert len(json_output["citizens"]) == 1
```

---

## Acceptance Criteria

1. **Backend emits `live.state`**: The `/v1/town/{id}/live` endpoint emits `live.state` events containing valid `ColonyDashboardJSON`

2. **Frontend consumes `live.state`**: The `useTownStreamWidget` hook updates its `dashboard` state when receiving `live.state`

3. **Type safety**: No `any` types in the new hook; `ColonyDashboardJSON` from `@/reactive/types` is used

4. **Tests pass**:
   - Backend: `test_town_live_state.py` passes
   - Frontend: `useTownStreamWidget.test.ts` passes
   - Existing: All 109 reactive/widget tests continue to pass

5. **Backwards compatible**: The existing `useTownStream` hook continues to work unchanged

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `impl/claude/protocols/api/town.py` | Modify - add `live.state` emission |
| `impl/claude/web/src/hooks/useTownStreamWidget.ts` | Create - new widget-focused hook |
| `impl/claude/web/tests/unit/hooks/useTownStreamWidget.test.ts` | Create - hook tests |
| `impl/claude/protocols/api/_tests/test_town_live_state.py` | Create - backend tests |

---

## Notes

- Do NOT modify `useTownStream.ts` - create a new hook instead for backwards compatibility
- The `build_colony_dashboard` function needs to map from the environment's `Citizen` objects to `CitizenWidget` cards
- Check if `ColonyDashboard` widget class exists at `impl/claude/agents/i/reactive/colony_dashboard.py` - if not, create it
- The `live.state` event should be emitted after `live.event` to ensure the dashboard reflects the latest event

---

## Verification Commands

```bash
# Backend tests
cd impl/claude && uv run pytest protocols/api/_tests/test_town_live_state.py -v

# Frontend tests
cd impl/claude/web && npm test -- --run tests/unit/hooks/useTownStreamWidget.test.ts

# All reactive tests still pass
cd impl/claude/web && npm test -- --run tests/unit/reactive tests/unit/widgets
```
