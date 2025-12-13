"""
Tutorial: Lift to Maybe - Handle Optional Values.

Teaches the Maybe functor pattern for graceful error handling
without exceptions or null checks everywhere.
"""

from __future__ import annotations

from ..tutorial import Tutorial, TutorialStep


async def _run_maybe_basic() -> str:
    """Demonstrate basic Maybe usage."""
    try:
        from agents.c import Just, Maybe, Nothing

        # Create some Maybe values
        has_value: Maybe[int] = Just(42)
        no_value: Maybe[int] = Nothing

        return f"Just(42) = {has_value}\nNothing = {no_value}"
    except ImportError:
        return "(agents.c not available - showing pattern only)"


async def _run_functor_lift() -> str:
    """Demonstrate lifting an agent to Maybe."""
    try:
        from agents.c import Just, Maybe, MaybeFunctor, Nothing
        from bootstrap.types import Agent

        class DoubleAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "double"

            async def invoke(self, input: int) -> int:
                return input * 2

        double = DoubleAgent()
        maybe_double = MaybeFunctor.lift(double)

        result_just = await maybe_double.invoke(Just(21))
        result_nothing = await maybe_double.invoke(Nothing)

        return f"maybe_double(Just(21)) = {result_just}\nmaybe_double(Nothing) = {result_nothing}"
    except ImportError:
        return "(agents.c not available - showing pattern only)"


FUNCTOR_TUTORIAL = Tutorial(
    name="Lift to Maybe",
    description="""A Functor lifts agents to work with wrapped values.
The Maybe functor lets agents handle optional values:

  Agent[A, B]  ->  Agent[Maybe[A], Maybe[B]]

If the input is Nothing, the output is Nothing.
If the input is Just(x), the agent processes x.

No null checks. No exceptions. Just elegant composition.""",
    steps=[
        TutorialStep(
            title="The Maybe Type",
            code="""
from agents.c import Maybe, Just, Nothing

# Maybe[A] represents "maybe has a value of type A"
# It's either Just(value) or Nothing

has_value: Maybe[int] = Just(42)    # Has a value
no_value: Maybe[int] = Nothing       # No value

# Pattern: Use Maybe instead of None/null
# Benefits:
#   - Type-safe: compiler knows it might be empty
#   - Composable: works with functors
#   - Explicit: no surprise NoneType errors
""",
            explanation="Maybe[A] explicitly represents optional values - Just(value) or Nothing.",
            execute=_run_maybe_basic,
            next_hint="How do we use this with agents?",
        ),
        TutorialStep(
            title="Lifting Agents with MaybeFunctor",
            code="""
from agents.c import MaybeFunctor, Just, Nothing
from bootstrap.types import Agent

class DoubleAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "double"

    async def invoke(self, input: int) -> int:
        return input * 2

# Original: Agent[int, int]
double = DoubleAgent()

# Lifted: Agent[Maybe[int], Maybe[int]]
maybe_double = MaybeFunctor.lift(double)

# Now it handles optional values automatically!
await maybe_double.invoke(Just(21))  # -> Just(42)
await maybe_double.invoke(Nothing)   # -> Nothing
""",
            explanation="MaybeFunctor.lift() makes any agent handle optional values gracefully.",
            execute=_run_functor_lift,
            next_hint="Notice: no if/else, no null checks, just lift!",
        ),
        TutorialStep(
            title="Why Functors Are Powerful",
            code="""
# A Functor F transforms Agent[A, B] to Agent[F[A], F[B]]
#
# Different functors give different powers:
#
# Maybe[A]    - Optional values (Nothing propagates)
# List[A]     - Multiple values (process each)
# Either[E,A] - Success or error (short-circuit on error)
# Flux[A]     - Streams (continuous processing)
#
# The pattern is always the same:
#   lifted_agent = SomeFunctor.lift(original_agent)
#
# Your agent code stays simple.
# The functor handles the wrapping/unwrapping.

# COMPOSE LIFTED AGENTS:
# maybe_parse >> maybe_double >> maybe_stringify
# If any step returns Nothing, the whole pipeline returns Nothing!
""",
            explanation="Functors are a design pattern for transforming agents to handle new contexts.",
            next_hint="See agents.c for more functors, or try the Flux functor for streams",
        ),
    ],
    completion_message="""You've learned the functor pattern:

  - Maybe[A] represents optional values explicitly
  - MaybeFunctor.lift() makes agents handle optionals
  - Functors let you add powers without changing agent code

Next: Chat with K-gent with `kgents play soul`""",
)
