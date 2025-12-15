# Skill: Turn Projector Pattern

> One Turn, many projections: render conversation moments to any target.

**Difficulty**: Easy
**Prerequisites**: Python dataclasses, basic JSON
**Files**: `impl/claude/protocols/api/turn.py`
**References**: `protocols/api/_tests/test_turn.py`, `weave/turn.py`

---

## Overview

A Turn is the atomic unit of conversation—a single speaker saying something at a point in time. The key insight is **holographic**: from one Turn, all views derive.

| Projector | Output | Use Case |
|-----------|--------|----------|
| `to_cli()` | Plain text | Terminal output |
| `to_tui()` | Rich Text | Interactive TUI |
| `to_json()` | Dict | API responses, storage |
| `to_json_str()` | JSON string | Wire format |
| `to_marimo()` | HTML | Notebook rendering |
| `to_sse()` | SSE format | Streaming responses |

---

## Create a Turn

```python
from protocols.api.turn import Turn

turn = Turn(
    speaker="kgent",
    content="Hello! How can I help you today?",
    timestamp=1734200000.0,
    meta={"confidence": 0.95},
)
```

**Fields**:
- `speaker`: Who is speaking (e.g., "user", "assistant", "kgent", "system")
- `content`: The message text
- `timestamp`: Unix timestamp (seconds since epoch)
- `meta`: Optional metadata dict (tool calls, citations, etc.)

**Note**: Turn is frozen (immutable). Once created, it cannot be modified.

---

## Projections

### to_cli() - Terminal Output

```python
print(turn.to_cli())
# Output: [kgent]: Hello! How can I help you today?
```

Simple `[speaker]: content` format.

### to_tui() - Rich Terminal

```python
from rich.console import Console

console = Console()
console.print(turn.to_tui())
# Output: Bold colored speaker, styled content
```

Speaker colors:
- `user` → cyan
- `assistant` → green
- `kgent` → magenta
- `system` → yellow

Falls back to `to_cli()` if Rich is not installed.

### to_json() - Dict Format

```python
data = turn.to_json()
# {
#     "speaker": "kgent",
#     "content": "Hello! How can I help you today?",
#     "timestamp": 1734200000.0,
#     "meta": {"confidence": 0.95}
# }
```

Use for API responses, logging, and storage.

### to_json_str() - JSON String

```python
json_str = turn.to_json_str()
# '{"speaker": "kgent", "content": "Hello!...", ...}'
```

Direct serialization convenience.

### to_marimo() - Notebook HTML

```python
html = turn.to_marimo()
# Returns styled HTML div with speaker-based colors
```

Renders as conversation bubbles:
- `user` → blue left border
- `assistant` → green left border
- `kgent` → purple left border
- `system` → yellow left border

### to_sse() - Server-Sent Events

```python
sse = turn.to_sse()
# "data: {\"speaker\": \"kgent\", ...}\n\n"
```

Follows SSE specification format for streaming APIs.

---

## Immutable Updates

Since Turn is frozen, use `with_meta()` to add metadata:

```python
turn2 = turn.with_meta(edited=True, reason="typo fix")
# Original turn unchanged
# turn2 has merged metadata
```

---

## Helper Methods

### summarize() - Short Preview

```python
turn.summarize(max_length=30)
# "[kgent]: Hello! How can I hel..."
```

Useful for logging and compact displays.

---

## Collection Helpers

### turns_to_markdown()

```python
from protocols.api.turn import turns_to_markdown

turns = [turn1, turn2, turn3]
md = turns_to_markdown(turns)
# **user**: What is the weather?
#
# **assistant**: It's sunny today.
#
# ...
```

### turns_to_json()

```python
from protocols.api.turn import turns_to_json

data = turns_to_json(turns)
# [{"speaker": "user", ...}, {"speaker": "assistant", ...}, ...]
```

---

## Full Example

```python
from protocols.api.turn import Turn, turns_to_markdown
import time

# Create conversation
conversation = [
    Turn(speaker="user", content="What time is it?", timestamp=time.time()),
    Turn(speaker="kgent", content="It's 3:42 PM.", timestamp=time.time()),
    Turn(speaker="user", content="Thanks!", timestamp=time.time()),
]

# Render to different targets
for turn in conversation:
    print(turn.to_cli())          # Terminal
    # turn.to_tui()               # Rich TUI
    # turn.to_marimo()            # Notebook
    # turn.to_sse()               # Streaming

# Bulk operations
print(turns_to_markdown(conversation))  # Markdown export
api_response = turns_to_json(conversation)  # JSON API
```

---

## Advanced: Weave Turn

For agents with causal structure, use `weave.turn.Turn`:

```python
from weave.turn import Turn, TurnType

turn = Turn.create_turn(
    content="Executing query...",
    source="agent-a",
    turn_type=TurnType.ACTION,
    state_pre={"status": "idle"},
    state_post={"status": "querying"},
    confidence=0.95,
    entropy_cost=0.02,
)

# Query turn properties
print(turn.is_effectful())        # True (ACTION type)
print(turn.requires_governance())  # True (ACTION requires review)
print(turn.is_observable())        # True (not THOUGHT)
```

**TurnTypes**:
- `SPEECH`: Utterance to user/agent
- `ACTION`: Tool call, side effect
- `THOUGHT`: Internal chain-of-thought (hidden by default)
- `YIELD`: Request for approval (blocks)
- `SILENCE`: Intentional non-action

---

## Verification

```bash
cd impl/claude
uv run pytest protocols/api/_tests/test_turn.py -v
uv run pytest protocols/api/_tests/test_turn_stress.py -v
```

---

## Common Pitfalls

### 1. Trying to Modify Frozen Turn

```python
turn.content = "new"  # FrozenInstanceError!
```

**Fix**: Use `with_meta()` or create a new Turn.

### 2. Missing Timestamp

```python
# Use time.time() for current timestamp
turn = Turn(speaker="user", content="Hi", timestamp=time.time())
```

### 3. Forgetting Meta is Optional

```python
# Meta defaults to empty dict
turn = Turn(speaker="user", content="Hi", timestamp=0.0)
print(turn.meta)  # {}
```

---

## Category Theory Note

Turn is a **product type** with projection morphisms. Each projector (`to_cli`, `to_tui`, etc.) is a **natural transformation** from the Turn functor to the target rendering category.

The holographic principle: all views derive from the same source data.

---

## Related Skills

- [reactive-primitives](reactive-primitives.md) - Observable state management
- [modal-scope-branching](modal-scope-branching.md) - Context windows
- [handler-patterns](handler-patterns.md) - CLI handlers that use Turn

---

## Source Reference

`impl/claude/protocols/api/turn.py:36-254`

---

*Skill created: 2025-12-14 | Wave 1 EDUCATE Phase*
