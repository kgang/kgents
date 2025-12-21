# Flux: Discrete to Continuous

> *"The noun is a lie. There is only the rate of change."*

---

## The Insight

Agents are corpses. They only move when poked.

```python
result = await agent.invoke(input)  # Discrete: twitch, return, die
```

**Flux** lifts agents from discrete transformations to continuous flow:

```python
async for result in flux_agent.start(source):  # Continuous: live, respond, flow
    ...
```

---

## The Signature

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T]
```

**Static**: `Agent: A → B` — a point transformation
**Dynamic**: `Flux(Agent): dA/dt → dB/dt` — a continuous flow

---

## The Three Problems Solved

### 1. The Sink Problem

Where does output go?

```python
# BAD: Output vanishes
async def start(self, source) -> None:
    async for event in source:
        result = await self.invoke(event)  # result goes... where?

# GOOD: Output flows
async def start(self, source) -> AsyncIterator[B]:
    async for event in source:
        yield await self.invoke(event)  # Living Pipeline enabled
```

### 2. The Polling Fallacy

Life is event-driven, not clock-driven.

```python
# BAD: Zombie on a timer
while True:
    await asyncio.sleep(1.0)  # twitch

# GOOD: Respond to events
async for event in source:
    yield await self.invoke(event)  # live
```

### 3. The Bypass Problem

`invoke()` on a running agent must not bypass the stream.

```python
# BAD: Schizophrenia (state loaded twice, race conditions)
async def invoke(self, x):
    if self._flowing:
        return await self.inner.invoke(x)  # Bypasses stream state!

# GOOD: Perturbation (injected into stream, state integrity preserved)
async def invoke(self, x):
    if self._flowing:
        future = asyncio.Future()
        await self._perturbation_queue.put((x, future))
        return await future  # Goes through stream
```

---

## Functor Laws

```python
# Identity Preservation
Flux(Id) ≅ Id_Flux

# Composition Preservation
Flux(f >> g) ≅ Flux(f) >> Flux(g)
```

---

## States

```
DORMANT   → Created, not started (invoke works directly)
FLOWING   → Processing stream (invoke = perturbation)
DRAINING  → Source exhausted, flushing output
STOPPED   → Explicitly stopped
COLLAPSED → Entropy depleted → Ground
```

---

## Configuration

```python
@dataclass
class FluxConfig:
    # Entropy (from void.*)
    entropy_budget: float = 1.0
    entropy_decay: float = 0.01
    max_events: int | None = None

    # Backpressure
    buffer_size: int = 100
    drop_policy: Literal["block", "drop_oldest", "drop_newest"] = "block"

    # Ouroboros
    feedback_fraction: float = 0.0  # 0.0 = reactive, 1.0 = solipsism
    feedback_transform: Callable[[B], A] | None = None
```

---

## Living Pipelines

```python
pipeline = flux_a | flux_b | flux_c

async for result in pipeline.start(source):
    ...
```

The `|` operator chains flux agents. Output of `flux_a` flows to `flux_b`.

---

## The Perturbation Principle

When `invoke()` is called on a FLOWING flux:

1. Input is wrapped with a Future
2. Input is queued with priority
3. Stream processor handles it in order
4. Result is returned via Future

**State Integrity**: If agent has Symbiont memory, perturbation flows through the same state-loading path. No race conditions.

---

## The Ouroboros

```python
config = FluxConfig(
    feedback_fraction=0.3,  # 30% of outputs feed back to input
    feedback_transform=lambda b: b.as_context(),
)
```

| Fraction | Behavior |
|----------|----------|
| 0.0 | Pure reactive |
| 0.3 | Light context |
| 0.5 | Equal internal/external |
| 1.0 | Full ouroboros (solipsism risk) |

---

## Flux Topology

Agents are topological knots in event streams:

| Metric | Meaning |
|--------|---------|
| **Pressure** | Queue depth |
| **Flow** | events/second |
| **Turbulence** | errors/events |
| **Temperature** | Token metabolism |

---

## Relationship to Bootstrap

**Flux is derived from Fix**, not irreducible:

```python
Flux(agent) ≅ Fix(
    transform=lambda stream: map_async(agent.invoke, stream),
    equality_check=lambda s1, s2: s1.exhausted and s2.exhausted
)
```

Flux belongs in `functor-catalog.md`, not `bootstrap.md`.

---

## Relationship to Symbiont

| Pattern | Threads | Domain |
|---------|---------|--------|
| **Symbiont** | State (S) | Space |
| **Flux** | Time (Δt) | Time |

**FluxSymbiont**: A Symbiont lifted to Flux has both persistent memory and continuous execution.

---

## Archetypes as Flux

| Archetype | Flux Configuration |
|-----------|-------------------|
| Consolidator | `source=idle_signal` |
| Spawner | Flux emitting child FluxAgents |
| Witness | `Flux(Id)` with trace |
| Dialectician | `feedback_fraction=0.5` |

See `spec/archetypes.md` for full mapping.

---

## Anti-Patterns

1. **Timer zombies**: `asyncio.sleep()` as default mechanic
2. **Void output**: `start() → None`
3. **Bypass invocation**: Calling inner directly when flowing
4. **Closed ouroboros**: `feedback_fraction=1.0` with no external input

---

## Implementation

```
impl/claude/agents/flux/
├── functor.py      # Flux.lift(), Flux.unlift()
├── agent.py        # FluxAgent
├── config.py       # FluxConfig
├── state.py        # FluxState
├── pipeline.py     # FluxPipeline, | operator
├── perturbation.py # Perturbation handling
├── metabolism.py   # Entropy integration
└── sources/        # Event sources
```

**Status**: Implemented (261 tests)

---

## FluxConfig

```python
@dataclass
class FluxConfig:
    # Entropy (J-gent physics)
    entropy_budget: float = 1.0
    entropy_decay: float = 0.01
    max_events: int | None = None

    # Backpressure
    buffer_size: int = 100
    drop_policy: str = "block"  # "block" | "drop_oldest" | "drop_newest"

    # Feedback (Ouroboros)
    feedback_fraction: float = 0.0
    feedback_transform: Callable[[B], A] | None = None

    # Observability
    emit_pheromones: bool = True
    trace_enabled: bool = True
    agent_id: str | None = None
```

### Backpressure Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `block` | Producer waits | Preserve all events |
| `drop_oldest` | Discard stale events | Real-time priority |
| `drop_newest` | Discard fresh events | Historical priority |

---

## Event Sources

```python
# GOOD: Event-driven
async def from_events(bus: EventBus) -> AsyncIterator[Event]:
    async for event in bus.subscribe():
        yield event

# Sparingly: Timer-driven
async def periodic(interval: float) -> AsyncIterator[float]:
    while True:
        yield time.time()
        await asyncio.sleep(interval)
```

| Source | Nature | Use Case |
|--------|--------|----------|
| `from_events(bus)` | Reactive | Event-driven systems |
| `from_pheromones(field)` | Reactive | Multi-agent sensing |
| `periodic(interval)` | Active | Scheduled tasks (use sparingly) |

---

## See Also

- [functor-catalog.md](functor-catalog.md) §13 — Flux in functor catalog
- [composition.md](composition.md) — Sequential composition foundation
- `spec/principles.md` §6 — Heterarchical Principle, Flux Topology
- `spec/archetypes.md` — Archetypes as Flux configurations

---

*"Static: A → B. Dynamic: dA/dt → dB/dt."*
