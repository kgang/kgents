# Functors

Lift agents to handle wrapped values - elegantly handling optionals, errors, and more.

## The Problem

You have a simple agent:

```python
class DoubleAgent(Agent[int, int]):
    async def invoke(self, input: int) -> int:
        return input * 2
```

But now your input might be `None`. What do you do?

**Bad solution**: Add null checks everywhere

```python
async def invoke(self, input: int | None) -> int | None:
    if input is None:
        return None
    return input * 2  # Now with special cases!
```

This gets messy fast. What about composition?

```python
# Now every agent needs null checks
pipeline = maybe_double >> maybe_add_one >> maybe_stringify
# Each one has if input is None: return None
```

**Better solution**: Use a **Functor** to lift the agent.

## The Maybe Type

First, we need a type that explicitly represents "maybe has a value":

```python
from agents.c import Maybe, Just, Nothing

# Maybe[A] is either Just(value) or Nothing
has_value: Maybe[int] = Just(42)
no_value: Maybe[int] = Nothing

# Pattern: Use Maybe instead of None
# Benefits:
#   - Type-safe: compiler knows it might be empty
#   - Composable: works with functors
#   - Explicit: no surprise NoneType errors
```

`Maybe[A]` is like `Optional[A]`, but designed for composition:

- `Just(value)` = has a value
- `Nothing` = no value (singleton, not a type)

## The MaybeFunctor

A **Functor** transforms agents to work with wrapped values:

```python
Agent[A, B]  ->  Agent[F[A], F[B]]
```

For the Maybe functor:

```python
Agent[A, B]  ->  Agent[Maybe[A], Maybe[B]]
```

Here's how:

```python
from agents.c import MaybeFunctor, Just, Nothing

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
```

**No null checks. No special cases. Just lift.**

## How It Works

The `MaybeFunctor.lift()` function wraps your agent:

1. If input is `Just(value)`, unwrap it and call the original agent
2. If input is `Nothing`, skip the agent and return `Nothing`
3. Wrap the result back in `Maybe`

```python
# Conceptual implementation
class LiftedMaybeAgent(Agent[Maybe[A], Maybe[B]]):
    def __init__(self, original: Agent[A, B]):
        self.original = original

    async def invoke(self, input: Maybe[A]) -> Maybe[B]:
        if isinstance(input, Just):
            result = await self.original.invoke(input.value)
            return Just(result)
        else:
            return Nothing
```

## Composition with Maybe

The real power: compose lifted agents without any null checks:

```python
from agents.c import MaybeFunctor

# Original agents (simple, no null handling)
double = DoubleAgent()       # int -> int
add_one = AddOneAgent()      # int -> int
stringify = StringifyAgent() # int -> str

# Lift all of them
maybe_double = MaybeFunctor.lift(double)
maybe_add_one = MaybeFunctor.lift(add_one)
maybe_stringify = MaybeFunctor.lift(stringify)

# Compose the lifted agents
pipeline = maybe_double >> maybe_add_one >> maybe_stringify

# If ANY step returns Nothing, the whole pipeline returns Nothing
await pipeline.invoke(Just(5))   # -> Just("Result: 11")
await pipeline.invoke(Nothing)   # -> Nothing
```

**Your agent code stays simple. The functor handles the wrapping.**

## Other Functors

The Maybe functor is just one example. kgents provides several:

### List Functor

Process multiple values:

```python
Agent[A, B]  ->  Agent[List[A], List[B]]
```

Apply an agent to each item in a list:

```python
list_double = ListFunctor.lift(double)
await list_double.invoke([1, 2, 3])  # -> [2, 4, 6]
```

### Either Functor

Handle success or error:

```python
Agent[A, B]  ->  Agent[Either[E, A], Either[E, B]]
```

Short-circuit on error:

```python
from agents.c import Either, Left, Right

either_double = EitherFunctor.lift(double)
await either_double.invoke(Right(21))  # -> Right(42)
await either_double.invoke(Left("error"))  # -> Left("error")
```

### Flux Functor

Transform discrete agents into continuous processors:

```python
Agent[A, B]  ->  FluxAgent[A, B]
```

(See the [Streaming](streaming.md) example for details.)

## The Functor Pattern

All functors follow the same pattern:

```python
# 1. Define a wrapper type (Maybe, List, Either, Flux)
# 2. Implement lift() to transform Agent[A, B] -> Agent[F[A], F[B]]
# 3. Use it!

original_agent = MyAgent()
lifted_agent = SomeFunctor.lift(original_agent)
```

**The power**: Your agent code stays simple. The functor adds the behavior.

## Functor Laws

Like agents, functors must satisfy laws:

### 1. Identity Law

Lifting the identity agent does nothing:

```python
identity = IdentityAgent[int]()
lifted = MaybeFunctor.lift(identity)

# lifted is effectively identity
await lifted.invoke(Just(42))  # -> Just(42)
await lifted.invoke(Nothing)   # -> Nothing
```

### 2. Composition Law

Lifting preserves composition:

```python
# Lift then compose
lifted_f = MaybeFunctor.lift(f)
lifted_g = MaybeFunctor.lift(g)
pipeline1 = lifted_f >> lifted_g

# Compose then lift
pipeline2 = MaybeFunctor.lift(f >> g)

# Both are equivalent!
```

These laws guarantee that functors behave predictably.

## Real-World Example: Parsing Pipeline

```python
from agents.c import Maybe, Just, Nothing, MaybeFunctor
from bootstrap.types import Agent

class ParseInt(Agent[str, int | None]):
    """Parse string to int, return None if invalid."""

    @property
    def name(self) -> str:
        return "parse-int"

    async def invoke(self, input: str) -> int | None:
        try:
            return int(input)
        except ValueError:
            return None

class ConvertToMaybe(Agent[int | None, Maybe[int]]):
    """Convert None to Nothing, value to Just(value)."""

    @property
    def name(self) -> str:
        return "to-maybe"

    async def invoke(self, input: int | None) -> Maybe[int]:
        return Just(input) if input is not None else Nothing

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

# Build the pipeline
parse = ParseInt()
to_maybe = ConvertToMaybe()
maybe_double = MaybeFunctor.lift(DoubleAgent())
maybe_stringify = MaybeFunctor.lift(StringifyAgent())

pipeline = parse >> to_maybe >> maybe_double >> maybe_stringify

# Use it
await pipeline.invoke("21")    # -> Just("Result: 42")
await pipeline.invoke("xyz")   # -> Nothing
```

The functor handles all the error propagation. Your business logic stays clean.

## When to Use Functors

Use functors when you need to:

- **Handle optionals**: MaybeFunctor
- **Process lists**: ListFunctor
- **Manage errors**: EitherFunctor
- **Work with streams**: FluxFunctor (Flux)
- **Add context**: ReaderFunctor, WriterFunctor

**Don't** use functors when:

- The agent naturally handles the wrapped type
- You need custom error handling logic
- The wrapping adds more complexity than it removes

## What's Next?

You've learned:

- `Maybe[A]` represents optional values explicitly
- `MaybeFunctor.lift()` makes agents handle optionals
- Functors let you add powers without changing agent code
- The functor pattern: lift, compose, profit

**Next step**: Chat with K-gent and experience personality-aligned dialogue.

[:octicons-arrow-right-24: Meet K-gent](soul-dialogue.md)

## Exercises

1. **Lift a custom agent**: Create your own agent and lift it with MaybeFunctor
2. **Chain three lifted agents**: Compose `maybe_parse >> maybe_double >> maybe_stringify`
3. **Create a ListFunctor pipeline**: Process a list of numbers through multiple transformations

## Run the Example

```bash
python -m impl.claude.agents.examples.composed_pipeline
```

(The composed_pipeline example includes functor demos.)

## Full Source

View functor implementations:
- [impl/claude/agents/c/functor.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/c/functor.py)
- [impl/claude/agents/c/maybe.py](https://github.com/kentgang/kgents/blob/main/impl/claude/agents/c/maybe.py)
