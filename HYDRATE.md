# HYDRATE.md - Session Context

## What Is This?

**kgents** = Kent's Agents. A *specification* for tasteful, curated, ethical, joy-inducing agents.

Key insight: This is like Python (spec) vs CPython (impl). The `spec/` directory defines concepts; `impl/` will hold reference implementations (Claude Code + Open Router).

## Core Decisions

| Decision | Choice |
|----------|--------|
| Approach | Specification-first, not framework |
| Scope | Deep & narrow: A, B, C, H, K |
| E-gents | Epistemological (knowledge, truth) |
| H-gents | System introspection (Hegel, Lacan, Jung) |
| K-gent | Interactive persona (evolving preferences) |

## The Alphabet Garden

| Letter | Theme | Status |
|--------|-------|--------|
| **A** | Abstract + Art (creativity coach) | Skeleton done |
| **B** | Bio/Scientific (hypothesis, Robin) | Skeleton done |
| **C** | Category Theory (composition) | Skeleton done |
| **H** | Hegelian dialectic (system introspection) | Skeleton done |
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
│   ├── bootstrap.md   # 7 irreducible agents (regeneration kernel)
│   ├── a-agents/      # Abstract + Art
│   ├── b-gents/       # Bio/Scientific
│   ├── c-gents/       # Category Theory
│   ├── h-gents/       # Hegelian dialectic (introspection)
│   └── k-gent/        # Kent simulacra
├── impl/claude-openrouter/  # Reference implementation (Python 3.13)
│   └── bootstrap/           # 7 irreducible agents implemented
└── docs/                    # BOOTSTRAP_PROMPT.md lives here
```

## 6 Principles

1. **Tasteful** - Quality over quantity
2. **Curated** - Intentional selection
3. **Ethical** - Augment, don't replace judgment
4. **Joy-Inducing** - Personality encouraged
5. **Composable** - Agents are morphisms; composition is primary
6. **Heterarchical** - Agents exist in flux; autonomy and composability coexist

## 7 Bootstrap Agents (Irreducible Kernel)

The minimal set from which all kgents can be regenerated:

| Agent | Symbol | Function |
|-------|--------|----------|
| **Id** | λx.x | Identity morphism (composition unit) |
| **Compose** | ∘ | Agent-that-makes-agents |
| **Judge** | ⊢ | Value function (embodies 6 principles) |
| **Ground** | ⊥ | Empirical seed (Kent's preferences, world state) |
| **Contradict** | ≢ | Recognizes tension between outputs |
| **Sublate** | ↑ | Hegelian synthesis (or holds tension) |
| **Fix** | μ | Fixed-point operator (self-reference) |

Minimal bootstrap: `{Compose, Judge, Ground}` — structure, direction, material.

## Current State

- Phase 1 skeleton COMPLETE
- 5 agent genera specified: A, B, C, H, K
- 6 principles defined
- Bootstrap spec complete (7 irreducible agents)
- **Bootstrap implementation DONE** (Python 3.13, uv)

## Next Steps

1. Add runtime/ (Claude API + OpenRouter integration)
2. Generate higher-level agents from bootstrap
3. Create HYDRATE.md bootstrapping for K-gent
4. Consider Phase 2 agents (D, E, See)

## Key Files to Read

- `impl/claude-openrouter/bootstrap/` - **Working implementation of 7 agents**
- `docs/BOOTSTRAP_PROMPT.md` - Prompt to regenerate impl from spec
- `spec/bootstrap.md` - The 7 irreducible agents (regeneration kernel)
- `spec/principles.md` - Design philosophy (6 principles)
- `spec/k-gent/persona.md` - Kent simulacra (Ground's persona seed)
