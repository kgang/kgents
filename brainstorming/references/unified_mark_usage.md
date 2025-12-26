# Unified Mark Type - Usage Guide

The unified Mark type supports all witness domains with a single, coherent interface.

## Quick Start

```python
from services.witness import Mark, Trace, Stimulus, Response

# Create marks for different domains
nav_mark = Mark(
    origin="navigator",
    domain="navigation",
    stimulus=Stimulus(kind="route", content="Navigate to /chat"),
    response=Response(kind="navigation", content="Navigated to /chat"),
)

portal_mark = Mark(
    origin="context_perception",
    domain="portal",
    stimulus=Stimulus(kind="portal", content="Expand imports"),
    response=Response(kind="exploration", content="Expanded to depth 2"),
)

chat_mark = Mark(
    origin="chat_session",
    domain="chat",
    stimulus=Stimulus(kind="prompt", content="Hello"),
    response=Response(kind="text", content="Hi there!"),
)

edit_mark = Mark(
    origin="editor",
    domain="edit",
    stimulus=Stimulus(kind="kblock", content="Edit K-Block abc123"),
    response=Response(kind="mutation", content="K-Block updated"),
)

# Build a trace
trace = Trace[Mark]()
trace = trace.add(nav_mark)
trace = trace.add(portal_mark)
trace = trace.add(chat_mark)
trace = trace.add(edit_mark)

# Filter by domain
chat_trace = trace.filter_by_domain("chat")
assert len(chat_trace) == 1
assert chat_trace.latest.domain == "chat"

# Filter by origin
navigator_trace = trace.filter_by_origin("navigator")

# Custom filtering
recent = trace.filter(lambda m: m.timestamp > some_cutoff)

# Merge traces
other_trace = Trace[Mark]().add(some_mark)
merged = trace.merge(other_trace)  # Sorted by timestamp

# Slicing
last_10 = trace.slice(-10)  # Last 10 marks
first_5 = trace.slice(0, 5)  # First 5 marks
```

## Domain Field

The `domain` field categorizes marks for frontend routing and filtering:

- `"navigation"`: Route changes, page navigation
- `"portal"`: Portal expansions/collapses (Context Perception)
- `"chat"`: Chat messages, turns
- `"edit"`: K-Block edits, mutations
- `"system"`: System-level events (default)

## Integration with Existing Systems

### ChatMark → Mark

The existing `ChatMark` type can remain for backward compatibility, but new code
should use the unified `Mark` with `domain="chat"`:

```python
# Old pattern (still works)
from services.chat.witness import ChatMark
chat_mark = ChatMark(
    session_id="sess-123",
    turn_number=1,
    user_message="Hello",
    assistant_response="Hi!",
)

# New pattern (recommended)
from services.witness import Mark, Stimulus, Response
chat_mark = Mark(
    origin="chat_session",
    domain="chat",
    stimulus=Stimulus(kind="prompt", content="Hello"),
    response=Response(kind="text", content="Hi!"),
    metadata={
        "session_id": "sess-123",
        "turn_number": 1,
    },
)
```

### Portal Marks

Portal marks already use the unified Mark type:

```python
from services.witness.portal_marks import mark_portal_expansion

# This already creates Mark with domain="portal"
await mark_portal_expansion(
    file_path="foo.py",
    edge_type="imports",
    portal_path=["imports", "pathlib"],
    depth=2,
    observer_archetype="developer",
)
```

### Walk → Trace

`Walk` is for N-Phase workflows with Forest bindings. `Trace` is simpler:

```python
# Use Walk when you need:
# - N-Phase workflow tracking (SENSE → ACT → REFLECT)
# - Forest plan binding (root_plan: PlanPath)
# - Participant Umwelts
from services.witness import Walk

# Use Trace when you need:
# - Simple mark collection
# - Domain filtering
# - Generic mark history
from services.witness import Trace
```

## Serialization

Marks serialize to/from dictionaries with full domain preservation:

```python
mark = Mark(origin="test", domain="chat")
data = mark.to_dict()
# {
#   "id": "mark-abc123...",
#   "origin": "test",
#   "domain": "chat",  # ← Preserved
#   ...
# }

restored = Mark.from_dict(data)
assert restored.domain == "chat"
```

## Immutability

Both `Mark` and `Trace` are immutable:

```python
# Marks are frozen
mark = Mark(origin="test")
mark.domain = "chat"  # ✗ Raises FrozenInstanceError

# Traces return new instances
trace1 = Trace[Mark]()
trace2 = trace1.add(mark)
assert len(trace1) == 0  # Original unchanged
assert len(trace2) == 1  # New trace has mark
```

## Type Safety

Both types are fully typed with mypy support:

```python
from services.witness import Mark, Trace

# Generic over mark type
trace: Trace[Mark] = Trace()
mark: Mark = Mark(origin="test")
trace = trace.add(mark)  # ✓ Type-safe

# Filter preserves type
filtered: Trace[Mark] = trace.filter_by_domain("chat")
```

## Testing

See comprehensive test suites:
- `services/witness/_tests/test_unified_mark.py` - Mark domain support
- `services/witness/_tests/test_trace.py` - Trace operations

Both test files demonstrate all supported operations with examples.
