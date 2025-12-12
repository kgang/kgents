---
path: agents/terrarium
status: active
progress: 40
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Phase 1 COMPLETE: WebSocket Gateway with Mirror Protocol implemented.
  - HolographicBuffer: Fire-and-forget broadcast, 45 tests passing
  - Gateway: /perturb (The Beam), /observe (The Reflection) endpoints
  - Events: TerriumEvent, SemaphoreEvent for I-gent widget integration
  - Mypy: 0 errors (with type ignores for FastAPI decorators)
  Next: Phase 2 (Prism REST Bridge), Phase 3 (I-gent Widgets)
---

# Terrarium: The Agent Server Web Gateway

> *"The terrarium is not a cage. It is a window into life. The mirror shows without disturbing."*

**AGENTESE Context**: `world.terrarium.*`, `self.flux.bridge`
**Status**: Phase 1 Complete (40%)
**Principles**: Composable (WebSocket IS Flux), Tasteful (thin gateway), Heterarchical (observe, don't control)
**Cross-refs**: Flux Functor (archived), `agents/semaphores` (Purgatory), K8-Terrarium v2.0 (archived)

---

## Core Insight

Traditional agent APIs are request-response: you poke, it answers. This is the corpse model.

Agent Servers embrace the **Living Pipeline** paradigm from FluxAgent:
- WebSocket connections ARE Flux sources
- Agent outputs stream back in real-time
- I-gent widgets provide dashboard visualization
- The browser becomes a terrarium window into the hive mind

---

## The Mirror Protocol (Critical Architecture)

**The Observer Paradox**: If 50 users connect to "watch" an agent, does the agent expend Entropy calculating projections for them?

AGENTESE states: *"To Observe is to Disturb."* The original design (WebSocket directly to agent) risks **unbounded metabolic drain from passive observation**.

**Resolution**: The Mirror Protocol separates observation from interaction.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        THE MIRROR PROTOCOL                            │
│                                                                       │
│   /perturb (write)          FluxAgent           HolographicBuffer    │
│   ┌──────────┐             ┌──────────┐         ┌──────────┐         │
│   │ Client A │────────────▶│          │────────▶│ Broadcast │        │
│   │ Client B │────────────▶│ (The Real)│        └────┬──────┘        │
│   └──────────┘             └──────────┘              │               │
│                                                      ▼               │
│   /observe (read)                              ┌──────────┐          │
│   ┌──────────┐◀────────────────────────────────│ Client C │          │
│   │ Client D │◀────────────────────────────────│ Client E │          │
│   └──────────┘                                 └──────────┘          │
│                                                                       │
│   Key:                                                                │
│   /perturb = The Beam (high entropy, auth required, injects)         │
│   /observe = The Reflection (zero entropy to agent, broadcast)       │
└──────────────────────────────────────────────────────────────────────┘
```

**The Mechanism**:

1. **Beam (Write/Perturb)**: `ws://gateway/perturb/{agent_id}`
   - High entropy cost (agent processes input)
   - Requires authentication
   - Injects into FluxAgent's Perturbation queue
   - Rate-limited per client

2. **Reflection (Read-Only)**: `ws://gateway/observe/{agent_id}`
   - Zero entropy cost to the agent
   - No authentication required (public mirror)
   - Subscribes to HolographicBuffer broadcast
   - N clients share one emission

---

## AGENTESE Path Integration

| Path | Operation | Returns |
|------|-----------|---------|
| `world.terrarium.agents.manifest` | List running agents | AgentStatus[] |
| `world.terrarium.connect` | Open WebSocket | ConnectionHandle |
| `world.terrarium.dashboard.manifest` | Render I-gent view | HTML/Widget |
| `self.flux.bridge` | Get WebSocket bridge | FluxWebSocketBridge |
| `void.terrarium.metabolism` | System-wide health | MetabolismStatus |

---

## Integration Points

### With Flux

WebSocket IS a bidirectional stream:
- Client → Server: Flux source (perturbations)
- Server → Client: Flux output (results)

### With Semaphores/Purgatory

When an event yields to Purgatory:
1. `/observe` shows the semaphore state (token visible in broadcast)
2. `/perturb` can send the resolution context
3. The Agent Server UI can render semaphore as interactive card

**This unifies Terrarium with the Rodizio Pattern**: Purgatory is observable through the Mirror.

### With I-gent

I-gent widgets find their home:
- DensityField shows agent activity
- FluxReflector bridges CLI ↔ Web
- Glitch aesthetics make the terrarium delightful

### With K8-Terrarium

Leverages existing K8-Terrarium infrastructure:
- Ghost Protocol provides offline resilience
- Cognitive Probes ensure agent health
- Pheromone CRs enable inter-agent signaling visible in UI

---

## Implementation Phases

### Phase 1: WebSocket Gateway with Mirror Protocol

**Goal**: FastAPI server with split endpoints: `/perturb` (write) and `/observe` (read-only).

**Files**:
```
impl/claude/protocols/terrarium/
├── __init__.py
├── gateway.py              # FastAPI application
├── mirror.py               # HolographicBuffer implementation
├── perturb_handler.py      # /perturb endpoint (write path)
├── observe_handler.py      # /observe endpoint (read-only mirror)
├── config.py               # Server configuration
└── _tests/
```

**Exit Criteria**: Mirror broadcasts to N observers without slowing agent.

### Phase 2: Prism REST Bridge

**Goal**: Auto-generate REST endpoints from CLICapable agents.

**Key Insight**: Reuse Prism's type mapping for request/response schemas.

**Exit Criteria**: `POST /api/grammar/parse` works via CLI → REST bridge.

### Phase 3: I-gent Widget Server

**Goal**: Serve I-gent dashboard widgets over WebSocket.

**Exit Criteria**: Browser shows live DensityField of running agents.

### Phase 4: K8s Operator

**Goal**: AgentServer CRD and operator for K8s deployment.

**Exit Criteria**: `kubectl apply -f agentserver.yaml` deploys working terrarium.

### Phase 5: Purgatory Integration

**Goal**: Semaphores in Purgatory are visible and resolvable via Agent Server.

**Exit Criteria**: Observer receives `semaphore_ejected` events via Mirror.

---

## Key Types

```python
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
    _active_mirrors: list[WebSocket]
    _history: deque

    async def reflect(self, event: dict) -> None:
        """Fire and forget—don't let slow clients slow the agent."""

    async def attach_mirror(self, websocket: WebSocket) -> None:
        """Connect a read-only observer (The Reflection)."""

@dataclass
class TerriumEvent:
    """Event for I-gent widget updates."""
    agent_id: str
    state: str       # FluxState enum value
    pressure: float  # Queue depth
    flow: float      # Events/second
    temperature: float  # Metabolic heat
```

---

## Endpoint Summary

| Endpoint | Type | Auth | Entropy Cost | Purpose |
|----------|------|------|--------------|---------|
| `POST /api/{agent}/invoke` | REST | Yes | High | Discrete invocation |
| `ws://*/perturb/{agent}` | WebSocket | Yes | High | Stream perturbation |
| `ws://*/observe/{agent}` | WebSocket | No | Zero | Passive observation |
| `GET /api/{agent}/snapshot` | REST | No | Zero | Current state |

---

## Principle Assessment

| Principle | Assessment |
|-----------|------------|
| **Tasteful** | Thin gateway, projects existing capabilities |
| **Curated** | Not a UI framework, just a bridge |
| **Ethical** | Transparency: users SEE agents thinking |
| **Joy-Inducing** | Terrarium metaphor, I-gent widgets |
| **Composable** | WebSocket IS Flux source, composes naturally |
| **Heterarchical** | Agents run autonomously, users observe |
| **Generative** | Spec can generate FastAPI routes |

---

## Self-Debate Resolutions

### Q: Is Agent Server redundant with I-gent?
Different modalities for different contexts:
- I-gent TUI: Local terminal, developer-focused
- Agent Server: Remote access, browser-based, multi-user

They're complementary. I-gent widgets can be served *through* Agent Server.

### Q: Doesn't the Mirror add complexity?
The "simpler" design violated AGENTESE principle. Mirror Protocol:
- Protects agent metabolism
- Enables public dashboards (no auth for /observe)
- Scales to many observers without agent load

Complexity is justified when it honors a principle.

### Q: Why not use existing tools (Gradio, Streamlit)?
kgents has a specific paradigm:
- FluxAgent's AsyncIterator semantics
- AGENTESE path resolution
- Pheromone-based coordination
- Metabolism and entropy

Build a thin gateway that respects kgents semantics, not a UI framework.

---

## Cross-References

- **Spec**: `spec/c-gents/flux.md` — FluxAgent foundation
- **Spec**: `spec/principles.md` — Design constraints
- **Spec**: `spec/protocols/agentese.md` — "To Observe is to Disturb"
- **Plan**: `plans/_archive/k8-terrarium-v2.0-complete.md` — K8s infrastructure
- **Plan**: `plans/_archive/flux-functor-v1.0-complete.md` — Living Pipelines
- **Plan**: `plans/agents/semaphores.md` — Purgatory Pattern
- **Impl**: `impl/claude/protocols/cli/prism/` — CLI → REST pattern
- **Impl**: `impl/claude/agents/flux/` — FluxAgent implementation

---

*"The terrarium is not a cage. It is a window into life. The mirror shows without disturbing."*
