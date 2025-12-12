# Agent Semaphores Implementation Prompt

> *Use this prompt with `/hydrate` to begin implementing Agent Semaphores (The Rodizio Pattern).*

---

## Context for the Implementing Agent

You are implementing **Agent Semaphores** for kgents—a human-in-the-loop coordination pattern that allows FluxAgents to yield control until humans provide context. This implements the **Rodizio Pattern** (named after Brazilian steakhouse service).

**Before writing any code, read these documents in order:**

1. **`plans/agents/semaphores.md`** — The plan file (READ FIRST)
2. **`spec/principles.md`** — Design principles (constraints on ALL work)
3. **`plans/principles.md`** — Forest protocol (session coordination)
4. **`impl/claude/agents/flux/agent.py`** — FluxAgent implementation
5. **`impl/claude/agents/flux/perturbation.py`** — Perturbation pattern (you'll reuse this)

---

## The Core Insight

Traditional human-in-the-loop: ask question → block → wait → continue. This is the **interrupt model**.

Agent Semaphores embrace the **yield model** via the **Purgatory Pattern**:

```
Flux Stream        Purgatory         Human           Flux Stream
┌──────────┐      ┌──────────┐      ┌────────┐      ┌──────────┐
│ Event A  │──────│  Eject   │      │        │      │ Context  │
│ needs    │ ──→  │  & Save  │ ──→  │ Review │ ──→  │ Re-inject│
│ human    │      │ state    │      │ & Flip │      │ as Perturb│
└──────────┘      └──────────┘      └────────┘      └──────────┘
     │                                                    │
     │               ┌──────────┐                         │
     └──────────────▶│ Event B  │◀────────────────────────┘
                     │ proceeds │
                     └──────────┘

Key: Stream CONTINUES. Blocked event waits in Purgatory, not in flux.
```

**Why Purgatory?** Two problems with naive generator encoding:
1. **Python generators cannot be pickled** — server restart loses stack frame
2. **Head-of-line blocking** — one semaphore blocks entire Flux stream

**Resolution**: We RETURN tokens (not YIELD), eject state to Purgatory, and re-inject via existing Perturbation mechanism.

---

## Implementation Scope: Phase 1 Only

**This prompt is for Phase 1: SemaphoreToken, ReentryContext, and Purgatory.**

Do NOT attempt Phases 2-5 in this session. Phase 1 is foundational.

**Goal**: Define core types and the Purgatory store. Tests demonstrate token creation and resolution.

**Exit Criteria**:
- `SemaphoreToken` can be created with reason, prompt, options
- `ReentryContext` carries frozen state and human input
- `Purgatory` can save, resolve, cancel, list, and recover tokens
- Tests demonstrate the round-trip: create → save → resolve → reentry

---

## File Structure to Create

```
impl/claude/agents/flux/
├── semaphore/
│   ├── __init__.py           # Exports: SemaphoreToken, ReentryContext, Purgatory, SemaphoreReason
│   ├── token.py              # SemaphoreToken dataclass
│   ├── reentry.py            # ReentryContext dataclass
│   ├── reason.py             # SemaphoreReason enum
│   ├── purgatory.py          # Purgatory store
│   └── _tests/
│       ├── __init__.py
│       ├── test_token.py
│       ├── test_reentry.py
│       └── test_purgatory.py
```

---

## Type Definitions

### SemaphoreReason (reason.py)

```python
from enum import Enum

class SemaphoreReason(Enum):
    """Why the agent yielded to human."""
    APPROVAL_NEEDED = "approval_needed"      # Sensitive action requiring explicit approval
    CONTEXT_REQUIRED = "context_required"    # Agent needs info only human has
    SENSITIVE_ACTION = "sensitive_action"    # Privacy/security implications
    AMBIGUOUS_CHOICE = "ambiguous_choice"    # Multiple valid interpretations
    RESOURCE_DECISION = "resource_decision"  # Resource allocation needed
    ERROR_RECOVERY = "error_recovery"        # Error occurred, human guidance needed
```

### SemaphoreToken (token.py)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
import uuid

from .reason import SemaphoreReason

R = TypeVar("R")  # Required context type

@dataclass
class SemaphoreToken(Generic[R]):
    """
    The Red Card. Return this from an agent to flip red.

    When a FluxAgent's inner.invoke() RETURNS this (not yields!),
    the event is ejected to Purgatory until human provides context.

    The Rodizio Pattern:
    - Agent returns SemaphoreToken → FluxAgent detects → Eject to Purgatory
    - Stream continues flowing (no head-of-line blocking)
    - Human resolves → ReentryContext injected as Perturbation
    - Agent.resume() completes processing
    """

    # Identity
    id: str = field(default_factory=lambda: f"sem-{uuid.uuid4().hex[:8]}")

    # Why yielded
    reason: SemaphoreReason = SemaphoreReason.CONTEXT_REQUIRED

    # State preservation (CRITICAL: this is what makes it crash-safe)
    frozen_state: bytes = b""  # Pickled agent state at ejection
    original_event: Any = None  # The event that triggered this semaphore

    # Type hint for expected human input
    required_type: type[R] | None = None

    # Optional timing
    deadline: datetime | None = None  # Auto-escalate after this
    escalation: str | None = None     # Who to escalate to

    # UI metadata (for CLI/TUI display)
    prompt: str = ""                  # Human-readable question
    options: list[str] = field(default_factory=list)  # Suggested responses
    severity: str = "info"            # "info" | "warning" | "critical"

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    cancelled_at: datetime | None = None

    @property
    def is_pending(self) -> bool:
        """Check if token is still awaiting resolution."""
        return self.resolved_at is None and self.cancelled_at is None

    @property
    def is_resolved(self) -> bool:
        """Check if token was resolved (not cancelled)."""
        return self.resolved_at is not None

    @property
    def is_cancelled(self) -> bool:
        """Check if token was cancelled."""
        return self.cancelled_at is not None
```

### ReentryContext (reentry.py)

```python
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

R = TypeVar("R")

@dataclass
class ReentryContext(Generic[R]):
    """
    The Green Card. Injected back into Flux as high-priority Perturbation.

    When a human resolves a semaphore, this carries:
    1. The frozen state from before ejection
    2. The human's input/decision
    3. Reference back to original event

    The agent's resume() method receives this to complete processing.
    """

    token_id: str
    """ID of the resolved SemaphoreToken."""

    frozen_state: bytes
    """Pickled state from before ejection. Agent unpickles to restore context."""

    human_input: R
    """What the human provided. Type should match token.required_type."""

    original_event: Any
    """The event that triggered the semaphore. For audit/debugging."""

    def __post_init__(self) -> None:
        """Validate reentry context."""
        if not self.token_id:
            raise ValueError("ReentryContext requires token_id")
```

### Purgatory (purgatory.py)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .token import SemaphoreToken
from .reentry import ReentryContext

@dataclass
class Purgatory:
    """
    The waiting room for ejected events.

    Crash-resistant: survives server restarts via D-gent backing (Phase 3).
    For Phase 1, in-memory only.

    Key insight: We pickle DATA (frozen_state), not GENERATORS.
    This is what makes Purgatory crash-safe when D-gent is wired.

    Usage:
        purgatory = Purgatory()

        # Agent returns SemaphoreToken, FluxAgent detects and ejects
        await purgatory.save(token)

        # Stream continues, human eventually resolves
        reentry = await purgatory.resolve(token.id, human_input)

        # reentry is injected as Perturbation
        # Agent.resume() receives it
    """

    _pending: dict[str, SemaphoreToken] = field(default_factory=dict)
    _memory: Any = None  # D-gent memory adapter (Phase 3)

    async def save(self, token: SemaphoreToken) -> None:
        """
        Eject an event to Purgatory.

        Called by FluxAgent when inner.invoke() returns SemaphoreToken.
        """
        self._pending[token.id] = token
        if self._memory:
            await self._persist()

    async def resolve(
        self,
        token_id: str,
        human_input: Any
    ) -> ReentryContext | None:
        """
        Resolve a pending semaphore with human-provided context.

        Returns ReentryContext to be injected as Perturbation.
        Returns None if token not found or already resolved.
        """
        token = self._pending.get(token_id)
        if token is None:
            return None
        if not token.is_pending:
            return None

        token.resolved_at = datetime.now()

        reentry = ReentryContext(
            token_id=token_id,
            frozen_state=token.frozen_state,
            human_input=human_input,
            original_event=token.original_event,
        )

        if self._memory:
            await self._persist()

        return reentry

    async def cancel(self, token_id: str) -> bool:
        """
        Cancel a pending semaphore. Event is discarded.

        Returns True if cancelled, False if not found or already resolved.
        """
        token = self._pending.get(token_id)
        if token is None:
            return False
        if not token.is_pending:
            return False

        token.cancelled_at = datetime.now()

        if self._memory:
            await self._persist()

        return True

    def get(self, token_id: str) -> SemaphoreToken | None:
        """Get a token by ID (any state)."""
        return self._pending.get(token_id)

    def list_pending(self) -> list[SemaphoreToken]:
        """List all pending (unresolved) semaphores."""
        return [t for t in self._pending.values() if t.is_pending]

    def list_all(self) -> list[SemaphoreToken]:
        """List all semaphores (any state)."""
        return list(self._pending.values())

    async def recover(self) -> list[SemaphoreToken]:
        """
        Recover pending semaphores after restart.

        Called during FluxAgent initialization (Phase 3).
        For Phase 1, returns empty list (no persistence).
        """
        if self._memory:
            state = await self._memory.load()
            if state:
                self._pending = state.get("pending", {})
        return self.list_pending()

    def clear(self) -> None:
        """Clear all tokens (for testing)."""
        self._pending.clear()

    async def _persist(self) -> None:
        """Persist state to D-gent (Phase 3)."""
        if self._memory:
            await self._memory.save({"pending": self._pending})
```

---

## Test Requirements

### test_token.py

Test SemaphoreToken:
- Creation with defaults generates valid ID
- `is_pending` True initially, False after resolve/cancel
- `is_resolved` and `is_cancelled` mutually exclusive
- Severity values: "info", "warning", "critical"
- Options list preserved
- Prompt string preserved
- frozen_state can hold pickled data

### test_reentry.py

Test ReentryContext:
- Requires token_id (ValueError if empty)
- Preserves frozen_state bytes
- Preserves human_input of various types
- Preserves original_event

### test_purgatory.py

Test Purgatory:
- `save()` stores token by ID
- `list_pending()` returns only pending tokens
- `resolve()` marks token resolved and returns ReentryContext
- `resolve()` returns None for already-resolved token
- `resolve()` returns None for unknown ID
- `cancel()` marks token cancelled
- `cancel()` returns False for already-resolved token
- `get()` returns token regardless of state
- `list_all()` returns all tokens
- `clear()` removes all tokens

### Integration Test (in test_purgatory.py)

```python
async def test_round_trip():
    """Full round-trip: create → save → resolve → reentry."""
    import pickle

    purgatory = Purgatory()

    # Simulate agent state at ejection
    agent_state = {"partial_result": "halfway there", "step": 3}
    frozen = pickle.dumps(agent_state)

    # Create token
    token = SemaphoreToken(
        reason=SemaphoreReason.APPROVAL_NEEDED,
        frozen_state=frozen,
        original_event="delete_records",
        prompt="Delete 47 records?",
        options=["Approve", "Reject", "Review"],
        severity="critical",
    )

    # Eject to purgatory
    await purgatory.save(token)
    assert len(purgatory.list_pending()) == 1

    # Human resolves
    reentry = await purgatory.resolve(token.id, "Approve")

    assert reentry is not None
    assert reentry.token_id == token.id
    assert reentry.human_input == "Approve"
    assert reentry.original_event == "delete_records"

    # Restore agent state
    restored = pickle.loads(reentry.frozen_state)
    assert restored["partial_result"] == "halfway there"
    assert restored["step"] == 3

    # Token no longer pending
    assert len(purgatory.list_pending()) == 0
    assert token.is_resolved
```

---

## Technical Constraints

From `spec/principles.md` and codebase conventions:

1. **Python 3.12+**: Use `Generic[R]` pattern, not `class Foo[R]:`
2. **Mypy strict**: 0 errors required. Run `uv run mypy .` after every file.
3. **Imports**: Prefer absolute (`from agents.flux.semaphore import ...`)
4. **Tests**: Place in `_tests/` subdirectory with `test_` prefix
5. **No bloat**: Keep files focused. Each file does one thing.
6. **Serialization**: `frozen_state` is bytes (pickle). Token itself should be JSON-serializable for Phase 3.

---

## Validation Commands

Run these after each file:

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Type check
uv run mypy agents/flux/semaphore/

# Run tests
uv run pytest agents/flux/semaphore/_tests/ -v

# Full validation (before committing)
uv run mypy .
uv run pytest -m "not slow" -q
```

---

## What NOT To Do

1. **Don't implement Flux integration** — That's Phase 2
2. **Don't implement D-gent persistence** — That's Phase 3
3. **Don't implement AGENTESE paths** — That's Phase 4
4. **Don't implement CLI** — That's Phase 5
5. **Don't use generators** — We RETURN tokens, not YIELD them
6. **Don't add timeouts by default** — Rodizio is INDEFINITE; deadline is opt-in
7. **Don't poll** — Purgatory doesn't poll; resolution is explicit

---

## Session Workflow

1. Read the required documents listed above
2. Create the directory structure
3. Implement `reason.py` first (simplest)
4. Implement `token.py` with tests
5. Implement `reentry.py` with tests
6. Implement `purgatory.py` with tests
7. Write the integration test
8. Run full validation
9. Do NOT commit — leave for human review

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Files created | 8 (4 impl + 4 test) |
| Mypy errors | 0 |
| Test coverage | All public methods tested |
| Integration test | Round-trip works |

---

## Questions to Consider While Implementing

1. Should `SemaphoreToken` have a `__hash__` for use in sets?
2. Should `Purgatory` emit events when tokens change state?
3. What happens if `resolve()` is called twice with different inputs?
4. Should cancelled tokens be removed from `_pending` or just marked?

Document your decisions in code comments.

---

## After Phase 1 Complete

Update `plans/agents/semaphores.md`:
- Change `progress: 0` to `progress: 20`
- Add session notes about what was implemented
- Update `last_touched` date

Update `plans/_status.md`:
- Mark Phase 1 as complete

---

*"The card speaks. The gaucho listens. The purgatory remembers. This is the protocol."*
