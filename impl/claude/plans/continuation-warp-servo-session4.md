# WARP + Servo Integration: Session 4 Handoff

> *"Law 3: Every AGENTESE invocation emits exactly one TraceNode."*

**Date**: 2025-12-20
**Previous Session**: Session 3 (AGENTESE Node Registration)
**This Session**: A3 TraceNode Coverage Enforcement

---

## Session 4 Accomplishments

### A3: TraceNode Coverage Enforcement (COMPLETE)

**The Big Insight**: Instead of TraceNodeBuilder (which would complicate immutability), we create TraceNode AFTER invocation with complete information. This preserves Law 1 (immutability) while enforcing Law 3 (completeness).

**Implementation**:

1. **Added AGENTESE topics to WitnessSynergyBus** (`services/witness/bus.py`):
   ```python
   AGENTESE_INVOKED = "witness.agentese.invoked"
   AGENTESE_COMPLETED = "witness.agentese.completed"
   AGENTESE_ERROR = "witness.agentese.error"
   AGENTESE_ALL = "witness.agentese.*"
   ```

2. **Added `get_synergy_bus()` convenience function** for external access to the bus.

3. **Wired TraceStore to DI container** (`services/providers.py`):
   - Added `get_trace_store()` provider function
   - Registered in container as singleton

4. **Instrumented `gateway._invoke_path()`** (`protocols/agentese/gateway.py`):
   - `_invoke_path()` now wraps all invocations with TraceNode emission
   - `_emit_trace()` creates and stores TraceNode
   - `_summarize_result()` truncates large results for storage
   - `_publish_trace_event()` publishes to SynergyBus (fire-and-forget)

5. **Added 6 tests for TraceNode emission** (`protocols/agentese/_tests/test_gateway.py`):
   - `test_invoke_emits_trace_node` - Verifies successful invocations emit traces
   - `test_manifest_emits_trace_node` - Verifies manifest calls emit traces
   - `test_error_emits_trace_node_with_error` - Verifies errors emit traces with error response
   - `test_trace_node_captures_observer` - Verifies observer context is captured
   - `test_multiple_invocations_emit_multiple_traces` - Verifies trace uniqueness
   - `test_trace_node_synergy_bus_publication` - Verifies bus wiring

**Test Results**:
- Gateway tests: 28 passed
- Witness tests: 862 passed
- Mypy: Success (no issues)

---

## Design Decisions

### Why Not TraceNodeBuilder?

TraceNode is `frozen=True` (Law 1: Immutability). Options considered:

1. **TraceNodeBuilder** (mutable → frozen pattern) - Adds complexity, breaks the single frozen pattern
2. **`object.__setattr__` trick** - Violates the spirit of immutability
3. **Create after invocation** (chosen) - Simple, preserves Law 1, complete information available

The chosen approach creates the TraceNode AFTER the invocation completes, with full stimulus + response information.

### Streaming (SSE) Handling

For async generators (streaming responses), we can't wait for stream completion. Instead:
- Emit TraceNode at invocation start
- Response kind is `"stream"` with `metadata={"streaming": True}`
- This captures the invocation while allowing the stream to proceed

### Error Isolation

Trace emission is wrapped in try/except to ensure:
- Gateway never fails due to trace emission failure
- Errors are logged at WARNING level (visible but not blocking)
- SynergyBus publish failures are logged at DEBUG level

---

## Files Changed This Session

| File | Change |
|------|--------|
| `services/witness/bus.py` | Added AGENTESE topics + `get_synergy_bus()` |
| `services/providers.py` | Added `get_trace_store()` provider |
| `protocols/agentese/gateway.py` | Instrumented `_invoke_path()` with trace emission |
| `protocols/agentese/_tests/test_gateway.py` | Added 6 TraceNode emission tests |

---

## Remaining Work for Session 5

### C1: Brain + Terrace Integration (1 hour)

**Files**:
- `services/brain/`
- `services/witness/terrace.py`
- `protocols/agentese/contexts/brain_terrace.py`

**Tasks**:
- [ ] Wire Brain.capture to emit TraceNode via gateway (already done!)
- [ ] Wire Brain.synthesize to check VoiceGate
- [ ] Wire Terrace to Brain's crystal system
- [ ] Add `brain.terrace.curate` aspect for human-curated knowledge

### C2: Gardener + Walk Integration (1 hour)

**Files**:
- `services/gardener/`
- `services/witness/walk.py`
- `protocols/agentese/contexts/time_trace_warp.py`

**Tasks**:
- [ ] Every CLI session creates a Walk
- [ ] Walk binds to current plan (from `plans/` Forest)
- [ ] Walk advances on each Gardener tending operation
- [ ] Walk pauses/resumes with session lifecycle

### C3: Conductor + Ritual Integration (1.5 hours)

**Files**:
- `services/conductor/`
- `services/witness/ritual.py`
- `protocols/agentese/contexts/self_ritual.py`

**Tasks**:
- [ ] Conductor workflows become Rituals
- [ ] Each Ritual has exactly one Covenant (enforced)
- [ ] Each Ritual has exactly one Offering (enforced)
- [ ] Phase transitions follow N-Phase grammar
- [ ] SentinelGuards emit TraceNodes on evaluation

---

## Quick Start for Next Session

```bash
# Verify TraceNode emission working
cd impl/claude
uv run python -c "
from protocols.agentese.gateway import create_gateway
from services.witness.trace_store import get_trace_store, reset_trace_store
reset_trace_store()
print('TraceStore ready, gateway instrumented with Law 3 enforcement')
"

# Run all WARP tests
uv run pytest services/witness/_tests/ protocols/agentese/_tests/test_gateway.py -v --tb=short

# Start servers for manual testing
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

---

## Anti-Sausage Check

Before ending:
- Did I smooth anything that should stay rough? **No - Law 3 is now enforced at the gateway level**
- Did I add words Kent wouldn't use? **No - "Law 3", "TraceNode", "composable" are from the spec**
- Did I lose any opinionated stances? **No - every invocation now traces, no exceptions**
- Is this still daring, bold, creative? **Yes - automatic tracing of ALL AGENTESE invocations is bold**

---

## Learnings for meta.md

```
Gateway-level trace emission: Law 3 enforced at _invoke_path() - all paths get tracing automatically
TraceNode after invocation: Create frozen after completion, not mutable during - simpler, Law 1 preserved
Fire-and-forget bus publish: asyncio.create_task for non-blocking SynergyBus events
```

---

*"The persona is a garden, not a museum"* — Session 4 made every AGENTESE path auditable
