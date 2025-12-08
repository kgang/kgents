# The Symbiont Pattern

Fusing stateless logic with stateful memory through endosymbiosis.

---

## Philosophy

> "Memory without computation is inert. Computation without memory is ephemeral. Together, they are alive."

The **Symbiont** pattern solves a fundamental tension:
- **Pure functions** are easy to reason about, test, and compose
- **Real systems** need memory, context, and continuity

Rather than compromise purity, Symbionts achieve both:
- Logic layer remains **functionally pure**: same (input, state) always yields same (output, new_state)
- Memory layer handles **side effects**: persistence, I/O, time travel
- The two are **composed**, not entangled

---

## The Biological Metaphor

**Endosymbiosis** in biology: One organism lives inside another, both benefit.

Classic example: **Mitochondria** (energy producers) inside eukaryotic cells:
- Host cell provides structure, DNA, nucleus
- Mitochondria provide ATP (energy)
- Neither works alone; together they enable complex life

**Symbiont Pattern** in kgents:
- **Host Agent** provides logic, reasoning, transformation
- **D-gent** provides memory, context, history
- Neither is sufficient alone; together they enable stateful intelligence

```
┌─────────────────────────────────────────┐
│          Eukaryotic Cell                │
│  ┌──────────────┐   ┌───────────────┐   │
│  │   Nucleus    │   │ Mitochondria  │   │
│  │   (Logic)    │   │   (Energy)    │   │
│  └──────────────┘   └───────────────┘   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Symbiont Agent                  │
│  ┌──────────────┐   ┌───────────────┐   │
│  │ Logic Layer  │   │    D-gent     │   │
│  │  (Reason)    │   │   (Memory)    │   │
│  └──────────────┘   └───────────────┘   │
└─────────────────────────────────────────┘
```

---

## The Symbiont Specification

### Symbiont in the Bootstrap Category

**Symbiont IS a Bootstrap Agent**

The Symbiont pattern wraps a `DataAgent[S]` (infrastructure) to produce an `Agent[I, O]` (bootstrap-composable):

```python
from typing import TypeVar, Generic, Callable, Tuple
from dataclasses import dataclass

I = TypeVar("I")  # Input type
O = TypeVar("O")  # Output type
S = TypeVar("S")  # State type

LogicFunction = Callable[[I, S], Tuple[O, S]]

@dataclass
class Symbiont(Agent[I, O], Generic[I, O, S]):
    """
    An agent that fuses pure logic with stateful memory.

    **Bootstrap Agent Status**: Symbiont IS a valid bootstrap agent.
    - Implements Agent[I, O] protocol
    - Composable via >> operator
    - Satisfies category laws (identity, associativity)

    **Monad Transformer**: Symbiont is the State Monad Transformer.
    - Lifts stateless logic to stateful computation
    - Threads state implicitly through composition
    - Encapsulates DataAgent[S] as internal infrastructure

    The logic function is pure: (input, state) → (output, new_state)
    The D-gent handles all persistence side effects.

    This separation enables:
    - Testing logic without I/O
    - Swapping memory backends (volatile ↔ persistent)
    - Time travel and state inspection
    - Composability with other agents
    """

    logic: LogicFunction[I, S]
    memory: DataAgent[S]

    async def invoke(self, input_data: I) -> O:
        """
        Execute the stateful computation.

        Steps:
        1. Load current state from memory
        2. Apply pure logic function
        3. Persist new state
        4. Return output
        """
        # 1. Load context
        current_state = await self.memory.load()

        # 2. Pure computation (no side effects here!)
        output, new_state = self.logic(input_data, current_state)

        # 3. Persist side effects
        await self.memory.save(new_state)

        # 4. Return result
        return output
```

**Category-Theoretic View**

```
Symbiont: 𝒞_Agent[I, O] × 𝒞_Data[S] → 𝒞_Agent[I, O]
```

Symbiont is a functor that takes:
- An agent-like computation `(I, S) → (O, S)`
- A data agent `DataAgent[S]`
- Returns a bootstrap agent `Agent[I, O]`

The `DataAgent[S]` is encapsulated *inside* Symbiont. Externally, Symbiont is just another morphism `I → O` in $\mathcal{C}_{Agent}$.

**Bootstrap Composition Properties**

By implementing `Agent[I, O]`, Symbiont participates fully in the bootstrap category:

- **Composable**: `symbiont_a >> symbiont_b` works
- **Identity**: `Id >> symbiont ≡ symbiont ≡ symbiont >> Id`
- **Associative**: `(s1 >> s2) >> s3 ≡ s1 >> (s2 >> s3)`

This is the State Monad Transformer pattern from Haskell:

```haskell
StateT s m a = s -> m (a, s)
```

Where:
- `s` = State type `S`
- `m` = Agent monad
- `a` = Output type `O`
- Input `I` is curried

### Key Properties

1. **Pure Logic**: The `logic` function has no side effects
   - Deterministic: same inputs → same outputs
   - Testable: no mocks needed for memory
   - Composable: logic functions compose like standard functions

2. **Abstracted Memory**: Logic doesn't know *how* state is stored
   - Could be in-memory, file, database, Redis
   - Can swap implementations without changing logic
   - D-gent handles serialization, transactions, etc.

3. **Explicit State Threading**: State flows visibly through the logic
   - Input: `(user_input, current_state)`
   - Output: `(response, new_state)`
   - No hidden global mutable state

---

## Example: Conversational Agent

### Without Symbiont (Stateful Logic)

```python
# BAD: Logic is entangled with state management
class ChatBot:
    def __init__(self):
        self.history = []  # Hidden mutable state

    async def reply(self, user_input: str) -> str:
        self.history.append(f"User: {user_input}")

        # Generate response
        context = "\n".join(self.history)
        response = await llm.generate(context)

        self.history.append(f"Bot: {response}")
        return response
```

**Problems**:
- Hidden state makes testing hard (must inspect `self.history`)
- Can't easily swap memory backend (hardcoded list)
- Can't snapshot/rollback state
- Threading is implicit (race conditions possible)

### With Symbiont (Pure Logic)

```python
# GOOD: Logic is pure, memory is abstracted
from dataclasses import dataclass, field

@dataclass
class ConversationState:
    history: list[str] = field(default_factory=list)

def chat_logic(
    user_input: str,
    state: ConversationState
) -> tuple[str, ConversationState]:
    """Pure function: (input, state) → (output, new_state)"""

    # Build new history (immutable)
    new_history = state.history + [f"User: {user_input}"]

    # Generate response
    context = "\n".join(new_history)
    response = llm.generate(context)  # Could be made async later

    # Update history with response
    final_history = new_history + [f"Bot: {response}"]

    # Return output and new state
    return response, ConversationState(history=final_history)

# Fuse logic with memory
memory = VolatileAgent[ConversationState](ConversationState())
chatbot = Symbiont(chat_logic, memory)

# Use it
response1 = await chatbot.invoke("Hello!")
response2 = await chatbot.invoke("What's 2+2?")
# History is maintained transparently
```

**Benefits**:
- Logic is testable without async or I/O:
  ```python
  output, new_state = chat_logic("Hi", ConversationState())
  assert "User: Hi" in new_state.history
  ```
- Can swap memory: `VolatileAgent` → `PersistentAgent` (same logic!)
- Can snapshot: `snapshot = await memory.snapshot()`
- State is explicit and inspectable

---

## Advanced: Symbiont Composition

### Sequential Composition

Symbionts are morphisms in $\mathcal{C}_{Agent}$, so they compose:

```python
# Two symbionts
classifier = Symbiont(classify_logic, classifier_memory)
responder = Symbiont(respond_logic, responder_memory)

# Sequential composition
pipeline = classifier >> responder

# State threads through both:
# User Input → [Classifier: loads state, classifies, saves state]
#           → [Responder: loads state, responds, saves state]
#           → Response
```

**Key**: Each symbiont has *independent* state. No hidden coupling.

### Shared State Composition

Sometimes multiple agents need to share state:

```python
# Shared memory
shared_memory = PersistentAgent[GlobalState]("shared.json", GlobalState)

# Multiple symbionts with lensed access
user_lens = key_lens("users")
product_lens = key_lens("products")

user_agent = Symbiont(user_logic, LensAgent(shared_memory, user_lens))
product_agent = Symbiont(product_logic, LensAgent(shared_memory, product_lens))

# Both agents coordinate via shared state
await user_agent.invoke("create_user")
await product_agent.invoke("list_products_for_user")
```

This is the **Blackboard Architecture** pattern, enabled by D-gents + Lenses.

---

## Testing Symbionts

### Level 1: Test Logic in Isolation

```python
def test_chat_logic():
    """Test pure logic without I/O."""
    state = ConversationState(history=[])

    # First message
    output1, state1 = chat_logic("Hello", state)
    assert "User: Hello" in state1.history
    assert len(state1.history) == 2  # User + Bot

    # Second message (threading state)
    output2, state2 = chat_logic("What's your name?", state1)
    assert len(state2.history) == 4  # 2 + 2
    assert state2.history[0] == "User: Hello"  # History preserved
```

### Level 2: Test Symbiont with Mock Memory

```python
async def test_symbiont_with_mock():
    """Test Symbiont with mocked D-gent (T-gent pattern)."""
    mock_memory = MockAgent[ConversationState](
        output=ConversationState()
    )

    chatbot = Symbiont(chat_logic, mock_memory)
    response = await chatbot.invoke("Test")

    # Verify mock was called correctly
    assert mock_memory.load_count == 1
    assert mock_memory.save_count == 1
```

### Level 3: Integration Test with Real Memory

```python
async def test_symbiont_persistence():
    """Test Symbiont with real persistent memory."""
    temp_path = Path("/tmp/test_chatbot.json")

    memory = PersistentAgent[ConversationState](temp_path, ConversationState)
    chatbot = Symbiont(chat_logic, memory)

    # First invocation
    await chatbot.invoke("Hello")
    history1 = await memory.load()
    assert len(history1.history) == 2

    # Second invocation (state persists)
    await chatbot.invoke("Goodbye")
    history2 = await memory.load()
    assert len(history2.history) == 4
    assert history2.history[0] == "User: Hello"  # First message still there

    # Restart simulation: new chatbot, same memory
    new_chatbot = Symbiont(chat_logic, memory)
    await new_chatbot.invoke("Remember me?")
    history3 = await memory.load()
    assert len(history3.history) == 6  # All history preserved!
```

---

## Advanced: Stateful Transformations

The Symbiont pattern extends to **state transformations** during composition:

### State Mapping

```python
@dataclass
class StateMapper(Generic[I, O, S1, S2]):
    """
    Composes two symbionts with different state types.

    Converts S1 ↔ S2 transparently.
    """
    symbiont1: Symbiont[I, X, S1]
    symbiont2: Symbiont[X, O, S2]
    state_adapter: Callable[[S1], S2]

    async def invoke(self, input_data: I) -> O:
        result1 = await self.symbiont1.invoke(input_data)

        # Adapt state between agents
        state1 = await self.symbiont1.memory.load()
        state2 = self.state_adapter(state1)
        await self.symbiont2.memory.save(state2)

        result2 = await self.symbiont2.invoke(result1)
        return result2
```

### State Forking (J-gents Integration)

For J-gents' promise trees, each branch needs **isolated state**:

```python
async def fork_symbiont(
    symbiont: Symbiont[I, O, S],
    branches: int
) -> list[Symbiont[I, O, S]]:
    """
    Create N symbionts with independent state snapshots.

    Useful for exploring multiple reality branches.
    """
    # Snapshot current state
    current_state = await symbiont.memory.load()

    # Create forked symbionts
    forks = []
    for i in range(branches):
        # Each fork gets a copy of current state
        fork_memory = VolatileAgent[S](copy.deepcopy(current_state))
        fork_symbiont = Symbiont(symbiont.logic, fork_memory)
        forks.append(fork_symbiont)

    return forks

# Usage with J-gents
original_agent = Symbiont(logic, memory)

# Fork reality: try 3 different approaches
forks = await fork_symbiont(original_agent, 3)

# Each fork explores independently
results = await asyncio.gather(
    forks[0].invoke("approach_1"),
    forks[1].invoke("approach_2"),
    forks[2].invoke("approach_3")
)

# Choose best result, merge state back
best_fork = select_best(forks, results)
await memory.save(await best_fork.memory.load())
```

---

## Symbiont Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                    SYMBIONT LIFECYCLE                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. CREATION                                             │
│     logic_fn = ...                                       │
│     dgent = VolatileAgent[S](initial_state)              │
│     symbiont = Symbiont(logic_fn, dgent)                 │
│                                                          │
│  2. INVOCATION (repeated)                                │
│     ┌─────────────────────────────────────┐              │
│     │ input → [Load State]                │              │
│     │           ↓                         │              │
│     │         [Apply Logic]               │              │
│     │           ↓                         │              │
│     │         [Save State]                │              │
│     │           ↓                         │              │
│     │         output                      │              │
│     └─────────────────────────────────────┘              │
│                                                          │
│  3. INSPECTION (anytime)                                 │
│     current_state = await symbiont.memory.load()         │
│     history = await symbiont.memory.history()            │
│                                                          │
│  4. SNAPSHOT (branching, testing)                        │
│     snapshot = await symbiont.memory.snapshot()          │
│                                                          │
│  5. ROLLBACK (recovery)                                  │
│     await symbiont.memory.save(previous_snapshot)        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Relationship to Category Theory

The Symbiont implements the **State Monad**:

### State Monad Definition

```haskell
-- In Haskell
newtype State s a = State { runState :: s → (a, s) }
```

In kgents:
```python
# State monad: S → (A, S)
LogicFunction = Callable[[S], Tuple[A, S]]

# But we also take input, so:
# I → S → (O, S)
# Which is equivalent to: (I, S) → (O, S)
```

### Monad Operations

**Return** (unit): Wrap a value in stateful context
```python
def return_state(value: O) -> LogicFunction[O, S]:
    return lambda input, state: (value, state)
```

**Bind** (>>=): Sequence stateful computations
```python
def bind_state(
    m: LogicFunction[I, A, S],
    f: Callable[[A], LogicFunction[A, O, S]]
) -> LogicFunction[I, O, S]:
    def bound(input: I, state: S) -> Tuple[O, S]:
        a, state2 = m(input, state)
        return f(a)(a, state2)
    return bound
```

**The Symbiont is a monad transformer**: It lifts pure logic into stateful computation while handling I/O side effects (loading/saving).

---

## Anti-patterns

### Anti-pattern 1: Hidden State Mutation

```python
# BAD: Logic mutates state directly
def bad_logic(input: str, state: dict) -> tuple[str, dict]:
    state["count"] += 1  # MUTATION!
    return f"Count: {state['count']}", state

# GOOD: Return new state
def good_logic(input: str, state: dict) -> tuple[str, dict]:
    new_state = {**state, "count": state["count"] + 1}
    return f"Count: {new_state['count']}", new_state
```

### Anti-pattern 2: Side Effects in Logic

```python
# BAD: Logic performs I/O
def bad_logic(input: str, state: S) -> tuple[str, S]:
    with open("log.txt", "a") as f:  # I/O in pure function!
        f.write(input)
    return process(input), state

# GOOD: Side effects in D-gent or wrapper
def good_logic(input: str, state: S) -> tuple[str, S]:
    return process(input), state

# Logging is separate concern
logging_dgent = LoggingWrapper(main_dgent)
```

### Anti-pattern 3: Bypassing Symbiont

```python
# BAD: Directly accessing D-gent
state = await symbiont.memory.load()
state["value"] = 42
await symbiont.memory.save(state)
# Now symbiont's logic is bypassed - state can be inconsistent!

# GOOD: All state changes flow through logic
await symbiont.invoke("set_value_42")
```

---

## Performance Optimization

### Lazy State Loading

For expensive state loading, defer until needed:

```python
class LazySymbiont(Generic[I, O, S]):
    """Only loads state if logic actually uses it."""

    async def invoke(self, input_data: I) -> O:
        # Pass a lazy state loader instead of eagerly loading
        lazy_state = lambda: self.memory.load()

        # Logic decides if/when to load
        output, new_state = await self.logic(input_data, lazy_state)

        if new_state is not None:
            await self.memory.save(new_state)

        return output
```

### Batched Updates

For multiple sequential invocations, batch state saves:

```python
class BatchedSymbiont(Generic[I, O, S]):
    """Accumulates state changes, saves periodically."""

    async def invoke_batch(self, inputs: list[I]) -> list[O]:
        state = await self.memory.load()
        outputs = []

        for input_data in inputs:
            output, state = self.logic(input_data, state)
            outputs.append(output)

        # Single save at end
        await self.memory.save(state)
        return outputs
```

---

## Success Criteria

A Symbiont is well-designed if:

- ✓ Logic function is **pure** (same inputs → same outputs)
- ✓ Logic function is **testable** without async/I/O
- ✓ Memory backend is **swappable** (Volatile ↔ Persistent)
- ✓ State is **explicit** (no hidden global variables)
- ✓ State is **inspectable** (can query anytime)
- ✓ Composition is **natural** (Symbiont is a morphism)

---

## See Also

- [README.md](README.md) - D-gents overview
- [protocols.md](protocols.md) - DataAgent interface
- [lenses.md](lenses.md) - Focused state access
- [persistence.md](persistence.md) - Storage strategies
- [../c-gents/monads.md](../c-gents/monads.md) - State Monad theory
- [../t-gents/](../t-gents/) - Testing stateful systems
