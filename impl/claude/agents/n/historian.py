"""
The Historian: Invisible Crystal Collector.

The Historian records agent executions as SemanticTraces (crystals).
Key property: Agents are UNAWARE of the Historian. Recording is invisible.

Philosophy:
    Story is a Read-Time projection, not a Write-Time artifact.
    The Historian is silent. The Bard speaks.
"""

from __future__ import annotations

import hashlib
import json
from contextvars import ContextVar
from datetime import datetime, timezone
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable
from uuid import uuid4

from .types import Action, Determinism, SemanticTrace, TraceContext

if TYPE_CHECKING:
    from .store import CrystalStore


@runtime_checkable
class Traceable(Protocol):
    """Protocol for agents that can be traced."""

    @property
    def name(self) -> str:
        """Agent name/identifier."""
        ...

    @property
    def genus(self) -> str:
        """Agent genus (B, G, J, etc.)."""
        ...


class Historian:
    """
    The invisible recorder. Creates crystals, not stories.

    Implementation via ContextVar—the agent is unaware of observation.
    The Historian operates at the runtime level, not the agent level.

    Usage:
        store = MemoryCrystalStore()
        historian = Historian(store)

        # Begin recording (called by runtime, not agent)
        ctx = historian.begin_trace(agent, input_data)

        # ... agent executes ...

        # End recording
        crystal = historian.end_trace(ctx, "INVOKE", outputs, Determinism.PROBABILISTIC)

    For automatic tracing, use the HistorianTap with W-gent wire protocol.
    """

    # Thread-local trace context for nested calls
    _current_trace: ContextVar[str | None] = ContextVar("current_trace", default=None)

    def __init__(self, store: CrystalStore):
        """
        Initialize the Historian.

        Args:
            store: Where to persist crystals (MemoryCrystalStore, DgentCrystalStore, etc.)
        """
        self.store = store

    def begin_trace(
        self,
        agent: Traceable | Any,
        input_data: Any,
    ) -> TraceContext:
        """
        Begin recording a trace.

        Called by the RUNTIME, not the agent. The agent doesn't know
        it's being recorded.

        Args:
            agent: The agent being traced (must have name and genus)
            input_data: The input to the agent

        Returns:
            TraceContext to pass to end_trace or abort_trace
        """
        trace_id = str(uuid4())
        parent_id = self._current_trace.get()

        # Set current trace for nested calls
        self._current_trace.set(trace_id)

        # Get agent info
        if isinstance(agent, Traceable):
            agent_id = agent.name
            agent_genus = agent.genus
        else:
            agent_id = getattr(agent, "name", str(type(agent).__name__))
            agent_genus = getattr(agent, "genus", "unknown")

        # Serialize and hash input
        input_snapshot = self._serialize(input_data)
        input_hash = self._hash(input_snapshot)

        return TraceContext(
            trace_id=trace_id,
            parent_id=parent_id,
            agent_id=agent_id,
            agent_genus=agent_genus,
            input_snapshot=input_snapshot,
            input_hash=input_hash,
            start_time=datetime.now(timezone.utc),
        )

    def end_trace(
        self,
        ctx: TraceContext,
        action: str,
        outputs: dict[str, Any],
        determinism: Determinism | None = None,
    ) -> SemanticTrace:
        """
        Complete and store a trace.

        Args:
            ctx: Context from begin_trace
            action: The action performed (INVOKE, GENERATE, etc.)
            outputs: The outputs from the agent
            determinism: How reproducible this action is (auto-detected if None)

        Returns:
            The completed SemanticTrace (crystal)
        """
        # Restore parent trace context
        self._current_trace.set(ctx.parent_id)

        # Auto-detect determinism if not provided
        if determinism is None:
            determinism = Action.classify_determinism(action)

        # Build the crystal
        crystal = SemanticTrace(
            trace_id=ctx.trace_id,
            parent_id=ctx.parent_id,
            timestamp=ctx.start_time,
            agent_id=ctx.agent_id,
            agent_genus=ctx.agent_genus,
            action=action,
            inputs=self._extract_semantic_inputs(ctx.input_snapshot),
            outputs=outputs,
            input_hash=ctx.input_hash,
            input_snapshot=ctx.input_snapshot,
            output_hash=self._hash(self._serialize(outputs)),
            gas_consumed=self._estimate_gas(ctx, outputs),
            duration_ms=self._duration_ms(ctx),
            vector=None,  # Computed later by L-gent
            determinism=determinism,
            metadata={},
        )

        # Store the crystal
        self.store.store(crystal)
        return crystal

    def abort_trace(
        self,
        ctx: TraceContext,
        error: Exception | str,
    ) -> SemanticTrace:
        """
        Record a failed trace.

        Args:
            ctx: Context from begin_trace
            error: The error that occurred

        Returns:
            The error trace (crystal)
        """
        # Restore parent trace context
        self._current_trace.set(ctx.parent_id)

        # Build error details
        if isinstance(error, Exception):
            error_type = type(error).__name__
            error_msg = str(error)
            error_repr = repr(error)
        else:
            error_type = "Error"
            error_msg = str(error)
            error_repr = str(error)

        crystal = SemanticTrace(
            trace_id=ctx.trace_id,
            parent_id=ctx.parent_id,
            timestamp=ctx.start_time,
            agent_id=ctx.agent_id,
            agent_genus=ctx.agent_genus,
            action=Action.ERROR,
            inputs=self._extract_semantic_inputs(ctx.input_snapshot),
            outputs={"error": error_msg, "type": error_type},
            input_hash=ctx.input_hash,
            input_snapshot=ctx.input_snapshot,
            output_hash=None,
            gas_consumed=0,
            duration_ms=self._duration_ms(ctx),
            vector=None,
            determinism=Determinism.CHAOTIC,
            metadata={"exception": error_repr},
        )

        self.store.store(crystal)
        return crystal

    def get_current_trace_id(self) -> str | None:
        """Get the current trace ID (for nested calls)."""
        return self._current_trace.get()

    def reset_context(self) -> None:
        """Reset the trace context (for testing)."""
        self._current_trace.set(None)

    def _serialize(self, obj: Any) -> bytes:
        """
        Efficient binary serialization.

        Uses JSON for now; can switch to msgpack for production.
        NOT prose. Compact, fast, reproducible.
        """
        try:
            return json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
        except (TypeError, ValueError):
            # Fallback for non-serializable objects
            return json.dumps({"repr": repr(obj)}).encode("utf-8")

    def _hash(self, data: bytes) -> str:
        """Create a short hash for deduplication."""
        return hashlib.sha256(data).hexdigest()[:16]

    def _extract_semantic_inputs(self, snapshot: bytes) -> dict[str, Any]:
        """Extract structured inputs from snapshot."""
        try:
            data = json.loads(snapshot.decode("utf-8"))
            if isinstance(data, dict):
                return data
            return {"value": data}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {"raw": snapshot.hex()[:100]}

    def _estimate_gas(self, ctx: TraceContext, outputs: dict[str, Any]) -> int:
        """
        Estimate gas consumption (tokens used).

        Rough estimate: 4 bytes per token.
        """
        input_tokens = len(ctx.input_snapshot) // 4
        output_bytes = len(self._serialize(outputs))
        output_tokens = output_bytes // 4
        return input_tokens + output_tokens

    def _duration_ms(self, ctx: TraceContext) -> int:
        """Calculate duration in milliseconds."""
        delta = datetime.now(timezone.utc) - ctx.start_time
        return int(delta.total_seconds() * 1000)


class TracingContext:
    """
    Context manager for automatic trace recording.

    Usage:
        async with TracingContext(historian, agent, input_data) as ctx:
            result = await agent.invoke(input_data)
            # Trace is automatically recorded on exit
    """

    def __init__(
        self,
        historian: Historian,
        agent: Traceable | Any,
        input_data: Any,
        action: str = Action.INVOKE,
    ):
        self.historian = historian
        self.agent = agent
        self.input_data = input_data
        self.action = action
        self._ctx: TraceContext | None = None
        self._result: Any = None
        self._error: Exception | None = None

    def __enter__(self) -> TracingContext:
        self._ctx = self.historian.begin_trace(self.agent, self.input_data)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        if self._ctx is None:
            return False

        if exc_val is not None:
            # Convert BaseException to Exception or str for abort_trace
            if isinstance(exc_val, Exception):
                self.historian.abort_trace(self._ctx, exc_val)
            else:
                self.historian.abort_trace(self._ctx, str(exc_val))
        else:
            outputs = self._result if isinstance(self._result, dict) else {"result": self._result}
            self.historian.end_trace(self._ctx, self.action, outputs)

        return False  # Don't suppress exceptions

    async def __aenter__(self) -> TracingContext:
        return self.__enter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        return self.__exit__(exc_type, exc_val, exc_tb)

    def set_result(self, result: Any) -> None:
        """Set the result to record."""
        self._result = result

    @property
    def trace_id(self) -> str | None:
        """Get the current trace ID."""
        return self._ctx.trace_id if self._ctx else None
