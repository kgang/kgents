# Chat PolicyTrace (Witness Walk) - Quick Reference

**Status**: ✅ Phase 1 Complete (2025-12-25)

## What Was Implemented

The Chat PolicyTrace integration creates a witnessed trace of every conversation turn.

### Files Created

1. **`services/chat/witness.py`**
   - `ChatMark`: Witness mark for a single chat turn
   - `ChatPolicyTrace`: Immutable trace of all marks in a session

2. **`services/chat/_tests/test_witness.py`**
   - 22 tests covering creation, serialization, and integration scenarios
   - All tests passing ✅

### Core Classes

#### ChatMark (frozen dataclass)

Records a single chat turn:

```python
@dataclass(frozen=True)
class ChatMark:
    session_id: str
    turn_number: int
    user_message: str
    assistant_response: str
    tools_used: tuple[str, ...] = ()
    constitutional_scores: PrincipleScore | None = None  # Optional for now
    evidence_snapshot: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""  # Why this response was generated
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

**Key Methods**:
- `to_dict()`: Serialize to JSON-compatible dict
- `from_dict(data)`: Deserialize from dict
- `summary`: One-line summary of the turn

#### ChatPolicyTrace (frozen dataclass)

Maintains the complete conversation witness trail:

```python
@dataclass(frozen=True)
class ChatPolicyTrace:
    session_id: str
    marks: tuple[ChatMark, ...] = ()
```

**Key Methods**:
- `add_mark(mark) -> ChatPolicyTrace`: Immutable append
- `get_marks() -> tuple[ChatMark, ...]`: Get all marks
- `get_mark(turn_number) -> ChatMark | None`: Get specific mark
- `get_recent_marks(n) -> tuple[ChatMark, ...]`: Get N most recent
- `to_dict()`: Serialize entire trace
- `from_dict(data)`: Deserialize trace

**Properties**:
- `turn_count`: Total number of turns
- `latest_mark`: Most recent mark (or None)

## Usage Examples

### Creating Marks

```python
from services.chat import ChatMark, ChatPolicyTrace

# Create a mark
mark = ChatMark(
    session_id="sess-123",
    turn_number=1,
    user_message="Hello, how are you?",
    assistant_response="I'm doing well, thanks!",
    reasoning="Friendly greeting response",
)

# With tools
mark_with_tools = ChatMark(
    session_id="sess-123",
    turn_number=2,
    user_message="What's the weather?",
    assistant_response="The weather is sunny, 72°F",
    tools_used=("weather_api",),
    evidence_snapshot={"api_latency_ms": 150},
    reasoning="Fetched weather data from external API",
)
```

### Building Traces

```python
# Start empty trace
trace = ChatPolicyTrace(session_id="sess-123")

# Add marks (immutable append pattern)
trace = trace.add_mark(mark1)
trace = trace.add_mark(mark2)
trace = trace.add_mark(mark3)

# Query trace
print(f"Total turns: {trace.turn_count}")
latest = trace.latest_mark
recent_3 = trace.get_recent_marks(3)
turn_2 = trace.get_mark(2)
```

### Persistence

```python
# Serialize to dict (for DB storage)
data = trace.to_dict()

# Deserialize from dict (from DB retrieval)
restored_trace = ChatPolicyTrace.from_dict(data)

# Round-trip preserves all data
assert restored_trace.session_id == trace.session_id
assert restored_trace.turn_count == trace.turn_count
```

## Integration with ChatSession (Phase 4)

The `ChatSession` class will integrate ChatPolicyTrace:

```python
class ChatSession:
    # ... existing fields ...
    witness_trace: ChatPolicyTrace = field(default_factory=...)

    def add_turn(self, user_msg: str, assistant_resp: str, **kwargs):
        # Create mark
        mark = ChatMark(
            session_id=self.session_id,
            turn_number=self.turn_count + 1,
            user_message=user_msg,
            assistant_response=assistant_resp,
            tools_used=kwargs.get("tools_used", ()),
            reasoning=kwargs.get("reasoning", ""),
            evidence_snapshot=self._capture_evidence_snapshot(),
        )

        # Add to trace
        self.witness_trace = self.witness_trace.add_mark(mark)

        # ... rest of turn logic ...
```

## Design Patterns Used

### 1. Immutable Append-Only Pattern

Both `ChatMark` and `ChatPolicyTrace` are frozen dataclasses. Mutations return new instances:

```python
# WRONG: This will error (frozen=True)
trace.marks = trace.marks + (new_mark,)  # AttributeError

# RIGHT: Immutable append returns new instance
trace = trace.add_mark(new_mark)
```

### 2. Writer Monad Pattern

`ChatPolicyTrace` follows the Writer monad pattern from `dp_bridge.PolicyTrace`:
- `pure(value)`: Lift a value into the trace context
- `bind(f)`: Chain operations while accumulating the log
- Append-only log accumulation

### 3. Evidence Snapshot Pattern

The `evidence_snapshot` dict captures context at turn time:

```python
mark = ChatMark(
    # ...
    evidence_snapshot={
        "context_length": 2500,
        "model": "claude-opus-4",
        "temperature": 0.7,
        "latency_ms": 1200,
        "tools_invoked": 2,
    }
)
```

This enables:
- Context replay: "What did the agent know at turn 5?"
- Performance tracking: "How long did turn 3 take?"
- Debugging: "What model was used for turn 7?"

## What's Next (Phase 4)

1. **Integrate with ChatSession**
   - Add `witness_trace: ChatPolicyTrace` field
   - Create mark on every turn
   - Persist trace with session

2. **Constitutional Scoring**
   - Compute `PrincipleScore` for each turn
   - Attach to `ChatMark.constitutional_scores`
   - Expose in API

3. **Trace Visualization**
   - Frontend component to display trace
   - Turn-by-turn replay
   - Evidence inspection

4. **Trace Analytics**
   - Aggregate metrics across traces
   - Identify patterns
   - Optimize based on evidence

## Testing

Run witness tests:

```bash
cd impl/claude
uv run pytest services/chat/_tests/test_witness.py -v
```

All 22 tests passing ✅

## Philosophy

> *"The proof IS the decision. The mark IS the witness."*

Every chat turn leaves a mark. Every mark joins a trace. Every trace tells the story of the conversation.

This isn't just logging—it's witnessed execution. The trace IS the proof that the conversation happened.

## Related Files

- `services/witness/mark.py`: Generic Mark pattern (this mimics it)
- `services/categorical/dp_bridge.py`: PolicyTrace pattern (Writer monad)
- `services/categorical/constitution.py`: PrincipleScore (for constitutional scoring)
- `spec/protocols/witness-primitives.md`: Specification
- `spec/protocols/chat-unified.md`: Chat protocol spec

---

**Implemented**: 2025-12-25
**Author**: Claude (with Kent's guidance)
**Status**: Phase 1 Complete ✅
