# Stigmergy: The Chalkboard Architecture

> Agents communicate by modifying and observing a shared environment, not by direct invocation.

**⚠️ TRANSFORMATIVE**: This proposal **dirties the purity of agents definitionally**. Agents become "tainted" by their environmental entanglement. This is intentional.

---

## The Theory

Termites build cathedrals without architects. They drop pheromones on dirt balls; other termites smell the pheromones and add more dirt. The architecture emerges from the *environment*, not from inter-agent communication.

**Traditional Agent Coupling**:
```
Agent A ──calls──> Agent B ──calls──> Agent C
```

**Stigmergic Coordination**:
```
Agent A ──emits──> Environment <──observes── Agent B
                       ↑
                       └──────── Agent C observes
```

---

## The W-gent as Pheromone Field

W-gent transforms from "observation tool" to "coordination infrastructure." It pushes state changes via **WebSocket/SSE**, not polling.

### Pheromone Data Model

```python
@dataclass(frozen=True)
class Pheromone:
    """A signal in the environment."""
    type: str               # "error", "completion", "request", "claim"
    selector: str           # CSS-like selector for targeting
    payload: dict           # Signal-specific data
    timestamp: datetime
    source: str | None      # Originating agent (if known)
    ttl: int | None         # Time-to-live in seconds (None = permanent)

    def matches(self, pattern: str) -> bool:
        """Check if this pheromone matches a subscription pattern."""
        # Support wildcards: "error.*", "*.completion", "*"
        ...

@dataclass
class ClaimedPheromone(Pheromone):
    """A pheromone that has been claimed by an agent."""
    claimed_by: str
    claimed_at: datetime
```

### Stigmergic Agent Protocol

```python
class StigmergicAgent(Agent[None, None]):
    """
    Agent that responds to environmental signals (pheromones).

    Definitionally tainted: this agent's behavior depends on
    indefinite environmental dimensions.
    """
    pheromone_subscriptions: list[str]  # Selectors to watch
    w_gent_url: str = "ws://localhost:8000/pheromones"

    # Flag: This agent is environmentally entangled
    __stigmergic__ = True

    async def listen_loop(self):
        """
        Subscribe to W-gent pheromone stream (push, not poll).

        WebSocket/SSE eliminates polling latency and reduces
        resource usage vs. N agents polling.
        """
        async with websocket_connect(self.w_gent_url) as ws:
            # Subscribe to relevant pheromones
            await ws.send(json.dumps({
                "subscribe": self.pheromone_subscriptions
            }))

            # React to pushed pheromones
            async for message in ws:
                pheromone = Pheromone(**json.loads(message))
                await self.respond_to_pheromone(pheromone)

    async def respond_to_pheromone(self, pheromone: Pheromone):
        """React to environmental signal."""
        ...

    async def emit_pheromone(self, pheromone: Pheromone):
        """Deposit a pheromone into the environment."""
        await self.w_gent.broadcast(pheromone)

    async def claim_pheromone(self, pheromone: Pheromone) -> bool:
        """
        Atomic claim—first responder wins.

        Returns True if this agent successfully claimed the pheromone.
        """
        return await self.w_gent.atomic_claim(pheromone, self.agent_id)
```

---

## The Taint Model

Stigmergic agents are **definitionally impure**. We acknowledge this explicitly:

| Property | Pure Agent | Stigmergic Agent |
|----------|------------|------------------|
| Determinism | Same input → same output | Output depends on environment |
| Isolation | No external dependencies | Entangled with W-gent |
| Testability | Unit testable | Requires environment mock |
| Composability | `>>` is straightforward | `>>` must account for environment |

**This is fine.** The real world is entangled. Agents that pretend otherwise are lying.

For any "turn" an agent has, it could be affected by indefinite dimensions—this is the nature of reality, and stigmergic agents embrace it.

---

## The W-gent Server

```python
class WGentPheromoneServer:
    """
    W-gent as coordination infrastructure.

    Manages pheromone subscriptions and broadcasts.
    """
    subscriptions: dict[str, set[WebSocket]]  # selector → subscribers
    active_pheromones: dict[str, Pheromone]   # id → pheromone
    claimed: dict[str, str]                    # pheromone_id → agent_id

    async def handle_connection(self, ws: WebSocket):
        """Handle a new agent connection."""
        await ws.accept()

        async for message in ws.iter_json():
            if "subscribe" in message:
                for selector in message["subscribe"]:
                    self.subscriptions.setdefault(selector, set()).add(ws)

            elif "emit" in message:
                pheromone = Pheromone(**message["emit"])
                await self.broadcast(pheromone)

            elif "claim" in message:
                success = await self.atomic_claim(
                    message["pheromone_id"],
                    message["agent_id"]
                )
                await ws.send_json({"claimed": success})

    async def broadcast(self, pheromone: Pheromone):
        """Push pheromone to all matching subscribers."""
        self.active_pheromones[pheromone.id] = pheromone

        for selector, sockets in self.subscriptions.items():
            if pheromone.matches(selector):
                for ws in sockets:
                    try:
                        await ws.send_json(pheromone.to_dict())
                    except WebSocketDisconnect:
                        sockets.discard(ws)

    async def atomic_claim(self, pheromone_id: str, agent_id: str) -> bool:
        """
        Atomic claim—first responder wins.

        Thread-safe via asyncio lock or Redis SETNX.
        """
        async with self.claim_lock:
            if pheromone_id in self.claimed:
                return False
            self.claimed[pheromone_id] = agent_id
            return True

    def render_pheromone_map(self) -> str:
        """
        Render current pheromone state as visualization.

        This becomes the I-gent "pheromone map" view.
        """
        ...
```

---

## Pheromone Types

Common pheromone categories:

| Type | Purpose | Example Payload |
|------|---------|-----------------|
| `request.*` | Work to be done | `{"task": "review code", "file": "main.py"}` |
| `completion.*` | Work completed | `{"task_id": "123", "result": {...}}` |
| `error.*` | Failure signal | `{"error": "timeout", "context": {...}}` |
| `claim.*` | Resource claim | `{"resource": "gpu-0", "duration": 300}` |
| `heartbeat.*` | Agent liveness | `{"agent_id": "reviewer", "status": "idle"}` |
| `discovery.*` | Capability announcement | `{"agent_id": "new", "capabilities": [...]}` |

---

## Integration with I-gents

I-gent Garden view becomes the "pheromone map"—you can see:
- Active pheromones in the environment (glowing dots)
- Which agents are subscribed to which selectors (connection lines)
- Pheromone flow over time (animated trails)
- Claimed vs unclaimed work (color coding)

```
┌─ Pheromone Map ───────────────────────────────────────────┐
│                                                            │
│    ○ ReviewerAgent        ○ LinterAgent                    │
│      └──[request.code]──────┘                              │
│            │                                               │
│            ▼                                               │
│    ┌─────────────────────────────┐                        │
│    │  🔵 request.code.review     │ ← active pheromone     │
│    │     file: main.py           │                        │
│    │     emitted: 2s ago         │                        │
│    │     claimed: ReviewerAgent  │                        │
│    └─────────────────────────────┘                        │
│                                                            │
│    ○ TestAgent ──[completion.*]─────────────────────────  │
│                                                            │
│    Environment: 3 active | 12 claimed | 5 expired          │
└────────────────────────────────────────────────────────────┘
```

---

## Decoupling Benefits

- **Add agents dynamically**: Add 50 "Janitor" agents without existing agents knowing
- **Remove agents safely**: Unsubscribe and disconnect; work redistributes
- **Natural load balancing**: First responder claims pheromone
- **Environment as truth**: No hidden state in agent-to-agent calls
- **Push eliminates polling**: Real-time response to environment changes
- **Audit trail**: All pheromones are logged

---

## Race Condition Handling

Multiple agents may try to claim the same pheromone:

```python
# Agent 1 and Agent 2 both see the same request
pheromone = Pheromone(type="request.code.review", ...)

# Race to claim
agent_1_claimed = await agent_1.claim_pheromone(pheromone)  # True
agent_2_claimed = await agent_2.claim_pheromone(pheromone)  # False

# Agent 2 knows to back off
if not agent_2_claimed:
    # Either wait for new work or help Agent 1
    pass
```

---

## Anti-Patterns

- **Tight coupling**: Agent A must know Agent B exists
- **Orchestrator bottleneck**: All communication through one coordinator
- **Hidden state**: Agents hold state that environment can't observe
- **Pretending stigmergic agents are pure**: Acknowledge the taint
- **Polling instead of push**: Use WebSocket/SSE, not HTTP polling
- **Ignoring TTL**: Stale pheromones should expire

---

## When to Use Stigmergy

**Good fit**:
- Multi-agent coordination without central orchestrator
- Dynamic agent pools (agents join/leave)
- Work distribution with natural load balancing
- Observable system behavior (debugging/visualization)

**Poor fit**:
- Single-agent pipelines (unnecessary overhead)
- Strict ordering requirements (pheromones are unordered)
- Latency-critical paths (WebSocket adds ~1ms)

---

*Zen Principle: The termite knows nothing of the cathedral; the cathedral knows nothing of the termite. Together they build.*

---

## See Also

- [w-gents/README.md](README.md) - W-gent overview
- [w-gents/wire-protocol.md](wire-protocol.md) - Wire protocol details
- [i-gents/README.md](../i-gents/README.md) - Visualization integration
- [anatomy.md](../anatomy.md) - Observable protocol
