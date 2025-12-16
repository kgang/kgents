# D-gent Integration: Phase 3-5 Continuation

**Plan**: `~/.claude/plans/binary-meandering-bunny.md`
**Status**: 85% complete
**Last Session**: 2025-12-16

## Context

The D-gent architecture rewrite is nearly complete:
1. ✅ 156 D-gent tests pass (datum, backends, router, bus, upgrader)
2. ✅ 26 Postgres backend tests pass with Docker
3. ✅ AGENTESE `self.data.*` and `self.bus.*` paths wired (27 tests)
4. ✅ L-gent, B-gent, K-gent persistence updated to new `DgentRouter` API
5. ✅ DGENT added to Jewel enum in synergy events
6. ✅ DataBus → Synergy Bus bridge implemented
7. ✅ Web types updated (synergy/types.ts, synergy/store.ts)

## What Was Done This Session

### Phase 3: Docker Postgres ✅
- **Fixed deadlock bug** in `PostgresBackend._ensure_schema()` - pool creation must happen outside the lock
- Verified 26 Postgres tests pass with Docker container
- No init script needed (backend self-initializes via `_ensure_schema()`)

### Phase 4: DataBus → Synergy Wiring ✅
- Added `DGENT` to `Jewel` enum
- Added 4 new event types: `DATA_STORED`, `DATA_DELETED`, `DATA_UPGRADED`, `DATA_DEGRADED`
- Created factory functions in `protocols/synergy/events.py`
- Implemented bridge in `protocols/agentese/contexts/self_bus.py`:
  - `wire_data_to_synergy()` - forwards DataBus events to SynergyBus
  - `reset_data_synergy_bridge()` - for testing
- Updated web types:
  - `web/src/components/synergy/types.ts` - Added dgent jewel and event types
  - `web/src/components/synergy/store.ts` - Added toast titles and type mappings

## Remaining Work

### Phase 5: Upgrader Observability (Priority: Low)

**Goal**: See tier promotions in UI.

**Tasks**:
1. Add AGENTESE path: `self.data.upgrader.status`
2. Emit synergy events from `AutoUpgrader.promote()` and `demote()`
3. Create visual indicator in Brain/Gestalt for data tier status

### Phase 6: Integration Tests (Priority: Medium)

**Goal**: End-to-end test of data flow.

**Tasks**:
1. Test: Store data → DataBus emits → SynergyBus receives → Toast appears
2. Test: Tier promotion → UPGRADE event → Brain receives
3. Property tests for the bridge

## Key Files Reference

| Component | Path |
|-----------|------|
| D-gent Router | `agents/d/router.py` |
| D-gent Backends | `agents/d/backends/*.py` |
| DataBus | `agents/d/bus.py` |
| AutoUpgrader | `agents/d/upgrader.py` |
| PostgresBackend | `agents/d/backends/postgres.py` (deadlock fix) |
| AGENTESE self.data | `protocols/agentese/contexts/self_data.py` |
| AGENTESE self.bus | `protocols/agentese/contexts/self_bus.py` |
| Synergy Events | `protocols/synergy/events.py` |
| Web Types | `web/src/components/synergy/types.ts` |

## Test Commands

```bash
# Run all D-gent tests (156 tests)
cd impl/claude
uv run pytest agents/d/_tests/test_datum.py agents/d/_tests/test_backends.py agents/d/_tests/test_router.py agents/d/_tests/test_bus.py agents/d/_tests/test_upgrader.py -v

# Test Postgres backend (26 tests, requires Docker)
docker compose up -d postgres
KGENTS_POSTGRES_URL="postgresql://kgents:kgents@127.0.0.1:5432/kgents" uv run pytest agents/d/_tests/test_postgres.py -v

# Test AGENTESE self.data paths (27 tests)
uv run pytest protocols/agentese/_tests/test_self_data_bus.py -v

# Test synergy events (includes new D-gent events)
uv run pytest protocols/synergy/_tests/ -v
```

## Continuation Prompt

```
Continue the D-gent Integration plan (binary-meandering-bunny.md).

Phases 3-4 are complete:
- Fixed Postgres deadlock bug (pool before lock)
- 26 Postgres tests pass with Docker
- DataBus → SynergyBus bridge wired
- Web types updated

Next: Phase 5 - Upgrader Observability
- Add self.data.upgrader.status AGENTESE path
- Emit synergy events on tier promotion/demotion
- Integration tests for data → UI flow
```
