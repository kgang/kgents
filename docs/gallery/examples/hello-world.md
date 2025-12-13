# Hello World

Your first agent - the fundamental building block of kgents.

## The Minimal Agent

An agent is a **morphism** A → B: it transforms input of type A into output of type B.

```python
from bootstrap.types import Agent

class GreetAgent(Agent[str, str]):
    """Transforms a name into a greeting."""

    @property
    def name(self) -> str:
        return "greeter"

    async def invoke(self, input: str) -> str:
        return f"Hello, {input}!"
```

That's it. Every agent in kgents follows this pattern:

- **Type parameters**: `Agent[Input, Output]` declares the transformation
- **name property**: Identifies the agent (used in composition, logs, traces)
- **invoke method**: The actual transformation logic

## Running It

```python
import asyncio

async def main():
    agent = GreetAgent()
    result = await agent.invoke("World")
    print(result)  # Hello, World!

asyncio.run(main())
```

Or run the included example:

```bash
python -m impl.claude.agents.examples.hello_world
```

## Why Async?

The `invoke` method is async (`async def`) even though this example doesn't need it. Why?

**Flexibility**. Many real-world agents:

- Call external APIs (LLMs, databases, web services)
- Perform I/O operations
- Coordinate with other async agents

By making `invoke` async from the start, we avoid retrofitting later.

## Key Insight: Agents Are Morphisms

In category theory, a **morphism** is an arrow between objects. In kgents:

- Objects = Python types (str, int, MyDataClass, etc.)
- Morphisms = Agents (transformations between types)

This mathematical framing gives us **guarantees**:

1. **Composition**: `f >> g` chains agents predictably
2. **Identity**: There exists an identity agent that does nothing
3. **Associativity**: `(f >> g) >> h = f >> (g >> h)`

These aren't just nice properties - they're **laws** that make agents composable.

## Creating Your Own Agent

Let's build a different agent with different types:

```python
from bootstrap.types import Agent

class ShoutAgent(Agent[str, str]):
    """Transforms text to uppercase with enthusiasm."""

    @property
    def name(self) -> str:
        return "shouter"

    async def invoke(self, input: str) -> str:
        return input.upper() + "!"

# Usage
agent = ShoutAgent()
result = await agent.invoke("hello kgents")
# -> "HELLO KGENTS!"
```

## Different Input/Output Types

Agents can transform between ANY types:

```python
from dataclasses import dataclass
from bootstrap.types import Agent

@dataclass
class Person:
    name: str
    age: int

class PersonToGreeting(Agent[Person, str]):
    @property
    def name(self) -> str:
        return "person-greeter"

    async def invoke(self, input: Person) -> str:
        return f"Hello, {input.name}! You are {input.age} years old."

# Usage
agent = PersonToGreeting()
person = Person(name="Alice", age=30)
greeting = await agent.invoke(person)
# -> "Hello, Alice! You are 30 years old."
```

## Agent != Class Hierarchy

**Critical insight**: `Agent[A, B]` is NOT a traditional class hierarchy.

Traditional OOP:
```python
class Animal:
    def speak(self): pass

class Dog(Animal):
    def speak(self): return "woof"
```

Agent-oriented:
```python
class GreetAgent(Agent[str, str]):
    # This is the SKELETON
    # Everything else (state, soul, observability) is added via Halo
    ...
```

The skeleton is minimal. **Capabilities** are added via decorators:

```python
from agents.a import Capability

@Capability.Soulful(persona="Kent")
@Capability.Stateful
class MyAgent(Agent[str, str]):
    ...
```

(More on capabilities in later examples.)

## What's Next?

You've learned:

- Agent[A, B] is a transformation from A to B
- Every agent has a `name` and an `invoke` method
- Agents are morphisms (they obey category laws)

**Next step**: Learn to chain agents together with composition.

[:octicons-arrow-right-24: Learn Composition](composition.md)

## Exercises

1. **Create a ReverseAgent**: Agent[str, str] that reverses a string
2. **Create a LengthAgent**: Agent[str, int] that returns string length
3. **Create a ValidateEmailAgent**: Agent[str, bool] that checks if input is a valid email

## Run the Example

```bash
# From the kgents repo root
python -m impl.claude.agents.examples.hello_world
```

## Full Source

View the complete source code:
[impl/claude/agents/examples/hello_world.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/examples/hello_world.py)
