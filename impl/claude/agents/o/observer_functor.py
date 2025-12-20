"""
Unified Observer Functor: The Categorical Consolidation of Observation.

This module provides a unified ObserverFunctor that can express all observation
patterns in kgents through a single, composable interface:

    ObserverFunctor.lift(agent, sink=observer)     # O-gent telemetry
    ObserverFunctor.lift(agent, sink=historian)    # N-gent narrative
    ObserverFunctor.lift(agent, sink=metrics)      # T-gent metrics

The key insight: Observation is a functor that preserves agent behavior while
adding a side effect (recording to a sink).

Mathematical Properties:
    - Identity: O(id) ≅ id (behavioral equivalence)
    - Composition: O(g >> f) ≅ O(g) >> O(f)
    - Non-mutating: Observation never changes outputs
    - Non-blocking: Observation happens asynchronously where possible

Sink Protocol:
    Any class implementing ObservationSink can be used as a sink.
    This unifies O-gent (Observer), N-gent (Historian), and T-gent patterns.

See: plans/architecture/categorical-consolidation.md Phase 2
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from agents.a.functor import FunctorRegistry, UniversalFunctor
from agents.poly.types import Agent, ComposedAgent

A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# Observation Event: The Universal Record
# =============================================================================


@dataclass
class ObservationEvent:
    """
    Universal observation event that all sinks can consume.

    This is the "lowest common denominator" that unifies:
    - O-gent ObservationResult
    - N-gent SemanticTrace
    - T-gent history records

    Sinks can extract what they need from this universal record.
    """

    # Identity
    agent_name: str
    agent_id: str

    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0

    # Data (input/output)
    input_data: Any = None
    output_data: Any = None

    # Outcome
    success: bool = True
    error: str | None = None

    # Extensible metadata
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Observation Sink Protocol: The Universal Interface
# =============================================================================


@runtime_checkable
class ObservationSink(Protocol):
    """
    Protocol for observation sinks.

    Any class implementing this protocol can receive observation events.
    This unifies the interfaces of:
    - O-gent Observer (pre_invoke/post_invoke/record_entropy → record)
    - N-gent Historian (begin_trace/end_trace → record)
    - T-gent Spy/Metrics (internal state → record)
    """

    async def record(self, event: ObservationEvent) -> None:
        """
        Record an observation event.

        Args:
            event: The universal observation event

        This method should:
        - Be async (can be non-blocking)
        - Not raise exceptions (observation shouldn't fail the agent)
        - Transform the event to sink-specific format if needed
        """
        ...


# =============================================================================
# Sink Adapters: Bridge existing implementations to the protocol
# =============================================================================


class ObserverSinkAdapter(ObservationSink):
    """
    Adapts O-gent Observer to ObservationSink protocol.

    Converts ObservationEvent → Observer.post_invoke() calls.
    """

    def __init__(self, observer: Any) -> None:
        """
        Create an adapter for an O-gent Observer.

        Args:
            observer: An instance of agents.o.observer.Observer
        """
        self._observer = observer

    async def record(self, event: ObservationEvent) -> None:
        """Record event using O-gent Observer."""
        from agents.o.observer import (
            ObservationContext,
            ObservationResult,
            ObservationStatus,
        )

        # Create O-gent context (minimal reconstruction)
        context = ObservationContext(
            agent_id=event.agent_id,
            agent_name=event.agent_name,
            input_data=event.input_data,
            timestamp=event.timestamp,
            metadata=event.metadata,
        )

        # Create O-gent result
        status = ObservationStatus.COMPLETED if event.success else ObservationStatus.FAILED
        result = ObservationResult(
            context=context,
            status=status,
            output_data=event.output_data,
            duration_ms=event.duration_ms,
            error=event.error,
        )

        # Append to observer's internal storage
        if hasattr(self._observer, "_observations"):
            self._observer._observations.append(result)


class HistorianSinkAdapter(ObservationSink):
    """
    Adapts N-gent Historian to ObservationSink protocol.

    Converts ObservationEvent → Historian trace operations.
    Note: This is a simplified bridge; for full N-gent functionality,
    use Historian directly with begin_trace/end_trace.
    """

    def __init__(self, historian: Any, store: Any | None = None) -> None:
        """
        Create an adapter for an N-gent Historian.

        Args:
            historian: An instance of agents.n.historian.Historian
            store: Optional CrystalStore (defaults to historian's store)
        """
        self._historian = historian
        self._store = store or getattr(historian, "store", None)

    async def record(self, event: ObservationEvent) -> None:
        """
        Record event using N-gent patterns.

        Note: This creates a simplified trace. For full SemanticTrace support
        with all fields (determinism, action types, etc.), use Historian directly.
        """
        # Store basic observation data to historian's store if available
        if self._store and hasattr(self._store, "store"):
            from agents.n.types import Action, Determinism, SemanticTrace

            # Create minimal SemanticTrace
            trace = SemanticTrace(
                trace_id=f"obs_{event.agent_id}_{event.timestamp.isoformat()}",
                parent_id=None,
                timestamp=event.timestamp,
                agent_id=event.agent_id,
                agent_genus=event.metadata.get("genus", "unknown"),
                action=Action.INVOKE,
                inputs={"data": event.input_data},
                outputs={"result": event.output_data},
                input_hash=str(hash(str(event.input_data)))[:16],
                output_hash=str(hash(str(event.output_data)))[:16] if event.output_data else "",
                input_snapshot=b"",  # Required field, empty for unified observation
                gas_consumed=0,
                duration_ms=int(event.duration_ms),  # Must be int
                determinism=Determinism.DETERMINISTIC,
            )
            await self._store.store(trace)


class MetricsSinkAdapter(ObservationSink):
    """
    Adapts T-gent MetricsAgent to ObservationSink protocol.

    Updates timing metrics from ObservationEvents.
    """

    def __init__(self, metrics_agent: Any) -> None:
        """
        Create an adapter for a T-gent MetricsAgent.

        Args:
            metrics_agent: An instance of agents.t.metrics.MetricsAgent
        """
        self._metrics = metrics_agent

    async def record(self, event: ObservationEvent) -> None:
        """Record event to T-gent metrics."""
        # Update T-gent metrics
        if hasattr(self._metrics, "_metrics"):
            m = self._metrics._metrics
            m.invocation_count += 1
            m.total_time += event.duration_ms
            m.min_time = min(m.min_time, event.duration_ms)
            m.max_time = max(m.max_time, event.duration_ms)


class ListSink(ObservationSink):
    """
    Simple list-based sink for testing and lightweight observation.

    Collects all events in a list for later inspection.
    """

    def __init__(self) -> None:
        self.events: list[ObservationEvent] = []

    async def record(self, event: ObservationEvent) -> None:
        """Append event to list."""
        self.events.append(event)

    def clear(self) -> None:
        """Clear all recorded events."""
        self.events.clear()


# =============================================================================
# Observed Agent: The Lifted Agent
# =============================================================================


class ObservedAgent(Generic[A, B]):
    """
    An agent under observation.

    Wraps an inner agent and records all invocations to a sink.
    The wrapped agent's behavior is unchanged—observation is invisible.
    """

    def __init__(
        self,
        inner: Agent[A, B],
        sink: ObservationSink,
        non_blocking: bool = True,
    ) -> None:
        """
        Create an observed agent.

        Args:
            inner: The agent to observe
            sink: Where to send observation events
            non_blocking: If True, observation is fire-and-forget (default)
        """
        self._inner = inner
        self._sink = sink
        self._non_blocking = non_blocking

    @property
    def name(self) -> str:
        """Delegate to inner agent."""
        return getattr(self._inner, "name", type(self._inner).__name__)

    @property
    def id(self) -> str:
        """Delegate to inner agent."""
        return getattr(self._inner, "id", str(id(self._inner)))

    @property
    def inner(self) -> Agent[A, B]:
        """Access the inner agent (for unlift)."""
        return self._inner

    @property
    def sink(self) -> ObservationSink:
        """Access the observation sink."""
        return self._sink

    async def invoke(self, input: A) -> B:
        """
        Invoke the agent with observation.

        1. Capture start time
        2. Execute inner agent (unchanged)
        3. Record observation event to sink

        The observation never affects the result.
        """
        start_time = datetime.now()
        error_msg: str | None = None
        output: Any = None
        success = True

        try:
            result: B = await self._inner.invoke(input)
            output = result
            return result
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            success = False
            raise
        finally:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            event = ObservationEvent(
                agent_name=self.name,
                agent_id=self.id,
                timestamp=start_time,
                duration_ms=duration_ms,
                input_data=input,
                output_data=output,
                success=success,
                error=error_msg,
                metadata={"non_blocking": self._non_blocking},
            )

            if self._non_blocking:
                # Fire-and-forget (non-blocking)
                asyncio.create_task(self._sink.record(event))
            else:
                # Wait for observation to complete
                await self._sink.record(event)

    def __rshift__(self, other: Agent[B, Any]) -> Any:
        """Compose with another agent."""
        return ComposedAgent(self, other)  # type: ignore[arg-type]


# =============================================================================
# Unified Observer Functor
# =============================================================================


class UnifiedObserverFunctor(UniversalFunctor[ObservedAgent[Any, Any]]):
    """
    Unified Observer Functor: The Categorical Consolidation of Observation.

    This functor lifts agents to be observed, sending events to any sink
    implementing the ObservationSink protocol.

    Satisfies functor laws:
    - Identity: lift(id) behaves like identity (with observation side effect)
    - Composition: lift(g >> f) ≅ lift(g) >> lift(f)

    Usage:
        # O-gent style (telemetry)
        observed = UnifiedObserverFunctor.lift(agent, sink=observer_adapter)

        # N-gent style (narrative)
        traced = UnifiedObserverFunctor.lift(agent, sink=historian_adapter)

        # T-gent style (metrics)
        metered = UnifiedObserverFunctor.lift(agent, sink=metrics_adapter)

        # Simple list collection
        list_sink = ListSink()
        observed = UnifiedObserverFunctor.lift(agent, sink=list_sink)
    """

    # Default sink for when none is provided
    _default_sink: ObservationSink | None = None

    @classmethod
    def set_default_sink(cls, sink: ObservationSink) -> None:
        """Set the default sink for observation."""
        cls._default_sink = sink

    @staticmethod
    def lift(
        agent: Agent[A, B],
        sink: ObservationSink | None = None,
        non_blocking: bool = True,
    ) -> Agent[Any, Any]:
        """
        Lift an agent to be observed.

        Args:
            agent: The agent to observe
            sink: Where to send observation events (defaults to ListSink)
            non_blocking: If True, observation is fire-and-forget

        Returns:
            ObservedAgent wrapping the input agent
        """
        actual_sink = sink or UnifiedObserverFunctor._default_sink or ListSink()
        observed = ObservedAgent(inner=agent, sink=actual_sink, non_blocking=non_blocking)
        return observed  # type: ignore[return-value]

    @staticmethod
    def unlift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
        """Extract inner agent from ObservedAgent."""
        if not isinstance(agent, ObservedAgent):
            raise TypeError(f"Cannot unlift {type(agent).__name__} - not an ObservedAgent")
        return agent.inner

    @staticmethod
    def pure(value: A) -> Any:
        """Observer functor is an endofunctor; pure returns value unchanged."""
        return value


# =============================================================================
# Convenience Functions
# =============================================================================


def observe(
    agent: Agent[A, B],
    sink: ObservationSink | None = None,
    non_blocking: bool = True,
) -> ObservedAgent[A, B]:
    """
    Lift an agent to be observed.

    Convenience function for UnifiedObserverFunctor.lift().

    Args:
        agent: The agent to observe
        sink: Where to send events (defaults to ListSink)
        non_blocking: Fire-and-forget observation (default True)

    Returns:
        ObservedAgent that records to the sink
    """
    actual_sink = sink or UnifiedObserverFunctor._default_sink or ListSink()
    return ObservedAgent(inner=agent, sink=actual_sink, non_blocking=non_blocking)


def unobserve(agent: ObservedAgent[A, B]) -> Agent[A, B]:
    """
    Extract inner agent from observed wrapper.

    Convenience function for UnifiedObserverFunctor.unlift().
    """
    return agent.inner


# =============================================================================
# Factory functions for sink adapters
# =============================================================================


def observer_sink(observer: Any) -> ObserverSinkAdapter:
    """
    Create a sink adapter for an O-gent Observer.

    Args:
        observer: An instance of agents.o.observer.Observer

    Returns:
        ObserverSinkAdapter that bridges to O-gent
    """
    return ObserverSinkAdapter(observer)


def historian_sink(historian: Any, store: Any | None = None) -> HistorianSinkAdapter:
    """
    Create a sink adapter for an N-gent Historian.

    Args:
        historian: An instance of agents.n.historian.Historian
        store: Optional CrystalStore

    Returns:
        HistorianSinkAdapter that bridges to N-gent
    """
    return HistorianSinkAdapter(historian, store)


def metrics_sink(metrics_agent: Any) -> MetricsSinkAdapter:
    """
    Create a sink adapter for a T-gent MetricsAgent.

    Args:
        metrics_agent: An instance of agents.t.metrics.MetricsAgent

    Returns:
        MetricsSinkAdapter that bridges to T-gent
    """
    return MetricsSinkAdapter(metrics_agent)


# =============================================================================
# Registry
# =============================================================================


def _register_observer_functor() -> None:
    """Register UnifiedObserverFunctor with the universal registry."""
    FunctorRegistry.register("Observer", UnifiedObserverFunctor)


# Auto-register on import
_register_observer_functor()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "ObservationEvent",
    "ObservationSink",
    "ObservedAgent",
    "UnifiedObserverFunctor",
    # Sink adapters
    "ObserverSinkAdapter",
    "HistorianSinkAdapter",
    "MetricsSinkAdapter",
    "ListSink",
    # Convenience functions
    "observe",
    "unobserve",
    # Factory functions
    "observer_sink",
    "historian_sink",
    "metrics_sink",
]
