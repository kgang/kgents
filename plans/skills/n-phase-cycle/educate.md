---
path: plans/skills/n-phase-cycle/educate
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
  EDUCATE: touched
  MEASURE: touched
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.035
  returned: 0.015
---

# Skill: EDUCATE (N-Phase Cycle)

> Teach humans and agents how to wield the shipped capability.

**Difficulty**: Easy  
**Prerequisites**: `test.md`, user journey knowledge, docs style guides  
**Files Touched**: docs/, prompts/, plans/skills/, release notes

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → EDUCATE | audiences + artifacts | ledger.EDUCATE=touched | entropy.sip(0.05–0.10) | next=MEASURE
```
- **Minimal artifacts**: audience map, docs/prompts/quickstarts with runnable examples or explicit skip debt, degraded-mode notes, ledger update, branch/bounty entries for missing infra.
- **Signals**: log tokens/time/entropy + adoption hooks added for `process-metrics.md`.
- **Branch check**: emit follow-up branches for observability gaps or missing demos.

---

## Overview
EDUCATE converts validated behavior into accessible guidance (operator guides, prompts, demos). It fulfills Ethical and Joy-Inducing principles by preserving agency and delight.

---

## Step-by-Step

1. **Audience mapping**: Identify personas (operator, maintainer, contributor) and their AGENTESE contexts.  
2. **Artifacts**: Update docs, quickstarts, prompts, and demo data using pre-computed richness. Highlight degraded-mode behavior and safety notes.  
3. **Support scripts**: Add helper CLI snippets or `kg` invocations; ensure observability cues align with Transparent Infrastructure.

---

## Recursive Hologram
- PLAN→RESEARCH→DEVELOP the docs themselves: what minimum grammar communicates the capability?
- Use `meta-skill-operad.md` to keep documentation morphisms composable (snippets as reusable arrows).

---

## Accursed Share (Entropy Budget)

EDUCATE reserves 5-10% for exploration:

- **Alternative explanations**: Try explaining to three different personas. One framing will click.
- **Demo discovery**: What's the smallest runnable example? Sometimes the demo IS the documentation.
- **Failure documentation**: What happens when it breaks? Users need error paths too.
- **Personality injection**: Where can joy live in this documentation? Find the human moment.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`

---

## Verification
- Documentation/prompt updates land with runnable examples.  
- Warnings, degraded paths, and personality coordinates noted.  
- Users can reproduce validated behaviors without inside knowledge.

---

## Hand-off
Next: `measure.md` to track whether education changed outcomes.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../hotdata-pattern.md`

---

## Continuation Generator

Emit this when exiting EDUCATE:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[MEASURE]
/hydrate
handles: docs=${docs_created}; quickstarts=${quickstarts}; scripts=${support_scripts}; audiences=${audiences_mapped}; summary=${education_summary}; degraded=${degraded_paths_docs}; ledger={EDUCATE:touched}; branches=${branch_notes}
mission: instrument adoption/latency/error signals; wire dashboards/fixtures; capture baselines.
actions: define leading indicators via process-metrics schema; add telemetry/flags; create hotloadable dashboards; validate data quality.
exit: metrics live + baselines captured; ledger.MEASURE=touched; continuation → REFLECT.

# Halt conditions (rare for EDUCATE):
⟂[BLOCKED:missing_infra] Required docs infrastructure missing
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${docs_created}`, `${quickstarts}`, `${support_scripts}`, `${audiences_mapped}`, `${education_summary}`, `${degraded_paths_docs}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../hotdata-pattern.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
