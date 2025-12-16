# Continuation: Gardener-Logos Phase 6 - Synergy Bus Integration

> *"The garden sends signals through the roots. The other jewels listen."*

## Context

**Plan:** `plans/gardener-logos-enactment.md`
**Progress:** 80% (Phases 1-5 complete)
**Next:** Phase 6 - Synergy Bus Integration

### What's Been Built (Phases 1-5)

| Phase | What | Tests |
|-------|------|-------|
| 1 | AGENTESE Integration | GardenerLogosNode, all aspects |
| 2 | CLI Implementation | `kgents garden`, `kgents plot`, `kgents tend` |
| 3 | Persistence | GardenStore (JSON + SQLite) |
| 4 | Session Unification | N-Phase sessions, lifecycle tracking |
| 5 | Prompt Delegation | `prompt.*` delegation, season-aware TextGRAD |

**Total:** 178 tests passing in `gardener_logos/`

### What Synergy Bus Already Has

The Synergy Bus infrastructure is **already built** (Foundation 4). Existing:
- `SynergyEventBus` with async emit, handler registration, result subscription
- `SynergyEvent` base class with jewel routing
- Handler pattern: `BaseSynergyHandler` with `success()`, `failure()`, `skip()`
- Factory functions for common events (Gestalt, Brain, Atelier, Coalition, Domain, Park)
- Existing Gardener events: `SESSION_STARTED`, `SESSION_COMPLETE`, `ARTIFACT_CREATED`, `LEARNING_RECORDED`

### What Phase 6 Adds

New **Garden-specific** events and handlers:
1. `SEASON_CHANGED` - When garden season transitions
2. `GESTURE_APPLIED` - When tending gesture completes
3. `PLOT_PROGRESS_UPDATED` - When plot progress changes
4. Cross-jewel handlers (Garden ↔ Brain, Garden ↔ Gestalt)

## Key Files to Read

```
impl/claude/protocols/synergy/events.py                    # Event types & factories
impl/claude/protocols/synergy/bus.py                       # SynergyEventBus singleton
impl/claude/protocols/synergy/handlers/base.py             # BaseSynergyHandler pattern
impl/claude/protocols/synergy/handlers/gestalt_brain.py    # Example handler
impl/claude/protocols/gardener_logos/garden.py             # GardenState.transition_season
impl/claude/protocols/gardener_logos/tending.py            # apply_gesture
impl/claude/protocols/gardener_logos/plots.py              # Plot.update_progress
plans/gardener-logos-enactment.md                          # Full plan (Phase 6 section)
```

## Deliverables from Plan

From `plans/gardener-logos-enactment.md` Phase 6:

- [ ] Garden event types (SEASON_CHANGED, GESTURE_APPLIED, PLOT_PROGRESS_UPDATED)
- [ ] Factory functions for garden events
- [ ] Event emission in garden.py, tending.py, plots.py
- [ ] GardenToBrainHandler (auto-capture garden state changes)
- [ ] GestaltToGardenHandler (update plots when Gestalt analyzes)
- [ ] Tests for synergy

## Design Pattern

### 1. Add Event Types to `events.py`

```python
# In SynergyEventType enum (already has GARDENER events)
SEASON_CHANGED = "season_changed"      # NEW
GESTURE_APPLIED = "gesture_applied"    # NEW
PLOT_PROGRESS_UPDATED = "plot_progress_updated"  # NEW

# Factory functions
def create_season_changed_event(
    garden_id: str,
    old_season: str,
    new_season: str,
    reason: str,
    correlation_id: str | None = None,
) -> SynergyEvent:
    """Create a garden season changed event."""
    return SynergyEvent(
        source_jewel=Jewel.GARDENER,
        target_jewel=Jewel.ALL,  # Broadcast to all jewels
        event_type=SynergyEventType.SEASON_CHANGED,
        source_id=garden_id,
        payload={
            "old_season": old_season,
            "new_season": new_season,
            "reason": reason,
        },
        correlation_id=correlation_id or str(uuid.uuid4()),
    )
```

### 2. Emit Events in Garden Operations

```python
# In garden.py, GardenState.transition_season()
async def transition_season(
    self,
    new_season: GardenSeason,
    reason: str,
    emit_event: bool = True,  # NEW
) -> None:
    old_season = self.season
    self.season = new_season

    if emit_event:
        from protocols.synergy import get_synergy_bus
        from protocols.synergy.events import create_season_changed_event

        event = create_season_changed_event(
            garden_id=self.garden_id,
            old_season=old_season.name,
            new_season=new_season.name,
            reason=reason,
        )
        await get_synergy_bus().emit(event)

# In tending.py, apply_gesture()
# After successful gesture application:
if emit_event and result.accepted:
    event = create_gesture_applied_event(
        garden_id=garden.garden_id,
        verb=gesture.verb.name,
        target=gesture.target,
        success=result.success,
        synergies=result.synergies_triggered,
    )
    await get_synergy_bus().emit(event)
```

### 3. Create Garden Handlers

**File:** `impl/claude/protocols/synergy/handlers/garden_brain.py`

```python
class GardenToBrainHandler(BaseSynergyHandler):
    """Auto-capture garden state changes to Brain."""

    @property
    def name(self) -> str:
        return "GardenToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        # Handle season changes and significant gestures
        if event.event_type == SynergyEventType.SEASON_CHANGED:
            return await self._handle_season_change(event)
        elif event.event_type == SynergyEventType.GESTURE_APPLIED:
            # Only capture significant gestures (not observe/wait)
            if event.payload.get("verb") not in {"OBSERVE", "WAIT"}:
                return await self._handle_gesture(event)
        return self.skip("Not a capturable garden event")
```

**File:** `impl/claude/protocols/synergy/handlers/gestalt_garden.py`

```python
class GestaltToGardenHandler(BaseSynergyHandler):
    """Update garden plots when Gestalt analyzes relevant modules."""

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        if event.event_type != SynergyEventType.ANALYSIS_COMPLETE:
            return self.skip("Not handling non-analysis events")

        # Find plots that match the analyzed path
        root_path = event.payload.get("root_path", "")
        garden = await self._get_current_garden()

        for plot in garden.plots.values():
            if self._plot_matches_path(plot, root_path):
                # Apply observe gesture with analysis summary
                gesture = observe(
                    plot.path,
                    f"Gestalt analysis: {event.payload.get('health_grade', '?')}"
                )
                await apply_gesture(garden, gesture)

        return self.success(f"Updated plots for {root_path}")
```

### 4. Register Handlers in Bus

```python
# In bus.py, _register_default_handlers()
def _register_default_handlers(bus: SynergyEventBus) -> None:
    # ... existing handlers ...

    # Wave 4: Garden synergy handlers
    from .handlers import GardenToBrainHandler, GestaltToGardenHandler

    bus.register(SynergyEventType.SEASON_CHANGED, GardenToBrainHandler())
    bus.register(SynergyEventType.GESTURE_APPLIED, GardenToBrainHandler())
    bus.register(SynergyEventType.ANALYSIS_COMPLETE, GestaltToGardenHandler())
```

## Implementation Order

1. **Event Types** - Add to `events.py` enum and create factory functions
2. **Event Emission** - Modify `garden.py` and `tending.py` to emit events
3. **GardenToBrainHandler** - Auto-capture season/gesture changes
4. **GestaltToGardenHandler** - Cross-jewel plot updates
5. **Registration** - Wire up handlers in `bus.py`
6. **Tests** - Unit tests for events and handlers

## Questions to Clarify

Before implementing, check:
- What granularity of gestures should trigger synergy events? (All? Only state-changing?)
- Should plot progress updates be broadcast to ALL jewels or just Brain?
- How should GestaltToGardenHandler find the "current garden"? (Session context? Global singleton?)
- Should SEASON_CHANGED emit synchronously (blocking) or async (fire-and-forget)?

## Success Criteria

Phase 6 is complete when:
- [x] Garden events flow through Synergy Bus
- [x] Brain auto-captures season transitions and significant gestures
- [x] Gestalt analysis updates relevant garden plots
- [x] Tests verify cross-jewel communication
- [x] Plan progress updated to 90%

## Implementation Summary (2025-12-16)

### Files Created
- `impl/claude/protocols/synergy/handlers/garden_brain.py` - GardenToBrainHandler
- `impl/claude/protocols/synergy/handlers/gestalt_garden.py` - GestaltToGardenHandler
- `impl/claude/protocols/synergy/_tests/test_garden_handlers.py` - 22 tests

### Files Modified
- `impl/claude/protocols/synergy/events.py` - Added Wave 4 event types and factories
- `impl/claude/protocols/synergy/handlers/__init__.py` - Exported new handlers
- `impl/claude/protocols/synergy/bus.py` - Registered Wave 4 handlers
- `impl/claude/protocols/gardener_logos/garden.py` - Added event emission in transition_season
- `impl/claude/protocols/gardener_logos/tending.py` - Added event emission in apply_gesture

### Test Results
- 22 new tests in `test_garden_handlers.py`
- 92 total synergy tests passing

---

*Created: 2025-12-16*
*Completed: 2025-12-16*
*Session: Phase 6 implemented - Synergy Bus Integration*
