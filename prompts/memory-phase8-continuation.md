# Memory Phase 8: Ghost Synchronization & Final Integration

> *"One truth across representations. The ghost is the allocation is the crystal."*

**Date**: 2025-12-13
**Entry Phase**: PLAN → DEVELOP
**Entropy Budget**: 0.06 (focused closure)

---

## Previous Session Outcome

### What Shipped (Phase 7: Crystallization Integration)

**Track A: CrystallizationEngine → Substrate**
- `SubstrateCrystallizer` bridges D-gent crystals to M-gent substrate
- `crystallize_allocation()`, `crystallize_on_promotion()`, `crystallize_with_compaction()`
- `CrystallizationEvent` for unified I-gent visualization

**Track B: CrystalReaper Integration**
- `ReaperIntegration` connects CrystalReaper to substrate allocations
- `reap_all()` for TTL-based expiration
- `get_expiring_soon()` for proactive lifecycle management

**Track D: AGENTESE Handler Wiring**
- Added `self.memory.reap` and `self.memory.expiring_soon` paths
- `_parse_timedelta()` helper for duration strings

**K-gent Enhancement**
- `KgentAllocationManager.crystallize()` returns allocation state
- `KgentCrystallizer` for dialogue/dream/soul crystallization

### Updated Metrics

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Total tests | 13,168 | 13,287 | +119 |
| Phase 7 tests | — | 17 | +17 |
| Memory status | 75% | 90% | +15% |
| Mypy errors | 0 | 0 | — |

### Files Created (Phase 7)

- `impl/claude/agents/m/crystallization_integration.py` (450 lines)
- `impl/claude/agents/m/_tests/test_crystallization_integration.py` (17 tests)

---

## Current Forest State

### Active Trees
- **self/memory** (90%): Crystallization complete. Ghost sync remains.
- **agents/k-gent** (97%): Substrate integration complete.
- **void/entropy** (95%): FeverOverlay complete.

### What Remains (Memory to 100%)

1. **Ghost ↔ Substrate Bidirectional Sync**: The final coherence layer
2. **Dashboard Crystallization Widget**: Show CrystallizationEvents in SubstrateScreen
3. **Integration smoke test**: Full AGENTESE → real storage roundtrip

---

## Next Cycle: Phase 8 Tracks

### Track A: Ghost ↔ Substrate Sync (IMPLEMENT)

**Intent**: When allocation stores pattern → create ghost entry. When ghost updates → touch allocation. When reaper evicts → remove ghost.

**Files to modify**:
- `impl/claude/infra/ghost/lifecycle.py` - Add allocation sync hooks
- `impl/claude/agents/m/crystallization_integration.py` - Add ghost sync to ReaperIntegration
- `impl/claude/agents/k/memory_allocation.py` - Emit ghost entries on store

**Key Insight**: The ghost cache and substrate allocation are two views of the same truth. Bidirectional sync maintains coherence.

```python
# When allocation stores
async def store_working(self, concept_id, content, embedding):
    success = await self._working.store(concept_id, content, embedding)
    if success and self._ghost_cache:
        await self._ghost_cache.set(
            f"alloc:{self._working.agent_id}:{concept_id}",
            content,
            policy=self._working.lifecycle,
        )
    return success

# When ghost updates
async def on_ghost_access(self, key: str, allocation: Allocation):
    allocation._record_access()

# When reaper evicts
async def reap_allocation(self, allocation):
    # ... existing reap logic ...
    if self._ghost_cache:
        await self._ghost_cache.invalidate_prefix(f"alloc:{allocation.agent_id}:")
```

**Tests**:
- Store via allocation → ghost entry exists
- Ghost access → allocation last_accessed updated
- Reap allocation → ghost entries removed

**Effort**: Medium

---

### Track B: Dashboard Crystallization Widget (IMPLEMENT)

**Intent**: Show CrystallizationEvents in SubstrateScreen for I-gent visualization.

**Files to modify**:
- `impl/claude/agents/i/screens/substrate.py` - Add CrystallizationWidget
- `impl/claude/agents/i/widgets/crystallization.py` - New widget file

**Widget Design**:
```python
@dataclass
class CrystallizationView:
    """View model for crystallization events."""
    timestamp: str
    event_type: str  # crystallize, reap, promote
    agent_id: str
    crystal_id: str | None
    patterns_affected: int
    resolution_loss: float
    reason: str

class CrystallizationTimelineWidget(Widget):
    """Timeline of crystallization events."""

    def render(self) -> str:
        # Show recent crystallization events as timeline
        pass
```

**Effort**: Low-Medium

---

### Track C: Integration Smoke Test (QA)

**Intent**: Full roundtrip test from AGENTESE path to real storage and back.

**Test Flow**:
```python
async def test_full_memory_lifecycle():
    # 1. Create logos with real substrate
    substrate = create_substrate()
    logos = create_logos(substrate=substrate)

    # 2. Allocate via AGENTESE
    result = await logos.invoke("self.memory.allocate", observer,
                                agent_id="smoke_test",
                                human_label="Integration test")

    # 3. Store patterns (via KgentAllocationManager)
    manager = await create_kgent_allocation(substrate)
    await manager.store_working("concept_1", "test", [1.0, 0.0])

    # 4. Check stats via AGENTESE
    stats = await logos.invoke("self.memory.substrate_stats", observer)
    assert stats["total_patterns"] > 0

    # 5. Crystallize
    crystallizer = create_substrate_crystallizer(engine, substrate)
    event = await crystallizer.crystallize_allocation(...)
    assert event.crystal_id is not None

    # 6. Reap expired
    result = await logos.invoke("self.memory.reap", observer)

    # 7. Verify ghost sync (if wired)
```

**Effort**: Low

---

## Synergy Map

```
Track A (Ghost Sync)
   └── enables → Unified cache invalidation
   └── enables → Holistic lifecycle management
   └── requires → Ghost cache infrastructure (exists)

Track B (Dashboard Widget)
   └── enables → Visual monitoring of crystallization
   └── requires → Track A (events to display)

Track C (Smoke Test)
   └── validates → Full integration
   └── requires → Track A + B (optional)

Recommended Sequence: A → C → B
- Ghost sync first (completes coherence)
- Smoke test second (validates integration)
- Widget last (visualization polish)
```

---

## Execution Protocol

### Phase Sequence

```
PLAN (this) → DEVELOP (ghost sync contracts)
→ IMPLEMENT (bidirectional sync) → TEST (integration)
→ REFLECT (epilogue + memory 100%)
```

### Success Criteria

By session end:
- [ ] Track A complete: Ghost ↔ Substrate bidirectional sync
- [ ] Track C complete: Integration smoke test passing
- [ ] Track B started: Crystallization widget skeleton
- [ ] Tests passing (current: 13,287 → target: 13,310+)
- [ ] Mypy strict (0 errors)
- [ ] Memory status: 90% → 100%
- [ ] Epilogue written

---

## Key Files Reference

### Ghost Infrastructure
- `impl/claude/infra/ghost/cache.py` - LifecycleAwareCache
- `impl/claude/infra/ghost/lifecycle.py` - LifecyclePolicy, CrystalReaper

### Substrate
- `impl/claude/agents/m/substrate.py` - SharedSubstrate, Allocation
- `impl/claude/agents/m/crystallization_integration.py` - ReaperIntegration

### K-gent
- `impl/claude/agents/k/memory_allocation.py` - KgentAllocationManager

### AGENTESE
- `impl/claude/protocols/agentese/contexts/self_.py` - MemoryNode

---

## Invocation

```bash
/hydrate
```

Then:
1. Read ghost cache infrastructure
2. Design sync protocol
3. Implement Track A
4. Write integration smoke test (Track C)

---

*"The ghost is the shadow of the allocation. When one moves, the other follows."*
