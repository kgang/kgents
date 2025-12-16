"""
Tutorial: Hello World - Your First Agent.

Teaches the fundamental Agent[A, B] pattern: a morphism
that transforms input A to output B.
"""

from __future__ import annotations

from ..tutorial import Tutorial, TutorialStep


async def _run_greet() -> str:
    """Execute the GreetAgent example."""
    try:
        from agents.examples.hello_world import GreetAgent

        agent = GreetAgent()
        result = await agent.invoke("World")
        return result
    except ImportError:
        # Define inline for demo
        from bootstrap.types import Agent

        class InlineGreetAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "greeter"

            async def invoke(self, input: str) -> str:
                return f"Hello, {input}!"

        inline_agent = InlineGreetAgent()
        result = await inline_agent.invoke("World")
        return result


async def _run_custom() -> str:
    """Execute custom agent example."""
    from bootstrap.types import Agent

    class ShoutAgent(Agent[str, str]):
        @property
        def name(self) -> str:
            return "shouter"

        async def invoke(self, input: str) -> str:
            return input.upper() + "!"

    agent = ShoutAgent()
    result = await agent.invoke("hello kgents")
    return result


HELLO_WORLD_TUTORIAL = Tutorial(
    name="Hello World",
    description="""An Agent is a morphism A -> B: it transforms input of type A
into output of type B. This is the fundamental building block of kgents.

Every agent has:
  - A `name` property (for identification)
  - An `invoke` method (the transformation)
  - Type parameters [Input, Output]""",
    steps=[
        TutorialStep(
            title="The Minimal Agent",
            code='''
from bootstrap.types import Agent

class GreetAgent(Agent[str, str]):
    """Transforms a name into a greeting."""

    @property
    def name(self) -> str:
        return "greeter"

    async def invoke(self, input: str) -> str:
        return f"Hello, {input}!"
''',
            explanation="An agent is just a class that inherits from Agent[Input, Output] and implements invoke().",
            execute=_run_greet,
            next_hint="Try creating your own agent with different input/output types",
        ),
        TutorialStep(
            title="Creating Your Own Agent",
            code='''
class ShoutAgent(Agent[str, str]):
    """Transforms text to uppercase with enthusiasm."""

    @property
    def name(self) -> str:
        return "shouter"

    async def invoke(self, input: str) -> str:
        return input.upper() + "!"

# Usage:
agent = ShoutAgent()
result = await agent.invoke("hello kgents")
# -> "HELLO KGENTS!"
''',
            explanation="The invoke() method is where your transformation logic lives. It's async for flexibility.",
            execute=_run_custom,
            next_hint="What if you wanted to chain multiple agents together?",
        ),
        TutorialStep(
            title="Why Agents Are Morphisms",
            code="""
# Agent[A, B] is a morphism in the category of types
#
# Think of it as:
#   f: A -> B
#
# This mathematical framing gives us:
# 1. Composition: f >> g (chain agents)
# 2. Identity: id[A] (do nothing agent)
# 3. Associativity: (f >> g) >> h = f >> (g >> h)

# These aren't just nice properties - they're
# GUARANTEES that make agents composable.
""",
            explanation="Agents form a category. This means they compose predictably and safely.",
            next_hint="Try the 'compose' tutorial to see composition in action",
        ),
    ],
    completion_message="""You've learned the basics:

  - Agent[A, B] is a transformation from A to B
  - Every agent has a name and an invoke() method
  - Agents form a category (they compose!)

Next: Learn to chain agents with `kgents play compose`""",
)
