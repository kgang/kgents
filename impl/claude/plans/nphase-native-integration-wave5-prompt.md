# N-Phase Native Integration: Wave 5 Continuation Prompt

## Context

Waves 1-4 of N-Phase native integration are complete. This prompt continues with Wave 5: Frontend & Polish.

## What Was Built (Waves 1-4)

### Wave 1: Session State Foundation
**File**: `protocols/nphase/session.py` (50 tests)

```python
from protocols.nphase.session import (
    NPhaseSession,      # Stateful session with phase tracking
    Handle,             # AGENTESE paths acquired during phases
    SessionCheckpoint,  # Snapshot for rollback/recovery
    PhaseLedgerEntry,   # Audit trail entry
    create_session,     # Factory function
    get_session,        # Retrieve by ID
)
```

### Wave 2: Phase Detection
**File**: `protocols/nphase/detector.py` (45 tests)

```python
from protocols.nphase.detector import (
    PhaseDetector,   # Detects transitions from output
    PhaseSignal,     # Detection result
    SignalAction,    # CONTINUE, HALT, ELASTIC, HEURISTIC, NONE
    detect_phase,    # Convenience function
)
```

### Wave 3: REST API
**File**: `protocols/api/nphase.py` (29 tests)

Endpoints:
- `POST /v1/nphase/sessions` - Create session
- `GET /v1/nphase/sessions/{id}` - Get session
- `POST /v1/nphase/sessions/{id}/advance` - Advance phase
- `POST /v1/nphase/sessions/{id}/detect` - Detect phase from output
- `POST /v1/nphase/sessions/{id}/checkpoint` - Create checkpoint
- `POST /v1/nphase/sessions/{id}/restore` - Restore from checkpoint

### Wave 4: Integration (64 tests)

| Task | Feature | File |
|------|---------|------|
| 4.1 | WorkshopFlux N-Phase tracking | `agents/town/workshop.py` |
| 4.2 | Builder phase awareness | `agents/town/builders/base.py` |
| 4.3 | K-gent session bridge | `agents/k/session.py` |
| 4.4 | EventBus integration | `protocols/nphase/session.py` |
| 4.5 | Town live state SSE | `protocols/api/town.py` |

**Key APIs from Wave 4:**

```python
# Town live streaming with N-Phase
GET /v1/town/{id}/live?nphase_enabled=true

# SSE events emitted:
# - live.start (includes nphase context)
# - live.nphase (on phase transitions)
# - live.state (includes nphase in payload)
# - live.end (includes nphase_summary)
```

**Phase Mapping (Town → N-Phase):**
- MORNING, AFTERNOON → UNDERSTAND
- EVENING → ACT
- NIGHT → REFLECT

## Wave 5: Frontend & Polish Tasks

### Task 5.1: React Hook for N-Phase SSE

**Goal**: Create a React hook that consumes N-Phase events from the live stream.

**File to create**: `web/src/hooks/useNPhaseStream.ts`

**Implementation**:
```typescript
interface NPhaseState {
  sessionId: string | null;
  currentPhase: 'UNDERSTAND' | 'ACT' | 'REFLECT';
  cycleCount: number;
  checkpointCount: number;
  handleCount: number;
  transitions: NPhaseTransition[];
}

interface NPhaseTransition {
  tick: number;
  fromPhase: string;
  toPhase: string;
  trigger: string;
  timestamp: Date;
}

export function useNPhaseStream(townId: string, enabled: boolean): NPhaseState;
```

**Features**:
1. Parse `live.nphase` events into state
2. Track transition history
3. Extract N-Phase from `live.state` events
4. Handle `live.start` and `live.end` for session lifecycle

### Task 5.2: Phase Indicator Component

**Goal**: Visual indicator showing current N-Phase in Town UI.

**File to create**: `web/src/components/town/PhaseIndicator.tsx`

**Design**:
```
┌─────────────────────────────────────┐
│  ◉ UNDERSTAND  ○ ACT  ○ REFLECT    │
│  Cycle 1 • 3 checkpoints           │
└─────────────────────────────────────┘
```

**Features**:
1. Three-phase indicator with active highlight
2. Cycle count display
3. Checkpoint count
4. Animate on transitions
5. Tooltip with phase description

### Task 5.3: Phase Timeline Widget

**Goal**: Show N-Phase transitions over time in the event feed.

**File to create**: `web/src/components/town/PhaseTimeline.tsx`

**Design**:
```
UNDERSTAND ════════╗
                   ║ tick 15: EVENING
ACT ═══════════════╬════════╗
                            ║ tick 28: NIGHT
REFLECT ════════════════════╩═══════
```

**Features**:
1. Horizontal timeline showing phase regions
2. Transition markers with tick numbers
3. Current position indicator
4. Click to see transition details

### Task 5.4: Integration with Town Page

**Goal**: Wire N-Phase components into the Town page.

**File to modify**: `web/src/pages/Town.tsx` or `TownV2.tsx`

**Implementation**:
1. Add `nphaseEnabled` toggle to controls
2. Pass to `useTownStream` hook
3. Render `PhaseIndicator` in header
4. Show `PhaseTimeline` in sidebar or below mesa

### Task 5.5: API Client Updates

**Goal**: Update TypeScript API client with N-Phase types.

**File to modify**: `web/src/api/types.ts`

**Types to add**:
```typescript
interface NPhaseContext {
  session_id: string;
  current_phase: 'UNDERSTAND' | 'ACT' | 'REFLECT';
  cycle_count: number;
  checkpoint_count: number;
  handle_count: number;
}

interface NPhaseTransitionEvent {
  tick: number;
  from_phase: string;
  to_phase: string;
  session_id: string;
  cycle_count: number;
  trigger: string;
}

interface LiveStartEvent {
  town_id: string;
  phases: number;
  speed: number;
  nphase_enabled: boolean;
  nphase?: NPhaseContext;
}

interface LiveEndEvent {
  town_id: string;
  total_ticks: number;
  status: string;
  nphase_summary?: NPhaseContext & { ledger_entries: number };
}
```

### Task 5.6: End-to-End Test

**Goal**: Playwright test for N-Phase UI flow.

**File to create**: `web/e2e/nphase-integration.spec.ts`

**Test scenarios**:
1. Start town with N-Phase enabled
2. Verify phase indicator appears
3. Wait for phase transition
4. Verify timeline updates
5. Check end summary includes N-Phase

### Task 5.7: Documentation

**Goal**: Document N-Phase integration for developers.

**File to create**: `docs/skills/nphase-integration.md`

**Sections**:
1. Overview of N-Phase cycle
2. Backend API reference
3. Frontend hook usage
4. Phase mapping rules
5. Event bus integration
6. Troubleshooting

## Testing Strategy

```bash
# Backend tests (already passing)
uv run pytest protocols/nphase/_tests/ -v  # 195 tests
uv run pytest protocols/api/_tests/test_town_nphase.py -v  # 16 tests

# Frontend tests (to add)
cd web && npm test -- --grep "NPhase"

# E2E tests (to add)
cd web && npx playwright test nphase-integration
```

## Key Files Reference

| Purpose | File |
|---------|------|
| Session state | `protocols/nphase/session.py` |
| Phase detection | `protocols/nphase/detector.py` |
| Events | `protocols/nphase/events.py` |
| N-Phase API | `protocols/api/nphase.py` |
| Town live SSE | `protocols/api/town.py` |
| React hook (new) | `web/src/hooks/useNPhaseStream.ts` |
| Phase indicator (new) | `web/src/components/town/PhaseIndicator.tsx` |
| Phase timeline (new) | `web/src/components/town/PhaseTimeline.tsx` |

## Design Principles

1. **Progressive Enhancement**: N-Phase UI should be optional, not intrusive
2. **Observable State**: All phase changes visible in real-time
3. **Graceful Degradation**: Works without N-Phase enabled
4. **Consistent Mapping**: Town phase → N-Phase mapping is deterministic

## Success Criteria

- [ ] React hook consumes N-Phase SSE events
- [ ] Phase indicator shows current phase and cycle
- [ ] Phase timeline visualizes transitions
- [ ] Town page has N-Phase toggle
- [ ] TypeScript types match backend models
- [ ] E2E test validates full flow
- [ ] Documentation complete

## Estimated Scope

- Task 5.1: ~100 lines TypeScript
- Task 5.2: ~80 lines TSX + CSS
- Task 5.3: ~120 lines TSX + CSS
- Task 5.4: ~30 lines modifications
- Task 5.5: ~50 lines types
- Task 5.6: ~60 lines Playwright
- Task 5.7: ~200 lines markdown

## Notes

The backend is complete and stable. Wave 5 is purely frontend integration and polish. All SSE events are already being emitted correctly - we just need to consume them in the React UI.

Consider using the existing `useTownStream` hook as a base pattern for `useNPhaseStream`, or extending it to include N-Phase state.
