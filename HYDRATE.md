# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude-openrouter/` = Reference impl (like CPython)
- `impl/zen-agents/` = **Production-ready** zenportal reimplementation

## Current State (Dec 2025)

| Component | Status |
|-----------|--------|
| 6 Principles | ✅ Defined |
| 7 Bootstrap Agents | ✅ Spec + Impl |
| 5 Agent Genera (A,B,C,H,K) | ✅ Implemented |
| zen-agents | ✅ **41 tests** |
| runtime/ | ✅ **LLM-backed** (53 tests) |
| zen-agents UI | ✅ **Phase 1** (Textual TUI) |

## Quick Commands

```bash
# Launch zen-agents TUI
cd impl/zen-agents && uv run zen-agents

# Run demo
cd impl/zen-agents && uv run python demo.py

# Run tests
cd impl/zen-agents && uv run pytest tests/ -v
```

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

## Directory Map

```
kgents/
├── spec/                    # THE SPECIFICATION
│   ├── principles.md        # 6 core principles
│   ├── bootstrap.md         # 7 irreducible agents
│   └── {a,b,c,h,k}-gents/   # 5 agent genera
├── impl/claude-openrouter/  # Reference implementation
│   ├── bootstrap/           # 7 bootstrap agents (Python)
│   ├── runtime/             # LLM-backed agents (4 auth methods)
│   └── agents/{a,b,c,h,k}/  # 5 genera
└── impl/zen-agents/         # PRODUCTION APP
    ├── zen_agents/          # Core agents + ui/
    ├── pipelines/           # NewSessionPipeline, SessionTickPipeline
    └── tests/               # 41 pytest tests
```

## Next Steps

1. ~~runtime/~~ ✅ Done
2. ~~UI Phase 1~~ ✅ Done
3. **UI Phase 2**: NewSessionModal, conflict dialogs, session actions
4. Refactor zenportal to use zen-agents as library

## UI Phase 2 TODO

- [ ] NewSessionModal (NewSessionPipeline integration)
- [ ] Conflict resolution dialogs (Contradict/Sublate)
- [ ] Session create/pause/kill/revive actions
- [ ] TmuxCapture live output streaming

## Key Files

- `impl/zen-agents/demo.py` - Comprehensive demo (13 sections)
- `impl/zen-agents/zen_agents/ui/` - Textual TUI
- `impl/claude-openrouter/runtime/` - LLM-backed agents
- `spec/bootstrap.md` - Bootstrap agents spec

## Recent Changes

- **UI Phase 1 complete** - MainScreen, SessionList, OutputView, HelpScreen
- **Runtime implemented** - LLMJudge, LLMSublate, LLMContradict
