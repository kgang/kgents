# U-gent Tooling Phase 0: Complete ✓

> *"Spec is compression. A handoff that can't regenerate the fix doesn't understand the fix."*

## Foundation Status

**Complete** (58 tests passing, 0 mypy errors):
- `Tool[A, B]` protocol with `>>` composition — category laws verified
- `ToolRegistry` — trust-gated discovery
- `ToolTrustGate` — integrates with Witness trust levels
- `ToolExecutor` — timeout, trace recording, SynergyBus integration
- Contracts for all tool types in `contracts.py`
- `Jewel.TOOLING` — 10th Crown Jewel registered
- `TOOL_*` events — invoked, completed, failed, trust_denied

---

## The Fixes (Generative Patterns)

### Pattern 1: Generic Umwelt Reference

**Problem**: `Umwelt` without type params, or undefined name.

**Solution**: Use `Any` in TYPE_CHECKING blocks, never raw `Umwelt` in type hints.

```python
# BEFORE (error)
def check(self, observer: Umwelt, ...) -> GateResult:

# AFTER (fixed)
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from typing import Any as UmweltType

def check(self, observer: Any, ...) -> GateResult:  # Umwelt is generic, use Any
```

Files: `trust_gate.py:167,215,241`, `executor.py:262`

### Pattern 2: Pipeline Return Type

**Problem**: `ToolPipeline.invoke` returns `Any`, declared as `B`.

**Solution**: Cast is acceptable here — the pipeline composition ensures type safety at construction.

```python
# base.py line 317
async def invoke(self, request: A) -> B:
    result: Any = request
    for step in self.steps:
        result = await step.invoke(result)
    return cast(B, result)  # Safe: pipeline composition guarantees type flow
```

### Pattern 3: DifferanceStore Method Name

**Problem**: `record_trace` doesn't exist — it's `append`.

**Solution**: `executor.py` line 301:
```python
# BEFORE
asyncio.create_task(self._differance.record_trace(trace))

# AFTER
asyncio.create_task(self._differance.append(trace))
```

### Pattern 4: Duplicate Test Name

**Problem**: `test_returns_result_on_allowed` defined twice in `test_trust_gate.py`.

**Solution**: Rename second occurrence (likely `test_returns_result_on_allowed_with_observer`).

---

## SynergyBus Integration (Complete the Executor)

The `_emit_event` method currently logs. To fully integrate:

### Step 1: Add TOOLING Jewel

```python
# protocols/synergy/events.py - Jewel enum
TOOLING = "tooling"  # 10th Crown Jewel - Tool Infrastructure
```

### Step 2: Add TOOL_* Event Types

```python
# protocols/synergy/events.py - SynergyEventType enum
# Tooling events (U-gent Tool Infrastructure)
TOOL_INVOKED = "tool.invoked"
TOOL_COMPLETED = "tool.completed"
TOOL_FAILED = "tool.failed"
TOOL_TRUST_DENIED = "tool.trust_denied"
```

### Step 3: Factory Function

```python
def create_tool_invoked_event(
    execution_id: str,
    tool_name: str,
    observer_id: str | None = None,
    trust_level: int = 0,
    correlation_id: str | None = None,
) -> SynergyEvent:
    return SynergyEvent(
        source_jewel=Jewel.TOOLING,
        target_jewel=Jewel.ALL,
        event_type=SynergyEventType.TOOL_INVOKED,
        source_id=execution_id,
        payload={
            "tool_name": tool_name,
            "observer_id": observer_id,
            "trust_level": trust_level,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )
```

### Step 4: Executor Implementation

```python
# services/tooling/executor.py
async def _emit_event(
    self,
    event_type: str,
    ctx: ExecutionContext,
    request: Any,
    result: Any = None,
    error: str | None = None,
) -> None:
    if self._synergy_bus is None:
        return

    from protocols.synergy import SynergyEvent, SynergyEventType, Jewel

    type_map = {
        "tool.invoked": SynergyEventType.TOOL_INVOKED,
        "tool.completed": SynergyEventType.TOOL_COMPLETED,
        "tool.failed": SynergyEventType.TOOL_FAILED,
        "tool.trust_denied": SynergyEventType.TOOL_TRUST_DENIED,
    }

    event = SynergyEvent(
        source_jewel=Jewel.TOOLING,
        target_jewel=Jewel.ALL,
        event_type=type_map.get(event_type, SynergyEventType.TOOL_INVOKED),
        source_id=ctx.execution_id,
        payload={
            "tool_name": ctx.tool_name,
            "observer_id": ctx.observer_id,
            "success": ctx.success,
            "duration_ms": ctx.duration_ms,
            "error": error,
        },
    )

    # Fire-and-forget (Pattern 6)
    asyncio.create_task(self._synergy_bus.emit(event))
```

---

## Verification (All Passing ✓)

```bash
cd impl/claude
uv run mypy services/tooling/        # ✓ 0 errors (12 files)
uv run pytest services/tooling/ -v   # ✓ 58 passed
uv run pytest protocols/synergy/ -q  # ✓ 146 passed
```

---

## What Was Done

1. **Fixed Umwelt type references** → Use `Any` instead of generic `Umwelt`
2. **Fixed ToolPipeline return type** → Added `cast(B, result)`
3. **Fixed DifferanceStore method** → `append` not `record_trace`
4. **Fixed duplicate test name** → Renamed to unique name
5. **Added TOOLING Jewel** → 10th Crown Jewel
6. **Added TOOL_* events** → 4 event types with factory functions
7. **Completed executor emission** → Full SynergyBus integration

*The simplest thing that could work. Tasteful > feature-complete.*
