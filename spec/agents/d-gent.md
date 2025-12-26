# D-gent: The Data Agent

> *"The cortex is singular. Memory is global. Context is local."*

**Status**: Canonical | **Layer**: 0 (Persistence) | **Impl**: `impl/claude/agents/d/`

---

## Purpose

D-gent owns all persistence for kgents. It is **Layer 0** of the Metaphysical Fullstack—the foundation upon which services build. D-gent is infrastructure, not a Crown Jewel.

---

## Core Abstractions

### Datum: The Atomic Unit

Schema-free bytes with identity and causal lineage.

```python
@dataclass(frozen=True)
class Datum:
    id: str                      # UUID or content-addressed hash
    content: bytes               # Schema-free payload
    created_at: float            # Unix timestamp
    causal_parent: str | None    # Enables lineage tracing
    metadata: dict[str, str]     # Optional tags
```

**Key Design Decisions**:
- **Schema-free**: Interpretation happens at read time (lenses), not write time
- **Content-addressed option**: `Datum.create(content, content_addressed=True)` → SHA-256 ID
- **Causal chain**: `datum.derive(new_content)` → new datum with `causal_parent` set

### DgentProtocol: Five Methods

```python
class DgentProtocol(Protocol):
    async def put(self, datum: Datum) -> str: ...      # Store, return ID
    async def get(self, id: str) -> Datum | None: ...  # Retrieve by ID
    async def delete(self, id: str) -> bool: ...       # Remove, return success
    async def list(self, prefix: str | None = None, after: float | None = None, limit: int = 100) -> list[Datum]: ...
    async def causal_chain(self, id: str) -> list[Datum]: ...  # Trace ancestry
```

**That's it.** Five methods. All backends implement this.

---

## Backend Lattice (Projection Tiers)

```
Tier 0: Memory     → Ephemeral, fastest (~1μs)
Tier 1: JSONL      → Simple file, append-only (~1ms)
Tier 2: SQLite     → Local database, concurrent reads (~5ms)
Tier 3: Postgres   → Production database, ACID (~10ms)
```

### DgentRouter: Automatic Selection

```python
router = DgentRouter(namespace="brain", preferred=Backend.SQLITE)
await router.put(datum)  # Routes to best available backend
```

**Graceful Degradation**: If preferred unavailable, falls back through the lattice.

**Environment Override**: `KGENTS_DGENT_BACKEND=POSTGRES` forces specific backend.

---

## XDG Compliance

D-gent backends (SQLite, JSONL) use XDG-compliant paths internally:

| Backend | Default Path | Env Variable |
|---------|--------------|--------------|
| SQLite | `~/.kgents/data/{namespace}.db` | `KGENTS_DATA_ROOT` |
| JSONL | `~/.kgents/data/{namespace}.jsonl` | `KGENTS_DATA_ROOT` |
| Postgres | *(connection URL)* | `KGENTS_DATABASE_URL` |

**Note**: For user-friendliness, kgents uses `~/.kgents` as the default data root instead of `~/.local/share/kgents`. This can be overridden with `KGENTS_DATA_ROOT`.

**For higher-level file operations** (uploads, exports, backups), use the unified `StorageProvider`:

```python
from services.storage import get_storage_provider

provider = get_storage_provider()
uploads_dir = provider.paths.uploads  # ~/.kgents/uploads
```

See: `spec/protocols/storage-unified.md` for the complete storage architecture.

---

## Symbiont: State Threading

Fuses stateless logic with stateful memory.

```python
Symbiont[I, O, S] = StateFunctor.lift_logic(f) where backend is D-gent
```

**Pattern**:
```python
def chat_logic(msg: str, history: list) -> tuple[str, list]:
    """Pure function: (input, state) → (output, new_state)"""
    history.append(("user", msg))
    response = generate(history)
    history.append(("bot", response))
    return response, history

memory = VolatileAgent(_state=[])
chatbot = Symbiont(logic=chat_logic, memory=memory)
await chatbot.invoke("Hello")  # State threaded automatically
```

**Key Insight**: Logic remains pure; D-gent handles side effects.

See: `spec/agents/functor-catalog.md` §14 (State Functor) for formal treatment.

---

## Lenses: Focused State Access

Compositional getter/setter pairs for sub-state access.

```python
Lens[S, A] = (get: S → A, set: (S, A) → S)
```

**Laws** (must satisfy all three):
1. **GetPut**: `lens.set(s, lens.get(s)) == s`
2. **PutGet**: `lens.get(lens.set(s, a)) == a`
3. **PutPut**: `lens.set(lens.set(s, a), b) == lens.set(s, b)`

**Composition**: `user_lens >> address_lens >> city_lens` → focus on nested city.

**LensAgent**: D-gent that projects through a lens:
```python
global_dgent = PersistentAgent[GlobalState](...)
user_dgent = LensAgent(global_dgent, user_lens)  # Sees only user slice
```

---

## DataBus Integration

D-gent emits events on state changes:

```python
class DataEventType(Enum):
    CREATED = auto()
    UPDATED = auto()
    DELETED = auto()

@dataclass
class DataEvent:
    event_type: DataEventType
    datum_id: str
    namespace: str
    timestamp: float
```

**BusEnabledDgent**: Wraps any DgentProtocol to emit events.

See: `docs/skills/data-bus-integration.md` for event-driven patterns.

---

## Usage Patterns

### Via DgentRouter (Recommended)

```python
from agents.d import DgentRouter, Datum

router = DgentRouter(namespace="my-service")
datum = Datum.create(b'{"key": "value"}')
await router.put(datum)
retrieved = await router.get(datum.id)
```

### Via Symbiont (State Threading)

```python
from agents.d import Symbiont, VolatileAgent

memory = VolatileAgent(_state=initial_state)
agent = Symbiont(logic=my_logic, memory=memory)
result = await agent.invoke(input_data)
```

### Via LensAgent (Focused Access)

```python
from agents.d import LensAgent, key_lens

global_store = DgentRouter(namespace="global")
user_store = LensAgent(global_store, key_lens("users"))
```

---

## Anti-Patterns

```python
# ❌ Hardcoded paths
Path.home() / ".kgents" / "state.json"

# ✅ XDG-compliant via DgentRouter
DgentRouter(namespace="state")

# ❌ Multiple databases per project
project / ".kgents" / "cortex.db"

# ✅ Single database with namespace
DgentRouter(namespace=f"project:{project_hash}")

# ❌ Direct file I/O
Path("state.json").write_text(json.dumps(state))

# ✅ DgentProtocol
await router.put(Datum.create(json.dumps(state).encode()))

# ❌ Bypassing Symbiont state threading
state = await memory.load()
state["value"] = 42
await memory.save(state)  # Logic bypassed!

# ✅ All changes through logic
await symbiont.invoke("set_value_42")
```

---

## Dual Protocol Design

D-gent provides **two complementary protocols** for different use cases:

| Protocol | Signature | Use Case |
|----------|-----------|----------|
| **DgentProtocol** | `put/get/delete/list/causal_chain` | Schema-free Datum persistence |
| **DataAgent[S]** | `load/save/history` | Typed state management with Symbiont |

```python
# DgentProtocol: Schema-free bytes
class DgentProtocol(Protocol):
    async def put(self, datum: Datum) -> str: ...
    async def get(self, id: str) -> Datum | None: ...

# DataAgent[S]: Typed state (used with Symbiont)
class DataAgent(Protocol[S]):
    async def load(self) -> S: ...
    async def save(self, state: S) -> None: ...
    async def history(self, limit: int | None = None) -> list[S]: ...
```

**When to use which**:
- **DgentProtocol**: Raw data storage, causal lineage, schema-at-read patterns
- **DataAgent[S]**: Symbiont state threading, typed agents, state machines

---

## Implementation Reference

| File | Purpose |
|------|---------|
| `datum.py` | Datum dataclass |
| `protocol.py` | DgentProtocol + legacy DataAgent |
| `router.py` | DgentRouter (backend selection) |
| `backends/` | Memory, JSONL, SQLite, Postgres |
| `symbiont.py` | State threading pattern |
| `lens.py` | Lens, Prism, Traversal |
| `lens_agent.py` | LensAgent (focused D-gent) |
| `bus.py` | DataBus, BusEnabledDgent |

---

## Cross-References

- **Protocol**: `spec/protocols/storage-unified.md` (Unified storage architecture)
- **Skill**: `docs/skills/unified-storage.md`
- **Skill**: `docs/skills/metaphysical-fullstack.md` (Layer 0)
- **Functor**: `spec/agents/functor-catalog.md` §14 (State Functor)
- **Principles**: `spec/principles.md` §Graceful Degradation

---

*"Every agent that persists does so through D-gent. D-gent is the ground upon which memory stands."*
