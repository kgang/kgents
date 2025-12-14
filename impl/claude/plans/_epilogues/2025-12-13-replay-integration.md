# Epilogue: Replay Integration Session (2025-12-13)

## Session Intent
Wire the HotData "Day in the Life" scenario to the dashboard for animated playback, proving the holographic principle: the Turn IS the fundamental unit from which all dashboard state derives.

## Artifacts Created

### impl/claude/agents/i/data/replay_integration.py (~350 lines)
Bridge between HotData scenarios and ReplayController:
- `turn_event_to_turn(event, index)` - Convert TurnEvent → Turn
- `scenario_to_turns(scenario)` - Full conversion with parent/child linking
- `create_replay_from_scenario()` - Factory for ReplayController
- `ScenarioReplayProvider` - Async metrics stream from replay playback
- `ReplayState` - Current playback state dataclass
- `ReplayControls` - UI control state dataclass

### impl/claude/agents/i/widgets/replay_controls.py (~200 lines)
Textual widget for replay controls:
- Play/Pause button (space)
- Speed indicator with cycle (s)
- Progress bar with percentage
- Time label (simulated hour)
- Turn preview (truncated content)

### Dashboard Integration (screens/dashboard.py)
- Added `replay_mode` parameter to DashboardScreen
- Added `ScenarioReplayProvider` initialization on mount
- Added keybindings: `p` (toggle replay), `space` (play/pause), `s` (speed)
- Updated status bar to show replay state when active
- Added `run_dashboard(replay_mode=True)` entry point

## Key Insight
The holographic principle validated: 24 TurnEvents generate complete dashboard state for any simulated hour:
- K-gent panel: mode, garden lifecycle, interactions
- Metabolism panel: pressure, temperature, fever state
- Flux panel: events/sec, queue depth, active agents
- Traces panel: recent AGENTESE invocations
- Weather widget: entropy-derived forecast

## Tests Passed
1. All imports successful
2. Scenario created with 24 turn events
3. Turn conversion preserves content, duration, parent/child links
4. ReplayController accepts converted turns
5. ScenarioReplayProvider generates 11 metric updates in 1 second at 4x speed
6. Dashboard instantiation with replay_mode=True

## Continuation Track
**Next: Track A (Triad Reality Wiring)** - Connect to actual database health checks for production dashboard, or **Track C (Pheromone Visualization)** - Convert turn→turn edges into stigmergic trails.

## Verification Commands
```bash
# Quick test
uv run python -c "
from impl.claude.agents.i.data.replay_integration import ScenarioReplayProvider
import asyncio
async def t():
    p = ScenarioReplayProvider()
    u = []
    p.on_metrics_update = lambda m: u.append(m)
    await p.start_replay(speed=4.0)
    await asyncio.sleep(1.0)
    await p.stop()
    print(f'{len(u)} updates, hour {p.state.current_hour}')
asyncio.run(t())
"

# Interactive replay
uv run python -c "from impl.claude.agents.i.screens.dashboard import run_dashboard; run_dashboard(replay_mode=True)"
```

## Session Principle
*"The demo IS the system showing itself."* (AD-004)

The replay mode doesn't simulate a dashboard—it replays actual scenario data through the same metrics pipeline used in production. The form is the function.

---

## Continuation Session: Tracks D & E (Night)

### Track D: Dynamic Widget Mounting (COMPLETE)

Fixed `action_toggle_replay()` to dynamically mount/unmount the `ReplayControlsWidget`:

```python
async def action_toggle_replay(self) -> None:
    if self.replay_mode:
        # Dynamically mount replay controls widget
        if self._replay_controls is None:
            self._replay_controls = ReplayControlsWidget(id="replay-controls")
            await self.mount(self._replay_controls, before=self._status_bar)
        self._replay_controls.set_provider(self._replay_provider)
    else:
        if self._replay_controls:
            await self._replay_controls.remove()
            self._replay_controls = None
```

**Key insight**: Use `before=` parameter for visual ordering.

### Track E: Hour Jump Key Propagation (COMPLETE)

Added hour jumping at DashboardScreen level via `on_key()`:

```python
def on_key(self, event: Key) -> None:
    if self.replay_mode and self._replay_provider:
        hour_map = {"0": 0, "1": 3, "2": 6, "3": 9, "4": 12, "5": 15, "6": 18, "7": 21}
        if event.key in hour_map:
            self._replay_provider.seek_to_hour(hour_map[event.key])
            event.prevent_default()
            return
```

Added actions for bracket keys:
- `[` - `action_seek_hour_back` - Decrement hour
- `]` - `action_seek_hour_forward` - Increment hour

### Complete Keybinding Summary (Replay Mode)

| Key | Action |
|-----|--------|
| `p` | Toggle replay mode |
| `space` | Play/Pause |
| `s` | Cycle speed (0.25x → 4x) |
| `0-7` | Jump to hour (0=00:00, 7=21:00) |
| `[` | Seek hour back |
| `]` | Seek hour forward |

### Remaining Tracks
- **Track A**: Triad Reality Wiring (production DB health checks)
- **Track C**: Pheromone Visualization (stigmergic trails)
