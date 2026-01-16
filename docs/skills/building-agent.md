# Skill: Building an Agent

> *"Agents are morphisms. Composition is primary."*

**Purpose**: Creating agents from scratch—from simple `Agent[A, B]` to composed pipelines. Start here before advancing to polynomial agents.

**Prerequisites**: Basic Python, async/await
**Next**: [polynomial-agent.md](polynomial-agent.md) for state-dependent behavior

---

## When to Use This Skill

- Creating a new agent from scratch
- Understanding agent composition (`>>` operator)
- Integrating with D-gent memory patterns
- Verifying composition laws (identity, associativity)

---

## The Agent Model

### Core Type

```python
Agent[A, B] = A → B  # Input → Output (simplest form)
```

An agent transforms input type `A` to output type `B`. That's it.

### kgents Agent Protocol

```python
from typing import Protocol, TypeVar

A = TypeVar("A", contravariant=True)
B = TypeVar("B", covariant=True)

class Agent(Protocol[A, B]):
    """The minimal agent interface."""

    async def invoke(self, input: A) -> B:
        """Transform input to output."""
        ...
```

---

## Creating Your First Agent

### Step 1: Define Input/Output Types

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AnalysisRequest:
    text: str
    max_tokens: int = 1000

@dataclass(frozen=True)
class AnalysisResult:
    summary: str
    confidence: float
    reasoning: list[str]
```

**Key**: Use frozen dataclasses for immutable, composable contracts.

### Step 2: Implement the Agent

```python
from agents.base import BaseAgent

class TextAnalyzer(BaseAgent[AnalysisRequest, AnalysisResult]):
    """Analyzes text and produces a summary."""

    def __init__(self, model: str = "fast"):
        self.model = model

    async def invoke(self, request: AnalysisRequest) -> AnalysisResult:
        # Your logic here
        summary = await self._analyze(request.text)
        return AnalysisResult(
            summary=summary,
            confidence=0.85,
            reasoning=["Pattern matched", "Keywords found"],
        )

    async def _analyze(self, text: str) -> str:
        # Implementation details
        return f"Summary of: {text[:50]}..."
```

### Step 3: Use the Agent

```python
analyzer = TextAnalyzer()
result = await analyzer.invoke(AnalysisRequest(text="Hello world"))
print(result.summary)  # "Summary of: Hello world..."
```

---

## Agent Composition

### The `>>` Operator

Agents compose sequentially with `>>`:

```python
# A >> B means: run A, then pass output to B
pipeline = analyzer >> summarizer >> validator

# Equivalent to:
# result = await validator.invoke(
#     await summarizer.invoke(
#         await analyzer.invoke(input)
#     )
# )
result = await pipeline.invoke(input)
```

### Composition Laws

All agents MUST satisfy these laws:

| Law | Requirement | Meaning |
|-----|-------------|---------|
| **Left Identity** | `Id >> f = f` | Identity agent is a no-op prefix |
| **Right Identity** | `f >> Id = f` | Identity agent is a no-op suffix |
| **Associativity** | `(f >> g) >> h = f >> (g >> h)` | Grouping doesn't matter |

### The Identity Agent

```python
from agents.base import identity

Id = identity()  # Returns input unchanged

# These are equivalent:
result1 = await (Id >> my_agent).invoke(x)
result2 = await my_agent.invoke(x)
result3 = await (my_agent >> Id).invoke(x)
```

### Testing Composition Laws

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_left_identity(x):
    """Id >> f = f"""
    composed = Id >> my_agent
    direct = my_agent

    assert composed.invoke(x) == direct.invoke(x)

@given(st.integers())
def test_associativity(x):
    """(f >> g) >> h = f >> (g >> h)"""
    left = (a >> b) >> c
    right = a >> (b >> c)

    assert left.invoke(x) == right.invoke(x)
```

---

## Agent Factory Pattern

**Problem**: Agents with state can accidentally share memory.

```python
# BAD: Global state
class StatefulAgent:
    cache = {}  # Shared across ALL instances!
```

**Solution**: Factory functions create isolated instances.

```python
from dataclasses import dataclass, field

@dataclass
class AgentStore:
    """Per-instance storage."""
    cache: dict = field(default_factory=dict)
    history: list = field(default_factory=list)

def create_analyzer(model: str = "fast") -> TextAnalyzer:
    """Factory creates isolated agent instances."""
    store = AgentStore()
    return TextAnalyzer(model=model, store=store)

# Each call creates an independent agent
agent1 = create_analyzer()
agent2 = create_analyzer()
# agent1 and agent2 have separate stores
```

---

## Integration with D-gent (Memory)

For agents that need persistence, use D-gent patterns.

### Pattern: Universe for Typed Storage

```python
from agents.d import get_universe

async def create_memory_agent():
    """Agent backed by D-gent Universe."""
    universe = await get_universe()

    class MemoryAgent(BaseAgent[StoreRequest, StoreResult]):
        async def invoke(self, request: StoreRequest) -> StoreResult:
            # Store via Universe
            await universe.put(
                Crystal,
                id=request.id,
                content=request.content,
            )
            return StoreResult(success=True)

    return MemoryAgent()
```

### Pattern: DataBus for Reactive Events

```python
from agents.d import get_data_bus

async def create_reactive_agent():
    """Agent that emits events on action."""
    bus = await get_data_bus()

    class ReactiveAgent(BaseAgent[Action, Result]):
        async def invoke(self, action: Action) -> Result:
            result = await self._process(action)

            # Emit event for other systems
            await bus.emit("action.completed", {
                "action_id": action.id,
                "result": result.model_dump(),
            })

            return result

    return ReactiveAgent()
```

---

## Error Handling Patterns

### Pattern: Result Type

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class Result(Generic[T]):
    success: bool
    value: T | None = None
    error: str | None = None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        return cls(success=False, error=error)

class SafeAgent(BaseAgent[Request, Result[Response]]):
    async def invoke(self, request: Request) -> Result[Response]:
        try:
            response = await self._process(request)
            return Result.ok(response)
        except ValidationError as e:
            return Result.fail(f"Validation failed: {e}")
        except Exception as e:
            return Result.fail(f"Unexpected error: {e}")
```

### Pattern: Validation at Boundaries

```python
def validate_input(input: Any) -> Request:
    """Normalize and validate input at agent boundary."""
    if input is None:
        return Request(query="<empty>")

    if isinstance(input, Request):
        query = input.query.strip() if input.query else "<empty>"
        if len(query) > 10000:
            query = query[:10000] + "... [truncated]"
        return Request(query=query)

    return Request(query=str(input).strip() or "<empty>")
```

---

## Async Patterns

### Pattern: Concurrent Fan-Out

```python
import asyncio
from agents.base import parallel

async def fan_out_agent():
    """Run multiple agents concurrently, collect results."""

    async def invoke(self, input: Request) -> CombinedResult:
        # Run in parallel
        results = await asyncio.gather(
            self.agent_a.invoke(input),
            self.agent_b.invoke(input),
            self.agent_c.invoke(input),
        )

        return CombinedResult(
            a=results[0],
            b=results[1],
            c=results[2],
        )
```

### Pattern: Streaming Agent

```python
from typing import AsyncIterator

class StreamingAgent(BaseAgent[Request, AsyncIterator[Chunk]]):
    async def invoke(self, request: Request) -> AsyncIterator[Chunk]:
        """Yield chunks as they become available."""
        async for chunk in self._stream(request):
            yield Chunk(content=chunk, is_final=False)
        yield Chunk(content="", is_final=True)
```

**Gotcha**: Don't await async generators! They return the iterator directly.

```python
# WRONG
chunks = await streaming_agent.invoke(request)  # TypeError!

# RIGHT
chunks = streaming_agent.invoke(request)  # Returns AsyncIterator
async for chunk in chunks:
    print(chunk.content)
```

---

## When to Upgrade to Polynomial Agents

Use `PolyAgent[S, A, B]` when you need:

| Need | Agent[A,B] | PolyAgent[S,A,B] |
|------|------------|------------------|
| Simple transform | OK | Overkill |
| Mode-dependent inputs | Complex | Natural |
| State machine | Workaround | Built-in |
| Protocol phases | Hack | Elegant |

**Upgrade criteria**:
- You find yourself adding a `mode` or `phase` field
- Different inputs are valid at different times
- You're implementing a protocol with stages

See [polynomial-agent.md](polynomial-agent.md) for the upgrade path.

---

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Global state in agents | Factory pattern with isolated stores |
| Mutable contracts | Frozen dataclasses |
| Await async generators | Call directly, iterate with `async for` |
| Skip composition tests | Property-based tests for laws |
| Catch and swallow errors | Result types with explicit errors |

---

## Quick Reference

```python
# Basic agent
class MyAgent(BaseAgent[A, B]):
    async def invoke(self, input: A) -> B: ...

# Composition
pipeline = agent1 >> agent2 >> agent3

# Factory for isolation
def create_agent() -> MyAgent:
    store = AgentStore()
    return MyAgent(store=store)

# Identity
from agents.base import identity
Id = identity()

# Parallel
results = await asyncio.gather(a.invoke(x), b.invoke(x))
```

---

## Related Skills

- [polynomial-agent.md](polynomial-agent.md) — State machines with mode-dependent behavior
- [test-patterns.md](test-patterns.md) — Testing agents and composition laws
- [metaphysical-fullstack.md](metaphysical-fullstack.md) — Integrating agents into the stack
- [data-bus-integration.md](data-bus-integration.md) — Reactive event patterns

---

*"An agent is a morphism. Composition is the structure. Identity is the zero."*
