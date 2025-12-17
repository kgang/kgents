# S-gent Composition Patterns

> *"Functors compose. That's the point."*

---

## Purpose

This document specifies how S-gent (StateFunctor) composes with other kgents functors, particularly Flux and D-gent.

---

## The Composition Hierarchy

```
Level 3: Flux        — Continuous event processing (stream)
Level 2: State       — State threading (S-gent)
Level 1: D-gent      — Persistence substrate
Level 0: Pure logic  — (I, S) → (O, S)
```

Each level adds a capability without breaking composition.

---

## Pattern 1: State ∘ D-gent (Symbiont)

The foundational composition: state threading backed by persistence.

### Definition

```python
Symbiont = State ∘ D-gent

# Explicitly:
Symbiont[I, O, S] = StateFunctor[S](backend=D-gent) >> lift(logic)
```

### Usage

```python
from agents.d.state_functor import StateFunctor
from agents.d.backends import SQLiteBackend

# Create state functor with D-gent backend
state_functor = StateFunctor(
    state_type=ConversationState,
    backend=SQLiteBackend("conversations.db"),
    initial_state=ConversationState(history=[]),
)

# Lift pure logic to stateful agent
def chat_logic(message: str, state: ConversationState) -> tuple[str, ConversationState]:
    new_history = state.history + [f"User: {message}"]
    response = generate_response(new_history)
    return response, ConversationState(history=new_history + [f"Bot: {response}"])

chat_agent = state_functor.lift_logic(chat_logic)

# Use like any Agent[str, str]
response = await chat_agent.invoke("Hello!")
```

### Properties

| Property | Guarantee |
|----------|-----------|
| State persistence | State survives process restart |
| Logic purity | `chat_logic` is testable without I/O |
| Backend swap | Change SQLiteBackend → PostgresBackend without changing logic |

---

## Pattern 2: Flux ∘ State (Streaming Stateful)

Adds continuous processing to stateful agents.

### Definition

```python
FluxState = Flux ∘ State

# Signature:
FluxState: Agent[A, B] → FluxAgent[A, B] with state threading
```

### Usage

```python
from agents.d.state_functor import StateFunctor
from agents.flux import Flux

# Create composed functor
FluxState = StateFunctor.compose_flux(state_functor)

# Lift agent through composed functor
flux_stateful = FluxState(process_agent)

# Process stream with state threading
async for result in flux_stateful.start(event_source):
    print(result)  # Each event processed with state threaded
```

### State Threading in Streams

Each event in the stream:
1. Loads current state
2. Processes event with state
3. Saves new state
4. Yields result

```
Event 1 ──▶ [load S₀] ──▶ [process] ──▶ [save S₁] ──▶ Result 1
Event 2 ──▶ [load S₁] ──▶ [process] ──▶ [save S₂] ──▶ Result 2
Event 3 ──▶ [load S₂] ──▶ [process] ──▶ [save S₃] ──▶ Result 3
```

### The Perturbation Principle

When a FluxAgent is FLOWING and `invoke()` is called:
- The invocation becomes a **high-priority perturbation**
- It's injected into the stream, not processed separately
- State integrity is preserved (no race conditions)

```python
# Agent is streaming
async for result in flux_stateful.start(source):
    if urgent_event:
        # Perturbation: injected into stream, not separate
        await flux_stateful.invoke(urgent_event)
```

---

## Pattern 3: Flux ∘ State ∘ D-gent (Full Stack)

The complete composition: streaming, stateful, persistent.

### Definition

```python
FluxStateDgent = Flux ∘ State ∘ D-gent

# Each layer adds capability:
# D-gent:  Persistence (WHERE state lives)
# State:   Threading (HOW state flows)
# Flux:    Streaming (WHEN processing happens)
```

### Usage

```python
# Level 1: D-gent backend
backend = SQLiteBackend("process_state.db")

# Level 2: State functor
state_functor = StateFunctor(
    state_type=ProcessorState,
    backend=backend,
    initial_state=ProcessorState(),
)

# Level 3: Flux composition
flux_stateful = Flux.lift(state_functor.lift(processor_agent))

# Full stack: streaming + stateful + persistent
async for result in flux_stateful.start(event_source):
    # Each event:
    # 1. Loads state from SQLite
    # 2. Processes with state
    # 3. Saves new state to SQLite
    # 4. Yields result to stream
    process_result(result)
```

---

## Pattern 4: TableAdapter Integration

Typed state from Alembic tables.

### Definition

```python
TypedState = StateFunctor.from_table_adapter(adapter)

# State type S is an Alembic model:
# - Schema-enforced (typed)
# - Migration-versioned
# - Queryable via SQL
```

### Usage

```python
from agents.d.adapters.table_adapter import TableAdapter
from models.brain import Crystal

# Create adapter for Alembic table
crystal_adapter = TableAdapter(Crystal, session_factory)

# Create StateFunctor with typed state
crystal_state = StateFunctor.from_table_adapter(
    adapter=crystal_adapter,
    initial_state=Crystal(id="session_crystal", tags=[], access_count=0),
)

# Lift agent
crystal_agent = crystal_state.lift(analysis_agent)

# Compose with Flux
flux_crystal = Flux.lift(crystal_agent)

# Each stream event:
# 1. Loads Crystal from Alembic table
# 2. Passes to analysis_agent with typed state
# 3. Saves updated Crystal back to table
# 4. Yields analysis result
```

### Why TableAdapter?

| Without TableAdapter | With TableAdapter |
|---------------------|-------------------|
| Schema-free Datum | Typed Alembic model |
| No migrations | Versioned schema |
| Bytes content | Queryable columns |
| Lens-only access | SQL queries possible |

---

## Composition Laws

### Functor Composition Law

```
(Flux ∘ State).lift(agent) ≅ Flux.lift(State.lift(agent))
```

Composing functors then lifting equals lifting then composing.

### Identity Preservation

```
Flux ∘ State ∘ D-gent (Id) ≅ Id (with stream + state + persistence overhead)
```

### Associativity

```
(Flux ∘ State) ∘ D-gent ≅ Flux ∘ (State ∘ D-gent)
```

Functor composition is associative.

---

## State Sharing Patterns

### Independent State

Default: each StatefulAgent has isolated state.

```python
# Independent state via namespace
chat_functor = StateFunctor(..., namespace="chat")
memory_functor = StateFunctor(..., namespace="memory")

# No interference between chat and memory state
```

### Shared State (Blackboard)

Multiple agents share state through lenses.

```python
# Shared backend
shared_backend = SQLiteBackend("shared.db")

# Different lenses into shared state
user_lens = key_lens("users")
product_lens = key_lens("products")

# Agents with lensed access
user_agent = StateFunctor(
    state_type=dict,
    backend=LensBackend(shared_backend, user_lens),
)

product_agent = StateFunctor(
    state_type=dict,
    backend=LensBackend(shared_backend, product_lens),
)
```

### Forked State (Branching)

For exploration, fork state into isolated branches.

```python
async def fork_stateful(
    agent: StatefulAgent[S, A, B],
    branches: int
) -> list[StatefulAgent[S, A, B]]:
    """Fork state for parallel exploration."""
    current_state = await agent._load_state()

    forks = []
    for i in range(branches):
        fork_backend = MemoryBackend()
        await fork_backend.save(copy.deepcopy(current_state))
        forks.append(StatefulAgent(
            inner=agent.inner,
            backend=fork_backend,
            state_type=agent.state_type,
            initial_state=None,
            namespace=f"fork_{i}",
        ))

    return forks
```

---

## Integration Points

### With Crown Jewels

| Jewel | Composition Pattern |
|-------|---------------------|
| **Brain** | `StateFunctor.from_table_adapter(Crystal)` — typed crystal state |
| **Town** | `Flux ∘ State` — citizen conversations are streaming stateful |
| **Gardener** | `State ∘ D-gent` — idea lifecycle is stateful persistent |

### With PolyAgent

StatefulAgent can be lifted to polynomial positions:

```python
# Polynomial with stateful position
poly = PolyAgent[Status, Request, Response](
    state=Status.READY,
    directions={
        Status.READY: StateFunctor.lift(ready_handler),
        Status.PROCESSING: StateFunctor.lift(process_handler),
    },
    transition=status_transition,
)
```

### With AGENTESE

State access through established paths:

```python
# State threading is implicit in agent composition
# Access persisted state through D-gent:
await logos.invoke("self.data.get[state_id]", umwelt)

# Or through typed table:
await logos.invoke("self.data.table.crystal.get[id]", umwelt)
```

---

## Anti-patterns

### 1. Double State Loading

```python
# BAD: Loading state twice in stream
async for event in source:
    state = await backend.load()  # Manual load
    result = await stateful_agent.invoke(event)  # Also loads state!

# GOOD: Let StatefulAgent handle loading
async for event in source:
    result = await stateful_agent.invoke(event)  # Handles state
```

### 2. Mixing Persistence Tiers

```python
# BAD: State split across tiers without bridge
half_in_memory = MemoryBackend()
half_in_sqlite = SQLiteBackend("state.db")
# Inconsistent state!

# GOOD: Single backend or proper bridging
backend = SQLiteBackend("state.db")
state_functor = StateFunctor(backend=backend)
```

### 3. Unbounded Stream State

```python
# BAD: State grows without bound
def logic(event: Event, state: S) -> tuple[Result, S]:
    return result, S(history=state.history + [event])  # Grows forever!

# GOOD: Bounded state
def logic(event: Event, state: S) -> tuple[Result, S]:
    bounded_history = (state.history + [event])[-1000:]  # Keep last 1000
    return result, S(history=bounded_history)
```

---

## See Also

- [README.md](README.md) — S-gent overview
- [state-functor.md](state-functor.md) — StateFunctor specification
- [laws.md](laws.md) — Functor laws and proofs
- [../c-gents/functor-catalog.md](../c-gents/functor-catalog.md) — Functor catalog (§13 Flux, §14 State)
- [../d-gents/dual-track.md](../d-gents/dual-track.md) — Dual-track architecture

---

*"Composition is not just syntactic sugar. It's the reason these abstractions exist."*
