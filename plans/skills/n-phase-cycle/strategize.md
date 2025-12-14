---
path: plans/skills/n-phase-cycle/strategize
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
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: STRATEGIZE (N-Phase Cycle)

> Choose the order of moves that maximizes leverage and resilience.

**Difficulty**: Medium  
**Prerequisites**: `develop.md`, `plans/principles.md` (attention budgeting)  
**Files Touched**: sprint notes, plan chunk sequencing, risk/impact matrix

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → STRATEGIZE | backlog to order | interfaces/owners | ledger.STRATEGIZE=touched | entropy.sip(0.05) | next=CROSS-SYNERGIZE
```
- **Minimal artifacts**: ordered backlog with dependencies/owners/checkpoints, parallel track interfaces, metrics to watch, branch decisions logged, ledger updated.
- **Signals**: record tokens/time/entropy + branch count + decision gates for `process-metrics.md`.
- **Branch check**: classify and emit handles for parallel/deferred tracks before exiting.

---

## Overview
STRATEGIZE translates design into a path: which chunks land first, what runs in parallel, and how to minimize risk. It aligns with Heterarchical and Transparent Infrastructure principles—leadership is contextual and communication is explicit.

---

## Step-by-Step

1. **Prioritize by leverage**: Sequence chunks by impact/effort and dependency graph; reserve Accursed Share buffer.  
2. **Parallelize safely**: Identify parallel tracks with clear interfaces and ownership (human/agent).  
3. **Define signals**: Establish checkpoints, metrics to watch early, and decision gates for CROSS-SYNERGIZE and IMPLEMENT.
4. **Run an oblique lookback**: Execute `lookback-revision.md` on the strategy to surface frame errors/double-loop shifts before locking the order.

---

## Recursive Hologram
- Mini-cycle the strategy itself: PLAN (goal), RESEARCH (constraints), DEVELOP (ordering), STRATEGIZE (revision).
- Use `meta-skill-operad.md` to treat strategy as morphisms; ensure refactors preserve composition (no orphaned chunks).

---

## Accursed Share (Entropy Budget)

STRATEGIZE reserves 5-10% for exploration:

- **Order experiments**: Try reverse order or random order—sometimes dependencies reveal themselves.
- **Risk probing**: What's the scariest chunk? Consider doing it first to de-risk early.
- **Parallel discovery**: Which chunks are secretly independent? Parallelization often hides.
- **Abort criteria**: What would make us stop this track entirely? Name it now.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`

---

## Verification
- Ordered backlog with owners, dependencies, and checkpoints.  
- Parallel tracks identified with interfaces.  
- Ready to discover combinations in CROSS-SYNERGIZE.

---

## Hand-off
Next: `cross-synergize.md` to explore compositions and entanglements.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `lookback-revision.md`
- `../plan-file.md`

---

## Continuation Generator

Emit this when exiting STRATEGIZE:

```markdown
/hydrate
# CROSS-SYNERGIZE ← STRATEGIZE
handles: backlog=${ordered_chunks}; parallel=${parallel_tracks}; checkpoints=${checkpoints}; gates=${decision_gates}; interfaces=${track_interfaces}; decisions=${strategy_decisions}; ledger=${phase_ledger}; branches=${branch_notes}
mission: hunt compositions/entanglements; probe with hotdata; select law-abiding pipelines.
actions: enumerate morphisms; micro-prototype with fixtures; test identity/associativity; log tokens/time/entropy/law-checks.
exit: chosen comps + rationale; rejected paths noted; interfaces ready; ledger.CROSS-SYNERGIZE=touched; continuation → IMPLEMENT.
```

Template vars: `${ordered_chunks}`, `${parallel_tracks}`, `${checkpoints}`, `${decision_gates}`, `${track_interfaces}`, `${strategy_decisions}`, `${phase_ledger}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `lookback-revision.md`
- `../plan-file.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
