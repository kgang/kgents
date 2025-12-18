# Archived: Evergreen Prompt Compiler

**Archived**: 2025-12-18
**Reason**: Infrastructure without implementation (0 section compilers registered in production)
**Absorbed by**: Forest Protocol reconciliation (`self.forest.reconcile`)

## What Was This?

The Evergreen Prompt System was designed to automatically compile CLAUDE.md from multiple section compilers. The architecture was:

```
Section Compilers → Prompt Compiler → CLAUDE.md
```

## Why Archived?

1. **Zero production usage**: While infrastructure existed, no section compilers were actually used
2. **CLAUDE.md is hand-curated**: Manual editing proved more effective than automated compilation
3. **Forest Protocol supersedes**: `self.forest.reconcile` handles meta-file generation now
4. **11-phase replaced by 3-phase**: The `NPhase` enum's complexity wasn't justified

## Preserved Concepts

These concepts live on in other parts of the codebase:

| Concept | New Location |
|---------|--------------|
| `NPhase` enum | Simplified to 3-phase (SENSE/ACT/REFLECT) in `docs/skills/three-phase-workflow.md` |
| Section composition | Forest reconciliation handles this now |
| Token budget management | Not needed (CLAUDE.md is hand-curated) |
| Source abstraction | `protocols.prompt.sources/` still exists if needed |

## Files Archived

```
compiler.py          - Main prompt compiler
polynomial.py        - PROMPT_POLYNOMIAL state machine
sections/            - Section compilers (principles, skills, forest, etc.)
```

## If You Need This

The concepts live on in:
- `protocols/agentese/contexts/forest.py` - Forest reconciliation
- `docs/skills/three-phase-workflow.md` - Simplified phase workflow

**Delete after 30 days per archive policy (2025-01-17).**

## Restoration

If you need to restore:
```bash
mv impl/claude/protocols/_archived/evergreen-prompt-2025-12-18/* impl/claude/protocols/prompt/
```

Then restore imports in `protocols/prompt/__init__.py`.
