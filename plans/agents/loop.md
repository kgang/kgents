---
path: agents/loop
status: complete
progress: 100
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [void/entropy, self/interface]
session_notes: |
  IMPLEMENTED 2025-12-12. 261 tests, all passing.
  Location: impl/claude/agents/flux/
  Key features:
  - Signature: Agent[A,B] → Agent[Flux[A], Flux[B]]
  - start() returns AsyncIterator[B] (Living Pipelines)
  - invoke() on running loop = Perturbation (not bypass)
  - Ouroboric feedback configuration
  - Event-driven (no polling in core)
  - Living Pipelines via | operator
---

# Flux: The Agentic Stream Transformer

> *"The noun is a lie. There is only the rate of change."*
> — kgents ontology

> *"Static: Agent: A → B. Dynamic: Flux(Agent): dA/dt → dB/dt"*

**AGENTESE Context**: `self.flux.*`
**Status**: Planned
**Principles**: Heterarchical, Composable, Generative
**Location**: `impl/claude/agents/flux/`

---

## The Paradigm Shift: From Loop to Flux

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

### The Flux Insight

**Life is event-driven, not clock-driven.**

The Flux functor doesn't wrap an agent in a loop — it lifts the agent from the domain of **Discrete State** to the domain of **Continuous Flow**.

```
Static:  Agent[A, B]        — A morphism from A to B
Dynamic: Flux(Agent)[A, B]  — A morphism from Flux[A] to Flux[B]
```

Where `Flux[T]` is an asynchronous stream of values of type T.

---

## The Problem: Agents Without Life

The kgents codebase has 8,076+ tests, 22+ agent implementations, and rich infrastructure. But every agent is a **corpse** — it only moves when poked.

| Have | Don't Have |
|------|-----------|
| `agent.invoke(input) → output` | `agent.process(stream) → stream` |
| Discrete transformations | Continuous transformations |
| Corpses (await invocation) | Life (respond to flux) |

### The Vision

```python
# Static (what we have)
result = await agent.invoke(input)

# Dynamic (what we need)
output_stream = flux_agent.start(input_stream)
async for result in output_stream:
    # Living pipeline — results flow continuously
```

---

## The Flux Functor

### Category-Theoretic Foundation

Flux is a functor that lifts agents into the streaming domain:

```
Flux: 𝒞_Agent[A, B] → 𝒞_Agent[Flux[A], Flux[B]]

Where:
  Agent[A, B]           = Morphism from A to B (discrete)
  Flux[A]               = AsyncIterator[A] (continuous stream)
  FluxAgent[A, B]       = Morphism from Flux[A] to Flux[B]
```

### The Signature (Critical)

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]
```

This solves **The Sink Problem**: Where does output go?
- In Function Mode: Output is returned to caller
- In Flux Mode: Output is emitted as a continuous stream

**Living Pipelines become possible**:
```python
# Compose streams, not just agents
pipeline = flux_a.start(source) | flux_b | flux_c
async for final_result in pipeline:
    ...
```

### Functor Laws

```python
# Identity Preservation
Flux(Id) ≅ Id_Flux  # Identity agent maps Flux[A] → Flux[A]

# Composition Preservation
Flux(f >> g) ≅ Flux(f) >> Flux(g)

# Because streams compose:
# Flux[A] → Flux[B] → Flux[C]
```

---

## FluxAgent Specification

### Core Structure

```python
from dataclasses import dataclass, field
from typing import TypeVar, Generic, AsyncIterator, Callable, Any
from enum import Enum
import asyncio

A = TypeVar("A")  # Input flux type
B = TypeVar("B")  # Output flux type

class FluxState(Enum):
    """Flux lifecycle states."""
    DORMANT = "dormant"       # Created but not started
    FLOWING = "flowing"       # Processing stream
    PERTURBED = "perturbed"   # Handling external invoke
    DRAINING = "draining"     # Source exhausted, flushing output
    STOPPED = "stopped"       # Explicitly stopped
    COLLAPSED = "collapsed"   # Entropy exhausted → Ground

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
    config: FluxConfig = field(default_factory=FluxConfig)

    # Runtime state
    _state: FluxState = field(default=FluxState.DORMANT, init=False)
    _events_processed: int = field(default=0, init=False)
    _entropy_remaining: float = field(init=False)
    _perturbation_queue: asyncio.Queue[A] = field(init=False)
    _output_queue: asyncio.Queue[B] = field(init=False)
    _task: asyncio.Task | None = field(default=None, init=False)
    _id: str = field(init=False)

    def __post_init__(self):
        self._entropy_remaining = self.config.entropy_budget
        self._perturbation_queue = asyncio.Queue()
        self._output_queue = asyncio.Queue(maxsize=self.config.buffer_size)
        self._id = self.config.agent_id or f"flux-{uuid.uuid4().hex[:8]}"

    # ─────────────────────────────────────────────────────────────
    # The Critical Method: start() returns a stream
    # ─────────────────────────────────────────────────────────────

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
        if self._state not in (FluxState.DORMANT, FluxState.STOPPED):
            raise FluxError(f"Cannot start from state {self._state}")

        # Spawn the processing task
        self._task = asyncio.create_task(
            self._process_flux(source),
            name=f"flux-{self._id}"
        )

        # Return async generator that yields from output queue
        return self._output_generator()

    async def _output_generator(self) -> AsyncIterator[B]:
        """Yield results from output queue."""
        while True:
            if self._state in (FluxState.STOPPED, FluxState.COLLAPSED):
                # Drain remaining items
                while not self._output_queue.empty():
                    yield await self._output_queue.get()
                break

            try:
                result = await asyncio.wait_for(
                    self._output_queue.get(),
                    timeout=0.1
                )
                yield result
            except asyncio.TimeoutError:
                continue

    # ─────────────────────────────────────────────────────────────
    # The Perturbation Principle
    # ─────────────────────────────────────────────────────────────

    async def invoke(self, input_data: A) -> B:
        """
        Perturbation (The Heisenberg Interface).

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
            # Perturbation: inject into stream
            self._state = FluxState.PERTURBED

            # Create a future to receive this specific result
            result_future: asyncio.Future[B] = asyncio.Future()

            # Wrap input with result callback
            perturbation = _Perturbation(
                data=input_data,
                result_future=result_future,
            )
            await self._perturbation_queue.put(perturbation)

            # Wait for result
            try:
                return await result_future
            finally:
                if self._state == FluxState.PERTURBED:
                    self._state = FluxState.FLOWING

        raise FluxError(f"Cannot invoke from state {self._state}")

    # ─────────────────────────────────────────────────────────────
    # The Flux Processor
    # ─────────────────────────────────────────────────────────────

    async def _process_flux(self, source: AsyncIterator[A]) -> None:
        """Process input flux, emit output flux."""
        self._state = FluxState.FLOWING

        try:
            async for event in self._merged_source(source):
                # Check entropy
                if not self._can_continue():
                    self._collapse_to_ground()
                    break

                # Process event
                is_perturbation = isinstance(event, _Perturbation)
                input_data = event.data if is_perturbation else event

                try:
                    result = await self.inner.invoke(input_data)
                except Exception as e:
                    await self._emit_pheromone("error", str(e))
                    if is_perturbation:
                        event.result_future.set_exception(e)
                    continue

                # Emit result
                if is_perturbation:
                    event.result_future.set_result(result)
                else:
                    await self._emit_output(result)

                # Ouroboric feedback
                if self.config.feedback_fraction > 0:
                    await self._inject_feedback(result)

                # Consume entropy
                self._consume_entropy()
                self._events_processed += 1

            # Source exhausted
            self._state = FluxState.DRAINING

        finally:
            if self._state not in (FluxState.STOPPED, FluxState.COLLAPSED):
                self._state = FluxState.STOPPED
            await self._emit_pheromone("stopped", {
                "events_processed": self._events_processed,
                "final_state": self._state.value,
            })

    async def _merged_source(self, source: AsyncIterator[A]) -> AsyncIterator[A | _Perturbation]:
        """Merge source stream with perturbation queue (priority)."""
        source_done = False

        while not source_done or not self._perturbation_queue.empty():
            # Check perturbations first (priority)
            try:
                perturbation = self._perturbation_queue.get_nowait()
                yield perturbation
                continue
            except asyncio.QueueEmpty:
                pass

            # Get from source
            try:
                event = await asyncio.wait_for(
                    source.__anext__(),
                    timeout=0.1
                )
                yield event
            except asyncio.TimeoutError:
                continue
            except StopAsyncIteration:
                source_done = True

    async def _emit_output(self, result: B) -> None:
        """Emit result to output stream with backpressure."""
        if self.config.drop_policy == "block":
            await self._output_queue.put(result)
        elif self.config.drop_policy == "drop_oldest":
            if self._output_queue.full():
                try:
                    self._output_queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            await self._output_queue.put(result)
        else:  # drop_newest
            try:
                self._output_queue.put_nowait(result)
            except asyncio.QueueFull:
                pass

    # ─────────────────────────────────────────────────────────────
    # Ouroboric Feedback
    # ─────────────────────────────────────────────────────────────

    async def _inject_feedback(self, result: B) -> None:
        """
        The Ouroboros: Output feeds back to input.

        If feedback_fraction > 0, a portion of outputs are
        re-injected into the input stream, creating recurrence.

        This enables true autonomy: the agent's output affects
        its future perceptions.
        """
        import random

        if random.random() > self.config.feedback_fraction:
            return

        # Transform B → A if needed
        if self.config.feedback_transform:
            feedback_input = self.config.feedback_transform(result)
        elif isinstance(result, type(self.inner).__annotations__.get('A', object)):
            feedback_input = result  # B is compatible with A
        else:
            return  # Can't feedback incompatible types

        # Low-priority injection (not perturbation)
        # This goes to the normal source merge, not priority queue
        # Implementation: separate feedback queue merged at low priority

    # ─────────────────────────────────────────────────────────────
    # Entropy Management (unchanged philosophy, renamed)
    # ─────────────────────────────────────────────────────────────

    def _can_continue(self) -> bool:
        if self.config.max_events and self._events_processed >= self.config.max_events:
            return False
        return self._entropy_remaining > 0

    def _consume_entropy(self) -> None:
        self._entropy_remaining -= self.config.entropy_decay
        self._entropy_remaining = max(0.0, self._entropy_remaining)

    def _collapse_to_ground(self) -> None:
        self._state = FluxState.COLLAPSED

    # ─────────────────────────────────────────────────────────────
    # Composition: The Pipe Operator
    # ─────────────────────────────────────────────────────────────

    def __or__(self, other: "FluxAgent[B, Any]") -> "FluxPipeline[A, Any]":
        """
        Pipe operator for Living Pipelines.

        flux_a | flux_b | flux_c

        Creates a pipeline where output of flux_a flows to flux_b, etc.
        """
        return FluxPipeline([self, other])

    def __rshift__(self, other: Agent[B, Any]) -> "FluxAgent[A, Any]":
        """
        Compose with static agent: Flux(f) >> g

        The result is a FluxAgent with composed inner.
        """
        composed = ComposedAgent(self.inner, other)
        return FluxAgent(inner=composed, config=self.config)
```

---

## Flux Topology: The Physics of Flow

### The Fluid Dynamics View

Agents are not architecture — they are **topological knots in a stream of events**.

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

This allows us to model agents using **fluid dynamics**:

| Metric | Meaning | Calculation |
|--------|---------|-------------|
| **Pressure** | Queue depth | `len(input_queue) + len(output_queue)` |
| **Flow** | Throughput | `events_processed / elapsed_time` |
| **Turbulence** | Error rate | `errors / events_processed` |
| **Temperature** | Token metabolism | Integrated from void/entropy |

### Backpressure

When downstream consumers can't keep up, pressure builds:

```python
config = FluxConfig(
    buffer_size=100,           # Max buffered outputs
    drop_policy="block",       # "block" | "drop_oldest" | "drop_newest"
)
```

- **block**: Producer waits (preserves all events, may stall)
- **drop_oldest**: Discard stale events (real-time priority)
- **drop_newest**: Discard fresh events (historical priority)

---

## Living Pipelines

### The Pipe Operator

Flux agents compose via `|` (pipe), creating Living Pipelines:

```python
# Static composition (what we had)
static_pipeline = agent_a >> agent_b >> agent_c
result = await static_pipeline.invoke(input)

# Living composition (what we have now)
living_pipeline = flux_a | flux_b | flux_c

async for result in living_pipeline.start(source):
    # Results flow continuously through the entire pipeline
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

## The Perturbation Principle

### Why Not Just invoke()?

The naive approach: "If agent is running, bypass the loop and invoke directly."

```python
# BAD: Causes schizophrenia
async def invoke(self, input):
    return await self.inner.invoke(input)  # Bypasses loop state!
```

**The Problem**: If the agent has Symbiont memory, bypassing the loop means:
- State loaded twice (once by loop, once by invoke)
- Race conditions on state updates
- Inconsistent memory ("schizophrenia")

### The Perturbation Solution

**invoke() on a running flux = inject event with priority**

```python
async def invoke(self, input: A) -> B:
    if self._state == FluxState.FLOWING:
        # Don't bypass — perturb!
        future = asyncio.Future()
        await self._perturbation_queue.put(
            _Perturbation(data=input, result_future=future)
        )
        return await future  # Wait for loop to process it
```

**Why This Works**:
- Perturbation goes through the same processing path
- State integrity preserved (Symbiont compatible)
- Result returned to caller (feels like invoke)
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

### How It Works

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

### Use Cases

| Fraction | Behavior |
|----------|----------|
| 0.0 | Pure reactive (no feedback) |
| 0.1-0.3 | Light context accumulation |
| 0.5 | Equal external/internal influence |
| 1.0 | Full ouroboros (mostly self-talk) |

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

### Archetypes as Flux Configurations

| Archetype | Flux Configuration |
|-----------|-------------------|
| **Consolidator** | Flux with idle_signal source (await, don't poll) |
| **Spawner** | Flux that emits child FluxAgents |
| **Witness** | Flux(Id) with trace side effects |
| **Questioner** | Flux with Type IV Critic inner |
| **Uncertain** | Flux maintaining N parallel streams |
| **Dialectician** | Flux(Contradict >> Sublate) with feedback_fraction=0.5 |

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
| `periodic(interval)` | Active | Scheduled tasks |
| `from_kairos(ctrl, src)` | Filtered | Timing-aware |

---

## Implementation Phases

### Phase 1: Core Flux Functor

**Files**:
```
impl/claude/agents/flux/
├── __init__.py
├── functor.py          # Flux.lift() / Flux.unlift()
├── agent.py            # FluxAgent
├── config.py           # FluxConfig
├── state.py            # FluxState
├── errors.py           # FluxError
├── pipeline.py         # FluxPipeline
└── _tests/
```

**Exit Criteria**:
```python
flux_agent = Flux.lift(my_agent)
results = flux_agent.start(source)
async for result in results:
    # Living pipeline works
    ...
```

### Phase 2: Perturbation & Ouroboros

**Files**:
```
impl/claude/agents/flux/
├── perturbation.py     # Perturbation handling
├── feedback.py         # Ouroboric feedback
└── _tests/
```

**Exit Criteria**:
```python
# Perturbation works
flux_agent.start(source)  # Running
result = await flux_agent.invoke(urgent_input)  # Perturbation, not bypass

# Feedback works
config = FluxConfig(feedback_fraction=0.5)
# Agent's outputs affect its inputs
```

### Phase 3: Sources & Pipeline

**Files**:
```
impl/claude/agents/flux/
├── sources/
│   ├── events.py
│   ├── pheromones.py
│   ├── periodic.py
│   └── merged.py
└── _tests/
```

**Exit Criteria**:
```python
# Living pipeline
pipeline = flux_a | flux_b | flux_c
async for result in pipeline.start(source):
    ...
```

### Phase 4: Observability & Metabolism

**Files**:
```
impl/claude/agents/flux/
├── observable.py
├── metabolism.py
└── _tests/
```

---

## Anti-Patterns

### 1. Timer-Driven Zombies

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

### 3. Bypass Invocation

```python
# BAD: Bypass running loop (schizophrenia risk)
async def invoke(self, input):
    if self._running:
        return await self.inner.invoke(input)  # Bypasses loop!

# GOOD: Perturbation
async def invoke(self, input):
    if self._running:
        return await self._perturb(input)  # Goes through loop
```

### 4. Closed Ouroboros

```python
# BAD: Full feedback with no external input
config = FluxConfig(feedback_fraction=1.0)
# Agent talks only to itself — solipsism!

# GOOD: Balanced feedback
config = FluxConfig(feedback_fraction=0.3)
# 70% external, 30% self-context
```

---

## Success Criteria

- [ ] `Flux.lift(agent)` returns FluxAgent
- [ ] `flux.start(source)` returns `AsyncIterator[B]`
- [ ] `flux.invoke(x)` on running flux = perturbation
- [ ] Pipeline composition via `|` works
- [ ] Ouroboric feedback configurable
- [ ] Entropy depletion collapses to Ground
- [ ] No `asyncio.sleep()` in core mechanics (event-driven)
- [ ] Tests: 100+
- [ ] Functor laws verified

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

## Cross-References

- **Spec**: `spec/principles.md` §6 (Heterarchical)
- **Spec**: `spec/c-gents/functor-catalog.md` (add Flux functor)
- **Spec**: `spec/bootstrap.md` (Fix as foundation)
- **Spec**: `spec/d-gents/symbiont.md` (Symbiont comparison)
- **Spec**: `spec/archetypes.md` (Flux instantiations)
- **Plan**: `plans/void/entropy.md` (Metabolism integration)
- **Impl**: `impl/claude/agents/flux/` (target location)

---

*"The noun is a lie. There is only the rate of change."*
*"Static: A → B. Dynamic: dA/dt → dB/dt."*
