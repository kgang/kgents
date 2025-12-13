# Quickstart Guide

> *"Zero to agent in 5 minutes."*

This guide gets you from installation to running your first agent as quickly as possible.

---

## Installation

```bash
# Clone
git clone https://github.com/kgang/kgents.git
cd kgents

# Install (uv recommended)
uv sync

# Verify
kgents --help
```

---

## Your First Agent

### 1. Hello World

```python
from agents import agent

@agent
async def hello(name: str) -> str:
    return f"Hello, {name}!"

# Run it
result = await hello.invoke("World")
print(result)  # "Hello, World!"
```

### 2. Composing Agents

```python
from agents import agent, pipeline

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
pipe = parse >> double >> format
result = await pipe.invoke("21")
print(result)  # "Result: 42"
```

### 3. Lifting to Handle Optional Values

```python
from agents import Maybe, Just, Nothing, MaybeFunctor

@agent
async def divide(pair: tuple[int, int]) -> float:
    a, b = pair
    return a / b

# Lift to handle Maybe inputs
safe_divide = MaybeFunctor.lift(divide)

await safe_divide.invoke(Just((10, 2)))  # Just(5.0)
await safe_divide.invoke(Nothing)         # Nothing (no error!)
```

---

## CLI Commands

### K-gent (Persona)

```bash
kgents soul                  # Interactive chat
kgents soul challenge "idea" # Dialectic challenge
kgents soul dream            # Trigger dream cycle
```

### Infrastructure

```bash
kgents status               # System health
kgents a list               # List archetypes
kgents a inspect Kappa      # Inspect capabilities
```

### Observation

```bash
kgents observe trace        # Execution traces
kgents signal               # Semantic field
```

---

## Next Steps

| Document | What You'll Learn |
|----------|-------------------|
| [Functor Field Guide](functor-field-guide.md) | Lifting agents to new contexts |
| [Operator's Guide](operators-guide.md) | Production scenarios |
| [Categorical Foundations](categorical-foundations.md) | The math behind it |

---

*"The difference between a good system and a great one is the last 5%."*
