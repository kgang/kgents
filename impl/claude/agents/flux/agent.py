"""
FluxAgent: Stream-transforming agent wrapper.

The core implementation of the Flux Functor. FluxAgent wraps a discrete
agent (Agent[A, B]) and lifts it to the streaming domain:

    Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T].

Key Design Decisions:
1. start() returns AsyncIterator[B], NOT None (The Sink Problem solved)
2. invoke() on FLOWING = perturbation (The Bypass Problem solved)
3. No asyncio.sleep() in core (Event-driven, NOT timer-driven)
4. Ouroboric feedback via feedback_fraction config
"""

from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, Generic, TypeVar, cast

from agents.poly.types import Agent

from .config import FluxConfig
from .errors import FluxStateError
from .perturbation import (
    Perturbation,
    is_perturbation,
    unwrap_perturbation,
)
from .state import FluxState

if TYPE_CHECKING:
    from impl.claude.protocols.terrarium.mirror import HolographicBuffer

    from .metabolism import FluxMetabolism
    from .pipeline import FluxPipeline
    from .semaphore.purgatory import Purgatory

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

    Example:
        >>> flux_agent = Flux.lift(my_agent)
        >>> async for result in flux_agent.start(events):
        ...     process(result)

        # Or pipe to another flux:
        >>> pipeline = flux_a | flux_b
        >>> async for result in pipeline.start(source):
        ...     ...
    """

    inner: Agent[A, B]
    config: FluxConfig = field(default_factory=FluxConfig)

    # Runtime state (not part of initialization)
    _state: FluxState = field(default=FluxState.DORMANT, init=False)
    _events_processed: int = field(default=0, init=False)
    _entropy_remaining: float = field(init=False)
    _id: str = field(init=False)

    # Queues (initialized in __post_init__)
    _perturbation_queue: asyncio.PriorityQueue[Perturbation] = field(init=False)
    _output_queue: asyncio.Queue[B] = field(init=False)
    _feedback_queue: asyncio.Queue[A] = field(init=False)

    # Task handle
    _task: asyncio.Task[None] | None = field(default=None, init=False)

    # Sentinel for output completion
    _SENTINEL: object = field(default_factory=object, init=False)

    # Metabolism integration (optional)
    _metabolism: "FluxMetabolism[A, B] | None" = field(default=None, init=False)

    # Mirror Protocol integration (Phase 5: Terrarium observability)
    _mirror: "HolographicBuffer | None" = field(default=None, init=False)

    # Purgatory integration (Phase 5: Semaphore system)
    _purgatory: "Purgatory | None" = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize runtime state and queues."""
        self._entropy_remaining = self.config.entropy_budget
        self._id = self.config.agent_id or f"flux-{uuid.uuid4().hex[:8]}"
        self._perturbation_queue = asyncio.PriorityQueue()
        self._output_queue = asyncio.Queue(maxsize=self.config.buffer_size)
        self._feedback_queue = asyncio.Queue(maxsize=self.config.feedback_queue_size)

    # ─────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Human-readable name including inner agent."""
        return f"Flux({self.inner.name})"

    @property
    def state(self) -> FluxState:
        """Current lifecycle state."""
        return self._state

    @property
    def events_processed(self) -> int:
        """Number of events processed so far."""
        return self._events_processed

    @property
    def entropy_remaining(self) -> float:
        """Remaining entropy budget."""
        return self._entropy_remaining

    @property
    def id(self) -> str:
        """Unique identifier for this flux."""
        return self._id

    @property
    def is_running(self) -> bool:
        """Check if flux is currently processing."""
        return self._state.is_processing()

    @property
    def metabolism(self) -> "FluxMetabolism[A, B] | None":
        """Optional metabolism adapter."""
        return self._metabolism

    # ─────────────────────────────────────────────────────────────
    # Metabolism Integration
    # ─────────────────────────────────────────────────────────────

    def attach_metabolism(
        self, metabolism: "FluxMetabolism[A, B]"
    ) -> "FluxAgent[A, B]":
        """
        Attach a metabolism adapter to this flux.

        When attached, the flux will:
        - Call metabolism.consume() on each event processed
        - Track metabolic pressure alongside flux entropy
        - Potentially trigger fever events

        Args:
            metabolism: The FluxMetabolism adapter to attach

        Returns:
            Self (for chaining)

        Example:
            >>> flux = Flux.lift(agent).attach_metabolism(metabolism)
        """
        self._metabolism = metabolism
        return self

    def detach_metabolism(self) -> "FluxMetabolism[A, B] | None":
        """
        Detach the metabolism adapter.

        Returns:
            The previously attached metabolism, or None
        """
        metabolism = self._metabolism
        self._metabolism = None
        return metabolism

    # ─────────────────────────────────────────────────────────────
    # Mirror Protocol Integration (Phase 5: Terrarium)
    # ─────────────────────────────────────────────────────────────

    def attach_mirror(self, mirror: "HolographicBuffer") -> "FluxAgent[A, B]":
        """
        Attach a HolographicBuffer for Terrarium observability.

        When attached, the flux will:
        - Emit TerriumEvents for semaphore ejections
        - Emit TerriumEvents for semaphore resolutions
        - Allow external observation without disturbing metabolism

        The Mirror Protocol ensures:
        - Agent emits ONCE to the buffer
        - Buffer broadcasts to N clients
        - Slow clients don't slow the agent

        Args:
            mirror: The HolographicBuffer to attach

        Returns:
            Self (for chaining)

        Example:
            >>> flux = Flux.lift(agent).attach_mirror(buffer)
        """
        self._mirror = mirror
        return self

    def detach_mirror(self) -> "HolographicBuffer | None":
        """
        Detach the mirror.

        Returns:
            The previously attached mirror, or None
        """
        mirror = self._mirror
        self._mirror = None
        return mirror

    @property
    def mirror(self) -> "HolographicBuffer | None":
        """Optional mirror for Terrarium observability."""
        return self._mirror

    # ─────────────────────────────────────────────────────────────
    # Purgatory Integration (Phase 5: Semaphores)
    # ─────────────────────────────────────────────────────────────

    def attach_purgatory(self, purgatory: "Purgatory") -> "FluxAgent[A, B]":
        """
        Attach a Purgatory for semaphore handling.

        When attached, the flux will:
        - Detect SemaphoreToken returns from inner.invoke()
        - Eject blocked events to Purgatory (no head-of-line blocking)
        - Handle ReentryContext injection for resolution

        The Rodizio Pattern:
        - Agent returns SemaphoreToken (the Red Card)
        - FluxAgent detects and ejects to Purgatory
        - Stream continues processing other events
        - Human resolves via CLI/API
        - ReentryContext injected as high-priority Perturbation
        - Agent's resume() method completes processing

        Args:
            purgatory: The Purgatory instance

        Returns:
            Self (for chaining)

        Example:
            >>> flux = Flux.lift(agent).attach_purgatory(purgatory)
        """
        self._purgatory = purgatory
        return self

    def detach_purgatory(self) -> "Purgatory | None":
        """
        Detach the purgatory.

        Returns:
            The previously attached purgatory, or None
        """
        purgatory = self._purgatory
        self._purgatory = None
        return purgatory

    @property
    def purgatory(self) -> "Purgatory | None":
        """Optional purgatory for semaphore handling."""
        return self._purgatory

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
            raise FluxStateError(
                f"Cannot start from state {self._state}",
                current_state=self._state.value,
                attempted_operation="start",
            )

        # Reset if restarting
        if self._state == FluxState.STOPPED:
            self._events_processed = 0
            self._entropy_remaining = self.config.entropy_budget
            # Create fresh queues (more reliable than clearing)
            self._perturbation_queue = asyncio.PriorityQueue()
            self._output_queue = asyncio.Queue(maxsize=self.config.buffer_size)
            self._feedback_queue = asyncio.Queue(
                maxsize=self.config.feedback_queue_size
            )
            # Create fresh sentinel
            self._SENTINEL = object()
            # Reset state to DORMANT so we can properly transition
            self._state = FluxState.DORMANT

        # Spawn processing task
        self._task = asyncio.create_task(
            self._process_flux(source),
            name=f"flux-{self._id}",
        )

        # Return output generator
        async for item in self._output_generator():
            yield item

    async def _output_generator(self) -> AsyncIterator[B]:
        """
        Yield results from output queue.

        This generator is what makes Living Pipelines possible.
        It continues yielding until the flux reaches a terminal state
        and the output queue is drained.
        """
        while True:
            # Check for terminal state with empty queue
            if self._state.is_terminal():
                # Drain remaining items
                while not self._output_queue.empty():
                    try:
                        item = self._output_queue.get_nowait()
                        if item is not self._SENTINEL:
                            yield item
                    except asyncio.QueueEmpty:
                        break
                break

            # Get next output (with timeout to check state)
            try:
                result = await asyncio.wait_for(
                    self._output_queue.get(),
                    timeout=0.1,
                )
                # Check for sentinel
                if result is self._SENTINEL:
                    break
                yield result
            except asyncio.TimeoutError:
                # Check if processing is done
                if self._state.is_terminal():
                    # Drain remaining
                    while not self._output_queue.empty():
                        try:
                            item = self._output_queue.get_nowait()
                            if item is not self._SENTINEL:
                                yield item
                        except asyncio.QueueEmpty:
                            break
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

        Raises:
            FluxStateError: If state doesn't allow invocation
        """
        if self._state == FluxState.DORMANT:
            # Direct invocation (discrete mode)
            return await self.inner.invoke(input_data)

        if self._state.allows_perturbation():
            # Perturbation: inject into stream with priority
            loop = asyncio.get_running_loop()
            result_future: asyncio.Future[B] = loop.create_future()

            perturbation = Perturbation(
                data=input_data,
                result_future=result_future,
                priority=self.config.perturbation_priority,
            )

            await self._perturbation_queue.put(perturbation)

            # Wait for result (processed by flux)
            if self.config.perturbation_timeout:
                return await asyncio.wait_for(
                    result_future,
                    timeout=self.config.perturbation_timeout,
                )
            return await result_future

        raise FluxStateError(
            f"Cannot invoke from state {self._state}",
            current_state=self._state.value,
            attempted_operation="invoke",
        )

    # ─────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────

    async def stop(self) -> None:
        """Stop the flux gracefully."""
        self._state = FluxState.STOPPED

        # Cancel pending perturbations
        while not self._perturbation_queue.empty():
            try:
                perturbation = self._perturbation_queue.get_nowait()
                perturbation.cancel("Flux stopped")
            except asyncio.QueueEmpty:
                break

        # Signal output completion
        try:
            self._output_queue.put_nowait(self._SENTINEL)  # type: ignore
        except asyncio.QueueFull:
            pass

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
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def reset(self) -> None:
        """
        Reset flux to DORMANT state.

        Only valid from STOPPED or COLLAPSED states.
        Restores entropy budget and clears counters.
        """
        if self._state not in (FluxState.STOPPED, FluxState.COLLAPSED):
            raise FluxStateError(
                f"Cannot reset from state {self._state}",
                current_state=self._state.value,
                attempted_operation="reset",
            )

        self._state = FluxState.DORMANT
        self._events_processed = 0
        self._entropy_remaining = self.config.entropy_budget
        self._task = None

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
                    await self._emit_pheromone(
                        "collapsed",
                        {
                            "events_processed": self._events_processed,
                            "entropy_remaining": self._entropy_remaining,
                        },
                    )
                    break

                # Unwrap perturbation if needed
                input_data, result_future = unwrap_perturbation(event)

                # Consume metabolic energy (The Accursed Share)
                # This may trigger fever if pressure exceeds threshold
                if self._metabolism is not None:
                    fever_event = await self._metabolism.consume(input_data)
                    if fever_event is not None:
                        await self._emit_pheromone(
                            "fever",
                            {
                                "intensity": fever_event.intensity,
                                "oblique": fever_event.oblique_strategy,
                            },
                        )

                if result_future:
                    self._state = FluxState.PERTURBED

                # Phase 5: Check for ReentryContext (semaphore resolution)
                # ReentryContext is injected as Perturbation when human resolves
                is_reentry, reentry_result = await self._handle_reentry_if_needed(
                    input_data
                )
                if is_reentry:
                    # Reentry handled - emit result and continue
                    if result_future and not result_future.done():
                        result_future.set_result(reentry_result)
                    else:
                        await self._emit_output(reentry_result)
                    # Emit resolution event to mirror
                    await self._emit_semaphore_resolved(input_data)
                    if self._state == FluxState.PERTURBED:
                        self._state = FluxState.FLOWING
                    self._consume_entropy()
                    self._events_processed += 1
                    continue

                # Process through inner agent
                try:
                    result = await self.inner.invoke(input_data)
                except Exception as e:
                    if result_future and not result_future.done():
                        result_future.set_exception(e)
                    await self._emit_pheromone(
                        "error",
                        {
                            "error": str(e),
                            "input": repr(input_data),
                        },
                    )
                    continue
                finally:
                    if self._state == FluxState.PERTURBED:
                        self._state = FluxState.FLOWING

                # Phase 5: Check for SemaphoreToken (agent yielding to human)
                # If detected, eject to Purgatory and emit to Mirror
                if await self._handle_semaphore_if_needed(result, input_data):
                    # Semaphore handled - stream continues (no head-of-line blocking)
                    # Don't emit to output, don't set result_future
                    self._consume_entropy()
                    self._events_processed += 1
                    continue

                # Route result
                if result_future and not result_future.done():
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
            if self._state == FluxState.FLOWING:
                self._state = FluxState.DRAINING

        except asyncio.CancelledError:
            raise

        finally:
            if self._state not in (FluxState.STOPPED, FluxState.COLLAPSED):
                self._state = FluxState.STOPPED

            # Signal output completion
            try:
                self._output_queue.put_nowait(self._SENTINEL)  # type: ignore
            except asyncio.QueueFull:
                pass

            await self._emit_pheromone(
                "stopped",
                {
                    "events_processed": self._events_processed,
                    "final_state": self._state.value,
                    "entropy_remaining": self._entropy_remaining,
                },
            )

    async def _merged_source(
        self,
        source: AsyncIterator[A],
    ) -> AsyncIterator[A | Perturbation]:
        """
        Merge source with perturbation queue and feedback queue.

        Priority order:
        1. Perturbations (highest)
        2. Feedback (medium)
        3. Source (normal)

        EVENT-DRIVEN: We await events, not poll on timers.
        """
        source_done = False
        source_iter = source.__aiter__()

        while not source_done or not self._all_queues_empty():
            # Check if we should stop
            if self._state in (FluxState.STOPPED, FluxState.COLLAPSED):
                break

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

            # 3. Get from source (with short timeout to check queues)
            if not source_done:
                try:
                    event = await asyncio.wait_for(
                        source_iter.__anext__(),
                        timeout=0.05,  # Short timeout to check queues
                    )
                    yield event
                except asyncio.TimeoutError:
                    # No event ready, loop back to check queues
                    continue
                except StopAsyncIteration:
                    source_done = True
            else:
                # Source done, wait briefly for more perturbations/feedback
                await asyncio.sleep(0.01)

    def _all_queues_empty(self) -> bool:
        """Check if all internal queues are empty."""
        return self._perturbation_queue.empty() and self._feedback_queue.empty()

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

        if random.random() > self.config.feedback_fraction:
            return

        # Transform B → A if needed
        if self.config.feedback_transform:
            try:
                feedback_input = self.config.feedback_transform(result)
            except Exception:
                # Transform failed, skip feedback
                return
        else:
            # Hope B is compatible with A
            feedback_input = cast(A, result)

        # Low-priority injection (not perturbation)
        try:
            self._feedback_queue.put_nowait(feedback_input)
        except asyncio.QueueFull:
            pass  # Drop if feedback queue full

    # ─────────────────────────────────────────────────────────────
    # Entropy Management
    # ─────────────────────────────────────────────────────────────

    def _can_continue(self) -> bool:
        """Check if flux can process more events."""
        if self.config.max_events is not None:
            if self._events_processed >= self.config.max_events:
                return False
        return self._entropy_remaining > 0

    def _consume_entropy(self) -> None:
        """Consume entropy for processing one event."""
        self._entropy_remaining -= self.config.entropy_decay
        self._entropy_remaining = max(0.0, self._entropy_remaining)

    # ─────────────────────────────────────────────────────────────
    # Pheromone Emission (best-effort)
    # ─────────────────────────────────────────────────────────────

    async def _emit_pheromone(self, signal: str, data: Any) -> None:
        """
        Emit pheromone signal for observability.

        Best-effort: failures are silently ignored.
        """
        if not self.config.emit_pheromones:
            return
        # TODO: Integration with pheromone system
        # For now, this is a placeholder

    # ─────────────────────────────────────────────────────────────
    # Phase 5: Semaphore Integration (Purgatory + Mirror)
    # ─────────────────────────────────────────────────────────────

    async def _handle_semaphore_if_needed(
        self, result: Any, original_event: Any
    ) -> bool:
        """
        Check if result is SemaphoreToken and handle if so.

        The Rodizio Pattern:
        1. Detect SemaphoreToken return
        2. Eject to Purgatory (if attached)
        3. Emit to Mirror (if attached)
        4. Stream continues (no blocking)

        Args:
            result: Return value from inner.invoke()
            original_event: The input event that triggered this

        Returns:
            True if result was a SemaphoreToken (handled), False otherwise
        """
        from .semaphore.flux_integration import process_semaphore_result
        from .semaphore.mixin import is_semaphore_token

        if not is_semaphore_token(result):
            return False

        # Eject to Purgatory if attached
        if self._purgatory is not None:
            await process_semaphore_result(
                token=result,
                purgatory=self._purgatory,
                original_event=original_event,
            )

        # Emit to Mirror if attached (Phase 5 Terrarium integration)
        await self._emit_semaphore_ejected(result)

        return True

    async def _handle_reentry_if_needed(self, event: Any) -> tuple[bool, Any]:
        """
        Check if event is ReentryContext and handle if so.

        Called when human resolves a semaphore and ReentryContext
        is injected as a high-priority Perturbation.

        Args:
            event: The event to check

        Returns:
            (True, result) if was ReentryContext, (False, None) otherwise
        """
        from .semaphore.flux_integration import (
            is_reentry_context,
            process_reentry_event,
        )

        if not is_reentry_context(event):
            return False, None

        # Process reentry through agent.resume()
        result = await process_reentry_event(
            reentry=event,
            agent=self.inner,
        )
        return True, result

    async def _emit_semaphore_ejected(self, token: Any) -> None:
        """
        Emit SemaphoreEvent to Mirror when token ejected.

        Fire and forget - failures are silently ignored.
        The agent's metabolism is sacred; observers don't slow it.

        Args:
            token: The SemaphoreToken that was ejected
        """
        if self._mirror is None:
            return

        try:
            from protocols.terrarium.events import SemaphoreEvent

            # Build context from token
            context: dict[str, Any] = {}
            if hasattr(token, "reason") and token.reason is not None:
                context["reason"] = (
                    token.reason.value
                    if hasattr(token.reason, "value")
                    else str(token.reason)
                )
            if hasattr(token, "deadline") and token.deadline is not None:
                context["deadline"] = (
                    token.deadline.isoformat()
                    if hasattr(token.deadline, "isoformat")
                    else str(token.deadline)
                )

            semaphore_event = SemaphoreEvent(
                token_id=token.id,
                agent_id=self._id,
                prompt=getattr(token, "prompt", "") or "",
                options=getattr(token, "options", []) or [],
                severity=getattr(token, "severity", "info") or "info",
                context=context,
            )

            # Convert to TerriumEvent and emit
            terrium_event = semaphore_event.as_terrium_event()
            await self._mirror.reflect(terrium_event.as_dict())

        except Exception:
            # Best effort - don't disrupt flux for mirror failures
            pass

    async def _emit_semaphore_resolved(self, reentry: Any) -> None:
        """
        Emit resolution event to Mirror when semaphore resolved.

        Fire and forget - failures are silently ignored.

        Args:
            reentry: The ReentryContext that was processed
        """
        if self._mirror is None:
            return

        try:
            from protocols.terrarium.events import EventType, TerriumEvent

            terrium_event = TerriumEvent(
                event_type=EventType.SEMAPHORE_RESOLVED,
                agent_id=self._id,
                data={
                    "token_id": getattr(reentry, "token_id", "unknown"),
                    "resolved": True,
                },
            )
            await self._mirror.reflect(terrium_event.as_dict())

        except Exception:
            # Best effort - don't disrupt flux for mirror failures
            pass

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

    def __rshift__(self, other: Agent[B, Any]) -> "FluxAgent[A, Any]":
        """
        Compose with static agent: Flux(f) >> g

        Result is FluxAgent with composed inner.
        """
        from agents.poly.types import ComposedAgent

        composed = ComposedAgent(self.inner, other)
        return FluxAgent(inner=composed, config=self.config)

    # ─────────────────────────────────────────────────────────────
    # String Representation
    # ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"FluxAgent(id={self._id!r}, "
            f"inner={self.inner.name!r}, "
            f"state={self._state.value}, "
            f"events={self._events_processed}, "
            f"entropy={self._entropy_remaining:.3f})"
        )
