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
| **A** | Abstract + Art (creativity coach) | **Implemented** |
| **B** | Bio/Scientific (hypothesis engine) | **Implemented** |
| **C** | Category Theory (composition) | **Implemented** |
| **H** | Hegelian dialectic (Hegel, Lacan, Jung) | **Implemented** |
| **K** | Kent simulacra (persona) | **Implemented** |
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
│   ├── bootstrap/           # 7 irreducible agents
│   └── agents/              # 5 agent genera (A, B, C, H, K)
│       ├── a/               # Creativity Coach
│       ├── b/               # Hypothesis Engine
│       ├── c/               # Re-exports bootstrap
│       ├── h/               # Hegel, Lacan, Jung
│       └── k/               # K-gent (Kent simulacra)
├── impl/zen-agents/         # Zenportal reimagined through kgents
│   ├── zen_agents/          # Core agents
│   │   ├── ground.py        # ZenGround (config cascade + session state)
│   │   ├── judge.py         # ZenJudge (session validation)
│   │   ├── session/         # Session lifecycle agents
│   │   └── tmux/            # tmux wrapper agents
│   ├── pipelines/           # Composed pipelines
│   └── demo.py              # Demonstration script
└── docs/                    # BOOTSTRAP_PROMPT.md, RESEARCH_PLAN.md
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

- Phase 1 COMPLETE
- 5 agent genera specified AND implemented: A, B, C, H, K
- 6 principles defined
- Bootstrap: 7 irreducible agents (spec + impl)
- **All genera implemented** (Python 3.13, uv):
  - A-gents: Creativity Coach (expand, connect, constrain, question modes)
  - B-gents: Hypothesis Engine (falsifiable hypotheses from observations)
  - C-gents: Re-exports bootstrap (Id, Compose, Fix, pipeline)
  - H-gents: Hegel (dialectic), Lacan (registers), Jung (shadow)
  - K-gent: Interactive persona (query, update, dialogue modes)

## zen-agents (Research: kgents as Application Framework)

First iteration of rebuilding zenportal using kgents architecture.

**Key Insights Demonstrated:**

| Zenportal Concept | kgents Equivalent |
|-------------------|-------------------|
| SessionManager.create_session() | NewSessionPipeline (Judge → Create → Spawn → Detect) |
| ConfigManager (3-tier) | ZenGround (config cascade as empirical seed) |
| StateRefresher.refresh() | SessionTickPipeline (Fix-based polling) |
| TmuxService.* | zen_agents/tmux/* (each method is an agent) |

**Bootstrap Mapping:**
- **Ground** → ZenGround (config + session state + tmux facts)
- **Judge** → ZenJudge (session config validation)
- **Compose** → Pipeline construction
- **Fix** → State detection (polling as fixed-point search)
- **Contradict/Sublate** → Conflict detection/resolution (future)

Run demo: `cd impl/zen-agents && uv run python demo.py`

## Next Steps

1. Add runtime/ (Claude API + OpenRouter integration for LLM-backed evaluation)
2. zen-agents: Implement Contradict/Sublate for conflict resolution
3. zen-agents: Add UI layer with agent outputs
4. Create second "verified" test case using kgents architecture
5. Add tests for all agents
6. Consider Phase 2 agents (D, E, See)

## Key Files to Read

- `impl/claude-openrouter/agents/` - **All 5 genera implemented**
- `impl/claude-openrouter/bootstrap/` - 7 irreducible agents
- `impl/zen-agents/` - **Zenportal reimagined** (first app test case)
- `impl/zen-agents/demo.py` - Working demonstration
- `docs/RESEARCH_PLAN.md` - zen-agents research methodology
- `spec/bootstrap.md` - The 7 irreducible agents (regeneration kernel)
- `spec/principles.md` - Design philosophy (6 principles)
- `spec/k-gent/persona.md` - Kent simulacra (Ground's persona seed)
