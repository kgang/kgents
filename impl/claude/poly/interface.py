"""
PolyInterface - The Polynomial Functor Interface Protocol.

This replaces LogosNode with a mathematically-grounded interface
where observation ALWAYS triggers state transition.

Mathematical Foundation:
A polynomial functor P has the form:
    P(y) = Σ_{s ∈ S} y^{A_s}

Where:
- S: Set of internal states (modes)
- A_s: Set of valid inputs at state s (affordances)
- y: Formal variable for output channels

Key Insight from Category Theory:
There is no way to "get" a value without triggering a state update.
This structurally eliminates passive observation.

Usage:
    @dataclass
    class CounterState:
        count: int = 0

    class CounterInput:
        pass

    @dataclass
    class Increment(CounterInput):
        amount: int = 1

    @dataclass
    class Read(CounterInput):
        pass  # Even reading changes state!

    @dataclass
    class CounterOutput:
        value: int
        changed: bool

    class Counter(PolyInterface[CounterState, CounterInput, CounterOutput]):
        def scope(self, s: CounterState) -> Type[CounterInput]:
            return CounterInput

        def dynamics(self, s: CounterState, input: CounterInput) -> tuple[CounterState, CounterOutput]:
            match input:
                case Increment(amount):
                    return CounterState(s.count + amount), CounterOutput(s.count + amount, True)
                case Read():
                    # Reading still updates state (e.g., read_count)
                    return CounterState(s.count), CounterOutput(s.count, False)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, Type, TypeVar, runtime_checkable

# Type variables for the polynomial functor
S = TypeVar("S")  # State type
A = TypeVar("A")  # Input type (affordances)
B = TypeVar("B")  # Output type


class PolyState(Protocol):
    """Protocol for polynomial functor states."""

    pass


class PolyInput(Protocol):
    """Protocol for polynomial functor inputs."""

    pass


class PolyOutput(Protocol):
    """Protocol for polynomial functor outputs."""

    pass


@runtime_checkable
class PolyInterface(Protocol[S, A, B]):  # type: ignore[misc]
    """
    A Polynomial Functor Interface.

    P(y) = Σ_{s ∈ S} y^{A_s}

    Represents a Mode-Dependent Dynamical System where:
    - state: Current position in state space S
    - scope(s): Returns valid input type at state s
    - dynamics(s, a): State transition S × A → S × B

    This replaces LogosNode. Key differences:
    1. State is explicit, not hidden
    2. affordances() becomes scope() - returns TYPE not list
    3. invoke() becomes dynamics() - ALWAYS updates state

    The type system ensures observation cannot be passive.

    Example:
        >>> counter = Counter(state=CounterState(0))
        >>> new_state, output = counter.dynamics(counter.state, Increment(5))
        >>> assert new_state.count == 5
    """

    state: S

    def scope(self, s: S) -> Type[A]:
        """
        The 'Interface' function: At state S, what inputs are valid?

        This replaces `affordances(observer) -> list[str]`.

        Returns a TYPE, not a list. This enables:
        - Static type checking of valid inputs
        - Exhaustive pattern matching
        - No runtime "affordance not found" errors

        The returned type may be a Union, Enum, or Protocol.
        """
        ...

    def dynamics(self, s: S, input: A) -> tuple[S, B]:
        """
        The 'Update' function: Given input A, transition and emit B.

        S × A → S × B

        This replaces `invoke(aspect, observer, **kwargs)`.

        CRITICAL: This ALWAYS updates state. There is no
        "read-only" operation. Even observation causes transition.

        This structurally enforces "to observe is to act."
        """
        ...


@dataclass
class BasePolyInterface(ABC, Generic[S, A, B]):
    """
    Base class for implementing PolyInterface.

    Provides convenience methods and enforces the Poly contract.

    Example:
        @dataclass
        class MyInterface(BasePolyInterface[MyState, MyInput, MyOutput]):
            state: MyState

            def scope(self, s: MyState) -> Type[MyInput]:
                return MyInput

            def dynamics(self, s: MyState, input: MyInput) -> tuple[MyState, MyOutput]:
                # Implementation
                ...
    """

    state: S

    @abstractmethod
    def scope(self, s: S) -> Type[A]:
        """Return valid input type at state s."""
        ...

    @abstractmethod
    def dynamics(self, s: S, input: A) -> tuple[S, B]:
        """Execute state transition."""
        ...

    def step(self, input: A) -> B:
        """
        Convenience method: step forward and update internal state.

        Returns only the output; state is mutated in place.

        Example:
            >>> output = counter.step(Increment(5))
            >>> assert counter.state.count == 5
        """
        new_state, output = self.dynamics(self.state, input)
        self.state = new_state
        return output

    def valid_input(self, input: A) -> bool:
        """Check if input is valid at current state."""
        return isinstance(input, self.scope(self.state))


# Common state patterns


@dataclass
class ObservationTrackedState:
    """
    A state that tracks observations.

    This is a mixin for states that need to record
    that they were observed.
    """

    observation_count: int = 0
    last_observer: str | None = None


@dataclass
class VersionedState:
    """
    A state with version tracking.

    Useful for optimistic concurrency control.
    """

    version: int = 0


# Common input patterns


@dataclass
class ObserveInput:
    """
    Standard observation input.

    Even though it's "just" an observation, it will
    cause state transition (at minimum, updating
    observation_count).
    """

    observer_id: str
    intent: str = "observe"


@dataclass
class QueryInput:
    """
    Query input that still triggers state transition.

    Queries are recorded in the state for auditing
    and to enable morphic resonance.
    """

    query: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class MutateInput:
    """
    Explicit mutation input.
    """

    changes: dict[str, Any]


# Common output patterns


@dataclass
class ObservationOutput:
    """Standard output from observation."""

    view: Any
    state_changed: bool
    delta: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryOutput:
    """Standard output from query."""

    result: Any
    query_recorded: bool = True


@dataclass
class MutationOutput:
    """Standard output from mutation."""

    previous: Any
    current: Any
    changes_applied: dict[str, Any] = field(default_factory=dict)


# Example: House as PolyInterface


@dataclass
class HouseState:
    """Internal state of a house entity."""

    observation_count: int = 0
    last_observer_archetype: str | None = None
    reified_properties: frozenset[str] = field(default_factory=frozenset)
    version: int = 0


class HouseInput:
    """Sum type of valid house inputs."""

    pass


@dataclass
class ObserveHouse(HouseInput):
    """Request to observe the house."""

    observer_archetype: str
    intent: str


@dataclass
class RenovateHouse(HouseInput):
    """Request to renovate (architect only)."""

    changes: dict[str, Any]


@dataclass
class InhabitHouse(HouseInput):
    """Request to inhabit the house."""

    duration: float


@dataclass
class HouseOutput:
    """Output from house interactions."""

    view: dict[str, Any]
    state_delta: dict[str, Any]


@dataclass
class WorldHouse(BasePolyInterface[HouseState, HouseInput, HouseOutput]):
    """
    A house in the world, as a Polynomial Interface.

    This is the canonical example showing how observation
    causes state change.

    Note: The house REMEMBERS being observed. Each observation
    reifies certain properties based on observer archetype.
    """

    state: HouseState = field(default_factory=HouseState)

    def scope(self, s: HouseState) -> Type[HouseInput]:
        """All inputs are always valid (for now)."""
        return HouseInput

    def dynamics(
        self,
        s: HouseState,
        input: HouseInput,
    ) -> tuple[HouseState, HouseOutput]:
        """
        Execute house dynamics.

        CRITICAL: Every branch updates state.
        """
        if isinstance(input, ObserveHouse):
            # Observation reifies properties
            new_properties = self._reify(input.observer_archetype)
            new_state = HouseState(
                observation_count=s.observation_count + 1,
                last_observer_archetype=input.observer_archetype,
                reified_properties=s.reified_properties | new_properties,
                version=s.version + 1,
            )
            view = self._render(input.observer_archetype, input.intent, new_state)
            return new_state, HouseOutput(
                view=view,
                state_delta={
                    "observed": True,
                    "reified": list(new_properties),
                },
            )

        elif isinstance(input, RenovateHouse):
            # Renovation changes properties
            new_state = HouseState(
                observation_count=s.observation_count,
                last_observer_archetype=s.last_observer_archetype,
                reified_properties=s.reified_properties,
                version=s.version + 1,
            )
            return new_state, HouseOutput(
                view={"status": "renovated"},
                state_delta=input.changes,
            )

        elif isinstance(input, InhabitHouse):
            # Inhabitation marks the house as lived-in
            new_state = HouseState(
                observation_count=s.observation_count,
                last_observer_archetype=s.last_observer_archetype,
                reified_properties=s.reified_properties | frozenset(["inhabited"]),
                version=s.version + 1,
            )
            return new_state, HouseOutput(
                view={"status": "inhabited"},
                state_delta={"inhabited_duration": input.duration},
            )

        else:
            # Unknown input - still update version
            new_state = HouseState(
                observation_count=s.observation_count,
                last_observer_archetype=s.last_observer_archetype,
                reified_properties=s.reified_properties,
                version=s.version + 1,
            )
            return new_state, HouseOutput(
                view={"error": "unknown input"},
                state_delta={},
            )

    def _reify(self, archetype: str) -> frozenset[str]:
        """Observation reifies properties based on who observes."""
        properties = {
            "architect": {
                "structural_integrity",
                "load_bearing_walls",
                "foundation_type",
            },
            "poet": {"atmosphere", "memories", "emotional_resonance"},
            "economist": {"market_value", "appreciation_rate", "comparable_sales"},
        }
        return frozenset(properties.get(archetype, {"exists", "location"}))

    def _render(
        self,
        archetype: str,
        intent: str,
        state: HouseState,
    ) -> dict[str, Any]:
        """Render the house for a specific observer."""
        base = {
            "observation_count": state.observation_count,
            "properties": list(state.reified_properties),
        }

        if archetype == "architect":
            base["blueprint"] = {"walls": 4, "floors": 2, "foundation": "concrete"}
        elif archetype == "poet":
            base["metaphor"] = "a vessel of memories"
        elif archetype == "economist":
            base["appraisal"] = {"value": 500000, "currency": "USD"}

        return base
