---
path: docs/skills/n-phase-cycle/qa
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

# Skill: QA (N-Phase Cycle)

> Gatekeeping for quality, hygiene, and readiness before formal testing.

**Difficulty**: Easy-Medium  
**Prerequisites**: `implement.md`, repo QA standards, HYDRATE gotchas  
**Files Touched**: QA checklist, minor fixes in code/docs/tests

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → QA | checks=mypy+ruff+security | ledger.QA=touched | entropy.sip(0.05) | next=TEST
```
- **Minimal artifacts**: checklist results, security notes, degraded-mode exercise, ledger update, branch/bounty entries for tech debt.
- **Signals**: log tokens/time/entropy + law-check status for `process-metrics.md`.
- **Branch check**: emit refactor/infra branches if QA exposes debt.

---

## Overview
QA verifies the work is clean, explainable, and reversible. It ensures Transparent Infrastructure and Ethical principles are visible before deeper testing or release.

---

## Step-by-Step

1. **Checklist pass**: Run lint/mypy/unit tests; check logging clarity, error messages, degraded-mode behavior, and privacy defaults.
2. **Narrate intent**: Ensure commit/notes explain what changed and why (tasteful, curated).
3. **Risk sweep**: Identify failure domains, feature flags, rollback plan, and data migration safety.
4. **Documentation hygiene**: Audit plan files for archival or spec promotion (see below).

---

## Documentation Hygiene (Archiving Gate)

> *"Planning docs are scaffolding. Ship them or demolish them."*

**Every QA pass must audit associated planning documentation:**

| Check | Action if True |
|-------|----------------|
| Plan achieved its goal | **Archive** to `plans/_archive/` or **Promote** distilled insights to `spec/` |
| Plan is >7 days old with <50% progress | **Re-assess**: still relevant? Merge, archive, or re-scope |
| Plan duplicates another plan | **Merge** into single source of truth, archive redundant |
| Plan's insights are spec-worthy | **Upgrade**: distill to `spec/` or `docs/skills/`, then archive original |

**The Molasses Test**: If a planning doc can't be deleted in 30 days, it's either:
- Needed (promote to spec/skill)
- Abandoned (archive with reason)
- Duplicative (merge and archive)

**QA Checklist Addition**:
```markdown
- [ ] Plans touched during this work: [list]
- [ ] Archive candidates identified: [list or "none"]
- [ ] Spec promotion candidates: [list or "none"]
```

---

## Recursive Hologram
- Apply PLAN→RESEARCH→DEVELOP to the QA checklist itself: are gates still sufficient? any new invariants to add?
- Use `meta-skill-operad.md` to mutate the checklist lawfully; preserve identity (baseline gates) and associativity (order-independent checks).

---

## Accursed Share (Entropy Budget)

QA's entropy is spent on:

- **Edge case exploration**: Try degraded modes that might fail. That's where bugs hide.
- **Alternative lint rules**: Sometimes ruff suggests a refactor. Follow it briefly—it might be right.
- **Graceful degradation paths**: Document what happens when dependencies are missing.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`

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

## Continuation Generator

Emit this when exiting QA:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[TEST]
/hydrate
handles: qa=${qa_checklist_status}; static=${static_analysis_results}; security=${security_notes}; degraded=${degraded_mode_tests}; findings=${qa_findings}; rollback=${rollback_plan}; ledger={QA:touched}; branches=${branch_notes}
mission: design/run tests that prove grammar + invariants; prefer hotdata; record repros.
actions: choose strata (unit/property/integration/snapshot); design fixtures; uv run pytest -m "not slow" -v.
exit: tests aligned to risks + ledger.TEST=touched; repro notes captured; continuation → EDUCATE.

# Halt conditions:
⟂[QA:blocked] mypy/ruff/security errors require resolution before TEST
⟂[BLOCKED:security_issue] Security vulnerability detected; human review required
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${qa_checklist_status}`, `${static_analysis_results}`, `${security_notes}`, `${degraded_mode_tests}`, `${qa_findings}`, `${rollback_plan}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../test-patterns.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (meta-re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
