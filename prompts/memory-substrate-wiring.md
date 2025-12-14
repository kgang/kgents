# IMPLEMENT: Memory Substrate Wiring

> *"The architecture is compositionally sound—all pieces exist. The gap is in the runtime initialization pipeline."*

**Date**: 2025-12-13
**Entry Phase**: IMPLEMENT (continuing from RESEARCH)
**Entropy Budget**: 0.10 (full allocation)

---

## ATTACH

/hydrate

You are entering **IMPLEMENT** phase of the N-Phase Cycle (AD-005).

Previous phase (RESEARCH) created these handles:
- Epilogue: `plans/_epilogues/2025-12-13-fever-overlay-trigger-wiring.md`
- Track B complete: FeverOverlay trigger wiring (100%)
- Track A researched: Memory Substrate integration points mapped

---

## Context from Previous Phase

### Track A Research Summary

The RESEARCH phase mapped these integration points for Memory Substrate wiring:

**1. MemoryNode Initialization** (`protocols/agentese/contexts/self_.py`)
- `_substrate: Any = None` (line 132)
- `_compactor: Any = None` (line 135)
- `_router: Any = None` (line 134)
- Factory: `create_self_resolver(substrate=, compactor=, router=)` passes to MemoryNode

**2. SharedSubstrate API** (`agents/m/substrate.py`)
- `allocate(agent_id, quota, lifecycle)` → Creates Allocation with MemoryQuota
- `promote(agent_id)` → Evaluates CrystalPolicy, transfers to DedicatedCrystal
- `demote(agent_id, compress_ratio)` → Applies compression, returns to shared
- `compact(allocation)` → Checks CompactionTrigger, applies resolution loss
- `stats()` → Returns allocation count, dedicated count, pattern totals

**3. Compactor Integration** (`agents/m/compaction.py`)
- `compact(crystal, target_id, pressure, force)` → Evaluates policy, applies ratio
- `compact_allocation(allocation, force)` → Calculates pressure, delegates
- Policy thresholds: pressure=0.8, critical=0.95, min_resolution=0.1

**4. Router/Stigmergy** (`agents/m/routing.py`)
- `CategoricalRouter` takes `PheromoneField` in constructor
- `route(task)` → Senses gradients, makes decision
- Adjunction: deposit ⊣ route

**5. Ghost Lifecycle Gap** (`infra/ghost/lifecycle.py`)
- `LifecycleAwareCache` exists with TTL support
- But `MemoryNode.engram` uses raw filesystem, not LifecycleAwareCache
- Need to wire: engram operations → LifecycleAwareCache

---

## Your Mission

Wire the real SharedSubstrate, Compactor, and Router into MemoryNode for self.memory.* AGENTESE paths.

### Priority Order

**P0: Wire Substrate to MemoryNode**
1. Update `create_self_resolver()` to accept/create real `SharedSubstrate[Any]`
2. Update `MemoryNode.__init__()` to store substrate reference
3. Wire `self.memory.allocate` to call `substrate.allocate()`
4. Wire `self.memory.substrate_stats` to call `substrate.stats()`

**P1: Wire Compactor**
1. Create default `Compactor` with sensible `CompactionPolicy`
2. Pass to `create_self_resolver(compactor=)`
3. Wire `self.memory.compact` to call `compactor.compact_allocation()`

**P2: Wire Router (if time permits)**
1. Need `PheromoneField` from somewhere (may need to defer)
2. Wire `self.memory.route` to call `router.route()`

**P3: Ghost Lifecycle Integration (stretch)**
1. Update `MemoryNode.engram` to use `LifecycleAwareCache`
2. Allocations should sync to Ghost cache on create/update

---

## Principles Alignment

This phase emphasizes:
- **Composable** (P1): Substrate, Compactor, Router compose orthogonally
- **AGENTESE** (P6): No view from nowhere; paths require observer
- **Courage Imperative**: Wire real code, not more mocks

From `spec/principles.md`:
> *"The agent does not describe work. The agent DOES work."*

---

## Implementation Strategy

```python
# Current (mocks or None):
resolver = create_self_resolver()  # All None

# Target (real instances):
substrate = SharedSubstrate[Any](global_crystal=MemoryCrystal())
compactor = Compactor(policy=CompactionPolicy())
# router requires PheromoneField - may defer

resolver = create_self_resolver(
    substrate=substrate,
    compactor=compactor,
)
```

The key insight: substrate + compactor are self-contained. Router needs field which is external dependency.

---

## Exit Criteria

- [ ] `create_self_resolver()` accepts and passes real `SharedSubstrate`
- [ ] `self.memory.allocate` creates real allocations in substrate
- [ ] `self.memory.compact` triggers real compaction with pressure calculation
- [ ] `self.memory.substrate_stats` returns real substrate metrics
- [ ] Tests pass (current: 13,205+)
- [ ] Mypy strict (0 errors)
- [ ] Epilogue written documenting integration

---

## Constraints

- **Minimal Output**: Every aspect returns single logical unit
- **Observer Required**: Always pass Umwelt to methods
- **Law Enforcement**: Identity/associativity on composition
- **Backward Compatible**: Existing `create_self_resolver()` callers should still work (None defaults)

---

## Continuation Imperative

Upon completing this phase, generate the prompt for **QA** phase:
- Verify substrate integration with property-based tests
- Test allocation lifecycle: create → use → compact → stats
- Test pressure thresholds trigger compaction correctly

The form is the function.

---

## Synergy Note

Track B (FeverOverlay) is now wired. When substrate compaction happens at high pressure, the FeverOverlay will automatically surface via EventBus. The Accursed Share becomes visible at both layers:
- **Data layer**: Compaction is purposeful forgetting
- **Visual layer**: FeverOverlay shows entropy state

---

*"To read is to invoke. There is no view from nowhere."*
