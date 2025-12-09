# Evolution Plan: impl/ Improvement Roadmap

**Generated**: 2025-12-08 (Dry run analysis)
**Source**: `evolve.py all --dry-run` (26 hypotheses across 97 modules)
**Status**: Phase C Complete, planning Phase D improvements

---

## Executive Summary

The evolve loop identified **26 actionable improvement opportunities** across the codebase, categorized into 6 strategic themes. The dominant theme is **composability** (10 items, 38%), highlighting the need to strengthen the "agents as morphisms" foundation across all agent types.

### Priority Breakdown

| Priority | Category | Count | Focus |
|----------|----------|-------|-------|
| **P0** | Composability | 10 | Enable >> operator across all agents |
| **P1** | Protocol Conformance | 8 | Ensure type safety and interfaces |
| **P2** | Testing | 3 | Increase test coverage for edge cases |
| **P2** | Performance | 1 | Optimize hot paths (O(n) → O(1)) |
| **P3** | Refactoring | 1 | Reduce complexity in large functions |
| **P3** | Other | 3 | Enhancements and bug fixes |

---

## Phase D: Composability First (P0 - Critical)

**Theme**: "Agents are morphisms, composition is primary"

### D1. D-gent Composability Overhaul

**Scope**: 5 modules in `agents/d/`

#### D1.1: Protocol-Level Changes
- **File**: `agents/d/protocol.py`
- **Changes**:
  1. Add morphism signature `Agent[A, B]` conformance
  2. Add explicit error type imports (canonical error hierarchy)
  3. Enable `>>` composition for D-gent pipelines
- **Impact**: Foundation for all D-gent composability

#### D1.2: Agent-Specific Implementations
**LensAgent** (`agents/d/lens_agent.py`):
- Add `>>` operator for lens composition (deeper focusing)
- Fix race condition: atomic update with lock for load-modify-save
- Example: `user_lens >> address_lens >> zip_code_lens`

**VolatileAgent** (`agents/d/volatile.py`):
- Add `>>` and `|` operators for morphism behavior
- Replace `List._history.pop(0)` with `collections.deque(maxlen=N)` (O(n) → O(1))

**CachedAgent** (`agents/d/cached.py`):
- Add explicit `DataAgent` protocol conformance
- Fix `invalidate_cache()` semantics (currently warms instead of invalidates)

#### D1.3: Error Handling Enhancement
- **File**: `agents/d/errors.py`
- **Changes**:
  1. Add structured context attributes (state keys, backend info)
  2. Add `StateResult[T] = T | StateError` for monadic composition
- **Benefit**: Enable Result-style error handling instead of exceptions

---

### D2. T-gent Composability Refinement

**Scope**: 2 modules in `agents/t/`

#### D2.1: CounterAgent Symmetric Composition
- **File**: `agents/t/counter.py`
- **Changes**:
  1. Add `__lshift__` operator (currently only `__rshift__` exists)
  2. Make `CounterAgent[A]` explicitly extend `Agent[A, A]` for type checking
- **Benefit**: Enable counter as right-hand operand in pipelines

#### D2.2: NoiseAgent Enhancements
- **File**: `agents/t/noise.py`
- **Changes**:
  1. Ensure proper `Agent` ABC inheritance with `name` property
  2. Add configurable per-operation weights (non-uniform noise selection)
- **Benefit**: More realistic test scenarios with weighted noise types

---

### D3. Test Infrastructure Composability

**Scope**: 1 module in `agents/shared/`

#### D3.1: Composition Fixtures
- **File**: `agents/shared/fixtures.py`
- **Changes**:
  1. Add fixtures demonstrating `>>` operator usage
  2. Add parameterized factory functions for property-based testing
- **Examples**:
  ```python
  def make_composed_pipeline() -> ComposedAgent[A, C]:
      return make_sample_agent_a() >> make_sample_agent_b()

  def make_sample_agent(
      input_type: type = str,
      output_type: type = str,
      randomize: bool = False
  ) -> Agent[A, B]:
      # Parameterized factory for diverse testing
  ```

---

## Phase E: Protocol Conformance & Type Safety (P1 - High)

**Theme**: Ensure all agents follow the contract

### E1. Dataclass Validation (8 items)

**Status**: Mostly correct, but evolve loop flagged for review

**Action Items**:
1. ✅ Validate that all `@dataclass` types are correctly used (not Protocols/ABCs)
2. ⚠️ Fix 2 cases where description is missing:
   - `agents/e/retry.py`: `RetryConfig`, `RetryAttempt`

**Findings**: 6/8 are correct (no change needed), 2 need clarification

---

## Phase F: Testing & Quality (P2 - Medium)

### F1. Test Coverage for Private Functions

**Scope**: `runtime/json_utils.py`

**Missing Tests**:
1. `_repair_json()` - JSON repair logic
2. `_extract_field_values()` - Field extraction

**Action**: Add unit tests to `runtime/_tests/test_json_utils.py`

### F2. Property-Based Testing Infrastructure

**Scope**: `agents/shared/fixtures.py` (see D3.1)

**Goal**: Enable hypothesis-based testing with randomized inputs

---

## Phase G: Performance Optimization (P2 - Medium)

### G1. VolatileAgent History Management

**File**: `agents/d/volatile.py:save()`

**Issue**: `_history.pop(0)` is O(n) for every write

**Fix**:
```python
# Before
self._history.append(entry)
if len(self._history) > self._max_history:
    self._history.pop(0)  # O(n)

# After
from collections import deque
self._history: deque[StateEntry] = deque(maxlen=self._max_history)
self._history.append(entry)  # O(1) with automatic eviction
```

**Impact**: High-frequency state updates (e.g., real-time agents)

---

## Phase H: Code Quality (P3 - Low)

### H1. Refactor Large Functions

**File**: `agents/f/forge_with_search.py`

**Issue**: `search_before_forge()` is 71 lines

**Approach**: Extract composable helpers
```python
def _build_no_match_result(...) -> SearchBeforeForgeResult
def _build_match_found_result(...) -> SearchBeforeForgeResult
async def search_before_forge(...) -> SearchBeforeForgeResult:
    matches = await registry.search(...)
    if not matches:
        return _build_no_match_result(...)
    return _build_match_found_result(matches, ...)
```

---

## Implementation Strategy

### Tiered Rollout (Conservative → Confident)

#### Tier 1: Bug Fixes (99% confidence)
1. ✅ **DONE**: `SpyAgent._max_history` parameter fix (Session 18)
2. **TODO**: `CachedAgent.invalidate_cache()` semantics fix
3. **TODO**: `VolatileAgent.deque` performance fix

#### Tier 2: Composability (85% confidence)
1. D-gent protocol morphism signature
2. LensAgent `>>` operator
3. VolatileAgent `>>` operator
4. CounterAgent `__lshift__` operator

#### Tier 3: Structural (75% confidence)
1. Composition fixtures
2. Property-based testing infrastructure
3. Refactor `search_before_forge()`

### Validation Approach

For each change:
1. **Pre-flight**: AST analysis + type checking
2. **Experiment**: Sandbox test with original tests
3. **Judge**: Bootstrap Judge against 7 principles
4. **Contradict**: Detect tensions with existing code
5. **Incorporate**: Apply if tests pass + no tensions

---

## Metrics & Success Criteria

### Pre-Evolution Baseline (Session 18)
- F-gent: 192 passing ✅
- E-gent: 50 passing, 4 errors ⚠️
- J-gent: 72 passing ✅
- T-gent: 43 passing ✅
- D-gent: 73 passing, 3 failed ⚠️
- L-gent: 39 passing ✅

**Total**: 469 passing, 7 failing

### Post-Evolution Target
- **All tests passing**: 476+ (fix 7 failures)
- **New tests added**: +20 (private function coverage + composition fixtures)
- **Type errors**: 0 (strict mypy across all modules)
- **Composability**: 100% of agents support `>>` operator

---

## Next Steps

### Immediate Actions (Session 19)

**Option A: Commit Preflight Fix** (recommended):
```bash
git add impl/claude/agents/e/preflight.py
git commit -m "fix(evolve): Expand builtins list in preflight checker

- Add 30+ missing Python built-ins (property, super, open, etc.)
- Fixes false positives blocking evolution experiments
- Impact: All 97 modules now pass preflight checks"
```

**Option B: Start Phase D.1 - D-gent Composability**:
1. Update `agents/d/protocol.py` with morphism signature
2. Run evolve loop on D-gents only: `python evolve.py agents/d --auto-apply`
3. Validate all D-gent tests still pass

**Option C: Run Full Dry Run (Post-Fix Validation)**:
```bash
python evolve.py all --dry-run --hypotheses=3 --max-improvements=2
```
- Verify preflight checks now pass
- Collect fresh hypotheses post-fix
- Compare with baseline analysis

---

## Appendix: Raw Hypotheses by Module

### Runtime (2 hypotheses)
1. `json_utils`: Missing tests for `_repair_json()`
2. `json_utils`: Missing tests for `_extract_field_values()`

### T-gents (4 hypotheses)
1. `noise`: Missing Agent ABC inheritance
2. `noise`: Lacks configurable operation weights
3. `counter`: Missing `__lshift__` operator
4. `counter`: Incomplete type signature for `Agent[A, A]`

### F-gents (3 hypotheses)
1. `intent.Dependency`: Dataclass review (✅ correct)
2. `forge_with_search.SearchBeforeForgeResult`: Dataclass review (✅ correct)
3. `forge_with_search.search_before_forge()`: 71-line function refactor

### D-gents (9 hypotheses)
1. `lens_agent`: Missing `>>` operator
2. `lens_agent`: Race condition in `save()`
3. `protocol`: Missing morphism signature
4. `protocol`: Missing explicit error types
5. `cached`: Missing DataAgent conformance
6. `cached`: Incorrect `invalidate_cache()` semantics
7. `volatile`: Missing `>>` operator
8. `volatile`: O(n) history management
9. `errors`: Missing structured context + `StateResult[T]`

### E-gents (6 hypotheses)
1. `forge_integration.ImprovedIntent`: Dataclass review (✅ correct)
2. `forge_integration.ReforgeResult`: Dataclass review (✅ correct)
3. `safe_evolution_orchestrator.SafeEvolutionOrchestratorResult`: Dataclass review (✅ correct)
4. `retry.RetryConfig`: Dataclass review (needs description)
5. `retry.RetryAttempt`: Dataclass review (needs description)

### Shared (2 hypotheses)
1. `fixtures`: Missing composition fixtures
2. `fixtures`: Missing parameterized factories

---

## Philosophy Alignment

This evolution plan aligns with kgents principles:

1. **Tasteful**: Focus on composability (the core abstraction)
2. **Curated**: 26 hypotheses from 97 modules = selective improvement
3. **Ethical**: Preserve backward compatibility, avoid breaking changes
4. **Joyful**: Enable delightful composition patterns (`>>` operator everywhere)
5. **Composable**: Every change strengthens the morphism foundation
6. **Heterarchical**: No fixed hierarchy, agents compose freely
7. **Generative**: Changes can be regenerated from specs

---

**Meta-Note**: This plan was generated by analyzing the evolve loop's dry run output. The categorization and prioritization reflect both the frequency of issues (composability dominates) and the principles-based judgment (composition is primary).
