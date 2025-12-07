# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude-openrouter/` = Reference impl (like CPython)
- `impl/zen-agents/` = **Production-ready** zenportal reimplementation proving kgents works

## Current State (Dec 2025)

| Component | Status |
|-----------|--------|
| 6 Principles | ✅ Defined |
| 7 Bootstrap Agents | ✅ Spec + Impl |
| 5 Agent Genera (A,B,C,H,K) | ✅ Implemented |
| zen-agents | ✅ **Production-ready** (41 tests) |
| runtime/ | ✅ **LLM-backed agents** (53 tests) |
| zen-agents UI | ✅ **Phase 1 complete** (Textual TUI) |

## Quick Commands

```bash
# Launch zen-agents TUI
cd impl/zen-agents && uv run zen-agents

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
│   ├── runtime/             # LLM-backed execution (NEW)
│   │   ├── client.py        # 4 auth methods (CLI, OAuth, OpenRouter, API)
│   │   ├── llm_agents/      # LLMJudge, LLMSublate, LLMContradict
│   │   └── cache.py, usage.py
│   └── agents/{a,b,c,h,k}/  # 5 genera
└── impl/zen-agents/         # PRODUCTION APP (zenportal reimagined)
    ├── zen_agents/          # Core agents
    │   ├── ground.py, judge.py, conflicts.py, persistence.py
    │   ├── discovery.py, commands.py
    │   ├── session/         # create, detect, lifecycle
    │   ├── tmux/            # spawn, capture, send, query, kill
    │   └── ui/              # NEW: Textual TUI (Phase 1)
    │       ├── app.py       # ZenAgentsApp
    │       ├── screens/     # MainScreen, HelpScreen
    │       └── widgets/     # SessionList, OutputView, Notification
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

1. ~~**Implement `runtime/`**~~ ✅ Done (53 tests)
2. ~~**Build UI layer for zen-agents (Phase 1)**~~ ✅ Done
3. **UI Phase 2**: NewSessionModal, conflict resolution dialogs
4. Refactor zenportal to use zen-agents as library
5. Consider Phase 2 agents (D, E, See)

---

## UI/UX Plan for zen-agents

### Reference: zenportal (~/git/zenportal)

**Tech stack**: Textual 6.7+ TUI framework, Rich rendering

**Architecture patterns to adopt**:
- Screen-based navigation (MainScreen + modal stack)
- Vim-style keybindings (j/k navigation, mnemonics)
- ZenScreen/ZenModalScreen base classes
- Reactive state via Textual's `reactive` properties
- Custom Message classes for inter-widget events
- Central CSS system (`styles/base.py`)
- Eye-strain optimization (session echo in output header)

**Key zenportal components**:
| Component | Location | Purpose |
|-----------|----------|---------|
| MainScreen | screens/main.py | Primary UI: session list + output view |
| SessionList | widgets/session_list.py | Vim nav, grab-mode reorder |
| OutputView | widgets/output_view.py | RichLog with search |
| SessionInfo | widgets/session_info.py | Metadata + token sparkline |
| NewSessionModal | screens/new_session_modal.py | 3-tab create/attach/resume |
| ZenNotification | widgets/notification.py | Toast system |

### kgents Bootstrap Integration for UI

**Compose**: Build UI pipelines
```python
# Input validation → judge → create → render
session_create_pipeline = pipeline(
    ParseInputAgent,
    ZenJudge,
    SessionCreate,
    RenderConfirmation
)
```

**Judge**: Quality-gate UI components
```python
# Validate user input against principles
verdict = await zen_judge.invoke(session_config)
if verdict.overall == Verdict.REJECT:
    show_notification(verdict.reasons, severity="error")
```

**Ground**: Persona-aware rendering
```python
state = await zen_ground.invoke()
theme = state.query("preferences.aesthetics")  # minimal, functional
```

**Contradict + Sublate**: Conflict resolution UI
```python
# Show detected conflicts, offer resolutions
conflicts = await session_contradict.invoke((config, ground_state))
for conflict in conflicts:
    resolution = await session_sublate.invoke(conflict)
    show_conflict_dialog(conflict, resolution)
```

**Fix**: State stabilization
```python
# Poll until session state stabilizes (already implemented in SessionDetect)
result = await fix(poll_and_detect, initial_state)
update_ui(result.value.state)
```

### Proposed UI Architecture

```
impl/zen-agents/
├── zen_agents/           # Existing agents (unchanged)
├── pipelines/            # Existing pipelines (unchanged)
├── ui/                   # NEW: Textual UI layer
│   ├── app.py            # ZenAgentsApp (main Textual app)
│   ├── screens/
│   │   ├── base.py       # ZenScreen, ZenModalScreen
│   │   ├── main.py       # MainScreen (list + output)
│   │   ├── new_session.py # NewSessionModal
│   │   ├── config.py     # ConfigScreen
│   │   └── help.py       # HelpScreen
│   ├── widgets/
│   │   ├── session_list.py
│   │   ├── output_view.py
│   │   ├── session_info.py
│   │   └── notification.py
│   ├── styles/
│   │   └── base.py       # Central CSS
│   └── events.py         # Custom Textual messages
├── cli.py                # NEW: CLI entry point (argparse or click)
└── __main__.py           # python -m zen_agents
```

### Key Differences from zenportal

| Aspect | zenportal | zen-agents UI |
|--------|-----------|---------------|
| Services | Procedural classes | Agents (composable) |
| Validation | Inline checks | ZenJudge pipeline |
| State | SessionManager | ZenGround (empirical seed) |
| Conflicts | Manual handling | Contradict + Sublate agents |
| Polling | Ad-hoc refresh | Fix-based (SessionDetect) |

### Implementation Phases

**Phase 1: Core UI Shell** ✅ DONE
- [x] ZenAgentsApp with agent dependency injection
- [x] MainScreen with SessionList + OutputView
- [x] Vim-style keybindings (j/k nav, ?=help, q=quit)
- [x] CLI entry point (`zen-agents` command)
- [x] Notification system (toast messages)
- [x] HelpScreen with keybinding reference

**Phase 2: Session Management** ← Current
- [ ] NewSessionModal (NewSessionPipeline integration)
- [ ] Conflict resolution dialogs (Contradict/Sublate)
- [ ] Session create/pause/kill/revive actions
- [ ] TmuxCapture live output streaming

**Phase 3: Polish**
- [ ] Config screen
- [ ] Theme support (from Ground persona)
- [ ] Search in output view

## Runtime Module (impl/claude-openrouter/runtime/)

**4 Auth Methods** (auto-detected in priority order):
1. Claude CLI (`claude login`) - Max subscribers, no API key
2. OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`) - containers/CI
3. OpenRouter via y-router (`http://localhost:8787`) - multi-model
4. Anthropic API key (fallback)

**LLM-backed agents**: LLMJudge, LLMSublate, LLMContradict

```python
from runtime import get_llm_judge, get_llm_sublate, get_llm_contradict

# Get LLM-backed agents (auto-detects auth)
judge = get_llm_judge()
result = await judge.invoke(JudgeInput(subject=my_agent))
```

## Key Files

- `impl/zen-agents/README.md` - zen-agents documentation
- `impl/zen-agents/demo.py` - **Comprehensive demo** (13 modular sections, CLI interface)
- `impl/claude-openrouter/runtime/` - **LLM-backed agents** (53 tests)
- `spec/bootstrap.md` - Bootstrap agents spec
- `spec/principles.md` - Design philosophy

## Manual Testing Runtime

```bash
cd impl/claude-openrouter
uv run python -c "
import asyncio
from runtime import get_client, detect_auth_method, user

print(detect_auth_method())  # Shows which auth is active

async def test():
    client = get_client()
    r = await client.complete([user('Say hello')])
    print(r.content)

asyncio.run(test())
"
```

## Recent Changes

- **UI Phase 1 complete** - Textual TUI with MainScreen, SessionList, OutputView, HelpScreen
- **CLI client fix** - Removed invalid `--max-tokens` flag from ClaudeCLIClient
- **Runtime implemented** - LLMJudge, LLMSublate, LLMContradict with 4 auth methods
- demo.py refactored into modular CLI with `--section`, `--list` options
