# Alethic Algebra: Polish & Batteries Included

> *"The skeleton exists. The algebra provides the muscles. The soul breathes life. Now give it dance lessons."*

## Context

The Alethic Algebra is **95% complete**. The categorical foundation is operational:

- **10+ functors** registered: Maybe, Either, List, Async, Logged, Fix, Flux, Soul, Observer, State
- **Symmetric lifting**: `lift()`/`unlift()` for all major functors
- **Cross-functor composition**: `compose_functors(SoulFunctor, MaybeFunctor)` works
- **LocalProjector**: Compiles Halo → runtime in canonical order
- **K8sProjector**: Generates Kubernetes manifests from Halo
- **CLI**: `kgents a {list,inspect,manifest,run}` operational
- **337+ tests** passing

The architecture is sound. Now make it **delightful to use**.

## Your Mission: Polish, Usability, Batteries Included

### 1. Developer Experience (DX) Quick Wins

**Goal**: A developer can go from zero to working agent in 5 minutes.

Create `impl/claude/agents/examples/` with:
- `hello_world.py` — Minimal agent (3 lines of real code)
- `stateful_counter.py` — `@Stateful` example with state access
- `soulful_advisor.py` — `@Soulful` example with persona
- `streaming_processor.py` — `@Streamable` with Flux patterns
- `composed_pipeline.py` — Multiple agents composed via `>>`

Each example should:
- Be runnable: `python -m agents.examples.hello_world`
- Have a docstring that explains *why*, not just *what*
- Demonstrate one concept clearly

### 2. Convenience Imports ("Batteries Included")

**Goal**: `from agents import *` gives you everything you need.

Update `impl/claude/agents/__init__.py` to export:
```python
# Core types
from bootstrap.types import Agent

# Functors (the algebra)
from agents.a.functor import (
    UniversalFunctor,
    FunctorRegistry,
    compose_functors,
    verify_functor,
)

# Capabilities (the decorators)
from agents.a.halo import (
    Capability,
    Stateful, Soulful, Observable, Streamable,
    get_halo, has_capability,
)

# Archetypes (the presets)
from agents.a.archetype import Kappa, Lambda, Delta

# C-gent (composition primitives)
from agents.c.functor import (
    Maybe, Just, Nothing,
    Either, Left, Right,
    MaybeFunctor, EitherFunctor, ListFunctor,
)

# K-gent (soul)
from agents.k.functor import Soul, SoulFunctor, soul, soul_lift

# Flux (streaming)
from agents.flux import FluxAgent, Flux
from agents.flux.functor import FluxFunctor

# Projector (compilation)
from system.projector import LocalProjector
```

### 3. One-Liner Agent Creation

**Goal**: The simplest possible agent definition.

Add to `agents/a/quick.py`:
```python
def agent(fn: Callable[[A], Awaitable[B]]) -> Agent[A, B]:
    """
    Decorator to create an agent from an async function.

    Example:
        @agent
        async def double(x: int) -> int:
            return x * 2

        result = await double.invoke(5)  # 10
    """
    ...

def pipeline(*agents: Agent) -> Agent:
    """
    Compose multiple agents into a pipeline.

    Example:
        pipe = pipeline(double, add_one, stringify)
        result = await pipe.invoke(5)  # "11"
    """
    ...
```

### 4. CLI Polish

**Goal**: Make `kgents a` a joy to use.

Add to existing CLI:
- `kgents a new <name>` — Scaffold a new agent with boilerplate
- `kgents a test <name>` — Run tests for a specific agent
- `kgents a docs <name>` — Generate docs for an agent's Halo
- Improve `kgents a list` output with Halo summary

### 5. Documentation: The Functor Field Guide

**Goal**: A developer understands the algebra without reading category theory.

Create `docs/functor-field-guide.md`:

```markdown
# The Functor Field Guide

> *"A functor is a way to transform agents while preserving their structure."*

## The Core Insight

You have an agent that does one thing well:
    double: Agent[int, int]  # Doubles numbers

But your input might be missing:
    input: Maybe[int] = Just(5)  # or Nothing

**The functor lifts your agent to handle the new context:**
    lifted = MaybeFunctor.lift(double)
    await lifted.invoke(Just(5))   # Just(10)
    await lifted.invoke(Nothing)   # Nothing (no error!)

## The Functor Zoo

| Functor | Handles | Example Use Case |
|---------|---------|------------------|
| Maybe   | Optional values | User might not provide input |
| Either  | Success/Error | API might fail |
| List    | Collections | Process batch of items |
| Async   | Background work | Fire-and-forget |
| Logged  | Observability | Debug production issues |
| Fix     | Retries | Transient network failures |
| Soul    | Personality | K-gent persona awareness |
| Flux    | Streams | Real-time event processing |
| Observer| Telemetry | Metrics and tracing |
| State   | Memory | Maintain state across calls |

## Composition: The Magic

Functors compose. Need retry with logging?

    stack = compose_functors(LoggedFunctor, FixFunctor)
    resilient_agent = stack(my_agent)

## The Laws (Why It Works)

Every functor satisfies two laws:
1. **Identity**: `F(id) = id` — Lifting identity does nothing
2. **Composition**: `F(g >> f) = F(g) >> F(f)` — Lifting preserves composition

These laws guarantee composition is safe. Break them, break everything.
```

### 6. Test Helpers

**Goal**: Testing agents should be easy.

Add to `agents/t/helpers.py`:
```python
async def assert_agent_output(agent: Agent[A, B], input: A, expected: B) -> None:
    """Assert an agent produces expected output."""
    ...

async def assert_functor_laws(functor: type[UniversalFunctor]) -> None:
    """Verify a functor satisfies identity and composition laws."""
    ...

def mock_agent(return_value: B) -> Agent[Any, B]:
    """Create a mock agent that always returns the given value."""
    ...
```

### 7. Type Stubs (Optional but Nice)

If time permits, ensure mypy is happy with all the new conveniences:
- Proper overloads for `compose_functors`
- Generic type preservation through `pipeline()`
- Capability decorator typing

## Success Criteria

- [ ] Examples directory with 5 runnable examples
- [ ] `from agents import *` provides useful defaults
- [ ] `@agent` decorator works for quick agent creation
- [ ] `kgents a new` scaffolds a new agent
- [ ] `docs/functor-field-guide.md` explains the algebra accessibly
- [ ] Test helpers exist and are documented
- [ ] All new code has tests
- [ ] mypy clean

## Anti-Patterns to Avoid

- Don't break backward compatibility
- Don't add features that don't compose
- Don't document implementation details (document behavior)
- Don't scaffold bloated boilerplate (minimal is beautiful)

## The Vibe

This is the *finishing touch*. The architecture is right. The tests pass. Now make someone smile when they use it for the first time.

Think Apple: "It just works."
Think Stripe: "The best API is no API."
Think Kent: "Tasteful > feature-complete."

---

*"The difference between a good system and a great one is the last 5%."*
