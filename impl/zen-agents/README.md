# zen-agents

Zenportal reimagined through kgents.

## What Is This?

A research implementation demonstrating that the kgents agent framework can serve as a foundation for real applications. Zenportal is the test case.

## Key Insight

**Services are Agents; Composition is Primary**

| Zenportal | zen-agents |
|-----------|------------|
| `SessionManager.create_session()` | `NewSessionPipeline` (Judge → Create → Spawn → Detect) |
| `ConfigManager` (3-tier) | `ZenGround` (config cascade as empirical seed) |
| `StateRefresher.refresh()` | `SessionTickPipeline` (Fix-based polling) |
| `TmuxService.*` | `agents/tmux/*` (each method is an agent) |

## Architecture

```
zen-agents/
├── agents/
│   ├── types.py          # Session, SessionConfig, ZenGroundState
│   ├── ground.py         # ZenGround - empirical seed
│   ├── judge.py          # ZenJudge - validation against principles
│   ├── session/          # Session lifecycle agents
│   │   ├── create.py     # SessionConfig → Session
│   │   ├── detect.py     # Fix-based state detection
│   │   └── lifecycle.py  # Pause, Kill, Resume
│   └── tmux/             # tmux wrapper agents
│       ├── spawn.py      # Create tmux session
│       ├── capture.py    # Capture pane output
│       ├── send.py       # Send keys
│       └── query.py      # List, Exists
├── pipelines/
│   ├── new_session.py    # Full creation pipeline
│   └── session_tick.py   # Per-tick state update
└── demo.py               # Demonstration script
```

## Bootstrap Mapping

The 7 irreducible agents from kgents map directly:

| Bootstrap | zen-agents Role |
|-----------|-----------------|
| **Id** | Pass-through transforms |
| **Compose** | Pipeline construction |
| **Judge** | ZenJudge (config validation) |
| **Ground** | ZenGround (config cascade + state) |
| **Contradict** | Detect conflicts (names, ports) |
| **Sublate** | Resolve conflicts |
| **Fix** | State detection polling |

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

## Status

**First iteration** - demonstrates architecture, not production-ready.

What works:
- Type system and agent interfaces
- Ground/Judge/Create/Detect agents
- tmux wrapper agents
- Composition pipelines

What's missing:
- Actual tmux integration (mocked in demo)
- Config persistence
- Full reconciliation (Contradict + Sublate)
- UI layer

## Research Questions

1. **Does agent composition reduce complexity?**
   - Hypothesis: Explicit composition surfaces hidden dependencies
   - Evidence: Compare LOC, cyclomatic complexity

2. **Does the bootstrap kernel generalize?**
   - Hypothesis: 7 agents suffice for any domain
   - Test: Are there operations that can't be expressed?

3. **Does heterarchy work in practice?**
   - Hypothesis: Agents can switch modes fluidly
   - Test: Same agent used both functionally and autonomously

## Next Steps

1. Add runtime/ (real LLM integration)
2. Implement Contradict/Sublate for conflict resolution
3. Build UI layer with agent outputs
4. Compare metrics with zenportal

---

*This is research - the goal is to learn, not to replace zenportal.*
