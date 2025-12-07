# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude-openrouter/` = Reference impl (like CPython)
- `impl/zen-agents/` = **Production-ready** zenportal reimplementation proving kgents works

## Current State (Dec 2024)

| Component | Status |
|-----------|--------|
| 6 Principles | ✅ Defined |
| 7 Bootstrap Agents | ✅ Spec + Impl |
| 5 Agent Genera (A,B,C,H,K) | ✅ Implemented |
| zen-agents | ✅ **Production-ready** (41 tests) |

## Quick Commands

```bash
# Run zen-agents demo (comprehensive tour)
cd impl/zen-agents && uv run python demo.py

# Run specific demo section
cd impl/zen-agents && uv run python demo.py --section conflicts

# List demo sections
cd impl/zen-agents && uv run python demo.py --list

# Run tests
cd impl/zen-agents && uv run pytest tests/ -v
```

## Demo Sections (13 total)

`intro` `ground` `judge` `create` `conflicts` `pipeline` `fix` `lifecycle` `discovery` `commands` `persistence` `bootstrap` `summary`

## 7 Bootstrap Agents

| Agent | Symbol | Purpose |
|-------|--------|---------|
| **Id** | λx.x | Identity (composition unit) |
| **Compose** | ∘ | Agent-that-makes-agents |
| **Judge** | ⊢ | Value function (6 principles) |
| **Ground** | ⊥ | Empirical seed (persona + world) |
| **Contradict** | ≢ | Tension detection |
| **Sublate** | ↑ | Hegelian synthesis |
| **Fix** | μ | Fixed-point (self-reference) |

## 6 Principles

1. Tasteful 2. Curated 3. Ethical 4. Joy-Inducing 5. Composable 6. Heterarchical

## Directory Map

```
kgents/
├── spec/                    # THE SPECIFICATION
│   ├── principles.md        # 6 core principles
│   ├── bootstrap.md         # 7 irreducible agents
│   └── {a,b,c,h,k}-gents/   # 5 agent genera
├── impl/claude-openrouter/  # Reference implementation
│   ├── bootstrap/           # 7 bootstrap agents (Python)
│   └── agents/{a,b,c,h,k}/  # 5 genera
└── impl/zen-agents/         # PRODUCTION APP (zenportal reimagined)
    ├── zen_agents/          # Core agents
    │   ├── ground.py, judge.py, conflicts.py, persistence.py
    │   ├── discovery.py, commands.py
    │   ├── session/         # create, detect, lifecycle
    │   └── tmux/            # spawn, capture, send, query, kill
    ├── pipelines/           # NewSessionPipeline, SessionTickPipeline
    └── tests/               # 41 pytest tests
```

## zen-agents: All 7 Bootstrap Agents in Use

| Bootstrap | zen-agents Implementation |
|-----------|---------------------------|
| Id | Pass-through transforms |
| Compose | NewSessionPipeline, SessionTickPipeline |
| Judge | ZenJudge (config validation) |
| Ground | ZenGround (config cascade + state) |
| Contradict | SessionContradict (conflict detection) |
| Sublate | SessionSublate (conflict resolution) |
| Fix | State detection (polling as fixed-point) |

## Next Steps

1. **Implement `runtime/`** - See `impl/claude-openrouter/PLAN.md` (plan ready)
2. Build UI layer for zen-agents
3. Refactor zenportal to use zen-agents as library
4. Consider Phase 2 agents (D, E, See)

## Runtime Plan (impl/claude-openrouter/PLAN.md)

**4 Auth Methods** (priority order):
1. Claude CLI (`claude login`) - Max subscribers, no API key
2. OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`) - containers/CI
3. OpenRouter via y-router (`http://localhost:8787`) - multi-model
4. Anthropic API key (fallback)

**LLM-backed agents**: Judge, Sublate, Contradict (replace heuristics with LLM reasoning)

## Key Files

- `impl/zen-agents/README.md` - zen-agents documentation
- `impl/zen-agents/demo.py` - **Comprehensive demo** (13 modular sections, CLI interface)
- `impl/claude-openrouter/PLAN.md` - **Runtime implementation plan** (ready to implement)
- `spec/bootstrap.md` - Bootstrap agents spec
- `spec/principles.md` - Design philosophy

## Recent Changes

- **Runtime plan added** (`impl/claude-openrouter/PLAN.md`) - 4 auth methods, LLM-backed agents
- **demo.py refactored** into modular CLI with `--section`, `--list` options
- All 7 bootstrap agents demonstrated with architectural insights
