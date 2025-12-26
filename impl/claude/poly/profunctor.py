"""
LogosProfunctor - The Bridge Between Intent and Implementation.

This replaces the old Logos "God Object" with a modular Profunctor
that can have multiple instances (Real, Dream, Test).

Mathematical Foundation:
A profunctor is a functor P: C^op × D → Set
Contravariant in C, covariant in D.

This captures:
- Different intents can map to the same implementation
- Same intent can yield different implementations (context-dependent)

The profunctor structure enables:
- RealLogos: Production implementations
- DreamLogos: Hallucinated/simulated implementations
- TestLogos: Mocked interfaces for testing

Usage:
    logos = LogosComposition(
        resolver=MyResolver(),
        lifter=MyLifter(),
        ground=MyGround(),
    )

    interface = logos.bridge("world.house", observer=my_observer)
    output = interface.step(ObserveHouse("architect", "view"))
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, TypeVar

from .interface import PolyInterface
from .morphism import IdentityMorphism, PolyMorphism

if TYPE_CHECKING:
    pass


# Type variables
Intent = TypeVar("Intent", bound=str)


class LogosProfunctor(Protocol):
    """
    Maps: Intent -/-> PolyInterface

    A profunctor is contravariant in the first argument,
    covariant in the second. This captures:
    - Different intents can map to the same implementation
    - The same intent can yield different implementations
      depending on context (observer)

    This is NOT a function; it's a relation with structure.
    """

    def bridge(
        self,
        intent: str,
        observer: Any = None,
    ) -> PolyInterface[Any, Any, Any]:
        """
        Bridge intent to polynomial interface.

        Args:
            intent: The AGENTESE path (e.g., "world.house")
            observer: The requesting observer (provides context)

        Returns:
            A PolyInterface ready for dynamics() calls

        Note: This is NOT a lookup. The observer's state
        affects which interface is returned (polymorphism).
        """
        ...

    def lift(
        self,
        interface: PolyInterface[Any, Any, Any],
    ) -> PolyMorphism[Any, Any, Any, Any]:
        """
        Lift an interface into a composable morphism.

        Enables: logos.lift(P) >> logos.lift(Q)
        """
        ...


class PolyResolver(ABC):
    """
    Resolves AGENTESE paths to PolyInterfaces.

    This is the first component of the LogosComposition.
    """

    @abstractmethod
    def resolve(
        self,
        intent: str,
        observer: Any = None,
    ) -> PolyInterface[Any, Any, Any]:
        """Resolve intent string to interface."""
        ...

    @abstractmethod
    def can_resolve(self, intent: str) -> bool:
        """Check if this resolver handles the intent."""
        ...


class PolyLifter(ABC):
    """
    Lifts PolyInterfaces into composable morphisms.

    This is the second component of the LogosComposition.
    """

    @abstractmethod
    def lift(
        self,
        interface: PolyInterface[Any, Any, Any],
    ) -> PolyMorphism[Any, Any, Any, Any]:
        """Lift interface to morphism."""
        ...


class PolyGround(ABC):
    """
    Executes morphisms against the world.

    This is the third component of the LogosComposition.
    """

    @abstractmethod
    async def execute(
        self,
        morphism: PolyMorphism[Any, Any, Any, Any],
        input: Any,
    ) -> Any:
        """Execute a morphism with input."""
        ...


@dataclass
class LogosComposition:
    """
    Concrete implementation of LogosProfunctor.

    Decomposes into three modular components
    (Profunctor Optics pattern):
    - resolver: String → PolyInterface
    - lifter: Interface → Morphism
    - ground: Morphism → Execution

    This enables different "modes" of Logos:
    - RealLogos: resolver points to real implementations
    - DreamLogos: resolver points to hallucinated implementations
    - TestLogos: resolver points to mocks
    """

    resolver: PolyResolver
    lifter: PolyLifter
    ground: PolyGround

    def bridge(
        self,
        intent: str,
        observer: Any = None,
    ) -> PolyInterface[Any, Any, Any]:
        """Bridge intent to interface via resolver."""
        return self.resolver.resolve(intent, observer)

    def lift(
        self,
        interface: PolyInterface[Any, Any, Any],
    ) -> PolyMorphism[Any, Any, Any, Any]:
        """Lift interface to morphism via lifter."""
        return self.lifter.lift(interface)

    async def execute(
        self,
        morphism: PolyMorphism[Any, Any, Any, Any],
        input: Any,
    ) -> Any:
        """Execute morphism via ground."""
        return await self.ground.execute(morphism, input)

    def pipeline(
        self,
        *intents: str,
        observer: Any = None,
    ) -> PolyMorphism[Any, Any, Any, Any]:
        """
        Create a pipeline of interfaces composed as morphisms.

        Example:
            pipeline = logos.pipeline(
                "world.document.manifest",
                "concept.summary.refine",
                "self.memory.engram",
            )
        """
        morphisms = [self.lift(self.bridge(intent, observer)) for intent in intents]

        if not morphisms:
            return IdentityMorphism()

        result = morphisms[0]
        for m in morphisms[1:]:
            result = result >> m

        return result


# Default implementations


@dataclass
class DictResolver(PolyResolver):
    """
    Simple resolver using a dictionary mapping.

    Useful for testing and simple setups.
    """

    registry: dict[str, PolyInterface[Any, Any, Any]] = field(default_factory=dict)
    fallback: PolyInterface[Any, Any, Any] | None = None

    def resolve(
        self,
        intent: str,
        observer: Any = None,
    ) -> PolyInterface[Any, Any, Any]:
        if intent in self.registry:
            return self.registry[intent]
        if self.fallback is not None:
            return self.fallback
        raise KeyError(f"No interface registered for intent: {intent}")

    def can_resolve(self, intent: str) -> bool:
        return intent in self.registry or self.fallback is not None

    def register(
        self,
        intent: str,
        interface: PolyInterface[Any, Any, Any],
    ) -> None:
        """Register an interface for an intent."""
        self.registry[intent] = interface


@dataclass
class WrappingLifter(PolyLifter):
    """
    Lifter that wraps interfaces in a standard morphism.
    """

    def lift(
        self,
        interface: PolyInterface[Any, Any, Any],
    ) -> PolyMorphism[Any, Any, Any, Any]:
        return InterfaceMorphism(interface)


@dataclass
class InterfaceMorphism(PolyMorphism[Any, Any, Any, Any]):
    """
    A morphism that wraps a PolyInterface.

    Allows interfaces to participate in composition.
    """

    interface: PolyInterface[Any, Any, Any]

    def on_states(self, s: Any) -> Any:
        return self.interface.state

    def on_directions(self, s: Any, direction: Any) -> Any:
        return direction

    def apply(
        self,
        _interface: PolyInterface[Any, Any, Any],
        input: Any,
    ) -> tuple[Any, Any]:
        # Use our wrapped interface, not the passed one
        return self.interface.dynamics(self.interface.state, input)


@dataclass
class SyncGround(PolyGround):
    """
    Synchronous execution ground.

    Executes morphisms synchronously (wraps in async).
    """

    async def execute(
        self,
        morphism: PolyMorphism[Any, Any, Any, Any],
        input: Any,
    ) -> Any:
        # For sync ground, we need an interface to apply against
        # This is a simplified implementation
        if isinstance(morphism, InterfaceMorphism):
            _, output = morphism.apply(morphism.interface, input)
            return output
        raise ValueError("Morphism must be InterfaceMorphism for SyncGround")


@dataclass
class AsyncGround(PolyGround):
    """
    Asynchronous execution ground.

    For interfaces that need async execution.
    """

    executor: Callable[["PolyMorphism[Any, Any, Any, Any]", Any], Any] | None = None

    async def execute(
        self,
        morphism: PolyMorphism[Any, Any, Any, Any],
        input: Any,
    ) -> Any:
        if self.executor is not None:
            return await self.executor(morphism, input)
        # Default behavior
        if isinstance(morphism, InterfaceMorphism):
            _, output = morphism.apply(morphism.interface, input)
            return output
        raise ValueError("Morphism must be InterfaceMorphism")


# Factory functions


def create_real_logos(
    registry: dict[str, PolyInterface[Any, Any, Any]] | None = None,
) -> LogosComposition:
    """Create a production Logos instance."""
    return LogosComposition(
        resolver=DictResolver(registry=registry or {}),
        lifter=WrappingLifter(),
        ground=SyncGround(),
    )


def create_test_logos(
    mocks: dict[str, PolyInterface[Any, Any, Any]] | None = None,
) -> LogosComposition:
    """Create a test Logos instance with mocked interfaces."""
    return LogosComposition(
        resolver=DictResolver(registry=mocks or {}),
        lifter=WrappingLifter(),
        ground=SyncGround(),
    )


def create_dream_logos(
    hallucinator: Callable[[str], PolyInterface[Any, Any, Any]],
) -> LogosComposition:
    """
    Create a dream Logos that generates interfaces on-the-fly.

    The hallucinator function creates interfaces for any intent,
    useful for exploration and simulation.
    """

    @dataclass
    class DreamResolver(PolyResolver):
        hallucinate: Callable[[str], PolyInterface[Any, Any, Any]]

        def resolve(
            self,
            intent: str,
            observer: Any = None,
        ) -> PolyInterface[Any, Any, Any]:
            return self.hallucinate(intent)

        def can_resolve(self, intent: str) -> bool:
            return True  # Dreams can resolve anything

    return LogosComposition(
        resolver=DreamResolver(hallucinate=hallucinator),
        lifter=WrappingLifter(),
        ground=SyncGround(),
    )
