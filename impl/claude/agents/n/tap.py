"""
HistorianTap: Wire Protocol Integration for the Historian.

The HistorianTap sits on the W-gent wire protocol and observes frames
without mutating them. It feeds observations to the Historian to create
crystals.

Philosophy:
    Observe without affecting the observed.
    The tap is a tap, not a transform.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from .historian import Historian
from .types import Action, Determinism, TraceContext


class FrameType(Enum):
    """Types of wire frames the tap observes."""

    INVOKE_START = "invoke_start"
    INVOKE_END = "invoke_end"
    ERROR = "error"
    # Additional frame types for richer observation
    STATE_UPDATE = "state_update"
    LOG_EVENT = "log_event"


@dataclass
class WireFrame:
    """
    A frame on the wire protocol.

    This is a simplified representation—the actual wire protocol
    may use WireEvent, WireState, etc. from W-gent.
    """

    frame_type: FrameType
    correlation_id: str  # Links INVOKE_START to INVOKE_END
    timestamp: datetime
    agent_id: str
    agent_genus: str
    payload: Any
    metadata: dict[str, Any]

    @property
    def action(self) -> str:
        """Extract action from metadata or default to INVOKE."""
        return self.metadata.get("action", Action.INVOKE)

    @property
    def determinism_hint(self) -> Determinism | None:
        """Extract determinism hint from metadata."""
        if self.metadata.get("llm_call"):
            return Determinism.PROBABILISTIC
        if self.metadata.get("external_api"):
            return Determinism.CHAOTIC
        if "determinism" in self.metadata:
            return Determinism(self.metadata["determinism"])
        return None


class HistorianTap:
    """
    A wire tap that feeds the Historian.

    Observes W-gent wire protocol frames without mutation.
    Creates crystals from the observations.

    Usage:
        historian = Historian(store)
        tap = HistorianTap(historian)

        # On each wire frame:
        frame = await tap.on_frame(incoming_frame)
        # frame is returned unchanged

    The tap maintains state to correlate INVOKE_START with INVOKE_END.
    """

    def __init__(self, historian: Historian):
        """
        Initialize the tap.

        Args:
            historian: The Historian to feed observations to
        """
        self.historian = historian
        self._active_contexts: dict[str, TraceContext] = {}

    async def on_frame(self, frame: WireFrame) -> WireFrame:
        """
        Observe a frame without mutating it.

        Args:
            frame: The incoming wire frame

        Returns:
            The frame unchanged (pass-through)
        """
        match frame.frame_type:
            case FrameType.INVOKE_START:
                self._handle_invoke_start(frame)

            case FrameType.INVOKE_END:
                self._handle_invoke_end(frame)

            case FrameType.ERROR:
                self._handle_error(frame)

            case FrameType.STATE_UPDATE:
                # State updates don't create traces, just metadata
                self._handle_state_update(frame)

            case FrameType.LOG_EVENT:
                # Log events don't create traces (that's O-gent territory)
                pass

        return frame  # Pass through unchanged

    def on_frame_sync(self, frame: WireFrame) -> WireFrame:
        """Synchronous version of on_frame for non-async contexts."""
        match frame.frame_type:
            case FrameType.INVOKE_START:
                self._handle_invoke_start(frame)
            case FrameType.INVOKE_END:
                self._handle_invoke_end(frame)
            case FrameType.ERROR:
                self._handle_error(frame)
            case _:
                pass
        return frame

    def _handle_invoke_start(self, frame: WireFrame) -> None:
        """Handle INVOKE_START: Begin tracing."""
        # Create a minimal agent proxy for the historian
        agent_proxy = _AgentProxy(
            name=frame.agent_id,
            genus=frame.agent_genus,
        )

        ctx = self.historian.begin_trace(
            agent=agent_proxy,
            input_data=frame.payload,
        )

        # Store context for correlation
        self._active_contexts[frame.correlation_id] = ctx

    def _handle_invoke_end(self, frame: WireFrame) -> None:
        """Handle INVOKE_END: Complete trace."""
        ctx = self._active_contexts.pop(frame.correlation_id, None)
        if not ctx:
            # No matching start—possibly lost or never started
            return

        # Determine determinism
        determinism = frame.determinism_hint
        if determinism is None:
            determinism = Action.classify_determinism(frame.action)

        # Complete the trace
        outputs = (
            frame.payload
            if isinstance(frame.payload, dict)
            else {"result": frame.payload}
        )
        self.historian.end_trace(
            ctx=ctx,
            action=frame.action,
            outputs=outputs,
            determinism=determinism,
        )

    def _handle_error(self, frame: WireFrame) -> None:
        """Handle ERROR: Abort trace."""
        ctx = self._active_contexts.pop(frame.correlation_id, None)
        if not ctx:
            return

        # Extract error from payload
        if isinstance(frame.payload, Exception):
            error = frame.payload
        elif isinstance(frame.payload, dict) and "error" in frame.payload:
            error = frame.payload["error"]
        else:
            error = str(frame.payload)

        self.historian.abort_trace(ctx, error)

    def _handle_state_update(self, frame: WireFrame) -> None:
        """Handle STATE_UPDATE: Add metadata to active context."""
        ctx = self._active_contexts.get(frame.correlation_id)
        if ctx and isinstance(frame.payload, dict):
            # We can't modify the frozen TraceContext, but we can
            # note state changes in a side channel if needed
            pass

    @property
    def active_traces(self) -> int:
        """Number of traces currently in progress."""
        return len(self._active_contexts)

    def get_pending_trace_ids(self) -> list[str]:
        """Get IDs of traces that started but haven't ended."""
        return list(self._active_contexts.keys())


@dataclass
class _AgentProxy:
    """Minimal agent proxy for the Historian."""

    name: str
    genus: str


class WireIntegration:
    """
    Higher-level integration with W-gent wire protocol.

    Provides convenience methods for common patterns.
    """

    def __init__(self, historian: Historian):
        self.historian = historian
        self.tap = HistorianTap(historian)

    def trace_callable(
        self,
        agent_id: str,
        agent_genus: str,
        action: str = Action.INVOKE,
    ) -> Callable[[Callable], Callable]:
        """
        Decorator to trace a callable.

        Usage:
            @wire.trace_callable("my-agent", "B", "GENERATE")
            async def generate_hypothesis(data):
                ...
        """

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                # Create frame for start
                import uuid

                correlation_id = str(uuid.uuid4())

                start_frame = WireFrame(
                    frame_type=FrameType.INVOKE_START,
                    correlation_id=correlation_id,
                    timestamp=datetime.utcnow(),
                    agent_id=agent_id,
                    agent_genus=agent_genus,
                    payload={"args": args, "kwargs": kwargs},
                    metadata={"action": action},
                )
                await self.tap.on_frame(start_frame)

                try:
                    result = await func(*args, **kwargs)

                    end_frame = WireFrame(
                        frame_type=FrameType.INVOKE_END,
                        correlation_id=correlation_id,
                        timestamp=datetime.utcnow(),
                        agent_id=agent_id,
                        agent_genus=agent_genus,
                        payload=result
                        if isinstance(result, dict)
                        else {"result": result},
                        metadata={"action": action},
                    )
                    await self.tap.on_frame(end_frame)

                    return result

                except Exception as e:
                    error_frame = WireFrame(
                        frame_type=FrameType.ERROR,
                        correlation_id=correlation_id,
                        timestamp=datetime.utcnow(),
                        agent_id=agent_id,
                        agent_genus=agent_genus,
                        payload=e,
                        metadata={"action": action},
                    )
                    await self.tap.on_frame(error_frame)
                    raise

            return wrapper

        return decorator

    def create_start_frame(
        self,
        correlation_id: str,
        agent_id: str,
        agent_genus: str,
        payload: Any,
        action: str = Action.INVOKE,
    ) -> WireFrame:
        """Create an INVOKE_START frame."""
        return WireFrame(
            frame_type=FrameType.INVOKE_START,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            agent_genus=agent_genus,
            payload=payload,
            metadata={"action": action},
        )

    def create_end_frame(
        self,
        correlation_id: str,
        agent_id: str,
        agent_genus: str,
        payload: Any,
        action: str = Action.INVOKE,
        determinism: Determinism | None = None,
    ) -> WireFrame:
        """Create an INVOKE_END frame."""
        metadata = {"action": action}
        if determinism:
            metadata["determinism"] = determinism.value
        return WireFrame(
            frame_type=FrameType.INVOKE_END,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            agent_genus=agent_genus,
            payload=payload,
            metadata=metadata,
        )

    def create_error_frame(
        self,
        correlation_id: str,
        agent_id: str,
        agent_genus: str,
        error: Exception | str,
    ) -> WireFrame:
        """Create an ERROR frame."""
        return WireFrame(
            frame_type=FrameType.ERROR,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            agent_genus=agent_genus,
            payload=error,
            metadata={},
        )
