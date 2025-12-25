"""
O-gent Core: The Observer Functor

The O-gent provides Systemic Proprioception—the innate ability of the system
to sense its own cognitive posture. Like biological proprioception enables
body coordination, O-gents enable system self-awareness.

Key Principles:
1. Observation doesn't mutate (outputs unchanged)
2. Observation doesn't block (async, non-blocking)
3. Observation doesn't leak (data stays within boundaries)
4. Observation enables (self-knowledge enables improvement)

Mathematical Foundation:
- Observer Functor O: Agent[A,B] → Agent[A,B]
- The Law: O(f) ≅ f for all behavioral purposes
- Observation is invisible to the observed
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, Protocol, TypeVar

# Type variables for generic agent typing
A = TypeVar("A", contravariant=True)  # Input type (contravariant for protocols)
B = TypeVar("B", covariant=True)  # Output type (covariant for protocols)


# =============================================================================
# Core Agent Protocol
# =============================================================================


class Agent(Protocol[A, B]):
    """
    Protocol for composable agents.

    An agent is a morphism A → B in the category of computational processes.
    """

    async def invoke(self, input: A) -> B:
        """Execute the agent with given input."""
        ...

    @property
    def name(self) -> str:
        """Agent's identifier."""
        ...


# =============================================================================
# Observation Context and Result Types
# =============================================================================


class ObservationStatus(Enum):
    """Status of an observation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ObservationContext:
    """
    Context for an observation event.

    Captures the state before agent invocation.
    """

    agent_id: str
    agent_name: str
    input_data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    observation_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.observation_id:
            self.observation_id = f"obs_{self.agent_id}_{self.timestamp.isoformat()}"


@dataclass
class ObservationResult:
    """
    Result of an observation event.

    Captures what happened during/after agent invocation.
    """

    context: ObservationContext
    status: ObservationStatus
    output_data: Any = None
    duration_ms: float = 0.0
    error: Optional[str] = None
    entropy_detected: bool = False
    telemetry: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success(self) -> bool:
        """Whether the observed operation succeeded."""
        return self.status == ObservationStatus.COMPLETED and self.error is None


# =============================================================================
# Observer Base Classes
# =============================================================================


class Observer(ABC):
    """
    Abstract base class for observers.

    Observers implement the three hooks:
    1. pre_invoke: Before agent execution (capture context)
    2. post_invoke: After successful execution (analyze result)
    3. record_entropy: On exception (log anomaly)
    """

    @abstractmethod
    def pre_invoke(
        self,
        agent: Agent[Any, Any],
        input_data: Any,
    ) -> ObservationContext:
        """
        Called before agent invocation.

        Returns context to be passed to post_invoke.
        """
        ...

    @abstractmethod
    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """
        Called after successful agent invocation.

        Should be async and non-blocking (fire-and-forget pattern).
        """
        ...

    @abstractmethod
    def record_entropy(
        self,
        context: ObservationContext,
        error: Exception,
    ) -> None:
        """
        Called when agent invocation fails.

        Records the exception as an entropy event.
        """
        ...


class BaseObserver(Observer):
    """
    Default implementation of Observer.

    Provides basic observation without deep analysis.
    Suitable as a base class for specialized observers.
    """

    def __init__(self, observer_id: str = "base_observer") -> None:
        self.observer_id = observer_id
        self._observations: list[ObservationResult] = []

    def pre_invoke(
        self,
        agent: Agent[Any, Any],
        input_data: Any,
    ) -> ObservationContext:
        """Capture pre-invocation context."""
        return ObservationContext(
            agent_id=getattr(agent, "id", str(id(agent))),
            agent_name=getattr(agent, "name", type(agent).__name__),
            input_data=input_data,
            metadata={"observer_id": self.observer_id},
        )

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """Record successful invocation."""
        observation = ObservationResult(
            context=context,
            status=ObservationStatus.COMPLETED,
            output_data=result,
            duration_ms=duration_ms,
            telemetry={
                "observer_id": self.observer_id,
                "result_type": type(result).__name__,
            },
        )
        self._observations.append(observation)
        return observation

    def record_entropy(
        self,
        context: ObservationContext,
        error: Exception,
    ) -> None:
        """Record exception as entropy event."""
        # Store as failed observation
        observation = ObservationResult(
            context=context,
            status=ObservationStatus.FAILED,
            error=str(error),
            telemetry={
                "exception_type": type(error).__name__,
            },
        )
        self._observations.append(observation)

    @property
    def observations(self) -> list[ObservationResult]:
        """Get all recorded observations."""
        return list(self._observations)

    def clear(self) -> None:
        """Clear observation history."""
        self._observations.clear()


# =============================================================================
# Observer Functor
# =============================================================================


class ObserverFunctor:
    """
    O: Agent[A, B] → Agent[A, B]

    The Observer Functor lifts an agent into an observed agent.
    The lifted agent behaves identically but emits telemetry.

    This is the fundamental law: Observation doesn't mutate.

    Mathematical Properties:
    - Functor laws hold: O(id) = id, O(f >> g) = O(f) >> O(g)
    - Behavioral equivalence: O(f)(x) ≅ f(x) for all x
    - Side effects: Only telemetry emission
    """

    def __init__(self, observer: Observer) -> None:
        """
        Initialize the functor with an observer.

        Args:
            observer: The observer that will receive telemetry.
        """
        self.observer = observer

    def lift(self, agent: Agent[A, B]) -> "ProprioceptiveWrapper[A, B]":
        """
        Lift an agent into the observed category.

        Returns an agent that behaves identically but is observed.
        """
        return ProprioceptiveWrapper(inner=agent, observer=self.observer)


class ProprioceptiveWrapper(Generic[A, B]):
    """
    Agent under observation.

    Same interface, same behavior, but observed.
    The wrapper is invisible to callers and doesn't affect results.
    """

    def __init__(self, inner: Agent[A, B], observer: Observer) -> None:
        """
        Wrap an agent with observation.

        Args:
            inner: The agent to wrap.
            observer: The observer that will receive telemetry.
        """
        self._inner = inner
        self._observer = observer

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
        """Access the wrapped agent."""
        return self._inner

    async def invoke(self, input: A) -> B:
        """
        Invoke the agent with observation.

        1. Pre-computation snapshot
        2. Execute (unchanged)
        3. Post-computation analysis (async, non-blocking)
        """
        # 1. Pre-computation snapshot
        ctx = self._observer.pre_invoke(self._inner, input)
        start_time = datetime.now()

        try:
            # 2. Execute (unchanged behavior)
            result = await self._inner.invoke(input)

            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            # 3. Post-computation analysis (fire-and-forget)
            # Use create_task for non-blocking observation
            asyncio.create_task(self._observer.post_invoke(ctx, result, duration_ms))

            return result

        except Exception as e:
            # Record entropy but re-raise the exception
            # Observation doesn't change error behavior
            self._observer.record_entropy(ctx, e)
            raise


# =============================================================================
# Convenience Functions
# =============================================================================


def observe(agent: Agent[A, B], observer: Observer | None = None) -> ProprioceptiveWrapper[A, B]:
    """
    Lift an agent into observation.

    Convenience function for creating an observed agent.

    Args:
        agent: The agent to observe
        observer: Optional observer (defaults to BaseObserver)

    Returns:
        ProprioceptiveWrapper wrapping the agent
    """
    if observer is None:
        observer = BaseObserver()
    functor = ObserverFunctor(observer)
    return functor.lift(agent)
