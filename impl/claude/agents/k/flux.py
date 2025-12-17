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
import os
import uuid
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

from agents.poly.types import Agent

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
from .llm import LLMClient, StreamingLLMResponse
from .persona import DialogueMode
from .soul import BudgetTier, KgentSoul

if TYPE_CHECKING:
    from protocols.terrarium.mirror import HolographicBuffer


# =============================================================================
# FluxEvent: Generic Streaming Event Type
# =============================================================================

T = TypeVar("T")
M = TypeVar("M")


@dataclass(frozen=True)
class FluxEvent(Generic[T]):
    """
    A streaming event in a Flux stream.

    FluxEvent represents a single item in an async stream, wrapping either:
    - Data: The actual content (e.g., text chunks)
    - Metadata: Stream metadata (e.g., token counts, completion signals)

    Type Parameters:
        T: The type of the data payload (typically str for LLM text)

    Usage:
        async for event in llm_stream_source(...):
            if event.is_data:
                print(event.value, end="", flush=True)
            elif event.is_metadata:
                print(f"\\nTotal tokens: {event.value.tokens_used}")
    """

    _kind: str  # "data" or "metadata"
    _value: Any  # T for data, StreamingLLMResponse for metadata

    @classmethod
    def data(cls, value: T) -> "FluxEvent[T]":
        """Create a data event containing a chunk of content."""
        return cls(_kind="data", _value=value)

    @classmethod
    def metadata(cls, meta: StreamingLLMResponse) -> "FluxEvent[T]":
        """Create a metadata event containing stream completion info."""
        return cls(_kind="metadata", _value=meta)

    @property
    def is_data(self) -> bool:
        """Check if this is a data event."""
        return self._kind == "data"

    @property
    def is_metadata(self) -> bool:
        """Check if this is a metadata event."""
        return self._kind == "metadata"

    @property
    def value(self) -> Any:
        """Get the event value (data or metadata)."""
        return self._value


# Default buffer size from environment or fallback
DEFAULT_STREAM_BUFFER_SIZE = int(os.environ.get("KGENT_STREAM_BUFFER_SIZE", "64"))

# WebSocket buffer size from environment
DEFAULT_WS_BUFFER_SIZE = int(os.environ.get("KGENT_WS_BUFFER_SIZE", "32"))

U = TypeVar("U")


# =============================================================================
# FluxOperator Protocol
# =============================================================================


class FluxOperator(Protocol[T, U]):
    """
    Protocol for FluxStream transformation operators.

    FluxOperators transform one stream to another while preserving
    laziness and metadata passthrough.
    """

    def __call__(
        self, source: AsyncIterator[FluxEvent[T]]
    ) -> AsyncIterator[FluxEvent[U]]:
        """Apply the operator to a source stream."""
        ...


# =============================================================================
# FluxStream: Composable Async Stream with Operators
# =============================================================================


from typing import Callable


class FluxStream(Generic[T]):
    """
    Composable async stream of FluxEvents with operators.

    FluxStream wraps an async iterator and provides chainable operators
    for transformation, filtering, and composition. All operators are lazy -
    they don't consume the source until iterated.

    Key Properties:
    - Lazy evaluation: operators don't consume until iterated
    - Metadata passthrough: metadata events pass through operators unchanged
    - Composable: operators chain to build complex pipelines

    Usage:
        stream = FluxStream(llm_source)
            .filter(lambda e: e.is_data and len(e.value.strip()) > 0)
            .map(lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e)
            .take(5)

        async for event in stream:
            print(event.value)
    """

    def __init__(self, source: AsyncIterator[FluxEvent[T]]) -> None:
        """
        Initialize FluxStream wrapping an async iterator.

        Args:
            source: The underlying async iterator of FluxEvents
        """
        self._source = source
        self._consumed = False

    def __aiter__(self) -> AsyncIterator[FluxEvent[T]]:
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> FluxEvent[T]:
        """Get next event from the stream."""
        if self._consumed:
            raise StopAsyncIteration
        try:
            return await self._source.__anext__()
        except StopAsyncIteration:
            self._consumed = True
            raise

    # ─────────────────────────────────────────────────────────────
    # C14: Stream Operators
    # ─────────────────────────────────────────────────────────────

    def map(self, fn: Callable[[FluxEvent[T]], FluxEvent[U]]) -> "FluxStream[U]":
        """
        Transform data events, pass metadata through unchanged.

        Args:
            fn: Function to apply to each event. Should return FluxEvent[U].
                For data events, transform the value. For metadata, pass through.

        Returns:
            New FluxStream with transformed events.

        Example:
            stream.map(lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e)
        """
        source = self._source

        async def mapped() -> AsyncIterator[FluxEvent[U]]:
            async for event in source:
                if event.is_metadata:
                    # Metadata passes through unchanged
                    yield event  # type: ignore[misc]
                else:
                    yield fn(event)

        return FluxStream(mapped())

    def filter(self, predicate: Callable[[FluxEvent[T]], bool]) -> "FluxStream[T]":
        """
        Filter events based on a predicate, metadata always passes through.

        Args:
            predicate: Function that returns True to keep an event.
                       Metadata events always pass through regardless of predicate.

        Returns:
            New FluxStream with filtered events.

        Example:
            stream.filter(lambda e: e.is_data and len(e.value.strip()) > 0)
        """
        source = self._source

        async def filtered() -> AsyncIterator[FluxEvent[T]]:
            async for event in source:
                if event.is_metadata:
                    # Metadata always passes through
                    yield event
                elif predicate(event):
                    yield event

        return FluxStream(filtered())

    def take(self, n: int) -> "FluxStream[T]":
        """
        Limit stream to first n data events, metadata always passes through.

        Args:
            n: Maximum number of data events to emit.
               Metadata events don't count toward the limit.

        Returns:
            New FluxStream limited to n data events.

        Example:
            stream.take(5)  # Only first 5 data events
        """
        source = self._source

        async def taken() -> AsyncIterator[FluxEvent[T]]:
            count = 0
            async for event in source:
                if event.is_metadata:
                    # Metadata always passes through
                    yield event
                elif count < n:
                    count += 1
                    yield event
                # Data events after n are dropped

        return FluxStream(taken())

    def tap(self, fn: Callable[[FluxEvent[T]], None]) -> "FluxStream[T]":
        """
        Perform side effects without modifying the stream.

        Args:
            fn: Function called with each event for side effects.
                Return value is ignored.

        Returns:
            Same FluxStream (events unchanged).

        Example:
            stream.tap(lambda e: print(e.value) if e.is_data else None)
        """
        source = self._source

        async def tapped() -> AsyncIterator[FluxEvent[T]]:
            async for event in source:
                fn(event)
                yield event

        return FluxStream(tapped())

    # ─────────────────────────────────────────────────────────────
    # C15: Stream Composition
    # ─────────────────────────────────────────────────────────────

    @classmethod
    def chain(cls, *sources: "FluxStream[T]") -> "FluxStream[T]":
        """
        Concatenate multiple streams sequentially.

        Streams are consumed one after another. When the first stream
        exhausts, the second begins, etc.

        Args:
            *sources: FluxStreams to concatenate in order.

        Returns:
            New FluxStream that yields all events from all sources in order.

        Example:
            FluxStream.chain(stream1, stream2, stream3)
        """

        async def chained() -> AsyncIterator[FluxEvent[T]]:
            for source in sources:
                async for event in source:
                    yield event

        return cls(chained())

    @classmethod
    def merge(cls, *sources: "FluxStream[T]") -> "FluxStream[T]":
        """
        Interleave multiple streams (first-available wins).

        Events from all sources are yielded as they arrive.
        Metadata events from all streams pass through; token counts
        are aggregated in a final metadata event.

        Args:
            *sources: FluxStreams to merge.

        Returns:
            New FluxStream that interleaves events from all sources.

        Example:
            FluxStream.merge(stream1, stream2)  # Events interleaved
        """

        async def merged() -> AsyncIterator[FluxEvent[T]]:
            # Track metadata for aggregation
            total_tokens = 0
            metadata_count = 0

            # Create tasks for each source
            pending: dict[asyncio.Task[tuple[int, FluxEvent[T] | None]], int] = {}
            source_iters: list[AsyncIterator[FluxEvent[T]]] = [
                s.__aiter__() for s in sources
            ]
            exhausted: set[int] = set()

            def create_task(idx: int) -> asyncio.Task[tuple[int, FluxEvent[T] | None]]:
                async def get_next() -> tuple[int, FluxEvent[T] | None]:
                    try:
                        event = await source_iters[idx].__anext__()
                        return (idx, event)
                    except StopAsyncIteration:
                        return (idx, None)

                task = asyncio.create_task(get_next())
                pending[task] = idx
                return task

            # Start initial tasks for all sources
            for i in range(len(source_iters)):
                create_task(i)

            # Process until all sources exhausted
            while pending:
                done, _ = await asyncio.wait(
                    pending.keys(), return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    _ = pending.pop(task)  # Remove from tracking
                    result_idx, event = task.result()

                    if event is None:
                        # Source exhausted
                        exhausted.add(result_idx)
                    elif event.is_metadata:
                        # Aggregate metadata
                        metadata_count += 1
                        if hasattr(event.value, "tokens_used"):
                            total_tokens += event.value.tokens_used
                        # Don't yield individual metadata; we'll yield aggregate at end
                    else:
                        # Yield data event
                        yield event
                        # Request next from this source
                        if result_idx not in exhausted:
                            create_task(result_idx)

            # Yield aggregate metadata if any were collected
            if metadata_count > 0:
                aggregate_meta = StreamingLLMResponse(
                    text="",
                    tokens_used=total_tokens,
                    model="merged",
                    raw_metadata={"merged_sources": len(sources)},
                )
                yield FluxEvent.metadata(aggregate_meta)

        return cls(merged())

    def zip(self, other: "FluxStream[T]") -> "FluxStream[tuple[T, T]]":
        """
        Pair events from two streams.

        Only data events are paired. Metadata from both streams
        passes through. Stops when either stream exhausts.

        Args:
            other: FluxStream to zip with.

        Returns:
            New FluxStream of paired events.

        Example:
            stream1.zip(stream2)  # Pairs (event1, event2)
        """
        source = self._source
        other_source = other._source

        async def zipped() -> AsyncIterator[FluxEvent[tuple[T, T]]]:
            # Buffer for pending data events
            source_buffer: list[FluxEvent[T]] = []
            other_buffer: list[FluxEvent[T]] = []

            async def fill_buffer(
                src: AsyncIterator[FluxEvent[T]], buf: list[FluxEvent[T]]
            ) -> FluxEvent[T] | None:
                """Get next data event, yielding metadata."""
                async for event in src:
                    if event.is_metadata:
                        # Can't yield from nested function; return for handling
                        return event
                    else:
                        buf.append(event)
                        return None
                return None  # Exhausted

            source_iter = source.__aiter__()
            other_iter = other_source.__aiter__()
            source_done = False
            other_done = False

            while not (source_done and other_done):
                # Fill buffers until we have at least one data event each
                while not source_buffer and not source_done:
                    try:
                        event = await source_iter.__anext__()
                        if event.is_metadata:
                            yield event  # type: ignore[misc]
                        else:
                            source_buffer.append(event)
                    except StopAsyncIteration:
                        source_done = True

                while not other_buffer and not other_done:
                    try:
                        event = await other_iter.__anext__()
                        if event.is_metadata:
                            yield event  # type: ignore[misc]
                        else:
                            other_buffer.append(event)
                    except StopAsyncIteration:
                        other_done = True

                # Pair events if both buffers have data
                if source_buffer and other_buffer:
                    e1 = source_buffer.pop(0)
                    e2 = other_buffer.pop(0)
                    paired: tuple[T, T] = (e1.value, e2.value)
                    yield FluxEvent.data(paired)
                elif source_done or other_done:
                    # One stream exhausted, stop zipping
                    break

        return FluxStream(zipped())

    async def collect(self) -> list[T]:
        """
        Materialize stream to a list of data values.

        Consumes the entire stream and returns all data values.
        Metadata events are discarded.

        Returns:
            List of data values from the stream.

        Example:
            values = await stream.collect()
        """
        result: list[T] = []
        async for event in self:
            if event.is_data:
                result.append(event.value)
        return result

    # ─────────────────────────────────────────────────────────────
    # C20: Stream Pipe Composition
    # ─────────────────────────────────────────────────────────────

    def pipe(
        self,
        *operators: Callable[["FluxStream[Any]"], "FluxStream[Any]"],
    ) -> "FluxStream[Any]":
        """
        Apply a sequence of operators to this stream.

        Operators are functions that transform FluxStream[A] -> FluxStream[B].
        The pipe method composes operators sequentially, enabling functional
        pipeline composition.

        Composition is associative:
            stream.pipe(f, g) == stream.pipe(f).pipe(g)

        Args:
            *operators: Functions that transform FluxStream to FluxStream.
                       Each operator receives the stream from the previous
                       stage and returns a transformed stream.

        Returns:
            The transformed FluxStream after all operators have been applied.

        Example:
            # Define operators as functions
            filter_empty = lambda s: s.filter(lambda e: e.is_data and e.value.strip())
            take_n = lambda n: lambda s: s.take(n)
            log_chunks = lambda s: s.tap(lambda e: print(e.value) if e.is_data else None)

            # Compose pipeline
            result = await (
                source
                .pipe(filter_empty, take_n(5), log_chunks)
                .collect()
            )

            # Equivalent to:
            result = await (
                source
                .pipe(filter_empty)
                .pipe(take_n(5))
                .pipe(log_chunks)
                .collect()
            )
        """
        result: FluxStream[Any] = self
        for op in operators:
            result = op(result)
        return result


# Type alias for backward compatibility
FluxStreamAlias = AsyncIterator[FluxEvent[str]]


# =============================================================================
# LLMStreamSource: Flux Source Wrapping LLM Streaming
# =============================================================================


class LLMStreamSource:
    """
    Wraps an LLMClient's generate_stream() as a Flux source.

    Converts the raw LLM stream (yielding str | StreamingLLMResponse) into
    FluxEvent[str] events for integration with the Flux streaming system.

    Features:
    - AsyncIterator[FluxEvent[str]] interface
    - Backpressure handling via async queue with configurable buffer size
    - Emits FluxEvent.data(chunk) for text deltas
    - Emits FluxEvent.metadata(StreamingLLMResponse) on completion

    Usage:
        source = LLMStreamSource(
            client=llm_client,
            system="You are K-gent...",
            user="What should I focus on?",
        )

        async for event in source:
            if event.is_data:
                print(event.value, end="", flush=True)
            elif event.is_metadata:
                print(f"\\n[{event.value.tokens_used} tokens]")
    """

    def __init__(
        self,
        client: LLMClient,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        buffer_size: Optional[int] = None,
    ) -> None:
        """
        Initialize the LLM stream source.

        Args:
            client: The LLM client to use for generation
            system: System prompt for the LLM
            user: User message/prompt
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            buffer_size: Async queue buffer size for backpressure handling.
                        Defaults to KGENT_STREAM_BUFFER_SIZE env var or 64.
        """
        self._client = client
        self._system = system
        self._user = user
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._buffer_size = buffer_size or DEFAULT_STREAM_BUFFER_SIZE

        # Internal state
        self._queue: asyncio.Queue[FluxEvent[str] | None] = asyncio.Queue(
            maxsize=self._buffer_size
        )
        self._producer_task: Optional[asyncio.Task[None]] = None
        self._started = False
        self._completed = False

    async def _produce(self) -> None:
        """Producer coroutine that reads from LLM and enqueues events."""
        try:
            async for item in self._client.generate_stream(
                system=self._system,
                user=self._user,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            ):
                if isinstance(item, str):
                    event: FluxEvent[str] = FluxEvent.data(item)
                else:
                    # StreamingLLMResponse
                    event = FluxEvent.metadata(item)

                await self._queue.put(event)
        except Exception as e:
            # On error, create a metadata event with empty response
            # This ensures the consumer knows the stream ended
            error_meta = StreamingLLMResponse(
                text="",
                tokens_used=0,
                model="error",
                raw_metadata={"error": str(e)},
            )
            await self._queue.put(FluxEvent.metadata(error_meta))
        finally:
            # Signal completion
            await self._queue.put(None)

    def __aiter__(self) -> AsyncIterator[FluxEvent[str]]:
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> FluxEvent[str]:
        """Get next event from the stream."""
        if not self._started:
            self._started = True
            self._producer_task = asyncio.create_task(
                self._produce(), name="llm-stream-producer"
            )

        if self._completed:
            raise StopAsyncIteration

        event = await self._queue.get()
        if event is None:
            self._completed = True
            raise StopAsyncIteration

        return event

    async def cancel(self) -> None:
        """Cancel the stream source."""
        if self._producer_task and not self._producer_task.done():
            self._producer_task.cancel()
            try:
                await self._producer_task
            except asyncio.CancelledError:
                pass

    @property
    def is_complete(self) -> bool:
        """Check if the stream has completed."""
        return self._completed


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
        """Handle a DIALOGUE_TURN event with streaming support."""
        message = event.payload.get("message", "")
        mode_str = event.payload.get("mode")
        correlation_id = event.correlation_id

        mode: Optional[DialogueMode] = None
        if mode_str:
            try:
                mode = DialogueMode(mode_str)
            except ValueError:
                pass

        # Track chunks for streaming
        chunk_index = 0

        def on_chunk(chunk_text: str) -> None:
            """Emit streaming chunk event via mirror."""
            nonlocal chunk_index

            # Create chunk event
            chunk_event = dialogue_turn_event(
                message=message,
                mode=mode.value if mode else None,
                is_request=False,
                correlation_id=correlation_id,
                soul_state={
                    "chunk": chunk_text,
                    "chunk_index": chunk_index,
                    "is_final": False,
                },
            )

            # Emit to mirror if attached (fire-and-forget)
            if self._mirror is not None:
                import asyncio

                # Schedule async emit without blocking
                asyncio.create_task(self._mirror.reflect(chunk_event.to_dict()))

            chunk_index += 1

        # Call KgentSoul.dialogue() with streaming callback
        output = await self.soul.dialogue(
            message=message,
            mode=mode,
            budget=BudgetTier.DIALOGUE,
            on_chunk=on_chunk,
        )

        # Create final response event
        final_event = from_dialogue_output(
            output=output,
            original_message=message,
            soul_state=self.soul.manifest(),
            correlation_id=correlation_id,
        )

        # Add streaming metadata to final event payload
        # Note: SoulEvent is frozen, so we create a new one with enriched payload
        enriched_payload = dict(final_event.payload)
        enriched_payload["is_final"] = True
        enriched_payload["total_chunks"] = chunk_index

        return SoulEvent(
            event_type=final_event.event_type,
            timestamp=final_event.timestamp,
            payload=enriched_payload,
            soul_state=final_event.soul_state,
            correlation_id=final_event.correlation_id,
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
    # Core flux types
    "KgentFlux",
    "KgentFluxConfig",
    "KgentFluxState",
    "create_kgent_flux",
    # Streaming types (C11)
    "FluxEvent",
    "FluxStream",
    "FluxStreamAlias",
    "FluxOperator",
    "LLMStreamSource",
    "DEFAULT_STREAM_BUFFER_SIZE",
    "DEFAULT_WS_BUFFER_SIZE",
]
