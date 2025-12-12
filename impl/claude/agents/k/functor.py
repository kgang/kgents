"""
Soul Functor: The Categorical Imperative.

The Soul Functor lifts agents to operate with persona/soul awareness:

    Soul: Agent[A, B] → Agent[Soul[A], Soul[B]]

Where Soul[T] represents T enriched with persona context.

Functor Laws:
    Identity:    Soul(Id) ≅ Id_Soul
    Composition: Soul(f >> g) ≅ Soul(f) >> Soul(g)

The Categorical Imperative:
    "Act only according to that maxim whereby you can at the same time
     will that it should become a universal law."

In K-gent terms: Agents lifted through Soul operate through the lens of
identity—Kent's eigenvectors, preferences, and principles. The soul context
transforms agent behavior without changing the agent's core logic.

Universal Functor Integration (Alethic Algebra Phase 4):
    SoulFunctor implements UniversalFunctor[SoulAgent], enabling:
    - Law verification via verify_functor()
    - Registry integration with other functors
    - Functor composition: compose_functors(SoulFunctor, MaybeFunctor)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

from agents.a.functor import FunctorRegistry, UniversalFunctor
from bootstrap.types import Agent, ComposedAgent

from .eigenvectors import KENT_EIGENVECTORS, KentEigenvectors
from .persona import PersonaSeed, PersonaState

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# =============================================================================
# Soul Context: The Container
# =============================================================================


@dataclass
class Soul(Generic[A]):
    """
    Soul context wrapper for values.

    A Soul[A] is a value A enriched with persona context. The context
    includes eigenvectors (personality coordinates), preferences, and
    principles that inform how agents should process the value.

    This is the "effect" in our functor: values wrapped in soul carry
    persona awareness that can influence behavior.

    Example:
        >>> raw_input = "Should I add more features?"
        >>> soul_input = Soul(raw_input, eigenvectors=KENT_EIGENVECTORS)
        >>> # Now agents can access the minimalist aesthetic preference
    """

    value: A
    eigenvectors: KentEigenvectors = field(default_factory=lambda: KENT_EIGENVECTORS)
    persona: Optional[PersonaState] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        """Equality based on value and context."""
        if not isinstance(other, Soul):
            return NotImplemented
        return (
            self.value == other.value
            and self.eigenvectors == other.eigenvectors
            and self.persona == other.persona
        )

    def __repr__(self) -> str:
        return f"Soul({self.value!r})"

    def map(self, f: Any) -> "Soul[Any]":
        """Apply a function to the wrapped value, preserving context."""
        return Soul(
            value=f(self.value),
            eigenvectors=self.eigenvectors,
            persona=self.persona,
            metadata=self.metadata.copy(),
        )

    def with_metadata(self, key: str, value: Any) -> "Soul[A]":
        """Add metadata while preserving context."""
        new_metadata = self.metadata.copy()
        new_metadata[key] = value
        return Soul(
            value=self.value,
            eigenvectors=self.eigenvectors,
            persona=self.persona,
            metadata=new_metadata,
        )

    @property
    def context_prompt(self) -> str:
        """Generate a context prompt from soul state."""
        return self.eigenvectors.to_context_prompt()


# =============================================================================
# SoulAgent: The Lifted Agent
# =============================================================================


class SoulAgent(Agent[Soul[A], Soul[B]]):
    """
    An agent lifted to operate with soul context.

    SoulAgent wraps an inner agent (Agent[A, B]) and transforms it to
    operate on Soul[A] -> Soul[B]. The soul context (eigenvectors, persona)
    flows through the computation, potentially influencing behavior.

    The key insight: The inner agent processes raw values, but the context
    travels alongside. This enables:
    - Persona-aware logging and tracing
    - Principle-aligned decision making
    - Identity-preserving transformations
    """

    def __init__(
        self,
        inner: Agent[A, B],
        default_eigenvectors: KentEigenvectors | None = None,
        default_persona: PersonaState | None = None,
    ) -> None:
        """
        Create a soul-lifted agent.

        Args:
            inner: The underlying agent to lift
            default_eigenvectors: Default eigenvectors if input has none
            default_persona: Default persona state if input has none
        """
        self._inner = inner
        self._default_eigenvectors = default_eigenvectors or KENT_EIGENVECTORS
        self._default_persona = default_persona

    @property
    def name(self) -> str:
        """Name of the lifted agent."""
        return f"Soul({self._inner.name})"

    @property
    def inner(self) -> Agent[A, B]:
        """Access the inner (unlifted) agent."""
        return self._inner

    async def invoke(self, input: Soul[A]) -> Soul[B]:
        """
        Invoke the inner agent, preserving soul context.

        The soul context (eigenvectors, persona) flows through unchanged,
        while the inner agent processes the wrapped value.
        """
        # Extract value and process through inner agent
        result = await self._inner.invoke(input.value)

        # Wrap result in soul context, preserving the input's context
        return Soul(
            value=result,
            eigenvectors=input.eigenvectors,
            persona=input.persona,
            metadata=input.metadata.copy(),
        )

    def __rshift__(
        self, other: "Agent[Soul[B], C]"
    ) -> "ComposedAgent[Soul[A], Soul[B], C]":
        """Compose with another soul-aware agent."""
        return ComposedAgent(self, other)


# =============================================================================
# SoulFunctor: The Universal Functor
# =============================================================================


class SoulFunctor(UniversalFunctor[SoulAgent[Any, Any]]):
    """
    Universal Functor for Soul (K-gent persona) context.

    Lifts agents from the raw domain (Agent[A, B]) to the soul-aware
    domain (SoulAgent[A, B]) where values carry persona context.

    The Categorical Imperative:
        Agents lifted through Soul act through the lens of identity.
        The persona (eigenvectors, preferences, principles) enriches
        every value without altering the agent's core logic.

    Satisfies functor laws:
    - Identity: SoulFunctor.lift(id) preserves identity through soul
    - Composition: SoulFunctor.lift(g . f) = SoulFunctor.lift(g) . SoulFunctor.lift(f)

    Example:
        >>> lifted = SoulFunctor.lift(my_agent)
        >>> result = await lifted.invoke(Soul(input_value))
        >>> # result is Soul[B] with preserved persona context
    """

    @staticmethod
    def lift(agent: Agent[A, B]) -> SoulAgent[A, B]:
        """
        Lift an agent to operate with soul context.

        This is the core functor operation. It takes a raw agent
        (one that processes plain values) and lifts it to the soul
        domain (one that processes and produces soul-wrapped values).

        Args:
            agent: The raw agent to lift

        Returns:
            SoulAgent wrapping the input agent
        """
        return SoulAgent(inner=agent)

    @staticmethod
    def pure(value: A) -> Soul[A]:
        """
        Embed a value in the soul context.

        In the Soul context, pure wraps a raw value with the default
        persona context (KENT_EIGENVECTORS). This satisfies the Pointed
        functor requirement.

        Args:
            value: The raw value to embed

        Returns:
            Soul[A] with default persona context
        """
        return Soul(value=value)

    @staticmethod
    def lift_with_persona(
        agent: Agent[A, B],
        eigenvectors: KentEigenvectors | None = None,
        persona: PersonaState | None = None,
    ) -> SoulAgent[A, B]:
        """
        Lift an agent with explicit persona configuration.

        This variant allows specifying the default eigenvectors and
        persona state for the lifted agent.

        Args:
            agent: The raw agent to lift
            eigenvectors: Custom eigenvectors (defaults to KENT_EIGENVECTORS)
            persona: Custom persona state

        Returns:
            SoulAgent with specified persona defaults
        """
        return SoulAgent(
            inner=agent,
            default_eigenvectors=eigenvectors,
            default_persona=persona,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def soul_lift(agent: Agent[A, B]) -> SoulAgent[A, B]:
    """
    Lift an agent to the soul domain.

    Convenience function for SoulFunctor.lift().

    Example:
        >>> lifted = soul_lift(my_agent)
        >>> result = await lifted.invoke(Soul(input))
    """
    return SoulFunctor.lift(agent)


def soul(value: A) -> Soul[A]:
    """
    Embed a value in soul context.

    Convenience function for SoulFunctor.pure().

    Example:
        >>> s = soul("What should I prioritize?")
        >>> s.eigenvectors.aesthetic.value  # 0.15 (minimalist)
    """
    return SoulFunctor.pure(value)


def soul_with(
    value: A,
    eigenvectors: KentEigenvectors | None = None,
    persona: PersonaState | None = None,
    **metadata: Any,
) -> Soul[A]:
    """
    Create a soul with explicit context.

    Args:
        value: The raw value to wrap
        eigenvectors: Custom eigenvectors
        persona: Custom persona state
        **metadata: Additional metadata

    Returns:
        Soul[A] with specified context
    """
    return Soul(
        value=value,
        eigenvectors=eigenvectors or KENT_EIGENVECTORS,
        persona=persona,
        metadata=metadata,
    )


def unlift(soul_agent: SoulAgent[A, B]) -> Agent[A, B]:
    """
    Extract inner agent from soul wrapper.

    Args:
        soul_agent: The SoulAgent to unwrap

    Returns:
        The inner raw agent
    """
    return soul_agent.inner


def unwrap(soul_value: Soul[A]) -> A:
    """
    Extract raw value from soul wrapper.

    Args:
        soul_value: The Soul[A] to unwrap

    Returns:
        The inner raw value
    """
    return soul_value.value


# =============================================================================
# Registry
# =============================================================================


def _register_soul_functor() -> None:
    """Register SoulFunctor with the universal registry."""
    FunctorRegistry.register("Soul", SoulFunctor)


# Auto-register on import
_register_soul_functor()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "Soul",
    "SoulAgent",
    "SoulFunctor",
    # Convenience functions
    "soul_lift",
    "soul",
    "soul_with",
    "unlift",
    "unwrap",
]
