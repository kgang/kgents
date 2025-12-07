# HYDRATE.md - Session Context

## What Is This?

**kgents** = Kent's Agents. A *specification* for tasteful, curated, ethical, joy-inducing agents.

Key insight: This is like Python (spec) vs CPython (impl). The `spec/` directory defines concepts; `impl/` will hold reference implementations (Claude Code + Open Router).

## Core Decisions

| Decision | Choice |
|----------|--------|
| Approach | Specification-first, not framework |
| Scope | Deep & narrow: A, B, C, K first |
| E-gents | Epistemological (knowledge, truth) |
| K-gent | Interactive persona (evolving preferences) |

## The Alphabet Garden

| Letter | Theme | Status |
|--------|-------|--------|
| **A** | Abstract + Art (creativity coach) | Skeleton done |
| **B** | Bio/Scientific (hypothesis, Robin) | Skeleton done |
| **C** | Category Theory (composition) | Skeleton done |
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
│   ├── principles.md  # 5 core principles
│   ├── anatomy.md     # What is an agent?
│   ├── a-agents/      # Abstract + Art
│   ├── b-gents/       # Bio/Scientific
│   ├── c-gents/       # Category Theory
│   └── k-gent/        # Kent simulacra
├── impl/              # Reference implementations (empty)
└── docs/              # Supporting docs (empty)
```

## 5 Principles

1. **Tasteful** - Quality over quantity
2. **Curated** - Intentional selection
3. **Ethical** - Augment, don't replace judgment
4. **Joy-Inducing** - Personality encouraged
5. **Composable** - Agents are morphisms; composition is primary

## Current State

- Phase 1 skeleton COMPLETE (18 spec files)
- No implementation yet
- No commits yet (all local)

## Next Steps

1. Review/refine spec files
2. Create HYDRATE.md bootstrapping for K-gent
3. Start reference implementation in `impl/claude-openrouter/`
4. Consider Phase 2 agents (D, E, See)

## Key Files to Read

- `spec/principles.md` - Design philosophy
- `spec/anatomy.md` - What constitutes an agent
- `spec/c-gents/composition.md` - How agents combine
- `spec/k-gent/persona.md` - Kent simulacra structure

## Research Sources

Plan file with full research: `~/.claude/plans/rippling-beaming-minsky.md`
