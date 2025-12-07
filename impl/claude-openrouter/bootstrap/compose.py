"""
Compose (∘) - The agent-that-makes-agents.

Type: (Agent, Agent) → Agent
Law: Compose(f, g) = g ∘ f

Takes two agents and yields their sequential composition.

Why irreducible: Composition IS the fundamental operation.
What it grounds: All agent pipelines. The C-gents category.
"""

from typing import TypeVar

from .types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class ComposedAgent(Agent[A, C]):
    """
    A composed agent: the result of first >> second.

    Applies first, then second. Type-safe pipeline.
    """

    def __init__(self, first: Agent[A, B], second: Agent[B, C]):
        self._first = first
        self._second = second
        self._name = f"({first.name} >> {second.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> C:
        """Apply first agent, then second agent."""
        intermediate = await self._first.invoke(input)
        return await self._second.invoke(intermediate)

    def __repr__(self) -> str:
        return self._name


def compose(first: Agent[A, B], second: Agent[B, C]) -> Agent[A, C]:
    """
    Compose two agents into a pipeline.

    The fundamental operation. Creates an agent that:
    1. Applies `first` to input
    2. Applies `second` to the result

    Laws:
    - Associativity: (f >> g) >> h == f >> (g >> h)
    - Identity: Id >> f == f, f >> Id == f

    Usage:
        pipeline = compose(validate, transform)
        # or via operator:
        pipeline = validate >> transform

    Example:
        Pipeline = Judge(config) >> Create(config) >> Spawn(session)
    """
    return ComposedAgent(first, second)


# Idiom: Compose, Don't Concatenate
#
# If a function does A then B then C, it should BE `A >> B >> C`.
#
# Benefits:
# - Each step is testable in isolation
# - Clear data flow between steps
# - Steps are replaceable/mockable
# - Debugging: "which step failed?"
#
# Anti-pattern: 130-line methods mixing validation, I/O, state, errors.
