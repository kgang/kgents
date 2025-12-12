# Prompt: Implement Flux Functor

**Purpose**: Implement the Flux Functor as specified in `plans/agents/loop.md` and `spec/agents/flux.md`
**Scope**: Implementation in `impl/claude/agents/flux/`
**Estimated Tests**: 100+
**Estimated LOC**: ~1500

**Key Paradigm**: Event-driven streams, NOT timer-driven loops

---

## Context

You are implementing the **Flux Functor** — the mechanism that lifts agents from Discrete State to Continuous Flow.

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T]
```

### The Four Critiques (MUST Address)

| Problem | Solution | Implementation |
|---------|----------|----------------|
| **Polling Fallacy** | Event-driven | No `asyncio.sleep()` in core |
| **Sink Problem** | `start() → AsyncIterator[B]` | Output queue + generator |
| **Bypass Problem** | Perturbation | Priority queue injection |
| **Recurrence Gap** | Ouroboric feedback | `feedback_fraction` config |

### Required Reading

1. `plans/agents/loop.md` — Full plan (content is Flux-revised)
2. `docs/spec-change-proposal.md` — Design decisions
3. `spec/agents/flux.md` — Formal specification (if created)
4. `spec/c-gents/functor-catalog.md` — Functor patterns
5. `spec/d-gents/symbiont.md` — State threading comparison
6. `impl/claude/agents/shared/skeleton.py` — Agent base

---

## File Structure

```
impl/claude/agents/flux/
├── __init__.py           # Public exports
├── functor.py            # Flux.lift() / Flux.unlift()
├── agent.py              # FluxAgent dataclass
├── config.py             # FluxConfig
├── state.py              # FluxState enum
├── errors.py             # FluxError exceptions
├── perturbation.py       # Perturbation handling
├── feedback.py           # Ouroboric feedback
├── pipeline.py           # FluxPipeline, | operator
├── topology.py           # Pressure, Flow, Turbulence metrics
├── sources/
│   ├── __init__.py
│   ├── base.py           # Source protocol
│   ├── events.py         # from_events()
│   ├── pheromones.py     # from_pheromones()
│   ├── periodic.py       # periodic() (when you need a timer)
│   ├── merged.py         # merged(), filtered(), mapped()
│   └── channel.py        # AsyncChannel for backpressure
├── observable.py         # I-gent integration
└── _tests/
    ├── __init__.py
    ├── test_functor.py
    ├── test_agent.py
    ├── test_perturbation.py
    ├── test_feedback.py
    ├── test_pipeline.py
    ├── test_sources.py
    ├── test_backpressure.py
    └── test_integration.py
```

---

## Phase 1: Core Infrastructure

### Task 1.1: Create `state.py`

```python
"""Flux lifecycle states."""

from enum import Enum

class FluxState(Enum):
    """
    Lifecycle states for FluxAgent.

    State machine:
        DORMANT ──start()──→ FLOWING ──source exhausted──→ DRAINING ──→ STOPPED
            │                    │                              │
            │                    │ entropy exhausted            │
            │                    ↓                              │
            │               COLLAPSED                           │
            │                                                   │
            └──────────────────stop()───────────────────────────┘

    Perturbation:
        FLOWING ──invoke()──→ PERTURBED ──processed──→ FLOWING
    """

    DORMANT = "dormant"
    """Created but not started. invoke() works in discrete mode."""

    FLOWING = "flowing"
    """Processing stream. invoke() = perturbation."""

    PERTURBED = "perturbed"
    """Currently handling a perturbation (high-priority event)."""

    DRAINING = "draining"
    """Source exhausted, flushing output buffer."""

    STOPPED = "stopped"
    """Explicitly stopped. Can restart."""

    COLLAPSED = "collapsed"
    """Entropy exhausted. Cannot restart without reset."""

    def can_start(self) -> bool:
        return self in (FluxState.DORMANT, FluxState.STOPPED)

    def is_processing(self) -> bool:
        return self in (FluxState.FLOWING, FluxState.PERTURBED, FluxState.DRAINING)

    def is_terminal(self) -> bool:
        return self in (FluxState.STOPPED, FluxState.COLLAPSED)

    def allows_perturbation(self) -> bool:
        """Can accept invoke() as perturbation?"""
        return self == FluxState.FLOWING
```

---

### Task 1.2: Create `errors.py`

```python
"""Flux-specific exceptions."""

from typing import Any

class FluxError(Exception):
    """Base exception for flux operations."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.context = context or {}

class FluxStateError(FluxError):
    """Invalid state transition."""
    pass

class FluxEntropyError(FluxError):
    """Entropy budget exhausted."""
    pass

class FluxBackpressureError(FluxError):
    """Backpressure limit exceeded."""
    pass

class FluxPerturbationError(FluxError):
    """Perturbation failed."""
    pass
```

---

### Task 1.3: Create `config.py`

```python
"""Flux configuration."""

from dataclasses import dataclass
from typing import Callable, TypeVar, Any

A = TypeVar("A")
B = TypeVar("B")

@dataclass
class FluxConfig:
    """
    Configuration for FluxAgent behavior.

    Three concerns:
    1. Entropy (J-gent physics) — bounds computation
    2. Backpressure — handles slow consumers
    3. Feedback (Ouroboros) — enables recurrence
    """

    # ─────────────────────────────────────────────────────────────
    # Entropy (J-gent physics)
    # ─────────────────────────────────────────────────────────────

    entropy_budget: float = 1.0
    """Initial entropy budget. Flux collapses when exhausted."""

    entropy_decay: float = 0.01
    """Entropy consumed per event processed."""

    max_events: int | None = None
    """Hard cap on events. None = unlimited (bounded by entropy)."""

    # ─────────────────────────────────────────────────────────────
    # Backpressure
    # ─────────────────────────────────────────────────────────────

    buffer_size: int = 100
    """Maximum items in output buffer."""

    drop_policy: str = "block"
    """
    How to handle full buffer:
    - "block": Wait for space (preserves all, may stall)
    - "drop_oldest": Discard oldest (real-time priority)
    - "drop_newest": Discard newest (historical priority)
    """

    # ─────────────────────────────────────────────────────────────
    # Feedback (Ouroboros)
    # ─────────────────────────────────────────────────────────────

    feedback_fraction: float = 0.0
    """
    Fraction of outputs routed back to input.
    0.0 = pure reactive (no feedback)
    0.5 = equal external/internal
    1.0 = full ouroboros (solipsism risk!)
    """

    feedback_transform: Callable[[Any], Any] | None = None
    """
    Transform B → A for feedback.
    Required if B is not compatible with A.
    """

    # ─────────────────────────────────────────────────────────────
    # Observability
    # ─────────────────────────────────────────────────────────────

    emit_pheromones: bool = True
    """Emit stigmergic signals during processing."""

    trace_enabled: bool = True
    """Enable W-gent tracing."""

    agent_id: str | None = None
    """Identifier for observability. Auto-generated if None."""

    # ─────────────────────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────────────────────

    def __post_init__(self) -> None:
        if self.entropy_budget <= 0:
            raise ValueError(f"entropy_budget must be > 0")
        if self.entropy_decay < 0:
            raise ValueError(f"entropy_decay must be >= 0")
        if self.buffer_size <= 0:
            raise ValueError(f"buffer_size must be > 0")
        if self.drop_policy not in ("block", "drop_oldest", "drop_newest"):
            raise ValueError(f"drop_policy must be block|drop_oldest|drop_newest")
        if not 0.0 <= self.feedback_fraction <= 1.0:
            raise ValueError(f"feedback_fraction must be in [0.0, 1.0]")
```

---

### Task 1.4: Create `perturbation.py`

```python
"""Perturbation handling for FluxAgent."""

from dataclasses import dataclass
from typing import TypeVar, Any
import asyncio

A = TypeVar("A")
B = TypeVar("B")

@dataclass
class Perturbation:
    """
    A high-priority event injected via invoke() on a FLOWING flux.

    The Perturbation Principle:
    - invoke() on DORMANT = direct invocation
    - invoke() on FLOWING = perturbation (injected into stream)

    This preserves State Integrity for Symbiont agents.
    """

    data: Any
    """The input data (type A)."""

    result_future: asyncio.Future
    """Future to receive the result (type B)."""

    priority: int = 0
    """Higher = processed sooner. Default perturbations have priority 0."""

    def __lt__(self, other: "Perturbation") -> bool:
        """For priority queue ordering (higher priority first)."""
        return self.priority > other.priority  # Reversed for max-heap behavior

def is_perturbation(event: Any) -> bool:
    """Check if event is a Perturbation wrapper."""
    return isinstance(event, Perturbation)

def unwrap_perturbation(event: Any) -> tuple[Any, asyncio.Future | None]:
    """
    Unwrap event, returning (data, future_or_none).

    If event is Perturbation: returns (data, result_future)
    If event is normal: returns (event, None)
    """
    if is_perturbation(event):
        return event.data, event.result_future
    return event, None
```

---

### Task 1.5: Create `agent.py` (The Core)

This is the critical file. Note the signature of `start()`:

```python
"""FluxAgent: Stream-transforming agent wrapper."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Any, AsyncIterator

from .config import FluxConfig
from .state import FluxState
from .errors import FluxError, FluxStateError, FluxEntropyError
from .perturbation import Perturbation, is_perturbation, unwrap_perturbation

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type

@dataclass
class FluxAgent(Generic[A, B]):
    """
    An agent lifted into the streaming domain.

    Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

    The Heterarchical Principle (§6) realized:
    - DORMANT: invoke() works discretely
    - FLOWING: invoke() = perturbation (injected into stream)
    - start() returns AsyncIterator[B] (output flows, not sinks)

    Key Methods:
    - start(source) → AsyncIterator[B]  # THE CRITICAL SIGNATURE
    - invoke(input) → B  # Discrete OR perturbation depending on state
    - stop() → None  # Graceful shutdown
    """

    inner: Any  # Agent[A, B] - using Any to avoid import cycle
    config: FluxConfig = field(default_factory=FluxConfig)

    # Runtime state
    _state: FluxState = field(default=FluxState.DORMANT, init=False)
    _events_processed: int = field(default=0, init=False)
    _entropy_remaining: float = field(init=False)
    _id: str = field(init=False)

    # Queues
    _perturbation_queue: asyncio.PriorityQueue = field(init=False)
    _output_queue: asyncio.Queue = field(init=False)
    _feedback_queue: asyncio.Queue = field(init=False)

    # Task handle
    _task: asyncio.Task | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._entropy_remaining = self.config.entropy_budget
        self._id = self.config.agent_id or f"flux-{uuid.uuid4().hex[:8]}"
        self._perturbation_queue = asyncio.PriorityQueue()
        self._output_queue = asyncio.Queue(maxsize=self.config.buffer_size)
        self._feedback_queue = asyncio.Queue()

    # ─────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────

    @property
    def state(self) -> FluxState:
        return self._state

    @property
    def events_processed(self) -> int:
        return self._events_processed

    @property
    def entropy_remaining(self) -> float:
        return self._entropy_remaining

    @property
    def id(self) -> str:
        return self._id

    # ─────────────────────────────────────────────────────────────
    # THE CRITICAL METHOD: start() returns AsyncIterator[B]
    # ─────────────────────────────────────────────────────────────

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
        """
        Start the flux and return the output stream.

        THIS IS THE KEY INSIGHT: start() doesn't return None.
        It returns Flux[B], enabling Living Pipelines.

        Args:
            source: Input stream (Flux[A])

        Returns:
            Output stream (Flux[B])

        Example:
            >>> async for result in flux_agent.start(events):
            ...     process(result)

            # Or pipe to another flux:
            >>> pipeline = flux_a | flux_b
            >>> async for result in pipeline.start(source):
            ...     ...
        """
        if not self._state.can_start():
            raise FluxStateError(f"Cannot start from state {self._state}")

        # Reset if restarting
        if self._state == FluxState.STOPPED:
            self._events_processed = 0
            self._entropy_remaining = self.config.entropy_budget

        # Spawn processing task
        self._task = asyncio.create_task(
            self._process_flux(source),
            name=f"flux-{self._id}"
        )

        # Return output generator
        return self._output_generator()

    async def _output_generator(self) -> AsyncIterator[B]:
        """
        Yield results from output queue.

        This generator is what makes Living Pipelines possible.
        """
        while True:
            # Check for terminal state
            if self._state.is_terminal():
                # Drain remaining items
                while not self._output_queue.empty():
                    yield self._output_queue.get_nowait()
                break

            # Get next output (with timeout to check state)
            try:
                result = await asyncio.wait_for(
                    self._output_queue.get(),
                    timeout=0.1
                )
                yield result
            except asyncio.TimeoutError:
                # Check if processing is done
                if self._state.is_terminal():
                    break
                continue

    # ─────────────────────────────────────────────────────────────
    # THE PERTURBATION PRINCIPLE: invoke() on FLOWING = inject
    # ─────────────────────────────────────────────────────────────

    async def invoke(self, input_data: A) -> B:
        """
        Discrete invocation OR perturbation depending on state.

        - DORMANT: Direct invocation (discrete mode)
        - FLOWING: Inject as high-priority perturbation

        The Perturbation Principle preserves State Integrity:
        If agent has Symbiont memory, perturbation flows through
        the same state-loading path. No race conditions.

        Args:
            input_data: Input to process

        Returns:
            Result from inner agent
        """
        if self._state == FluxState.DORMANT:
            # Direct invocation (discrete mode)
            return await self.inner.invoke(input_data)

        if self._state.allows_perturbation():
            # Perturbation: inject into stream with priority
            result_future: asyncio.Future[B] = asyncio.Future()

            perturbation = Perturbation(
                data=input_data,
                result_future=result_future,
                priority=100,  # High priority
            )

            await self._perturbation_queue.put(perturbation)

            # Wait for result (processed by flux)
            return await result_future

        raise FluxStateError(f"Cannot invoke from state {self._state}")

    # ─────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────

    async def stop(self) -> None:
        """Stop the flux gracefully."""
        self._state = FluxState.STOPPED

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def wait(self) -> None:
        """Wait for flux to complete (source exhausted or stopped)."""
        if self._task:
            await self._task

    # ─────────────────────────────────────────────────────────────
    # The Flux Processor (NO asyncio.sleep in core!)
    # ─────────────────────────────────────────────────────────────

    async def _process_flux(self, source: AsyncIterator[A]) -> None:
        """
        Process input flux, emit output flux.

        EVENT-DRIVEN: No asyncio.sleep() here!
        We await events from source, not poll on a timer.
        """
        self._state = FluxState.FLOWING

        try:
            async for event in self._merged_source(source):
                # Check entropy budget
                if not self._can_continue():
                    self._state = FluxState.COLLAPSED
                    break

                # Unwrap perturbation if needed
                input_data, result_future = unwrap_perturbation(event)

                if result_future:
                    self._state = FluxState.PERTURBED

                # Process through inner agent
                try:
                    result = await self.inner.invoke(input_data)
                except Exception as e:
                    if result_future:
                        result_future.set_exception(e)
                    await self._emit_pheromone("error", str(e))
                    continue
                finally:
                    if self._state == FluxState.PERTURBED:
                        self._state = FluxState.FLOWING

                # Route result
                if result_future:
                    # Perturbation result goes to caller
                    result_future.set_result(result)
                else:
                    # Normal result goes to output stream
                    await self._emit_output(result)

                # Ouroboric feedback
                await self._maybe_feedback(result)

                # Consume entropy
                self._consume_entropy()
                self._events_processed += 1

            # Source exhausted
            self._state = FluxState.DRAINING

        except asyncio.CancelledError:
            raise

        finally:
            if self._state not in (FluxState.STOPPED, FluxState.COLLAPSED):
                self._state = FluxState.STOPPED

            await self._emit_pheromone("stopped", {
                "events_processed": self._events_processed,
                "final_state": self._state.value,
            })

    async def _merged_source(
        self,
        source: AsyncIterator[A]
    ) -> AsyncIterator[A | Perturbation]:
        """
        Merge source with perturbation queue and feedback queue.

        Priority order:
        1. Perturbations (highest)
        2. Feedback (medium)
        3. Source (normal)
        """
        source_done = False

        while not source_done or not self._all_queues_empty():
            # 1. Check perturbations (priority)
            try:
                perturbation = self._perturbation_queue.get_nowait()
                yield perturbation
                continue
            except asyncio.QueueEmpty:
                pass

            # 2. Check feedback
            try:
                feedback_event = self._feedback_queue.get_nowait()
                yield feedback_event
                continue
            except asyncio.QueueEmpty:
                pass

            # 3. Get from source
            try:
                event = await asyncio.wait_for(
                    source.__anext__(),
                    timeout=0.05  # Short timeout to check queues
                )
                yield event
            except asyncio.TimeoutError:
                continue
            except StopAsyncIteration:
                source_done = True

    def _all_queues_empty(self) -> bool:
        return (
            self._perturbation_queue.empty() and
            self._feedback_queue.empty()
        )

    # ─────────────────────────────────────────────────────────────
    # Output Emission (with backpressure)
    # ─────────────────────────────────────────────────────────────

    async def _emit_output(self, result: B) -> None:
        """Emit to output stream with backpressure handling."""
        policy = self.config.drop_policy

        if policy == "block":
            await self._output_queue.put(result)

        elif policy == "drop_oldest":
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
                pass  # Discard newest

    # ─────────────────────────────────────────────────────────────
    # Ouroboric Feedback
    # ─────────────────────────────────────────────────────────────

    async def _maybe_feedback(self, result: B) -> None:
        """
        The Ouroboros: Output feeds back to input.

        If feedback_fraction > 0, route some outputs back.
        """
        if self.config.feedback_fraction <= 0:
            return

        import random
        if random.random() > self.config.feedback_fraction:
            return

        # Transform B → A if needed
        if self.config.feedback_transform:
            feedback_input = self.config.feedback_transform(result)
        else:
            # Hope B is compatible with A
            feedback_input = result

        # Low-priority injection (not perturbation)
        try:
            self._feedback_queue.put_nowait(feedback_input)
        except asyncio.QueueFull:
            pass  # Drop if feedback queue full

    # ─────────────────────────────────────────────────────────────
    # Entropy Management
    # ─────────────────────────────────────────────────────────────

    def _can_continue(self) -> bool:
        if self.config.max_events:
            if self._events_processed >= self.config.max_events:
                return False
        return self._entropy_remaining > 0

    def _consume_entropy(self) -> None:
        self._entropy_remaining -= self.config.entropy_decay
        self._entropy_remaining = max(0.0, self._entropy_remaining)

    # ─────────────────────────────────────────────────────────────
    # Pheromone Emission (best-effort)
    # ─────────────────────────────────────────────────────────────

    async def _emit_pheromone(self, signal: str, data: Any) -> None:
        if not self.config.emit_pheromones:
            return
        try:
            # Integration with pheromone system
            pass
        except Exception:
            pass  # Best-effort

    # ─────────────────────────────────────────────────────────────
    # Composition: The Pipe Operator
    # ─────────────────────────────────────────────────────────────

    def __or__(self, other: "FluxAgent[B, Any]") -> "FluxPipeline[A, Any]":
        """
        Pipe operator: flux_a | flux_b

        Creates a Living Pipeline.
        """
        from .pipeline import FluxPipeline
        return FluxPipeline([self, other])

    def __rshift__(self, other: Any) -> "FluxAgent[A, Any]":
        """
        Compose with static agent: Flux(f) >> g

        Result is FluxAgent with composed inner.
        """
        from ..shared.skeleton import ComposedAgent
        composed = ComposedAgent(self.inner, other)
        return FluxAgent(inner=composed, config=self.config)

    # ─────────────────────────────────────────────────────────────
    # String Representation
    # ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"FluxAgent(id={self._id!r}, "
            f"state={self._state.value}, "
            f"events={self._events_processed}, "
            f"entropy={self._entropy_remaining:.3f})"
        )
```

---

### Task 1.6: Create `functor.py`

```python
"""Flux Functor: The lift mechanism."""

from typing import TypeVar, Any

from .agent import FluxAgent
from .config import FluxConfig

A = TypeVar("A")
B = TypeVar("B")

class Flux:
    """
    The Flux Functor: Agent[A, B] → Agent[Flux[A], Flux[B]]

    Lifts an agent from Discrete State to Continuous Flow.

    Functor Laws:
        Identity:    Flux(Id) ≅ Id_Flux
        Composition: Flux(f >> g) ≅ Flux(f) >> Flux(g)

    Usage:
        >>> flux_agent = Flux.lift(my_agent)
        >>> async for result in flux_agent.start(source):
        ...     process(result)
    """

    @staticmethod
    def lift(
        agent: Any,  # Agent[A, B]
        config: FluxConfig | None = None,
    ) -> FluxAgent[A, B]:
        """
        Lift agent to flux domain.

        Args:
            agent: The discrete agent to lift
            config: Optional configuration

        Returns:
            FluxAgent wrapping the input agent
        """
        return FluxAgent(
            inner=agent,
            config=config or FluxConfig(),
        )

    @staticmethod
    def unlift(flux_agent: FluxAgent[A, B]) -> Any:
        """
        Extract inner agent from flux.

        Note: Does NOT stop a running flux.
        Call flux_agent.stop() first if needed.
        """
        return flux_agent.inner

    @staticmethod
    def is_flux(agent: Any) -> bool:
        """Check if agent is a FluxAgent."""
        return isinstance(agent, FluxAgent)
```

---

### Task 1.7: Create `pipeline.py`

```python
"""FluxPipeline: Living Pipelines via | operator."""

from dataclasses import dataclass
from typing import TypeVar, Generic, AsyncIterator, Any

A = TypeVar("A")
B = TypeVar("B")

@dataclass
class FluxPipeline(Generic[A, B]):
    """
    A chain of FluxAgents forming a Living Pipeline.

    Because start() returns AsyncIterator[B], pipelines are possible:

        pipeline = flux_a | flux_b | flux_c
        async for result in pipeline.start(source):
            ...

    Output of each stage flows to input of next stage.
    """

    stages: list[Any]  # list[FluxAgent]

    async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
        """
        Start all stages, chaining their streams.

        Output of stage N becomes input of stage N+1.
        """
        current_stream: AsyncIterator[Any] = source

        for stage in self.stages:
            current_stream = await stage.start(current_stream)

        async for result in current_stream:
            yield result

    def __or__(self, other: Any) -> "FluxPipeline[A, Any]":
        """Extend pipeline: pipeline | flux_c"""
        return FluxPipeline(self.stages + [other])

    async def stop(self) -> None:
        """Stop all stages."""
        for stage in self.stages:
            await stage.stop()
```

---

## Phase 2: Sources (Event-Driven!)

### Task 2.1: Create `sources/events.py`

```python
"""Event-driven sources (NOT timer-driven)."""

from typing import AsyncIterator, TypeVar, Protocol, runtime_checkable

T = TypeVar("T")

@runtime_checkable
class EventBus(Protocol[T]):
    """Protocol for event buses."""

    def subscribe(self) -> AsyncIterator[T]:
        """Subscribe to events."""
        ...

async def from_events(bus: EventBus[T]) -> AsyncIterator[T]:
    """
    Yield events as they occur.

    THIS IS THE PATTERN. Event-driven, not timer-driven.

    Example:
        >>> async for event in from_events(my_bus):
        ...     process(event)
    """
    async for event in bus.subscribe():
        yield event

async def from_stream(stream: AsyncIterator[T]) -> AsyncIterator[T]:
    """
    Pass-through adapter for any async iterator.

    Useful for wrapping existing async iterators.
    """
    async for item in stream:
        yield item
```

### Task 2.2: Create `sources/periodic.py`

```python
"""
Periodic source (timer-based).

NOTE: This is for when you ACTUALLY need a timer.
It's not the default pattern — event-driven is the default.
"""

import asyncio
import time
from typing import AsyncIterator

async def periodic(interval: float) -> AsyncIterator[float]:
    """
    Emit timestamps at regular intervals.

    USE SPARINGLY. This is timer-driven (polling).
    Prefer event-driven sources when possible.

    Args:
        interval: Seconds between emissions

    Yields:
        Unix timestamps
    """
    while True:
        yield time.time()
        await asyncio.sleep(interval)

async def countdown(count: int, interval: float = 1.0) -> AsyncIterator[int]:
    """
    Emit countdown from count to 0.

    Finite source for bounded flux.
    """
    for n in range(count, -1, -1):
        yield n
        if n > 0:
            await asyncio.sleep(interval)
```

---

## Phase 3: Testing

### Key Test Cases

```python
# test_agent.py

@pytest.mark.asyncio
async def test_start_returns_async_iterator():
    """THE CRITICAL TEST: start() returns AsyncIterator[B], not None."""
    agent = MockAgent()
    flux = Flux.lift(agent)

    result = flux.start(mock_source())

    # Must be async iterator
    assert hasattr(result, '__anext__')

@pytest.mark.asyncio
async def test_perturbation_not_bypass():
    """invoke() on FLOWING must perturb, not bypass."""
    agent = StatefulMockAgent()  # Has state that must be respected
    flux = Flux.lift(agent)

    # Start flowing
    output = flux.start(slow_source())

    # Perturb while flowing
    result = await flux.invoke("perturbation_input")

    # Result must have gone through the same processing path
    # (state loaded/saved correctly)
    assert agent.state_was_respected

@pytest.mark.asyncio
async def test_no_sleep_in_core():
    """Core processing must be event-driven, not timer-driven."""
    # Inspect FluxAgent._process_flux for asyncio.sleep calls
    # (Static analysis or code review)
    import inspect
    source = inspect.getsource(FluxAgent._process_flux)
    assert "asyncio.sleep" not in source  # No polling in core!

@pytest.mark.asyncio
async def test_living_pipeline():
    """Pipeline composition via | must work."""
    flux_a = Flux.lift(DoublerAgent())
    flux_b = Flux.lift(AdderAgent())

    pipeline = flux_a | flux_b

    results = []
    async for result in pipeline.start(number_source([1, 2, 3])):
        results.append(result)

    # Input: 1, 2, 3
    # After flux_a (double): 2, 4, 6
    # After flux_b (add 1): 3, 5, 7
    assert results == [3, 5, 7]

@pytest.mark.asyncio
async def test_ouroboric_feedback():
    """feedback_fraction routes output back to input."""
    agent = EchoAgent()
    flux = Flux.lift(agent, FluxConfig(
        feedback_fraction=1.0,  # Full ouroboros
        max_events=5,  # Prevent infinite
    ))

    results = []
    async for result in flux.start(single_item_source("seed")):
        results.append(result)

    # Should have processed multiple times due to feedback
    assert len(results) > 1
```

---

## Verification Checklist

### Code Quality
- [ ] No `asyncio.sleep()` in `FluxAgent._process_flux`
- [ ] `start()` returns `AsyncIterator[B]`, never `None`
- [ ] Perturbation queue, not bypass, for invoke() on FLOWING
- [ ] Ouroboric feedback implemented
- [ ] Type hints on all public methods

### Tests
- [ ] 100+ tests
- [ ] All pass: `pytest impl/claude/agents/flux/`
- [ ] Coverage > 90%
- [ ] Functor laws verified
- [ ] Perturbation preserves state integrity
- [ ] Living pipelines work

### Integration
- [ ] `Flux.lift()` works with existing agents
- [ ] `|` operator creates FluxPipeline
- [ ] Observable protocol for I-gent

---

## Success Criteria

1. **`start()` returns `AsyncIterator[B]`** — NOT `None`
2. **No polling in core** — Event-driven
3. **Perturbation, not bypass** — State integrity
4. **Living Pipelines** — `flux_a | flux_b` works
5. **Ouroboros** — `feedback_fraction` routes output to input
6. **Functor laws hold**
7. **Tests: 100+, all green**

---

*"The noun is a lie. There is only the rate of change."*
*"Static: A → B. Dynamic: dA/dt → dB/dt."*
