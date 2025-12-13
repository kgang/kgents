"""
Composed Pipeline: Agents as Morphisms.

Agents form a category. The >> operator composes them:

    f: Agent[A, B]
    g: Agent[B, C]
    f >> g: Agent[A, C]

Key insight:
    Composition is NOT chaining. It creates a NEW agent that:
    - Runs f, then g on f's output
    - Satisfies identity: id >> f = f = f >> id
    - Satisfies associativity: (f >> g) >> h = f >> (g >> h)

Run:
    python -m agents.examples.composed_pipeline
"""

import asyncio
from typing import Generic, TypeVar

from agents.c import Maybe, Just, Nothing, MaybeFunctor
from bootstrap.types import Agent

T = TypeVar("T")


class ParseIntAgent(Agent[str, int | None]):
    """Parse string to int, return None if invalid."""

    @property
    def name(self) -> str:
        return "parse-int"

    async def invoke(self, input: str) -> int | None:
        try:
            return int(input)
        except ValueError:
            return None


class DoubleAgent(Agent[int, int]):
    """Double the input."""

    @property
    def name(self) -> str:
        return "double"

    async def invoke(self, input: int) -> int:
        return input * 2


class StringifyAgent(Agent[int, str]):
    """Convert int to string with formatting."""

    @property
    def name(self) -> str:
        return "stringify"

    async def invoke(self, input: int) -> str:
        return f"Result: {input}"


class IdentityAgent(Agent[T, T], Generic[T]):
    """The identity agent: returns input unchanged."""

    @property
    def name(self) -> str:
        return "identity"

    async def invoke(self, input: T) -> T:
        return input


async def main() -> None:
    """Demonstrate agent composition."""
    print("=== Agent Composition Demo ===\n")

    # Create individual agents
    double = DoubleAgent()
    stringify = StringifyAgent()

    # Compose them: double >> stringify
    # Type: Agent[int, int] >> Agent[int, str] → Agent[int, str]
    pipeline = double >> stringify

    print(f"Pipeline: {pipeline.name}")  # (double >> stringify)

    result = await pipeline.invoke(21)
    print(f"pipeline.invoke(21) = {result}")  # Result: 42

    # Verify associativity
    print("\n=== Associativity Demo ===\n")

    class AddOneAgent(Agent[int, int]):
        @property
        def name(self) -> str:
            return "add-one"

        async def invoke(self, input: int) -> int:
            return input + 1

    add_one = AddOneAgent()

    # (double >> add_one) >> stringify
    left_assoc = (double >> add_one) >> stringify
    # double >> (add_one >> stringify)
    right_assoc = double >> (add_one >> stringify)

    result_left = await left_assoc.invoke(5)
    result_right = await right_assoc.invoke(5)

    print(f"(double >> add_one) >> stringify: {result_left}")
    print(f"double >> (add_one >> stringify): {result_right}")
    print(f"Equal: {result_left == result_right}")  # True (associativity)

    # Verify identity
    print("\n=== Identity Law Demo ===\n")

    identity: IdentityAgent[int] = IdentityAgent()

    # id >> double should equal double
    with_id_left = identity >> double
    # double >> id should equal double
    with_id_right = double >> identity

    plain = await double.invoke(10)
    with_left = await with_id_left.invoke(10)
    with_right = await with_id_right.invoke(10)

    print(f"double.invoke(10) = {plain}")
    print(f"(id >> double).invoke(10) = {with_left}")
    print(f"(double >> id).invoke(10) = {with_right}")
    print(f"All equal: {plain == with_left == with_right}")  # True (identity)

    # Functor lifting demo
    print("\n=== Functor Lifting Demo ===\n")

    # The Maybe functor lifts agents to handle optional values
    maybe_double = MaybeFunctor.lift(double)

    # Now it can handle Maybe[int] instead of just int
    # Note: Nothing is a singleton instance, not a callable
    result_just = await maybe_double.invoke(Just(21))
    result_nothing = await maybe_double.invoke(Nothing)

    print(f"MaybeFunctor.lift(double).invoke(Just(21)) = {result_just}")
    print(f"MaybeFunctor.lift(double).invoke(Nothing) = {result_nothing}")


if __name__ == "__main__":
    asyncio.run(main())
