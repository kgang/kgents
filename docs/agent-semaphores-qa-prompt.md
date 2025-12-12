# Agent Semaphores: QA & Integration Prompt

> *Use this prompt with `/hydrate` to complete Agent Semaphores integration.*

---

## Session Context

**Date**: 2025-12-12
**Status**: Phases 1-5 complete (138 tests), QA integration remaining
**Progress**: 95% → target 100%

### What Was Built

All core functionality is implemented and tested:

1. **Core Types** (`agents/flux/semaphore/`):
   - `SemaphoreToken` with JSON serialization, deadline checking
   - `ReentryContext` for resumption
   - `Purgatory` in-memory store with pheromone emission
   - `DurablePurgatory` with D-gent persistence
   - `SemaphoreMixin` and `SemaphoreCapable` protocol

2. **AGENTESE Paths** (`protocols/agentese/contexts/`):
   - `self.semaphore.pending/yield/status`
   - `world.purgatory.list/resolve/cancel/inspect/void_expired`

3. **CLI Handler** (`protocols/cli/handlers/semaphore.py`):
   - `kgents semaphore list/resolve/cancel/inspect/void`

---

## QA Tasks

### 1. AGENTESE Path Tests

Create `protocols/agentese/contexts/_tests/test_semaphore_paths.py`:

```python
# Test self.semaphore.pending returns empty list without purgatory
# Test self.semaphore.yield creates token when purgatory configured
# Test self.semaphore.status returns token details
# Test world.purgatory.list returns pending tokens
# Test world.purgatory.resolve requires token_id and human_input
# Test world.purgatory.cancel marks token as cancelled
# Test world.purgatory.inspect returns full token details
# Test world.purgatory.void_expired voids past-deadline tokens
# Test affordance filtering (admin vs non-admin)
```

### 2. CLI Handler Tests

Create `protocols/cli/handlers/_tests/test_semaphore.py`:

```python
# Test cmd_semaphore with --help
# Test cmd_semaphore list with empty purgatory
# Test cmd_semaphore list with pending tokens
# Test cmd_semaphore resolve with --input flag
# Test cmd_semaphore cancel
# Test cmd_semaphore inspect
# Test cmd_semaphore void
# Test --json output mode
# Test error cases (missing token_id, not found, etc.)
```

### 3. End-to-End Integration Test

Create `agents/flux/semaphore/_tests/test_e2e_integration.py`:

```python
# Test full rodizio flow:
# 1. FluxAgent processes event
# 2. Agent returns SemaphoreToken (needs approval)
# 3. Token ejected to DurablePurgatory
# 4. Stream continues processing other events
# 5. Human resolves via CLI/AGENTESE
# 6. ReentryContext injected as perturbation
# 7. Agent resumes with human input
```

### 4. Cortex Daemon Integration

Wire CLI handler to shared Purgatory:

**Current** (`protocols/cli/handlers/semaphore.py:188-206`):
```python
# Module-level purgatory instance (singleton for CLI session)
_purgatory_instance: Any = None

def _get_purgatory() -> Any:
    global _purgatory_instance
    if _purgatory_instance is None:
        _purgatory_instance = Purgatory()  # In-memory only!
    return _purgatory_instance
```

**Target**: Get from Cortex daemon context:
```python
def _get_purgatory() -> Any:
    from protocols.cli.hollow import get_cortex
    cortex = get_cortex()
    return cortex.purgatory  # Shared DurablePurgatory
```

---

## Validation Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Run all semaphore tests
uv run pytest agents/flux/semaphore/_tests/ -v

# Run AGENTESE context tests (when created)
uv run pytest protocols/agentese/contexts/_tests/test_semaphore_paths.py -v

# Run CLI handler tests (when created)
uv run pytest protocols/cli/handlers/_tests/test_semaphore.py -v

# Type check
uv run mypy agents/flux/semaphore/ protocols/cli/handlers/semaphore.py

# Full validation
uv run pytest -m "not slow" -q
```

---

## Files to Create

```
protocols/agentese/contexts/_tests/test_semaphore_paths.py  # AGENTESE path tests
protocols/cli/handlers/_tests/test_semaphore.py            # CLI handler tests
agents/flux/semaphore/_tests/test_e2e_integration.py       # End-to-end test
```

## Files to Modify

```
protocols/cli/handlers/semaphore.py   # Wire to Cortex daemon
```

---

## Success Criteria

- [ ] All AGENTESE path tests pass
- [ ] All CLI handler tests pass
- [ ] End-to-end integration test passes
- [ ] CLI reads from Cortex daemon's shared Purgatory
- [ ] mypy passes on all new/modified files
- [ ] Update `plans/agents/semaphores.md` to 100%
- [ ] Archive plan to `_archive/semaphores-v1.0-complete.md`

---

## Architecture Notes

### Purgatory Lifetime

The Purgatory instance should be:
1. Created by Cortex daemon on startup
2. Backed by D-gent (DurablePurgatory) for persistence
3. Recovered on restart via `create_and_recover_purgatory()`
4. Shared across CLI, AGENTESE, and Flux integration

### Pheromone Integration

Purgatory emits pheromones for monitoring:
- `purgatory.ejected` - Agent yielded, token in purgatory
- `purgatory.resolved` - Human provided input
- `purgatory.cancelled` - Token cancelled
- `purgatory.voided` - Token expired past deadline

These should be wired to the Cortex's signal system.

---

*"The card speaks. The gaucho listens. The purgatory remembers. This is the protocol."*
