"""
Polynomial Agent Protocol: Agents as Dynamical Systems.

Based on Spivak's "Polynomial Functors: A Mathematical Theory of Interaction",
this module provides the foundational protocol for polynomial agents.

A polynomial functor is:
    P(y) = Σ_{s ∈ Position} y^{Direction(s)}

This captures dynamical systems with:
- Positions: States the system can be in
- Directions: Inputs the system can receive at each position
- Transitions: How state × input → state × output

The key insight: Agents aren't just functions A → B, they're dynamical
systems with internal state and mode-dependent behavior.

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    FrozenSet,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

# Type variables for polynomial structure
S = TypeVar("S")  # State/Position type
A = TypeVar("A")  # Input/Direction type
B = TypeVar("B")  # Output type
S2 = TypeVar("S2")  # Second state type (for composition)
C = TypeVar("C")  # Third output type (for composition)


@runtime_checkable
class PolyAgentProtocol(Protocol[S, A, B]):
    """
    Protocol for polynomial agents.

    Every polynomial agent must expose:
    - positions: The set of valid states
    - directions: A function from state to valid inputs
    - transition: The state × input → (state, output) function
    """

    @property
    def name(self) -> str:
        """Agent name for identification."""
        ...

    @property
    def positions(self) -> FrozenSet[S]:
        """The set of valid states (positions in polynomial)."""
        ...

    def directions(self, state: S) -> FrozenSet[A]:
        """
        Valid inputs for a given state.

        This captures the mode-dependent behavior: different states
        accept different inputs.
        """
        ...

    def transition(self, state: S, input: A) -> tuple[S, B]:
        """
        State transition function.

        Given current state and valid input, produce:
        - New state
        - Output value
        """
        ...


@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """
    Immutable polynomial agent.

    This is the primary implementation of PolyAgentProtocol.
    Agents are frozen dataclasses for safe composition.

    Example:
        >>> id_agent = PolyAgent(
        ...     name="Id",
        ...     positions=frozenset({"ready"}),
        ...     _directions=lambda s: frozenset({Any}),
        ...     _transition=lambda s, x: ("ready", x)
        ... )
    """

    name: str
    positions: FrozenSet[S]
    _directions: Callable[[S], FrozenSet[A]]
    _transition: Callable[[S, A], tuple[S, B]]

    def directions(self, state: S) -> FrozenSet[A]:
        """Get valid inputs for state."""
        return self._directions(state)

    def transition(self, state: S, input: A) -> tuple[S, B]:
        """Execute state transition."""
        return self._transition(state, input)

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        """
        Execute one step of the dynamical system.

        Validates state and input before executing transition.

        Args:
            state: Current state (must be in positions)
            input: Input value (must be in directions(state))

        Returns:
            Tuple of (new_state, output)

        Raises:
            ValueError: If state or input is invalid
        """
        if state not in self.positions:
            raise ValueError(f"Invalid state: {state} not in {self.positions}")

        valid_inputs = self.directions(state)
        # Handle the "Any" case for universal acceptance
        if not _accepts_input(valid_inputs, input):
            raise ValueError(f"Invalid input {input} for state {state}")

        return self.transition(state, input)

    def run(self, initial: S, inputs: list[A]) -> tuple[S, list[B]]:
        """
        Run the system through a sequence of inputs.

        Args:
            initial: Starting state
            inputs: Sequence of inputs to process

        Returns:
            Tuple of (final_state, list_of_outputs)
        """
        state = initial
        outputs: list[B] = []
        for inp in inputs:
            state, out = self.invoke(state, inp)
            outputs.append(out)
        return state, outputs

    def __repr__(self) -> str:
        return f"PolyAgent({self.name}, positions={len(self.positions)})"


def _accepts_input(valid_inputs: FrozenSet[Any], input: Any) -> bool:
    """
    Check if input is accepted.

    Handles the special case where valid_inputs contains Any type
    to indicate universal acceptance.
    """
    # Check for Any type marker (universal acceptance)
    if Any in valid_inputs:
        return True
    if type in valid_inputs:
        # Type-based acceptance
        for t in valid_inputs:
            if isinstance(t, type) and isinstance(input, t):
                return True
    return input in valid_inputs


@dataclass
class WiringDiagram(Generic[S, S2, A, B, C]):
    """
    Wiring diagram for polynomial composition.

    Wiring diagrams are morphisms between polynomials, describing
    how to connect agents together.

    See: Spivak et al., "Wiring diagrams as organizing principle"
    """

    name: str
    left: PolyAgent[S, A, B]
    right: PolyAgent[S2, B, C]

    @property
    def composed_positions(self) -> FrozenSet[tuple[S, S2]]:
        """Product of position sets."""
        return frozenset(
            (s1, s2) for s1 in self.left.positions for s2 in self.right.positions
        )

    def compose(self) -> PolyAgent[tuple[S, S2], A, C]:
        """
        Compose two agents via wiring diagram.

        Returns a new PolyAgent that:
        - Has positions = left.positions × right.positions
        - Threads input through left, then right
        - Returns final output from right
        """

        def composed_directions(state: tuple[S, S2]) -> FrozenSet[A]:
            s1, _ = state
            return self.left.directions(s1)

        def composed_transition(
            state: tuple[S, S2], input: A
        ) -> tuple[tuple[S, S2], C]:
            s1, s2 = state
            new_s1, intermediate = self.left.transition(s1, input)
            new_s2, output = self.right.transition(s2, intermediate)
            return (new_s1, new_s2), output

        return PolyAgent(
            name=f"{self.left.name}>>{self.right.name}",
            positions=self.composed_positions,
            _directions=composed_directions,
            _transition=composed_transition,
        )


# =============================================================================
# Primitive Constructors
# =============================================================================


def identity(name: str = "Id") -> PolyAgent[str, Any, Any]:
    """
    Create the identity polynomial agent.

    The identity agent passes input through unchanged.
    It has a single "ready" state and accepts any input.
    """
    return PolyAgent(
        name=name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: ("ready", x),
    )


def constant(value: B, name: str = "Const") -> PolyAgent[str, Any, B]:
    """
    Create a constant polynomial agent.

    Always outputs the same value regardless of input.
    """
    return PolyAgent(
        name=name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: ("ready", value),
    )


def stateful(
    name: str,
    states: FrozenSet[S],
    initial: S,
    transition_fn: Callable[[S, A], tuple[S, B]],
    directions_fn: Callable[[S], FrozenSet[A]] | None = None,
) -> PolyAgent[S, A, B]:
    """
    Create a stateful polynomial agent.

    Args:
        name: Agent name
        states: Set of valid states
        initial: Initial state (must be in states)
        transition_fn: State transition function
        directions_fn: Optional function mapping state to valid inputs
                       (defaults to accepting Any)

    Returns:
        A PolyAgent with the specified behavior
    """

    def _default_directions(s: S) -> FrozenSet[Any]:
        return frozenset({Any})

    if directions_fn is None:
        directions_fn = _default_directions  # type: ignore[assignment]

    return PolyAgent(
        name=name,
        positions=states,
        _directions=directions_fn,
        _transition=transition_fn,
    )


def from_function(
    name: str,
    fn: Callable[[A], B],
) -> PolyAgent[str, A, B]:
    """
    Lift a pure function to a polynomial agent.

    The resulting agent has a single state and is stateless.
    This is the embedding of traditional functions into polynomial space.
    """
    return PolyAgent(
        name=name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),  # type: ignore[arg-type]
        _transition=lambda s, x: ("ready", fn(x)),
    )


# =============================================================================
# Composition Operations
# =============================================================================


def sequential(
    left: PolyAgent[S, A, B],
    right: PolyAgent[S2, B, C],
) -> PolyAgent[tuple[S, S2], A, C]:
    """
    Sequential composition: left >> right.

    Output of left feeds into input of right.
    State is the product of both agent states.
    """
    return WiringDiagram(
        name=f"seq({left.name},{right.name})",
        left=left,
        right=right,
    ).compose()


def parallel(
    left: PolyAgent[S, A, B],
    right: PolyAgent[S2, A, C],
) -> PolyAgent[tuple[S, S2], A, tuple[B, C]]:
    """
    Parallel composition: run both agents on same input.

    Both agents receive the same input, outputs are paired.
    State is the product of both agent states.
    """

    def par_directions(state: tuple[S, S2]) -> FrozenSet[A]:
        s1, s2 = state
        # Intersection of valid inputs
        left_dirs = left.directions(s1)
        right_dirs = right.directions(s2)
        # If either accepts Any, use the other's directions
        if Any in left_dirs:
            return right_dirs
        if Any in right_dirs:
            return left_dirs
        return left_dirs & right_dirs

    def par_transition(
        state: tuple[S, S2], input: A
    ) -> tuple[tuple[S, S2], tuple[B, C]]:
        s1, s2 = state
        new_s1, out1 = left.transition(s1, input)
        new_s2, out2 = right.transition(s2, input)
        return (new_s1, new_s2), (out1, out2)

    positions = frozenset((s1, s2) for s1 in left.positions for s2 in right.positions)

    return PolyAgent(
        name=f"par({left.name},{right.name})",
        positions=positions,
        _directions=par_directions,
        _transition=par_transition,
    )


# =============================================================================
# Deprecation Sugar: Agent[A, B] Compatibility
# =============================================================================


# Type alias for stateless agents (backwards compatibility)
# Agent[A, B] ≅ PolyAgent[str, A, B] where state is always "ready"
StatelessAgent = PolyAgent[str, A, B]
"""
Type alias for stateless polynomial agents.

This provides backwards compatibility with the Agent[A, B] pattern.
A StatelessAgent has a single "ready" state and accepts any input.

Usage:
    # Traditional Agent[A, B] pattern
    def double(x: int) -> int:
        return x * 2

    # Lift to polynomial space
    agent: StatelessAgent[int, int] = from_function("double", double)
"""


def to_bootstrap_agent(poly: PolyAgent[S, A, B]) -> Any:
    """
    Convert a PolyAgent to a bootstrap Agent-compatible wrapper.

    This enables polynomial agents to work with existing code expecting
    the Agent[A, B] interface.

    Note: Returns Any to avoid circular import with types module.

    Example:
        >>> poly = from_function("doubler", lambda x: x * 2)
        >>> agent = to_bootstrap_agent(poly)
        >>> await agent.invoke(21)  # Returns 42
    """
    from .types import Agent as BootstrapAgent

    class PolyAgentWrapper(BootstrapAgent[A, B]):
        """Wrapper that adapts PolyAgent to bootstrap Agent interface."""

        def __init__(self, poly_agent: PolyAgent[S, A, B], initial_state: S) -> None:
            self._poly = poly_agent
            self._state = initial_state

        @property
        def name(self) -> str:
            return self._poly.name

        async def invoke(self, input: A) -> B:
            """Execute the polynomial agent."""
            self._state, output = self._poly.transition(self._state, input)
            return output

    # Find initial state (first position, or "ready" for stateless)
    initial: S
    if "ready" in poly.positions:
        initial = "ready"  # type: ignore
    else:
        initial = next(iter(poly.positions))

    return PolyAgentWrapper(poly, initial)


def from_bootstrap_agent(agent: Any) -> PolyAgent[str, Any, Any]:
    """
    Convert a bootstrap Agent to a PolyAgent.

    The resulting polynomial has a single "ready" state.

    Note: Takes Any to avoid circular import with bootstrap.types.

    Example:
        >>> from agents import agent
        >>> @agent
        ... async def doubler(x: int) -> int:
        ...     return x * 2
        >>> poly = from_bootstrap_agent(doubler)
    """
    import asyncio

    def transition(state: str, input: Any) -> tuple[str, Any]:
        # Run the async invoke synchronously if needed
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context - this is problematic
            # Return a coroutine wrapper
            async def run() -> tuple[str, Any]:
                result = await agent.invoke(input)
                return "ready", result

            # For now, just document this limitation
            raise RuntimeError(
                "Cannot convert async agent in running event loop. "
                "Use to_bootstrap_agent() in the other direction instead."
            )
        else:
            result = loop.run_until_complete(agent.invoke(input))
            return "ready", result

    return PolyAgent(
        name=agent.name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=transition,
    )


__all__ = [
    # Protocol
    "PolyAgentProtocol",
    # Core Implementation
    "PolyAgent",
    "WiringDiagram",
    # Constructors
    "identity",
    "constant",
    "stateful",
    "from_function",
    # Composition
    "sequential",
    "parallel",
    # Deprecation Sugar
    "StatelessAgent",
    "to_bootstrap_agent",
    "from_bootstrap_agent",
]
