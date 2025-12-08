"""
Id (Identity) - The agent that does nothing.

Type: A → A
Law: Id(x) = x

The composition unit. Required by category-theoretic structure:
- Left identity:  Id ∘ f = f
- Right identity: f ∘ Id = f

Why irreducible: You cannot define identity in terms of anything simpler.
What it grounds: The existence of agents as a category.
"""

from typing import TypeVar, Any

from .types import Agent

A = TypeVar("A")


class Id(Agent[A, A]):
    """
    Identity agent: λx.x

    Usage:
        id_agent = Id()
        result = await id_agent.invoke(x)  # result == x

    Composition:
        Id() >> SomeAgent == SomeAgent
        SomeAgent >> Id() == SomeAgent
    """

    @property
    def name(self) -> str:
        return "Id"

    async def invoke(self, input: A) -> A:
        """Identity: returns input unchanged."""
        # Runtime verification that we truly return the same object
        result = input
        if result is not input:
            raise RuntimeError(
                f"Id agent violated identity law: input is not result (id mismatch)"
            )
        return result

    def __rshift__(self, other: "Agent[A, Any]") -> "Agent[A, Any]":
        """Right identity law: Id >> f = f"""
        # Optimization: composing with Id on the left is just the other agent
        return other

    def __repr__(self) -> str:
        return "Id()"
