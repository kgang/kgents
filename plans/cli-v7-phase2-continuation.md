# CLI v7 Phase 2 Continuation: D-gent Persistence

**Handoff Date**: 2025-12-19
**Previous Work**: ConversationWindow, Summarizer, ChatMorpheusComposer integration
**Status**: ✅ **COMPLETE** — All deliverables implemented and tested (146 tests passing)

---

## Context

Phase 2 (Deep Conversation) is **100% COMPLETE**. All components implemented and tested:

### ✅ All Components Complete

| Component | Location | Tests | Purpose |
|-----------|----------|-------|---------|
| `ConversationWindow` | `services/conductor/window.py` | 48 | Bounded history, 4 strategies, context breakdown |
| `Summarizer` | `services/conductor/summarizer.py` | 19 | LLM-powered + fallback compression |
| `WindowPersistence` | `services/conductor/persistence.py` | 22 | D-gent save/load roundtrip |
| `FileEditGuard` | `services/conductor/file_guard.py` | 32 | Read-before-edit pattern (Phase 1) |
| `WorldFileNode` | `protocols/agentese/contexts/world_file.py` | 25 | AGENTESE file operations |
| **Total** | `services/conductor/` | **146** | Full conductor service |

### How It Works Now

```python
# ChatMorpheusComposer creates a window per session
window = composer.get_or_create_window(session)

# Window provides bounded context for LLM calls
context = window.get_context_messages()  # Returns at most max_turns messages

# Window is updated after each turn
composer.update_window(session, user_message, assistant_response)
```

---

## Remaining Work: D-gent Persistence

### Goal

Enable ConversationWindow state to persist across sessions via D-gent. This allows:
1. Session resumption with bounded history intact
2. Summary preservation across restarts
3. Integration with existing `ChatPersistence`

### Existing Patterns to Follow

**Reference**: `services/chat/persistence.py` — Already persists `ChatSession` to D-gent

```python
# Current pattern in ChatPersistence
class PersistedSession:
    turns: list[dict[str, Any]]  # Full turn history
    summary: str | None = None   # Optional summary (currently unused)

# D-gent storage pattern
datum = Datum.create(
    content=json.dumps(data).encode("utf-8"),
    id=f"chat:session:{session_id}",
    metadata={"node_path": ..., "observer_id": ...},
)
await dgent.put(datum)
```

### Implementation Plan

#### 1. Add Window State to PersistedSession

```python
# services/chat/persistence.py - Update PersistedSession

@dataclass
class PersistedSession:
    # ... existing fields ...

    # NEW: ConversationWindow state (Phase 2)
    window_state: dict[str, Any] | None = None  # From window.to_dict()
```

#### 2. Create WindowPersistence Class

```python
# services/conductor/persistence.py (NEW FILE)

class WindowPersistence:
    """
    Persist ConversationWindow state to D-gent.

    Integrates with ChatPersistence for unified session storage.
    """

    PREFIX = "conductor:window:"

    async def save_window(
        self,
        session_id: str,
        window: ConversationWindow,
    ) -> str:
        """Save window state to D-gent."""
        data = window.to_dict()
        datum = Datum.create(
            content=json.dumps(data).encode("utf-8"),
            id=f"{self.PREFIX}{session_id}",
        )
        return await self._dgent.put(datum)

    async def load_window(
        self,
        session_id: str,
    ) -> ConversationWindow | None:
        """Load window state from D-gent."""
        datum = await self._dgent.get(f"{self.PREFIX}{session_id}")
        if datum is None:
            return None
        data = json.loads(datum.content.decode("utf-8"))
        return ConversationWindow.from_dict(data)
```

#### 3. Wire into ChatMorpheusComposer

```python
# services/chat/composer.py - Update get_or_create_window

def get_or_create_window(self, session: ChatSession) -> ConversationWindow:
    if session_id not in self._windows:
        # Try to load from D-gent first
        if self._window_persistence:
            window = await self._window_persistence.load_window(session_id)
            if window:
                self._windows[session_id] = window
                return window

        # Create new window (existing logic)
        ...
```

#### 4. Add Auto-Save on Turn Completion

```python
# services/chat/composer.py - Update update_window

def update_window(self, session, user_message, assistant_response):
    window = self.get_or_create_window(session)
    window.add_turn(user_message, assistant_response)

    # Auto-save to D-gent (fire-and-forget or queued)
    if self._window_persistence:
        asyncio.create_task(
            self._window_persistence.save_window(session.session_id, window)
        )
```

### Test Requirements

Per the test strategy in `plans/cli-v7-implementation.md`:

| Type | Count | Examples |
|------|-------|----------|
| Type I (Unit) | 5 | `test_save_window`, `test_load_window`, `test_roundtrip` |
| Type II (Integration) | 3 | `test_persistence_with_dgent`, `test_resume_session_with_window` |
| Type III (Property) | 2 | `test_window_state_preserved_across_save_load` |

---

## ✅ COMPLETE — Next Steps

**Both Phase 1 and Phase 2 are complete!** The plan recommends continuing with:

### Option A: Phase 3 (Agent Presence) ⭐ RECOMMENDED
- Cursor states and activity indicators
- Joy-inducing visible agent presence
- Medium value, medium effort
- **Why**: Creates the "inhabited" feeling that makes kgents special

### Option B: Phase 4 (The REPL)
- Direct conversation with the lattice
- Builds on Phase 2's conversation infrastructure
- Medium value, low effort
- **Why**: Quick win, foundation already exists in repl.py

### Option C: Phase 5 (Collaborative Canvas)
- Full mind-map with multiplayer (Web)
- High value, high effort
- **Why**: Impressive showcase, but requires significant frontend work

---

## Key Files to Read

1. **Plan**: `plans/cli-v7-implementation.md` — Full implementation plan with patterns
2. **Window**: `services/conductor/window.py` — ConversationWindow implementation
3. **Existing Persistence**: `services/chat/persistence.py` — Pattern to follow
4. **D-gent**: `agents/d/` — D-gent router and backends
5. **Tests**: `services/conductor/_tests/` — Existing test patterns

---

## Voice Anchor

> *"Daring, bold, creative, opinionated but not gaudy"*

The persistence should be:
- **Simple**: Just save/load window state, don't over-engineer
- **Integrated**: Work with existing ChatPersistence, not parallel
- **Reliable**: Handle missing data gracefully (create new window)

---

## Commands to Verify

```bash
# Run tests
cd /Users/kentgang/git/kgents/impl/claude
uv run pytest services/conductor/_tests/ services/chat/_tests/ -v

# Type check
uv run mypy services/conductor/ services/chat/

# Full test suite
uv run pytest -q
```

---

*Continuation prompt for CLI v7 Phase 2 completion*
