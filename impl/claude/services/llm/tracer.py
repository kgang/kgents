"""
LLM Invocation Tracer - Captures every LLM call with full causality.

More granular than Datadog/Splunk because we capture:
- Causal chain (parent → this → children)
- Ripple effects (what crystals changed)
- Galois coherence (semantic quality)

Usage:
    >>> tracer = LLMTracer(universe, galois)
    >>>
    >>> async with tracer.trace(
    ...     causal_parent_id=parent_mark_id,
    ...     triggered_by="user_input",
    ... ) as ctx:
    ...     # Set request details
    ...     ctx.set_request(
    ...         model="claude-3.5-sonnet",
    ...         prompt="Explain kgents",
    ...         system="You are a helpful assistant",
    ...     )
    ...
    ...     # Make LLM call
    ...     response = await llm.generate(prompt)
    ...
    ...     # Record response
    ...     ctx.set_response(response, tokens=(100, 50))
    ...
    ...     # Record state changes
    ...     ctx.add_crystal_created("crystal-123")
    ...     ctx.add_state_change(StateChange(...))
    ...
    >>> # Trace automatically stored on context exit

Example with error handling:
    >>> async with tracer.trace(triggered_by="agent_decision") as ctx:
    ...     ctx.set_request("claude-3.5-sonnet", "Question")
    ...     try:
    ...         response = await llm.generate(...)
    ...         ctx.set_response(response)
    ...     except Exception as e:
    ...         ctx.set_error(str(e))
    ...         raise
"""

import hashlib
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, AsyncIterator

from agents.d.galois import GaloisLossComputer
from agents.d.schemas.llm_trace import LLMInvocationMark, StateChange
from agents.d.universe import Query, Universe, get_universe

logger = logging.getLogger(__name__)


class LLMTraceContext:
    """
    Context for building an LLM invocation trace.

    Accumulates trace data during invocation, computes metrics on exit.

    Fields are filled progressively:
    1. set_request() - before LLM call
    2. set_response() - after LLM call
    3. add_* methods - during processing
    4. finalize() - computes loss, creates mark

    Example:
        >>> ctx = LLMTraceContext(tracer, causal_parent_id="mark-123")
        >>> ctx.set_request("claude-3.5-sonnet", "Hello")
        >>> ctx.set_response("Hi there!", tokens=(10, 5))
        >>> ctx.add_crystal_created("crystal-456")
        >>> mark = await ctx.finalize()
    """

    def __init__(
        self,
        tracer: "LLMTracer",
        causal_parent_id: str | None,
        triggered_by: str,
        invocation_type: str,
        tags: set[str],
    ):
        """
        Initialize trace context.

        Args:
            tracer: Parent LLMTracer instance
            causal_parent_id: ID of mark that triggered this
            triggered_by: Trigger source
            invocation_type: Type of invocation
            tags: Initial tags
        """
        self._tracer = tracer
        self._id = f"llm-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        self._start_time = datetime.now(UTC)

        # Causality
        self._causal_parent_id = causal_parent_id
        self._triggered_by = triggered_by
        self._invocation_type = invocation_type
        self._tags = tags

        # Request fields (set via set_request)
        self._model: str | None = None
        self._provider: str = "anthropic"
        self._user_prompt: str | None = None
        self._system_prompt: str | None = None
        self._system_prompt_hash: str | None = None
        self._temperature: float = 0.0

        # Response fields (set via set_response)
        self._response: str | None = None
        self._prompt_tokens: int = 0
        self._completion_tokens: int = 0
        self._latency_ms: int = 0

        # State changes (accumulated via add_*)
        self._crystals_created: list[str] = []
        self._crystals_modified: list[str] = []
        self._edges_created: list[str] = []
        self._state_changes: list[StateChange] = []

        # Error handling
        self._error: str | None = None
        self._success: bool = True

    @property
    def id(self) -> str:
        """Get trace ID."""
        return self._id

    def set_request(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        provider: str = "anthropic",
        temperature: float = 0.0,
    ) -> None:
        """
        Record request details.

        Args:
            model: Model name (e.g., "claude-3.5-sonnet")
            prompt: User prompt
            system: System prompt (optional)
            provider: Provider name (default: "anthropic")
            temperature: Temperature parameter
        """
        self._model = model
        self._user_prompt = prompt
        self._system_prompt = system
        self._provider = provider
        self._temperature = temperature

        # Hash system prompt for deduplication
        if system:
            self._system_prompt_hash = hashlib.sha256(system.encode()).hexdigest()[:16]
        else:
            self._system_prompt_hash = "none"

    def set_response(
        self,
        response: str,
        tokens: tuple[int, int] | None = None,
    ) -> None:
        """
        Record response details.

        Args:
            response: LLM response text
            tokens: (prompt_tokens, completion_tokens) if known
        """
        self._response = response

        if tokens:
            self._prompt_tokens, self._completion_tokens = tokens
        else:
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            if self._user_prompt:
                self._prompt_tokens = len(self._user_prompt) // 4
            self._completion_tokens = len(response) // 4

        # Compute latency
        elapsed = datetime.now(UTC) - self._start_time
        self._latency_ms = int(elapsed.total_seconds() * 1000)

    def add_crystal_created(self, crystal_id: str) -> None:
        """Record a crystal created by this invocation."""
        self._crystals_created.append(crystal_id)

    def add_crystal_modified(self, crystal_id: str) -> None:
        """Record a crystal modified by this invocation."""
        self._crystals_modified.append(crystal_id)

    def add_edge_created(self, edge_id: str) -> None:
        """Record an edge created by this invocation."""
        self._edges_created.append(edge_id)

    def add_state_change(self, change: StateChange) -> None:
        """Record a state change."""
        self._state_changes.append(change)

    def set_error(self, error: str) -> None:
        """Record an error."""
        self._error = error
        self._success = False

    async def finalize(self) -> LLMInvocationMark:
        """
        Compute final metrics and create LLMInvocationMark.

        Computes:
        - Galois loss (if galois computer available)
        - Total tokens
        - Final latency

        Returns:
            Completed LLMInvocationMark
        """
        # Ensure request was set
        if self._model is None or self._user_prompt is None:
            raise ValueError("set_request() must be called before finalize()")

        # Ensure response was set (unless error)
        if self._response is None and self._success:
            raise ValueError("set_response() must be called before finalize() for successful calls")

        # Compute Galois loss
        galois_loss = 0.0
        if self._tracer._galois and self._response:
            try:
                galois_loss = await self._tracer._galois.compute(self._response)
            except Exception as e:
                logger.warning(f"Failed to compute Galois loss: {e}")

        coherence = 1.0 - galois_loss

        # Create mark
        mark = LLMInvocationMark(
            id=self._id,
            timestamp=self._start_time,
            model=self._model,
            provider=self._provider,
            prompt_tokens=self._prompt_tokens,
            completion_tokens=self._completion_tokens,
            total_tokens=self._prompt_tokens + self._completion_tokens,
            latency_ms=self._latency_ms,
            temperature=self._temperature,
            system_prompt_hash=self._system_prompt_hash or "none",
            user_prompt=self._user_prompt,
            response=self._response or "",
            causal_parent_id=self._causal_parent_id,
            triggered_by=self._triggered_by,
            state_changes=tuple(self._state_changes),
            crystals_created=tuple(self._crystals_created),
            crystals_modified=tuple(self._crystals_modified),
            edges_created=tuple(self._edges_created),
            galois_loss=galois_loss,
            coherence=coherence,
            invocation_type=self._invocation_type,
            error=self._error,
            success=self._success,
            tags=frozenset(self._tags),
        )

        return mark


class LLMTracer:
    """
    Traces LLM invocations and stores as LLMInvocationMarks.

    Every LLM call is witnessed with full causality:
    - Request/response
    - Causal parent (what triggered this)
    - Ripple effects (what changed)
    - Galois loss (semantic coherence)

    This is MORE granular than traditional observability because we track
    the full causal chain and semantic quality, not just timing.

    Usage:
        >>> tracer = LLMTracer(universe, galois)
        >>>
        >>> async with tracer.trace(
        ...     causal_parent_id="mark-123",
        ...     triggered_by="user_input",
        ... ) as ctx:
        ...     ctx.set_request("claude-3.5-sonnet", "Hello")
        ...     response = await llm.generate("Hello")
        ...     ctx.set_response(response)
        ...     ctx.add_crystal_created("crystal-456")

    Querying:
        >>> # Get recent traces
        >>> traces = await tracer.query_traces(limit=50)
        >>>
        >>> # Get causal chain
        >>> chain = await tracer.get_causal_chain("llm-123")
        >>>
        >>> # Get ripple effects
        >>> effects = await tracer.get_ripple_effects("llm-123")
    """

    def __init__(
        self,
        universe: Universe | None = None,
        galois: GaloisLossComputer | None = None,
    ):
        """
        Initialize LLM tracer.

        Args:
            universe: Universe instance (uses singleton if None)
            galois: Galois loss computer (optional)
        """
        self._universe = universe or get_universe()
        self._galois = galois

        # Register schema
        from agents.d.schemas.llm_trace import LLM_INVOCATION_SCHEMA
        self._universe.register_schema(LLM_INVOCATION_SCHEMA)

    @asynccontextmanager
    async def trace(
        self,
        causal_parent_id: str | None = None,
        triggered_by: str = "unknown",
        invocation_type: str = "generation",
        tags: set[str] | None = None,
    ) -> AsyncIterator[LLMTraceContext]:
        """
        Context manager for tracing an LLM invocation.

        Args:
            causal_parent_id: ID of mark that triggered this
            triggered_by: Trigger source ("user_input", "agent_decision", etc.)
            invocation_type: Type of invocation ("generation", "analysis", etc.)
            tags: Additional tags for filtering

        Yields:
            LLMTraceContext for accumulating trace data

        Example:
            >>> async with tracer.trace(triggered_by="user_input") as ctx:
            ...     ctx.set_request("claude-3.5-sonnet", "Hello")
            ...     response = await llm.generate("Hello")
            ...     ctx.set_response(response)
        """
        ctx = LLMTraceContext(
            tracer=self,
            causal_parent_id=causal_parent_id,
            triggered_by=triggered_by,
            invocation_type=invocation_type,
            tags=tags or set(),
        )

        error_occurred = False
        try:
            yield ctx
        except Exception as e:
            # Record error but re-raise
            if ctx._error is None:  # Only set if not already set explicitly
                ctx.set_error(str(e))
            error_occurred = True
            raise
        finally:
            # Store trace regardless of success/failure
            try:
                mark = await ctx.finalize()
                await self.store_trace(mark)
                logger.info(
                    f"Stored LLM trace {mark.id}: {mark.model} "
                    f"({mark.total_tokens} tokens, {mark.latency_ms}ms, "
                    f"loss={mark.galois_loss:.3f})"
                )
            except Exception as e:
                logger.error(f"Failed to store LLM trace: {e}")

    async def store_trace(self, mark: LLMInvocationMark) -> str:
        """
        Store completed trace in Universe.

        Args:
            mark: LLMInvocationMark to store

        Returns:
            Trace ID
        """
        return await self._universe.store(mark, "llm.invocation")

    async def get_trace(self, id: str) -> LLMInvocationMark | None:
        """
        Retrieve trace by ID.

        Args:
            id: Trace ID (the LLMInvocationMark.id, not datum ID)

        Returns:
            LLMInvocationMark or None if not found
        """
        # Query all traces and filter by ID
        # Note: For production, consider adding ID indexing to backend
        query = Query(
            schema="llm.invocation",
            limit=1000,  # Reasonable upper bound
        )
        results = await self._universe.query(query)

        # Find matching trace
        for result in results:
            if isinstance(result, LLMInvocationMark) and result.id == id:
                return result

        return None

    async def query_traces(
        self,
        limit: int = 50,
        after: float | None = None,
        prefix: str | None = None,
    ) -> list[LLMInvocationMark]:
        """
        Query traces with filters.

        Args:
            limit: Maximum traces to return
            after: Filter by timestamp > after (Unix timestamp)
            prefix: Filter by ID prefix

        Returns:
            List of LLMInvocationMark objects
        """
        query = Query(
            schema="llm.invocation",
            limit=limit,
            after=after,
            prefix=prefix,
        )
        results = await self._universe.query(query)

        # Filter to only LLMInvocationMark instances
        return [r for r in results if isinstance(r, LLMInvocationMark)]

    async def get_causal_chain(self, id: str) -> list[LLMInvocationMark]:
        """
        Get full causal chain for a trace.

        Walks up the causal_parent_id chain to root.

        Args:
            id: Trace ID to start from

        Returns:
            List of traces from root to current (chronological order)
        """
        chain: list[LLMInvocationMark] = []
        visited: set[str] = set()
        current_id: str | None = id

        # Walk up to root
        while current_id and current_id not in visited:
            visited.add(current_id)
            trace = await self.get_trace(current_id)
            if trace is None:
                break

            chain.append(trace)
            current_id = trace.causal_parent_id

        # Reverse to get chronological order (root → current)
        return list(reversed(chain))

    async def get_causal_children(self, id: str) -> list[LLMInvocationMark]:
        """
        Get all traces that were triggered by this trace.

        Args:
            id: Parent trace ID

        Returns:
            List of child traces
        """
        # Query all traces and filter by causal_parent_id
        # Note: This is inefficient for large datasets
        # Consider adding causal_parent_id indexing to backend
        all_traces = await self.query_traces(limit=1000)
        return [t for t in all_traces if t.causal_parent_id == id]

    async def get_ripple_effects(self, id: str) -> list[StateChange]:
        """
        Get all state changes triggered by a trace.

        Includes both direct state changes and cascaded changes from children.

        Args:
            id: Trace ID

        Returns:
            List of StateChange objects
        """
        effects: list[StateChange] = []

        # Get trace
        trace = await self.get_trace(id)
        if trace:
            effects.extend(trace.state_changes)

            # Get children and their state changes (cascade)
            children = await self.get_causal_children(id)
            for child in children:
                effects.extend(child.state_changes)

        return effects

    async def get_traces_by_crystal(self, crystal_id: str) -> list[LLMInvocationMark]:
        """
        Get all traces that created or modified a crystal.

        Args:
            crystal_id: Crystal ID to search for

        Returns:
            List of traces that touched this crystal
        """
        all_traces = await self.query_traces(limit=1000)
        return [
            t
            for t in all_traces
            if crystal_id in t.crystals_created or crystal_id in t.crystals_modified
        ]

    async def compute_aggregate_loss(self, traces: list[LLMInvocationMark]) -> float:
        """
        Compute average Galois loss across traces.

        Args:
            traces: List of traces to aggregate

        Returns:
            Average loss (0.0 if no traces)
        """
        if not traces:
            return 0.0

        total_loss = sum(t.galois_loss for t in traces)
        return total_loss / len(traces)

    async def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about LLM traces.

        Returns:
            Dict with counts, averages, etc.
        """
        traces = await self.query_traces(limit=1000)

        if not traces:
            return {
                "total_traces": 0,
                "total_tokens": 0,
                "average_latency_ms": 0,
                "average_loss": 0.0,
                "success_rate": 0.0,
            }

        total_tokens = sum(t.total_tokens for t in traces)
        total_latency = sum(t.latency_ms for t in traces)
        total_loss = sum(t.galois_loss for t in traces)
        successful = sum(1 for t in traces if t.success)

        return {
            "total_traces": len(traces),
            "total_tokens": total_tokens,
            "average_latency_ms": total_latency // len(traces),
            "average_loss": total_loss / len(traces),
            "success_rate": successful / len(traces),
            "average_tokens_per_call": total_tokens // len(traces),
        }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "LLMTracer",
    "LLMTraceContext",
]
