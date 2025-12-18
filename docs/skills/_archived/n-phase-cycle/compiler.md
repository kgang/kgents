# N-Phase Prompt Compiler

Generate structured prompts from YAML project definitions.

**Difficulty**: Medium
**Prerequisites**: Understanding of N-Phase cycle

---

## Overview

The N-Phase compiler transforms a YAML project definition into a structured meta-prompt that guides multi-phase development work.

```
project.yaml → compile → meta-prompt.md
```

---

## CLI Commands

```bash
# Compile a project definition
kg nphase compile project.yaml

# Save to file
kg nphase compile project.yaml -o prompt.md

# Validate without compiling
kg nphase validate project.yaml

# Bootstrap from existing plan file
kg nphase bootstrap plans/my-plan.md

# Show phase template
kg nphase template PLAN
```

---

## Project Definition Schema

```yaml
name: "My Project"
classification: CROWN_JEWEL  # or STANDARD, QUICK_WIN
effort: M  # XS, S, M, L, XL
n_phases: 11  # or 3 for QUICK_WIN

scope:
  goal: "What we're building"
  non_goals:
    - "What we're NOT building"
  parallel_tracks:
    - "Independent work streams"

decisions:
  - id: D1
    title: "Architecture choice"
    decision: "Use X approach"
    rationale: "Because..."

files:
  - path: "src/main.py"
    lines: "1-50"
    purpose: "Entry point"

invariants:
  - id: I1
    statement: "X must always be true"
    verification: "Run test Y"

blockers:
  - id: B1
    description: "Dependency unavailable"
    evidence: "Error message..."
    resolved: false

components:
  - id: C1
    name: "Core module"
    description: "Main implementation"
    effort: S
    dependencies: []

waves:
  - id: W1
    components: [C1, C2]
    checkpoint: "Tests pass"

entropy_budget:
  total: 0.10
  allocations:
    UNDERSTAND: 0.05
    ACT: 0.03
    REFLECT: 0.02
```

---

## Output Structure

The compiled prompt includes:

1. **Header** with project name
2. **ATTACH section** with `/hydrate`
3. **Phase selector** for environment variable
4. **Project overview** (scope, decisions)
5. **Shared context** (files, invariants, blockers)
6. **Cumulative state** (handles, entropy)
7. **Phase details** in expandable sections
8. **Phase accountability** ledger

---

## 3-Phase vs 11-Phase

| Mode | Phases | Use Case |
|------|--------|----------|
| 3-phase | UNDERSTAND, ACT, REFLECT | Most work |
| 11-phase | All phases | Crown Jewels |

Set `n_phases: 3` for quick wins, `n_phases: 11` for full ceremony.

---

## State Management

The compiler uses non-destructive state:

- Original YAML stays immutable
- State stored in separate JSON file
- Handles accumulate across phases
- Entropy tracked per phase

---

## Example

```yaml
# minimal.yaml
name: "Add Feature X"
classification: STANDARD
effort: S
n_phases: 3

scope:
  goal: "Add user authentication"
  non_goals:
    - "OAuth integration"

components:
  - id: C1
    name: "Auth module"
    effort: S
```

Compile:
```bash
kg nphase compile minimal.yaml
```

---

## Related

- [README.md](README.md) — N-Phase cycle overview
- [metatheory.md](metatheory.md) — Theoretical grounding

---

*Last updated: 2025-12-15*
