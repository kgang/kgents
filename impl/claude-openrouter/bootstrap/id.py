"""
Id Agent (Identity)

Id: A → A
Id(x) = x

The agent that does nothing. Required by the category-theoretic structure:
- Left identity: Id ∘ f = f
- Right identity: f ∘ Id = f

Why irreducible: You cannot define identity in terms of anything simpler.
                 It is the unit of composition.
"""

from typing import TypeVar
from .types import Agent

A = TypeVar('A')


class Id(Agent[A, A]):
    """
    Identity morphism.

    Type signature: Id: A → A

    The composition unit. Satisfies:
        Id ∘ f = f
        f ∘ Id = f
    """

    @property
    def name(self) -> str:
        return "Id"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Identity morphism; composition unit"

    async def invoke(self, input: A) -> A:
        """λx.x — returns input unchanged"""
        return input


# Singleton instance
id_agent: Agent = Id()
