"""
Compose Agent (∘)

Compose: (Agent, Agent) → Agent
Compose(f, g) = g ∘ f

The agent-that-makes-agents. Takes two agents and yields their sequential composition.

Why irreducible: Composition is the fundamental operation. You cannot define it
                 in terms of simpler operations—it IS the simplest operation.

What it grounds: All agent pipelines. The C-gents category.
                 The ability to build complex from simple.
"""

from typing import TypeVar, Generic
from .types import Agent

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class ComposedAgent(Agent[A, C], Generic[A, B, C]):
    """
    An agent that is the composition of two other agents.

    Given f: A → B and g: B → C, this is (g ∘ f): A → C
    """

    def __init__(self, first: Agent[A, B], second: Agent[B, C]):
        self._first = first
        self._second = second
        self._name = f"({second.name} ∘ {first.name})"

    @property
    def name(self) -> str:
        return self._name

    @property
    def genus(self) -> str:
        return "composed"

    @property
    def purpose(self) -> str:
        return f"Sequential composition of {self._first.name} then {self._second.name}"

    async def invoke(self, input: A) -> C:
        """Apply first, then second"""
        intermediate: B = await self._first.invoke(input)
        result: C = await self._second.invoke(intermediate)
        return result


class Compose(Agent[tuple[Agent[A, B], Agent[B, C]], Agent[A, C]]):
    """
    The composition operator.

    Type signature: Compose: (Agent[A,B], Agent[B,C]) → Agent[A,C]

    Laws:
        - Associativity: (f ∘ g) ∘ h ≡ f ∘ (g ∘ h)
        - Identity: Id ∘ f ≡ f, f ∘ Id ≡ f
        - Closure: composition of agents is an agent
    """

    @property
    def name(self) -> str:
        return "Compose"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Agent-that-makes-agents; the composition operator"

    async def invoke(self, input: tuple[Agent[A, B], Agent[B, C]]) -> Agent[A, C]:
        """Compose two agents into a pipeline"""
        first, second = input
        return ComposedAgent(first, second)


def compose(f: Agent[A, B], g: Agent[B, C]) -> Agent[A, C]:
    """
    Convenience function for composing agents.

    compose(f, g) means: apply f first, then g
    Written mathematically as: g ∘ f
    """
    return ComposedAgent(f, g)


def pipeline(*agents: Agent) -> Agent:
    """
    Compose multiple agents into a pipeline.

    pipeline(a, b, c) = c ∘ b ∘ a

    Data flows left-to-right: input → a → b → c → output
    """
    if not agents:
        from .id import id_agent
        return id_agent

    result = agents[0]
    for agent in agents[1:]:
        result = ComposedAgent(result, agent)
    return result


# Singleton instance
compose_agent = Compose()
