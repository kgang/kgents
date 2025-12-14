# TEST: Continuation from QA (Memory Substrate Wiring)

> *"Verify correctness with intentional depth."*

**Date**: 2025-12-13
**Entry Phase**: TEST (continuing from QA)
**Entropy Budget**: 0.02

---

## ATTACH

/hydrate

You are entering **TEST** phase of the N-Phase Cycle (AD-005).

Previous phase (QA) created these handles:
- QA checklist status: All complete
- Property tests added: 6 (3 allocation invariants, 2 compaction invariants, 1 soft limit)
- Threshold tests added: 6 (below/normal/critical pressure, rate limiting)
- Edge case tests added: 4 (zero/max patterns, empty crystal, exact soft limit)
- Total new tests: 15

---

## Context from QA

### Quality Checks Passed

| Check | Status |
|-------|--------|
| Mypy strict (contexts/__init__.py) | 0 errors |
| Ruff (agentese/ + agents/m/) | All clean after fix |
| Property tests | All passing |
| Threshold tests | All passing |

### Tests Added

**TestAllocationInvariants** (3 tests):
- `test_usage_ratio_bounded_when_enforced` - Hypothesis-based
- `test_pattern_count_respects_quota` - Hypothesis-based
- `test_soft_limit_less_than_max` - Hypothesis-based

**TestCompactionInvariants** (2 tests):
- `test_compression_preserves_patterns` - Holographic property
- `test_compression_reduces_resolution` - Resolution reduction

**TestPressureThresholds** (6 tests):
- `test_below_threshold_not_needed` - Below 80%
- `test_normal_threshold_uses_normal_ratio` - 80-95%
- `test_critical_threshold_uses_aggressive_ratio` - Above 95%
- `test_rate_limiting_enforced` - Max 4/hour
- `test_rate_limit_allows_below_max` - Below max
- `test_critical_overrides_interval` - Critical pressure override

**TestEdgeCases** (4 tests):
- `test_zero_patterns_usage_ratio` - Empty allocation
- `test_max_patterns_usage_ratio` - Full allocation
- `test_empty_crystal_compression` - Empty crystal safety
- `test_allocation_at_exactly_soft_limit` - Boundary condition

### Security Checklist Completed

- [x] No secrets in code (verified in IMPLEMENT)
- [x] Input validation at boundaries (human_label required)
- [x] Graceful degradation when deps missing (MemoryNode checks)
- [x] Error messages don't leak internal details

### Test Counts

| Before | After | Delta |
|--------|-------|-------|
| 863 substrate path tests | 878 | +15 |
| 13,210 total tests | 13,291 | +81 (from other work) |

---

## Your Mission

Verify correctness with intentional depth:

### P0: Full Test Suite Verification

Run the complete test suite and ensure all tests pass:
```bash
cd impl/claude && uv run pytest -q
```

### P1: Property Test Edge Case Discovery

Review Hypothesis test outputs:
- Did property tests find any unexpected edge cases?
- Are there shrunk examples worth examining?

### P2: Coverage Analysis

Check coverage on new code paths:
```bash
cd impl/claude && uv run pytest protocols/agentese/_tests/test_substrate_paths.py --cov=protocols/agentese/contexts/self_ --cov-report=term-missing
```

### P3: Law Verification (Stretch)

Verify categorical laws for new morphisms:
- Identity: `create_self_resolver()` with no args still works
- Composition: `substrate >> compactor` composition is associative
- Roundtrip: `promote >> demote ≅ id` (up to resolution loss)

---

## Actions to Take NOW

1. **Run full test suite**:
   ```bash
   cd impl/claude && uv run pytest -q
   ```

2. **Verify Hypothesis found edge cases**:
   ```bash
   cd impl/claude && uv run pytest protocols/agentese/_tests/test_substrate_paths.py::TestAllocationInvariants -v --hypothesis-show-statistics
   ```

3. **Check for flaky tests**:
   ```bash
   cd impl/claude && uv run pytest protocols/agentese/_tests/test_substrate_paths.py --count=3
   ```

4. **Verify mypy still clean**:
   ```bash
   cd impl/claude && uv run mypy protocols/agentese/contexts/__init__.py --strict
   ```

---

## Exit Criteria

- [ ] Full test suite passes
- [ ] No flaky tests detected
- [ ] Property tests have run sufficient examples
- [ ] Coverage on new code paths > 80%
- [ ] Notes for EDUCATE phase captured

---

## Accursed Share (Entropy Budget)

TEST's entropy (0.02) spent on:
- **Mutation testing**: Try `mutmut` on critical paths
- **Boundary exploration**: What happens at `int` overflow boundaries?

Draw: `void.entropy.sip(amount=0.02)`

---

## Principles Alignment

From `spec/principles.md`:

| Principle | Application |
|-----------|-------------|
| **Ethical** | Tests verify invariants that protect users |
| **Composable** | Tests are composable (fixtures >> assertions) |
| **Tasteful** | Don't over-test; focus on critical paths |

---

## Continuation Imperative

Upon completing TEST, generate the prompt for **EDUCATE** phase:

```markdown
# EDUCATE: Continuation from TEST

## ATTACH

/hydrate

You are entering EDUCATE phase of the N-Phase Cycle (AD-005).

Previous phase (TEST) created these handles:
- Full suite status: ${suite_status}
- Coverage: ${coverage_percent}%
- Edge cases found: ${edge_cases}

## Your Mission

Document the substrate wiring for others:
- Update docstrings if needed
- Add inline comments for non-obvious logic
- Consider updating HYDRATE.md status

## Continuation Imperative

Upon completing EDUCATE, generate the prompt for MEASURE.
The form is the function.
```

---

## Quick Reference

| What | Where |
|------|-------|
| Substrate code | `agents/m/substrate.py` |
| Compaction code | `agents/m/compaction.py` |
| MemoryNode | `protocols/agentese/contexts/self_.py:84` |
| Substrate tests | `protocols/agentese/_tests/test_substrate_paths.py` |
| QA epilogue | `plans/_epilogues/2025-12-13-memory-substrate-qa.md` |

---

*"The form is the function. TEST verifies; it does not doubt."*
