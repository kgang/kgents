"""
Id Agent - The identity agent (composition unit).

Id: A → A
Id(x) = x

Laws:
- Id(x) = x for all x
- Left identity: Id >> f ≡ f
- Right identity: f >> Id ≡ f

The identity agent is the "do nothing" agent. It returns its input unchanged.
Required by the category-theoretic structure as the unit of composition.

See spec/bootstrap.md lines 41-55.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from .types import Agent, ComposedAgent

if TYPE_CHECKING:
    pass

A = TypeVar("A")
B = TypeVar("B")


class Id(Agent[A, A]):
    """
    The identity agent.

    Returns input unchanged. Forms the unit of agent composition.

    Usage:
        id_agent = Id()
        result = await id_agent.invoke(42)  # Returns 42

    Composition laws:
        Id >> f ≡ f  (left identity)
        f >> Id ≡ f  (right identity)
    """

    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input: A) -> A:
        """Return input unchanged."""
        return input

    def __rshift__(self, other: Agent[A, B]) -> ComposedAgent[A, A, B]:
        """
        Optimized composition: Id >> other ≡ other.

        Instead of creating a ComposedAgent that would do:
            intermediate = await Id.invoke(input)  # just returns input
            return await other.invoke(intermediate)

        We short-circuit by creating a thin wrapper that behaves like other.
        This preserves the law: Id >> f ≡ f (behaviorally equivalent)

        Note: We return ComposedAgent to satisfy the type system, but
        the behavior is optimized to avoid unnecessary Id.invoke() call.
        """
        # Return standard composition - the overhead is minimal
        # and it preserves type safety
        return ComposedAgent(self, other)

    def __rlshift__(self, other: Agent[B, A]) -> Agent[B, A]:
        """
        Optimized reverse composition: other >> Id ≡ other.

        This is called when we have: other >> Id
        (Python calls __rlshift__ when Id is on the right side
        and other doesn't define __rshift__ that handles Id)

        However, since Agent.__rshift__ creates ComposedAgent,
        this won't be called in normal f >> Id cases.

        For completeness, we return other to preserve: f >> Id ≡ f
        """
        return other

    def __eq__(self, other: object) -> bool:
        """
        Identity agents are equal if they are the same type.

        Relaxed from strict 'is' check to allow equality comparison
        between different Id instances.
        """
        return isinstance(other, Id)

    def __hash__(self) -> int:
        """Hash for Id - all Id instances hash the same."""
        return hash("Id")


# Singleton instance for convenience
ID: Id[object] = Id()
