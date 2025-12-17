---
path: plans/d-gent-dual-track-architecture
status: spec
progress: 35
last_touched: 2025-12-17
touched_by: claude-opus-4
blocking: []
enables:
  - crown-jewels-enlightened (Phase 3+)
  - persistent citizen memory
  - typed Brain crystals
  - Flux(State(agent)) composition
session_notes: |
  2025-12-17: Initial spec exploration
  - Researched existing D-gent architecture (Datum, DgentProtocol, backends)
  - Found existing Alembic setup (system/migrations/)
  - Identified tension between agent-native memory and normative relational data
  - Proposed dual-track architecture with TableAdapter bridge
  2025-12-17: StateFunctor specification added
  - Analyzed bounty: "D-gent protocol → StateMonad functor enables Flux(State(agent))"
  - Found Symbiont pattern already implements StateMonad, but not formalized as functor
  - Specified StateFunctor with lift(), lift_logic(), compose_flux()
  - Integrated with dual-track via StateFunctor.from_table_adapter()
  - Added functor laws verification tests
phase_ledger:
  PLAN: in_progress
  RESEARCH: complete
  DEVELOP: in_progress
  IMPLEMENT: pending
  REFLECT: pending
entropy:
  planned: 0.5
  spent: 0.2
  returned: 0.0
---

# D-gent Dual-Track Architecture

> *"Memory is not monolithic. Agent cognition and application state serve different masters."*

## Purpose

Support both **agent-native memory** (crystals, associations, serendipity) AND **normative relational data** (users, sessions, schemas with migrations) within a unified persistence philosophy.

This refactor emerges from the Crown Jewels implementation, where we need:
- Brain crystals with queryable metadata AND semantic content
- Citizen conversations with foreign keys AND causal chains
- Garden ideas with lifecycle state AND associative connections

---

## The Core Insight

Memory is not monolithic. Two tracks serve different needs:

| Track | Purpose | Schema | Migration | Access Pattern |
|-------|---------|--------|-----------|----------------|
| **Agent Memory** | Cognition, association, serendipity | Schema-free (Datum) | None (append-only) | Lenses, semantic search |
| **Application State** | Consistent app data | Typed (Alembic) | Versioned | SQL, ORM queries |

**The key realization**: Don't force D-gent to support migrations. Instead, create a dual-track architecture where each track excels at what it's designed for, with a bridge functor for unified access.

---

## Current State Analysis

### D-gent Architecture (data-architecture-rewrite)

```
┌─────────────────────────────────────────────────────────────────┐
│                        DgentProtocol                             │
│  put(datum) | get(id) | delete(id) | list() | causal_chain()    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
     ┌────────────────────────┼────────────────────────────────┐
     │                        │                                │
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────────────┐
│ Memory  │  │  JSONL  │  │ SQLite  │  │ Postgres (asyncpg)   │
└─────────┘  └─────────┘  └─────────┘  └──────────────────────┘

Core abstraction: Datum(id, content: bytes, created_at, causal_parent, metadata)
```

**Strengths**:
- Schema-free (bytes + ID + causality)
- Graceful degradation via DgentRouter
- Lens algebra for focused access
- Already supports SQLite and Postgres backends

**Limitations**:
- No typed models for application state
- No migration support (intentionally)
- Metadata is unstructured dict, not queryable

### Existing Alembic Setup

Located at `impl/claude/system/migrations/`:
- `env.py` — Async SQLite support, XDG paths
- `versions/001_self_grow_tables.py` — self.grow persistence

The Alembic infrastructure **already exists** but operates in parallel to D-gent.

---

## Formal Definition

### The Agent Memory Category

Objects: `Datum[namespace]` — typed by namespace, not content schema
Morphisms: `Lens[S, A]` — focusing operations that compose

```python
AGENT_MEMORY = Category(
    objects={"crystals", "associations", "traces", "garden_entries"},
    morphisms=LensAlgebra,
    identity=identity_lens,
    composition=lambda f, g: f >> g  # Lens composition
)
```

### The Application State Category

Objects: `Table[T]` — SQLAlchemy models or raw tables
Morphisms: `Migration` — schema transformations

```python
APP_STATE = Category(
    objects={User, Session, Crystal, CitizenMemory, GardenEntry},
    morphisms=AlembicMigration,
    identity=no_op_migration,
    composition=sequential_migration
)
```

### The Bridge Functor

```python
Bridge: APP_STATE → AGENT_MEMORY
Bridge(Table[T]) = DgentProtocol where content = serialize(T)
```

This functor is **lossy** (schema → bytes loses type info) but enables agent access to application state through familiar patterns.

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMBRANE (Unified Persistence)                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              D-GENT TRACK (Agent Memory)                   │ │
│  │  - Datum abstraction (bytes + causality)                   │ │
│  │  - Projection lattice (Memory → JSONL → SQLite → Postgres) │ │
│  │  - Lens algebra (focused access)                           │ │
│  │  - Semantic/temporal/relational modes (vision.md)          │ │
│  │  - AGENTESE: self.data.*                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           ALEMBIC TRACK (Application State)                │ │
│  │  - Typed models (SQLAlchemy or raw SQL)                    │ │
│  │  - Migration versioning (forward-only in prod)             │ │
│  │  - Foreign keys, indices, constraints                      │ │
│  │  - Query builder (SQL or ORM)                              │ │
│  │  - AGENTESE: self.data.table.*                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               BRIDGE (TableAdapter)                        │ │
│  │  - Lifts Alembic tables → DgentProtocol                    │ │
│  │  - Enables lens composition on typed data                  │ │
│  │  - Bidirectional: table ↔ Datum                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Specification

### TableAdapter: The Bridge Functor

```python
from typing import Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from agents.d.protocol import DgentProtocol
from agents.d.datum import Datum

T = TypeVar("T")

class TableAdapter(DgentProtocol, Generic[T]):
    """
    Lifts an Alembic-managed table into DgentProtocol.

    Enables agent access to application state via the same
    patterns used for agent memory (lenses, causal chains).

    Category-theoretic: This is a functor APP_STATE → AGENT_MEMORY.
    """

    def __init__(
        self,
        model: Type[T],
        session_factory: Callable[[], AsyncSession],
        id_field: str = "id",
        serialize: Callable[[T], bytes] = default_serialize,
        deserialize: Callable[[bytes], T] = default_deserialize,
    ):
        self.model = model
        self.session_factory = session_factory
        self.id_field = id_field
        self.serialize = serialize
        self.deserialize = deserialize

    async def put(self, datum: Datum) -> str:
        """
        Store datum by upserting into the Alembic table.

        The datum.content is deserialized to model instance.
        """
        instance = self.deserialize(datum.content)

        async with self.session_factory() as session:
            # Upsert pattern
            existing = await session.get(self.model, datum.id)
            if existing:
                for key, value in instance.__dict__.items():
                    if not key.startswith("_"):
                        setattr(existing, key, value)
            else:
                session.add(instance)
            await session.commit()

        return datum.id

    async def get(self, id: str) -> Datum | None:
        """
        Retrieve from table, return as Datum.
        """
        async with self.session_factory() as session:
            instance = await session.get(self.model, id)
            if instance is None:
                return None

            return Datum(
                id=getattr(instance, self.id_field),
                content=self.serialize(instance),
                created_at=getattr(instance, "created_at", time.time()),
                causal_parent=getattr(instance, "causal_parent", None),
                metadata={"source": "alembic", "table": self.model.__tablename__},
            )

    async def delete(self, id: str) -> bool:
        """Delete from table."""
        async with self.session_factory() as session:
            instance = await session.get(self.model, id)
            if instance:
                await session.delete(instance)
                await session.commit()
                return True
            return False

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[Datum]:
        """List from table with filters."""
        async with self.session_factory() as session:
            query = select(self.model)

            if prefix:
                query = query.where(
                    getattr(self.model, self.id_field).startswith(prefix)
                )

            if after:
                query = query.where(self.model.created_at > after)

            query = query.order_by(self.model.created_at.desc()).limit(limit)

            result = await session.execute(query)
            instances = result.scalars().all()

            return [
                Datum(
                    id=getattr(inst, self.id_field),
                    content=self.serialize(inst),
                    created_at=getattr(inst, "created_at", time.time()),
                    causal_parent=getattr(inst, "causal_parent", None),
                    metadata={"source": "alembic", "table": self.model.__tablename__},
                )
                for inst in instances
            ]

    async def causal_chain(self, id: str) -> list[Datum]:
        """
        Get causal chain via recursive query.

        Requires causal_parent column in table.
        """
        # Similar to SQLiteBackend.causal_chain but via SQLAlchemy
        ...
```

### AGENTESE Integration

```python
# In protocols/agentese/contexts/self_data.py

class SelfDataContext:
    """
    AGENTESE paths for unified data access.

    self.data.*        → D-gent (agent memory)
    self.data.table.*  → Alembic tables (via TableAdapter)
    """

    def __init__(self, dgent: DgentRouter, adapters: dict[str, TableAdapter]):
        self.dgent = dgent
        self.adapters = adapters

    async def resolve(self, path: str, umwelt: Umwelt) -> Handle:
        parts = path.split(".")

        if parts[0] == "table" and len(parts) >= 2:
            # self.data.table.crystal.get → TableAdapter for Crystal
            table_name = parts[1]
            if table_name in self.adapters:
                return TableHandle(self.adapters[table_name], parts[2:])

        # Default: D-gent
        return DgentHandle(self.dgent, parts)
```

---

## Crown Jewel Examples

### Brain: Hybrid Crystal Storage

```python
# models/brain.py — Alembic-managed
class Crystal(Base):
    __tablename__ = "brain_crystals"

    id: Mapped[str] = mapped_column(primary_key=True)
    content_hash: Mapped[str] = mapped_column(index=True)
    summary: Mapped[str] = mapped_column()
    tags: Mapped[list[str]] = mapped_column(JSON)
    access_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)

    # Link to D-gent for semantic content
    datum_id: Mapped[str | None] = mapped_column()

# Usage in Brain handler
async def capture_crystal(content: str, tags: list[str]):
    # 1. Store semantic content in D-gent (for associations, serendipity)
    datum = Datum(
        id=uuid4().hex,
        content=content.encode(),
        created_at=time.time(),
        metadata={"type": "crystal", "tags": tags},
    )
    await dgent.put(datum)

    # 2. Store queryable metadata in Alembic table
    crystal = Crystal(
        id=uuid4().hex,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
        summary=content[:200],
        tags=tags,
        datum_id=datum.id,
    )
    session.add(crystal)
    await session.commit()

    return crystal.id
```

### Town: Citizen Memory with Causality

```python
# models/town.py — Alembic-managed
class CitizenConversation(Base):
    __tablename__ = "citizen_conversations"

    id: Mapped[str] = mapped_column(primary_key=True)
    citizen_name: Mapped[str] = mapped_column(index=True)
    topic: Mapped[str | None] = mapped_column()
    turn_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)

    # Head of D-gent causal chain for conversation turns
    datum_chain_head: Mapped[str | None] = mapped_column()

class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    id: Mapped[str] = mapped_column(primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("citizen_conversations.id"))
    role: Mapped[str] = mapped_column()  # "user" | "citizen"
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)

    # Causal link for D-gent access
    causal_parent: Mapped[str | None] = mapped_column()

# Citizen memory persists across sessions
async def add_turn(conversation_id: str, role: str, content: str):
    conversation = await session.get(CitizenConversation, conversation_id)

    turn = ConversationTurn(
        id=uuid4().hex,
        conversation_id=conversation_id,
        role=role,
        content=content,
        causal_parent=conversation.datum_chain_head,
    )
    session.add(turn)

    # Update chain head
    conversation.datum_chain_head = turn.id
    conversation.turn_count += 1

    await session.commit()
```

### Gardener: Idea Lifecycle

```python
# models/gardener.py — Alembic-managed
class GardenIdea(Base):
    __tablename__ = "garden_ideas"

    id: Mapped[str] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column()
    lifecycle: Mapped[str] = mapped_column(default="SEED")  # SEED|SAPLING|TREE|FLOWER|COMPOST
    confidence: Mapped[float] = mapped_column(default=0.3)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("gardener_sessions.id"))
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    last_nurtured: Mapped[datetime | None] = mapped_column()

    # D-gent link for associative connections
    datum_id: Mapped[str | None] = mapped_column()
```

---

## Migration Strategy

### Phase 1: TableAdapter (Bridge Functor)

1. Implement `TableAdapter` in `agents/d/adapters/table_adapter.py`
2. Add AGENTESE path `self.data.table.*`
3. Create migrations for Crown Jewel tables:
   - `002_brain_crystals.py`
   - `003_citizen_memory.py`
   - `004_garden_ideas.py`

### Phase 2: Integration

1. Update Brain handler to use hybrid storage
2. Update Town handler for persistent citizen memory
3. Update Gardener to store ideas in Alembic table

### Phase 3: Validation

1. Verify lens composition works on TableAdapter
2. Test graceful degradation (Postgres → SQLite)
3. Validate causal_chain queries across both tracks

### Phase 4: StateFunctor (Bounty: Flux(State(agent)))

1. Implement `StateFunctor` in `agents/d/state_functor.py`
   - `lift()`: Agent[A, B] → StatefulAgent[S, A, B]
   - `lift_logic()`: Pure (I, S) → (O, S) → Agent[I, O]
   - `compose_flux()`: StateFunctor → (Agent → FluxAgent)
2. Implement `StatefulAgent` wrapper class
3. Add `from_table_adapter()` for dual-track integration
4. Write functor law verification tests:
   - Identity: `lift(Id) ≅ Id`
   - Composition: `lift(f >> g) ≅ lift(f) >> lift(g)`
5. Deprecate old `state_monad.py` stub
6. Document in `spec/c-gents/functor-catalog.md`

### Phase 5: Functor Registry Integration

1. Register `StateFunctor` in `FunctorRegistry`
2. Enable automatic law verification via `FunctorRegistry.verify_all()`
3. Add to CLI: `kg functor verify state`
4. Update `docs/skills/flux-agent.md` with StateFunctor patterns

---

## Laws That Must Hold

### Agent Memory Laws (Preserved)
1. **Append-only**: `put` is idempotent (same content → same result)
2. **Causality**: Every `Datum` knows its `causal_parent`
3. **Lens composition**: `(f >> g) >> h = f >> (g >> h)`

### Application State Laws (New)
1. **Migration idempotence**: Applying migration twice = applying once
2. **Forward-only in production**: Downgrades only for development
3. **Schema evolution**: New columns nullable or with defaults

### Bridge Laws (New)
1. **Round-trip**: `TableAdapter.get(TableAdapter.put(datum).id) ≅ datum`
2. **Source tagging**: `Datum.metadata["source"] == "alembic"` for bridged data
3. **Isolation**: Agent memory changes don't affect Alembic tables (unless explicit)

---

## StateFunctor: Enabling Flux(State(agent)) Composition

> *"The Symbiont IS the State Monad. StateFunctor makes this explicit and composable."*

### Background: The Bounty Idea

From the bounty board:
> D-gent protocol → StateMonad functor would enable `Flux(State(agent))` composition

**Analysis**: This capability **already exists** via the Symbiont pattern, but is not formalized as a composable functor. The StateFunctor specification makes it explicit.

### The Symbiont Connection

The **Symbiont pattern** (`spec/d-gents/symbiont.md`) implements the State Monad Transformer:

```haskell
-- Haskell equivalent
StateT s m a = s -> m (a, s)
```

```python
# Current kgents implementation
Symbiont: LogicFunction[I, S] × DataAgent[S] → Agent[I, O]

# Where:
LogicFunction[I, S] = Callable[[I, S], tuple[O, S]]  # Pure: (input, state) → (output, new_state)
DataAgent[S] = DgentProtocol  # Side effects: load/save state
```

**Current usage** (works today):
```python
symbiont = Symbiont(logic_fn, dgent_memory)
flux_symbiont = Flux.lift(symbiont)  # Flux(State(agent)) achieved manually
```

### StateFunctor: The Formal Specification

```python
# impl/claude/agents/d/state_functor.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from agents.bootstrap import Agent
from agents.d.protocol import DgentProtocol
from agents.flux import Flux, FluxAgent

S = TypeVar("S")  # State type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


@dataclass
class StateFunctor(Generic[S]):
    """
    State Monad as a first-class functor.

    Lifts agents into stateful computation where state is:
    1. Loaded before each invocation
    2. Threaded through the logic
    3. Saved after each invocation

    Category-theoretic:
        StateFunctor[S]: 𝒞_Agent → 𝒞_Agent
        Where objects are Agent[A, B] and morphisms are natural transformations

    Functor Laws:
        1. Identity: StateFunctor.lift(Id) ≅ Id (with trivial state)
        2. Composition: StateFunctor.lift(f >> g) ≅ StateFunctor.lift(f) >> StateFunctor.lift(g)

    Relationship to Symbiont:
        StateFunctor is the generalized form of Symbiont.
        Symbiont = StateFunctor[S].lift(logic_as_agent) with DgentProtocol backend
    """

    state_type: type[S]
    backend: DgentProtocol
    initial_state: S | None = None
    namespace: str = "state"

    # =========================================================================
    # Core Functor Operations
    # =========================================================================

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
        # Wrap logic as an agent
        logic_agent = _LogicAgent(logic)
        return self.lift(logic_agent)

    # =========================================================================
    # Functor Composition
    # =========================================================================

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

    # =========================================================================
    # Integration with Dual-Track Architecture
    # =========================================================================

    @classmethod
    def from_table_adapter(
        cls,
        adapter: "TableAdapter[S]",
        initial_state: S | None = None,
    ) -> StateFunctor[S]:
        """
        Create StateFunctor backed by Alembic table via TableAdapter.

        This bridges the dual-track architecture:
        - State type S is an Alembic model (typed, migrated)
        - State persistence uses TableAdapter (DgentProtocol interface)
        - Agent logic remains pure and composable

        Example:
            # State is Crystal model from Alembic
            crystal_state = StateFunctor.from_table_adapter(
                adapter=TableAdapter(Crystal, session_factory),
                initial_state=Crystal(id="default", tags=[]),
            )

            # Lift agent to use Crystal state
            crystal_agent = crystal_state.lift(process_agent)

            # Compose with Flux for streaming
            flux_crystal = Flux.lift(crystal_agent)
        """
        return cls(
            state_type=adapter.model,
            backend=adapter,
            initial_state=initial_state,
            namespace=adapter.model.__tablename__,
        )


@dataclass
class StatefulAgent(Agent[A, B], Generic[S, A, B]):
    """
    An agent with explicit state threading.

    This is the result of StateFunctor.lift(agent).

    State lifecycle per invocation:
    1. Load: state = await backend.load(namespace)
    2. Invoke: output = await inner.invoke(input, state)  # Extended input
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

        # 2. Invoke inner agent
        # Try extended input first, fall back to simple input
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

    async def _load_state(self) -> S:
        """Load state from backend."""
        datum = await self.backend.get(f"{self.namespace}:state")
        if datum is None:
            return self.initial_state or self.state_type()

        import json
        return self.state_type(**json.loads(datum.content.decode()))

    async def _save_state(self, state: S) -> None:
        """Save state to backend."""
        import json
        import time
        from agents.d.datum import Datum

        content = json.dumps(state.__dict__ if hasattr(state, '__dict__') else state)
        datum = Datum(
            id=f"{self.namespace}:state",
            content=content.encode(),
            created_at=time.time(),
            causal_parent=None,
            metadata={"type": "state", "namespace": self.namespace},
        )
        await self.backend.put(datum)

    @property
    def current_state(self) -> S | None:
        """
        Get current state (sync, cached).

        For async state access, use load_state() directly.
        """
        # This would need caching implementation
        return self.initial_state


class _LogicAgent(Agent[tuple[A, S], tuple[B, S]], Generic[A, B, S]):
    """Wrapper to turn pure logic function into Agent."""

    def __init__(self, logic: Callable[[A, S], tuple[B, S]]):
        self.logic = logic

    async def invoke(self, input_data: tuple[A, S]) -> tuple[B, S]:
        a, s = input_data
        return self.logic(a, s)
```

### Usage Patterns

#### Pattern 1: Basic State Threading

```python
from agents.d.state_functor import StateFunctor
from agents.d.backends import SQLiteBackend

# Create state functor with SQLite backend
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

# Use it
response = await chat_agent.invoke("Hello!")  # State automatically threaded
```

#### Pattern 2: Flux(State(agent)) Composition

```python
from agents.d.state_functor import StateFunctor
from agents.flux import Flux

# Create composed functor
state_functor = StateFunctor(
    state_type=ProcessorState,
    backend=dgent_backend,
)
FluxState = StateFunctor.compose_flux(state_functor)

# Lift agent through composed functor
flux_stateful = FluxState(process_agent)

# Process stream with state threading
async for result in flux_stateful.start(event_source):
    print(result)  # Each event processed with state threaded
```

#### Pattern 3: Dual-Track Integration (Typed State from Alembic)

```python
from agents.d.state_functor import StateFunctor
from agents.d.adapters.table_adapter import TableAdapter
from models.brain import Crystal

# Create StateFunctor backed by Alembic table
crystal_adapter = TableAdapter(Crystal, session_factory)
crystal_state = StateFunctor.from_table_adapter(
    adapter=crystal_adapter,
    initial_state=Crystal(id="session_crystal", tags=[], access_count=0),
)

# Lift agent - state is now typed Crystal model
crystal_agent = crystal_state.lift(analysis_agent)

# Compose with Flux for streaming analysis
flux_crystal = Flux.lift(crystal_agent)

# Each stream event:
# 1. Loads Crystal from Alembic table
# 2. Passes to analysis_agent with typed state
# 3. Saves updated Crystal back to table
# 4. Yields analysis result
```

### Functor Laws Verification

```python
# impl/claude/agents/d/_tests/test_state_functor.py

import pytest
from agents.d.state_functor import StateFunctor
from agents.bootstrap import Id

class TestStateFunctorLaws:
    """Verify StateFunctor satisfies functor laws."""

    @pytest.fixture
    def state_functor(self, memory_backend):
        return StateFunctor(
            state_type=dict,
            backend=memory_backend,
            initial_state={},
        )

    async def test_identity_law(self, state_functor):
        """
        Identity Law: StateFunctor.lift(Id) ≅ Id

        Lifting identity should behave like identity (modulo state).
        """
        lifted_id = state_functor.lift(Id)

        input_val = "test"
        result = await lifted_id.invoke(input_val)

        # Output should equal input (identity behavior)
        assert result == input_val

    async def test_composition_law(self, state_functor):
        """
        Composition Law: lift(f >> g) ≅ lift(f) >> lift(g)

        Lifting a composition should equal composing lifted agents.
        """
        # Two simple agents
        double = lambda x: x * 2
        add_one = lambda x: x + 1

        # Composition 1: lift(f >> g)
        composed_then_lifted = state_functor.lift(
            Agent.from_function(lambda x: add_one(double(x)))
        )

        # Composition 2: lift(f) >> lift(g)
        lifted_double = state_functor.lift(Agent.from_function(double))
        lifted_add = state_functor.lift(Agent.from_function(add_one))
        lifted_then_composed = lifted_double >> lifted_add

        # Both should produce same result
        input_val = 5
        result1 = await composed_then_lifted.invoke(input_val)
        result2 = await lifted_then_composed.invoke(input_val)

        assert result1 == result2 == 11  # (5 * 2) + 1

    async def test_flux_composition_preserves_state(self, state_functor):
        """
        Flux(State(agent)) should thread state through stream events.
        """
        counter_logic = lambda x, s: (s["count"], {**s, "count": s.get("count", 0) + 1})
        FluxState = StateFunctor.compose_flux(state_functor)

        counter_agent = state_functor.lift_logic(counter_logic)
        flux_counter = Flux.lift(counter_agent)

        # Process 3 events
        results = []
        async for result in flux_counter.start(async_iter(["a", "b", "c"])):
            results.append(result)

        # State should thread: 0, 1, 2
        assert results == [0, 1, 2]
```

### Integration with Existing Architecture

| Component | Relationship to StateFunctor |
|-----------|------------------------------|
| **Symbiont** | StateFunctor generalizes Symbiont; Symbiont = StateFunctor.lift_logic |
| **D-gent Protocol** | StateFunctor uses DgentProtocol for state persistence |
| **TableAdapter** | StateFunctor.from_table_adapter enables typed Alembic state |
| **Flux** | StateFunctor.compose_flux creates Flux ∘ State functor |
| **PolyAgent** | StatefulAgent can be further lifted to polynomial via state positions |

### File Structure (Updated)

```
impl/claude/agents/d/
├── ...existing files...
├── state_functor.py       # NEW: StateFunctor implementation
├── adapters/
│   ├── __init__.py
│   └── table_adapter.py   # Bridge functor (existing plan)
└── _tests/
    └── test_state_functor.py  # NEW: Functor law tests
```

### Migration from Deprecated StateMonadFunctor

The existing `impl/claude/agents/d/state_monad.py` is a deprecated stub:

```python
# OLD (deprecated)
@dataclass
class StateMonadFunctor(Generic[S]):
    """DEPRECATED: Use DgentRouter + MemoryBackend instead."""
    initial: S
    def run(self, f: Any) -> tuple[Any, S]: ...

# NEW (StateFunctor)
@dataclass
class StateFunctor(Generic[S]):
    """First-class functor with composition support."""
    state_type: type[S]
    backend: DgentProtocol
    def lift(self, agent: Agent[A, B]) -> StatefulAgent[S, A, B]: ...
    @staticmethod
    def compose_flux(...) -> Callable[...]: ...
```

**Migration path**:
1. Replace `StateMonadFunctor` with `StateFunctor`
2. Use `StateFunctor.lift_logic` for pure logic functions
3. Use `StateFunctor.compose_flux` for streaming stateful agents

---

## Anti-patterns

- **Schema in Datum content**: Don't reinvent Alembic inside D-gent
- **ORM for agent memory**: Don't force typed models on associative cognition
- **Mixing tracks without bridge**: Don't access Alembic tables directly from agents
- **Eager migration**: Don't migrate everything to Alembic; only app state needs it

---

## File Structure

```
impl/claude/
├── agents/d/
│   ├── ...existing D-gent files...
│   ├── state_functor.py        # NEW: StateFunctor (Phase 4)
│   ├── state_monad.py          # DEPRECATED: Old stub (to be removed)
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── table_adapter.py    # Bridge functor (Phase 1)
│   └── _tests/
│       ├── ...existing tests...
│       └── test_state_functor.py  # NEW: Functor law tests
├── system/
│   └── migrations/
│       └── versions/
│           ├── 001_self_grow_tables.py  # Existing
│           ├── 002_brain_crystals.py    # NEW (Phase 1)
│           ├── 003_citizen_memory.py    # NEW (Phase 1)
│           └── 004_garden_ideas.py      # NEW (Phase 1)
├── models/
│   ├── __init__.py
│   ├── base.py       # SQLAlchemy Base
│   ├── brain.py      # Crystal, Tag
│   ├── town.py       # Citizen, Conversation, Turn
│   └── gardener.py   # Idea, Plot, Session
└── protocols/agentese/contexts/
    └── self_data.py  # Updated with table.* paths
```

---

## Open Questions for Kent

1. **Does the dual-track framing resonate?** Or should there be tighter integration?

2. **Which Crown Jewels need Alembic tables first?**
   - Brain crystals (for queryable tags, access_count)?
   - Citizen memory (for persistent conversations)?
   - Garden ideas (already partially in SQLite)?

3. **AGENTESE path naming**: Is `self.data.table.*` right, or prefer:
   - `self.db.*`
   - `self.state.*`
   - `self.data.typed.*`

4. **SQLAlchemy vs raw SQL**: The current Alembic setup uses raw SQL. Should we:
   - Continue with raw SQL (simpler, portable)?
   - Add SQLAlchemy ORM (richer queries, relationships)?
   - Hybrid (raw SQL migrations, ORM for queries)?

5. **Sync vs async**: Current D-gent is async. SQLAlchemy async requires `asyncpg` for Postgres. Is this acceptable complexity?

---

## Related

- `spec/d-gents/README.md` — D-gent philosophy
- `spec/d-gents/architecture.md` — Current architecture
- `spec/d-gents/vision.md` — Memory as Landscape (Noosphere)
- `plans/crown-jewels-enlightened.md` — Crown Jewel requirements
- `docs/skills/crown-jewel-patterns.md` — Implementation patterns

---

*"Agent cognition needs serendipity. Application state needs consistency. The dual-track architecture gives each what it needs."*
