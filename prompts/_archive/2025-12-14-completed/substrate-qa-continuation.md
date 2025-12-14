# QA: Continuation from IMPLEMENT (Memory Substrate Wiring)

> *"Gate the implementation before broader testing."*

**Date**: 2025-12-13
**Entry Phase**: QA (continuing from IMPLEMENT)
**Entropy Budget**: 0.05

---

## ATTACH

/hydrate

You are entering **QA** phase of the N-Phase Cycle (AD-005).

Previous phase (IMPLEMENT) created these handles:
- Epilogue: `plans/_epilogues/2025-12-13-memory-substrate-wiring.md`
- Re-metabolize epilogue: `plans/_epilogues/2025-12-13-re-metabolize-substrate-learnings.md`

---

## Context from IMPLEMENT

### Code Files Modified

| File | Change |
|------|--------|
| `protocols/agentese/contexts/__init__.py` | Added substrate/compactor/router params to `create_context_resolvers()` |
| `protocols/agentese/_tests/test_substrate_paths.py` | Added 9 new tests (real integration + unified factory) |

### Tests Written

- `TestRealSubstrateIntegration` (5 tests): Real `SharedSubstrate` and `Compactor` instances
- `TestCreateContextResolversSubstrate` (4 tests): Unified factory parameter passing

### Test Results

- Before: 854 tests
- After: 863 tests (+9)
- All passing ✓

### Implementation Summary

Wired real `SharedSubstrate`, `Compactor`, and `CategoricalRouter` to `MemoryNode` through the unified factory chain:

```
create_context_resolvers(substrate=, compactor=, router=)
    → create_self_resolver(substrate=, compactor=, router=)
        → MemoryNode(_substrate=, _compactor=, _router=)
```

### Composition Laws Verified

- Identity: `create_self_resolver()` with no args still works (backward compat)
- Associativity: Order of passing substrate/compactor/router doesn't matter

---

## Your Mission

Gate the substrate wiring implementation. Focus on:

### P0: Property-Based Tests for Allocation Lifecycle

Add Hypothesis tests for invariants:
- `∀ allocation: usage_ratio ∈ [0.0, 1.0]`
- `∀ allocation: pattern_count ≤ quota.max_patterns`
- `∀ compaction: patterns_after ≤ patterns_before`
- `∀ compaction: resolution_after ≤ resolution_before`

### P1: Pressure Threshold Verification

Test that compaction triggers at correct thresholds:
- Below 0.8: `status == "not_needed"`
- At 0.8-0.95: `ratio == normal_ratio (0.8)`
- Above 0.95: `ratio == aggressive_ratio (0.5)`
- Rate limiting: max 4 compactions per hour

### P2: Ghost Lifecycle Integration (Stretch)

Wire engram operations to `LifecycleAwareCache`:
- `self.memory.engram` should use Ghost cache with TTL
- Allocations should sync to Ghost on create/update

### P3: Router Integration (Stretch)

Wire router with real `PheromoneField`:
- Need to create/inject `PheromoneField` instance
- Verify `self.memory.route` follows gradients

---

## Actions to Take NOW

1. **Quality checks**:
   ```bash
   uv run mypy impl/claude/protocols/agentese/contexts/__init__.py --strict
   uv run ruff check impl/claude/protocols/agentese/
   ```

2. **Security scan** (manual review):
   - No secrets in code ✓
   - Input validation at boundaries (human_label required) ✓
   - Graceful degradation when deps missing ✓

3. **Property test design**:
   ```python
   from hypothesis import given, strategies as st

   @given(pattern_count=st.integers(0, 2000), max_patterns=st.integers(1, 1000))
   def test_usage_ratio_bounded(pattern_count, max_patterns):
       # ...
   ```

4. **Threshold verification**:
   ```python
   async def test_compaction_at_80_percent():
       # Fill allocation to 80%
       # Verify compaction triggers with normal_ratio
   ```

---

## Exit Criteria

- [ ] Mypy strict: 0 errors
- [ ] Ruff: All checks pass
- [ ] Property tests added for allocation lifecycle
- [ ] Pressure threshold tests cover all ranges
- [ ] Security checklist completed
- [ ] Notes for TEST phase captured

---

## Accursed Share (Entropy Budget)

QA's entropy (0.05) spent on:
- **Edge case exploration**: What happens with 0 patterns? Max patterns?
- **Graceful degradation**: What if substrate is None mid-operation?
- **Alternative compaction policies**: Try different thresholds briefly

Draw: `void.entropy.sip(amount=0.05)`

---

## Principles Alignment

From `spec/principles.md`:

| Principle | Application |
|-----------|-------------|
| **Ethical** | No hidden data collection; clear error messages |
| **Composable** | Verify >> operator still works through factory chain |
| **Tasteful** | Don't add tests for hypotheticals; test what matters |

---

## Continuation Imperative

Upon completing QA, generate the prompt for **TEST** phase:

```markdown
# TEST: Continuation from QA

## ATTACH

/hydrate

You are entering TEST phase of the N-Phase Cycle (AD-005).

Previous phase (QA) created these handles:
- QA checklist status: ${qa_status}
- Property tests added: ${property_test_count}
- Threshold tests added: ${threshold_test_count}

## Your Mission

Verify correctness with intentional depth:
- Run full test suite
- Verify property tests find edge cases
- Check coverage on new code paths
- Law checks for new morphisms

## Continuation Imperative

Upon completing TEST, generate the prompt for EDUCATE.
The form is the function.
```

---

## Quick Reference

| What | Where |
|------|-------|
| Substrate code | `agents/m/substrate.py` |
| Compactor code | `agents/m/compaction.py` |
| MemoryNode | `protocols/agentese/contexts/self_.py:84` |
| Existing tests | `protocols/agentese/_tests/test_substrate_paths.py` |
| Substrate tests | `agents/m/_tests/test_substrate.py` |
| Compaction tests | `agents/m/_tests/test_compaction.py` |

---

*"The form is the function. QA gates; it does not delay."*
