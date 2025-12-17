# StateFunctor: The State Monad as Functor

> *"Lift agents into stateful computation."*

---

## Purpose

StateFunctor lifts `Agent[A, B]` into stateful computation where state S is:
1. Loaded before each invocation
2. Threaded through the computation
3. Saved after each invocation

---

## Formal Definition

### The Functor

```
StateFunctor[S]: C_Agent → C_Agent

Where:
- Objects: Agent[A, B]
- Morphisms: Natural transformations
- S: The state type
```

### Category-Theoretic Properties

StateFunctor is an **endofunctor** on the Agent category—it maps agents to agents while preserving structure.

```
Original:     Agent[A, B]
Lifted:       StatefulAgent[S, A, B]  (still an Agent[A, B])

The interface (A → B) is preserved.
The implementation gains state threading.
```

---

## Core Operations

### StateFunctor[S]

```python
@dataclass
class StateFunctor(Generic[S]):
    """
    State Monad as a first-class functor.

    Lifts agents into stateful computation where state is:
    1. Loaded before each invocation
    2. Threaded through the logic
    3. Saved after each invocation

    Category-theoretic:
        StateFunctor[S]: C_Agent → C_Agent
        Where objects are Agent[A, B] and morphisms are natural transformations

    Relationship to Symbiont:
        StateFunctor is the generalized form of Symbiont.
        Symbiont = StateFunctor[S].lift(logic_as_agent) with DgentProtocol backend
    """

    state_type: type[S]
    backend: DgentProtocol
    initial_state: S | None = None
    namespace: str = "state"

    def lift(self, agent: Agent[A, B]) -> StatefulAgent[S, A, B]:
        """
        Lift an agent into stateful computation.

        StateFunctor.lift: Agent[A, B] → StatefulAgent[S, A, B]

        The lifted agent:
        - Loads state S before invoking the inner agent
        - Passes (input, state) to create extended input
        - Saves new state after invocation
        - Returns output B
        """
        return StatefulAgent(
            inner=agent,
            backend=self.backend,
            state_type=self.state_type,
            initial_state=self.initial_state,
            namespace=self.namespace,
        )

    def lift_logic(
        self,
        logic: Callable[[A, S], tuple[B, S]],
    ) -> StatefulAgent[S, A, B]:
        """
        Lift a pure logic function directly.

        This is the Symbiont pattern: (I, S) → (O, S) becomes Agent[I, O] with state.
        """
        logic_agent = _LogicAgent(logic)
        return self.lift(logic_agent)
```

### StatefulAgent[S, A, B]

```python
@dataclass
class StatefulAgent(Agent[A, B], Generic[S, A, B]):
    """
    An agent with explicit state threading.

    This is the result of StateFunctor.lift(agent).

    State lifecycle per invocation:
    1. Load: state = await backend.load(namespace)
    2. Invoke: output = await inner.invoke(input, state)
    3. Save: await backend.save(namespace, new_state)
    4. Return: output
    """

    inner: Agent[A, B]
    backend: DgentProtocol
    state_type: type[S]
    initial_state: S | None
    namespace: str

    async def invoke(self, input_data: A) -> B:
        """
        Invoke with state threading.

        If inner agent expects (A, S) tuple, pass it.
        Otherwise, just pass A and manage state separately.
        """
        # 1. Load current state
        state = await self._load_state()

        # 2. Invoke inner agent with extended input
        try:
            result = await self.inner.invoke((input_data, state))
            if isinstance(result, tuple) and len(result) == 2:
                output, new_state = result
            else:
                output, new_state = result, state
        except TypeError:
            # Inner agent doesn't accept tuple, use simple invocation
            output = await self.inner.invoke(input_data)
            new_state = state

        # 3. Save new state
        await self._save_state(new_state)

        # 4. Return output
        return output
```

---

## Functor Laws

### Identity Law

```
StateFunctor.lift(Id) ≅ Id
```

Lifting the identity agent produces behavior equivalent to identity (modulo state loading/saving overhead).

**Verification**:
```python
async def test_identity_law(state_functor, memory_backend):
    lifted_id = state_functor.lift(Id)
    input_val = "test"
    result = await lifted_id.invoke(input_val)
    assert result == input_val  # Identity behavior preserved
```

### Composition Law

```
StateFunctor.lift(f >> g) ≅ StateFunctor.lift(f) >> StateFunctor.lift(g)
```

Lifting a composition equals composing lifted agents.

**Verification**:
```python
async def test_composition_law(state_functor):
    double = Agent.from_function(lambda x: x * 2)
    add_one = Agent.from_function(lambda x: x + 1)

    # Composition 1: lift(f >> g)
    composed_then_lifted = state_functor.lift(double >> add_one)

    # Composition 2: lift(f) >> lift(g)
    lifted_then_composed = state_functor.lift(double) >> state_functor.lift(add_one)

    # Both should produce same result
    input_val = 5
    result1 = await composed_then_lifted.invoke(input_val)
    result2 = await lifted_then_composed.invoke(input_val)
    assert result1 == result2 == 11  # (5 * 2) + 1
```

---

## Composition with Flux

### compose_flux: Creating Flux(State(agent))

```python
@staticmethod
def compose_flux(
    state_functor: StateFunctor[S],
) -> Callable[[Agent[A, B]], FluxAgent[A, B]]:
    """
    Compose StateFunctor with Flux functor.

    Returns: Flux ∘ StateFunctor

    Usage:
        FluxState = StateFunctor.compose_flux(state_functor)
        flux_stateful = FluxState(agent)  # Flux(State(agent))

    The composed functor creates an agent that:
    1. Processes events as a stream (Flux)
    2. Threads state through each event (State)
    3. Respects the Perturbation Principle (invoke → inject into stream)
    """
    def composed_lift(agent: Agent[A, B]) -> FluxAgent[A, B]:
        stateful = state_functor.lift(agent)
        return Flux.lift(stateful)
    return composed_lift
```

### Usage Pattern

```python
# Create state functor
state_functor = StateFunctor(
    state_type=ProcessorState,
    backend=dgent_backend,
)

# Compose with Flux
FluxState = StateFunctor.compose_flux(state_functor)
flux_stateful = FluxState(process_agent)

# Process stream with state threading
async for result in flux_stateful.start(event_source):
    print(result)  # Each event processed with state threaded
```

---

## Integration with Dual-Track Architecture

### from_table_adapter: Typed State from Alembic

```python
@classmethod
def from_table_adapter(
    cls,
    adapter: TableAdapter[S],
    initial_state: S | None = None,
) -> StateFunctor[S]:
    """
    Create StateFunctor backed by Alembic table via TableAdapter.

    This bridges the dual-track architecture:
    - State type S is an Alembic model (typed, migrated)
    - State persistence uses TableAdapter (DgentProtocol interface)
    - Agent logic remains pure and composable

    Example:
        crystal_state = StateFunctor.from_table_adapter(
            adapter=TableAdapter(Crystal, session_factory),
            initial_state=Crystal(id="default", tags=[]),
        )
        crystal_agent = crystal_state.lift(process_agent)
        flux_crystal = Flux.lift(crystal_agent)
    """
    return cls(
        state_type=adapter.model,
        backend=adapter,
        initial_state=initial_state,
        namespace=adapter.model.__tablename__,
    )
```

---

## The Symbiont Connection

**Symbiont IS StateFunctor.lift_logic with D-gent backend.**

```python
# These are equivalent:
symbiont = Symbiont(logic=chat_logic, memory=dgent_memory)

stateful = StateFunctor(
    state_type=ConversationState,
    backend=dgent_memory,
    initial_state=ConversationState(),
).lift_logic(chat_logic)
```

Symbiont is the **canonical composition pattern**. StateFunctor makes the pattern explicit as a functor.

### Why Both?

| Concept | Purpose |
|---------|---------|
| **StateFunctor** | Formal functor, enables Flux composition, law verification |
| **Symbiont** | Ergonomic pattern, direct usage, established convention |

StateFunctor is the theory. Symbiont is the idiom.

---

## State Threading Invariants

### 1. Load-Before-Invoke

State is **always** loaded before inner agent invocation.

```python
# Wrong: invoke without loading
output = await inner.invoke(input_data)

# Right: load, then invoke with state
state = await self._load_state()
output = await inner.invoke((input_data, state))
```

### 2. Save-After-Complete

State is saved **only after** successful invocation.

```python
# Wrong: save before invoke completes
await self._save_state(new_state)
output = await inner.invoke(...)

# Right: save after successful invoke
output, new_state = await inner.invoke(...)
await self._save_state(new_state)
```

### 3. State Isolation

Each StatefulAgent has isolated state via namespace.

```python
# Different namespaces, isolated state
chat_state = StateFunctor(..., namespace="chat")
memory_state = StateFunctor(..., namespace="memory")
# No interference between chat_state and memory_state
```

---

## Anti-patterns

### 1. State Without Persistence

```python
# BAD: In-memory only, loses state on restart
state_functor = StateFunctor(
    state_type=S,
    backend=MemoryBackend(),  # Volatile!
)

# GOOD: Backed by durable D-gent
state_functor = StateFunctor(
    state_type=S,
    backend=SQLiteBackend("state.db"),
)
```

### 2. Bypassing State Loading

```python
# BAD: Directly access state outside of invoke()
state = await stateful_agent._load_state()
state.value = 42
await stateful_agent._save_state(state)

# GOOD: All state changes through invoke()
await stateful_agent.invoke("set_value_42")
```

### 3. Mutable State in Logic

```python
# BAD: Mutates state in-place
def logic(input: str, state: S) -> tuple[str, S]:
    state.count += 1  # MUTATION!
    return "ok", state

# GOOD: Returns new state
def logic(input: str, state: S) -> tuple[str, S]:
    return "ok", S(count=state.count + 1)
```

---

## See Also

- [README.md](README.md) — S-gent overview
- [composition.md](composition.md) — Flux and D-gent composition patterns
- [laws.md](laws.md) — Functor law proofs
- [../d-gents/symbiont.md](../d-gents/symbiont.md) — The canonical S >> D pattern
- [../d-gents/dual-track.md](../d-gents/dual-track.md) — Dual-track architecture
- [../c-gents/functor-catalog.md](../c-gents/functor-catalog.md) — Functor catalog (§14)

---

*"The functor doesn't change what the agent computes. It changes how state flows through the computation."*
