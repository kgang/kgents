# Replay Integration Continuation (Post-Wiring Session)

> Continue from the Replay Integration session. Track B complete; replay controls wired to dashboard.

## ATTACH

/hydrate

Previous session (2025-12-13 Night) completed:

1. **TurnEvent → Turn adapter** - `turn_event_to_turn()` converts HotData scenario events to ReplayController-compatible Turns
2. **ScenarioReplayProvider** - Bridges replay playback to dashboard metrics stream
3. **ReplayControlsWidget** - Textual widget with Play/Pause/Speed controls
4. **Dashboard integration** - `p` toggles replay mode, `space` play/pause, `s` cycle speed

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Replay Integration | COMPLETE | `impl/claude/agents/i/data/replay_integration.py` |
| Replay Controls Widget | COMPLETE | `impl/claude/agents/i/widgets/replay_controls.py` |
| Dashboard Replay Mode | COMPLETE | `p` key toggles, status bar shows state |
| End-to-end Test | PASSED | 11 updates in 1 second at 4x speed |

## Artifacts Created

- `impl/claude/agents/i/data/replay_integration.py` - 350+ lines
  - `turn_event_to_turn()` - TurnEvent → Turn conversion
  - `scenario_to_turns()` - Full scenario conversion with parent/child linking
  - `create_replay_from_scenario()` - Factory for ReplayController
  - `ScenarioReplayProvider` - Async metrics stream from replay
  - `ReplayControls` - Data class for control widget state

- `impl/claude/agents/i/widgets/replay_controls.py` - 200+ lines
  - `ReplayControlsWidget` - Textual widget with keybindings
  - Progress bar, speed indicator, turn preview

## Usage

```bash
# Run dashboard with replay mode
uv run python -c "from impl.claude.agents.i.screens.dashboard import run_dashboard; run_dashboard(replay_mode=True)"

# Or toggle with 'p' key while running
uv run python -c "from impl.claude.agents.i.screens.dashboard import run_dashboard; run_dashboard(demo_mode=True)"
```

## Next Tracks

### Track A: Triad Reality Wiring (Production Ready)

Wire Triad metrics to actual database health checks:
```python
async def collect_triad_metrics() -> TriadMetrics:
    # PostgreSQL: asyncpg connection pool stats
    # Qdrant: vector store health via qdrant_client
    # Redis: cache hit/miss rates via redis-py
```

**Requires**: Running databases or K8s port-forwarding.

### Track C: Pheromone Visualization

Convert turn→turn causal edges into stigmergic deposits for Observatory/Terrarium:
```python
from agents.i.data.pheromone import PheromoneManager

# TurnEvent[N] → TurnEvent[N+1] = edge
# Edge intensity = sum(entropy_cost)
pheromone.deposit(from_=turn_n.id, to=turn_n1.id, intensity=turn_n.entropy_cost)
```

### Track D: Replay Controls Widget Integration

The ReplayControlsWidget is created but not wired to the compose() flow when replay_mode is toggled dynamically. Fix:
```python
async def action_toggle_replay(self) -> None:
    if self.replay_mode:
        # Mount the replay controls widget dynamically
        await self.mount(self._replay_controls)
    else:
        # Remove the widget
        if self._replay_controls:
            await self._replay_controls.remove()
```

### Track E: Hour Jumping (0-9 keys)

The ReplayControlsWidget has bindings for 0-7 keys to jump to hours, but these need to be propagated to the DashboardScreen level for seamless control.

## Meta-Learning Applied

```
Turn-driven dashboard: single trace derives all panels; the Turn IS the fundamental unit (holographic)
The demo IS the system showing itself (AD-004): replay mode doesn't simulate—it uses real scenario data
```

The 24-turn DayScenario proves the holographic principle: all dashboard state derives from the Turn trace.

## Verification

```bash
# Test replay provider
uv run python -c "
import asyncio
from impl.claude.agents.i.data.replay_integration import ScenarioReplayProvider

async def test():
    provider = ScenarioReplayProvider()
    updates = []
    provider.on_metrics_update = lambda m: updates.append(m)
    await provider.start_replay(speed=4.0)
    await asyncio.sleep(1.0)
    await provider.stop()
    print(f'Received {len(updates)} updates')
    print(f'Final hour: {provider.state.current_hour}')

asyncio.run(test())
"

# Run interactive dashboard in replay mode
uv run python -c "from impl.claude.agents.i.screens.dashboard import run_dashboard; run_dashboard(replay_mode=True)"
```

## Continuation Imperative

Upon completing any Track, generate the next continuation prompt.
The form is the function.

---

*Epilogue: plans/_epilogues/2025-12-13-replay-integration.md*
