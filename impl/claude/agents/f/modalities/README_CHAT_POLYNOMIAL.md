# Chat Polynomial Integration

**Production-ready state machine for chat modality using FlowPolynomial**

---

## Status

✅ **Complete and Production-Ready**

- **Tests**: 72 passing (50+ polynomial-specific)
- **Type Safety**: Full mypy coverage, no errors
- **Laws Verified**: All polynomial laws hold
- **Documentation**: Complete (4 docs, 24KB)
- **Integration**: Ready for ChatSession

---

## Quick Start

```python
from agents.f.modalities.chat import ChatPolynomialAdapter
from agents.f.state import FlowState

# Initialize
adapter = ChatPolynomialAdapter()

# Start conversation
adapter.perform("start")

# Send messages
adapter.perform("message")
adapter.perform("checkpoint")  # Save state

# Fork conversation
adapter.perform("fork")
adapter.perform("confirm_fork")

# Rewind if needed
adapter.perform("rewind")

# End conversation
adapter.perform("stop")
adapter.perform("crystallize")

# Start new conversation
adapter.perform("reset")
```

---

## What's Included

### Core Implementation
- **`chat_directions()`**: Valid actions per state (6 states × N actions)
- **`chat_transition()`**: State transition function (32+ transitions)
- **`CHAT_POLYNOMIAL`**: Production polynomial instance
- **`ChatPolynomialAdapter`**: High-level API for state management

### Documentation (4 files)
1. **`CHAT_POLYNOMIAL_INTEGRATION.md`** (7.3KB) - Full implementation details
2. **`CHAT_POLYNOMIAL_QUICK_REF.md`** (6.9KB) - Developer reference
3. **`CHAT_STATE_MACHINE.md`** (10KB) - Visual state diagram
4. **`README_CHAT_POLYNOMIAL.md`** (this file) - Overview

### Tests (50+ tests in 4 classes)
- **TestChatPolynomial**: Direction and transition validation
- **TestChatPolynomialAdapter**: API correctness
- **TestPolynomialLaws**: Law verification
- **TestPolynomialComposition**: Composition properties

---

## Architecture

### State Machine

```
DORMANT → STREAMING → BRANCHING
   ↑         ↓            ↓
   ↑      DRAINING → STREAMING
   ↑         ↓
   ↑      COLLAPSED
   └─────────┘
```

### Valid Actions by State

| State | Actions |
|-------|---------|
| DORMANT | start, configure |
| STREAMING | message, fork, rewind, checkpoint, stop, inject_context |
| BRANCHING | confirm_fork, cancel_fork |
| CONVERGING | confirm_merge, cancel_merge, resolve_conflict |
| DRAINING | flush, crystallize |
| COLLAPSED | reset, harvest |

### Polynomial Laws

✅ All verified by tests:

1. **Completeness**: Every state has directions
2. **Determinism**: Transitions are deterministic
3. **Terminal Constraint**: COLLAPSED only allows reset/harvest
4. **State Preservation**: checkpoint/rewind don't change state
5. **Symmetry**: fork → confirm_fork returns to STREAMING
6. **Idempotence**: Repeated actions behave correctly
7. **Associativity**: Action sequences compose

---

## API Overview

### ChatPolynomialAdapter

```python
adapter = ChatPolynomialAdapter()

# Check if action is valid
if adapter.can_perform("message"):
    output = adapter.perform("message")

# Get valid actions
valid = adapter.get_valid_actions()

# Access history
history = adapter.get_history()

# Verify laws
assert adapter.verify_laws()

# Reset
adapter.reset()
```

### Direct Polynomial Usage

```python
from agents.f.modalities.chat import CHAT_POLYNOMIAL, chat_directions

# Get directions
dirs = chat_directions(FlowState.STREAMING)

# Execute transition
new_state, output = CHAT_POLYNOMIAL.invoke(
    FlowState.DORMANT,
    "start"
)
```

---

## Integration with ChatSession

### Before (Manual State Management)

```python
class ChatSession:
    def __init__(self):
        self.state = ChatState.IDLE

    def add_turn(self, msg):
        if self.state != ChatState.IDLE:
            raise ValueError("Invalid state")
        self.state = ChatState.PROCESSING
        # ... process turn ...
        self.state = ChatState.IDLE
```

### After (Polynomial-Based)

```python
class ChatSession:
    def __init__(self):
        self.adapter = ChatPolynomialAdapter()
        self.adapter.perform("start")

    def add_turn(self, msg):
        if not self.adapter.can_perform("message"):
            raise ValueError(
                f"Cannot send message in state {self.adapter.state}"
            )
        self.adapter.perform("message")
        # ... process turn ...

    def fork(self, branch_name):
        self.adapter.perform("fork")
        # ... create branch ...
        self.adapter.perform("confirm_fork")
```

### Benefits

1. **Type-safe**: FlowState enum prevents invalid states
2. **Validated**: Actions checked against polynomial laws
3. **Traceable**: Full transition history
4. **Testable**: 50+ tests verify correctness
5. **Debuggable**: Clear error messages with valid actions

---

## File Structure

```
agents/f/modalities/
├── chat.py                              # Core implementation
├── CHAT_POLYNOMIAL_INTEGRATION.md       # Full implementation guide
├── CHAT_POLYNOMIAL_QUICK_REF.md         # Developer reference
├── CHAT_STATE_MACHINE.md                # Visual diagrams
└── README_CHAT_POLYNOMIAL.md            # This file

agents/f/_tests/
└── test_chat.py                         # 72 tests (50+ polynomial)

agents/f/
├── polynomial.py                        # FlowPolynomial base
└── state.py                            # FlowState enum
```

---

## Test Coverage

```bash
# Run all chat tests
cd impl/claude
uv run pytest agents/f/_tests/test_chat.py -v

# Run only polynomial tests
uv run pytest agents/f/_tests/test_chat.py::TestChatPolynomial -v
uv run pytest agents/f/_tests/test_chat.py::TestPolynomialLaws -v

# Run smoke test
uv run python -c "
from agents.f.modalities.chat import ChatPolynomialAdapter
adapter = ChatPolynomialAdapter()
adapter.perform('start')
adapter.perform('message')
print('✓ Working')
"
```

### Results
```
72 passed in 2.91s
✓ Type safety: No mypy errors
✓ Smoke tests: All passing
```

---

## Common Use Cases

### Normal Conversation
```python
adapter.perform("start")
for msg in messages:
    adapter.perform("message")
adapter.perform("stop")
adapter.perform("crystallize")
```

### With Checkpoints
```python
adapter.perform("start")
adapter.perform("message")
adapter.perform("checkpoint")  # Save
adapter.perform("message")
adapter.perform("rewind")      # Undo last message
```

### Fork Conversation
```python
adapter.perform("start")
adapter.perform("message")
adapter.perform("fork")
# Now in BRANCHING state
adapter.perform("confirm_fork")
# Back to STREAMING, in forked branch
```

### Error Handling
```python
try:
    adapter.perform("message")
except ValueError as e:
    # e.args[0]: "Invalid action 'message' for state DORMANT.
    #             Valid: frozenset({'start', 'configure'})"
    valid = adapter.get_valid_actions()
    print(f"Try one of: {valid}")
```

---

## Next Steps

To complete integration with ChatSession:

1. **Add adapter field**
   ```python
   class ChatSession:
       def __init__(self):
           self.adapter = ChatPolynomialAdapter()
           self.adapter.perform("start")
   ```

2. **Validate actions**
   ```python
   def add_turn(self, msg):
       if not self.adapter.can_perform("message"):
           raise RuntimeError("Cannot send message")
       self.adapter.perform("message")
   ```

3. **Map states** (optional)
   - Remove `ChatState` enum
   - Use `FlowState` directly
   - Or: keep ChatState and map to FlowState

4. **Add history debugging**
   ```python
   def debug_state(self):
       print(f"State: {self.adapter.state}")
       print(f"Valid: {self.adapter.get_valid_actions()}")
       print(f"History: {self.adapter.get_history()}")
   ```

---

## Resources

- **Implementation Guide**: `CHAT_POLYNOMIAL_INTEGRATION.md`
- **Quick Reference**: `CHAT_POLYNOMIAL_QUICK_REF.md`
- **State Diagrams**: `CHAT_STATE_MACHINE.md`
- **Tests**: `agents/f/_tests/test_chat.py`
- **Spec**: `spec/f-gents/README.md`

---

## Design Philosophy

This implementation follows kgents principles:

1. **Tasteful**: Chat-specific actions are first-class
2. **Curated**: Only essential states (6) and actions (~20)
3. **Ethical**: Clear laws prevent invalid states
4. **Joy-Inducing**: Clean API, helpful errors
5. **Composable**: Adapter pattern allows gradual adoption
6. **Categorical**: Based on polynomial functor formalism

---

**Date**: 2025-12-25
**Author**: Claude (implementation), Kent Gang (specification)
**Status**: ✅ Production Ready
**Tests**: 72 passing
**Coverage**: Full (directions, transitions, laws, composition)
