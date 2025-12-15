# N-Phase Native Integration: Wave 4 Continuation Prompt

## Context

Waves 1-3 of N-Phase native integration are complete. This prompt continues with Wave 4: Integration.

## What Was Built (Waves 1-3)

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

Key design decisions implemented:
- D1: Phase state lives in Session Router (not LLM context)
- D4: Checkpoint at phase boundaries + on-demand
- D5: Handle accumulation per phase

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

Signifiers detected:
- `⟿[PHASE]` - Continue to phase (UNDERSTAND, ACT, REFLECT)
- `⟂[REASON]` - Halt, await human input
- `⤳[OP:args]` - Elastic operation (COMPRESS, EXPAND, CHECKPOINT)

### Wave 3: REST API
**File**: `protocols/api/nphase.py` (29 tests)

Endpoints available:
- `POST /v1/nphase/sessions` - Create session
- `GET /v1/nphase/sessions/{id}` - Get session
- `POST /v1/nphase/sessions/{id}/advance` - Advance phase
- `POST /v1/nphase/sessions/{id}/detect` - Detect phase from output
- `POST /v1/nphase/sessions/{id}/checkpoint` - Create checkpoint
- `POST /v1/nphase/sessions/{id}/restore` - Restore from checkpoint

### Events System
**File**: `protocols/nphase/events.py`

```python
from protocols.nphase.events import (
    PhaseTransitionEvent,
    PhaseCheckpointEvent,
    PhaseSignalDetectedEvent,
    SessionCreatedEvent,
    SessionEndedEvent,
)
```

## Wave 4: Integration Tasks

### Task 4.1: WorkshopFlux Integration

**Goal**: Wire N-Phase session to WorkshopFlux for automatic phase detection during builder execution.

**Files to modify**:
- `agents/town/workshop.py` - WorkshopFlux class
- `protocols/api/town.py` - Town API endpoints

**Pattern to follow** (from workshop.py):
```python
class WorkshopFlux:
    async def step(self) -> AsyncIterator[WorkshopEvent]:
        # After builder produces output, detect phase signal
        # If high-confidence transition, advance session
```

**Implementation approach**:
1. Add optional `nphase_session: NPhaseSession | None` to WorkshopFlux
2. In `step()`, after getting builder output:
   ```python
   if self._nphase_session:
       signal = detect_phase(output_text, self._nphase_session.current_phase)
       if signal.should_auto_advance and signal.target_phase:
           self._nphase_session.advance_phase(signal.target_phase)
           # Emit PhaseTransitionEvent
   ```
3. Map WorkshopPhase to NPhase:
   - EXPLORING, DESIGNING → UNDERSTAND
   - PROTOTYPING, REFINING → ACT
   - INTEGRATING → REFLECT

**Tests to add**: `agents/town/_tests/test_workshop_nphase.py`

### Task 4.2: Builder Phase Awareness

**Goal**: Builders should know which N-Phase they're operating in for context-aware behavior.

**Files to modify**:
- `agents/town/builders/base.py` - Builder class

**Implementation**:
1. Add `nphase_context: NPhase | None` property to Builder
2. Include in `WorkshopDialogueContext.to_prompt_context()`
3. Builders can adjust verbosity/approach based on phase

### Task 4.3: K-gent Session Bridge

**Goal**: Allow K-gent sessions to optionally use N-Phase tracking.

**Files to modify**:
- `protocols/api/sessions.py` - K-gent sessions API
- `agents/k/flux.py` - KgentFlux

**Implementation approach**:
1. Add `nphase_enabled: bool = False` to `CreateSessionRequest`
2. When enabled, create paired NPhaseSession
3. On dialogue response, run phase detection
4. Store N-Phase session ID in K-gent session metadata

**API changes**:
```python
# New field in CreateSessionRequest
nphase_enabled: bool = Field(default=False)

# New endpoint or extend existing
GET /v1/kgent/sessions/{id}/phase  # Get N-Phase state
POST /v1/kgent/sessions/{id}/phase/advance  # Manual advance
```

### Task 4.4: Event Bus Integration

**Goal**: N-Phase events should flow through the event bus for observability.

**Files to modify**:
- `protocols/nphase/session.py` - Add event emission
- `agents/town/event_bus.py` - Ensure compatibility

**Implementation**:
1. Add optional `event_bus: EventBus[NPhaseEvent]` to NPhaseSession
2. Emit events on:
   - Session creation → SessionCreatedEvent
   - Phase advance → PhaseTransitionEvent
   - Checkpoint creation → PhaseCheckpointEvent
   - Signal detection → PhaseSignalDetectedEvent

### Task 4.5: Town Live State Enhancement

**Goal**: Include N-Phase state in Town live streaming.

**Files to modify**:
- `protocols/api/town.py` - `/v1/town/{id}/live` endpoint

**Implementation**:
Add to live state response:
```python
{
    "nphase": {
        "session_id": "...",
        "current_phase": "ACT",
        "cycle_count": 1,
        "last_signal": {...}
    }
}
```

## Testing Strategy

Each task should have dedicated tests:

```
protocols/nphase/_tests/test_workshop_integration.py  # Task 4.1
agents/town/_tests/test_builder_nphase.py            # Task 4.2
protocols/api/_tests/test_sessions_nphase.py         # Task 4.3
protocols/nphase/_tests/test_events_integration.py   # Task 4.4
protocols/api/_tests/test_town_nphase.py             # Task 4.5
```

## Key Files Reference

| Purpose | File |
|---------|------|
| Session state | `protocols/nphase/session.py` |
| Phase detection | `protocols/nphase/detector.py` |
| Events | `protocols/nphase/events.py` |
| N-Phase API | `protocols/api/nphase.py` |
| Workshop | `agents/town/workshop.py` |
| Builder base | `agents/town/builders/base.py` |
| K-gent sessions | `protocols/api/sessions.py` |
| Town API | `protocols/api/town.py` |

## Design Principles to Follow

1. **Perturbation Principle**: Inject events, never bypass state
2. **Operad Composition**: N-Phase operations compose with Town operations
3. **Observer-Dependent**: Phase detection depends on current context
4. **Graceful Degradation**: N-Phase integration is optional, not required

## Success Criteria

- [ ] WorkshopFlux can optionally track N-Phase state
- [ ] Phase transitions emit events to event bus
- [ ] K-gent sessions can enable N-Phase tracking
- [ ] Town live state includes N-Phase information
- [ ] All new code has tests
- [ ] Existing tests still pass

## Estimated Scope

- Task 4.1: ~150 lines + tests
- Task 4.2: ~50 lines + tests
- Task 4.3: ~100 lines + tests
- Task 4.4: ~80 lines + tests
- Task 4.5: ~40 lines + tests

Total: ~420 lines of implementation + tests

## Command to Start

```bash
/hydrate plans/nphase-native-integration-wave4-prompt.md
```

Then: "Implement Wave 4 Task 4.1: WorkshopFlux Integration"
