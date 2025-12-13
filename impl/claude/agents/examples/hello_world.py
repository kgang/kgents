"""
Hello World: The Minimal Agent.

This is the simplest possible agent in kgents. An agent is a morphism A → B:
it takes input of type A and produces output of type B.

Key insight:
    Agent[A, B] is NOT a class hierarchy. It IS the skeleton.
    Everything else — state, soul, observability — is added via Halo.

Run:
    python -m agents.examples.hello_world
"""

import asyncio

from bootstrap.types import Agent


class GreetAgent(Agent[str, str]):
    """
    Greets the user by name.

    Type: Agent[str, str]
    Input: A name
    Output: A greeting
    """

    @property
    def name(self) -> str:
        return "greeter"

    async def invoke(self, input: str) -> str:
        return f"Hello, {input}!"


async def main() -> None:
    """Demonstrate the minimal agent."""
    agent = GreetAgent()

    # Invoke the agent
    result = await agent.invoke("World")
    print(result)  # Hello, World!

    # Composition: agents form a category
    # GreetAgent >> UppercaseAgent would produce "HELLO, WORLD!"
    # (See composed_pipeline.py for composition examples)


if __name__ == "__main__":
    asyncio.run(main())
