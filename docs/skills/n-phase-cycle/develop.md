---
path: docs/skills/n-phase-cycle/develop
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

# Skill: DEVELOP (N-Phase Cycle)

> Convert research into sharpened specs, APIs, and operable contracts.

**Difficulty**: Medium  
**Prerequisites**: `research.md`, `spec/principles.md`, relevant ADs (001-004)  
**Files Touched**: specs, docs/skills/, design scratchpads; implementation deferred

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → DEVELOP | contracts to draft | laws to assert | ledger.DEVELOP=touched | entropy.sip(0.05–0.10) | next=STRATEGIZE
```
- **Minimal artifacts**: chosen puppet/functor/operad, inputs/outputs/errors, laws, examples, risk notes, ledger + branch candidates.
- **Signals**: log law assertions + token/time/entropy for `process-metrics.md`; capture branch handles if alternative designs emerge.
- **Branch check**: if multiple architectures emerge, classify before leaving; emit bounty or branch handle.

---

## Overview
DEVELOP is design compression: minimal specs that can regenerate code. It enforces Generative and Tasteful principles—only the necessary primitives and operads survive.

---

## Step-by-Step

1. **Select puppets**: Choose representation (operad, functor, sheaf, puppet) that makes the problem tractable.  
2. **Define contracts**: Inputs/outputs, laws (identity/associativity), error surfaces, hotdata hooks, privacy/ethics constraints.  
3. **Prototype in spec**: Draft examples, reference skills, and edge cases. Annotate risks and decisions for STRATEGIZE.

---

## Recursive Hologram
- Run a micro PLAN→RESEARCH→DEVELOP on the spec draft: what is the smallest generative grammar that still composes?
- Use `meta-skill-operad.md` to register new primitives/operations; ensure identity and associativity hold for future mutations.

---

## Accursed Share (Entropy Budget)

DEVELOP reserves 5-10% for exploration:

- **Alternative representations**: Try 2-3 type signatures before committing. The best interface often isn't the first.
- **Law discovery**: What invariants should hold? Sketch property tests even if you don't run them yet.
- **Composition experiments**: Can this agent compose with existing functors? Try `Agent >> Flux` or `Maybe >> Agent`.
- **Puppet swapping**: What if we modeled this as a different category? (State vs Reader vs Writer)

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`

---

## Forest Adapter (dry-run contract)
- Map existing forest CLI functions to AGENTESE handles without code changes: `forest_status()` → `concept.forest.manifest`; `forest_update()` → `concept.forest.refine`; epilogue stream → `time.forest.witness`; dormant-picker → `void.forest.sip`; plan scaffold → `self.forest.define`.  
- Observer roles gate affordances: `ops` (update/define), `meta` (manifest/witness/refine), `guest` (manifest only).  
- Dry-run prompt: "Wrap forest_status/forest_update to emit single-handle responses; no arrays; return lawfulness checks (identity/assoc) as metadata only."

---

## Verification
- Spec/contract exists with examples and invariants.  
- Laws stated and testable; blockers/risks documented.  
- Work ready for sequencing in STRATEGIZE.

---

## Hand-off
Next: `strategize.md` to order delivery and choose leverage points.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../polynomial-agent.md`
- `../agentese-path.md`

---

## Continuation Generator

Emit this when exiting DEVELOP:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[STRATEGIZE]
/hydrate
handles: specs=${specs_created}; laws=${laws_stated}; risks=${risks_noted}; examples=${examples_count}; decisions=${design_decisions}; ledger={DEVELOP:touched}; branches=${branch_notes}
mission: order chunks for leverage; set owners/interfaces/checkpoints; prep decision gates.
actions: impact/effort + dependencies; parallel tracks w/ interfaces; metrics to watch; run lookback-revision.
exit: ordered backlog + owners/checkpoints; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE.

# Halt conditions:
⟂[BLOCKED:law_violation] Proposed design violates category laws (identity/associativity)
⟂[BLOCKED:composition_failure] Spec cannot compose with existing agents
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${specs_created}`, `${laws_stated}`, `${risks_noted}`, `${examples_count}`, `${design_decisions}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../polynomial-agent.md`
- `../agentese-path.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
