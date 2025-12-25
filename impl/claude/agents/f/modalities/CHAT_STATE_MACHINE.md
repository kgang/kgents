# Chat Flow State Machine

**Visual guide to FlowState transitions in chat modality**

---

## State Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CHAT FLOW STATE MACHINE                          │
└──────────────────────────────────────────────────────────────────────────┘

                              ┌──────────┐
                              │ DORMANT  │  Initial state
                              └────┬─────┘
                                   │
                            start  │  configure
                                   │     (stays in DORMANT)
                                   ↓
                    ┌──────────────────────────┐
                    │                          │
        ┌───────────┤      STREAMING          ├───────────┐
        │           │   (Main operational)     │           │
        │           └──────────────────────────┘           │
        │                    ↑  ↓                          │
        │     message ───────┘  └─────── checkpoint       │
        │     rewind                      inject_context   │
        │                                                   │
     fork                                                 stop
        │                                                   │
        ↓                                                   ↓
   ┌──────────┐                                      ┌──────────┐
   │BRANCHING │                                      │ DRAINING │
   └────┬─────┘                                      └────┬─────┘
        │                                                  │
confirm_fork                                          flush
cancel_fork                                          (stays in DRAINING)
        │                                                  │
        └────────────→ (back to STREAMING)                │
                                                    crystallize
                                                           │
                                                           ↓
                                                     ┌──────────┐
                                                     │COLLAPSED │  Terminal
                                                     └────┬─────┘
                                                          │
                                                    reset │  harvest
                                                          │  (stays)
                                                          ↓
                                                    (back to DORMANT)


        ┌──────────────┐
        │ CONVERGING   │  (Used for merge operations)
        └────┬─────────┘
             │
    confirm_merge
    cancel_merge
    resolve_conflict
             │
             ↓
        (back to STREAMING)
```

---

## State Descriptions

### DORMANT
**Purpose**: Initial state before conversation starts
**Valid Actions**: `start`, `configure`
**Typical Use**: Session initialization, configuration

```python
adapter = ChatPolynomialAdapter()
assert adapter.state == FlowState.DORMANT
adapter.perform("start")  # → STREAMING
```

### STREAMING
**Purpose**: Main operational state for conversation
**Valid Actions**: `message`, `fork`, `rewind`, `checkpoint`, `stop`, `inject_context`
**Typical Use**: Normal chat turns, context management

```python
# Main conversation loop
adapter.perform("message")     # User sends message
adapter.perform("message")     # Another turn
adapter.perform("checkpoint")  # Save state (stays in STREAMING)
adapter.perform("rewind")      # Undo last turn (stays in STREAMING)
```

### BRANCHING
**Purpose**: Fork conversation into alternative paths
**Valid Actions**: `confirm_fork`, `cancel_fork`
**Typical Use**: Exploring different conversation directions

```python
adapter.perform("fork")          # STREAMING → BRANCHING
# ... create branch ...
adapter.perform("confirm_fork")  # BRANCHING → STREAMING
```

### CONVERGING
**Purpose**: Merge branches or build consensus
**Valid Actions**: `confirm_merge`, `cancel_merge`, `resolve_conflict`
**Typical Use**: Combining forked conversations

```python
# When merging branches
adapter.perform("confirm_merge")    # → STREAMING
adapter.perform("resolve_conflict") # Handle conflicts (stays)
```

### DRAINING
**Purpose**: Flush remaining output before shutdown
**Valid Actions**: `flush`, `crystallize`
**Typical Use**: Graceful conversation termination

```python
adapter.perform("stop")        # STREAMING → DRAINING
adapter.perform("flush")       # Clear buffers (stays in DRAINING)
adapter.perform("crystallize") # Save and collapse
```

### COLLAPSED
**Purpose**: Terminal state after conversation ends
**Valid Actions**: `reset`, `harvest`
**Typical Use**: Extract metrics, restart

```python
adapter.perform("harvest")  # Get conversation artifacts (stays)
adapter.perform("reset")    # COLLAPSED → DORMANT (new conversation)
```

---

## Action Details

### Actions That Change State

| Action | From | To | Description |
|--------|------|-----|-------------|
| `start` | DORMANT | STREAMING | Begin conversation |
| `fork` | STREAMING | BRANCHING | Create branch |
| `confirm_fork` | BRANCHING | STREAMING | Finalize fork |
| `cancel_fork` | BRANCHING | STREAMING | Abort fork |
| `stop` | STREAMING | DRAINING | End conversation |
| `crystallize` | DRAINING | COLLAPSED | Finalize shutdown |
| `reset` | COLLAPSED | DORMANT | Restart |
| `confirm_merge` | CONVERGING | STREAMING | Finalize merge |
| `cancel_merge` | CONVERGING | STREAMING | Abort merge |

### Actions That Preserve State

| Action | State | Description |
|--------|-------|-------------|
| `configure` | DORMANT | Set configuration |
| `message` | STREAMING | Send/receive message |
| `rewind` | STREAMING | Undo turns |
| `checkpoint` | STREAMING | Save state |
| `inject_context` | STREAMING | Add context |
| `flush` | DRAINING | Clear buffers |
| `harvest` | COLLAPSED | Extract artifacts |
| `resolve_conflict` | CONVERGING | Handle merge conflicts |

---

## Common Flows

### Happy Path (Normal Conversation)
```
DORMANT ──start──→ STREAMING ──message──→ STREAMING
                       │                      │
                       │ (many turns)         │
                       ↓                      ↓
                   STREAMING ──stop──→ DRAINING ──crystallize──→ COLLAPSED
                                                                      │
                                                                    reset
                                                                      │
                                                                      ↓
                                                                  DORMANT
```

### With Checkpointing
```
STREAMING ──message──→ STREAMING ──checkpoint──→ STREAMING
   │                                                  │
   │                                              message
   │                                                  │
   └──────────────── rewind ────────────────────────┘
```

### Fork and Continue
```
STREAMING ──fork──→ BRANCHING ──confirm_fork──→ STREAMING (branch A)
                                                     │
                                                 message
                                                     │
                                                     ↓
                                                 STREAMING (continues)
```

### Merge Branches
```
STREAMING (branch A) ─┐
                      ├──→ CONVERGING ──confirm_merge──→ STREAMING (merged)
STREAMING (branch B) ─┘
```

---

## Error Cases

### Invalid Transitions
```python
adapter = ChatPolynomialAdapter()

# ❌ Cannot message before starting
adapter.perform("message")  # ValueError: Invalid action 'message' for state DORMANT

# ❌ Cannot fork from DORMANT
adapter.perform("fork")     # ValueError: Invalid action 'fork' for state DORMANT

# ✅ Must start first
adapter.perform("start")    # OK: DORMANT → STREAMING
adapter.perform("message")  # OK: STREAMING → STREAMING
```

### Recovery
```python
# If in COLLAPSED and want new conversation
if adapter.state == FlowState.COLLAPSED:
    adapter.perform("reset")    # → DORMANT
    adapter.perform("start")    # → STREAMING
    # Now ready for new conversation
```

---

## State Invariants

1. **DORMANT** is always reachable via `reset` from COLLAPSED
2. **STREAMING** is the only state that can transition to BRANCHING or DRAINING
3. **COLLAPSED** is a terminal state (only exits via `reset`)
4. **Every state** has at least one valid action
5. **Idempotent actions**: `checkpoint`, `flush`, `harvest` can be called multiple times
6. **Symmetric transitions**: fork/cancel_fork, confirm_fork return to same state

---

## Debugging States

```python
# Check current state
print(f"State: {adapter.state.value}")

# Check what's allowed
print(f"Valid: {adapter.get_valid_actions()}")

# Check how we got here
for old, action, new in adapter.get_history():
    print(f"{old.value} --[{action}]--> {new.value}")
```

---

**Implementation**: See `agents/f/modalities/chat.py`
**Tests**: See `agents/f/_tests/test_chat.py`
**Quick Ref**: See `CHAT_POLYNOMIAL_QUICK_REF.md`
