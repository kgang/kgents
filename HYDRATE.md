# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: IMPROVEMENT_PLAN Phase B - H1 COMPLETE ✅
**Branch**: `main`
**Achievement**: evolve.py refactored to use agents/e (-822 lines, 53% reduction!)
**Next**: Phase B remaining (H7: prompts.py, H10: sandbox.py)

---

## Recent Commits

- `cb98af8` refactor(runtime): Extract JSON utilities to separate module (H5)
- `745a04a` docs: Add systematic evolution analysis + improvement plan
- `3c736dd` docs: Update HYDRATE.md for J-gents Phase 5 session

---

## This Session: IMPROVEMENT_PLAN Phase A - H4 & H5 (2025-12-08)

### Completed: H5 - Extract runtime/json_utils.py ✅

**Before:**
- `runtime/base.py`: 635 lines (massive, mixed concerns)

**After:**
- `runtime/base.py`: 362 lines (-273 lines, -43% reduction!)
- `runtime/json_utils.py`: 287 lines (new, focused module)

**Extracted functions:**
- `robust_json_parse`: Handle LLM markdown/truncation/edge cases
- `json_response_parser`: Standard wrapper
- `parse_structured_sections`: Extract structured lists from responses
- Internal helpers: `_repair_json`, `_extract_field_values`

**Updated imports in:**
- `runtime/__init__.py`: Export from json_utils
- `agents/t/judge.py`: Use json_utils
- `agents/a/creativity.py`: Use json_utils

**Tests:** All pass ✅ (31 synergy tests, judge tests)

### Completed: H4 - Lazy Imports in evolve.py ✅

**Changes:**
- Added `TYPE_CHECKING` import pattern to defer type-only imports
- Moved runtime imports into lazy instantiation methods:
  - `HypothesisEngine` → `_get_hypothesis_engine()`
  - `HegelAgent` → `_get_hegel()`
  - `Sublate` → `_get_sublate()`
  - `AgentContext` → imported at usage site
- Updated type annotations to use string literals for forward references

**Benefits:**
- Reduced startup time for status/suggest modes
- Improved testability (easier to mock dependencies)
- Clear separation between type-checking and runtime imports

**Tests:** All pass ✅ (syntax valid, import successful, status command working)

### Phase A Status

| Hypothesis | Status | Notes |
|------------|--------|-------|
| H5: json_utils extraction | ✅ Complete | -273 lines from base.py |
| H4: Lazy imports | ✅ Complete | TYPE_CHECKING pattern + lazy methods |
| H2: SuggestionAgent | ⏸️ Deferred | Function already simple, no extraction needed |

**Verdict:** Phase A yielded **2 substantial improvements** (H4, H5).

### Background Meta-Evolution Results

Ran `evolve.py meta --auto-apply` (3 attempts, all completed):
- Generated 5 hypotheses each run
- All experiments failed type checking
- No auto-incorporations (expected for meta-evolution)
- Hypotheses aligned with IMPROVEMENT_PLAN.md ✅

---

## Next Session: Start Here

### Priority 1: IMPROVEMENT_PLAN Phase B - Core Refactoring

**H1: Decompose EvolutionPipeline (19 methods → 4 agents)**
- Extract into composable E-gent agents following the pipeline pattern
- Target: ~400 line reduction in evolve.py
- Impact: Improves testability, composability

**H7: Split agents/e/prompts.py (762 lines)**
- Separate into base/improvement/analysis modules
- Long functions: build_improvement_prompt (137 lines)

**H10: Split agents/j/sandbox.py (460 lines)**
- Long function: execute_in_sandbox (150 lines!)
- Separate executor/namespace/validation concerns

### Priority 2: Re-evaluate Phase A Deferrals

**H4 (lazy imports):** Needs careful design to avoid breaking changes
**H2 (SuggestionAgent):** Current implementation already simple

---

## Previous Sessions

### Systematic Evolution Analysis (2025-12-08)

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

### J-gents Phase 5 Complete

**Integration & Polish specification** written. See section below for details.

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
