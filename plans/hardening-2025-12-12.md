---
path: hardening-2025-12-12
status: active
progress: 0
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Focused hardening sprint prioritizing tight devex feedback loops.
  Emphasis on working products over completion metrics.
---

# Hardening Sprint: 2025-12-12

> *"The best ship is not the biggest ship, but the one that sails."*

## Guiding Principle

**Tight feedback loops over completion metrics.** Each action should result in something that works better. Avoid bureaucratic "completeness" — prefer working CLI commands, passing tests, and real user value.

---

## Priority 1: K-gent Hardening (High Impact, Quick Wins)

**Goal**: Shore up test coverage for the 684-line `refinements.py` and active modules

### 1.1 refinements.py Test Coverage (NEW TESTS NEEDED)

The module has 3 domains with complex code but no dedicated test file:

| Component | Lines | Test Coverage | Priority |
|-----------|-------|---------------|----------|
| SoulPathResolver | ~170 | Minimal (indirectly via soul tests) | HIGH |
| GracefulDegradation | ~40 | None | HIGH |
| FractalExpander | ~80 | None | MEDIUM |
| HolographicConstitution | ~140 | None | MEDIUM |

**Tasks**:
1. Create `impl/claude/agents/k/_tests/test_refinements.py`
2. Test SoulPathResolver:
   - `resolve()` happy paths for all registered paths
   - Observer-aware behavior (architect vs poet vs anonymous)
   - Unknown path handling (error response)
   - Exception handling in handlers
3. Test GracefulDegradation:
   - `record_error()` incrementing
   - Auto-degradation after 3 errors
   - `restore()` behavior
   - `is_degraded()` checks
4. Test FractalExpander:
   - Basic expansion to max_depth
   - Branching factor limits
   - Soul-influenced expansion
5. Test HolographicConstitution:
   - Article retrieval
   - Eigenvector-weighted lookup
   - Holographic search resonance

### 1.2 hypnagogia.py Edge Cases

**Existing**: 734 lines in test file with good coverage
**Gaps identified**:
- No explicit timeout/cancellation tests for dream cycles
- Missing tests for `_extract_patterns_llm` (requires mock)
- No malformed input tests

**Tasks**:
1. Add timeout edge case tests
2. Add mock LLM tests for pattern extraction
3. Add malformed pattern input tests

### 1.3 garden.py Edge Cases

**Existing**: 777 lines in test file
**Gaps identified**:
- `cross_pollinate` tested but edge cases missing
- `staleness_decay` edge cases
- `auto_plant_from_dialogue` needs more coverage

**Tasks**:
1. Add boundary tests for staleness decay
2. Test cross-pollination with empty/malformed entries
3. Test dialogue extraction with edge case inputs

---

## Priority 2: Memory Module Wiring (Medium, Enables Future Work)

**Goal**: Push `self/memory` from 30% → 60% with real working code

### 2.1 AGENTESE Path Wiring

The foundations exist in `impl/claude/agents/d/`:
- `crystal.py` - StateCrystal, CrystallizationEngine, CrystalReaper
- `modal_scope.py` - ModalScope (44 tests)
- `pulse.py` - Pulse, VitalityAnalyzer (35 tests)

**Tasks**:
1. Add `self.memory.*` paths to AGENTESE context (`impl/claude/protocols/agentese/contexts/self_.py`):
   - `self.memory.crystallize` → CrystallizationEngine.crystallize
   - `self.memory.resume` → Crystal restore
   - `self.memory.cherish` → Set pinned=True
   - `self.memory.manifest` → Ghost cache read
   - `self.memory.engram` → Ghost cache write
2. Wire to existing Ghost cache infrastructure
3. Add 10-15 integration tests

### 2.2 Ghost + Crystal Integration

Connect the memory hierarchy layers:
```
Hot (ContextWindow) → Warm (StateCrystal) → Cold (Ghost)
```

**Tasks**:
1. Implement `crystallize` handler that calls CrystallizationEngine
2. Implement `resume` handler that restores from crystal
3. Wire TTL-based reaping to void.entropy

---

## Priority 3: Alethic Architecture Decision (Human Required)

**Current State**: 70% complete (Phases 1-3 done: Functor, Halo, Archetypes)
**Remaining**: Phases 4-6 (LocalProjector, K8sProjector, CLI)

### Options

**Option A: Archive at 70% "MVP Complete"**
- The core algebra (functor protocols, halo capabilities) is done
- Projectors can be added later when needed
- Mark as "foundation complete, projectors deferred"
- **Effort**: 30 minutes (update docs, forest)

**Option B: Complete Phase 4 (LocalProjector)**
- Add `LocalProjector` for in-process deployment
- Useful for testing and single-node setups
- **Effort**: 2-4 hours

**Option C: Complete Phases 4-6 (Full Implementation)**
- LocalProjector + K8sProjector + CLI
- Full production-ready deployment story
- **Effort**: 8-12 hours

**Recommendation**: Option A (archive) or Option B (LocalProjector only). The functor algebra is the hard part and it's done. Projectors are straightforward when needed.

---

## Priority 4: Database Projector Integration (Lower Priority)

**Files**:
- `impl/claude/system/projector/k8s_database.py` (manifest generation)
- `impl/claude/agents/flux/synapse.py` (CDC streams)

### 4.1 Current State

Both files exist but tests are minimal/empty. The code generates K8s manifests but lacks:
- Error handling for malformed configs
- Mock K8s integration tests
- CDC stream validation tests

### 4.2 Tasks (If Prioritized)

1. Add test fixtures for K8s manifest generation
2. Add synapse CDC stream tests with mock data
3. Add error handling tests for edge cases

**Recommendation**: Defer unless actively using database projector. The code works for happy path; hardening can wait.

---

## Execution Order

Given tight feedback loops priority:

### Session 1: Quick Wins (~2-3 hours)
1. ✅ Create `test_refinements.py` with SoulPathResolver + GracefulDegradation tests
2. ✅ Run tests, verify passing
3. ✅ Commit: "test: Add refinements.py coverage (K-gent hardening)"

### Session 2: Memory Wiring (~2-3 hours)
1. ✅ Add `self.memory.*` AGENTESE paths
2. ✅ Wire to Ghost cache
3. ✅ Add integration tests
4. ✅ Commit: "feat: Wire self.memory.* AGENTESE paths"

### Session 3: Polish (~1-2 hours)
1. ✅ Add remaining hypnagogia/garden edge cases
2. ✅ Update `plans/_status.md` and `plans/_forest.md`
3. ✅ Human decision on Alethic Architecture
4. ✅ Commit: "chore: K-gent hardening complete"

---

## Metrics

| Metric | Before | Target |
|--------|--------|--------|
| K-gent tests | ~418 | 470+ |
| Memory module | 30% | 60% |
| Test coverage gaps | 4 modules | 0-1 modules |

---

## Commands

```bash
# Run K-gent tests
cd impl/claude && pytest agents/k/_tests/ -v --tb=short

# Run memory integration tests
cd impl/claude && pytest agents/d/_tests/test_crystal.py -v

# Full test suite
cd impl/claude && pytest -m "not slow" -q
```

---

*"A plan is a to-do list with delusions of grandeur. Ship early, ship often."*
