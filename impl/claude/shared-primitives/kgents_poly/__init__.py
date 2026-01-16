"""
kgents-poly: Polynomial State Machines for Everyone

A lightweight library for building mode-dependent state machines
based on polynomial functors.

Quick Start (10 minutes or less):

    from kgents_poly import PolyAgent, from_function, sequential

    # Lift a function to an agent
    doubler = from_function("double", lambda x: x * 2)

    # Run it
    state, output = doubler.invoke("ready", 21)
    # output = 42

    # Compose agents
    composed = sequential(doubler, from_function("add_one", lambda x: x + 1))
    _, result = composed.invoke(("ready", "ready"), 21)
    # result = 43

What is a PolyAgent?

    A PolyAgent is a dynamical system with:
    - Positions: The states the system can be in
    - Directions: What inputs are valid at each position
    - Transitions: How state + input produces (new_state, output)

    The key insight: Different states accept different inputs.
    This is "mode-dependent behavior" - a PolyAgent in state "loading"
    might only accept "cancel" or "retry", while in state "ready" it
    accepts any action.

Why not just use classes?

    PolyAgent is immutable and composable. You can:
    - Chain agents with sequential() or >>
    - Run them in parallel with parallel()
    - Verify composition laws automatically

License: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
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

# Protocol-specific type variables with proper variance
B_co = TypeVar("B_co", covariant=True)  # Output type for protocols (covariant)


# -----------------------------------------------------------------------------
# Protocol: The Interface
# -----------------------------------------------------------------------------


@runtime_checkable
class PolyAgentProtocol(Protocol[S, A, B_co]):
    """
    Protocol for polynomial agents.

    Every polynomial agent exposes:
    - positions: The set of valid states
    - directions: Valid inputs for each state
    - transition: The state x input -> (state, output) function

    Example:
        >>> class MyAgent:
        ...     @property
        ...     def name(self) -> str:
        ...         return "my_agent"
        ...
        ...     @property
        ...     def positions(self) -> frozenset[str]:
        ...         return frozenset({"ready", "busy"})
        ...
        ...     def directions(self, state: str) -> frozenset[str]:
        ...         if state == "ready":
        ...             return frozenset({"start"})
        ...         return frozenset({"cancel"})
        ...
        ...     def transition(self, state: str, input: str) -> tuple[str, str]:
        ...         if state == "ready" and input == "start":
        ...             return ("busy", "started!")
        ...         return ("ready", "cancelled")
        ...
        >>> agent = MyAgent()
        >>> isinstance(agent, PolyAgentProtocol)
        True
    """

    @property
    def name(self) -> str:
        """Agent name for identification."""
        ...

    @property
    def positions(self) -> frozenset[S]:
        """The set of valid states (positions in polynomial)."""
        ...

    def directions(self, state: S) -> frozenset[A]:
        """
        Valid inputs for a given state.

        This captures mode-dependent behavior: different states
        accept different inputs.
        """
        ...

    def transition(self, state: S, input: A) -> tuple[S, B_co]:
        """
        State transition function.

        Given current state and valid input, produce:
        - New state
        - Output value
        """
        ...


# -----------------------------------------------------------------------------
# Core Implementation
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """
    Immutable polynomial agent.

    A PolyAgent represents a state machine where:
    - positions = the set of valid states
    - directions(state) = valid inputs at that state
    - transition(state, input) = (new_state, output)

    Example:
        >>> # Simple counter agent
        >>> counter = PolyAgent(
        ...     name="counter",
        ...     positions=frozenset(range(10)),
        ...     _directions=lambda s: frozenset(["inc", "dec", "get"]),
        ...     _transition=lambda s, inp: (
        ...         (min(9, s + 1), s + 1) if inp == "inc" else
        ...         (max(0, s - 1), s - 1) if inp == "dec" else
        ...         (s, s)
        ...     )
        ... )
        >>> state, value = counter.invoke(0, "inc")
        >>> print(value)  # 1

    Tips:
        - Use frozenset({Any}) in directions to accept any input
        - PolyAgents are immutable - invoke() returns new state, doesn't mutate
        - Use run() for processing sequences of inputs
    """

    name: str
    positions: frozenset[S]
    _directions: Callable[[S], frozenset[A]]
    _transition: Callable[[S, A], tuple[S, B]]

    def directions(self, state: S) -> frozenset[A]:
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

        Example:
            >>> agent = from_function("double", lambda x: x * 2)
            >>> state, output = agent.invoke("ready", 21)
            >>> print(output)  # 42
        """
        if state not in self.positions:
            raise ValueError(
                f"Invalid state: {state!r}. Valid states: {self.positions}"
            )

        valid_inputs = self.directions(state)
        if not _accepts_input(valid_inputs, input):
            raise ValueError(
                f"Invalid input {input!r} for state {state!r}. "
                f"Valid inputs: {valid_inputs}"
            )

        return self.transition(state, input)

    def run(self, initial: S, inputs: list[A]) -> tuple[S, list[B]]:
        """
        Run the system through a sequence of inputs.

        Args:
            initial: Starting state
            inputs: Sequence of inputs to process

        Returns:
            Tuple of (final_state, list_of_outputs)

        Example:
            >>> agent = from_function("double", lambda x: x * 2)
            >>> state, outputs = agent.run("ready", [1, 2, 3])
            >>> print(outputs)  # [2, 4, 6]
        """
        state = initial
        outputs: list[B] = []
        for inp in inputs:
            state, out = self.invoke(state, inp)
            outputs.append(out)
        return state, outputs

    def __rshift__(self, other: PolyAgent[S2, B, C]) -> PolyAgent[tuple[S, S2], A, C]:
        """
        Composition operator: self >> other

        Chains this agent with another: output of self feeds into input of other.

        Example:
            >>> double = from_function("double", lambda x: x * 2)
            >>> add_one = from_function("add_one", lambda x: x + 1)
            >>> composed = double >> add_one
            >>> _, result = composed.invoke(("ready", "ready"), 10)
            >>> print(result)  # 21
        """
        return sequential(self, other)

    def map(self, f: Callable[[B], C]) -> PolyAgent[S, A, C]:
        """
        Apply a function to the output.

        The state machine behavior is unchanged, but outputs are transformed.

        Example:
            >>> agent = from_function("get", lambda x: x)
            >>> upper = agent.map(lambda s: s.upper())
            >>> _, result = upper.invoke("ready", "hello")
            >>> print(result)  # "HELLO"
        """

        def new_transition(state: S, input: A) -> tuple[S, C]:
            new_state, output = self._transition(state, input)
            return new_state, f(output)

        return PolyAgent(
            name=f"map({self.name})",
            positions=self.positions,
            _directions=self._directions,
            _transition=new_transition,
        )

    def __repr__(self) -> str:
        return f"PolyAgent({self.name!r}, positions={len(self.positions)})"


def _accepts_input(valid_inputs: frozenset[Any], input: Any) -> bool:
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


# -----------------------------------------------------------------------------
# Constructors: Easy Ways to Create Agents
# -----------------------------------------------------------------------------


def identity(name: str = "Id") -> PolyAgent[str, Any, Any]:
    """
    Create the identity agent.

    The identity agent passes input through unchanged.
    It has a single "ready" state and accepts any input.

    Example:
        >>> id_agent = identity()
        >>> _, result = id_agent.invoke("ready", "hello")
        >>> print(result)  # "hello"
    """
    return PolyAgent(
        name=name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: ("ready", x),
    )


def constant(value: B, name: str = "Const") -> PolyAgent[str, Any, B]:
    """
    Create a constant agent.

    Always outputs the same value regardless of input.

    Example:
        >>> always_42 = constant(42)
        >>> _, result = always_42.invoke("ready", "anything")
        >>> print(result)  # 42
    """
    return PolyAgent(
        name=name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: ("ready", value),
    )


def from_function(
    name: str,
    fn: Callable[[A], B],
) -> PolyAgent[str, A, B]:
    """
    Lift a pure function to a polynomial agent.

    The resulting agent has a single "ready" state and is stateless.
    This is the easiest way to create an agent.

    Example:
        >>> double = from_function("double", lambda x: x * 2)
        >>> _, result = double.invoke("ready", 21)
        >>> print(result)  # 42

        >>> # Compose with >> operator
        >>> add_one = from_function("add_one", lambda x: x + 1)
        >>> composed = double >> add_one
        >>> _, result = composed.invoke(("ready", "ready"), 10)
        >>> print(result)  # 21
    """
    return PolyAgent(
        name=name,
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),  # type: ignore[arg-type]
        _transition=lambda s, x: ("ready", fn(x)),
    )


def stateful(
    name: str,
    states: frozenset[S],
    transition_fn: Callable[[S, A], tuple[S, B]],
    directions_fn: Callable[[S], frozenset[A]] | None = None,
) -> PolyAgent[S, A, B]:
    """
    Create a stateful polynomial agent.

    Args:
        name: Agent name
        states: Set of valid states
        transition_fn: State transition function
        directions_fn: Optional function mapping state to valid inputs
                       (defaults to accepting Any)

    Returns:
        A PolyAgent with the specified behavior

    Example:
        >>> # Traffic light that cycles: red -> green -> yellow -> red
        >>> light = stateful(
        ...     name="traffic_light",
        ...     states=frozenset({"red", "green", "yellow"}),
        ...     transition_fn=lambda state, _: {
        ...         "red": ("green", "go"),
        ...         "green": ("yellow", "slow"),
        ...         "yellow": ("red", "stop"),
        ...     }[state]
        ... )
        >>> state, output = light.invoke("red", "tick")
        >>> print(state, output)  # green, go
    """

    def _default_directions(s: S) -> frozenset[Any]:
        return frozenset({Any})

    if directions_fn is None:
        directions_fn = _default_directions

    return PolyAgent(
        name=name,
        positions=states,
        _directions=directions_fn,
        _transition=transition_fn,
    )


# -----------------------------------------------------------------------------
# Composition: Combining Agents
# -----------------------------------------------------------------------------


def sequential(
    left: PolyAgent[S, A, B],
    right: PolyAgent[S2, B, C],
) -> PolyAgent[tuple[S, S2], A, C]:
    """
    Sequential composition: left >> right.

    Output of left feeds into input of right.
    State is the product of both agent states.

    Example:
        >>> double = from_function("double", lambda x: x * 2)
        >>> add_one = from_function("add_one", lambda x: x + 1)
        >>> composed = sequential(double, add_one)
        >>> _, result = composed.invoke(("ready", "ready"), 10)
        >>> print(result)  # 21
    """
    positions = frozenset((s1, s2) for s1 in left.positions for s2 in right.positions)

    def composed_directions(state: tuple[S, S2]) -> frozenset[A]:
        s1, _ = state
        return left.directions(s1)

    def composed_transition(state: tuple[S, S2], input: A) -> tuple[tuple[S, S2], C]:
        s1, s2 = state
        new_s1, intermediate = left.transition(s1, input)
        new_s2, output = right.transition(s2, intermediate)
        return (new_s1, new_s2), output

    return PolyAgent(
        name=f"{left.name}>>{right.name}",
        positions=positions,
        _directions=composed_directions,
        _transition=composed_transition,
    )


def parallel(
    left: PolyAgent[S, A, B],
    right: PolyAgent[S2, A, C],
) -> PolyAgent[tuple[S, S2], A, tuple[B, C]]:
    """
    Parallel composition: run both agents on same input.

    Both agents receive the same input, outputs are paired.
    State is the product of both agent states.

    Example:
        >>> double = from_function("double", lambda x: x * 2)
        >>> square = from_function("square", lambda x: x * x)
        >>> both = parallel(double, square)
        >>> _, result = both.invoke(("ready", "ready"), 3)
        >>> print(result)  # (6, 9)
    """
    positions = frozenset((s1, s2) for s1 in left.positions for s2 in right.positions)

    def par_directions(state: tuple[S, S2]) -> frozenset[A]:
        s1, s2 = state
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

    return PolyAgent(
        name=f"({left.name}|{right.name})",
        positions=positions,
        _directions=par_directions,
        _transition=par_transition,
    )


# -----------------------------------------------------------------------------
# Wiring Diagram: Advanced Composition
# -----------------------------------------------------------------------------


@dataclass
class WiringDiagram(Generic[S, S2, A, B, C]):
    """
    Wiring diagram for polynomial composition.

    Wiring diagrams describe how to connect agents together.
    This is the categorical machinery behind sequential composition.

    For most use cases, prefer sequential() or the >> operator.
    Use WiringDiagram when you need fine-grained control.
    """

    name: str
    left: PolyAgent[S, A, B]
    right: PolyAgent[S2, B, C]

    @property
    def composed_positions(self) -> frozenset[tuple[S, S2]]:
        """Product of position sets."""
        return frozenset(
            (s1, s2) for s1 in self.left.positions for s2 in self.right.positions
        )

    def compose(self) -> PolyAgent[tuple[S, S2], A, C]:
        """Compose the agents."""
        return sequential(self.left, self.right)


# Type alias for stateless agents
StatelessAgent = PolyAgent[str, A, B]


__all__ = [
    # Protocol
    "PolyAgentProtocol",
    # Core Implementation
    "PolyAgent",
    "WiringDiagram",
    # Constructors
    "identity",
    "constant",
    "from_function",
    "stateful",
    # Composition
    "sequential",
    "parallel",
    # Type alias
    "StatelessAgent",
]
