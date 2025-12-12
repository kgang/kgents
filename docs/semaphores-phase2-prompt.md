# Agent Semaphores Phase 2: Flux Integration

> *Use this prompt with `/hydrate` to continue implementing Agent Semaphores.*

---

## Context for the Implementing Agent

You are implementing **Phase 2 of Agent Semaphores** — integrating the Purgatory Pattern into FluxAgent's event loop. Phase 1 (core types) is complete with 78 tests.

**Before writing any code, read these documents in order:**

1. **`plans/agents/semaphores.md`** — The plan file (updated with Phase 1 status)
2. **`plans/_epilogues/2025-12-12-semaphores-phase1.md`** — Previous session notes
3. **`impl/claude/agents/flux/semaphore/__init__.py`** — Phase 1 exports
4. **`impl/claude/agents/flux/agent.py`** — FluxAgent (you'll modify `_process_flux`)
5. **`impl/claude/agents/flux/perturbation.py`** — Perturbation pattern (you'll reuse this)

---

## Phase 1 Recap: What's Already Implemented

```python
from agents.flux.semaphore import (
    SemaphoreToken,      # The Red Card - return to yield
    ReentryContext,      # The Green Card - injected as Perturbation
    Purgatory,           # The waiting room - crash-safe storage
    SemaphoreReason,     # 6-way taxonomy
)

# Creating a semaphore (agent returns this)
token = SemaphoreToken(
    reason=SemaphoreReason.APPROVAL_NEEDED,
    frozen_state=pickle.dumps(my_state),
    original_event=event,
    prompt="Delete 47 records?",
    options=["Approve", "Reject"],
)

# Purgatory operations
await purgatory.save(token)                          # Eject
reentry = await purgatory.resolve(token.id, input)   # Returns ReentryContext
await purgatory.cancel(token.id)                     # Cancel
purgatory.list_pending()                             # List pending tokens
```

---

## Phase 2 Goal: Wire Semaphores into FluxAgent

When an agent's `invoke()` returns a `SemaphoreToken`, FluxAgent should:
1. **Detect** the token (it's not a normal result)
2. **Eject** the event to Purgatory
3. **Continue** processing other events (no head-of-line blocking)
4. **Resume** when human resolves (via Perturbation re-injection)

```
FluxAgent._process_flux()
    │
    ▼
for event in merged_source:
    result = await inner.invoke(event)
    │
    ├── if isinstance(result, SemaphoreToken):
    │       # EJECT: Save to Purgatory, emit None, continue
    │       await purgatory.save(result)
    │       continue  # Don't emit result, don't block
    │
    └── else:
            # Normal result
            await emit_output(result)

# When human resolves:
reentry = await purgatory.resolve(token_id, human_input)
perturbation = create_perturbation(reentry, priority=200)
await flux._perturbation_queue.put(perturbation)

# FluxAgent processes perturbation, calls agent.resume()
```

---

## Files to Create

```
impl/claude/agents/flux/semaphore/
├── mixin.py             # SemaphoreCapable protocol + SemaphoreMixin
└── _tests/
    └── test_mixin.py    # Tests for mixin
```

### mixin.py

```python
from typing import Any, Protocol, TypeVar

B = TypeVar("B")  # Output type

class SemaphoreCapable(Protocol[B]):
    """
    Protocol for agents that can yield semaphores.

    Agents implementing this protocol:
    1. May return SemaphoreToken from invoke() to yield
    2. Must implement resume() to handle reentry

    The resume() method receives:
    - frozen_state: bytes from the original SemaphoreToken
    - human_input: What the human provided

    And returns the final result that would have been returned
    by the original invoke() if it hadn't yielded.
    """

    async def resume(self, frozen_state: bytes, human_input: Any) -> B:
        """
        Resume processing after human provides context.

        Args:
            frozen_state: Pickled agent state from before ejection
            human_input: Context provided by human

        Returns:
            The result that invoke() would have returned
        """
        ...


class SemaphoreMixin:
    """
    Mixin that adds semaphore yielding capability to agents.

    Provides helper methods for:
    - Creating SemaphoreTokens with proper state freezing
    - Implementing resume() with state restoration

    Example:
        class MyAgent(Agent[str, str], SemaphoreMixin):
            async def invoke(self, input: str) -> str | SemaphoreToken:
                if needs_human_input(input):
                    return self.yield_semaphore(
                        reason=SemaphoreReason.CONTEXT_REQUIRED,
                        prompt="Which environment?",
                        options=["staging", "production"],
                        state={"input": input, "step": 3},
                    )
                return process(input)

            async def resume(self, frozen_state: bytes, human_input: Any) -> str:
                state = self.restore_state(frozen_state)
                return process_with_context(state["input"], human_input)
    """

    def yield_semaphore(
        self,
        reason: SemaphoreReason,
        prompt: str,
        state: dict[str, Any],
        *,
        options: list[str] | None = None,
        severity: str = "info",
        original_event: Any = None,
        deadline: datetime | None = None,
        escalation: str | None = None,
    ) -> SemaphoreToken[Any]:
        """
        Create a SemaphoreToken to yield control to human.

        Args:
            reason: Why yielding (taxonomy)
            prompt: Human-readable question
            state: Agent state to freeze (will be pickled)
            options: Suggested responses
            severity: "info" | "warning" | "critical"
            original_event: The event that triggered this
            deadline: Optional auto-escalation deadline
            escalation: Who to escalate to after deadline

        Returns:
            SemaphoreToken to return from invoke()
        """
        import pickle
        return SemaphoreToken(
            reason=reason,
            frozen_state=pickle.dumps(state),
            original_event=original_event,
            prompt=prompt,
            options=options or [],
            severity=severity,
            deadline=deadline,
            escalation=escalation,
        )

    def restore_state(self, frozen_state: bytes) -> dict[str, Any]:
        """Restore state from frozen bytes."""
        import pickle
        return pickle.loads(frozen_state)
```

---

## Files to Modify

### impl/claude/agents/flux/agent.py

Add these changes to FluxAgent:

1. **Add Purgatory instance** (or accept via config)
2. **Detect SemaphoreToken** in `_process_flux()`
3. **Handle ReentryContext** in perturbation processing

```python
# In FluxAgent.__post_init__ or config:
self._purgatory: Purgatory = Purgatory()

# In _process_flux(), after getting result from inner.invoke():
result = await self.inner.invoke(input_data)

# NEW: Check if agent yielded a semaphore
if isinstance(result, SemaphoreToken):
    # Eject to Purgatory
    result.original_event = input_data  # Preserve original event
    await self._purgatory.save(result)

    # Emit pheromone for observability
    await self._emit_pheromone(
        "semaphore_ejected",
        {"token_id": result.id, "reason": result.reason.value},
    )

    # Don't emit result, continue to next event
    continue

# Existing code for normal results...
```

4. **Handle ReentryContext in perturbation processing**:

```python
# When processing perturbation, check if it's a ReentryContext
if isinstance(input_data, ReentryContext):
    # This is a resolved semaphore, call resume()
    if hasattr(self.inner, 'resume'):
        result = await self.inner.resume(
            input_data.frozen_state,
            input_data.human_input,
        )
    else:
        # Agent doesn't support resume, log warning
        await self._emit_pheromone(
            "semaphore_resume_failed",
            {"token_id": input_data.token_id, "error": "no resume method"},
        )
        continue
```

---

## Test Requirements

### test_mixin.py

- `SemaphoreMixin.yield_semaphore()` creates valid token
- `SemaphoreMixin.restore_state()` unpickles correctly
- Agent implementing `SemaphoreCapable` can yield and resume

### test_flux_integration.py (new file)

- FluxAgent detects `SemaphoreToken` from `inner.invoke()`
- Token is saved to Purgatory
- Stream continues (no blocking)
- Resolving token creates `Perturbation`
- Perturbation processed, `resume()` called
- Result from `resume()` emitted to output

### Integration test

```python
async def test_full_semaphore_flow():
    """Full round-trip: invoke → yield → eject → resolve → resume → result."""

    class ApprovalAgent(Agent[str, str], SemaphoreMixin):
        async def invoke(self, input: str) -> str | SemaphoreToken:
            if input.startswith("delete"):
                return self.yield_semaphore(
                    reason=SemaphoreReason.APPROVAL_NEEDED,
                    prompt=f"Confirm: {input}?",
                    state={"input": input},
                    options=["Approve", "Reject"],
                )
            return f"processed: {input}"

        async def resume(self, frozen_state: bytes, human_input: Any) -> str:
            state = self.restore_state(frozen_state)
            if human_input == "Approve":
                return f"deleted: {state['input']}"
            return f"cancelled: {state['input']}"

    flux = FluxAgent(inner=ApprovalAgent())
    purgatory = flux._purgatory

    # Start flux
    source = async_iter(["hello", "delete records", "world"])
    results = []

    async for result in flux.start(source):
        results.append(result)

    # Should have processed non-semaphore events
    assert "processed: hello" in results
    assert "processed: world" in results

    # Semaphore should be in purgatory
    pending = purgatory.list_pending()
    assert len(pending) == 1
    assert pending[0].prompt == "Confirm: delete records?"

    # Resolve semaphore
    reentry = await purgatory.resolve(pending[0].id, "Approve")

    # Inject as perturbation
    perturbation = create_perturbation(reentry, priority=200)
    await flux._perturbation_queue.put(perturbation)

    # Resume and get result
    # (need to process perturbation somehow - may need flux running or invoke())
```

---

## Technical Constraints

1. **Import SemaphoreToken** in agent.py (add to imports)
2. **Don't modify token.py or purgatory.py** unless necessary
3. **Preserve existing Flux behavior** for non-semaphore results
4. **Pheromone signals** for observability: `semaphore_ejected`, `semaphore_resumed`
5. **Type safety**: `SemaphoreCapable` should work with mypy

---

## Validation Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Type check
uv run mypy agents/flux/semaphore/ agents/flux/agent.py

# Run semaphore tests
uv run pytest agents/flux/semaphore/_tests/ -v

# Full validation
uv run mypy .
uv run pytest -m "not slow" -q
```

---

## Exit Criteria

| Metric | Target |
|--------|--------|
| New tests | 20+ |
| Mypy errors | 0 |
| Existing flux tests | Still pass |
| Integration test | Full round-trip works |

---

## Questions to Resolve

1. **Purgatory ownership**: Should Purgatory be on FluxAgent or passed via config?
2. **Resume without flux running**: How do we process ReentryContext perturbation if flux has stopped?
3. **Multiple semaphores**: Test that multiple pending semaphores work correctly

---

*"The gaucho sees the red card. The stream flows on. The purgatory holds. This is Phase 2."*
