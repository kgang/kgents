# HYDRATE.md - Session Context

## What Is This?

**kgents** = Kent's Agents. A *specification* for tasteful, curated, ethical, joy-inducing agents.

Key insight: This is like Python (spec) vs CPython (impl). The `spec/` directory defines concepts; `impl/` will hold reference implementations (Claude Code + Open Router).

## Core Decisions

| Decision | Choice |
|----------|--------|
| Approach | Specification-first, not framework |
| Scope | Deep & narrow: A, B, C, K first (H pending) |
| E-gents | Epistemological (knowledge, truth) |
| H-gents | System introspection (Hegel, Lacan, Jung) |
| K-gent | Interactive persona (evolving preferences) |

## The Alphabet Garden

| Letter | Theme | Status |
|--------|-------|--------|
| **A** | Abstract + Art (creativity coach) | Skeleton done |
| **B** | Bio/Scientific (hypothesis, Robin) | Skeleton done |
| **C** | Category Theory (composition) | Skeleton done |
| **H** | Hegelian dialectic (system introspection) | Skeleton done (uncommitted) |
| **K** | Kent simulacra (persona) | Skeleton done |
| D | Absurdlings (NPCs) | Future |
| E | Epistemological | Future |
| See | Observability | Future |

## Directory Structure

```
kgents/
├── CLAUDE.md          # Project instructions
├── HYDRATE.md         # This file
├── spec/              # THE SPECIFICATION
│   ├── principles.md  # 6 core principles
│   ├── anatomy.md     # What is an agent?
│   ├── a-agents/      # Abstract + Art
│   ├── b-gents/       # Bio/Scientific
│   ├── c-gents/       # Category Theory
│   ├── h-gents/       # Hegelian dialectic (introspection)
│   └── k-gent/        # Kent simulacra
├── impl/              # Reference implementations (empty)
└── docs/              # Supporting docs (empty)
```

## 6 Principles

1. **Tasteful** - Quality over quantity
2. **Curated** - Intentional selection
3. **Ethical** - Augment, don't replace judgment
4. **Joy-Inducing** - Personality encouraged
5. **Composable** - Agents are morphisms; composition is primary
6. **Heterarchical** - Agents exist in flux; autonomy and composability coexist

## Current State

- Phase 1 skeleton mostly complete (commit `5783126`)
- **Uncommitted**: H-gents skeleton + Principle #6 (Heterarchical)
- No implementation yet

## Next Steps

1. **Commit pending work** (H-gents, Principle #6)
2. Review/refine spec files
3. Create HYDRATE.md bootstrapping for K-gent
4. Start reference implementation in `impl/claude-openrouter/`
5. Consider Phase 2 agents (D, E, See)

## Key Files to Read

- `spec/principles.md` - Design philosophy (6 principles incl. Heterarchical)
- `spec/anatomy.md` - What constitutes an agent
- `spec/c-gents/composition.md` - How agents combine
- `spec/h-gents/index.md` - System introspection (Hegel, Lacan, Jung)
- `spec/k-gent/persona.md` - Kent simulacra structure

## Research Sources

Plan file with full research: `~/.claude/plans/rippling-beaming-minsky.md`
