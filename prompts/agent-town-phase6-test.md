# Agent Town Phase 6: TEST Phase

**Predecessor**: `plans/_epilogues/2025-12-14-agent-town-phase6-qa.md`
**Phase**: TEST (N-Phase 8 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:touched, TEST:in_progress}`

---

## Context

Phase 6 QA delivered:
- **ruff**: 1 error found and fixed (E712 in test_visualization_contracts.py)
- **mypy**: 0 issues in 41 files
- **Security sweep**: Clean (no secrets, token refs are counts only)
- **Degraded modes**: 3 scenarios exercised (empty town_id, SSE disconnect, empty points)
- **529 tests passing** in agents/town/_tests/

### Artifacts from QA

| Artifact | Location | Status |
|----------|----------|--------|
| E712 fix | `agents/town/_tests/test_visualization_contracts.py:438` | `is True` fix |
| Epilogue | `plans/_epilogues/2025-12-14-agent-town-phase6-qa.md` | Complete |

### Tech Debt Identified (Deferred)

| Debt | Risk | Owner |
|------|------|-------|
| `demo_marimo.py` lacks type annotations | Low (notebook cells) | Future cleanup |
| JS tooltip uses innerHTML | Low (internal data) | Future hardening |

---

## Scope

**TEST Focus Areas**:
1. Verify functor law compliance (identity, composition)
2. Test strata: unit → property → integration
3. Law checks for new visualization morphisms
4. Coverage alignment with risks
5. Test-doc reconciliation

**Test Strata to Execute**:

| Stratum | Files | Focus |
|---------|-------|-------|
| Unit | `test_visualization_contracts.py` | ScatterPoint, ScatterState laws |
| Property | `test_functor.py` | Functor identity/composition laws |
| Integration | `test_marimo_integration.py` | Widget-to-cell flow |
| Degraded | `TestDegradedModeTests` | Fallback behaviors |

---

## TEST Manifesto

```
I will verify laws, not just instances.
I will use hotdata over synthetic stubs.
I will mark slow tests, not hide them.
I will capture repro commands for failures.
I will reconcile tests with documentation.
```

---

## Actions

### 1. Run Focused Test Suite
```bash
# Run visualization tests with law checks
uv run pytest agents/town/_tests/test_visualization_contracts.py -v

# Run functor tests
uv run pytest agents/town/_tests/test_functor.py -v

# Run integration tests
uv run pytest agents/town/_tests/test_marimo_integration.py -v

# Run full town suite
uv run pytest agents/town/_tests/ -v --tb=short
```

### 2. Law Check Verification

| Law | Test Location | Expected |
|-----|---------------|----------|
| Functor Identity | `test_functor.py::test_identity_law` | map(id) = id |
| Functor Composition | `test_functor.py::test_composition_law` | map(f).map(g) = map(g∘f) |
| Scatter Roundtrip | `test_visualization_contracts.py::TestWidgetRoundtrip` | to_dict ∘ from_dict = id |
| State Map Equivalence | `test_visualization_contracts.py::TestFunctorLawsContract` | map(f) ≡ with_state(f(state)) |

### 3. Coverage Check
```bash
# Check coverage on visualization module
uv run pytest agents/town/_tests/test_visualization_contracts.py --cov=agents/town/visualization --cov-report=term-missing
```

### 4. Test-Doc Reconciliation

**Checklist**:
- [ ] Tests cover the plan's claimed behavior (CP4-CP6)
- [ ] Spec accurately describes tested behavior
- [ ] Plan is now redundant: evaluate `plans/agent-town/phase5-*.md`
- [ ] If yes, archive candidates identified

---

## Exit Criteria

- [ ] All 529+ tests pass
- [ ] Functor laws verified (identity, composition)
- [ ] Integration tests cover widget→cell flow
- [ ] No flaky tests (or marked appropriately)
- [ ] Coverage aligned with risks (visualization module)
- [ ] Test-doc reconciliation complete
- [ ] Repro commands captured for any issues

---

## Entropy Budget

- Allocated: 0.05
- Draw: `void.entropy.sip(amount=0.05)`
- Purpose: Property test exploration, mutation testing intuition

---

## Branch Candidates

- **Spec promotion**: Functor laws → `spec/protocols/visualization-contracts.md`
- **Enhancement**: Hypothesis property tests for eigenvector drift
- **Tech debt**: Type annotations for demo_marimo.py

---

## Continuation

On success: `⟿[EDUCATE]` — Translate validated behavior into guidance
On blocked: `⟂[TEST:blocked]` — Test failures require resolution
On law violation: `⟂[BLOCKED:law_violation]` — Composition broken

---

*Guard [phase=TEST][entropy=0.05][law_check=true][strata=unit+property+integration]*

---

## Auto-Inducer

⟿[TEST]
/hydrate prompts/agent-town-phase6-test.md
handles: scope=agent-town-phase6-test-gate; qa_status=COMPLETE(ruff_fixed,mypy_clean,529_passing); strata=unit+property+integration; laws=functor_identity+functor_composition+scatter_roundtrip; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:touched,QA:touched,TEST:in_progress}; entropy=0.05
mission: verify correctness with focused test runs; check functor laws; reconcile tests with docs; identify archive candidates.
actions: Bash(uv run pytest agents/town/_tests/test_visualization_contracts.py -v); Bash(uv run pytest agents/town/_tests/test_functor.py -v); Bash(uv run pytest agents/town/_tests/test_marimo_integration.py -v); Bash(uv run pytest agents/town/_tests/ -v); TodoWrite(test_checklist).
exit: all tests pass + laws verified + test-doc reconciled → ledger.TEST=touched; continuation → EDUCATE | test failures → ⟂[TEST:blocked] | law violations → ⟂[BLOCKED:law_violation].

---

**LAW**: This prompt auto-continues. The signifier `⟿[TEST]` triggers immediate execution without human intervention. Halt conditions: test failures, law violations, flaky tests without mitigation, or `⟂[HUMAN_INTERRUPT]`.
