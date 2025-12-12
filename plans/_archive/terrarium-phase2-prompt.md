# Terrarium Phase 2 Continuation Prompt

> *Use this prompt to continue Terrarium implementation.*

---

## Context

Phase 1 of Terrarium is complete:
- `HolographicBuffer` implements the Mirror Protocol (fire-and-forget broadcast)
- Gateway provides `/perturb` and `/observe` WebSocket endpoints
- 45 tests passing, mypy clean

**Commit**: `feat(terrarium): Implement Phase 1 - WebSocket Gateway with Mirror Protocol`

---

## Phase 2: Prism REST Bridge

**Goal**: Auto-generate REST endpoints from CLICapable agents.

### Key Files to Read

1. `impl/claude/protocols/cli/prism/` — Prism pattern
2. `impl/claude/protocols/cli/prism/type_mapping.py` — Type → JSON schema
3. `impl/claude/protocols/cli/prism/protocol.py` — CLICapable protocol

### Implementation

```python
# rest_bridge.py (new file in protocols/terrarium/)
from fastapi import APIRouter
from protocols.cli.prism import Prism, CLICapable

class PrismRestBridge:
    """Generate REST endpoints from CLICapable agents."""

    def mount(self, app: FastAPI, agent: CLICapable) -> None:
        """Mount all exposed commands as REST endpoints."""
        router = APIRouter(prefix=f"/api/{agent.genus_name}")

        for name, method in agent.get_exposed_commands().items():
            endpoint = self._method_to_endpoint(name, method)
            router.add_api_route(f"/{name}", endpoint, methods=["POST"])

        app.include_router(router)

    def _method_to_endpoint(self, name: str, method: Callable) -> Callable:
        """Convert a CLI method to a FastAPI endpoint."""
        # Use Prism's type introspection
        ...
```

### Exit Criteria

```bash
curl -X POST http://localhost:8080/api/grammar/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Create a calendar"}'
# Returns parsed result from GrammarAgent
```

---

## Phase 3: I-gent Widget Server

**Goal**: Serve live agent metrics over WebSocket for I-gent dashboard.

### Key Insight

`TerriumEvent` already carries pressure/flow/temperature. We need:
1. A way to poll running FluxAgents for metrics
2. Periodic emission to the HolographicBuffer
3. I-gent widget that consumes the WebSocket stream

### Implementation

```python
# metrics.py (new file)
async def emit_metrics_loop(
    agent_id: str,
    flux_agent: FluxAgent,
    buffer: HolographicBuffer,
    interval: float = 1.0,
) -> None:
    """Periodically emit metabolism metrics."""
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
```

### Exit Criteria

Browser shows live DensityField of running agents with updating metrics.

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

- **Tasteful**: Thin bridge, not a framework
- **Composable**: REST endpoints use Prism, don't reinvent
- **Heterarchical**: Agents run autonomously, REST is a view

---

*"The terrarium is not a cage. It is a window into life."*
