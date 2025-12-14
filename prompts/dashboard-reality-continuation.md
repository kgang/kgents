# Dashboard Reality Continuation (Post-Wiring Session)

> Continue from the Dashboard Reality Wiring session. All Quick Wins complete; HotData fixture created.

## ATTACH

/hydrate

Previous session (2025-12-13 Night) completed:

1. **Garden lifecycle visualization** - K-gent panel now shows `🌱2 🌿4 🌳5 🌸1` with season emoji
2. **Metabolism sparkline** - Pressure history, fever count, tithe tracking all wired
3. **Weather forecast with trend** - `set_trend(delta)` uses pressure history for prediction
4. **HotData "Day in the Life" fixture** - 24 turns, 24-hour pressure curve, garden evolution

## Current State

| Panel | Status | Next Step |
|-------|--------|-----------|
| K-gent | REAL + Lifecycle | Wire to active CLI session for interactions count |
| Metabolism | REAL + History | Wire last_tithe from actual engine |
| Triad | DEMO | **Wire to K8s/local DB health checks** |
| Flux | DEMO | **Wire to running Synapse metrics** |
| Turns | REAL (empty) | **Feed HotData to ReplayController** |
| Weather | DERIVED + Trend | Forecast uses pressure trend |
| Traces | DEMO | Wire to Logos invocation history |

## Artifacts Created

- `impl/claude/agents/i/data/hot_data.py` - 450 lines, Turn-driven scenario
- `impl/claude/agents/i/data/dashboard_collectors.py` - `create_scenario_metrics(hour)`
- `plans/_epilogues/2025-12-13-dashboard-reality-wiring.md` - Session epilogue

## Next Tracks

### Track A: Triad Reality Wiring (Production Ready)

Wire Triad metrics to actual database health:
```python
async def collect_triad_metrics() -> TriadMetrics:
    # PostgreSQL: Connection pool stats via asyncpg
    # Qdrant: Vector store health via qdrant_client
    # Redis: Cache hit/miss rates via redis-py
```

**Requires**: Running databases or K8s context with port-forwarding.

### Track B: Replay Integration

Feed `hot_data.py` scenario to `ReplayController` for animated playback:
```python
from agents.i.data.hot_data import create_day_scenario
from agents.i.navigation.replay import ReplayController

scenario = create_day_scenario()
controller = ReplayController(events=[...])  # Convert TurnEvents
async for event in controller.play(speed=10.0):  # 10x speed
    dashboard.update(event)
```

**Principle**: The demo IS the system showing itself (AD-004).

### Track C: Pheromone Visualization

Convert turn→turn causal edges into stigmergic deposits:
```python
from agents.i.data.pheromone import PheromoneManager

# TurnEvent[N] → TurnEvent[N+1] = edge
# Edge intensity = sum(entropy_cost)
pheromone.deposit(from_=turn_n.id, to=turn_n1.id, intensity=turn_n.entropy_cost)
```

Visualize in Observatory/Terrarium as trails between agents.

## Meta-Learning Applied

```
Turn-driven dashboard: single trace derives all panels; the Turn IS the fundamental unit (holographic)
```

The HotData scenario proves this: 24 TurnEvents → complete dashboard state for any hour.

## Verification

```bash
# Test scenario metrics at different hours
uv run python -c "
from agents.i.data.dashboard_collectors import create_scenario_metrics
for hour in [8, 12, 15, 20]:
    m = create_scenario_metrics(hour)
    print(f'{hour}:00 - {m.kgent.garden_patterns} patterns, {m.metabolism.pressure:.0%} pressure')
"

# Run dashboard in live mode
uv run python -c "from agents.i.screens.dashboard import run_dashboard; run_dashboard(demo_mode=False)"

# Run dashboard with scenario (demo mode uses it now)
uv run python -c "from agents.i.screens.dashboard import run_dashboard; run_dashboard(demo_mode=True)"
```

## Continuation Imperative

Upon completing any Track, generate the next continuation prompt.
The form is the function.

---

*Epilogue: plans/_epilogues/2025-12-13-dashboard-reality-wiring.md*
