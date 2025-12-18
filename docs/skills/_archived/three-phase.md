# Skill: Three-Phase Cycle

> The primary implementation lifecycle: **UNDERSTAND → ACT → REFLECT**

**Difficulty**: Easy
**Prerequisites**: None

---

## Overview

The Three-Phase Cycle is the **default workflow** for all development work. Use it for everything unless you explicitly need the full 11-phase ceremony.

```
UNDERSTAND → ACT → REFLECT → (loop)
```

---

## UNDERSTAND

**Purpose**: Map the terrain before acting.

**Activities**:
- Frame intent and scope
- Read relevant code/patterns
- Identify blockers and dependencies
- Choose approach

**Exit**: Clear understanding of what needs to change.

---

## ACT

**Purpose**: Ship working code with quality.

**Activities**:
- Write implementation
- Run quality checks (mypy, ruff, tests)
- Verify coverage
- Document if user-facing

**Exit**: Code works, tests pass.

---

## REFLECT

**Purpose**: Extract learnings, seed next cycle.

**Activities**:
- Note what worked and what didn't
- Append atomic insights to `meta.md` if generalizable
- Generate continuation prompt if needed

**Exit**: Learnings captured.

---

## Continuation

End each phase with a minimal prompt:

```markdown
# Next: [UNDERSTAND|ACT|REFLECT]

/hydrate

Mission: [One sentence]
Exit: [One criterion]
```

---

## When to Expand

Use the full 11-phase cycle only when:

1. **Multi-week scope** with multiple agents
2. **Architectural decisions** affecting many components
3. **Novel territory** with no existing patterns

See [n-phase-cycle/README.md](n-phase-cycle/README.md) for the full ceremony.

---

## Example: Bug Fix

**UNDERSTAND**: Read failing test → read code → identify root cause

**ACT**: Write fix → run tests → verify mypy

**REFLECT**: Note "edge case with empty input" → no epilogue needed

---

## Related

- [n-phase-cycle/](n-phase-cycle/README.md) — Full 11-phase for Crown Jewels
- [plan-file](plan-file.md) — Writing plan files

---

*Last updated: 2025-12-15*
