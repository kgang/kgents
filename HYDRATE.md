# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Context hydrated ✅ - Meta-evolution experiments completed (all failed)
**Branch**: `main` (commit ff576c5)
**Activity**: Two meta-evolution processes tried evolving `meta/evolve` module, all experiments rejected
**Next**: Clean uncommitted changes OR continue T-gents Phase 3 OR J-gents Phase 3

---

## This Session: Context Hydration + Test Organization (2025-12-08)

### Completed ✅

**Test Suite Organization** ⭐
- Reorganized all test files into concern-based folders:
  - `tests/agents/`: T-gents tests (test_t_gents.py)
  - `tests/evolution/`: Pipeline tests (test_metrics.py)
  - `tests/layers/`: E-gents layer tests (prompt, parsing, recovery)
- Created GitHub Actions CI workflow with uv:
  - Test job: Python 3.11, 3.12, 3.13
  - Lint job: ruff format + lint + mypy
  - Coverage job: pytest-cov with codecov upload
- Updated pyproject.toml with pytest configuration
- Created comprehensive tests/README.md documentation
- All 16 T-gents tests passing in new location ✅

**Meta-Evolution Experiments**
- Ran two parallel `evolve.py meta --auto-apply` processes
- Generated hypotheses about evolving the evolution system itself
- Key hypotheses tested:
  - Decomposing EvolutionPipeline into composable agent morphisms
  - Extracting StatusReportAgent from show_status function
  - Making DialecticFix explicit for thesis→antithesis→synthesis cycle
- **Results**: All experiments failed type checking (API mismatches, incorrect signatures)
- **Outcome**: 0 incorporated, 1 rejected per run, 0 held
- Evolution logs saved to `.evolve_logs/evolve_meta_*`

### Context Refreshed
- HYDRATE.md reviewed and updated
- T-gents Phase 2 status: COMPLETE (10 types, all tests passing)
- Background processes completed successfully

---

## Previous: T-gents Phase 2 Implementation (2025-12-08)

### Completed ✅

**T-gents Phase 2 - Additional Saboteurs & Observers**

Created 5 new T-gent agents in `impl/claude/agents/t/`:

**Type II Saboteurs (Chaos Engineering):**
1. **NoiseAgent** (`noise.py`) - Semantic perturbation N_ε: A → A + ε
   - Adds controlled noise while preserving semantics
   - Configurable noise level (0.0-1.0), deterministic with seed
   - Noise types: CASE, WHITESPACE, TYPOS, PUNCTUATION
   - Tests robustness to input perturbations

2. **LatencyAgent** (`latency.py`) - Temporal delay L_Δ: (A, t) → (A, t + Δ)
   - Adds configurable latency while preserving data
   - Variance support for realistic timing jitter
   - Tests performance under delay conditions

3. **FlakyAgent** (`flaky.py`) - Probabilistic failure F_p: A → B ∪ {⊥}
   - Wraps agent, fails with probability p
   - Deterministic with seed for reproducible chaos
   - Tests retry logic and error handling

**Type III Observers (Identity with Side Effects):**
4. **CounterAgent** (`counter.py`) - Invocation counting C: A → A
   - Tracks invocation count
   - Identity morphism with counting side effect
   - Assert helpers for test validation

5. **MetricsAgent** (`metrics.py`) - Performance profiling M: A → A
   - Records timing metrics: min, max, avg, total
   - Identity morphism with timing side effects
   - PerformanceMetrics dataclass for structured data

**Testing & Validation:**
- Updated `test_t_gents.py` with 6 new tests for Phase 2 agents
- All 16 tests passing (10 Phase 1 + 6 Phase 2)
- Verified composition: Counter >> Metrics >> Noise works
- All agents have `__rshift__` for category theory composition
- All agents marked with `__is_test__ = True`

**Files Modified:**
- `agents/t/__init__.py`: Added exports for Phase 2 agents
- `test_t_gents.py`: Added comprehensive Phase 2 tests

**Phase 1 + Phase 2 Summary:**
- **10 T-gent types total** across 3 categories
- **Type I (Nullifiers)**: MockAgent, FixtureAgent
- **Type II (Saboteurs)**: FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent
- **Type III (Observers)**: SpyAgent, PredicateAgent, CounterAgent, MetricsAgent
- All tests passing, composition verified, ready to commit

---

## Previous: T-gents Phase 1 Implementation (2025-12-08)

**Commit 8189e79: T-gents Phase 1**

Created Category Theory-based testing framework in `impl/claude/agents/t/`:
- MockAgent, FixtureAgent (Type I - Nullifiers)
- FailingAgent (Type II - Saboteurs)
- SpyAgent, PredicateAgent (Type III - Observers)
- Comprehensive test suite with 10 tests

## Previous: J-gents Phase 2 - Chaosmonger (2025-12-08)

### Completed ✅

**Commit 0107f3f: J-gents Phase 2 - Entropy Budget & Chaosmonger Integration**

**bootstrap/types.py:**
- Add `entropy_budget` field to `FixConfig` (J-gents entropy tracking)
- Add `entropy_remaining` field to `FixResult` (budget consumption tracking)

**bootstrap/fix.py:**
- Implement entropy budget tracking in fixed-point iteration
- Diminishing budget per iteration: `budget / (iteration + 1)`
- Early termination when budget < 0.1 threshold
- Add `entropy_budget` parameter to `fix()` convenience function

**agents/e/safety.py:**
- Add Chaosmonger integration fields to `SafetyConfig`:
  - `chaosmonger_enabled` (default True)
  - `max_cyclomatic_complexity` (20)
  - `max_branching_factor` (5)
  - `allowed_imports` / `forbidden_imports`
- Add `stability_valid` field to `SandboxTestResult`
- Implement `_check_stability()` method using Chaosmonger
- Pre-Judge stability check runs before syntax/type checks

**Test Results:**
```
✓ FixConfig with entropy_budget: 1.0
✓ FixResult with entropy_remaining: 0.5
✓ SafetyConfig.chaosmonger_enabled: True
✓ SafetyConfig.max_cyclomatic_complexity: 20
✓ All syntax checks pass
```

---

## Previous: J-gents Phase 2 - Chaosmonger (2025-12-08)

**Commit b917e2e: Chaosmonger AST Analyzer**

- `impl/claude/agents/j/chaosmonger.py` (~400 lines): Full AST-based stability analyzer
- Features: Import analysis, cyclomatic complexity, unbounded recursion detection
- All tests passing, mypy --strict passes

---

## Previous: T-gents Phase 1 Implementation (2025-12-08)

**Commit 8189e79: T-gents Phase 1**

5 T-gent types implemented:
- MockAgent, FixtureAgent, FailingAgent, SpyAgent, PredicateAgent
- Comprehensive test suite (10 tests, all passing)

---

## Next Session: Start Here

### Priority 1: Clean up uncommitted changes ⚠️

Uncommitted changes from previous sessions (not related to T-gents Phase 2):
```bash
git status  # Shows:
# modified:   impl/claude/agents/e/prompts.py (API signature extraction)
# modified:   impl/claude/agents/e/safety.py (SafetyConfig updates)
# modified:   impl/claude/bootstrap/fix.py (Entropy budget)
# modified:   impl/claude/bootstrap/types.py (FixConfig.entropy_budget)
# deleted:    impl/claude/bootstrap_reference/behavior_snapshot*.{json,pkl}
```

**Options:**
1. Commit these changes (from Phase 2.5d session)
2. Restore them with `git restore`
3. Review and decide case-by-case

### Priority 2: T-gents Phase 3 - Type IV Critics

From `spec/t-gents/taxonomy.md` Section 4:
- [ ] JudgeAgent: LLM-as-Judge for semantic evaluation
- [ ] PropertyAgent: Property-based testing with generators
- [ ] OracleAgent: Differential testing oracle

### Priority 3: J-gents Phase 3 - JIT Compilation

From JGENT_SPEC_PLAN.md:
- [ ] Write jit.md spec
- [ ] Implement MetaArchitect agent
- [ ] Sandboxed execution environment

---

## What Exists

**J-gents Implementation** (`impl/claude/agents/j/`) ✅ Phase 2 COMPLETE
- promise.py: Promise[T] lazy computation
- reality.py: RealityClassifier agent
- chaosmonger.py: AST stability analyzer
- __init__.py: Module exports

**J-gents Bootstrap Integration** ✅ Phase 2 COMPLETE
- bootstrap/types.py: FixConfig.entropy_budget, FixResult.entropy_remaining
- bootstrap/fix.py: Entropy tracking in iteration
- agents/e/safety.py: SafetyConfig + Chaosmonger integration

**T-gents Implementation** (`impl/claude/agents/t/`) ✅ Phase 1 + Phase 2 COMPLETE
- **Phase 1**: mock.py, fixture.py, failing.py, spy.py, predicate.py
- **Phase 2**: noise.py, latency.py, flaky.py, counter.py, metrics.py ⭐ NEW
- **Tests**: test_t_gents.py (16 tests: 10 Phase 1 + 6 Phase 2) ⭐ UPDATED

**J-gents Spec** (`spec/j-gents/`) ✅ Complete
- README.md, reality.md, lazy.md, stability.md, JGENT_SPEC_PLAN.md

**T-gents Spec** (`spec/t-gents/`) ✅ Complete
- README.md, algebra.md, taxonomy.md, adversarial.md

---

## Session Log

**Dec 8 (this)**: ff576c5 - Context hydration + meta-evolution experiments (0 incorporated)
**Dec 8**: 41c8d4c - T-gents Phase 2 (NoiseAgent, LatencyAgent, FlakyAgent, CounterAgent, MetricsAgent)
**Dec 8**: 8189e79 - T-gents Phase 1 implementation
**Dec 8**: 9d1c295 - HYDRATE.md update for J-gents Phase 2
**Dec 8**: b917e2e - J-gents Phase 2 Chaosmonger implementation
**Dec 8**: 0919279 - Phase 2.5d testing & analysis
**Dec 8**: d73283e - T-gents specification complete
**Dec 8**: dc27faa - J-gents Phase 1 (Promise[T], RealityClassifier)

---

## Quick Commands

```bash
# Run all tests (recommended)
cd impl/claude
uv run pytest

# Test specific suites
uv run pytest tests/agents/          # T-gents
uv run pytest tests/evolution/       # Evolution pipeline
uv run pytest tests/layers/          # E-gents layers

# Test T-gents Phase 1 + Phase 2
uv run pytest tests/agents/test_t_gents.py -v

# Test with coverage
uv run pytest --cov=agents --cov=bootstrap --cov=runtime --cov-report=term-missing

# Test J-gents Chaosmonger
python -c "from agents.j import is_stable; print(is_stable('def f(): pass'))"

# Type check
cd impl/claude
python -m mypy --strict --explicit-package-bases agents/ bootstrap/ runtime/

# Lint & format
uv run ruff format impl/claude
uv run ruff check impl/claude
```

---
