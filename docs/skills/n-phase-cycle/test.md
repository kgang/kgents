---
path: docs/skills/n-phase-cycle/test
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.02
  returned: 0.03
---

# Skill: TEST (N-Phase Cycle)

> Verify correctness, coverage, and lawfulness with intentional depth.

**Difficulty**: Medium  
**Prerequisites**: `qa.md`, `test-patterns.md`, relevant fixtures/hotdata  
**Files Touched**: tests/*, fixtures/hotdata, coverage configs

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → TEST | strata + fixtures | ledger.TEST=touched | entropy.sip(0.05–0.10) | next=EDUCATE
```
- **Minimal artifacts**: selected strata, fixtures/hotdata, test results + repros, ledger update, branch/bounty entries for gaps.
- **Signals**: log tokens/time/entropy + law-check results for `process-metrics.md`.
- **Branch check**: if tests expose API inconsistencies or new work, emit branches before exiting.

---

## Overview
TEST executes targeted suites to confirm laws, behaviors, and regressions. It operationalizes Composable and Generative principles—tests prove the grammar, not just instances.

---

## Step-by-Step

1. **Select strata**: Unit → property → integration → snapshot (prefer hotdata). Emphasize law checks (identity, associativity, operad closure).
2. **Design fixtures**: Use pre-computed richness; avoid synthetic stubs unless isolated.
3. **Run + triage**: Execute focused markers first (`-m "not slow"`), then broader; log failures with repro commands and suspected invariants.
4. **Test doc alignment**: Ensure test documentation matches spec; flag plan drift for archival.

---

## Test-Doc Reconciliation

> *"If tests prove the behavior, specs should capture it. Plans become redundant."*

**During TEST phase, reconcile documentation:**

| If Tests Prove... | Then... |
|-------------------|---------|
| Feature works as designed | Plan can be archived; insights go to spec/skill |
| Feature differs from plan | Update spec, then archive outdated plan |
| Feature requires new patterns | Create skill doc, then archive plan |

**TEST Phase Doc Checklist**:
```markdown
- [ ] Tests cover the plan's claimed behavior
- [ ] Spec accurately describes tested behavior
- [ ] Plan is now redundant: [yes/no]
- [ ] If yes, archive candidate: [path]
```

**Upgrade Path**: Test → passes → spec captures behavior → plan archives → forest shrinks.

---

## Recursive Hologram
- Mini-cycle the suite: PLAN (coverage goals), RESEARCH (gaps), DEVELOP (cases), STRATEGIZE (order), TEST (run).
- Register new laws/fixtures via `meta-skill-operad.md` so future mutations remain composable.

---

## Accursed Share (Entropy Budget)

TEST reserves 5-10% for exploration:

- **Property test intuition**: What invariants feel true? Write a hypothesis even if coverage isn't required.
- **Mutation testing**: Manually break the code—does the test catch it? If not, the test is weak.
- **Hotdata discovery**: Is there real-world data that could replace synthetic fixtures?
- **Flaky investigation**: If a test is flaky, spend entropy understanding why before marking it slow.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`

---

## Verification
- Tests pass with coverage aligned to risks.
- Law checks present for new morphisms.
- Repro notes captured for any flaky/slow cases.

---

## Common Pitfalls

- **Synthetic stubs over hotdata**: Per AD-004, use pre-computed LLM outputs. Synthetic data misses the soul.
- **Testing instances, not grammar**: Good tests verify laws (identity, associativity). Bad tests check specific strings.
- **Ignoring flaky tests**: A flaky test is a test that sometimes lies. Fix or delete, never ignore.
- **Missing law checks**: Every new agent/morphism needs identity and associativity tests. Category laws are not optional.
- **Coverage theater**: 100% line coverage means nothing if you're not testing invariants. Prefer property-based testing.
- **Slow tests in fast path**: Mark slow tests with `@pytest.mark.slow`. Default runs should complete in <30s.

---

## Hand-off
Next: `educate.md` to translate validated behavior into guidance.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../test-patterns.md`, `../hotdata-pattern.md`

---

## Continuation Generator

Emit this when exiting TEST:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[EDUCATE]
/hydrate
handles: results=${test_results_summary}; coverage=${coverage_summary}; laws=${law_check_results}; flaky=${flaky_notes}; findings=${test_findings}; repro=${repro_commands}; ledger={TEST:touched}; branches=${branch_notes}
mission: translate validated behavior into guidance; keep AGENTESE handles explicit; include degraded paths.
actions: map audiences; update docs/prompts/quickstarts with runnable examples + hotdata; add repro commands.
exit: docs/prompts updated or skip debt declared; ledger.EDUCATE=touched; continuation → MEASURE.

# Halt conditions:
⟂[TEST:blocked] Test failures require resolution before EDUCATE
⟂[BLOCKED:law_violation] Law checks failed; composition broken
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${test_results_summary}`, `${coverage_summary}`, `${law_check_results}`, `${flaky_notes}`, `${test_findings}`, `${repro_commands}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../test-patterns.md`, `../hotdata-pattern.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
