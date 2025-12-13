# Alethic Workbench - Debug, QA, and Realization Prompt

## Mission

Push the Alethic Workbench from demo mode to production reality—connecting the generative TUI to live K-gent agents, flux streams, and the full kgents ecosystem.

> *"Don't just look at the agent. Look THROUGH the agent."*

---

## Project Context

The **Alethic Workbench** is a terminal-based interface for observing and manipulating AI agents in the kgents system. It uses Textual for TUI rendering and implements a **semantic zoom** paradigm with three LOD (Level of Detail) levels:

| LOD | Name | View | Purpose |
|-----|------|------|---------|
| 0 | ORBIT | FluxScreen | Bird's eye view of all agents as density cards |
| 1 | SURFACE | CockpitScreen | Single agent operational dashboard |
| 2 | INTERNAL | MRIScreen | Deep inspection, entropy visualization |
| — | Temporal | LoomScreen | Cognitive branching history (decisions/counterfactuals) |

---

## Current State (as of 2025-12-12)

### What Works (Demo Mode)
- **All 17 primitives implemented** (see `plans/interfaces/primitives.md`)
- **4 screens functional**: FluxScreen, CockpitScreen, MRIScreen, LoomScreen
- **1019 tests passing** in `impl/claude/agents/i/`
- **Demo launcher**: `uv run python impl/claude/agents/i/demo_all_screens.py`
- Joy-inducing features: Oblique Strategies easter eggs, heartbeat pulsing

### What Needs Work (Production Mode)
1. **Live agent connection**: Screens use `create_demo_*()` functions, need real data sources
2. **Flux integration**: Connect to `impl/claude/agents/flux/` stream processing
3. **K-gent binding**: Wire up to actual K-gent instances
4. **WebSocket sources**: `TerrariumWebSocketSource` exists but not wired to screens
5. **State persistence**: Agent snapshots should persist across sessions

---

## Key Files to Understand

### Screens (the views)
```
impl/claude/agents/i/screens/
├── flux.py          # LOD 0: Agent card grid (FluxScreen)
├── cockpit.py       # LOD 1: Operational dashboard (CockpitScreen)
├── mri.py           # LOD 2: Deep inspection (MRIScreen)
├── loom.py          # Temporal: Branching history (LoomScreen)
└── _tests/          # Screen tests
```

### Widgets (the primitives)
```
impl/claude/agents/i/widgets/
├── density_field.py   # P1: Agent activity visualization
├── sparkline.py       # P2: Time series mini-chart
├── graph_layout.py    # P5: Agent relationship graph (semantic/tree/force)
├── branch_tree.py     # P6: Cognitive branching visualization
├── timeline.py        # P7: Temporal navigation
├── entropy.py         # P10: Entropy parameter calculation
├── slider.py          # P11: Direct manipulation control
├── glitch.py          # P9: Entropy-driven visual corruption
└── _tests/            # Widget tests (400+ tests)
```

### Data Layer (state management)
```
impl/claude/agents/i/data/
├── state.py           # AgentSnapshot, FluxState, SessionState
├── core_types.py      # Phase enum, Glyph, MarginNote
├── registry.py        # Agent registry protocol
├── loom.py            # CognitiveBranch, CognitiveTree (decision history)
├── hints.py           # VisualHint protocol (agent → UI)
├── hint_registry.py   # HintRegistry (hint → widget mapping)
└── ogent.py           # O-gent poller (XYZ health metrics)
```

### Flux Integration (stream processing)
```
impl/claude/agents/flux/
├── sources/           # Data sources (TerrariumWebSocketSource, etc.)
├── synapse.py         # Message routing
├── circuit_breaker.py # Fault tolerance
└── dlq.py             # Dead letter queue
```

### K-gent (the agent to observe)
```
impl/claude/agents/k/
├── __init__.py        # K-gent entry point
├── garden.py          # Agent orchestration
├── gatekeeper.py      # Request filtering
├── hypnagogia.py      # Dream/reflection state
├── llm.py             # LLM interaction
└── starters.py        # Initialization
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALETHIC WORKBENCH                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ FluxScreen  │  │CockpitScreen│  │  MRIScreen  │  LoomScreen │
│  │  (ORBIT)    │  │  (SURFACE)  │  │ (INTERNAL)  │  (Temporal) │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│                    ┌─────┴─────┐                                │
│                    │ FluxState │ ← AgentSnapshot[]              │
│                    └─────┬─────┘                                │
├──────────────────────────┼──────────────────────────────────────┤
│                          │                                      │
│              ┌───────────┴───────────┐                          │
│              │    DATA SOURCES       │                          │
│              ├───────────────────────┤                          │
│              │ • TerrariumWebSocket  │ ← Live agent streams     │
│              │ • OgentPoller         │ ← XYZ health metrics     │
│              │ • CognitiveLoom       │ ← Decision history       │
│              │ • VisualHints         │ ← Agent-emitted hints    │
│              └───────────┬───────────┘                          │
│                          │                                      │
├──────────────────────────┼──────────────────────────────────────┤
│                          │                                      │
│              ┌───────────┴───────────┐                          │
│              │      K-GENT           │                          │
│              │  (Real Agent)         │                          │
│              └───────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Debug & QA Tasks

### 1. Verify Demo Mode
```bash
# Run all tests
uv run pytest impl/claude/agents/i/ -v

# Run specific screen tests
uv run pytest impl/claude/agents/i/screens/_tests/ -v

# Launch interactive demo
uv run python impl/claude/agents/i/demo_all_screens.py
```

### 2. Check Type Safety
```bash
# Run mypy on i-gent module
uv run mypy impl/claude/agents/i/ --strict
```

### 3. Test Individual Screens
```bash
# FluxScreen demo
uv run python impl/claude/agents/i/screens/flux.py

# LoomScreen demo
uv run python impl/claude/agents/i/screens/loom.py
```

### 4. Identify Broken Imports
```bash
# Check for remaining types.py references (should be core_types.py)
grep -r "\.types import" impl/claude/agents/i/
grep -r "agents\.i\.types" impl/claude/agents/i/
```

---

## Realization Tasks (Priority Order)

### Phase 1: Live Data Binding
1. **Create `LiveFluxState` adapter** that subscribes to flux streams
2. **Wire `TerrariumWebSocketSource`** to FluxScreen
3. **Implement `AgentSnapshot.from_kgent()`** factory method
4. **Add refresh loop** to screens (currently static)

### Phase 2: K-gent Integration
1. **Connect CockpitScreen to a running K-gent**
2. **Emit VisualHints from K-gent** for custom rendering
3. **Wire up CognitiveLoom** to K-gent decision traces
4. **Test with `kg soul challenge`** command

### Phase 3: Full Ecosystem
1. **Multi-agent FluxScreen** with live garden view
2. **Cross-agent flow arrows** showing message passing
3. **Drill-down navigation** (click card → CockpitScreen)
4. **Session persistence** (save/load workbench state)

---

## Code Patterns to Follow

### Creating a Data Source
```python
# See impl/claude/agents/i/data/ogent.py for pattern
class LiveAgentSource:
    async def poll(self) -> AgentSnapshot:
        # Fetch from real agent
        pass

    def subscribe(self, callback: Callable[[AgentSnapshot], None]) -> None:
        # Push updates to UI
        pass
```

### Emitting Visual Hints (from K-gent)
```python
# Agent-side: emit hints for custom UI
from agents.i.data.hints import VisualHint

hint = VisualHint(
    type="density",
    data={"activity": 0.8, "phase": "ACTIVE", "entropy": 0.3},
    position="main",
    priority=1,
)
```

### Wiring Screens to Live Data
```python
# In screen's on_mount():
async def on_mount(self) -> None:
    if not self.demo_mode:
        self.source = LiveAgentSource(self.agent_id)
        self.set_interval(1.0, self.refresh_from_source)

async def refresh_from_source(self) -> None:
    snapshot = await self.source.poll()
    self.update_display(snapshot)
```

---

## Testing Strategy

### Unit Tests
- Each widget has `_tests/test_*.py`
- Use `pytest` fixtures for common state
- Mock Textual's `App` for screen tests

### Integration Tests
- Test screen ↔ data source binding
- Test hint emission → widget rendering
- Test navigation between LOD levels

### Manual QA Checklist
- [ ] FluxScreen shows agent cards with correct phases
- [ ] CockpitScreen temperature slider works
- [ ] MRIScreen shows entropy distortion
- [ ] LoomScreen navigation (j/k/h/l) works
- [ ] Escape returns to menu from any screen
- [ ] Heartbeat animation visible on active agents
- [ ] Oblique Strategies appear at high entropy

---

## Questions to Answer

1. **How should FluxScreen discover available agents?**
   - Registry polling? Flux subscription? Manual config?

2. **What triggers CognitiveLoom updates?**
   - Every LLM call? Only on decisions? Manual checkpoint?

3. **How do we handle agent crashes in the UI?**
   - Show error state? Remove from view? Attempt reconnect?

4. **Should VisualHints be persisted?**
   - Transient (current run only)? Or saved with agent state?

---

## Files to Read First

1. `plans/interfaces/alethic-workbench.md` — Full vision document
2. `plans/interfaces/primitives.md` — Primitive specification (17/17 complete)
3. `plans/interfaces/implementation-roadmap.md` — Implementation checklist
4. `impl/claude/agents/i/demo_all_screens.py` — Entry point for demos
5. `impl/claude/agents/i/data/state.py` — Core state types
6. `impl/claude/agents/k/__init__.py` — K-gent entry point

---

## Success Criteria

The Alethic Workbench is "realized" when:

1. **Live agent observation**: FluxScreen shows real running agents
2. **Interactive manipulation**: Temperature slider affects actual LLM calls
3. **Decision archaeology**: LoomScreen shows real branching history
4. **Multi-agent orchestration**: Multiple agents visible with flow arrows
5. **Zero demo mode**: All `create_demo_*()` functions replaced with live sources
6. **Joy-inducing**: Operators want to use it, not just tolerate it

---

## Command Reference

```bash
# Run demo
uv run python impl/claude/agents/i/demo_all_screens.py

# Run tests
uv run pytest impl/claude/agents/i/ -v

# Type check
uv run mypy impl/claude/agents/i/ --strict

# Run K-gent (for live testing)
kg soul challenge "test prompt"

# Check flux sources
ls impl/claude/agents/flux/sources/
```

---

*"The interface should make the invisible visible—not just status, but the soul of the agent."*
