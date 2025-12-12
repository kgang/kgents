# Flux Functor: Discrete State → Continuous Flow

> *"The noun is a lie. There is only the rate of change."*
> — kgents ontology

> *"Static: Agent: A → B. Dynamic: Flux(Agent): dA/dt → dB/dt"*

---

## Overview

The Flux Functor lifts agents from the domain of **Discrete State** to the domain of **Continuous Flow**. It transforms an agent that maps `A → B` into a process that maps `Flux[A] → Flux[B]`.

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where:
  Flux[T] = AsyncIterator[T]  # Asynchronous stream
```

This is NOT a "loop agent" or timer-driven polling mechanism. It is a **functor** that lifts agents into the streaming domain while preserving functor laws.

---

## Philosophy: The Flux Insight

### The Polling Fallacy

The naive approach models continuous agents as "loops with timers":

```python
# BAD: Imperative thinking in functional clothing
while True:
    perception = poll_source()
    result = agent.invoke(perception)
    await asyncio.sleep(interval)  # Zombie twitching on a clock
```

This creates "zombie agents" — entities that twitch on timers rather than respond to reality.

### The Truth

**Life is event-driven, not clock-driven.**

The Flux functor doesn't wrap an agent in a loop — it lifts the agent from the domain of discrete transformations to the domain of continuous flow.

```
Static:  Agent[A, B]        — A morphism from A to B (point transformation)
Dynamic: Flux(Agent)[A, B]  — A morphism from Flux[A] to Flux[B] (continuous flow)
```

---

## The Signature

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where:
  Agent[A, B]  = Morphism from A to B (discrete)
  Flux[A]      = AsyncIterator[A] (continuous stream)
```

### Why This Signature Matters

This solves **The Sink Problem**: Where does output go?

| Mode | Output Destination |
|------|-------------------|
| Function Mode | Returned to caller |
| Flux Mode | Emitted as continuous stream |

**Living Pipelines become possible**:
```python
pipeline = flux_a | flux_b | flux_c
async for result in pipeline.start(source):
    # Results flow continuously through entire pipeline
    ...
```

---

## Functor Laws

Flux preserves the category-theoretic structure:

```python
# Identity Preservation
Flux(Id) ≅ Id_Flux  # Identity agent maps Flux[A] → Flux[A]

# Composition Preservation
Flux(f >> g) ≅ Flux(f) >> Flux(g)

# Because streams compose:
# Flux[A] → Flux[B] → Flux[C]
```

### Proof Sketch

- **Identity**: `Flux(Id).start(source)` yields each element unchanged, which is `Id_Flux`
- **Composition**: Processing `source` through `Flux(f >> g)` is equivalent to processing through `Flux(f)` then `Flux(g)` because the inner composition `f >> g` applies at each element

---

## FluxAgent Protocol

### Core Structure

```python
class FluxState(Enum):
    """Flux lifecycle states."""
    DORMANT = "dormant"       # Created but not started
    FLOWING = "flowing"       # Processing stream
    PERTURBED = "perturbed"   # Handling external invoke
    DRAINING = "draining"     # Source exhausted, flushing output
    STOPPED = "stopped"       # Explicitly stopped
    COLLAPSED = "collapsed"   # Entropy exhausted → Ground

@dataclass
class FluxAgent(Generic[A, B]):
    """
    An agent lifted into the streaming domain.

    The Heterarchical Principle realized:
    - DORMANT: Can invoke() directly (discrete mode)
    - FLOWING: Processes stream, yields results (continuous mode)
    - invoke() on FLOWING = Perturbation (injected into stream)

    Categorical view:
    - Agent: A → B (discrete morphism)
    - FluxAgent: Flux[A] → Flux[B] (stream morphism)
    """

    inner: Agent[A, B]
    config: FluxConfig
```

### The Critical Method: start() Returns a Stream

```python
async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
    """
    Start the flux and return the output stream.

    This is the key insight: start() doesn't return None.
    It returns Flux[B], enabling Living Pipelines.

    Args:
        source: Input stream (Flux[A])

    Returns:
        Output stream (Flux[B])

    Example:
        >>> async for result in flux_agent.start(events):
        ...     process(result)

        # Or pipe to another flux:
        >>> pipeline = flux_a.start(source) | flux_b
    """
```

**Key Insight**: The signature `start(source) → AsyncIterator[B]` (not `start(source) → None`) is what enables composition and solves the Sink Problem.

---

## The Perturbation Principle

### The Problem: Bypass Causes Schizophrenia

The naive approach: "If agent is running, bypass the flux and invoke directly."

```python
# BAD: Causes state schizophrenia
async def invoke(self, input):
    return await self.inner.invoke(input)  # Bypasses flux state!
```

**The Problem**: If the agent has Symbiont memory, bypassing the flux means:
- State loaded twice (once by flux, once by invoke)
- Race conditions on state updates
- Inconsistent memory ("schizophrenia")

### The Solution: Perturbation

**invoke() on a running flux = inject event with priority**

```python
async def invoke(self, input_data: A) -> B:
    """
    If DORMANT: Direct invocation (discrete mode).
    If FLOWING: Inject input as high-priority perturbation.
               Wait for specific result from output stream.

    This preserves State Integrity:
    - If agent has Symbiont memory, perturbation goes through
      the same state-loading path as normal flux events
    - No race conditions, no schizophrenia

    Args:
        input_data: The perturbation event

    Returns:
        The result of processing this specific input
    """
    if self._state == FluxState.DORMANT:
        # Direct invocation (unchanged from original)
        return await self.inner.invoke(input_data)

    if self._state == FluxState.FLOWING:
        # Perturbation: inject into stream with callback
        future = asyncio.Future()
        await self._perturbation_queue.put(
            Perturbation(data=input_data, result_future=future)
        )
        return await future  # Wait for flux to process it
```

**Why This Works**:
- Perturbation goes through the same processing path
- State integrity preserved (Symbiont compatible)
- Result returned to caller (feels like normal invoke)
- No race conditions

---

## The Ouroboros: Self-Feeding Flux

### True Autonomy Requires Recurrence

A flux that only consumes external input isn't truly autonomous — it's reactive. True autonomy means **output affects future input**.

```python
config = FluxConfig(
    feedback_fraction=0.3,     # 30% of outputs feed back
    feedback_transform=lambda result: result.as_context(),
)
```

### The Feedback Loop

```
                    ┌─────────────────────────────────────┐
                    │                                     │
    Input ────────→ │ ─────→ Agent ─────→ Output ────────│──→ Emit
    Stream          │   ↑                    │           │
                    │   │                    │           │
                    │   └────── Feedback ────┘           │
                    │          (fraction)                │
                    └─────────────────────────────────────┘
```

### Feedback Fraction Guide

| Fraction | Behavior | Use Case |
|----------|----------|----------|
| 0.0 | Pure reactive (no feedback) | Simple stream processing |
| 0.1-0.3 | Light context accumulation | Conversational memory |
| 0.5 | Equal external/internal | Dialectician archetype |
| 1.0 | Full ouroboros (mostly self-talk) | Solipsism risk! |

**Anti-Pattern**: `feedback_fraction=1.0` creates a closed system that only talks to itself.

---

## FluxConfig

```python
@dataclass
class FluxConfig:
    """Configuration for flux behavior."""

    # Entropy (J-gent physics)
    entropy_budget: float = 1.0        # Initial budget
    entropy_decay: float = 0.01        # Per-event decay
    max_events: int | None = None      # Hard cap (None = unlimited)

    # Backpressure
    buffer_size: int = 100             # Output buffer size
    drop_policy: str = "block"         # "block" | "drop_oldest" | "drop_newest"

    # Feedback (Ouroboros)
    feedback_fraction: float = 0.0     # 0.0 = no feedback, 1.0 = full ouroboros
    feedback_transform: Callable[[B], A] | None = None  # B → A adapter

    # Observability
    emit_pheromones: bool = True
    trace_enabled: bool = True
    agent_id: str | None = None
```

### Backpressure Policies

When downstream consumers can't keep up, pressure builds:

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `block` | Producer waits | Preserve all events, may stall |
| `drop_oldest` | Discard stale events | Real-time priority |
| `drop_newest` | Discard fresh events | Historical priority |

---

## Living Pipelines

### The Pipe Operator

Flux agents compose via `|` (pipe), creating Living Pipelines:

```python
# Static composition (discrete)
static_pipeline = agent_a >> agent_b >> agent_c
result = await static_pipeline.invoke(input)

# Living composition (continuous)
living_pipeline = flux_a | flux_b | flux_c

async for result in living_pipeline.start(source):
    # Results flow continuously through entire pipeline
    ...
```

### Pipeline Implementation

```python
@dataclass
class FluxPipeline(Generic[A, B]):
    """A chain of FluxAgents forming a living pipeline."""

    stages: list[FluxAgent]

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
        """Start all stages, chaining their streams."""
        current_stream = source

        for stage in self.stages:
            current_stream = await stage.start(current_stream)

        async for result in current_stream:
            yield result

    def __or__(self, other: FluxAgent) -> "FluxPipeline":
        """Extend pipeline with another stage."""
        return FluxPipeline(self.stages + [other])
```

---

## Flux Topology: Physics of Flow

### The Fluid Dynamics View

Agents are not architecture — they are **topological knots in a stream of events**.

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

This allows modeling agents using **fluid dynamics**:

| Metric | Meaning | Calculation |
|--------|---------|-------------|
| **Pressure** | Queue depth (backlog) | `len(input_queue) + len(output_queue)` |
| **Flow** | Throughput | `events_processed / elapsed_time` |
| **Turbulence** | Error rate | `errors / events_processed` |
| **Temperature** | Token metabolism | Integrated from void/entropy |

---

## Sources: Event-Driven, Not Timer-Driven

### The Anti-Pattern

```python
# BAD: Timer-driven zombie
async def heartbeat(interval):
    while True:
        yield time.time()
        await asyncio.sleep(interval)  # Polling!
```

### The Pattern

```python
# GOOD: Event-driven life
async def from_events(event_bus: EventBus) -> AsyncIterator[Event]:
    """Yield events as they occur, not on a timer."""
    async for event in event_bus.subscribe():
        yield event

# Heartbeat is a SPECIFIC source, not the default mechanic
async def periodic(interval: float) -> AsyncIterator[float]:
    """Periodic events (when you actually need a timer)."""
    while True:
        yield time.time()
        await asyncio.sleep(interval)
```

### Source Types

| Source | Nature | Use Case |
|--------|--------|----------|
| `from_events(bus)` | Reactive | Event-driven systems |
| `from_stream(async_iter)` | Reactive | Any async iterator |
| `from_pheromones(field)` | Reactive | Multi-agent sensing |
| `periodic(interval)` | Active | Scheduled tasks (use sparingly) |
| `from_kairos(ctrl, src)` | Filtered | Timing-aware |

---

## Relationship to Existing Patterns

### Flux vs Symbiont

| Pattern | Threads | Domain |
|---------|---------|--------|
| **Symbiont** | State (S) | Space (memory across invocations) |
| **Flux** | Time (Δt) | Time (continuous execution) |

**Composition**: A FluxSymbiont has both:

```python
# Symbiont: threads state
stateful_agent = Symbiont(logic, memory)

# Flux: threads time
living_agent = Flux.lift(stateful_agent)

# Result: Continuous execution with persistent memory
```

### Flux vs Fix

| Pattern | Termination |
|---------|-------------|
| **Fix** | When f(x) = x (convergence) |
| **Flux** | When source exhausts OR entropy depletes |

**Relationship**: Flux is Fix applied to streams:

```python
Flux(agent) ≅ Fix(
    transform=lambda stream: map_async(agent.invoke, stream),
    equality_check=lambda s1, s2: s1.exhausted and s2.exhausted
)
```

### Why Flux Is Not a Bootstrap Agent

**Question**: Should Flux be added to the bootstrap?

| Criterion | Flux | Assessment |
|-----------|------|------------|
| **Irreducible?** | Derivable from Fix | Flux ≅ Fix applied to streams |
| **Required for regeneration?** | No | Can regenerate without Flux |
| **Categorical necessity?** | No | Composition works without Flux |

**Conclusion**: Flux is a **derived functor**. However, Flux is **foundational infrastructure** for living agents. Without it, all agents are corpses that only move when poked.

---

## Anti-Patterns

### 1. Timer-Driven Zombies (Polling Fallacy)

```python
# BAD: Default to polling
async def start(self):
    while True:
        await asyncio.sleep(1.0)
        # twitch

# GOOD: Default to awaiting events
async def start(self, source):
    async for event in source:
        # respond
```

### 2. Void Output (The Sink Problem)

```python
# BAD: Output disappears
async def start(self, source) -> None:
    async for event in source:
        result = await self.inner.invoke(event)
        # result goes... where?

# GOOD: Output flows
async def start(self, source) -> AsyncIterator[B]:
    async for event in source:
        result = await self.inner.invoke(event)
        yield result  # Output stream continues
```

### 3. Bypass Invocation (Schizophrenia Risk)

```python
# BAD: Bypass running flux
async def invoke(self, input):
    if self._running:
        return await self.inner.invoke(input)  # Bypasses flux!

# GOOD: Perturbation
async def invoke(self, input):
    if self._running:
        return await self._perturb(input)  # Goes through flux
```

### 4. Closed Ouroboros (Solipsism)

```python
# BAD: Full feedback with no external input
config = FluxConfig(feedback_fraction=1.0)
# Agent talks only to itself — solipsism!

# GOOD: Balanced feedback
config = FluxConfig(feedback_fraction=0.3)
# 70% external, 30% self-context
```

---

## Principle Assessment

| Principle | Assessment |
|-----------|------------|
| **Tasteful** | Single functor, clear purpose (lift to flux domain) |
| **Curated** | Not a God construct — just stream lifting |
| **Ethical** | Entropy bounds prevent runaway; perturbation preserves integrity |
| **Joy-Inducing** | Living pipelines feel alive |
| **Composable** | `|` operator, functor laws preserved |
| **Heterarchical** | Both invoke() and start() coexist via perturbation |
| **Generative** | Archetypes derive from Flux configuration |

### Is This a God Construct?

**No.** Flux does ONE thing: lift discrete agents to stream domain.

It doesn't:
- Manage memory (Symbiont does)
- Judge outputs (Judge does)
- Handle errors specially (Ground does)
- Create new agents (Spawner archetype does)

It ONLY transforms `Agent[A,B] → Agent[Flux[A], Flux[B]]`.

---

## Implementation Location

`impl/claude/agents/flux/`

```
impl/claude/agents/flux/
├── __init__.py
├── functor.py          # Flux.lift() / Flux.unlift()
├── agent.py            # FluxAgent
├── config.py           # FluxConfig
├── state.py            # FluxState
├── errors.py           # FluxError
├── perturbation.py     # Perturbation handling
├── feedback.py         # Ouroboric feedback
├── pipeline.py         # FluxPipeline
├── sources/
│   ├── events.py
│   ├── pheromones.py
│   ├── periodic.py
│   └── merged.py
└── _tests/
```

---

## See Also

- [functor-catalog.md](functor-catalog.md) §13 — Flux in catalog
- [functors.md](functors.md) — Functor theory
- [../principles.md](../principles.md) §6 — Heterarchical Principle
- [../bootstrap.md](../bootstrap.md) — Fix as foundation
- [../d-gents/symbiont.md](../d-gents/symbiont.md) — Symbiont comparison
- [../archetypes.md](../archetypes.md) — Flux instantiations

---

*"The noun is a lie. There is only the rate of change."*
*"Static: A → B. Dynamic: dA/dt → dB/dt."*
