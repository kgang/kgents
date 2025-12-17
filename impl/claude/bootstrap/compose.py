"""
Compose Agent - The agent-that-makes-agents via sequential composition.

Compose: (Agent, Agent) → Agent
Compose(f, g) = g ∘ f

The fundamental operation that makes agents form a category.
You cannot define composition in terms of simpler operations -
it IS the simplest operation.

Laws:
- Associativity: (f >> g) >> h ≡ f >> (g >> h)
- Identity: Id >> f ≡ f ≡ f >> Id
- Closure: Composition of agents produces an agent

See spec/bootstrap.md lines 57-70, spec/c-gents/composition.md.
"""

from __future__ import annotations

from typing import TypeVar

from agents.poly.types import Agent, ComposedAgent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def compose(f: Agent[A, B], g: Agent[B, C]) -> ComposedAgent[A, B, C]:
    """
    Compose two agents: f >> g.

    Given f: A → B and g: B → C, produces an agent A → C.
    This is the same as f >> g but as a function instead of operator.

    Usage:
        pipeline = compose(tokenize, parse)
        result = await pipeline.invoke("hello world")

    Laws:
        compose(Id, f) ≡ f  (left identity)
        compose(f, Id) ≡ f  (right identity)
        compose(compose(f, g), h) ≡ compose(f, compose(g, h))  (associativity)
    """
    return ComposedAgent(f, g)


from typing import Any as AnyType


def pipeline(*agents: Agent[AnyType, AnyType]) -> Agent[AnyType, AnyType]:
    """
    Compose multiple agents into a pipeline.

    Usage:
        p = pipeline(tokenize, parse, validate, transform)
        result = await p.invoke(input)

    Equivalent to: tokenize >> parse >> validate >> transform

    Note: Type safety is not enforced at compile time for pipeline().
    For type-safe composition, use the >> operator directly:
        typed_pipeline = tokenize >> parse >> validate >> transform

    Raises:
        ValueError: If no agents provided
    """
    if len(agents) == 0:
        raise ValueError("pipeline requires at least one agent")

    if len(agents) == 1:
        return agents[0]

    # Type-wise this is tricky because intermediate types vary
    # We use a runtime check and trust the caller to provide
    # type-compatible agents
    result: Agent[AnyType, AnyType] = agents[0]
    for agent in agents[1:]:
        result = result >> agent

    return result


class Compose(Agent[tuple[Agent[A, B], Agent[B, C]], ComposedAgent[A, B, C]]):
    """
    Compose as an agent itself.

    Takes a pair of agents and returns their composition.
    This is "the agent that makes agents" - meta-level composition.

    Usage:
        composer = Compose()
        pipeline = await composer.invoke((f, g))
        # pipeline is f >> g
    """

    @property
    def name(self) -> str:
        return "Compose"

    async def invoke(
        self, input: tuple[Agent[A, B], Agent[B, C]]
    ) -> ComposedAgent[A, B, C]:
        """Compose the two agents."""
        f, g = input
        return compose(f, g)


# --- Utility: Decompose (inverse operation for analysis) ---


def decompose(agent: ComposedAgent[A, B, C]) -> tuple[Agent[A, B], Agent[B, C]]:
    """
    Decompose a composed agent into its parts.

    The inverse of compose for analysis/debugging.

    Usage:
        pipeline = f >> g
        first, second = decompose(pipeline)
        # first is f, second is g
    """
    return (agent.first, agent.second)


def flatten(agent: Agent[A, B]) -> list[Agent[A, B]]:
    """
    Flatten a composed agent into a list of its atomic parts.

    Recursively decomposes all ComposedAgents.

    Usage:
        pipeline = a >> b >> c >> d
        parts = flatten(pipeline)  # [a, b, c, d]
    """
    if isinstance(agent, ComposedAgent):
        # Recursively flatten both parts
        # Note: Type system doesn't track intermediate types,
        # so we use Any for the internal list
        result: list[Agent[A, B]] = []
        result.extend(flatten(agent.first))
        result.extend(flatten(agent.second))
        return result
    else:
        return [agent]


def depth(agent: Agent[A, B]) -> int:
    """
    Get the nesting depth of a composed agent.

    Useful for analyzing composition complexity.

    Usage:
        simple = a >> b
        complex = (a >> b) >> (c >> d)
        print(depth(simple))  # 1
        print(depth(complex))  # 2
    """
    if isinstance(agent, ComposedAgent):
        return 1 + max(depth(agent.first), depth(agent.second))
    else:
        return 0
