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

Heisenberg Constraint:
Semantic observation (LLM-as-Judge) consumes energy (tokens).
O-gents must be Economically Self-Aware via VoI optimization.
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
T = TypeVar("T")


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


@dataclass
class EntropyEvent:
    """
    Represents entropy (unexpected behavior) detected during observation.

    Entropy is the system's word for "something interesting happened."
    Not necessarily bad—could be an anomaly worth investigating.
    """

    source_agent: str
    event_type: str  # "exception", "drift", "timeout", "conservation_violation"
    severity: str  # "info", "warning", "error", "critical"
    description: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


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
    ) -> EntropyEvent:
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
        self._entropy_events: list[EntropyEvent] = []

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
    ) -> EntropyEvent:
        """Record exception as entropy event."""
        event = EntropyEvent(
            source_agent=context.agent_name,
            event_type="exception",
            severity="error",
            description=str(error),
            data={
                "exception_type": type(error).__name__,
                "observation_id": context.observation_id,
            },
        )
        self._entropy_events.append(event)
        return event

    @property
    def observations(self) -> list[ObservationResult]:
        """Get all recorded observations."""
        return list(self._observations)

    @property
    def entropy_events(self) -> list[EntropyEvent]:
        """Get all recorded entropy events."""
        return list(self._entropy_events)

    def clear(self) -> None:
        """Clear observation history."""
        self._observations.clear()
        self._entropy_events.clear()


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
# Observer Hierarchy (Stratification)
# =============================================================================


class ObserverLevel(Enum):
    """
    Levels in the observer hierarchy.

    Level N observers may observe Level N-1, but not themselves or Level N.
    This prevents infinite regress ("Who watches the watchers?").
    """

    CONCRETE = 0  # Level 0: Concrete observers (BootstrapWitness, InvocationTracer)
    DOMAIN = 1  # Level 1: Domain observers (BootstrapObserver, AgentObserver)
    SYSTEM = 2  # Level 2: Meta-observer (SystemObserver - self-unobserved)


@dataclass
class StratifiedObserver:
    """
    Observer with stratification level.

    Enforces the hierarchy rule: can only observe lower levels.
    """

    observer: Observer
    level: ObserverLevel
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            self.name = getattr(self.observer, "observer_id", "unnamed")

    def can_observe(self, target_level: ObserverLevel) -> bool:
        """Check if this observer can observe the target level."""
        return self.level.value > target_level.value


class ObserverHierarchy:
    """
    Manages the stratified observer hierarchy.

    Prevents observation loops and enforces level constraints.
    """

    def __init__(self) -> None:
        self._observers: dict[ObserverLevel, list[StratifiedObserver]] = {
            level: [] for level in ObserverLevel
        }

    def register(
        self,
        observer: Observer,
        level: ObserverLevel,
        name: str = "",
    ) -> StratifiedObserver:
        """Register an observer at a specific level."""
        stratified = StratifiedObserver(observer=observer, level=level, name=name)
        self._observers[level].append(stratified)
        return stratified

    def get_observers_for_level(
        self,
        target_level: ObserverLevel,
    ) -> list[StratifiedObserver]:
        """Get all observers that can observe the target level."""
        result = []
        for level, observers in self._observers.items():
            if level.value > target_level.value:
                result.extend(observers)
        return result

    def get_all_at_level(self, level: ObserverLevel) -> list[StratifiedObserver]:
        """Get all observers at a specific level."""
        return list(self._observers.get(level, []))


# =============================================================================
# Composite Observer
# =============================================================================


class CompositeObserver(Observer):
    """
    Observer that delegates to multiple child observers.

    Useful for combining different observation dimensions
    (telemetry, semantic, axiological) into a single observation point.
    """

    def __init__(self, observers: list[Observer] | None = None) -> None:
        """
        Initialize with optional list of child observers.

        Args:
            observers: Child observers to delegate to.
        """
        self._observers = list(observers) if observers else []

    def add_observer(self, observer: Observer) -> None:
        """Add a child observer."""
        self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        """Remove a child observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def pre_invoke(
        self,
        agent: Agent[Any, Any],
        input_data: Any,
    ) -> ObservationContext:
        """
        Create context and notify all child observers.

        Returns a single context (children receive via delegation).
        """
        # Create the canonical context
        ctx = ObservationContext(
            agent_id=getattr(agent, "id", str(id(agent))),
            agent_name=getattr(agent, "name", type(agent).__name__),
            input_data=input_data,
            metadata={"composite": True, "observer_count": len(self._observers)},
        )

        # Notify all children
        for observer in self._observers:
            observer.pre_invoke(agent, input_data)

        return ctx

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """
        Notify all child observers of completion.

        Aggregates results from all children.
        """
        child_results = []

        for observer in self._observers:
            try:
                child_result = await observer.post_invoke(context, result, duration_ms)
                child_results.append(child_result)
            except Exception:
                # Don't let one observer's failure affect others
                pass

        # Create aggregate result
        return ObservationResult(
            context=context,
            status=ObservationStatus.COMPLETED,
            output_data=result,
            duration_ms=duration_ms,
            telemetry={
                "child_observer_count": len(self._observers),
                "child_results_collected": len(child_results),
            },
        )

    def record_entropy(
        self,
        context: ObservationContext,
        error: Exception,
    ) -> EntropyEvent:
        """
        Notify all child observers of entropy.

        Returns the first child's event (all are recorded).
        """
        events = []

        for observer in self._observers:
            try:
                event = observer.record_entropy(context, error)
                events.append(event)
            except Exception:
                pass

        # Return first event or create a new one
        if events:
            return events[0]

        return EntropyEvent(
            source_agent=context.agent_name,
            event_type="exception",
            severity="error",
            description=str(error),
            data={"composite": True},
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_observer(observer_id: str = "default") -> BaseObserver:
    """Create a basic observer."""
    return BaseObserver(observer_id=observer_id)


def create_functor(observer: Observer | None = None) -> ObserverFunctor:
    """Create an observer functor with optional custom observer."""
    if observer is None:
        observer = create_observer()
    return ObserverFunctor(observer=observer)


def observe(agent: Agent[A, B], observer: Observer | None = None) -> ProprioceptiveWrapper[A, B]:
    """
    Lift an agent into observation.

    Shorthand for create_functor(observer).lift(agent).
    """
    functor = create_functor(observer)
    return functor.lift(agent)


def create_hierarchy() -> ObserverHierarchy:
    """Create a new observer hierarchy."""
    return ObserverHierarchy()


def create_composite(*observers: Observer) -> CompositeObserver:
    """Create a composite observer from multiple observers."""
    return CompositeObserver(list(observers))
