"""
PolyMorphism - Composable Interface Transformations.

Morphisms in the category Poly allow interfaces to compose.
This enables building complex systems from simple interfaces.

Mathematical Foundation:
A morphism between polynomial functors P → Q consists of:
    (on_states, on_directions)

where:
    on_states     : P_states → Q_states
    on_directions : Π_{p ∈ P_states} Q_directions(on_states(p)) → P_directions(p)

The key insight: Morphisms naturally encode state transition.
Composition is functorial: (f >> g) >> h = f >> (g >> h)

Usage:
    # Compose two interfaces
    composed = interface_a >> interface_b

    # Execute the composition
    result = composed.dynamics(initial_state, input)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Type, TypeVar

from .interface import BasePolyInterface, PolyInterface

# Type variables
S1 = TypeVar("S1")  # Source state
S2 = TypeVar("S2")  # Target state
A = TypeVar("A")  # Input
B = TypeVar("B")  # Intermediate output / input
C = TypeVar("C")  # Output


class PolyMorphism(ABC, Generic[S1, A, S2, B]):
    """
    A morphism between polynomial functors.

    Transforms one PolyInterface into another while
    preserving the dynamics structure.

    Morphisms compose via >> operator:
        (f >> g)(x) = g(f(x))
    """

    @abstractmethod
    def on_states(self, s: S1) -> S2:
        """Map states from source to target."""
        ...

    @abstractmethod
    def on_directions(self, s: S1, direction: B) -> A:
        """
        Map directions (inputs) from target back to source.

        Note: Directions go backwards (contravariant in first argument).
        """
        ...

    @abstractmethod
    def apply(
        self,
        interface: PolyInterface[S1, A, Any],
        input: B,
    ) -> tuple[S2, B]:
        """Apply the morphism to an interface."""
        ...

    def __rshift__(self, other: "PolyMorphism[Any, Any, Any, Any]") -> "ComposedMorphism":
        """Compose morphisms: f >> g means apply f then g."""
        return ComposedMorphism(self, other)


@dataclass
class IdentityMorphism(PolyMorphism[S1, A, S1, A]):
    """
    Identity morphism: does nothing.

    Required for category laws:
    - Id >> f = f
    - f >> Id = f
    """

    def on_states(self, s: S1) -> S1:
        return s

    def on_directions(self, s: S1, direction: A) -> A:
        return direction

    def apply(
        self,
        interface: PolyInterface[S1, A, Any],
        input: A,
    ) -> tuple[S1, A]:
        # Identity just passes through
        new_state, output = interface.dynamics(interface.state, input)
        return new_state, output


@dataclass
class ComposedMorphism(PolyMorphism[Any, Any, Any, Any]):
    """
    Composition of two morphisms.

    f >> g applies f first, then g.
    """

    first: "PolyMorphism[Any, Any, Any, Any]"
    second: "PolyMorphism[Any, Any, Any, Any]"

    def on_states(self, s: Any) -> Any:
        intermediate = self.first.on_states(s)
        return self.second.on_states(intermediate)

    def on_directions(self, s: Any, direction: Any) -> Any:
        # Directions compose in reverse order
        intermediate_dir = self.second.on_directions(self.first.on_states(s), direction)
        return self.first.on_directions(s, intermediate_dir)

    def apply(
        self,
        interface: PolyInterface[Any, Any, Any],
        input: Any,
    ) -> tuple[Any, Any]:
        # Apply first morphism
        intermediate_state, intermediate_output = self.first.apply(interface, input)

        # Create intermediate interface view
        # (This is a simplification - full implementation would need proper state management)
        return self.second.on_states(intermediate_state), intermediate_output


@dataclass
class MapMorphism(PolyMorphism[S1, A, S2, B]):
    """
    A morphism defined by explicit mapping functions.

    Useful for simple transformations.
    """

    state_map: Callable[[S1], S2]
    direction_map: Callable[[S1, B], A]
    output_map: Callable[[Any], B] = field(default=lambda x: x)

    def on_states(self, s: S1) -> S2:
        return self.state_map(s)

    def on_directions(self, s: S1, direction: B) -> A:
        return self.direction_map(s, direction)

    def apply(
        self,
        interface: PolyInterface[S1, A, Any],
        input: B,
    ) -> tuple[S2, B]:
        # Map input to source domain
        source_input = self.on_directions(interface.state, input)

        # Execute dynamics
        new_state, output = interface.dynamics(interface.state, source_input)

        # Map state and output to target domain
        return self.on_states(new_state), self.output_map(output)


@dataclass
class FilterMorphism(PolyMorphism[S1, A, S1, A]):
    """
    A morphism that filters inputs based on predicate.

    Only allows inputs that pass the filter.
    """

    predicate: Callable[[S1, A], bool]
    default_output: Any = None

    def on_states(self, s: S1) -> S1:
        return s

    def on_directions(self, s: S1, direction: A) -> A:
        return direction

    def apply(
        self,
        interface: PolyInterface[S1, A, Any],
        input: A,
    ) -> tuple[S1, Any]:
        if self.predicate(interface.state, input):
            return interface.dynamics(interface.state, input)
        else:
            # Return unchanged state with default output
            return interface.state, self.default_output


@dataclass
class LiftMorphism(PolyMorphism[S1, A, S1, A]):
    """
    A morphism that lifts a function to operate on outputs.

    Applies a transformation to the output without
    changing the state handling.
    """

    transform: Callable[[Any], Any]

    def on_states(self, s: S1) -> S1:
        return s

    def on_directions(self, s: S1, direction: A) -> A:
        return direction

    def apply(
        self,
        interface: PolyInterface[S1, A, Any],
        input: A,
    ) -> tuple[S1, Any]:
        new_state, output = interface.dynamics(interface.state, input)
        return new_state, self.transform(output)


# Utility functions


def identity() -> "IdentityMorphism[Any, Any]":
    """Create an identity morphism."""
    return IdentityMorphism()


def map_output(f: Callable[[Any], Any]) -> "LiftMorphism[Any, Any]":
    """Create a morphism that transforms outputs."""
    return LiftMorphism(transform=f)


def filter_input(predicate: Callable[[Any, Any], bool]) -> "FilterMorphism[Any, Any]":
    """Create a morphism that filters inputs."""
    return FilterMorphism(predicate=predicate)


# Morphism laws verification


def verify_identity_law_left(
    morphism: "PolyMorphism[Any, Any, Any, Any]",
    interface: PolyInterface[Any, Any, Any],
    input: Any,
) -> bool:
    """Verify: Id >> f = f"""
    id_morphism = identity()
    composed = id_morphism >> morphism

    # Apply both and compare
    result1 = composed.apply(interface, input)
    result2 = morphism.apply(interface, input)

    return result1 == result2


def verify_identity_law_right(
    morphism: "PolyMorphism[Any, Any, Any, Any]",
    interface: PolyInterface[Any, Any, Any],
    input: Any,
) -> bool:
    """Verify: f >> Id = f"""
    id_morphism = identity()
    composed = morphism >> id_morphism

    # Apply both and compare
    result1 = composed.apply(interface, input)
    result2 = morphism.apply(interface, input)

    return result1 == result2


def verify_associativity(
    f: "PolyMorphism[Any, Any, Any, Any]",
    g: "PolyMorphism[Any, Any, Any, Any]",
    h: "PolyMorphism[Any, Any, Any, Any]",
    interface: PolyInterface[Any, Any, Any],
    input: Any,
) -> bool:
    """Verify: (f >> g) >> h = f >> (g >> h)"""
    left = (f >> g) >> h
    right = f >> (g >> h)

    # Apply both and compare
    result_left = left.apply(interface, input)
    result_right = right.apply(interface, input)

    return result_left == result_right
