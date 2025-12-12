# Terrarium Implementation Prompt

> *Use this prompt to guide the implementation of the Terrarium Web Gateway.*

---

## Context for the Implementing Agent

You are implementing **Terrarium** for kgents—a web gateway that exposes FluxAgents as WebSocket streams with the **Mirror Protocol**. This is not a UI framework—it's a thin bridge that projects existing capabilities to the browser.

### Pre-Reading (Critical)

Before writing any code, read these documents in order:

1. **`plans/agents/terrarium.md`** — The plan (THIS IS YOUR NORTH STAR)
2. **`spec/principles.md`** — Design constraints (ALL work must honor these)
3. **`plans/principles.md`** — The Forest Protocol (how plans coordinate)
4. **`impl/claude/agents/flux/agent.py`** — FluxAgent implementation (261 tests)
5. **`impl/claude/agents/flux/perturbation.py`** — Perturbation pattern (you'll reuse this)
6. **`impl/claude/protocols/cli/prism/`** — Prism pattern for CLI → REST bridge
7. **`plans/agents/semaphores.md`** — Purgatory Pattern (Phase 5 integration)

---

## The Single Most Important Thing

**THE MIRROR PROTOCOL**. This is non-negotiable.

The original design connected WebSockets directly to FluxAgents. This violates the AGENTESE principle: *"To Observe is to Disturb."*

If 50 browsers connect to watch an agent, the agent must NOT expend entropy calculating projections for each observer.

**Two Endpoints, Two Purposes**:

| Endpoint | Name | Auth | Entropy Cost | Purpose |
|----------|------|------|--------------|---------|
| `ws://*/perturb/{agent_id}` | The Beam | Required | High | Write: inject Perturbation |
| `ws://*/observe/{agent_id}` | The Reflection | None | Zero | Read: broadcast mirror |

The agent emits to a **HolographicBuffer**. The buffer broadcasts to N clients. Slow clients don't slow the agent.

```
Agent ──emit once──▶ HolographicBuffer ──broadcast──▶ [Client C, D, E, F...]
                          │
                          └── History buffer (100 events)
```

---

## Implementation Phases

### Phase 1: WebSocket Gateway with Mirror Protocol (START HERE)

**Goal**: FastAPI server with split endpoints.

**Directory Structure**:
```
impl/claude/protocols/terrarium/
├── __init__.py
├── gateway.py              # FastAPI application
├── mirror.py               # HolographicBuffer implementation
├── perturb_handler.py      # /perturb endpoint (write path)
├── observe_handler.py      # /observe endpoint (read-only mirror)
├── config.py               # Server configuration
└── _tests/
    ├── __init__.py
    ├── test_gateway.py
    ├── test_mirror.py
    └── test_perturb.py
```

**Core Implementation - HolographicBuffer**:

```python
# mirror.py
from collections import deque
from dataclasses import dataclass, field
import asyncio
from typing import Any
from fastapi import WebSocket

@dataclass
class HolographicBuffer:
    """
    The Mirror.
    Decouples the Agent's metabolism from the Observer's curiosity.

    The agent emits events ONCE to the buffer.
    The buffer broadcasts to N clients.
    Slow clients don't slow the agent.
    """
    max_history: int = 100

    _active_mirrors: list[WebSocket] = field(default_factory=list, init=False)
    _history: deque[dict[str, Any]] = field(init=False)

    def __post_init__(self) -> None:
        self._history = deque(maxlen=self.max_history)

    async def reflect(self, event: dict[str, Any]) -> None:
        """
        Called by FluxAgent. Does NOT await client acknowledgments.

        Fire and forget—don't let slow clients slow the agent.
        """
        self._history.append(event)
        # Fire and forget: don't await the broadcast
        asyncio.create_task(self._broadcast(event))

    async def _broadcast(self, event: dict[str, Any]) -> None:
        """Broadcast to all mirrors, ignoring failures."""
        import json
        payload = json.dumps(event)
        results = await asyncio.gather(*[
            ws.send_text(payload)
            for ws in self._active_mirrors
        ], return_exceptions=True)
        # Remove disconnected mirrors
        self._active_mirrors = [
            ws for ws, result in zip(self._active_mirrors, results)
            if not isinstance(result, Exception)
        ]

    async def attach_mirror(self, websocket: WebSocket) -> None:
        """Connect a read-only observer (The Reflection)."""
        import json
        await websocket.accept()
        self._active_mirrors.append(websocket)
        # Send initial snapshot (The Ghost)
        for event in self._history:
            await websocket.send_text(json.dumps(event))

    def detach_mirror(self, websocket: WebSocket) -> None:
        """Remove an observer."""
        if websocket in self._active_mirrors:
            self._active_mirrors.remove(websocket)
```

**Core Implementation - Gateway**:

```python
# gateway.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .mirror import HolographicBuffer

app = FastAPI(title="kgents Terrarium")

# Registry of agents and their mirrors
agent_mirrors: dict[str, HolographicBuffer] = {}

@app.websocket("/perturb/{agent_id}")
async def ws_perturb(websocket: WebSocket, agent_id: str) -> None:
    """
    The Beam: High entropy, auth required, injects Perturbation.
    """
    # TODO: Add authentication middleware
    await websocket.accept()

    flux_agent = get_agent(agent_id)  # Implement agent registry
    if flux_agent is None:
        await websocket.close(code=4004, reason="Agent not found")
        return

    try:
        while True:
            data = await websocket.receive_text()
            # Reuse existing perturbation pattern
            from impl.claude.agents.flux.perturbation import create_perturbation
            perturbation = create_perturbation(data, priority=100)
            await flux_agent._perturbation_queue.put(perturbation)

            # Wait for result and send back
            result = await perturbation.result_future
            await websocket.send_text(str(result))
    except WebSocketDisconnect:
        pass

@app.websocket("/observe/{agent_id}")
async def ws_observe(websocket: WebSocket, agent_id: str) -> None:
    """
    The Reflection: Zero entropy to agent, broadcast mirror.
    """
    mirror = agent_mirrors.get(agent_id)
    if mirror is None:
        await websocket.close(code=4004, reason="Agent not found")
        return

    await mirror.attach_mirror(websocket)

    try:
        # Keep connection alive; mirror broadcasts push events
        while True:
            await websocket.receive_text()  # Listen for pings/disconnect
    except WebSocketDisconnect:
        mirror.detach_mirror(websocket)
```

**Exit Criteria**:

1. `pytest protocols/terrarium/_tests/test_mirror.py` passes
2. Mirror broadcasts to 100 mock observers without blocking agent
3. `reflect()` returns in <10ms regardless of observer count
4. Disconnected observers are cleaned up automatically

### Phase 2: Prism REST Bridge

**Goal**: Auto-generate REST endpoints from CLICapable agents.

**Reuse Prism's type mapping** (`impl/claude/protocols/cli/prism/type_mapping.py`) for request/response schemas.

```python
# rest_bridge.py
from fastapi import FastAPI, APIRouter
from impl.claude.protocols.cli.prism import Prism
from impl.claude.protocols.cli.prism.protocol import CLICapable

class PrismRestBridge:
    """Generate REST endpoints from CLICapable agents."""

    def mount(self, app: FastAPI, agent: CLICapable) -> None:
        """Mount all exposed commands as REST endpoints."""
        router = APIRouter(prefix=f"/api/{agent.genus_name}")

        for name, method in agent.get_exposed_commands().items():
            endpoint = self._method_to_endpoint(name, method)
            router.add_api_route(
                f"/{name}",
                endpoint,
                methods=["POST"],
            )

        app.include_router(router)
```

**Exit Criteria**:
```bash
curl -X POST http://localhost:8080/api/grammar/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Create a calendar"}'
# Returns parsed result
```

### Phase 3: I-gent Widget Server

**Goal**: Serve I-gent dashboard widgets over WebSocket.

```python
# events.py
from dataclasses import dataclass

@dataclass
class TerriumEvent:
    """Event for I-gent widget updates."""
    agent_id: str
    state: str       # FluxState enum value
    pressure: float  # Queue depth (0-100)
    flow: float      # Events/second
    temperature: float  # Metabolic heat

    def as_json(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "pressure": self.pressure,
            "flow": self.flow,
            "temperature": self.temperature,
        }
```

**Exit Criteria**: Browser shows live DensityField of running agents.

### Phase 4: K8s Operator

**Goal**: AgentServer CRD and operator.

See `plans/_archive/k8-terrarium-v2.0-complete.md` for existing K8s patterns.

**Exit Criteria**:
```bash
kubectl apply -f agentserver.yaml
# Deploys gateway, agents, and UI
```

### Phase 5: Purgatory Integration

**Goal**: Semaphores in Purgatory are visible and resolvable via Agent Server.

**Key Integration**: When FluxAgent detects a `SemaphoreToken` result, emit to mirror:

```python
# In FluxAgent processing (future integration)
if isinstance(result, SemaphoreToken):
    await purgatory.save(result)
    # Broadcast to observers via mirror
    await mirror.reflect({
        "type": "semaphore_ejected",
        "token": {
            "id": result.id,
            "prompt": result.prompt,
            "options": result.options,
            "severity": result.severity,
        }
    })
```

**Purgatory REST endpoints**:

```python
# purgatory_handler.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/purgatory")

class ResolveRequest(BaseModel):
    human_input: str

@router.get("/{agent_id}/pending")
async def list_pending(agent_id: str):
    """List pending semaphores for an agent."""
    ...

@router.post("/{agent_id}/resolve/{token_id}")
async def resolve(agent_id: str, token_id: str, request: ResolveRequest):
    """Resolve a pending semaphore."""
    ...
```

**Exit Criteria**: Observer receives `semaphore_ejected` events via Mirror.

---

## Critical Constraints

### From spec/principles.md

| Principle | Constraint for Terrarium |
|-----------|--------------------------|
| **Tasteful** | Thin gateway only. No UI framework. |
| **Composable** | WebSocket IS a Flux source. Don't invent new abstractions. |
| **Heterarchical** | Agents run autonomously, UI observes. |
| **Ethical** | Users SEE agents thinking (transparency). |
| **Generative** | Spec can generate FastAPI routes. |

### Technical Constraints

- **Python 3.12+** — Use `Generic[A]` pattern, not `class Foo[A]`
- **Mypy strict** — 0 errors required (`uv run mypy .`)
- **All 8,741+ existing tests must pass** — Run `uv run pytest -m "not slow" -q`
- **Use `uv run`** for dependency management
- **FastAPI + Starlette** for WebSocket handling

### KENT's NEVERS (from `plans/_focus.md`)

- Do NOT place requirements for hitting some number of tests
- Describe tests conceptually, apply the Generativity principle
- Being/having fun is free :)

---

## Gotchas to Avoid

1. **Don't connect WebSocket directly to agent** — Use Mirror Protocol. Observers don't disturb agents.

2. **Don't build a UI framework** — Serve static HTML, update via WebSocket. This is a bridge, not Streamlit.

3. **Don't bypass Prism** — REST bridge USES Prism, doesn't replace it. Reuse `type_mapping.py`.

4. **Don't ignore backpressure** — FluxConfig policies apply to WebSocket too. Respect `buffer_size`.

5. **Don't forget Purgatory visibility** — When semaphores are implemented, they must be observable through the Mirror.

6. **Don't block on slow clients** — `reflect()` must fire-and-forget. Use `asyncio.create_task()`.

---

## Validation Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Before starting (baseline)
uv run mypy .                    # Must be 0 errors
uv run pytest -m "not slow" -q   # All tests pass

# During development
uv run pytest protocols/terrarium/_tests/ -v

# After each phase
uv run mypy .                    # Still 0 errors
uv run pytest -m "not slow" -q   # Still pass + new tests
```

---

## Questions You May Encounter

1. **How do we handle multiple WebSocket clients for the same agent?**
   → Mirror Protocol. One HolographicBuffer per agent, N observers subscribe.

2. **How does authentication work?**
   → Defer to middleware. `/perturb` requires auth, `/observe` is public.

3. **How do we rate-limit WebSocket messages?**
   → Reuse FluxConfig.buffer_size. Reject when queue full.

4. **How do we visualize pheromones in the UI?**
   → Phase 3. TerriumEvent carries pressure/flow/temperature.

5. **What if Semaphores aren't implemented yet?**
   → Phase 5 can be deferred. The plan declares dependency on `agents/semaphores`.

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Mypy errors | 0 |
| Existing tests | Still pass (8,741+) |
| WebSocket `/observe` latency | <50ms to attach |
| `/perturb` round-trip | <100ms (depends on agent) |
| Mirror broadcast | <10ms regardless of N observers |
| Memory per observer | <1MB |

---

## Session Protocol

Per `plans/principles.md`:

1. **Read `_forest.md`** at session start for canopy view
2. **Allocate attention** — Terrarium is dormant (Accursed Share rotation)
3. **Update plan YAML header** when making progress
4. **Write epilogue** to `plans/_epilogues/` when session ends

---

## After Implementation

1. Wire to `world.terrarium.*` AGENTESE paths
2. Update `plans/_forest.md` with new progress
3. Add Terrarium to I-gent as a reflector target
4. Create demo: Living Pipeline visualized in browser

---

*"The terrarium is not a cage. It is a window into life. The mirror shows without disturbing."*
