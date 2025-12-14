---
path: plans/skills/n-phase-cycle/phase-accountability
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

# Meta Skill: Phase Accountability

> *"Every phase touched leaves a trace. Every phase skipped leaves a debt."*

**Difficulty**: Easy
**Prerequisites**: `metatheory.md`, understanding of full 11-phase cycle
**Files Touched**: Phase output artifacts, `plans/_epilogues/`, `plans/meta.md`

---

## The Accountability Principle

The N-Phase Cycle is not a buffet. When the full cycle is declared (Crown Jewel work), **every phase must be touched**—even if briefly. An agent who skips a phase without explicit acknowledgment is **liable** for any consequences that would have been caught by that phase.

---

## What "Touched" Means

A phase is considered "touched" if any of the following occur:

| Minimal Touch | Full Engagement |
|---------------|-----------------|
| Phase mentioned in continuation prompt | Phase has its own section in output |
| Explicit skip declaration with reason | Phase produces artifacts |
| "Nothing to do here" documented | Phase triggers learnings in meta.md |

**The minimum bar**: Acknowledge the phase. State what you did (or explicitly didn't do) and why.

---

## The Liability Protocol

### When a Phase is Skipped Without Declaration

If a later phase fails or produces defects, and the skipped phase would have caught the issue, the agent is **liable**:

1. **Demotion signal**: The agent's track record notes the skip-induced failure
2. **Remediation**: The agent must execute the skipped phase retroactively
3. **Meta-learning**: The failure is recorded in `plans/meta.md` as anti-pattern

### How Liability is Assessed

| Skipped Phase | Typical Consequence |
|---------------|---------------------|
| PLAN | Scope creep, wasted work |
| RESEARCH | Duplicate work, missed prior art |
| DEVELOP | Brittle architecture, law violations |
| STRATEGIZE | Suboptimal ordering, blocked tracks |
| CROSS-SYNERGIZE | Missed leverage, isolated work |
| IMPLEMENT | (cannot be skipped) |
| QA | Bugs shipped, security vulnerabilities |
| TEST | Regressions, coverage gaps |
| EDUCATE | Unusable features, poor documentation |
| MEASURE | Invisible impact, no improvement signal |
| REFLECT | Repeated mistakes, no learning |

---

## Explicit Skip Protocol

To skip a phase without liability, declare:

```markdown
## PHASE: [Phase Name] — EXPLICIT SKIP

**Reason**: [Why this phase adds no value for this task]
**Risk accepted**: [What could go wrong, acknowledged]
**Fallback**: [What will catch issues if this skip was wrong]
```

**Examples of valid skips**:

```markdown
## EDUCATE — EXPLICIT SKIP

**Reason**: Internal refactor with no user-facing changes.
**Risk accepted**: Maintainers may not understand the change.
**Fallback**: Code comments serve as minimal documentation.
```

```markdown
## CROSS-SYNERGIZE — EXPLICIT SKIP

**Reason**: Single-track work with no obvious composition partners.
**Risk accepted**: May miss leverage with dormant plans.
**Fallback**: Bounty board review during REFLECT will surface missed synergies.
```

---

## The Full Cycle Trace

For Crown Jewel work (full 11-phase cycle declared), the epilogue must contain a **Phase Trace**:

```markdown
## Phase Trace

| Phase | Status | Key Output |
|-------|--------|------------|
| PLAN | ✓ | Scope defined, chunks identified |
| RESEARCH | ✓ | 15 files mapped, 3 blockers surfaced |
| DEVELOP | ✓ | Contract spec, 2 law assertions |
| STRATEGIZE | ✓ | 5 chunks prioritized |
| CROSS-SYNERGIZE | ⊘ skip | Internal work, no composition |
| IMPLEMENT | ✓ | 342 lines, 18 tests |
| QA | ✓ | mypy clean, ruff clean |
| TEST | ✓ | 743 → 761 tests |
| EDUCATE | ⊘ skip | Internal, comments sufficient |
| MEASURE | ⊘ defer | Metrics in next cycle |
| REFLECT | ✓ | 3 learnings, 1 bounty |

**Skips declared**: CROSS-SYNERGIZE, EDUCATE, MEASURE (deferred)
**Liability acknowledged**: Yes
```

---

## Ledger Snippet (plan header ready)

Embed a compact ledger in each plan header or scratch note to make `_forest` reconciliation trivial:

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: known pattern
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: single-track
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: skipped  # reason: internal change
  MEASURE: deferred  # reason: metrics lag
  REFLECT: touched
entropy:
  planned: 0.07
  spent: 0.05
  returned: 0.02
```

**Rules**:
- `touched | skipped | deferred` only; always include a reason for non-touch.
- Track entropy sip/pour to enforce the Accursed Share budget.
- Keep it terse; this is a pheromone trace, not prose.
- Epilogue-ready example:
  ```
  phase_trace: [{phase: PLAN, status: touched}, {phase: RESEARCH, status: touched}, ...]
  ledger: {PLAN: touched, ...}
  entropy: {planned: 0.07, spent: 0.05, returned: 0.02}
  ```
  `_forest.md` ingestion expects these keys; keep formats consistent across sessions.

**AGENTESE ledger micro-prompt (per phase)**:
- `concept.forest.manifest[phase=PLAN][minimal_output=true]@span=forest_plan` → note scope + ledger presence.
- `void.entropy.sip[phase=RESEARCH][entropy=0.07]@span=entropy_sip` → update `entropy.spent`.
- `concept.forest.refine[phase=DEVELOP][rollback=true][law_check=true]@span=forest_dev` → mutate header with rollback token.
- `time.forest.witness[phase=REFLECT][law_check=true]@span=forest_trace` → capture phase trace + ledger delta.

## Demotion Criteria

An agent may be "demoted" (reduced trust, increased oversight) if:

1. **Repeated skip-induced failures** (3+ in a session)
2. **Skip without declaration** (any phase silently ignored)
3. **False completion claims** (said "done" but tests fail)
4. **Liability denial** (refuses to acknowledge skip consequences)

Demotion is not permanent. Remediation via:
- Executing full cycle with explicit trace
- Retroactive phase execution for skipped work
- Meta-learning entry documenting the failure pattern

---

## The Three-Phase Escape Valve

The three-phase cycle (SENSE→ACT→REFLECT) is a **valid compression**, not a liability dodge:

- SENSE encompasses PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE
- ACT encompasses IMPLEMENT, QA, TEST, EDUCATE
- REFLECT encompasses MEASURE, REFLECT

Using three-phase is not skipping—it's compressing. The agent is still accountable for the work covered by each macro-phase.

**Example**: If using three-phase and ACT fails due to missing QA, the agent is liable because QA is within ACT's scope.

---

## Recursive Hologram

This accountability skill applies to itself:

- Did you PLAN accountability tracking?
- Did you RESEARCH prior art on process accountability?
- Did you DEVELOP the skip protocol?
- Did you IMPLEMENT the trace format?
- Did you TEST that traces are captured?
- Did you REFLECT on whether this protocol is burdensome?

---

## Verification

- [ ] Full cycle work has Phase Trace in epilogue
- [ ] Skipped phases have Explicit Skip declaration
- [ ] Risk accepted is specific, not generic
- [ ] Fallback mechanism is named
- [ ] No silent skips (phases missing without declaration)

---

## Related Skills

- `metatheory.md` — Why phases exist
- `three-phase.md` — Valid compression
- `reflect.md` — Where accountability is assessed
- `lookback-revision.md` — Where skip-induced failures are caught
- `detach-attach.md` — Handle creation includes trace

---

## Changelog

- 2025-12-13: Initial version (per user request for accountability protocol).
