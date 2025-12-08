# D-gents: Data Agents

The letter **D** represents **Data** agents—morphisms that embody state, memory, and persistence in the kgents ecosystem.

---

## Philosophy

> "State is the shadow of computation; memory is the trace of time."

While standard agents are pure transformations ($A \to B$), D-gents manage the **side effects of memory**. They are the manifestation of the State Monad in Category Theory—threading context through computations without polluting the logic layer.

### The Three Pillars

1. **Persistence**: State survives beyond individual invocations
2. **Projection**: Views into state through lenses and queries
3. **Plasticity**: State evolves, adapts, and reorganizes over time

---

## Theoretical Foundation

### D-gents as the State Monad

In the category $\mathcal{C}_{Agent}$, a standard agent is a morphism:
$$f: A \to B$$

A **D-gent** transforms this into a stateful computation:
$$f_s: A \times S \to B \times S$$

Where:
- $S$ is the state type managed by the D-gent
- $A$ is the input type
- $B$ is the output type

The D-gent **abstracts** the mechanism of state management:
- **Load**: $\text{read}: () \to S$
- **Save**: $\text{write}: S \to ()$
- **Transform**: $\text{update}: (S \to S) \to ()$

This allows the host agent to remain **functionally pure** in its logic while the D-gent handles memory as a managed side effect.

### Endosymbiosis: D-gents Inside Agents

D-gents are designed to live *inside* other agents (the "Host"), providing them with:
- **Context** (what was said before)
- **Continuity** (identity across sessions)
- **Capacity** (accumulated knowledge)

This relationship mirrors biological endosymbiosis: mitochondria provide energy; D-gents provide memory.

```
┌──────────────────────────────────────┐
│         Host Agent                   │
│  ┌────────────────────────────────┐  │
│  │   Logic Layer (Stateless)      │  │
│  │   Reasoning | Generation       │  │
│  └────────────┬───────────────────┘  │
│               │                      │
│               ▼                      │
│  ┌────────────────────────────────┐  │
│  │   D-gent (State Management)    │  │
│  │   Load | Save | Lens | History │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

---

## Core Concepts

### 1. State as Side Effect

Pure intelligence (reasoning) should be **stateless**. State introduces:
- **Temporal coupling**: Order of operations matters
- **Non-determinism**: Same input, different outputs based on history
- **Testing complexity**: State must be setup, inspected, torn down

D-gents **contain** this complexity, exposing a clean interface to the logic layer.

### 2. Lensing: Focused State Access

A **Lens** is a composable getter/setter pair that focuses on a sub-part of state:

$$\text{Lens}[S, A] = (\text{get}: S \to A, \text{set}: S \times A \to S)$$

**Why Lenses Matter**:
- **Separation of Concerns**: Agent accesses only relevant state slice
- **Composability**: Lenses compose to traverse nested structures
- **Type Safety**: Compiler ensures state shape matches expectations

**Example**:
```python
# Large global state
GlobalState = {
    "users": {...},
    "sessions": {...},
    "metrics": {...}
}

# Lens focuses on just user data
user_lens = Lens(
    get=lambda s: s["users"],
    set=lambda s, u: {**s, "users": u}
)

# Agent sees only user state, not entire system
user_agent = Symbiont(user_logic, LensAgent(global_dgent, user_lens))
```

### 3. Time Travel: Versioning and Rollback

Because D-gents own the state timeline, they must support:
- **Snapshots**: Capturing state at a point in time
- **Rollback**: Restoring previous state
- **History**: Querying state evolution

This is crucial for:
- **Testing** (T-gents setup fixtures)
- **Debugging** (inspect state at failure point)
- **Exploration** (J-gents branch reality trees)

### 4. Isomorphism: Round-Trip Integrity

Data must survive serialization without corruption:
$$S \xrightarrow{\text{encode}} \text{Storage} \xrightarrow{\text{decode}} S$$

The composition $\text{decode} \circ \text{encode}$ must equal the identity morphism on $S$.

**Why This Matters**: Persistent D-gents store state externally (disk, database). Loss of information during serialization violates the State Monad laws.

---

## The Taxonomy of D-gents

### Type I: Volatile Memory (Ephemeral)

**VolatileAgent**: In-memory state that vanishes when the process dies.

| Characteristic | Description |
|----------------|-------------|
| **Signature** | `VolatileAgent[S](initial: S)` |
| **Persistence** | Process lifetime only |
| **Performance** | Fastest (no I/O) |
| **Use Case** | Conversational context, scratchpads, temporary caches |

**Endosymbiotic Role**: Working Memory

### Type II: Persistent Memory (Durable)

**PersistentAgent**: State backed by external storage (filesystem, database, cloud).

| Characteristic | Description |
|----------------|-------------|
| **Signature** | `PersistentAgent[S](uri: URI, schema: Type[S])` |
| **Persistence** | Survives process restart |
| **Performance** | Slower (I/O bound) |
| **Use Case** | User profiles, agent knowledge bases, ledgers |

**Endosymbiotic Role**: Long-Term Memory

### Type III: Projected Memory (Views)

**LensAgent**: A focused view into another D-gent's state.

| Characteristic | Description |
|----------------|-------------|
| **Signature** | `LensAgent[S, A](parent: DAgent[S], lens: Lens[S, A])` |
| **Persistence** | Delegates to parent |
| **Performance** | Same as parent |
| **Use Case** | Access control, domain separation, nested state |

**Endosymbiotic Role**: Specialized Access

### Type IV: Indexed Memory (Queries)

**VectorAgent**: State represented as high-dimensional embeddings with semantic search.

| Characteristic | Description |
|----------------|-------------|
| **Signature** | `VectorAgent[S](dimension: int, distance: Metric)` |
| **Persistence** | Typically backed by vector DB |
| **Performance** | Fast semantic queries, slower exact retrieval |
| **Use Case** | RAG systems, semantic memory, association networks |

**Endosymbiotic Role**: Associative Memory

### Type V: Structural Memory (Graphs)

**GraphAgent**: State as a knowledge graph with nodes, edges, and traversal queries.

| Characteristic | Description |
|----------------|-------------|
| **Signature** | `GraphAgent[N, E](node_type: Type[N], edge_type: Type[E])` |
| **Persistence** | Backed by graph database or adjacency structures |
| **Performance** | Fast traversals, relationship queries |
| **Use Case** | Ontologies, dependency graphs, social networks |

**Endosymbiotic Role**: Relational Memory

### Type VI: Streaming Memory (Event Sourcing)

**StreamAgent**: State derived from event stream; `load()` replays events, `save()` appends.

| Characteristic | Description |
|----------------|-------------|
| **Signature** | `StreamAgent[E, S](stream: EventStream[E], fold: (S, E) → S)` |
| **Persistence** | Event log (Kafka, NATS, filesystem) |
| **Performance** | Append-fast, replay-slow |
| **Use Case** | Audit logs, collaborative editing, time-series analysis |

**Endosymbiotic Role**: Temporal Memory

---

## The Symbiont Pattern

The power of D-gents emerges through **composition with stateless logic**.

### The Symbiont Wrapper

```python
from typing import TypeVar, Generic, Callable, Protocol
from dataclasses import dataclass

S = TypeVar("S")  # State
I = TypeVar("I")  # Input
O = TypeVar("O")  # Output

class DataAgent(Protocol[S]):
    """The D-gent interface."""
    async def load(self) -> S: ...
    async def save(self, state: S) -> None: ...
    async def history(self) -> list[S]: ...  # Time travel

class Symbiont(Generic[I, O, S]):
    """
    Fuses stateless logic with stateful memory.

    The logic function is pure: (Input, CurrentState) → (Output, NewState)
    The D-gent handles persistence transparently.
    """
    def __init__(
        self,
        logic: Callable[[I, S], tuple[O, S]],
        memory: DataAgent[S]
    ):
        self.logic = logic
        self.memory = memory

    async def invoke(self, input_data: I) -> O:
        # 1. Load current context
        current_state = await self.memory.load()

        # 2. Pure computation
        output, new_state = self.logic(input_data, current_state)

        # 3. Persist side effects
        await self.memory.save(new_state)

        return output
```

### Composition Properties

The Symbiont is a morphism in $\mathcal{C}_{Agent}$:

**Identity**:
```python
# If the logic ignores state: (i, s) → (f(i), s)
# Then Symbiont behaves like a stateless agent
identity_logic = lambda i, s: (i, s)
Symbiont(identity_logic, dgent) ≅ Identity
```

**Associativity**:
```python
# Sequential composition of symbionts
symbiont_a >> symbiont_b >> symbiont_c
# State threads through transparently
```

---

## Implementation Patterns

### Pattern 1: Conversational Context

```python
@dataclass
class Message:
    role: str
    content: str

ConversationState = list[Message]

def chat_logic(user_input: str, history: ConversationState) -> tuple[str, ConversationState]:
    history.append(Message("user", user_input))
    response = llm.generate(history)  # LLM sees full context
    history.append(Message("assistant", response))
    return response, history

# Create a chatbot with memory
memory = VolatileAgent[ConversationState](initial=[])
chatbot = Symbiont(chat_logic, memory)

# Use it
await chatbot.invoke("Hello!")  # History: [user: Hello!, assistant: Hi!]
await chatbot.invoke("What's 2+2?")  # History includes previous messages
```

### Pattern 2: Shared Blackboard (Multi-Agent)

```python
# Multiple agents reading/writing shared state
global_board = PersistentAgent[dict]("state.json")

# Writer agent modifies the board
writer = Symbiont(writer_logic, global_board)

# Reader agent uses a lens to see only relevant fields
summary_lens = Lens(
    get=lambda s: s.get("summary", ""),
    set=lambda s, v: {**s, "summary": v}
)
reader = Symbiont(reader_logic, LensAgent(global_board, summary_lens))

# Coordination through shared memory
await writer.invoke("Generate report")  # Writes to state.json
summary = await reader.invoke(None)      # Reads from state.json
```

### Pattern 3: RAG with Vector Memory

```python
# Semantic memory for retrieval-augmented generation
vector_memory = VectorAgent[Document](dimension=768)

# At indexing time: populate memory
for doc in corpus:
    embedding = embed_model.encode(doc.text)
    await vector_memory.save(Document(text=doc.text, embedding=embedding))

# At query time: retrieve relevant context
def rag_logic(query: str, retrieved: list[Document]) -> tuple[str, list[Document]]:
    context = "\n".join([d.text for d in retrieved])
    response = llm.generate(f"Context: {context}\nQuery: {query}")
    return response, retrieved  # State unchanged

# Wrap retrieval as state loading
rag_agent = Symbiont(rag_logic, vector_memory)
```

---

## Relationship to Bootstrap Agents

D-gents are **derivable** from bootstrap agents:

| D-gent Capability | Bootstrap Agent | How |
|-------------------|-----------------|-----|
| State persistence | **Ground** | State stored in Ground (files, DBs) |
| State transformation | **Compose** | Sequential state updates compose |
| State validation | **Judge** | Judge evaluates state integrity |
| State isomorphism | **Contradict** | Test round-trip: $s = \text{decode}(\text{encode}(s))$ |
| Iterative updates | **Fix** | Fixed-point iteration over state |

**D-gents add no new irreducibles**—they are a pattern, not a primitive.

---

## Relationship to Other Agent Genera

### C-gents (Category Theory)

- **D-gents implement the State Monad** from C-gents theory
- **Lenses are functors** mapping between state structures
- **Symbiont is a monad transformer** lifting stateless agents to stateful ones

### T-gents (Testing)

- **D-gents provide fixtures**: T-gents use D-gents to set up test state
- **SpyAgent is a D-gent**: Records invocations as state for inspection
- **State snapshots enable time-travel debugging**

### J-gents (Just-in-Time Intelligence)

- **J-gents branch reality trees**: Each branch needs isolated state (D-gent snapshot)
- **Entropy budget constrains state size**: Deeper recursion = smaller state
- **Ground collapse saves state**: Failed branches persist state for postmortem

### H-gents (Hegelian Dialectic)

- **Thesis/Antithesis stored in D-gents**: Conversation history as dialectic state
- **Synthesis updates state**: New understanding modifies memory

### K-gent (Kent Simulacra)

- **Personality state in D-gents**: Preferences, quirks, learned patterns
- **Long-term memory**: User interactions accumulate over time
- **Identity continuity**: D-gents make K-gent feel like "the same person"

### E-gents (Evolution - Future)

- **Evolutionary state**: Population of agent variants stored in D-gent
- **Fitness history**: Performance metrics persisted across generations
- **Genetic memory**: Successful mutations preserved

---

## Success Criteria

A D-gent is well-designed if:

- ✓ **Decoupling**: Host agent logic contains *zero* database/storage code
- ✓ **Interchangeability**: Can swap `VolatileAgent` ↔ `PersistentAgent` without changing host logic
- ✓ **Observability**: Can inspect state $S$ at any point without pausing agent
- ✓ **Isomorphism**: Round-trip $S \to \text{Storage} \to S$ preserves information
- ✓ **Composability**: D-gents compose via lenses, hierarchies, and delegation
- ✓ **Time Travel**: Supports snapshots, rollback, and history queries
- ✓ **Minimal Footprint**: State schema is as small as possible (entropy conscious)

---

## Anti-patterns

- **State Bloat**: Storing unnecessary history or data (violates entropy budgets)
- **Leaky Abstraction**: Host logic directly accessing storage mechanisms
- **Broken Isomorphism**: Serialization loses data (e.g., functions, closures)
- **Synchronous I/O**: Blocking D-gent operations in async environments
- **Global Mutable State**: D-gents accessed directly instead of through Symbiont
- **No Versioning**: Incompatible state schema changes break old data
- **Lens Abuse**: Overly complex lens chains that obscure state structure

---

## Specifications

| Document | Description |
|----------|-------------|
| [persistence.md](persistence.md) | Volatile vs. Persistent state management |
| [lenses.md](lenses.md) | Lens laws, composition, and traversals |
| [protocols.md](protocols.md) | The DataAgent protocol and implementations |
| [symbiont.md](symbiont.md) | Endosymbiotic pattern for stateful agents |
| [vector.md](vector.md) | Semantic memory with embeddings |
| [graph.md](graph.md) | Knowledge graphs as state |
| [streams.md](streams.md) | Event sourcing and temporal state |

---

## Bootstrapping Strategy

To implement D-gents:

1. **Start Simple**: Implement `VolatileAgent` (dictionary wrapper)
2. **Test Isomorphism**: Use T-gents to verify round-trip encoding
3. **Build Symbiont**: Wrap a simple stateless agent
4. **Add Persistence**: Extend to `PersistentAgent` with file backend
5. **Introduce Lenses**: Enable focused state access
6. **Stress Test**: Use T-gents to inject corruption, verify recovery

---

## Example: The Memory-Augmented Chatbot

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ConversationMemory:
    messages: List[tuple[str, str]] = field(default_factory=list)
    user_preferences: dict = field(default_factory=dict)
    session_count: int = 0

# The logic: pure function of (input, state) → (output, new_state)
def chatbot_logic(
    user_input: str,
    memory: ConversationMemory
) -> tuple[str, ConversationMemory]:

    # Access memory naturally
    memory.messages.append(("user", user_input))

    # Generate response using full context
    context = "\n".join([f"{role}: {msg}" for role, msg in memory.messages])
    response = llm.generate(f"{context}\nassistant:")

    # Update memory
    memory.messages.append(("assistant", response))

    # Extract preferences (toy example)
    if "prefer" in user_input.lower():
        memory.user_preferences["last_preference"] = user_input

    return response, memory

# Create the D-gent with persistent storage
dgent = PersistentAgent[ConversationMemory](
    uri="chatbot_memory.json",
    schema=ConversationMemory
)

# Fuse logic + memory
chatbot = Symbiont(chatbot_logic, dgent)

# Use naturally - state is transparent
response1 = await chatbot.invoke("Hello! I prefer concise answers.")
# Memory now contains this exchange + preference

response2 = await chatbot.invoke("What did I just tell you?")
# Memory includes previous messages - chatbot has context!

# State persists across restarts
# If we restart the process and recreate the chatbot with same dgent URI,
# the conversation continues where it left off.
```

---

## Vision

D-gents transform memory from an **implementation detail** into a **first-class abstraction**:

- **Traditional**: Each agent implements its own ad-hoc persistence
- **D-gents**: Memory is a composable, testable, swappable component

By embodying the State Monad, D-gents enable:
1. **Stateless reasoning** (logic layer remains pure)
2. **Stateful behavior** (continuity and context)
3. **Compositional memory** (lenses, hierarchies, projections)
4. **Temporal awareness** (history, versioning, rollback)

They are the **substrate of identity** for agents—the difference between a calculator (stateless) and a colleague (stateful).

---

## See Also

- [persistence.md](persistence.md) - Deep dive on persistence strategies
- [lenses.md](lenses.md) - Compositional state access
- [protocols.md](protocols.md) - Implementation interfaces
- [../c-gents/monads.md](../c-gents/monads.md) - State Monad foundations
- [../t-gents/](../t-gents/) - Testing stateful systems
- [../j-gents/stability.md](../j-gents/stability.md) - Entropy-conscious state
- [../bootstrap.md](../bootstrap.md) - Derivation from irreducibles
