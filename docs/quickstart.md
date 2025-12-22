---
context: world
---

# Quickstart — Zero to Agent

> *"The difference between a good system and a great one is the last 5%."*

Five minutes. No fluff. Let's build.

---

## Install

```bash
# Clone the garden
git clone https://github.com/kentgang/kgents.git
cd kgents

# Grow the environment (uv: https://github.com/astral-sh/uv)
uv sync

# Verify life
kg --help   # (or 'kgents --help')

# Run the test suite (11,170+ tests, ~2 min)
cd impl/claude && uv run pytest -q

# Verify types (strict mypy)
uv run mypy .
```

**Requirements**: Python 3.12+ | [uv](https://github.com/astral-sh/uv) for dependency management

**If tests fail**: Check Python version (`python --version`). Most failures come from 3.11 or earlier.

---

## Your First Agent (60 seconds)

```python
from agents import agent

@agent
async def greet(name: str) -> str:
    return f"Hello, {name}!"

# Run it
result = await greet.invoke("World")
print(result)  # "Hello, World!"
```

That's it. An agent is a function with superpowers.

<details>
<summary>🌫️ Ghost: Why not start with K-gent?</summary>

K-gent is the soul of kgents—the governance functor, the personality space navigator, the categorical imperative made code. It's the *interesting* part.

We considered opening with it. Show the personality eigenvectors! The hypnagogia dreams! The dialectic challenges!

But K-gent requires understanding:
- Functors (it's a functor)
- Polynomials (it has modes)
- AGENTESE (it lives at `self.soul`)
- The Accursed Share (it tithes entropy)

Starting with K-gent would be *daring* but not *tasteful*. You'd see fireworks without understanding the chemistry.

So we start with `@agent` and `>>`. The composition laws. The categorical ground. K-gent comes later, and when it does, you'll know why it works.

*"Depth over breadth"* — including depth of understanding.

</details>

---

## Composition — The Real Magic

Agents compose via `>>`. This isn't syntax sugar—it's category theory made practical.

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

# Compose
pipe = parse >> double >> format

# Run
result = await pipe.invoke("21")
print(result)  # "Result: 42"
```

The `>>` operator satisfies associativity: `(a >> b) >> c == a >> (b >> c)`.

This isn't aspirational. It's verified at runtime via `BootstrapWitness.verify_composition_laws()`.

---

## Functors — Adding Superpowers

Want to handle optional values without crashing? Lift your agent to the Maybe domain:

```python
from agents import Maybe, Just, Nothing, MaybeFunctor

@agent
async def divide(pair: tuple[int, int]) -> float:
    a, b = pair
    return a / b

# Lift to Maybe domain
safe_divide = MaybeFunctor.lift(divide)

await safe_divide.invoke(Just((10, 2)))  # Just(5.0)
await safe_divide.invoke(Nothing)         # Nothing (no crash!)
```

Functors preserve composition: if `f >> g` works, so does `F.lift(f) >> F.lift(g)`.

Laws, not vibes.

---

## K-gent — The Governance Functor

K-gent isn't a chatbot. It's a categorical imperative—a point in personality-space that every response navigates toward.

K-gent has six eigenvectors: aesthetic, categorical, gratitude, heterarchy, generativity, joy. Each shapes how it responds. The CLI interface is under active development—for now, K-gent is best accessed via the Python API or web interface.

---

## AGENTESE — Observation Is Interaction

Traditional APIs return static JSON. AGENTESE returns **handles**—morphisms that depend on who's observing.

```python
from protocols.agentese import Logos

logos = Logos()

# Same path, different observers, different perceptions
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
```

**The Five Contexts**:

| Context | Scope | Examples |
|---------|-------|----------|
| `world.*` | External | Entities, tools, environments |
| `self.*` | Internal | Memory, state, capability |
| `concept.*` | Abstract | Platonics, definitions, logic |
| `void.*` | Entropy | Serendipity, gratitude, tithe |
| `time.*` | Temporal | Traces, forecasts, schedules |

No kitchen-sink API. This is the complete ontology.

---

## Web Interface

```bash
# Terminal 1: Backend API
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Frontend
cd impl/claude/web
npm install && npm run dev
# Visit http://localhost:3000
```

---

## Common Gotchas (Read Before You Hit Them)

### DI Enlightened Resolution (2025-12-21)
```python
@node(dependencies=("soul_provider",))  # If not registered → DependencyNotFoundError (fast!)
class MyNode: ...                        # Error tells you exactly what to add

# Required deps fail immediately with actionable message
# Optional deps (with `= None` default) skip gracefully
```

### Import-Time Registration
```python
# @node decorator runs at import time
# If your module isn't imported → node doesn't exist
# Fix: Ensure _import_node_modules() in gateway.py includes your module
```

### Frontend Type Drift
```bash
# Backend changed. Frontend has stale types. Silent failures.
cd impl/claude/web && npm run typecheck  # Run before every commit
```

### The Timer Zombie
```python
# ❌ Creates zombie processes that outlive their welcome
while True:
    await asyncio.sleep(1.0)
    do_work()

# ✅ Use event-driven Flux instead
async for event in event_stream:
    process(event)
```

**Pro tip**: When something fails silently, check `services/providers.py` first. 90% of cryptic errors are missing DI registrations.

---

## What's Next?

| Resource | What You'll Learn |
|----------|-------------------|
| [Skills](skills/) | The 13 essential skills (start here) |
| [Architecture](architecture-overview.md) | How the pieces fit |
| [Systems Reference](systems-reference.md) | Built infrastructure inventory |
| [Principles](../spec/principles.md) | The seven principles + 12 ADs |

### Skills Worth Reading Now

| Skill | When You'll Need It |
|-------|---------------------|
| [metaphysical-fullstack](skills/metaphysical-fullstack.md) | Building any feature |
| [crown-jewel-patterns](skills/crown-jewel-patterns.md) | Service logic (14 patterns) |
| [agentese-node-registration](skills/agentese-node-registration.md) | Exposing paths via @node |
| [polynomial-agent](skills/polynomial-agent.md) | State machines with modes |

---

## The Accursed Share

Even in quickstarts, we leave room for serendipity.

The 10% exploration budget means your agents can wander productively:

```python
pipeline = await void.compose.sip(
    primitives=PRIMITIVES,
    grammar=SOUL_OPERAD,
    entropy=0.10
)
```

This isn't inefficiency. It's how gardens grow.

<details>
<summary>🌫️ Ghost: The Fifth Context</summary>

Four contexts made sense: `world` (external), `self` (internal), `concept` (abstract), `time` (temporal). Clean, complete, symmetric.

Then we noticed the waste. Every system generates surplus—ideas that don't fit, tangents that lead nowhere, exploration that produces nothing "useful." What do you do with it?

The efficient answer: discard it. Prune ruthlessly. Every token serves the goal.

But Bataille taught us differently. Surplus energy that isn't *spent* becomes destructive. The system that can't waste becomes brittle.

So we added `void.*`—the Accursed Share context. Where you `sip` entropy for exploration. Where you `tithe` to maintain order. Where failed experiments go not to die but to compost.

The ghost is in the name: *void* sounds empty, but it's the fullest context of all. It holds everything we chose not to choose.

*"Everything is slop or comes from slop. We cherish and express gratitude and love."*

</details>

---

*"The river that knows its course flows without thinking."*
