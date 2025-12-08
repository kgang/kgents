# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Systematic Evolution Analysis COMPLETE ✅
**Branch**: `main` (clean)
**Achievement**: Generated `impl/claude/IMPROVEMENT_PLAN.md` with 17 hypotheses
**Next**: Phase A quick wins (H5: json_utils, H4: lazy imports, H2: SuggestionAgent)

---

## Recent Commits

- `3c736dd` docs: Update HYDRATE.md for J-gents Phase 5 session
- `4e3fce7` docs(j-gents): Complete Phase 5 Integration & Polish
- `1fa2e8b` docs: Update HYDRATE.md for J-gents Phase 4 completion

---

## This Session: Systematic Evolution Analysis (2025-12-08)

### Canvas Results

Ran `evolve.py suggest` on all impl/ targets:
- **meta**: EvolutionPipeline (19 methods), show_suggestions (55 lines)
- **runtime**: robust_json_parse (96 lines), with_retry (53 lines)
- **agents**: 50 modules analyzed, shared/ast_utils flagged
- **bootstrap**: Clean ✅

### Static Analysis Findings

| Metric | Count |
|--------|-------|
| Total lines | ~27,000 |
| Files >500 lines | 18 |
| Functions >50 lines | 45+ |
| Classes >10 methods | 8 |

**Worst offenders:**
1. `evolve.py` (1,286 lines, 8 long functions, 1 large class)
2. `agents/e/prompts.py` (762 lines)
3. `agents/e/parser.py` (687 lines)
4. `agents/j/sandbox.py` (460 lines, execute_in_sandbox: 150 lines!)

### Generated: IMPROVEMENT_PLAN.md

**17 Hypotheses across 4 priorities:**

| Priority | Focus | Key Items |
|----------|-------|-----------|
| 1 | evolve.py | H1-H4: Decompose EvolutionPipeline, lazy imports |
| 2 | runtime/E-gents | H5-H9: json_utils, prompts split, parser refactor |
| 3 | J-gents/B-gents | H10-H14: sandbox split, chaosmonger decompose |
| 4 | Shared | H15-H17: ast_utils polish, types cleanup |

**Implementation Phases:**
- Phase A: Quick wins (H5, H4, H2) - 1-2 sessions
- Phase B: Core refactoring (H1, H7, H10) - 2-3 sessions
- Phase C: Deep refactoring (H8, H11, H13) - 3-4 sessions
- Phase D: Polish - remaining items

---

## Previous: J-gents Phase 5 + Synergy 4A

---

## J-gents: Complete (Phases 1-5) ✅

**Full Pipeline Operational + Integrated:**
```
Reality Classification → Promise Tree → JIT Compile → Test → Ground → Cache
```

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Promise[T], Reality, RealityClassifier | ✓ Spec + Impl |
| 2 | Chaosmonger (AST stability) | ✓ Spec + Impl |
| 3 | MetaArchitect, Sandbox | ✓ Spec + Impl (22 tests) |
| 4 | JGent coordinator | ✓ Spec + Impl (28 tests) |
| 5 | Integration & Polish | ✓ Spec (this session) |
| **Total** | | **50 tests passing** |

**Complete Specification (6 docs):**
- `spec/j-gents/README.md` - Philosophy & overview
- `spec/j-gents/reality.md` - Reality classification
- `spec/j-gents/lazy.md` - Promise abstraction
- `spec/j-gents/stability.md` - Entropy budgets & Chaosmonger
- `spec/j-gents/jit.md` - JIT compilation
- `spec/j-gents/integration.md` - Caching & ecosystem (new ✨)

**Implementation:**
- `agents/j/jgent.py` (~400 lines) - Main coordinator
- `agents/j/meta_architect.py` (~550 lines) - JIT agent compiler
- `agents/j/sandbox.py` (~465 lines) - Safe execution

---

## T-gents: Phase 3 Complete ✅

**13 agents across 4 types:**
- Nullifiers (2): Mock, Fixture
- Saboteurs (4): Failing, Noise, Latency, Flaky
- Observers (4): Spy, Predicate, Counter, Metrics
- Critics (3): Judge, Oracle, Property

---

## Next Session: Start Here

### Priority 1: Synergy Phase 4B - Abstractions

**From SYNERGY_REFACTOR_PLAN.md:**
- ValidationPipeline pattern (compose validators)
- ResilientAgent wrapper (T-gents integration)
- Property-based evolution testing (T-gents + E-gents)

### Priority 2: Meta-Evolution Hypotheses

**From `evolve.py meta` analysis:**
- H4: `show_suggestions` refactor (56 lines → composable)
- H3: `EvolutionPipeline` decomposition (1100 lines)
- H5: Lazy import loading (57 imports)

### Priority 3: Continue J-gents Work

**Future enhancements from integration.md:**
- Persistent agent cache (disk-backed)
- Cross-genus integration tests
- Performance benchmarking

---

## Quick Commands

```bash
cd impl/claude

# Run all tests (93 total)
python -m pytest test_j_gents_phase*.py test_t_gents_phase3.py \
                 test_ast_utils.py test_regression_validator.py -v

# Just synergy tests (31 new)
python -m pytest test_ast_utils.py test_regression_validator.py -v
```

---
