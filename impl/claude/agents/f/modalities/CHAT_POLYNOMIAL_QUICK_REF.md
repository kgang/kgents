# Chat Polynomial Quick Reference

**For developers integrating FlowPolynomial with ChatSession**

---

## Import

```python
from agents.f.modalities.chat import (
    CHAT_POLYNOMIAL,
    ChatPolynomialAdapter,
    chat_directions,
    chat_transition,
)
from agents.f.state import FlowState
```

---

## State Machine

```
DORMANT ──start──→ STREAMING ──fork──→ BRANCHING
   ↑                    │                   │
   │                    │               confirm_fork
 reset              stop │               cancel_fork
   │                    │                   │
   │                    ↓                   ↓
COLLAPSED ←──crystallize── DRAINING   STREAMING
```

---

## Valid Actions Per State

| State | Valid Actions |
|-------|---------------|
| DORMANT | `start`, `configure` |
| STREAMING | `message`, `fork`, `rewind`, `checkpoint`, `stop`, `inject_context` |
| BRANCHING | `confirm_fork`, `cancel_fork` |
| CONVERGING | `confirm_merge`, `cancel_merge`, `resolve_conflict` |
| DRAINING | `flush`, `crystallize` |
| COLLAPSED | `reset`, `harvest` |

---

## ChatPolynomialAdapter API

### Check if action is valid
```python
adapter = ChatPolynomialAdapter()
adapter.state = FlowState.STREAMING

if adapter.can_perform("message"):
    # Action is valid for current state
    pass
```

### Get all valid actions
```python
valid_actions = adapter.get_valid_actions()
# → frozenset(["message", "fork", "rewind", "checkpoint", "stop", "inject_context"])
```

### Perform action (with validation)
```python
try:
    output = adapter.perform("message")
    # → {"event": "message_processed"}
except ValueError as e:
    # e.args[0]: "Invalid action 'X' for state Y. Valid: {...}"
    pass
```

### Access transition history
```python
history = adapter.get_history()
# → [(FlowState.DORMANT, "start", FlowState.STREAMING),
#     (FlowState.STREAMING, "message", FlowState.STREAMING), ...]
```

### Verify polynomial laws
```python
assert adapter.verify_laws()
```

### Reset to initial state
```python
adapter.reset()
assert adapter.state == FlowState.DORMANT
assert len(adapter.get_history()) == 0
```

---

## Direct Polynomial Usage

### Get directions for a state
```python
directions = chat_directions(FlowState.STREAMING)
# → frozenset(["message", "fork", "rewind", "checkpoint", "stop", "inject_context"])
```

### Execute transition
```python
new_state, output = chat_transition(FlowState.STREAMING, "fork")
# → (FlowState.BRANCHING, {"event": "fork_initiated"})
```

### Use polynomial directly
```python
new_state, output = CHAT_POLYNOMIAL.invoke(FlowState.DORMANT, "start")
# → (FlowState.STREAMING, {"event": "started", "ready": True})
```

---

## Integration Pattern

```python
from agents.f.modalities.chat import ChatPolynomialAdapter
from agents.f.state import FlowState

class ChatSession:
    def __init__(self):
        self.adapter = ChatPolynomialAdapter()
        # Start in DORMANT, transition to STREAMING
        self.adapter.perform("start")

    def add_turn(self, user_msg: str, assistant_msg: str):
        # Validate before executing
        if not self.adapter.can_perform("message"):
            raise RuntimeError(
                f"Cannot send message in state {self.adapter.state}"
            )

        # Transition state
        self.adapter.perform("message")

        # Execute turn logic
        # ...

    def fork(self, branch_name: str):
        if not self.adapter.can_perform("fork"):
            raise RuntimeError("Cannot fork in current state")

        self.adapter.perform("fork")
        # ... fork logic ...
        self.adapter.perform("confirm_fork")

    def checkpoint(self):
        if not self.adapter.can_perform("checkpoint"):
            raise RuntimeError("Cannot checkpoint in current state")

        self.adapter.perform("checkpoint")
        # ... checkpoint logic ...

    def stop(self):
        if not self.adapter.can_perform("stop"):
            raise RuntimeError("Cannot stop in current state")

        self.adapter.perform("stop")
        # ... cleanup ...
        self.adapter.perform("crystallize")
```

---

## Common Sequences

### Normal conversation flow
```python
adapter.perform("start")       # DORMANT → STREAMING
adapter.perform("message")     # STREAMING → STREAMING
adapter.perform("message")     # STREAMING → STREAMING
adapter.perform("checkpoint")  # STREAMING → STREAMING (saved)
adapter.perform("stop")        # STREAMING → DRAINING
adapter.perform("crystallize") # DRAINING → COLLAPSED
```

### Fork and merge
```python
adapter.perform("start")         # DORMANT → STREAMING
adapter.perform("message")       # STREAMING → STREAMING
adapter.perform("fork")          # STREAMING → BRANCHING
adapter.perform("confirm_fork")  # BRANCHING → STREAMING
# Now in forked branch, continue...
```

### Rewind after mistake
```python
adapter.perform("start")     # DORMANT → STREAMING
adapter.perform("message")   # STREAMING → STREAMING
adapter.perform("message")   # STREAMING → STREAMING
adapter.perform("rewind")    # STREAMING → STREAMING (undone)
```

### Cancel fork
```python
adapter.perform("start")        # DORMANT → STREAMING
adapter.perform("fork")         # STREAMING → BRANCHING
adapter.perform("cancel_fork")  # BRANCHING → STREAMING (no fork)
```

---

## Error Handling

```python
adapter = ChatPolynomialAdapter()

# Invalid action for current state
try:
    adapter.perform("message")  # DORMANT doesn't allow "message"
except ValueError as e:
    print(e)
    # "Invalid action 'message' for state FlowState.DORMANT.
    #  Valid: frozenset({'start', 'configure'})"

# Check before performing
if adapter.can_perform("start"):
    adapter.perform("start")
else:
    valid = adapter.get_valid_actions()
    print(f"Cannot start. Valid actions: {valid}")
```

---

## Laws to Remember

1. **Every state has directions**: `chat_directions(state)` never returns empty set
2. **Deterministic**: Same (state, action) always gives same result
3. **Terminal constraint**: COLLAPSED only allows `reset` and `harvest`
4. **State preservation**: `checkpoint` and `rewind` don't change state
5. **Symmetry**: `fork` → `confirm_fork` returns to STREAMING
6. **Idempotence**: Multiple `checkpoint` calls safe

---

## Testing

```python
def test_my_chat_feature():
    adapter = ChatPolynomialAdapter()

    # Start conversation
    adapter.perform("start")
    assert adapter.state == FlowState.STREAMING

    # Your test logic
    # ...

    # Verify laws still hold
    assert adapter.verify_laws()
```

---

## Debugging

```python
# Get transition history
history = adapter.get_history()
for old_state, action, new_state in history:
    print(f"{old_state.value} --[{action}]--> {new_state.value}")

# Check current state
print(f"Current state: {adapter.state.value}")

# Check what's allowed
print(f"Valid actions: {adapter.get_valid_actions()}")
```

---

**Full docs**: See `CHAT_POLYNOMIAL_INTEGRATION.md`
**Tests**: Run `pytest agents/f/_tests/test_chat.py -v`
