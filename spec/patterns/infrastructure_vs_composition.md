# Infrastructure vs Composition

A fundamental architectural distinction in kgents.

---

## The Distinction

Every agent genus in kgents operates at two abstraction levels:

```
┌────────────────────────────────────────┐
│  COMPOSITION LAYER                     │  ← User-facing
│  - Bootstrap agents (Agent[I, O])      │  ← Composable via >>
│  - Category: 𝒞_Agent                   │  ← Obeys category laws
│  Examples: Symbiont, DialecticAgent    │
├────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER                  │  ← Internal
│  - Primitives & protocols              │  ← Not Agent[I, O]
│  - Category: 𝒞_Effect (varies)         │  ← Domain-specific
│  Examples: DataAgent, Contradict       │
└────────────────────────────────────────┘
```

**Key Insight**: Infrastructure provides **effects** (state, errors, dialectics). Composition provides **agents** (composable morphisms).

---

## Why Separate?

### 1. Composability

**Infrastructure** often has incompatible signatures:
- `DataAgent[S]`: `load() → S`, `save(S) → ()`
- `Contradict`: `(A, B) → Tension | None`
- `Parser`: `str → AST`

These **cannot compose** via `>>` because they don't implement `Agent[I, O]`.

**Composition wrappers** unify them:
- `Symbiont[I, O, S]`: `Agent[I, O]` ✓
- `DialecticAgent[T, A, S]`: `Agent[Pair, S]` ✓
- `ForgeAgent[Intent, Agent]`: `Agent[str, Agent]` ✓

Now they **can compose**: `symbiont >> dialectic >> forge`

---

### 2. Testability

**Infrastructure** can be tested in isolation:
```python
# Test DataAgent without Agent protocol
dgent = VolatileAgent[int](initial=0)
await dgent.save(42)
assert await dgent.load() == 42
```

**Composition** can be tested with mocked infrastructure:
```python
# Test Symbiont with mock memory
mock_memory = MockDataAgent[S](output=initial_state)
symbiont = Symbiont(logic, mock_memory)
result = await symbiont.invoke(input)
assert mock_memory.save_count == 1
```

---

### 3. Substitutability

**Infrastructure** can be swapped without changing composition:

```python
# Same composition logic, different infrastructure
volatile_chatbot = Symbiont(chat_logic, VolatileAgent(state))
persistent_chatbot = Symbiont(chat_logic, PersistentAgent("state.json"))

# Both are Agent[str, str], both compose the same way
pipeline1 = validator >> volatile_chatbot >> formatter
pipeline2 = validator >> persistent_chatbot >> formatter
```

This is the **Dependency Inversion Principle**: composition depends on infrastructure *abstraction*, not *implementation*.

---

### 4. Clarity

The distinction makes **effects explicit**:

**Without stratification**:
```python
class ChatBot(Agent[str, str]):
    def __init__(self):
        self.history = []  # What is this? State? Cache? Log?

    async def invoke(self, msg: str) -> str:
        # Hidden: what effects happen here?
        ...
```

**With stratification**:
```python
chatbot = Symbiont[str, str, ConversationState](
    logic=chat_logic,           # Pure (no effects)
    memory=VolatileAgent(state) # Effect: stateful memory
)
# Clear: This agent has state as an effect
```

---

## The Pattern Across Genera

| Genus | Infrastructure | Composition | Effect |
|-------|----------------|-------------|--------|
| **D-gents** | `DataAgent[S]` | `Symbiont[I, O, S]` | State |
| **H-gents** | `Contradict`, `Sublate` | `HegelAgent`, `ContinuousDialectic`, `BackgroundDialectic`, `FullIntrospection` | Dialectics |
| **F-gents** (hypothesis) | `Parser`, `CodeGen` | `ForgeAgent[Intent, Agent]` | Compilation |
| **Bootstrap** | `Contradict`, `Sublate`, `Fix` | All bootstrap agents | Meta-operations |

**Universal**: Infrastructure ∉ 𝒞_Agent, Composition ∈ 𝒞_Agent

---

## Identifying the Layers

### Infrastructure Checklist

A component is **infrastructure** if:
- [ ] Does NOT implement `Agent[I, O]` protocol
- [ ] Has domain-specific methods (not `invoke`)
- [ ] Manages effects (state, errors, I/O, etc.)
- [ ] Forms its own category ($\mathcal{C}_{Data}$, $\mathcal{C}_{Dialectic}$, etc.)
- [ ] Not directly composable via `>>`

**Examples**: `DataAgent[S]`, `Contradict`, `Sublate`, `Parser`, `FitnessFunction`

---

### Composition Checklist

A component is **composition** if:
- [x] Implements `Agent[I, O]` protocol
- [x] Has `invoke(input: I) -> O` method
- [x] Composable via `>>` operator
- [x] Obeys category laws (identity, associativity)
- [x] Wraps infrastructure to provide effects

**Examples**: `Symbiont[I, O, S]`, `DialecticAgent`, `ForgeAgent`, all bootstrap agents

---

## The Monad Transformer Bridge

The **monad transformer** is what bridges infrastructure and composition:

```
Infrastructure + Monad Transformer = Composition

DataAgent[S] + StateT = Symbiont[I, O, S] : Agent[I, O]
Contradict + ContT = DialecticAgent : Agent[Pair, Synthesis]
Parser + CompileT = ForgeAgent : Agent[str, Agent]
```

**Monad transformers lift** infrastructure effects into the agent category.

See [monad_transformers.md](./monad_transformers.md) for details.

---

## Anti-patterns

### Anti-pattern 1: Infrastructure as Agents

```python
# BAD: DataAgent pretends to be Agent
class DataAgentWrapper(Agent[None, S]):
    """Wraps DataAgent as Agent[None, S]"""
    def __init__(self, dgent: DataAgent[S]):
        self.dgent = dgent

    async def invoke(self, _: None) -> S:
        return await self.dgent.load()

# Problems:
# - Signature is weird (None input?)
# - No clear transformation (just loads state)
# - Can't compose meaningfully (None >> ?)
```

**Fix**: Use infrastructure as-is, wrap with Symbiont for composition.

---

### Anti-pattern 2: Hidden Infrastructure

```python
# BAD: Agent with hidden infrastructure
class ChatBot(Agent[str, str]):
    def __init__(self):
        self._db = Database()  # Hidden infrastructure!

    async def invoke(self, msg: str) -> str:
        # User has no idea state is involved
        state = self._db.load()
        ...
        self._db.save(new_state)
        return response

# Problems:
# - Can't test without real database
# - Can't swap persistence strategy
# - Can't inspect state externally
```

**Fix**: Extract `DataAgent`, use `Symbiont` wrapper.

---

### Anti-pattern 3: Composition Without Infrastructure

```python
# BAD: Agent implements effects directly
class StatefulAgent(Agent[I, O]):
    def __init__(self):
        self.state = {}  # Direct state management

    async def invoke(self, input: I) -> O:
        # Logic mixed with state mutation
        self.state["count"] += 1
        ...

# Problems:
# - State is un-swappable
# - Logic is un-testable without state setup
# - No history, snapshots, or time-travel
```

**Fix**: Use `DataAgent` for state, `Symbiont` for logic+state.

---

### Anti-pattern 4: Infrastructure Leakage

```python
# BAD: Composition exposes infrastructure
class Symbiont(Agent[I, O], Generic[I, O, S]):
    logic: LogicFunction[I, S]
    memory: DataAgent[S]

    async def invoke(self, input: I) -> O:
        ...

    # DON'T DO THIS:
    def get_memory(self) -> DataAgent[S]:
        return self.memory  # Infrastructure leak!

# Problems:
# - Users can bypass logic layer
# - Breaks encapsulation
# - State can become inconsistent
```

**Fix**: Keep infrastructure private. Only expose agent methods.

---

## Design Principles

### Principle 1: Infrastructure is Swappable

Any infrastructure implementation should be replaceable without changing composition:

```python
# Same composition, different infrastructure
chatbot_v1 = Symbiont(logic, VolatileAgent(state))
chatbot_v2 = Symbiont(logic, PersistentAgent("state.json"))
chatbot_v3 = Symbiont(logic, RedisAgent("redis://..."))

# All have identical Agent[str, str] interface
```

**Test**: Can you swap infrastructure without changing composition code?

---

### Principle 2: Infrastructure is Testable

Infrastructure should be testable without the agent protocol:

```python
# Test DataAgent directly
dgent = PersistentAgent[MyState]("/tmp/test.json", MyState)
await dgent.save(MyState(value=42))

# Verify persistence
dgent2 = PersistentAgent[MyState]("/tmp/test.json", MyState)
state = await dgent2.load()
assert state.value == 42
```

**Test**: Can you test infrastructure without invoking an agent?

---

### Principle 3: Composition is Encapsulated

Composition should hide infrastructure details:

```python
# User sees Agent[I, O], not DataAgent
chatbot: Agent[str, str] = Symbiont(logic, memory)

# User composes agents, not infrastructure
pipeline = chatbot >> summarizer >> logger

# Infrastructure is internal implementation detail
```

**Test**: Can users compose agents without knowing infrastructure?

---

### Principle 4: Effects are Explicit

The presence of effects should be visible in types:

```python
# Clear: This is a stateful agent
Symbiont[str, str, ConversationState]

# Clear: This agent can fail
Agent[Input, Result[Output, Error]]

# Clear: This agent iterates
Fix[Agent[State, State]]
```

**Test**: Can you tell what effects an agent has from its type?

---

## Relationship to Bootstrap

The infrastructure/composition distinction clarifies **bootstrap primitive status**:

| Bootstrap Primitive | Layer | Category |
|---------------------|-------|----------|
| Id, Compose | Composition | 𝒞_Agent |
| Judge, Ground | Infrastructure | 𝒞_Judgment, 𝒞_Facts |
| Contradict, Sublate | Infrastructure | 𝒞_Dialectic |
| Fix | Composition | 𝒞_Agent (wraps iteration infrastructure) |

**Insight**: Bootstrap primitives exist at **both** layers:
- **Infrastructure primitives**: Judge, Ground, Contradict, Sublate
- **Composition primitives**: Id, Compose, Fix (wraps recursion infrastructure)

This resolves the question: "Are Contradict/Sublate bootstrap agents?"
- **No**, they are bootstrap **primitives** at the infrastructure level
- **But** they enable bootstrap agents (DialecticAgent) at the composition level

---

## Validation Questions

For any agent genus, ask:

1. **What is the infrastructure?**
   - What primitives/protocols are NOT agents?
   - What effects do they manage?

2. **What is the composition?**
   - What agents wrap the infrastructure?
   - Do they implement `Agent[I, O]`?

3. **Is infrastructure encapsulated?**
   - Can users compose agents without touching infrastructure?
   - Is infrastructure swappable?

4. **Is composition clean?**
   - Does it obey category laws?
   - Can it compose via `>>`?

5. **What monad transformer bridges them?**
   - State, Error, Continuation, etc.
   - How does it lift effects into agents?

---

## See Also

- [monad_transformers.md](./monad_transformers.md) - Detailed monad transformer patterns
- [../bootstrap.md](../bootstrap.md) - Bootstrap primitives
- [../d-gents/README.md](../d-gents/README.md) - Reference implementation (D-gents)
- [../h-gents/index.md](../h-gents/index.md) - H-gents stratification
- [../agents/composition.md](../agents/composition.md) - Category theory foundations

---

## Summary

**Infrastructure vs Composition** is the fundamental architectural pattern in kgents:

| Aspect | Infrastructure | Composition |
|--------|----------------|-------------|
| **Interface** | System-specific | Agent[I, O] |
| **Purpose** | Manage effects | Enable composition |
| **Category** | Effect-specific | 𝒞_Agent |
| **Composable** | No (via >>) | Yes (via >>) |
| **Testable** | Yes (standalone) | Yes (with mocks) |
| **User-facing** | No (internal) | Yes (external) |

**The Bridge**: Monad transformers lift infrastructure effects into composable agents.

**The Benefit**: Clean separation of concerns, testability, substitutability, clarity.
