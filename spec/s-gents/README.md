# S-gents: State Agents

> *"The Symbiont IS the State Monad. S-gent makes this explicit."*

---

## Purpose

S-gent provides **state threading** for agent computation—the categorical State Monad lifted to the agent domain.

| Concept | Traditional | S-gent |
|---------|-------------|--------|
| State Monad | `s -> (a, s)` | `Agent[A, B]` with S threading |
| StateT | `s -> m (a, s)` | `StatefulAgent[S, A, B]` |
| Composition | `>>=` (bind) | `>>` (agent composition) |

---

## The Core Insight

**State is orthogonal to persistence.**

- **D-gent**: WHERE state lives (memory, file, database)
- **S-gent**: HOW state threads through computation

The Symbiont pattern is `S >> D`—state threading backed by persistence.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE S-GENT INSIGHT                        │
│                                                              │
│  Traditional view:   Agent + Database = Stateful Agent       │
│                      (couples logic to persistence)          │
│                                                              │
│  S-gent view:        Agent ──StateFunctor──▶ StatefulAgent   │
│                              ↓                               │
│                      StatefulAgent + D-gent = Symbiont       │
│                      (orthogonal concerns, clean composition)│
└─────────────────────────────────────────────────────────────┘
```

---

## Theoretical Foundation

### The State Monad

In Haskell:
```haskell
newtype State s a = State { runState :: s -> (a, s) }
```

In kgents:
```python
# State monad: (Input, State) → (Output, NewState)
LogicFunction = Callable[[I, S], tuple[O, S]]

# StateFunctor lifts this to Agent[I, O] with S threading
```

### StateFunctor as Functor

```
StateFunctor[S]: C_Agent → C_Agent

Where:
- Objects: Agent[A, B]
- Morphisms: Natural transformations
- S: The state type
```

StateFunctor lifts agents into stateful computation where state is:
1. Loaded before each invocation
2. Threaded through the computation
3. Saved after each invocation

---

## Contents

| Document | Description |
|----------|-------------|
| [state-functor.md](state-functor.md) | The StateFunctor specification |
| [composition.md](composition.md) | Flux and D-gent composition |
| [laws.md](laws.md) | Functor laws and verification |

---

## Relationship to Other Agents

| Agent | Relationship |
|-------|--------------|
| **D-gent** | Persistence backend for StateFunctor |
| **Flux** | Composes as `Flux ∘ State` for streaming stateful agents |
| **PolyAgent** | StatefulAgent can be lifted to polynomial positions |
| **K-gent** | Soul state threads through K-gent interactions |

---

## The Symbiont: Canonical S >> D

The Symbiont pattern (`spec/d-gents/symbiont.md`) IS `StateFunctor.lift_logic` with a D-gent backend:

```python
# These are equivalent:
symbiont = Symbiont(logic_fn, dgent_memory)

stateful = StateFunctor(
    state_type=S,
    backend=dgent_memory,
).lift_logic(logic_fn)
```

Symbiont is the **canonical composition** of S-gent (state threading) and D-gent (persistence).

---

## Quick Start

### Pattern 1: Basic State Threading

```python
from agents.d.state_functor import StateFunctor
from agents.d.backends import SQLiteBackend

state_functor = StateFunctor(
    state_type=ConversationState,
    backend=SQLiteBackend("conversations.db"),
    initial_state=ConversationState(history=[]),
)

def chat_logic(message: str, state: ConversationState) -> tuple[str, ConversationState]:
    new_history = state.history + [f"User: {message}"]
    response = generate_response(new_history)
    return response, ConversationState(history=new_history + [f"Bot: {response}"])

chat_agent = state_functor.lift_logic(chat_logic)
response = await chat_agent.invoke("Hello!")  # State threaded automatically
```

### Pattern 2: Flux(State(agent))

```python
FluxState = StateFunctor.compose_flux(state_functor)
flux_stateful = FluxState(process_agent)

async for result in flux_stateful.start(event_source):
    print(result)  # Each event processed with state threaded
```

### Pattern 3: Typed State from Alembic

```python
# Use TableAdapter for typed state backed by Alembic
crystal_state = StateFunctor.from_table_adapter(
    adapter=TableAdapter(Crystal, session_factory),
    initial_state=Crystal(id="session_crystal", tags=[]),
)
crystal_agent = crystal_state.lift(analysis_agent)
```

---

## AGENTESE Paths

S-gent does not expose direct AGENTESE paths. State threading is implicit in agent composition. Access state through:

- `self.data.*` (D-gent) for persisted state
- Agent invocation for threaded state

---

## Design Principles

### Separation of Concerns

| Concern | Owner |
|---------|-------|
| State threading | S-gent (StateFunctor) |
| Persistence | D-gent (DgentProtocol) |
| Pure logic | User's logic function |

### Functor Laws

StateFunctor is a legitimate functor:

| Law | Statement | Verification |
|-----|-----------|--------------|
| Identity | `StateFunctor.lift(Id) ≅ Id` | test_state_identity_law |
| Composition | `lift(f >> g) ≅ lift(f) >> lift(g)` | test_state_composition_law |

### Composition Hierarchy

```
Flux ∘ State ∘ D-gent

Level 3: Flux        — Continuous event processing
Level 2: State       — State threading (S-gent)
Level 1: D-gent      — Persistence substrate
Level 0: Pure logic  — (I, S) → (O, S)
```

---

## Anti-patterns

- **State without persistence**: Use D-gent backend, not in-memory only
- **Bypassing state loading**: Always go through StatefulAgent.invoke()
- **Mutable state in logic**: Logic function must be pure `(A, S) → (B, S)`
- **Coupling logic to persistence**: Let S-gent handle threading, D-gent handle storage

---

## Implementation Location

```
impl/claude/agents/d/
├── state_functor.py     # StateFunctor implementation
├── symbiont.py          # Symbiont (S >> D composition)
└── _tests/
    └── test_state_functor.py  # Functor law verification
```

---

## See Also

- [state-functor.md](state-functor.md) — Full StateFunctor specification
- [composition.md](composition.md) — Composition patterns with Flux and D-gent
- [laws.md](laws.md) — Functor laws and verification approach
- [../d-gents/symbiont.md](../d-gents/symbiont.md) — The canonical S >> D pattern
- [../d-gents/dual-track.md](../d-gents/dual-track.md) — Dual-track persistence architecture
- [../c-gents/functor-catalog.md](../c-gents/functor-catalog.md) — Functor catalog (§14: State)

---

*"State threads through computation like a river through landscape. D-gent is the riverbed. S-gent is the flow."*
