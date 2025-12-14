---
path: plans/skills/flux-agent
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: Creating a Flux Agent

> Lift a discrete agent to continuous stream processing using the Flux Functor.

**Difficulty**: Medium
**Prerequisites**: Python async/await, understanding of `Agent[A, B]` protocol
**Files Touched**: Your agent implementation, potentially `agents/flux/` for extensions

---

## Overview

**Flux** lifts agents from discrete transformations to continuous flow:

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T]
```

| Mode | Description |
|------|-------------|
| **Static** | `Agent: A → B` — a point transformation (invoke once, get result) |
| **Dynamic** | `Flux(Agent): dA/dt → dB/dt` — continuous flow (stream in, stream out) |

Use Flux when you need:
- Stream processing (events, logs, messages)
- Long-running agents that respond to events
- Composable pipelines (`flux_a | flux_b | flux_c`)
- Backpressure handling and entropy budgeting

---

## Step-by-Step: Minimal Flux Agent

### Step 1: Create a Discrete Agent

Start with a standard `Agent[A, B]`.

**Pattern**:
```python
from bootstrap.types import Agent

class MyAgent(Agent[str, str]):
    """Processes strings."""

    @property
    def name(self) -> str:
        return "MyAgent"

    async def invoke(self, input: str) -> str:
        # Your processing logic here
        return input.upper()
```

### Step 2: Lift to Flux

Use `Flux.lift()` to lift your agent to the streaming domain.

**Pattern**:
```python
from agents.flux import Flux

# Create the discrete agent
agent = MyAgent()

# Lift to flux
flux_agent = Flux.lift(agent)
```

### Step 3: Start with a Source

Call `start()` with an `AsyncIterator` source.

**Pattern**:
```python
import asyncio
from typing import AsyncIterator

# Create an async source
async def my_source() -> AsyncIterator[str]:
    for item in ["hello", "world", "flux"]:
        yield item

# Process the stream
async def main():
    flux_agent = Flux.lift(MyAgent())

    async for result in flux_agent.start(my_source()):
        print(result)  # HELLO, WORLD, FLUX

asyncio.run(main())
```

---

## Step-by-Step: Configured Flux Agent

### Step 1: Create FluxConfig

Configure entropy, backpressure, and feedback.

**File**: Your code or `agents/flux/config.py` reference

**Pattern**:
```python
from agents.flux import FluxConfig

config = FluxConfig(
    # Entropy (computation budget)
    entropy_budget=10.0,      # Initial budget (default: 1.0)
    entropy_decay=0.1,        # Consumed per event (default: 0.01)
    max_events=100,           # Hard cap (default: None = unlimited)

    # Backpressure (slow consumer handling)
    buffer_size=50,           # Output buffer size (default: 100)
    drop_policy="drop_oldest", # block | drop_oldest | drop_newest

    # Observability
    agent_id="my-flux-001",   # For logs/traces (default: auto-generated)
    emit_pheromones=True,     # Emit signals for monitoring
)
```

### Step 2: Lift with Config

**Pattern**:
```python
from agents.flux import Flux, FluxConfig

config = FluxConfig(
    entropy_budget=10.0,
    buffer_size=50,
)

flux_agent = Flux.lift(MyAgent(), config)
```

### Alternative: Use Config Factories

```python
from agents.flux import FluxConfig

# Runs until source exhausts (no entropy limit)
infinite_config = FluxConfig.infinite()

# Processes exactly N events then stops
bounded_config = FluxConfig.bounded(max_events=1000)

# With ouroboric feedback (30% of output feeds back to input)
ouroboric_config = FluxConfig.ouroboric(feedback_fraction=0.3)
```

---

## Step-by-Step: Flux Pipeline (Composition)

### Step 1: Create Multiple Flux Agents

```python
class DoubleAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2

class AddOneAgent(Agent[int, int]):
    @property
    def name(self) -> str:
        return "AddOne"

    async def invoke(self, input: int) -> int:
        return input + 1
```

### Step 2: Compose with Pipe Operator

```python
from agents.flux import Flux

flux_double = Flux.lift(DoubleAgent())
flux_add = Flux.lift(AddOneAgent())

# Compose: double then add one
pipeline = flux_double | flux_add

# Process: 0→0→1, 1→2→3, 2→4→5, ...
async for result in pipeline.start(async_range(5)):
    print(result)  # 1, 3, 5, 7, 9
```

### Alternative: Use >> for Static Agent Composition

```python
# Compose flux with static agent (doesn't lift second agent)
flux_agent = Flux.lift(DoubleAgent()) >> AddOneAgent()
```

---

## Step-by-Step: Perturbation (Inject into Running Flux)

### Step 1: Start the Flux

```python
flux_agent = Flux.lift(MyAgent())

# Start in background task
async def run_flux():
    async for result in flux_agent.start(my_source()):
        print(f"Output: {result}")

task = asyncio.create_task(run_flux())
```

### Step 2: Invoke During Flow (Perturbation)

When flux is FLOWING, `invoke()` becomes a perturbation:

```python
# While flux is running, inject high-priority event
result = await flux_agent.invoke("urgent-event")
print(f"Perturbation result: {result}")
```

**Key Insight**: Perturbations flow through the same state-loading path as normal events, preserving state integrity.

---

## Step-by-Step: Ouroboric Feedback

### Step 1: Configure Feedback

```python
config = FluxConfig(
    feedback_fraction=0.3,  # 30% of outputs feed back
    feedback_transform=lambda result: result.as_context(),  # B → A transform
)

flux_agent = Flux.lift(MyAgent(), config)
```

### Step 2: Understand Feedback Fraction

| Fraction | Behavior |
|----------|----------|
| 0.0 | Pure reactive (no feedback) |
| 0.1-0.3 | Light context accumulation |
| 0.5 | Equal external/internal influence |
| 1.0 | Full ouroboros (solipsism risk!) |

---

## Verification

### Test 1: Start returns AsyncIterator

```bash
cd impl/claude
uv run python -c "
import asyncio
from agents.flux import Flux
from bootstrap.types import Agent

class Echo(Agent[str, str]):
    @property
    def name(self): return 'Echo'
    async def invoke(self, x): return x

async def source():
    yield 'test'

async def main():
    flux = Flux.lift(Echo())
    result = flux.start(source())
    assert hasattr(result, '__anext__')
    print('OK: start() returns AsyncIterator')

asyncio.run(main())
"
```

### Test 2: Process events

```bash
uv run python -c "
import asyncio
from agents.flux import Flux
from bootstrap.types import Agent

class Double(Agent[int, int]):
    @property
    def name(self): return 'Double'
    async def invoke(self, x): return x * 2

async def source():
    for i in range(5):
        yield i

async def main():
    flux = Flux.lift(Double())
    results = [r async for r in flux.start(source())]
    assert results == [0, 2, 4, 6, 8]
    print(f'OK: {results}')

asyncio.run(main())
"
```

### Test 3: Run tests

```bash
cd impl/claude
uv run pytest agents/flux/_tests/test_agent.py -v
```

---

## Common Pitfalls

### 1. Treating start() as void

**Wrong**:
```python
flux.start(source)  # Discards the output!
```

**Right**:
```python
async for result in flux.start(source):
    process(result)
```

The KEY insight: `start()` returns `AsyncIterator[B]`, not `None`. This enables Living Pipelines.

### 2. Using asyncio.sleep() for timing

**Wrong**:
```python
async def my_source():
    while True:
        await asyncio.sleep(1.0)  # Timer zombie
        yield event
```

**Right**:
```python
async def my_source():
    async for event in external_event_stream:
        yield event  # Event-driven
```

Flux is event-driven, not timer-driven.

### 3. Bypassing the stream during FLOWING

**Wrong**:
```python
if flux._state == FluxState.FLOWING:
    result = await flux.inner.invoke(x)  # Bypasses stream!
```

**Right**:
```python
result = await flux.invoke(x)  # Proper perturbation injection
```

### 4. feedback_fraction=1.0 without external input

**Wrong**:
```python
config = FluxConfig(feedback_fraction=1.0)
# With finite source → closed loop → infinite
```

Use `feedback_fraction < 1.0` or ensure continuous external input.

### 5. Not handling entropy exhaustion

**Symptom**: Flux stops unexpectedly.

**Fix**: Use appropriate entropy budget or `FluxConfig.infinite()`:
```python
# For long-running agents
config = FluxConfig(entropy_budget=float("inf"), entropy_decay=0.0)
```

### 6. Not awaiting perturbation results

**Wrong**:
```python
flux.invoke("event")  # Fire and forget (result lost)
```

**Right**:
```python
result = await flux.invoke("event")  # Wait for processing
```

---

## Flux States

```
DORMANT   → Created, not started (invoke works directly)
FLOWING   → Processing stream (invoke = perturbation)
DRAINING  → Source exhausted, flushing output
STOPPED   → Explicitly stopped
COLLAPSED → Entropy depleted
```

---

## Real Example: Event Processor

```python
from dataclasses import dataclass
from typing import AsyncIterator
from agents.flux import Flux, FluxConfig
from bootstrap.types import Agent

@dataclass
class Event:
    type: str
    data: dict

@dataclass
class ProcessedEvent:
    original_type: str
    summary: str

class EventProcessor(Agent[Event, ProcessedEvent]):
    @property
    def name(self) -> str:
        return "EventProcessor"

    async def invoke(self, event: Event) -> ProcessedEvent:
        # Your processing logic
        summary = f"Processed {event.type}: {len(event.data)} fields"
        return ProcessedEvent(
            original_type=event.type,
            summary=summary,
        )

async def kafka_events() -> AsyncIterator[Event]:
    """Simulated event source."""
    events = [
        Event("user.login", {"user_id": "123"}),
        Event("order.created", {"order_id": "456", "items": [1, 2, 3]}),
        Event("user.logout", {"user_id": "123"}),
    ]
    for event in events:
        yield event

async def main():
    config = FluxConfig(
        entropy_budget=100.0,
        buffer_size=50,
        agent_id="event-processor-001",
    )

    flux_processor = Flux.lift(EventProcessor(), config)

    async for processed in flux_processor.start(kafka_events()):
        print(f"{processed.original_type}: {processed.summary}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Related Skills

- [agentese-path](agentese-path.md) - Adding AGENTESE paths
- [test-patterns](test-patterns.md) - Testing async agents

---

## Changelog

- 2025-12-12: Initial version based on flux implementation
