# Terrarium Phase 3 Continuation Prompt

> *Use this prompt to continue Terrarium implementation.*

---

## Context

Phases 1 & 2 of Terrarium are complete:
- **Phase 1**: `HolographicBuffer` (Mirror Protocol) + WebSocket Gateway
- **Phase 2**: `PrismRestBridge` auto-generates REST from CLICapable agents
- 75 tests passing, mypy clean, FastAPI installed

**Commits**:
- `feat(terrarium): Implement Phase 1 - WebSocket Gateway with Mirror Protocol`
- `feat(terrarium): Implement Phase 2 - PrismRestBridge for REST endpoints`

---

## Phase 3: I-gent Widget Server

**Goal**: Serve live agent metrics over WebSocket for I-gent dashboard visualization.

### Key Files to Read

1. `impl/claude/protocols/terrarium/events.py` — `TerriumEvent` with pressure/flow/temperature
2. `impl/claude/protocols/terrarium/mirror.py` — `HolographicBuffer.reflect()`
3. `impl/claude/agents/flux/` — FluxAgent state and metabolism

### The Insight

`TerriumEvent` already carries pressure/flow/temperature. We need:
1. A way to poll running FluxAgents for metrics
2. Periodic emission to the HolographicBuffer
3. I-gent widget that consumes the WebSocket stream

### Implementation

```python
# metrics.py (new file in protocols/terrarium/)
import asyncio
from typing import TYPE_CHECKING

from .events import make_metabolism_event
from .mirror import HolographicBuffer

if TYPE_CHECKING:
    from agents.flux import FluxAgent


async def emit_metrics_loop(
    agent_id: str,
    flux_agent: "FluxAgent",
    buffer: HolographicBuffer,
    interval: float = 1.0,
) -> None:
    """
    Periodically emit metabolism metrics.

    Runs until the FluxAgent stops. Called when an agent is registered
    with the Terrarium if metrics emission is enabled.

    Args:
        agent_id: Unique identifier for the agent
        flux_agent: The FluxAgent to poll for metrics
        buffer: HolographicBuffer to emit events to
        interval: Polling interval in seconds
    """
    while flux_agent.is_running:
        event = make_metabolism_event(
            agent_id=agent_id,
            pressure=calculate_pressure(flux_agent),
            flow=calculate_flow(flux_agent),
            temperature=calculate_temperature(flux_agent),
            state=flux_agent.state.value,
        )
        await buffer.reflect(event.as_dict())
        await asyncio.sleep(interval)


def calculate_pressure(flux_agent: "FluxAgent") -> float:
    """
    Calculate queue pressure (backlog) as 0-100 scale.

    Pressure = how backed up is the agent's input queue?
    """
    # TODO: Access flux_agent's internal queue depth
    # Normalize to 0-100 scale
    return 0.0


def calculate_flow(flux_agent: "FluxAgent") -> float:
    """
    Calculate throughput (events/second).

    Flow = how fast is work moving through?
    """
    # TODO: Track events processed over time window
    return 0.0


def calculate_temperature(flux_agent: "FluxAgent") -> float:
    """
    Calculate metabolic heat (entropy consumption rate).

    Temperature = how hard is the agent working?
    High temperature = high LLM usage, complex processing
    """
    # TODO: Track token consumption, API calls
    return 0.0
```

### Integration with Terrarium

```python
# In gateway.py or a new file
class MetricsManager:
    """Manages metrics emission for registered agents."""

    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}

    def start_metrics(
        self,
        agent_id: str,
        flux_agent: "FluxAgent",
        buffer: HolographicBuffer,
        interval: float = 1.0,
    ) -> None:
        """Start emitting metrics for an agent."""
        if agent_id in self._tasks:
            return  # Already running

        task = asyncio.create_task(
            emit_metrics_loop(agent_id, flux_agent, buffer, interval)
        )
        self._tasks[agent_id] = task

    def stop_metrics(self, agent_id: str) -> None:
        """Stop emitting metrics for an agent."""
        if agent_id in self._tasks:
            self._tasks[agent_id].cancel()
            del self._tasks[agent_id]
```

### Exit Criteria

Browser shows live DensityField of running agents with updating metrics:
- Connect to `/observe/{agent_id}` WebSocket
- Receive `{"type": "metabolism", "pressure": 45, "flow": 12.5, "temperature": 0.8}`
- Widget updates visualization in real-time

---

## Validation Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Before starting
uv run mypy protocols/terrarium/
uv run pytest protocols/terrarium/_tests/ -v

# After implementation
uv run pytest -m "not slow" -q  # All tests pass
```

---

## Principles to Honor

- **Tasteful**: Thin metrics layer, not a monitoring framework
- **Composable**: Metrics use existing events and buffer
- **Heterarchical**: Agents run autonomously, metrics are observation

---

## Stretch Goals (if time permits)

1. **Aggregate view**: `/api/metrics/all` returns all agent metrics at once
2. **Historical metrics**: Store last N minutes for sparklines
3. **Alert thresholds**: Emit "fever" event when temperature > threshold

---

*"The terrarium is not a cage. It is a window into life."*
