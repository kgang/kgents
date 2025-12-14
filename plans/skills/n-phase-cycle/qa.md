# Skill: QA (N-Phase Cycle)

> Gatekeeping for quality, hygiene, and readiness before formal testing.

**Difficulty**: Easy-Medium  
**Prerequisites**: `implement.md`, repo QA standards, HYDRATE gotchas  
**Files Touched**: QA checklist, minor fixes in code/docs/tests

---

## Overview
QA verifies the work is clean, explainable, and reversible. It ensures Transparent Infrastructure and Ethical principles are visible before deeper testing or release.

---

## Step-by-Step

1. **Checklist pass**: Run lint/mypy/unit tests; check logging clarity, error messages, degraded-mode behavior, and privacy defaults.  
2. **Narrate intent**: Ensure commit/notes explain what changed and why (tasteful, curated).  
3. **Risk sweep**: Identify failure domains, feature flags, rollback plan, and data migration safety.

---

## Recursive Hologram
- Apply PLAN→RESEARCH→DEVELOP to the QA checklist itself: are gates still sufficient? any new invariants to add?  
- Use `meta-skill-operad.md` to mutate the checklist lawfully; preserve identity (baseline gates) and associativity (order-independent checks).

---

## Verification
- QA checklist completed; no silent degradations.  
- Reversible state recorded; degraded-mode paths exercised.  
- Ready for focused `test.md` execution.

---

## Hand-off
Next: `test.md` to verify correctness and coverage depth.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../test-patterns.md`

---

## Changelog
- 2025-12-13: Initial version.
