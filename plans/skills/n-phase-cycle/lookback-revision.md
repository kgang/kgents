---
path: plans/skills/n-phase-cycle/lookback-revision
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

# Skill: Lookback Revision (Oblique Cycle)

> Structured, unbiased retrospection that runs orthogonal to implementation to prevent hindsight bias and implementation drag.

**Difficulty**: Medium  
**Prerequisites**: `reflect.md`, reflective practice models (Schön: reflection-on/in-action; Argyris double-loop), `meta-skill-operad.md`  
**Files Touched**: plans/_epilogues/, plans/_bounty.md, optional notes under plans/skills/n-phase-cycle/

---

## Overview
Lookback Revision is a parallel cycle that critiques decisions after selected phases (e.g., after STRATEGIZE, after MEASURE) using an **oblique metabolizer**—a process deliberately detached from current implementation pressures. It draws from reflective practice research (Schön, Kolb, Gibbs) to encourage double-loop learning (changing objectives/frames, not just actions).

---

## Step-by-Step

1. **Trigger selection**: Run after STRATEGIZE, MEASURE, and REFLECT, or when risk/entropy crosses a threshold (major pivot, large token burn, high defect rate).  
2. **Oblique framing**: Assign a separate reviewer/agent identity (or randomized prompts) to avoid implementation anchoring; use the Gibbs cycle (Describe → Feelings → Evaluation → Analysis → Conclusions → Action plan).  
3. **Double-loop scan**: Identify where goals/frames were wrong, not just execution. Capture counterfactuals and alternative puppets (e.g., swap operad, change functor).  
4. **Metabolize outputs**: Route actionable changes to PLAN/STRATEGIZE, and archive divergent ideas in Accursed Share rotation. Resolve or open bounties for systemic issues.

---

## Metrics (process health)
- Revision cadence: #lookbacks / phase or per K tokens.  
- Frame shifts: count of objectives reframed (double-loop) vs single-loop fixes.  
- Decision reversals caught vs shipped.  
- Token/time saved from avoided rework (estimate).  
- Sentiment/entropy delta: divergence between implementer perspective and oblique reviewer.

---

## Recursive Hologram
- PLAN→RESEARCH→DEVELOP this lookback itself: Are prompts stale? Is the oblique persona still unbiased?  
- Use `meta-skill-operad.md` to mutate the lookback prompts lawfully; ensure identity (no-op review) and associativity (order of reviews does not change conclusions).

---

## Verification
- Lookback notes captured with counterfactuals and action deltas.  
- At least one double-loop adjustment considered.  
- Bounties posted/updated for systemic gaps.

---

## Hand-off
Feed changes to `plan.md`/`strategize.md`; schedule `meta-re-metabolize.md` if patterns repeat.

---

## Related Skills
- `meta-skill-operad.md`  
- `meta-re-metabolize.md`  
- `reflect.md`

---

## Changelog
- 2025-12-13: Initial version (integrates Schön/Kolb/Gibbs reflective patterns).
