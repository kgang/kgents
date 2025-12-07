# HYDRATE.md - Session Context for kgents

## Current State

**kgents** is complete as a specification + reference implementation.

**zen-agents** (`~/git/zen-agents`) is the active project: rebuilding Zenportal using kgents architecture.

## What Exists

### kgents (this repo)
- `spec/` - Complete specification for 5 agent genera + bootstrap kernel
- `impl/claude-openrouter/` - Reference implementation (Python 3.13, heuristic/mock)
- `docs/RESEARCH_PLAN.md` - Full plan for zen-agents project
- `docs/AGENT_DEMONSTRATIONS.md` - Example invocations

### zen-agents (~/git/zen-agents)
- Bootstrap agents with **real LLM calls** (Anthropic API)
- ZenGround with session state model
- 10 passing tests, working demo
- Initial commit made

## The Research Question

Can kgents' 7-agent bootstrap kernel serve as foundation for real apps?

Test case: Rebuild Zenportal (tmux session manager TUI) from agents up.

## Next Steps

1. **Session agents**: create, revive, pause, kill, detect_state
2. **tmux agents**: spawn, capture, send_keys
3. **Config cascade**: 3-tier resolution as composition
4. **First end-to-end**: create a Claude session via composed pipeline

## Key Files

| Purpose | Location |
|---------|----------|
| Research plan | `docs/RESEARCH_PLAN.md` |
| Bootstrap types | `zen-agents/zen_agents/bootstrap/types.py` |
| LLM client | `zen-agents/zen_agents/bootstrap/llm.py` |
| Session model | `zen-agents/zen_agents/ground/zen_ground.py` |
| Original Zenportal | `~/git/zenportal` |

## Commands

```bash
cd ~/git/zen-agents
uv run python demo.py                      # Run demo
uv run pytest tests/ -v                    # Run tests
ANTHROPIC_API_KEY=... uv run python demo.py  # With LLM
```
