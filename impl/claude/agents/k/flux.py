"""
KgentFlux: K-gent as a Flux Stream Agent.

K-gent Phase 2: Lifts KgentSoul to the streaming domain.

KgentFlux wraps KgentSoul and provides:
1. DORMANT mode: Direct invoke() for dialogue
2. FLOWING mode: Ambient presence processing SoulEvents
3. Perturbation: inject() while FLOWING for priority events
4. Pulse emission: Periodic vitality signals

The key insight: K-gent isn't just a CLI command. It's an ambient
presence that can:
- Listen to Semaphore tokens from the stream
- Emit dialogue turns as events
- Pulse vitality signals
- Maintain soul state across interactions

Architecture:
    SoulEvent → KgentFlux → KgentSoul → SoulEvent

This enables Terrarium integration: external systems can observe
K-gent activity and inject dialogue via WebSocket.

Usage:
    from agents.k.flux import KgentFlux

    # Create flux-lifted K-gent
    flux = KgentFlux()

    # FLOWING mode: process event stream
    async for output_event in flux.start(source_events):
        print(output_event.to_dict())

    # DORMANT mode: direct invoke
    event = dialogue_turn_event("What should I focus on?", is_request=True)
    result = await flux.invoke(event)
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from bootstrap.types import Agent

from .events import (
    SoulEvent,
    SoulEventType,
    dialogue_turn_event,
    error_event,
    from_dialogue_output,
    from_intercept_result,
    intercept_result_event,
    is_ambient_event,
    is_request_event,
    pulse_event,
    state_snapshot_event,
)
from .persona import DialogueMode
from .soul import BudgetTier, KgentSoul

if TYPE_CHECKING:
    from protocols.terrarium.mirror import HolographicBuffer


class KgentFluxState(str, Enum):
    """Lifecycle states for KgentFlux."""

    DORMANT = "dormant"  # Not streaming, invoke() works directly
    FLOWING = "flowing"  # Streaming, invoke() becomes perturbation
    DRAINING = "draining"  # Source exhausted, draining queues
    STOPPED = "stopped"  # Stopped, can restart


@dataclass
class KgentFluxConfig:
    """Configuration for KgentFlux."""

    # Pulse emission
    pulse_enabled: bool = True
    pulse_interval: timedelta = field(default_factory=lambda: timedelta(seconds=30))

    # Processing
    buffer_size: int = 100
    perturbation_timeout: float = 30.0

    # Entropy budget (events before collapse)
    entropy_budget: float = 1000.0
    entropy_decay: float = 1.0

    # Agent identity
    agent_id: Optional[str] = None


@dataclass
class KgentFlux:
    """
    K-gent as a Flux Stream Agent.

    Wraps KgentSoul and lifts it to the streaming domain. In FLOWING mode,
    processes SoulEvents from an input stream and emits SoulEvents to output.

    Key Behaviors:
    - DIALOGUE_TURN events → dialogue() → response event
    - INTERCEPT_REQUEST events → intercept_deep() → result event
    - MODE_CHANGE events → enter_mode() → acknowledgment
    - PULSE events emitted periodically when FLOWING

    The Perturbation Principle:
    When FLOWING, invoke() injects as high-priority perturbation, ensuring
    state consistency with the stream processing.
    """

    soul: KgentSoul = field(default_factory=KgentSoul)
    config: KgentFluxConfig = field(default_factory=KgentFluxConfig)

    # Runtime state
    _state: KgentFluxState = field(default=KgentFluxState.DORMANT, init=False)
    _events_processed: int = field(default=0, init=False)
    _entropy_remaining: float = field(init=False)
    _id: str = field(init=False)

    # Queues
    _perturbation_queue: asyncio.PriorityQueue[tuple[int, str, SoulEvent]] = field(
        init=False
    )
    _output_queue: asyncio.Queue[SoulEvent] = field(init=False)

    # Task handles
    _task: Optional[asyncio.Task[None]] = field(default=None, init=False)
    _pulse_task: Optional[asyncio.Task[None]] = field(default=None, init=False)

    # Sentinel for output completion
    _SENTINEL: object = field(default_factory=object, init=False)

    # Mirror Protocol integration (optional)
    _mirror: Optional["HolographicBuffer"] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize runtime state."""
        self._entropy_remaining = self.config.entropy_budget
        self._id = self.config.agent_id or f"kgent-flux-{uuid.uuid4().hex[:8]}"
        self._perturbation_queue = asyncio.PriorityQueue()
        self._output_queue = asyncio.Queue(maxsize=self.config.buffer_size)

    # ─────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Human-readable name."""
        return f"KgentFlux({self._id})"

    @property
    def state(self) -> KgentFluxState:
        """Current lifecycle state."""
        return self._state

    @property
    def events_processed(self) -> int:
        """Number of events processed."""
        return self._events_processed

    @property
    def entropy_remaining(self) -> float:
        """Remaining entropy budget."""
        return self._entropy_remaining

    @property
    def id(self) -> str:
        """Unique identifier."""
        return self._id

    @property
    def is_running(self) -> bool:
        """Check if flux is currently processing."""
        return self._state in (KgentFluxState.FLOWING, KgentFluxState.DRAINING)

    @property
    def is_dormant(self) -> bool:
        """Check if flux is in dormant mode."""
        return self._state == KgentFluxState.DORMANT

    # ─────────────────────────────────────────────────────────────
    # Mirror Protocol Integration
    # ─────────────────────────────────────────────────────────────

    def attach_mirror(self, mirror: "HolographicBuffer") -> "KgentFlux":
        """Attach a HolographicBuffer for Terrarium observability."""
        self._mirror = mirror
        return self

    def detach_mirror(self) -> Optional["HolographicBuffer"]:
        """Detach the mirror."""
        mirror = self._mirror
        self._mirror = None
        return mirror

    @property
    def mirror(self) -> Optional["HolographicBuffer"]:
        """Optional mirror for Terrarium observability."""
        return self._mirror

    # ─────────────────────────────────────────────────────────────
    # Core: start() returns AsyncIterator[SoulEvent]
    # ─────────────────────────────────────────────────────────────

    async def start(self, source: AsyncIterator[SoulEvent]) -> AsyncIterator[SoulEvent]:
        """
        Start the flux and return the output stream.

        Args:
            source: Input stream of SoulEvents

        Yields:
            Output SoulEvents (responses, results, pulses)
        """
        if self._state not in (KgentFluxState.DORMANT, KgentFluxState.STOPPED):
            raise RuntimeError(f"Cannot start from state {self._state}")

        # Reset if restarting
        if self._state == KgentFluxState.STOPPED:
            self._events_processed = 0
            self._entropy_remaining = self.config.entropy_budget
            self._perturbation_queue = asyncio.PriorityQueue()
            self._output_queue = asyncio.Queue(maxsize=self.config.buffer_size)
            self._SENTINEL = object()
            self._state = KgentFluxState.DORMANT

        # Spawn processing task
        self._task = asyncio.create_task(
            self._process_flux(source),
            name=f"kgent-flux-{self._id}",
        )

        # Spawn pulse task if enabled
        if self.config.pulse_enabled:
            self._pulse_task = asyncio.create_task(
                self._pulse_loop(),
                name=f"kgent-pulse-{self._id}",
            )

        # Return output generator
        async for item in self._output_generator():
            yield item

    async def _output_generator(self) -> AsyncIterator[SoulEvent]:
        """Yield results from output queue."""
        while True:
            # Check for terminal state with empty queue
            if self._state in (KgentFluxState.STOPPED,):
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
                if result is self._SENTINEL:
                    break
                yield result
            except asyncio.TimeoutError:
                if self._state == KgentFluxState.STOPPED:
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
    # The Perturbation Principle: invoke() on FLOWING = inject
    # ─────────────────────────────────────────────────────────────

    async def invoke(self, input_event: SoulEvent) -> SoulEvent:
        """
        Process a SoulEvent.

        - DORMANT: Direct processing
        - FLOWING: Inject as high-priority perturbation

        Args:
            input_event: The SoulEvent to process

        Returns:
            Response SoulEvent
        """
        if self._state == KgentFluxState.DORMANT:
            # Direct processing
            return await self._process_event(input_event)

        if self._state in (KgentFluxState.FLOWING, KgentFluxState.DRAINING):
            # Perturbation: inject into stream with priority
            loop = asyncio.get_running_loop()
            result_future: asyncio.Future[SoulEvent] = loop.create_future()

            # Priority 0 = highest (perturbations before normal events)
            perturbation_id = f"pert-{uuid.uuid4().hex[:8]}"
            await self._perturbation_queue.put((0, perturbation_id, input_event))

            # Store future for result delivery
            self._pending_perturbations[perturbation_id] = result_future

            # Wait for result
            return await asyncio.wait_for(
                result_future,
                timeout=self.config.perturbation_timeout,
            )

        raise RuntimeError(f"Cannot invoke from state {self._state}")

    # Track pending perturbations
    _pending_perturbations: dict[str, asyncio.Future[SoulEvent]] = field(
        default_factory=dict, init=False
    )

    # ─────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────

    async def stop(self) -> None:
        """Stop the flux gracefully."""
        self._state = KgentFluxState.STOPPED

        # Cancel pulse task
        if self._pulse_task:
            self._pulse_task.cancel()
            try:
                await self._pulse_task
            except asyncio.CancelledError:
                pass
            self._pulse_task = None

        # Cancel pending perturbations
        while not self._perturbation_queue.empty():
            try:
                _, pert_id, _ = self._perturbation_queue.get_nowait()
                future = self._pending_perturbations.pop(pert_id, None)
                if future and not future.done():
                    future.cancel()
            except asyncio.QueueEmpty:
                break

        # Signal output completion
        try:
            self._output_queue.put_nowait(self._SENTINEL)  # type: ignore
        except asyncio.QueueFull:
            pass

        # Cancel main task
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def wait(self) -> None:
        """Wait for flux to complete."""
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def reset(self) -> None:
        """Reset flux to DORMANT state."""
        if self._state not in (KgentFluxState.STOPPED,):
            raise RuntimeError(f"Cannot reset from state {self._state}")

        self._state = KgentFluxState.DORMANT
        self._events_processed = 0
        self._entropy_remaining = self.config.entropy_budget
        self._task = None
        self._pulse_task = None

    # ─────────────────────────────────────────────────────────────
    # The Flux Processor
    # ─────────────────────────────────────────────────────────────

    async def _process_flux(self, source: AsyncIterator[SoulEvent]) -> None:
        """Process input flux, emit output flux."""
        self._state = KgentFluxState.FLOWING

        try:
            async for event in self._merged_source(source):
                # Check entropy budget
                if not self._can_continue():
                    break

                # Check if this is a perturbation
                perturbation_id: Optional[str] = None
                if isinstance(event, tuple) and len(event) == 3:
                    _, perturbation_id, event = event

                # Process the event
                try:
                    result = await self._process_event(event)

                    # Route result
                    if perturbation_id:
                        # Perturbation result goes to caller
                        future = self._pending_perturbations.pop(perturbation_id, None)
                        if future and not future.done():
                            future.set_result(result)
                    else:
                        # Normal result goes to output stream
                        await self._emit_output(result)

                except Exception as e:
                    # Emit error event
                    err_event = error_event(
                        error=str(e),
                        error_type=type(e).__name__,
                        original_event_type=event.event_type.value,
                        correlation_id=event.correlation_id,
                    )

                    if perturbation_id:
                        future = self._pending_perturbations.pop(perturbation_id, None)
                        if future and not future.done():
                            future.set_result(err_event)
                    else:
                        await self._emit_output(err_event)

                # Consume entropy
                self._consume_entropy()
                self._events_processed += 1

            # Source exhausted
            if self._state == KgentFluxState.FLOWING:
                self._state = KgentFluxState.DRAINING

        except asyncio.CancelledError:
            raise

        finally:
            if self._state != KgentFluxState.STOPPED:
                self._state = KgentFluxState.STOPPED

            # Signal output completion
            try:
                self._output_queue.put_nowait(self._SENTINEL)  # type: ignore
            except asyncio.QueueFull:
                pass

    async def _merged_source(
        self,
        source: AsyncIterator[SoulEvent],
    ) -> AsyncIterator[SoulEvent | tuple[int, str, SoulEvent]]:
        """Merge source with perturbation queue."""
        source_done = False
        source_iter = source.__aiter__()

        while not source_done or not self._perturbation_queue.empty():
            if self._state == KgentFluxState.STOPPED:
                break

            # Check perturbations (priority)
            try:
                perturbation = self._perturbation_queue.get_nowait()
                yield perturbation
                continue
            except asyncio.QueueEmpty:
                pass

            # Get from source
            if not source_done:
                try:
                    event = await asyncio.wait_for(
                        source_iter.__anext__(),
                        timeout=0.05,
                    )
                    yield event
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    source_done = True
            else:
                await asyncio.sleep(0.01)

    # ─────────────────────────────────────────────────────────────
    # Event Processing
    # ─────────────────────────────────────────────────────────────

    async def _process_event(self, event: SoulEvent) -> SoulEvent:
        """Process a single SoulEvent through KgentSoul."""
        match event.event_type:
            case SoulEventType.DIALOGUE_TURN:
                return await self._handle_dialogue_turn(event)

            case SoulEventType.INTERCEPT_REQUEST:
                return await self._handle_intercept_request(event)

            case SoulEventType.MODE_CHANGE:
                return await self._handle_mode_change(event)

            case SoulEventType.EIGENVECTOR_PROBE:
                return await self._handle_eigenvector_probe(event)

            case SoulEventType.STATE_SNAPSHOT:
                return self._handle_state_snapshot(event)

            case SoulEventType.PING:
                return event  # Pass through

            # ───────────────────────────────────────────────────────────
            # Ambient Events: The soul present, not invoked
            # These pass through enriched with soul state
            # ───────────────────────────────────────────────────────────
            case (
                SoulEventType.THOUGHT
                | SoulEventType.FEELING
                | SoulEventType.OBSERVATION
                | SoulEventType.SELF_CHALLENGE
                | SoulEventType.GRATITUDE
            ):
                return self._handle_ambient_event(event)

            case SoulEventType.PERTURBATION:
                return await self._handle_perturbation(event)

            case _:
                # Pass through unknown events
                return event

    async def _handle_dialogue_turn(self, event: SoulEvent) -> SoulEvent:
        """Handle a DIALOGUE_TURN event."""
        message = event.payload.get("message", "")
        mode_str = event.payload.get("mode")

        mode: Optional[DialogueMode] = None
        if mode_str:
            try:
                mode = DialogueMode(mode_str)
            except ValueError:
                pass

        # Call KgentSoul.dialogue()
        output = await self.soul.dialogue(
            message=message,
            mode=mode,
            budget=BudgetTier.DIALOGUE,
        )

        # Convert to SoulEvent
        return from_dialogue_output(
            output=output,
            original_message=message,
            soul_state=self.soul.manifest(),
            correlation_id=event.correlation_id,
        )

    async def _handle_intercept_request(self, event: SoulEvent) -> SoulEvent:
        """Handle an INTERCEPT_REQUEST event."""
        token_id = event.payload.get("token_id", "unknown")
        prompt = event.payload.get("prompt", "")

        # Create a mock token for intercept_deep
        class MockToken:
            def __init__(self, tid: str, p: str, sev: str, opts: list[str]) -> None:
                self.id = tid
                self.prompt = p
                self.severity = sev
                self.options = opts
                self.reason = None

        token = MockToken(
            tid=token_id,
            p=prompt,
            sev=event.payload.get("severity", "info"),
            opts=event.payload.get("options", []),
        )

        # Call KgentSoul.intercept_deep()
        result = await self.soul.intercept_deep(token)

        # Convert to SoulEvent
        return from_intercept_result(
            result=result,
            token_id=token_id,
            soul_state=self.soul.manifest(),
            correlation_id=event.correlation_id,
        )

    async def _handle_mode_change(self, event: SoulEvent) -> SoulEvent:
        """Handle a MODE_CHANGE event."""
        to_mode_str = event.payload.get("to_mode", "reflect")

        try:
            to_mode = DialogueMode(to_mode_str)
        except ValueError:
            to_mode = DialogueMode.REFLECT

        # Call KgentSoul.enter_mode()
        acknowledgment = self.soul.enter_mode(to_mode)

        return dialogue_turn_event(
            message=acknowledgment,
            mode=to_mode.value,
            is_request=False,
            correlation_id=event.correlation_id,
        )

    async def _handle_eigenvector_probe(self, event: SoulEvent) -> SoulEvent:
        """Handle an EIGENVECTOR_PROBE event."""
        eigenvectors = self.soul.eigenvectors.to_dict()

        return SoulEvent(
            event_type=SoulEventType.EIGENVECTOR_PROBE,
            timestamp=event.timestamp,
            payload={"eigenvectors": eigenvectors, "is_response": True},
            correlation_id=event.correlation_id,
        )

    def _handle_state_snapshot(self, event: SoulEvent) -> SoulEvent:
        """Handle a STATE_SNAPSHOT request."""
        state = self.soul.manifest()
        return state_snapshot_event(
            state={
                "mode": state.active_mode.value,
                "interactions_count": state.interactions_count,
                "tokens_used_session": state.tokens_used_session,
                "eigenvectors": state.eigenvectors.to_dict(),
            },
            correlation_id=event.correlation_id,
        )

    def _handle_ambient_event(self, event: SoulEvent) -> SoulEvent:
        """
        Handle an ambient event (THOUGHT, FEELING, OBSERVATION, etc.).

        Ambient events are the soul's internal life—they pass through
        enriched with current soul state but without transformation.
        This is the soul *being present*, not responding.
        """
        state = self.soul.manifest()

        # Create new event with soul state attached
        return SoulEvent(
            event_type=event.event_type,
            timestamp=event.timestamp,
            payload=event.payload,
            soul_state={
                "mode": state.active_mode.value,
                "interactions_count": state.interactions_count,
                "eigenvectors": state.eigenvectors.to_dict(),
            },
            correlation_id=event.correlation_id,
        )

    async def _handle_perturbation(self, event: SoulEvent) -> SoulEvent:
        """
        Handle a PERTURBATION event (external stimulus).

        Perturbations are external events that the soul must process.
        Unlike ambient events, perturbations may trigger responses.
        """
        source = event.payload.get("source", "unknown")
        intensity = event.payload.get("intensity", 0.5)
        # Note: data is available in event.payload["data"] for future use

        # High-intensity perturbations may trigger a thought response
        if intensity > 0.7:
            # Import here to avoid circular imports
            from .events import thought_event

            thought = thought_event(
                content=f"A strong signal from {source}...",
                depth=2,
                triggered_by=f"perturbation:{source}",
                correlation_id=event.correlation_id,
            )
            return thought

        # Lower intensity perturbations pass through enriched
        state = self.soul.manifest()
        return SoulEvent(
            event_type=event.event_type,
            timestamp=event.timestamp,
            payload=event.payload,
            soul_state={
                "mode": state.active_mode.value,
                "interactions_count": state.interactions_count,
            },
            correlation_id=event.correlation_id,
        )

    # ─────────────────────────────────────────────────────────────
    # Pulse Emission
    # ─────────────────────────────────────────────────────────────

    async def _pulse_loop(self) -> None:
        """Emit pulse events periodically."""
        interval = self.config.pulse_interval.total_seconds()

        while self._state == KgentFluxState.FLOWING:
            await asyncio.sleep(interval)

            if self._state != KgentFluxState.FLOWING:
                break

            state = self.soul.manifest()
            pulse = pulse_event(
                interactions_count=state.interactions_count,
                tokens_used_session=state.tokens_used_session,
                active_mode=state.active_mode.value,
                is_healthy=True,
            )

            await self._emit_output(pulse)

    # ─────────────────────────────────────────────────────────────
    # Output Emission
    # ─────────────────────────────────────────────────────────────

    async def _emit_output(self, event: SoulEvent) -> None:
        """Emit event to output stream and mirror."""
        # Output stream
        try:
            await asyncio.wait_for(
                self._output_queue.put(event),
                timeout=1.0,
            )
        except asyncio.TimeoutError:
            # Drop if queue full
            pass

        # Mirror (fire and forget)
        if self._mirror is not None:
            try:
                await self._mirror.reflect(event.to_dict())
            except Exception:
                pass  # Best effort

    # ─────────────────────────────────────────────────────────────
    # Entropy Management
    # ─────────────────────────────────────────────────────────────

    def _can_continue(self) -> bool:
        """Check if flux can process more events."""
        return self._entropy_remaining > 0

    def _consume_entropy(self) -> None:
        """Consume entropy for processing one event."""
        self._entropy_remaining -= self.config.entropy_decay
        self._entropy_remaining = max(0.0, self._entropy_remaining)

    # ─────────────────────────────────────────────────────────────
    # Direct Dialogue Convenience
    # ─────────────────────────────────────────────────────────────

    async def dialogue(
        self,
        message: str,
        mode: Optional[DialogueMode] = None,
    ) -> SoulEvent:
        """
        Convenience method for dialogue.

        Creates a DIALOGUE_TURN event and processes it.
        Works in both DORMANT and FLOWING modes.
        """
        event = dialogue_turn_event(
            message=message,
            mode=mode.value if mode else None,
            is_request=True,
        )

        return await self.invoke(event)

    # ─────────────────────────────────────────────────────────────
    # String Representation
    # ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"KgentFlux(id={self._id!r}, "
            f"state={self._state.value}, "
            f"events={self._events_processed}, "
            f"entropy={self._entropy_remaining:.1f})"
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_kgent_flux(
    soul: Optional[KgentSoul] = None,
    config: Optional[KgentFluxConfig] = None,
    agent_id: Optional[str] = None,
) -> KgentFlux:
    """Create a KgentFlux instance."""
    cfg = config or KgentFluxConfig()
    if agent_id:
        cfg = KgentFluxConfig(
            pulse_enabled=cfg.pulse_enabled,
            pulse_interval=cfg.pulse_interval,
            buffer_size=cfg.buffer_size,
            perturbation_timeout=cfg.perturbation_timeout,
            entropy_budget=cfg.entropy_budget,
            entropy_decay=cfg.entropy_decay,
            agent_id=agent_id,
        )

    return KgentFlux(
        soul=soul or KgentSoul(),
        config=cfg,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "KgentFlux",
    "KgentFluxConfig",
    "KgentFluxState",
    "create_kgent_flux",
]
