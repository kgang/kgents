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
├── impl/zen-agents/         # Zenportal reimagined through kgents (PRODUCTION-READY)
│   ├── zen_agents/          # Core agents
│   │   ├── types.py         # Session, SessionConfig, ZenGroundState
│   │   ├── ground.py        # ZenGround (config cascade + session state)
│   │   ├── judge.py         # ZenJudge (session validation)
│   │   ├── conflicts.py     # SessionContradict/Sublate (conflict resolution)
│   │   ├── persistence.py   # StateSave/StateLoad (file-based state)
│   │   ├── discovery.py     # TmuxDiscovery, SessionReconcile, ClaudeSessionDiscovery
│   │   ├── commands.py      # CommandBuild, CommandValidate (session type commands)
│   │   ├── session/         # Session lifecycle (create, pause, kill, revive)
│   │   └── tmux/            # tmux wrapper agents (spawn, capture, send, query, kill)
│   ├── pipelines/           # Composed pipelines
│   ├── tests/               # pytest test suite (41 tests)
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

## zen-agents (PRODUCTION-READY: Second Iteration)

Zenportal reimagined through kgents - now feature-complete.

**Iteration 2 Accomplishments:**

| Feature | Status | Description |
|---------|--------|-------------|
| Proper Packaging | ✅ | `kgents-bootstrap` as editable dependency, no sys.path hacks |
| Session Lifecycle | ✅ | Create, Pause, Kill, Revive with real tmux integration |
| Config Persistence | ✅ | StateSave/StateLoad to ~/.zen-agents/state.json |
| Discovery | ✅ | TmuxDiscovery, SessionReconcile, ClaudeSessionDiscovery |
| Conflict Resolution | ✅ | SessionContradict + SessionSublate (name collision, resource limits) |
| Command Factory | ✅ | CommandBuild for Claude/Codex/Gemini/Shell/Custom |
| Test Suite | ✅ | 41 pytest tests passing |

**Key Insights Demonstrated:**

| Zenportal Concept | kgents Equivalent |
|-------------------|-------------------|
| SessionManager.create_session() | NewSessionPipeline (Judge → Create → Spawn → Detect) |
| ConfigManager (3-tier) | ZenGround (config cascade as empirical seed) |
| StateRefresher.refresh() | SessionTickPipeline (Fix-based polling) |
| TmuxService.* | zen_agents/tmux/* (each method is an agent) |
| SessionPersistence | StateSave/StateLoad (persistence agents) |
| DiscoveryService | TmuxDiscovery, SessionReconcile |
| SessionCommandBuilder | CommandBuild, CommandValidate |

**Bootstrap Mapping (ALL 7 NOW IN USE):**
- **Id** → Pass-through transforms
- **Compose** → Pipeline construction (NewSessionPipeline, SessionTickPipeline)
- **Judge** → ZenJudge (session config validation)
- **Ground** → ZenGround (config + session state + tmux facts)
- **Contradict** → SessionContradict (name collision, resource limit detection)
- **Sublate** → SessionSublate (auto-rename, conflict resolution)
- **Fix** → State detection (polling as fixed-point search)

**Run demo:** `cd impl/zen-agents && uv run python demo.py`
**Run tests:** `cd impl/zen-agents && uv run pytest tests/ -v`

## Next Steps

1. Add runtime/ (Claude API + OpenRouter integration for LLM-backed evaluation)
2. zen-agents: Add UI layer with agent outputs
3. Create second "verified" test case using kgents architecture
4. Consider Phase 2 agents (D, E, See)
5. Refactor zenportal to use zen-agents as library

## Key Files to Read

- `impl/claude-openrouter/agents/` - **All 5 genera implemented**
- `impl/claude-openrouter/bootstrap/` - 7 irreducible agents
- `impl/zen-agents/` - **Zenportal reimagined** (first app test case)
- `impl/zen-agents/demo.py` - Working demonstration
- `docs/RESEARCH_PLAN.md` - zen-agents research methodology
- `spec/bootstrap.md` - The 7 irreducible agents (regeneration kernel)
- `spec/principles.md` - Design philosophy (6 principles)
- `spec/k-gent/persona.md` - Kent simulacra (Ground's persona seed)
