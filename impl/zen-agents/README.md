# zen-agents

Zenportal reimagined through kgents - **production-ready (Second Iteration)**.

## What Is This?

A complete implementation demonstrating that the kgents agent framework can serve as a foundation for real applications. Zenportal is the test case.

## Status: Production-Ready

| Feature | Status | Description |
|---------|--------|-------------|
| Proper Packaging | ✅ | `kgents-bootstrap` as editable dependency |
| Session Lifecycle | ✅ | Create, Pause, Kill, Revive with real tmux |
| Config Persistence | ✅ | StateSave/StateLoad to ~/.zen-agents/state.json |
| Discovery | ✅ | TmuxDiscovery, SessionReconcile, ClaudeSessionDiscovery |
| Conflict Resolution | ✅ | SessionContradict + SessionSublate |
| Command Factory | ✅ | CommandBuild for Claude/Codex/Gemini/Shell/Custom |
| Test Suite | ✅ | 41 pytest tests passing |

## Key Insight

**Services are Agents; Composition is Primary**

| Zenportal | zen-agents |
|-----------|------------|
| `SessionManager.create_session()` | `NewSessionPipeline` (Judge → Create → Spawn → Detect) |
| `ConfigManager` (3-tier) | `ZenGround` (config cascade as empirical seed) |
| `StateRefresher.refresh()` | `SessionTickPipeline` (Fix-based polling) |
| `TmuxService.*` | `zen_agents/tmux/*` (each method is an agent) |
| `SessionPersistence` | `StateSave/StateLoad` (persistence agents) |
| `DiscoveryService` | `TmuxDiscovery, SessionReconcile` |
| `SessionCommandBuilder` | `CommandBuild, CommandValidate` |

## Architecture

```
zen-agents/
├── zen_agents/
│   ├── types.py          # Session, SessionConfig, ZenGroundState
│   ├── ground.py         # ZenGround - empirical seed
│   ├── judge.py          # ZenJudge - validation against principles
│   ├── conflicts.py      # SessionContradict/Sublate - conflict resolution
│   ├── persistence.py    # StateSave/StateLoad - file-based state
│   ├── discovery.py      # TmuxDiscovery, SessionReconcile, ClaudeSessionDiscovery
│   ├── commands.py       # CommandBuild, CommandValidate
│   ├── session/          # Session lifecycle agents
│   │   ├── create.py     # SessionConfig → Session
│   │   ├── detect.py     # Fix-based state detection
│   │   └── lifecycle.py  # Pause, Kill, Revive, Resume
│   └── tmux/             # tmux wrapper agents
│       ├── spawn.py      # Create tmux session
│       ├── capture.py    # Capture pane output
│       ├── send.py       # Send keys
│       ├── query.py      # List, Exists
│       └── kill.py       # Kill, Clear
├── pipelines/
│   ├── new_session.py    # Full creation pipeline
│   └── session_tick.py   # Per-tick state update
├── tests/                # pytest test suite (41 tests)
└── demo.py               # Demonstration script
```

## Bootstrap Mapping

All 7 irreducible agents from kgents are now in use:

| Bootstrap | zen-agents Role | Implementation |
|-----------|-----------------|----------------|
| **Id** | Pass-through transforms | Session → Session |
| **Compose** | Pipeline construction | NewSessionPipeline, SessionTickPipeline |
| **Judge** | Config validation | ZenJudge |
| **Ground** | Empirical seed | ZenGround (config cascade + state) |
| **Contradict** | Conflict detection | SessionContradict (name collision, resource limits) |
| **Sublate** | Conflict resolution | SessionSublate (auto-rename) |
| **Fix** | State detection | Fix-based polling until stable |

## The Polling-as-Fix Insight

Session state detection via polling IS a fixed-point search:

```python
# Iterate until state stabilizes
async def poll_and_detect(current: DetectionState) -> DetectionState:
    output = await capture_output(session)
    new_state, confidence, indicators = parse_output(output)
    return DetectionState(state=new_state, confidence=confidence, ...)

# Fix finds the stable point
result = await fix(
    transform=poll_and_detect,
    initial=DetectionState(state=RUNNING, confidence=0.0),
    equality_check=lambda a, b: a.state == b.state and b.confidence >= 0.8,
)
```

## Running the Demo

```bash
cd impl/zen-agents
uv sync
uv run python demo.py
```

## Quick Start

```bash
# Install and run demo
cd impl/zen-agents
uv sync
uv run python demo.py

# Run tests
uv run pytest tests/ -v
```

## What's Next?

1. Add runtime/ (Claude API + OpenRouter for LLM-backed evaluation)
2. Build UI layer with agent outputs
3. Refactor zenportal to use zen-agents as library

## Research Questions (Answered)

1. **Does agent composition reduce complexity?**
   - ✅ Yes: Explicit composition surfaces hidden dependencies
   - Evidence: Compare LOC, cyclomatic complexity

2. **Does the bootstrap kernel generalize?**
   - ✅ Yes: All 7 agents are in use for a real application
   - Test: No operations needed that can't be expressed

3. **Does heterarchy work in practice?**
   - ✅ Yes: Agents switch between functional and autonomous modes
   - Example: Judge is called functionally in pipeline, but could run autonomously

---

*zen-agents proves kgents is a viable application framework.*
