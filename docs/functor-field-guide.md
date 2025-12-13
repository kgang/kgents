# The Functor Field Guide

> *"A functor is a way to transform agents while preserving their structure."*

This guide explains the Alethic Algebra — how to lift, compose, and deploy agents — without requiring category theory background.

## The Core Insight

You have an agent that does one thing well:

```python
class Double(Agent[int, int]):
    async def invoke(self, x: int) -> int:
        return x * 2
```

But your input might be missing:

```python
input: Maybe[int] = Just(5)  # or Nothing
```

**The functor lifts your agent to handle the new context:**

```python
from agents import MaybeFunctor

double = Double()
lifted = MaybeFunctor.lift(double)

await lifted.invoke(Just(5))   # Just(10)
await lifted.invoke(Nothing)   # Nothing (no error!)
```

The magic: your agent's logic doesn't change. The functor handles the context.

## The Functor Zoo

| Functor | Handles | Use Case |
|---------|---------|----------|
| `Maybe` | Optional values | Input might be missing |
| `Either` | Success/Error | Operation might fail |
| `List` | Collections | Process batches |
| `Async` | Background work | Fire-and-forget |
| `Logged` | Observability | Debug production |
| `Fix` | Retries | Handle transient failures |
| `Soul` | Personality | K-gent persona awareness |
| `Flux` | Streams | Real-time event processing |
| `Observer` | Telemetry | Metrics and tracing |
| `State` | Memory | Maintain state across calls |

## Quick Start: Lifting Agents

### Maybe: Handle Optional Values

```python
from agents import Maybe, Just, Nothing, MaybeFunctor

@agent
async def double(x: int) -> int:
    return x * 2

# Lift to handle Maybe[int]
safe_double = MaybeFunctor.lift(double)

await safe_double.invoke(Just(21))  # Just(42)
await safe_double.invoke(Nothing)   # Nothing (propagates gracefully)
```

### Either: Handle Errors

```python
from agents.c import Either, Left, Right, EitherFunctor

@agent
async def divide(pair: tuple[int, int]) -> float:
    a, b = pair
    return a / b

# Lift to handle Either[str, tuple[int, int]]
safe_divide = EitherFunctor.lift(divide)

await safe_divide.invoke(Right((10, 2)))  # Right(5.0)
await safe_divide.invoke(Left("no data")) # Left("no data")
```

### Flux: Handle Streams

```python
from agents import Flux, FluxConfig

@agent
async def process(event: dict) -> dict:
    return {"processed": event}

# Lift to flux domain
flux_processor = Flux.lift(process)

# Process a stream
async for result in flux_processor.start(event_source):
    handle(result)
```

## Composition: The Magic

Functors compose. Need retry with logging?

```python
from agents import compose_functors
from agents.c import LoggedFunctor, FixFunctor

# Compose functors
stack = compose_functors(LoggedFunctor, FixFunctor)

# Apply to any agent
resilient_agent = stack(my_agent)
```

The composition works because functors preserve structure.

## Agent Composition: The `>>` Operator

Agents also compose directly:

```python
@agent
async def parse(s: str) -> int:
    return int(s)

@agent
async def double(x: int) -> int:
    return x * 2

@agent
async def format(x: int) -> str:
    return f"Result: {x}"

# Compose with >>
pipeline = parse >> double >> format

await pipeline.invoke("21")  # "Result: 42"
```

Or use the `pipeline()` helper:

```python
from agents import pipeline

pipe = pipeline(parse, double, format)
await pipe.invoke("21")  # "Result: 42"
```

## The Laws (Why It Works)

Every functor satisfies two laws:

1. **Identity**: `F(id) = id`
   Lifting the identity function does nothing

2. **Composition**: `F(g >> f) = F(g) >> F(f)`
   Lifting preserves composition

These laws guarantee composition is safe. Break them, break everything.

### Verifying Functor Laws

```python
from agents import verify_functor, MaybeFunctor

# Verify a functor satisfies the laws
report = await verify_functor(MaybeFunctor)
print(report.is_valid)  # True
```

## Archetypes: Pre-Packaged Capabilities

Instead of manually adding capabilities, use archetypes:

| Archetype | Capabilities | Use Case |
|-----------|--------------|----------|
| `Kappa` | All 4 | Production services |
| `Lambda` | Observable only | Lightweight processors |
| `Delta` | Stateful + Observable | Data handlers |

```python
from agents import Kappa

class MyService(Kappa[Request, Response]):
    async def invoke(self, req: Request) -> Response:
        return process(req)
```

## The Halo System

Capabilities are declared via decorators:

```python
from agents import Capability, Agent

@Capability.Stateful(schema=MyState)
@Capability.Soulful(persona="Kent")
class MyAgent(Agent[str, str]):
    ...
```

The Projector compiles Halo → runtime:

- **LocalProjector**: Runnable Python
- **K8sProjector**: Kubernetes manifests

```python
from system.projector import LocalProjector

projector = LocalProjector()
compiled = projector.compile(MyAgent)
```

## Complete Example

```python
"""A resilient, persona-aware data processor."""

from agents import (
    agent, pipeline, Flux, FluxConfig,
    Maybe, Just, Nothing, MaybeFunctor,
)

@agent
async def parse_json(raw: str) -> dict:
    import json
    return json.loads(raw)

@agent
async def extract_value(data: dict) -> int:
    return data.get("value", 0)

@agent
async def apply_business_logic(n: int) -> int:
    return n * 2 + 1

# Compose the pipeline
core_pipeline = pipeline(parse_json, extract_value, apply_business_logic)

# Lift to handle optional inputs
safe_pipeline = MaybeFunctor.lift(core_pipeline)

# Lift to handle streams
flux_pipeline = Flux.lift(safe_pipeline)

# Usage
async def process_events(source):
    async for result in flux_pipeline.start(source):
        print(f"Processed: {result}")
```

## Summary

1. **Agents are morphisms**: `Agent[A, B]` transforms A → B
2. **Functors lift agents**: Handle new contexts without changing logic
3. **Composition is safe**: Laws guarantee structure preservation
4. **Archetypes bundle capabilities**: Kappa, Lambda, Delta
5. **Projectors compile**: Halo → runnable code or K8s manifests

The Alethic Algebra is powerful because it's principled. The laws aren't academic — they're the reason composition works reliably at scale.

---

*"The difference between a good system and a great one is the last 5%."*
