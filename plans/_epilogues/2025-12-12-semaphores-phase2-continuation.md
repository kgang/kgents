# Agent Semaphores Implementation Continuation

> *Use this prompt with `/hydrate` to continue implementing Agent Semaphores.*

---

## Session Summary

**Date**: 2025-12-12
**Progress**: Phase 1 complete, Phase 2 complete, Phase 3 ~80% complete

### What Was Completed

#### Phase 1 (100%) - Core Types
- `SemaphoreToken` with all fields
- `ReentryContext` dataclass
- `Purgatory` in-memory store
- `SemaphoreReason` enum
- All Phase 1 tests passing (49 tests)

#### Phase 2 (100%) - Flux Integration
- JSON serialization (`to_json`/`from_json`) on `SemaphoreToken`
- Deadline checking with `check_deadline()` and `is_voided` property
- `voided_at` field for expired tokens
- Pheromone emission in `Purgatory` (`purgatory.ejected`, `purgatory.resolved`, `purgatory.cancelled`, `purgatory.voided`)
- `SemaphoreMixin` and `SemaphoreCapable` protocol
- `flux_integration.py` with detection/ejection helpers
- Tests for all Phase 2 features (70 additional tests)
- **119 tests passing total**

#### Phase 3 (80%) - D-gent Integration
- `DurablePurgatory` class created in `durable.py`
- `PurgatoryState` TypedDict for persistence schema
- `create_durable_purgatory()` and `create_and_recover_purgatory()` factory functions
- Exports added to `__init__.py`
- **Remaining**: Fix mypy errors in test files, write DurablePurgatory tests

---

## Immediate Next Steps

### 1. Fix Remaining Type Errors
The test file `test_flux_integration.py` has type errors that need fixing:
- Line 479: `process_reentry_event` arg type mismatch (add `# type: ignore[arg-type]`)
- Line 409 in `test_token.py`: `data` needs type annotation

Run: `uv run mypy agents/flux/semaphore/`

### 2. Write DurablePurgatory Tests
Create `agents/flux/semaphore/_tests/test_durable.py`:
- Test persistence roundtrip (save → restart → recover)
- Test void_expired persists voided tokens
- Test schema version handling
- Use `VolatileAgent` as mock D-gent

### 3. Complete Phase 4 - AGENTESE Paths
Wire `self.semaphore.*` and `world.purgatory.*` paths:

```
self.semaphore.pending     → List pending tokens for this agent
self.semaphore.yield       → Create semaphore (agent-side)
world.purgatory.list       → List all pending tokens
world.purgatory.resolve    → Resolve a token
world.purgatory.cancel     → Cancel a token
```

Location: `impl/claude/protocols/agentese/contexts/`
- Add `SemaphoreNode` to `self_.py`
- Add `PurgatoryNode` to `world.py` or new file

### 4. Complete Phase 5 - CLI Integration
Add CLI commands in the existing CLI handler pattern:
```
kgents semaphore list      → List pending semaphores
kgents semaphore resolve   → Resolve a semaphore
kgents semaphore cancel    → Cancel a semaphore
kgents semaphore inspect   → Show details of a semaphore
```

---

## File Locations

```
impl/claude/agents/flux/semaphore/
├── __init__.py           # Exports all types (UPDATED)
├── token.py              # SemaphoreToken with JSON + deadline (UPDATED)
├── reentry.py            # ReentryContext (unchanged)
├── reason.py             # SemaphoreReason enum (unchanged)
├── purgatory.py          # Purgatory with pheromones (UPDATED)
├── mixin.py              # SemaphoreMixin + SemaphoreCapable (NEW)
├── flux_integration.py   # Flux integration helpers (NEW)
├── durable.py            # DurablePurgatory with D-gent (NEW)
└── _tests/
    ├── test_token.py         # Token tests + JSON + deadline (UPDATED)
    ├── test_reentry.py       # (unchanged)
    ├── test_purgatory.py     # (unchanged)
    ├── test_flux_integration.py  # New Phase 2 tests (NEW)
    └── test_durable.py       # TODO: Create this
```

---

## Validation Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Type check
uv run mypy agents/flux/semaphore/

# Run semaphore tests
uv run pytest agents/flux/semaphore/_tests/ -v

# Full validation
uv run mypy .
uv run pytest -m "not slow" -q
```

---

## Key Design Decisions Made

1. **voided_at field**: Tokens with expired deadlines get `voided_at` timestamp, making them non-pending. This is the "default on a promise" semantic.

2. **Pheromone signals**: Best-effort emission via callback. Signals: `purgatory.ejected`, `purgatory.resolved`, `purgatory.cancelled`, `purgatory.voided`.

3. **JSON serialization**: `frozen_state` is base64-encoded for JSON compatibility. Datetimes are ISO strings.

4. **DurablePurgatory**: Extends Purgatory (not composition) to override save/resolve/cancel with persistence.

5. **Type ignores in tests**: `process_reentry_event` expects `Agent[Any, Any]` but our mock agents don't implement the full protocol. Using `# type: ignore[arg-type]` is acceptable for tests.

---

## After Implementation Complete

Update `plans/agents/semaphores.md`:
- Change `progress: 20` to `progress: 100`
- Add session notes

Update `plans/_focus.md` if needed.

---

*"The card speaks. The gaucho listens. The purgatory remembers. This is the protocol."*
