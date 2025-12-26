# Unified Mark Type - Implementation Summary

**Status**: ✅ Complete
**Date**: 2025-12-25
**Files Changed**: 4 created, 2 modified

## Overview

Implemented a unified `Mark` type with domain support for the backend, along with a generic `Trace` type for immutable mark sequences. This provides the backend infrastructure to match the frontend witness hooks.

## What Was Implemented

### 1. Domain Support for Mark (`services/witness/mark.py`)

**Added**:
- `WitnessDomain` type alias for domain categorization
- `domain` field to `Mark` dataclass (default: `"system"`)
- Domain preservation in all immutable operations (`with_link`, `with_proof`)
- Domain serialization/deserialization (`to_dict`, `from_dict`)

**Supported Domains**:
- `"navigation"` - Route changes, page navigation
- `"portal"` - Portal expansions/collapses (Context Perception)
- `"chat"` - Chat messages, turns
- `"edit"` - K-Block edits, mutations
- `"system"` - System-level events (default)

### 2. Trace Type (`services/witness/trace.py`)

**Created**:
New generic type `Trace[M]` for immutable mark sequences with:

**Operations**:
- `add(mark)` - Immutable append
- `extend(marks)` - Bulk append
- `filter(predicate)` - Custom filtering
- `filter_by_domain(domain)` - Domain filtering
- `filter_by_origin(origin)` - Origin filtering
- `merge(other)` - Combine traces (sorted by timestamp)
- `slice(start, end)` - Temporal slicing
- `get(index)` - Indexed access

**Properties**:
- `latest` - Most recent mark
- `earliest` - Oldest mark
- `len(trace)` - Mark count
- `bool(trace)` - Empty check

**Philosophy**: Simpler than `Walk` (no N-Phase, no Forest binding), focused on pure mark collection.

### 3. Comprehensive Tests

**Created**:
- `services/witness/_tests/test_unified_mark.py` (16 tests)
  - Domain support across all domain types
  - Mark immutability (frozen=True)
  - Serialization with domain preservation
  - Factory methods (`from_thought`, `from_agentese`)
  - Integration tests

- `services/witness/_tests/test_trace.py` (29 tests)
  - Trace immutability (add returns new Trace)
  - Filtering operations
  - Merging and temporal ordering
  - Slicing and indexing
  - Iteration and properties

**Results**: ✅ 45/45 tests passing, mypy clean

### 4. Documentation

**Created**:
- `services/witness/UNIFIED_MARK_USAGE.md` - Usage guide with examples
- `UNIFIED_MARK_IMPLEMENTATION.md` - This summary

## Files Changed

### Created
1. `/impl/claude/services/witness/trace.py` - Generic Trace type
2. `/impl/claude/services/witness/_tests/test_unified_mark.py` - Mark tests
3. `/impl/claude/services/witness/_tests/test_trace.py` - Trace tests
4. `/impl/claude/services/witness/UNIFIED_MARK_USAGE.md` - Usage guide
5. `/impl/claude/UNIFIED_MARK_IMPLEMENTATION.md` - This summary

### Modified
1. `/impl/claude/services/witness/mark.py`
   - Added `WitnessDomain` type alias
   - Added `domain` field to `Mark`
   - Updated `to_dict()` and `from_dict()`
   - Updated `with_link()` and `with_proof()`
   - Exported `WitnessDomain`

2. `/impl/claude/services/witness/__init__.py`
   - Imported and exported `Trace`
   - Imported and exported `WitnessDomain`

## Architecture Decisions

### Why Not Inherit ChatMark from Mark?

**Decision**: Keep `ChatMark` separate, recommend new code use `Mark` with `domain="chat"`.

**Reasoning**:
- ChatMark has domain-specific fields (`session_id`, `turn_number`, `user_message`)
- Mark is generic with `stimulus`/`response` pattern
- Inheritance would force either:
  - Mark to know about chat (coupling)
  - ChatMark to duplicate all Mark fields (complexity)
- Current gotcha comment in `services/chat/witness.py` already documents this

**Migration Path**: New chat code can use `Mark(domain="chat")` with metadata for session/turn.

### Trace vs Walk

**Trace**: Generic mark collection
- Immutable append-only sequence
- Generic filtering (domain, origin, predicate)
- No N-Phase awareness
- No Forest binding
- Lightweight

**Walk**: N-Phase workflow execution
- Binds to Forest plan (`root_plan: PlanPath`)
- Tracks phase transitions (SENSE → ACT → REFLECT)
- Manages participant Umwelts
- Heavyweight, workflow-aware

**Use Trace when**: You just need mark history with filtering
**Use Walk when**: You need N-Phase workflow tracking

## Integration Points

### Frontend Integration

Frontend witness hooks (useWitness.ts) can now:
```typescript
const { createMark } = useWitness();

// Backend will receive domain field
createMark({
  action: "Navigate to /chat",
  domain: "navigation",  // ← Now preserved in backend Mark
  reasoning: "User clicked chat link",
});
```

### Existing Systems

**Portal Marks**: Already uses unified Mark with `domain="portal"`
```python
# services/witness/portal_marks.py
mark = Mark(
    origin="context_perception",
    domain="portal",  # ✓ Already using unified type
    ...
)
```

**ChatMark**: Remains for backward compatibility
```python
# Old code continues to work
from services.chat.witness import ChatMark
chat_mark = ChatMark(...)

# New code can use unified type
from services.witness import Mark
mark = Mark(domain="chat", ...)
```

## Examples

### Creating Marks Across Domains

```python
from services.witness import Mark, Stimulus, Response

# Navigation mark
nav = Mark(
    origin="navigator",
    domain="navigation",
    stimulus=Stimulus(kind="route", content="/chat"),
    response=Response(kind="navigation", content="Navigated"),
)

# Portal mark
portal = Mark(
    origin="context_perception",
    domain="portal",
    stimulus=Stimulus(kind="portal", content="Expand imports"),
    response=Response(kind="exploration", content="Expanded"),
)

# Chat mark
chat = Mark(
    origin="chat_session",
    domain="chat",
    stimulus=Stimulus(kind="prompt", content="Hello"),
    response=Response(kind="text", content="Hi!"),
)
```

### Building and Filtering Traces

```python
from services.witness import Trace

# Build trace
trace = Trace[Mark]()
trace = trace.add(nav)
trace = trace.add(portal)
trace = trace.add(chat)

# Filter by domain
chat_trace = trace.filter_by_domain("chat")
assert len(chat_trace) == 1

# Custom filter
recent = trace.filter(lambda m: m.timestamp > cutoff)

# Slice
last_10 = trace.slice(-10)
```

## Testing Evidence

```bash
# Mark tests
$ uv run pytest services/witness/_tests/test_unified_mark.py -v
====== 16 passed in 2.85s ======

# Trace tests
$ uv run pytest services/witness/_tests/test_trace.py -v
====== 29 passed in 3.57s ======

# Type checking
$ uv run mypy services/witness/mark.py
Success: no issues found

$ uv run mypy services/witness/trace.py
Success: no issues found
```

## Next Steps

### Frontend Integration
1. Update API endpoints to accept `domain` field
2. Create AGENTESE nodes for mark creation/querying
3. Wire frontend useWitness hooks to backend endpoints
4. Add domain-based mark filtering in DirectorDashboard

### Backend Enhancements
1. Add MarkStore filtering by domain
2. Create domain-specific mark queries
3. Add trace persistence (optional)
4. Consider migrating ChatMark to use unified Mark (optional)

### Documentation
1. Update `spec/protocols/witness-primitives.md` with domain field
2. Add Trace to witness spec
3. Update API documentation

## Principles Applied

✅ **Immutable** - Marks frozen, Traces return new instances
✅ **Composable** - Traces support filtering, merging, slicing
✅ **Tasteful** - Clean API, well-tested, minimal complexity
✅ **Generative** - Domain field enables new filtering patterns
✅ **Joy-Inducing** - Simple, predictable, type-safe

## Teaching Moments

**Gotcha**: `Trace.add()` returns a NEW Trace. Don't forget to capture:
```python
trace = trace.add(mark)  # ✓ Correct
trace.add(mark)          # ✗ Wrong (discards result)
```

**Gotcha**: Domain defaults to `"system"` if not specified:
```python
mark = Mark(origin="test")
assert mark.domain == "system"  # Default
```

**Gotcha**: ChatMark is intentionally separate from Mark:
```python
# Different field structures:
ChatMark(user_message="...", assistant_response="...")
Mark(stimulus=Stimulus(...), response=Response(...))
```

---

**Implementation complete**. All tests pass. Ready for frontend integration.
