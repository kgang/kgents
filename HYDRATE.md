# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: J-gents Phase 4 + T-gents Phase 3 COMMITTED ✅
**Branch**: `main` (clean)
**Achievement**: Full J-gents pipeline (50 tests), T-gents critics (12 tests)
**Next**: J-gents Phase 5 (integration.md), cross-genus synergy

---

## Recent Commits

- `08c09ee` feat(j-gents): Implement Phase 3 JIT + Phase 4 Coordinator
- `1a77432` feat(t-gents): Implement Phase 3 Type IV Critics
- `ac7987a` refactor(evolve): Extract show_status into composable agents

---

## J-gents: Complete (Phases 1-4) ✅

**Full Pipeline Operational:**
```
Reality Classification → Promise Tree → JIT Compile → Test → Ground
```

| Phase | Component | Tests |
|-------|-----------|-------|
| 1 | Promise[T], Reality, RealityClassifier | ✓ |
| 2 | Chaosmonger (AST stability) | ✓ |
| 3 | MetaArchitect, Sandbox | 22 |
| 4 | JGent coordinator | 28 |
| **Total** | | **50** |

**Key Files:**
- `agents/j/jgent.py` - Main coordinator
- `agents/j/meta_architect.py` - JIT agent compiler
- `agents/j/sandbox.py` - Safe execution
- `spec/j-gents/jit.md` - JIT specification

---

## T-gents: Phase 3 Complete ✅

**13 agents across 4 types:**
- Nullifiers (2): Mock, Fixture
- Saboteurs (4): Failing, Noise, Latency, Flaky
- Observers (4): Spy, Predicate, Counter, Metrics
- Critics (3): Judge, Oracle, Property

---

## Next Session Priorities

### 1. J-gents Phase 5: Integration & Polish
- Write `spec/j-gents/integration.md` (memoization, caching)
- Performance optimization
- Documentation

### 2. Cross-Genus Synergy
- See `SYNERGY_REFACTOR_PLAN.md` for detailed plan
- Quick wins: Extract shared AST utils
- E-gents → T-gents regression testing integration

### 3. Meta-Evolution Hypotheses (from evolve.py meta)
- H4: show_suggestions refactor (56 lines)
- H3: EvolutionPipeline decomposition
- H5: Lazy import loading

---

## Quick Commands

```bash
cd impl/claude

# Run all J-gents tests
python -m pytest test_j_gents_phase3.py test_j_gents_phase4.py -v

# Run T-gents tests
python -m pytest test_t_gents_phase3.py -v

# Type check
python -m mypy --strict agents/j/

# Evolution status
python evolve.py status
```

---
