# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Ready for IMPROVEMENT_PLAN Phase A ✅
**Branch**: `main` (clean, just pushed)
**Reference**: `impl/claude/IMPROVEMENT_PLAN.md` (17 hypotheses)
**Next**: Phase A quick wins - H5: json_utils, H4: lazy imports, H2: SuggestionAgent

---

## Recent Commits

- `745a04a` docs: Add systematic evolution analysis + improvement plan
- `3c736dd` docs: Update HYDRATE.md for J-gents Phase 5 session
- `4e3fce7` docs(j-gents): Complete Phase 5 Integration & Polish

---

## Next Session: Phase A Quick Wins

**See `impl/claude/IMPROVEMENT_PLAN.md` for full details.**

### H5: Extract `runtime/json_utils.py`
Extract 250 lines from `runtime/base.py`:
- `robust_json_parse`, `_repair_json`, `_extract_field_values`, `parse_structured_sections`
- Pure refactor, no behavior change

### H4: Lazy imports in `evolve.py`
- 57 imports → `TYPE_CHECKING` + lazy factories
- Reduces startup overhead

### H2: Extract `SuggestionAgent`
- Move `show_suggestions` (56 lines) to `agents/e/suggestion.py`
- Composable agent pattern

**Validation:** `python -m pytest -v` + `mypy --strict` on changed files

---

## Previous: Systematic Evolution Analysis (2025-12-08)

**Analysis found:** 27k lines, 18 files >500 lines, 45+ functions >50 lines

**Worst offenders:**
1. `evolve.py` (1,286 lines)
2. `agents/e/prompts.py` (762 lines)
3. `agents/e/parser.py` (687 lines)
4. `agents/j/sandbox.py` (460 lines)

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
