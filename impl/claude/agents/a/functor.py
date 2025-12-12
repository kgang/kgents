"""
Universal Functor Protocol: The Alethic Algebra Foundation.

This module provides the categorical foundation for all agent transformations.
Every functor in kgents (Maybe, Either, List, Flux, K-gent) derives from this protocol.

The Insight:
Traditional systems: Functors are ad-hoc implementations
Alethic: Functors satisfy universal laws, enabling composition

Laws (verified by BootstrapWitness):
1. Identity: F(id_A) = id_F(A)
2. Composition: F(g . f) = F(g) . F(f)

See: plans/architecture/alethic-algebra-tactics.md
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, Protocol, TypeVar, runtime_checkable

from bootstrap.types import Agent

# Type variables for the functor structure
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# Covariant type variable for functor output (used in protocols)
F_co = TypeVar("F_co", covariant=True)


# =============================================================================
# Core Protocol: UniversalFunctor
# =============================================================================


@runtime_checkable
class Liftable(Protocol[F_co]):
    """
    Protocol for types that can lift agents into a functor category.

    A Liftable F transforms Agent[A, B] -> Agent[F[A], F[B]] while preserving:
    - Identity: lift(id) behaves like identity in F's category
    - Composition: lift(g >> f) = lift(g) >> lift(f)

    This is the minimal interface every functor must implement.
    """

    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[Any, Any]:
        """
        Lift an agent into this functor's category.

        Args:
            agent: The source agent to lift

        Returns:
            The lifted agent operating in F's context
        """
        ...


@runtime_checkable
class Pointed(Protocol[F_co]):
    """
    Protocol for functors with a pure/return operation.

    A Pointed functor can embed raw values into its context.
    This is required for Applicative and Monad structure.
    """

    @staticmethod
    def pure(value: A) -> Any:
        """
        Embed a value into the functor's context.

        Args:
            value: The raw value to embed

        Returns:
            The value wrapped in F's context
        """
        ...


# Type variable for UniversalFunctor - invariant for class inheritance
F = TypeVar("F")


class UniversalFunctor(Generic[F]):
    """
    The Universal Functor - base class for all kgents functors.

    Provides:
    - lift(): Transform agents into the functor's category
    - unlift(): Extract agents from the functor's category (symmetric operation)
    - pure(): Embed values (when available)
    - Law verification helpers

    Subclasses must implement lift() and unlift(). pure() is optional.

    Symmetric Lifting Law:
        unlift(lift(agent)) ≅ agent

    Example:
        class MaybeFunctor(UniversalFunctor[Maybe]):
            @staticmethod
            def lift(agent: Agent[A, B]) -> Agent[Maybe[A], Maybe[B]]:
                return MaybeAgent(agent)

            @staticmethod
            def unlift(agent: MaybeAgent[A, B]) -> Agent[A, B]:
                return agent._inner

            @staticmethod
            def pure(value: A) -> Maybe[A]:
                return Just(value)
    """

    @staticmethod
    @abstractmethod
    def lift(agent: Agent[A, B]) -> Agent[Any, Any]:
        """
        Lift an agent into this functor's category.

        This is the fundamental operation of a functor:
        F: Agent[A,B] -> Agent[F[A], F[B]]

        Must satisfy:
        - F(id) behaves like identity in F's category
        - F(g >> f) = F(g) >> F(f)
        """
        raise NotImplementedError

    @staticmethod
    def unlift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
        """
        Extract the inner agent from a lifted agent.

        This is the inverse operation of lift:
        unlift: Agent[F[A], F[B]] -> Agent[A, B]

        Must satisfy the symmetric lifting law:
        unlift(lift(agent)) ≅ agent

        Note: Not all functors support this (e.g., some irreversible transformations).
        Override in subclasses that support symmetric lifting.
        """
        raise NotImplementedError("unlift() not supported for this functor")

    @staticmethod
    def pure(value: A) -> Any:
        """
        Embed a value into the functor's context.

        Not all functors support this (e.g., contravariant functors).
        Override in subclasses that support Pointed structure.
        """
        raise NotImplementedError("pure() not supported for this functor")


# =============================================================================
# Law Verification
# =============================================================================


@dataclass
class FunctorLawResult:
    """Result of verifying a functor law."""

    law_name: str
    passed: bool
    left_result: Any
    right_result: Any
    explanation: str


@dataclass
class FunctorVerificationReport:
    """Complete verification report for a functor."""

    functor_name: str
    identity_law: FunctorLawResult
    composition_law: FunctorLawResult

    @property
    def passed(self) -> bool:
        """True if all laws passed."""
        return self.identity_law.passed and self.composition_law.passed


async def verify_identity_law(
    functor: type[UniversalFunctor[Any]],
    identity_agent: Agent[A, A],
    test_input: Any,
) -> FunctorLawResult:
    """
    Verify functor identity law: F(id) = id_F

    The lifted identity agent should behave like identity
    in the functor's category.

    Args:
        functor: The functor type to verify
        identity_agent: An identity agent (input -> same input)
        test_input: Test input in the functor's context

    Returns:
        FunctorLawResult with verification details
    """
    try:
        # Lift the identity agent
        lifted = functor.lift(identity_agent)

        # Apply to test input
        result = await lifted.invoke(test_input)

        # In most functors, F(id)(x) = x
        # This is a structural check - the specific comparison
        # depends on the functor's equality semantics
        passed = result == test_input

        return FunctorLawResult(
            law_name="identity",
            passed=passed,
            left_result=result,
            right_result=test_input,
            explanation=f"F(id)({test_input}) = {result}, expected {test_input}",
        )

    except Exception as e:
        return FunctorLawResult(
            law_name="identity",
            passed=False,
            left_result=None,
            right_result=test_input,
            explanation=f"Identity law verification failed: {e}",
        )


async def verify_composition_law(
    functor: type[UniversalFunctor[Any]],
    f: Agent[A, B],
    g: Agent[B, C],
    test_input: Any,
) -> FunctorLawResult:
    """
    Verify functor composition law: F(g . f) = F(g) . F(f)

    Lifting a composed agent should equal composing lifted agents.

    Args:
        functor: The functor type to verify
        f: First agent (A -> B)
        g: Second agent (B -> C)
        test_input: Test input in the functor's context

    Returns:
        FunctorLawResult with verification details
    """
    try:
        # Left side: F(g . f)
        composed = f >> g
        lifted_composed = functor.lift(composed)
        left_result = await lifted_composed.invoke(test_input)

        # Right side: F(g) . F(f)
        lifted_f = functor.lift(f)
        lifted_g = functor.lift(g)
        lifted_composition = lifted_f >> lifted_g
        right_result = await lifted_composition.invoke(test_input)

        passed = left_result == right_result

        return FunctorLawResult(
            law_name="composition",
            passed=passed,
            left_result=left_result,
            right_result=right_result,
            explanation=f"F(g.f)={left_result}, F(g).F(f)={right_result}",
        )

    except Exception as e:
        return FunctorLawResult(
            law_name="composition",
            passed=False,
            left_result=None,
            right_result=None,
            explanation=f"Composition law verification failed: {e}",
        )


async def verify_functor(
    functor: type[UniversalFunctor[Any]],
    identity_agent: Agent[A, A],
    f: Agent[A, B],
    g: Agent[B, C],
    test_input: Any,
) -> FunctorVerificationReport:
    """
    Complete functor law verification.

    Args:
        functor: The functor type to verify
        identity_agent: Identity agent for identity law
        f, g: Agents for composition law
        test_input: Test input in functor's context

    Returns:
        FunctorVerificationReport with all law results
    """
    identity = await verify_identity_law(functor, identity_agent, test_input)
    composition = await verify_composition_law(functor, f, g, test_input)

    return FunctorVerificationReport(
        functor_name=functor.__name__,
        identity_law=identity,
        composition_law=composition,
    )


# =============================================================================
# Functor Combinators
# =============================================================================


def compose_functors(
    f: type[UniversalFunctor[Any]], g: type[UniversalFunctor[Any]]
) -> Callable[[Agent[A, B]], Agent[Any, Any]]:
    """
    Compose two functors: (F . G)(agent) = F(G(agent))

    Functor composition is associative and forms a category.

    Args:
        f: Outer functor
        g: Inner functor

    Returns:
        A function that lifts through both functors
    """

    def composed_lift(agent: Agent[A, B]) -> Agent[Any, Any]:
        return f.lift(g.lift(agent))

    return composed_lift


def identity_functor() -> type[UniversalFunctor[Any]]:
    """
    The identity functor: Id(agent) = agent

    This is the unit of functor composition.
    """

    class IdentityFunctor(UniversalFunctor[Any]):
        @staticmethod
        def lift(agent: Agent[A, B]) -> Agent[A, B]:
            return agent

    return IdentityFunctor


# =============================================================================
# Functor Registry
# =============================================================================


class FunctorRegistry:
    """
    Registry of all functors in kgents.

    Enables runtime discovery and verification of functors.
    Used by BootstrapWitness for comprehensive law checking.
    """

    _functors: dict[str, type[UniversalFunctor[Any]]] = {}

    @classmethod
    def register(cls, name: str, functor: type[UniversalFunctor[Any]]) -> None:
        """Register a functor with the registry."""
        cls._functors[name] = functor

    @classmethod
    def get(cls, name: str) -> type[UniversalFunctor[Any]] | None:
        """Get a functor by name."""
        return cls._functors.get(name)

    @classmethod
    def all_functors(cls) -> dict[str, type[UniversalFunctor[Any]]]:
        """Get all registered functors."""
        return cls._functors.copy()

    @classmethod
    async def verify_all(
        cls,
        identity_agent: Agent[A, A],
        f: Agent[A, B],
        g: Agent[B, C],
        test_input_factory: Callable[[str], Any],
    ) -> dict[str, FunctorVerificationReport]:
        """
        Verify all registered functors.

        Args:
            identity_agent: Identity agent for identity law
            f, g: Agents for composition law
            test_input_factory: Function to create test input for each functor

        Returns:
            Dict mapping functor names to verification reports
        """
        reports = {}
        for name, functor in cls._functors.items():
            test_input = test_input_factory(name)
            reports[name] = await verify_functor(
                functor, identity_agent, f, g, test_input
            )
        return reports


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core Protocol
    "UniversalFunctor",
    "Liftable",
    "Pointed",
    # Verification
    "FunctorLawResult",
    "FunctorVerificationReport",
    "verify_identity_law",
    "verify_composition_law",
    "verify_functor",
    # Combinators
    "compose_functors",
    "identity_functor",
    # Registry
    "FunctorRegistry",
]
