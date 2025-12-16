"""
Tutorial: Composition - Pipe Agents Together.

Teaches the >> operator for agent composition,
demonstrating the category laws (identity, associativity).
"""

from __future__ import annotations

from ..tutorial import Tutorial, TutorialStep


async def _run_pipeline() -> str:
    """Execute the composition example."""
    from bootstrap.types import Agent

    class DoubleAgent(Agent[int, int]):
        @property
        def name(self) -> str:
            return "double"

        async def invoke(self, input: int) -> int:
            return input * 2

    class StringifyAgent(Agent[int, str]):
        @property
        def name(self) -> str:
            return "stringify"

        async def invoke(self, input: int) -> str:
            return f"Result: {input}"

    double = DoubleAgent()
    stringify = StringifyAgent()

    # Compose them
    pipeline = double >> stringify
    result = await pipeline.invoke(21)
    return f"{result}\n(Pipeline name: {pipeline.name})"


async def _run_associativity() -> str:
    """Demonstrate associativity."""
    from bootstrap.types import Agent

    class Double(Agent[int, int]):
        @property
        def name(self) -> str:
            return "double"

        async def invoke(self, input: int) -> int:
            return input * 2

    class AddOne(Agent[int, int]):
        @property
        def name(self) -> str:
            return "add-one"

        async def invoke(self, input: int) -> int:
            return input + 1

    class Square(Agent[int, int]):
        @property
        def name(self) -> str:
            return "square"

        async def invoke(self, input: int) -> int:
            return input * input

    double = Double()
    add_one = AddOne()
    square = Square()

    # (f >> g) >> h
    left = (double >> add_one) >> square
    result_left = await left.invoke(3)

    # f >> (g >> h)
    right = double >> (add_one >> square)
    result_right = await right.invoke(3)

    return f"(double >> add_one) >> square: {result_left}\ndouble >> (add_one >> square): {result_right}\nEqual: {result_left == result_right}"


COMPOSITION_TUTORIAL = Tutorial(
    name="Composition",
    description="""Agents compose with the >> operator. Given:
  f: Agent[A, B]
  g: Agent[B, C]

Then f >> g creates a new agent:
  Agent[A, C]

This is the heart of functional agent design.""",
    steps=[
        TutorialStep(
            title="The >> Operator",
            code="""
from bootstrap.types import Agent

class DoubleAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "double"

    async def invoke(self, input: int) -> int:
        return input * 2

class StringifyAgent(Agent[int, str]):
    @property
    def name(self) -> str:
        return "stringify"

    async def invoke(self, input: int) -> str:
        return f"Result: {input}"

# Compose: double >> stringify
double = DoubleAgent()
stringify = StringifyAgent()
pipeline = double >> stringify

result = await pipeline.invoke(21)
# -> "Result: 42"
""",
            explanation="The >> operator creates a NEW agent that runs both in sequence.",
            execute=_run_pipeline,
            next_hint="Notice that the pipeline itself is an agent with its own name",
        ),
        TutorialStep(
            title="Associativity: Order Doesn't Matter",
            code="""
# Category Law: (f >> g) >> h = f >> (g >> h)
#
# This means you can group pipelines however you want
# and get the same result.

# Given:
double    = DoubleAgent()   # int -> int
add_one   = AddOneAgent()   # int -> int
square    = SquareAgent()   # int -> int

# These are equivalent:
left  = (double >> add_one) >> square
right = double >> (add_one >> square)

# Both produce the same result!
await left.invoke(3)  == await right.invoke(3)  # True
""",
            explanation="Associativity guarantees predictable composition - build pipelines however you like.",
            execute=_run_associativity,
            next_hint="This is why agents are 'morphisms' - they obey category laws",
        ),
        TutorialStep(
            title="Why This Matters",
            code="""
# Composition is POWERFUL because:
#
# 1. BUILD BIG FROM SMALL
#    validator >> transformer >> formatter >> logger
#
# 2. REUSE COMPONENTS
#    sanitize = strip >> lowercase >> remove_punctuation
#    process = sanitize >> analyze >> summarize
#
# 3. TEST INDEPENDENTLY
#    Each agent can be tested in isolation
#    Composition guarantees correct behavior when combined
#
# 4. REASON MATHEMATICALLY
#    Category laws give you guarantees about behavior
#    No surprises when composing
""",
            explanation="Composition lets you build complex systems from simple, tested parts.",
            next_hint="What about handling errors or optional values?",
        ),
    ],
    completion_message="""You've learned composition:

  - Use >> to chain agents together
  - Composition creates new agents (not chains)
  - Associativity: (f >> g) >> h = f >> (g >> h)

Next: Learn about functors with `kgents play functor`""",
)
