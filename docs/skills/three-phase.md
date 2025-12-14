---
path: docs/skills/three-phase
status: active
progress: 0
last_touched: 2025-12-14
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

# Skill: Three-Phase Cycle

> The default implementation lifecycle: SENSE → ACT → REFLECT

**Difficulty**: Easy
**Prerequisites**: None
**Files Touched**: Varies by task

---

## Overview

The Three-Phase Cycle compresses the full 11-phase N-Phase Cycle into three macro-phases without loss of power. Use this for most tasks. Escalate to full 11-phase only for Crown Jewels (multi-week, multi-agent projects).

```
SENSE → ACT → REFLECT → (loop)
```

---

## The Three Phases

### SENSE (Understanding)

Compress: Plan, Research, Develop, Strategize, Cross-Synergize

**Purpose**: Understand the terrain before acting.

**Activities**:
- Frame intent and scope
- Map existing code/patterns
- Identify blockers and dependencies
- Find synergies with other work

**Exit Criteria**:
- Clear understanding of what needs to change
- Blockers identified (or confirmed none)
- Approach chosen

**AGENTESE Context**: `world.*` (external), `concept.*` (specs)

### ACT (Execution)

Compress: Implement, QA, Test, Educate

**Purpose**: Ship working code with quality.

**Activities**:
- Write implementation
- Run quality checks (mypy, tests)
- Verify coverage
- Document if needed

**Exit Criteria**:
- Code works
- Tests pass
- No regressions

**AGENTESE Context**: `self.*` (state), `world.*` (code)

### REFLECT (Learning)

Compress: Measure, Reflect, Re-Metabolize

**Purpose**: Extract learnings, seed next cycle.

**Activities**:
- Note what worked and what didn't
- Append insights to `meta.md` (if atomic and generalizable)
- Write epilogue for next session
- Generate continuation prompt if needed

**Exit Criteria**:
- Learnings captured
- Session handoff complete

**AGENTESE Context**: `time.*` (traces), `void.*` (entropy/gratitude)

---

## When to Use Three-Phase

| Task Type | Use Three-Phase? |
|-----------|------------------|
| Bug fix | Yes |
| Feature (single session) | Yes |
| Refactoring | Yes |
| Feature (multi-session, well-understood) | Yes |
| Crown Jewels (multi-week, architectural) | No → Use 11-Phase |
| Research/exploration only | Yes (SENSE only, skip ACT) |

---

## When to Escalate to 11-Phase

Use the full N-Phase Cycle (`docs/skills/n-phase-cycle/`) when:

1. **Crown Jewels**: Priority 10.0, multi-week scope
2. **Multi-agent coordination**: Multiple humans/AIs need sync points
3. **Architectural decisions**: Changes that affect many components
4. **Novel territory**: No existing patterns to follow

---

## Recursive Hologram

The Three-Phase Cycle is itself a hologram of the Three-Phase Cycle:

- **SENSE this skill**: What tasks am I facing? Is Three-Phase sufficient?
- **ACT with this skill**: Execute the phases boldly
- **REFLECT on this skill**: Did compression lose information? Should I have used 11-Phase?

Each phase also contains the full cycle:
- SENSE: mini-SENSE (what do I need to understand?) → mini-ACT (read files) → mini-REFLECT (is understanding complete?)
- ACT: mini-SENSE (what's the approach?) → mini-ACT (write code) → mini-REFLECT (did it work?)
- REFLECT: mini-SENSE (what happened?) → mini-ACT (write notes) → mini-REFLECT (is handoff complete?)

---

## Continuation Generation

Use the auto-inducer signifiers (`⟿`/`⟂`) for condensed handoffs. Keep the snap prompts to five lines (Minimal Output) and include ledger + entropy to preserve accountability.

### Snap Prompts (Auto-Inducer Ready)

- **SENSE → ACT**
```markdown
⟿[ACT]
/hydrate
handles: senses=${artifacts}; ledger={SENSE:touched}; entropy=${entropy_spent}/${entropy_remaining}; branches=${branch_notes}
mission: execute the chosen approach; line up QA/TEST intent; keep scope to one diff.
exit: draft diff + QA/TEST plan noted; continuation → REFLECT.
⟂[BLOCKED:scope_unclear] need a tighter target before ACT
```

- **ACT → REFLECT**
```markdown
⟿[REFLECT]
/hydrate
handles: impl=${diff_handles}; ledger={ACT:touched}; entropy=${entropy_spent}/${entropy_remaining}; qa=${qa_status}
mission: capture learnings/debts/metrics; decide whether to loop or detach.
exit: learnings + debts recorded; continuation → PLAN or DETACH decision.
⟂[TEST:blocked] checks failing; resolve before REFLECT
```

- **REFLECT → PLAN | DETACH**
```markdown
⟿[PLAN]
/hydrate
handles: learnings=${notes}; ledger={REFLECT:touched}; entropy=${entropy_spent}/${entropy_remaining}; branches=${branch_notes}
mission: seed next SENSE with scope, non-goals, exits, and any branch handles.
exit: PLAN ledger seeded; continuation → SENSE.
⟂[DETACH:cycle_complete] scope exhausted; epilogue ready | ⟂[DETACH:awaiting_human] decision needed
```

### Full Prompt (Context-Rich)

At the end of a session, generate a continuation prompt with:

```markdown
# Continuation: [Task Name] (Phase: SENSE|ACT|REFLECT)

## ATTACH

/hydrate

---

## Context from Previous Phase

**What was accomplished**: [Summary]

**Key Decisions Made**: [Decisions]

---

## Your Mission ([Phase] Phase)

[Specific tasks for next session]

---

## Exit Criteria

- [ ] Criterion 1
- [ ] Criterion 2

---

## Continuation Imperative

Upon completing this phase, generate a prompt for the next observer.
```

---

## AGENTESE Mapping

| Phase | Primary Context | Secondary |
|-------|-----------------|-----------|
| SENSE | `world.*`, `concept.*` | `time.*.witness` |
| ACT | `self.*`, `world.*` | `void.entropy.sip` |
| REFLECT | `time.*` | `void.gratitude.tithe` |

---

## Example: Bug Fix

### SENSE
```
- Read the failing test
- Read the code under test
- Identify the root cause
```

### ACT
```
- Write the fix
- Run tests
- Verify mypy passes
```

### REFLECT
```
- Note: "Edge case with empty input wasn't handled"
- No meta.md append (too specific)
- No epilogue needed (single-session task)
```

---

## Related Skills

- [n-phase-cycle/](n-phase-cycle/README.md) — Full 11-phase for Crown Jewels
- [plan-file](plan-file.md) — Writing plan files
- [reconciliation-session](reconciliation-session.md) — Forest state audit

---

## Changelog

- 2025-12-13: Added Recursive Hologram section (meta-re-metabolize).
- 2025-12-13: Initial version (extracted from HYDRATE.md Three-Phase section)
