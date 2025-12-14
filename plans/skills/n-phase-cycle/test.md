# Skill: TEST (N-Phase Cycle)

> Verify correctness, coverage, and lawfulness with intentional depth.

**Difficulty**: Medium  
**Prerequisites**: `qa.md`, `test-patterns.md`, relevant fixtures/hotdata  
**Files Touched**: tests/*, fixtures/hotdata, coverage configs

---

## Overview
TEST executes targeted suites to confirm laws, behaviors, and regressions. It operationalizes Composable and Generative principles—tests prove the grammar, not just instances.

---

## Step-by-Step

1. **Select strata**: Unit → property → integration → snapshot (prefer hotdata). Emphasize law checks (identity, associativity, operad closure).  
2. **Design fixtures**: Use pre-computed richness; avoid synthetic stubs unless isolated.  
3. **Run + triage**: Execute focused markers first (`-m "not slow"`), then broader; log failures with repro commands and suspected invariants.

---

## Recursive Hologram
- Mini-cycle the suite: PLAN (coverage goals), RESEARCH (gaps), DEVELOP (cases), STRATEGIZE (order), TEST (run).  
- Register new laws/fixtures via `meta-skill-operad.md` so future mutations remain composable.

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

## Changelog
- 2025-12-13: Initial version.
