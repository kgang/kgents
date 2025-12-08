# Persistence Strategies

Deep dive on state storage mechanisms and trade-offs.

---

## The Persistence Spectrum

D-gents span a spectrum from **ephemeral** to **eternal**:

```
Volatile ←──────────────────────────────────→ Persistent
(Memory)         (File/DB/Cloud)                (Blockchain)

Fast               ←→                           Durable
Ephemeral          ←→                           Permanent
Process-bound      ←→                           Distributed
```

**Key Trade-off**: Speed vs. Durability

---

## Type I: Volatile Memory

### VolatileAgent

State lives in process memory (RAM). Vanishes when process dies.

**Implementation**:
```python
@dataclass
class VolatileAgent(Generic[S]):
    _state: S
    _history: list[S] = field(default_factory=list)
    _max_history: int = 100

    async def load(self) -> S:
        return copy.deepcopy(self._state)

    async def save(self, state: S) -> None:
        self._history.append(copy.deepcopy(self._state))
        if len(self._history) > self._max_history:
            self._history.pop(0)
        self._state = copy.deepcopy(state)
```

**Characteristics**:
- **Latency**: ~1μs (memory access)
- **Durability**: Process lifetime only
- **Concurrency**: Single-threaded (no locking needed)
- **Size Limit**: Available RAM
- **History**: Optional, bounded by memory

**Use Cases**:
- Conversational context within a session
- Temporary caches
- Scratchpads for computation
- Testing (fast setup/teardown)

**Anti-use Cases**:
- Long-term user data (lost on restart)
- Critical state (no backup)
- Multi-process coordination (not shared)

---

## Type II: File-Based Persistence

### PersistentAgent (JSON/File)

State serialized to local filesystem.

**Implementation**:
```python
@dataclass
class PersistentAgent(Generic[S]):
    path: Path
    schema: Type[S]

    async def load(self) -> S:
        if not self.path.exists():
            raise StateNotFoundError(f"No state at {self.path}")

        with open(self.path, 'r') as f:
            data = json.load(f)

        if is_dataclass(self.schema):
            return self.schema(**data)
        return data

    async def save(self, state: S) -> None:
        # Atomic write: temp file + rename
        temp = self.path.with_suffix('.tmp')
        with open(temp, 'w') as f:
            json.dump(asdict(state) if is_dataclass(state) else state, f)
        temp.rename(self.path)  # Atomic on POSIX
```

**Characteristics**:
- **Latency**: ~1ms (disk I/O)
- **Durability**: Survives restart, not disk failure
- **Concurrency**: Single-process (file locking for multi-process)
- **Size Limit**: Available disk space
- **History**: JSONL append for versioning

**Use Cases**:
- User profiles
- Agent configuration
- Small-to-medium knowledge bases (<10MB)
- Offline-first applications

**Optimizations**:
1. **Write-behind caching**: Buffer writes, flush periodically
2. **Compression**: gzip for large states
3. **Incremental updates**: Write deltas, not full state

---

## Type III: Database-Backed Persistence

### SQLAgent

State stored in relational database (SQLite, Postgres, etc.).

**Implementation**:
```python
@dataclass
class SQLAgent(Generic[S]):
    db_uri: str
    table: str
    schema: Type[S]

    async def load(self) -> S:
        async with aiosqlite.connect(self.db_uri) as db:
            cursor = await db.execute(
                f"SELECT state FROM {self.table} ORDER BY version DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            if not row:
                raise StateNotFoundError()

            data = json.loads(row[0])
            return self.schema(**data)

    async def save(self, state: S) -> None:
        async with aiosqlite.connect(self.db_uri) as db:
            await db.execute(
                f"INSERT INTO {self.table} (state, version, timestamp) VALUES (?, ?, ?)",
                (json.dumps(asdict(state)), self._next_version(), time.time())
            )
            await db.commit()
```

**Characteristics**:
- **Latency**: ~10ms (network + query)
- **Durability**: High (ACID transactions)
- **Concurrency**: Multi-process/multi-node (with locking)
- **Size Limit**: Database limits (TBs)
- **History**: Native versioning via table rows

**Use Cases**:
- Multi-agent coordination (shared state)
- Large state (>10MB)
- Structured queries (SQL WHERE clauses)
- Compliance (audit trails required)

**Query Capabilities**:
```python
# Filter historical states
states = await sql_agent.query(
    "SELECT state FROM states WHERE timestamp > ?",
    (yesterday,)
)

# Aggregate metrics
count = await sql_agent.aggregate("COUNT(*)", "state")
```

---

## Type IV: Key-Value Stores

### RedisAgent

State in distributed key-value store.

**Implementation**:
```python
@dataclass
class RedisAgent(Generic[S]):
    redis_url: str
    key: str
    schema: Type[S]

    async def load(self) -> S:
        async with aioredis.from_url(self.redis_url) as redis:
            data = await redis.get(self.key)
            if not data:
                raise StateNotFoundError()

            return self.schema(**json.loads(data))

    async def save(self, state: S) -> None:
        async with aioredis.from_url(self.redis_url) as redis:
            await redis.set(
                self.key,
                json.dumps(asdict(state)),
                ex=3600  # TTL: 1 hour
            )
```

**Characteristics**:
- **Latency**: ~1-5ms (network roundtrip)
- **Durability**: Configurable (memory-only, AOF, RDB)
- **Concurrency**: Multi-process/multi-node (atomic ops)
- **Size Limit**: RAM on Redis server
- **History**: Via separate keys or streams

**Use Cases**:
- Distributed agent coordination
- Session state (with TTL)
- Real-time caching
- Pub/sub state updates

**Advanced Features**:
```python
# Atomic increment
await redis_agent.execute("INCR", "counter")

# Conditional update (optimistic locking)
await redis_agent.execute("SET", key, value, "XX")  # Only if exists
```

---

## Type V: Vector Stores

### VectorAgent

State as high-dimensional embeddings for semantic search.

**Implementation**:
```python
@dataclass
class VectorAgent(Generic[S]):
    index: faiss.Index
    metadata: dict[int, S]  # id → original state
    dimension: int

    async def load(self) -> list[S]:
        """Load doesn't make sense for vectors; use search instead."""
        raise NotImplementedError("Use search(query) instead")

    async def save(self, state: S) -> None:
        """Add state to vector index."""
        # Embed state (assume state has .embedding attribute)
        vector = np.array(state.embedding).reshape(1, -1)

        # Add to index
        idx = self.index.ntotal
        self.index.add(vector)
        self.metadata[idx] = state

    async def search(self, query_embedding: np.ndarray, k: int = 5) -> list[S]:
        """Find k nearest neighbors."""
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), k
        )
        return [self.metadata[i] for i in indices[0]]
```

**Characteristics**:
- **Latency**: ~1-10ms (index search)
- **Durability**: Depends on backing store (FAISS, Pinecone, Weaviate)
- **Concurrency**: Read-heavy (writes rebuild index)
- **Size Limit**: Millions of vectors
- **History**: No history (semantic memory, not timeline)

**Use Cases**:
- RAG (Retrieval-Augmented Generation)
- Semantic memory (find similar past interactions)
- Concept association ("what's related to X?")

**Query Pattern**:
```python
# Instead of load(), use semantic search
query = "How do I reset my password?"
query_embedding = embed_model.encode(query)

relevant_states = await vector_agent.search(query_embedding, k=3)
# Returns 3 most semantically similar past states
```

---

## Type VI: Event Sourcing

### StreamAgent

State derived by replaying event log.

**Implementation**:
```python
@dataclass
class StreamAgent(Generic[E, S]):
    """
    State reconstructed from events.

    E: Event type
    S: State type
    """
    event_log: list[E]
    fold: Callable[[S, E], S]  # How to apply event to state
    initial: S

    async def load(self) -> S:
        """Replay all events to reconstruct current state."""
        state = copy.deepcopy(self.initial)
        for event in self.event_log:
            state = self.fold(state, event)
        return state

    async def save(self, state: S) -> None:
        """Not used - append events instead."""
        raise NotImplementedError("Use append_event() instead")

    async def append_event(self, event: E) -> None:
        """Append event to log."""
        self.event_log.append(event)

    async def history(self, limit: int | None = None) -> list[S]:
        """Reconstruct state at each point in time."""
        states = []
        state = copy.deepcopy(self.initial)

        for event in self.event_log:
            state = self.fold(state, event)
            states.append(copy.deepcopy(state))

        return states[-limit:] if limit else states
```

**Characteristics**:
- **Latency**: Variable (depends on log length)
- **Durability**: Excellent (append-only log)
- **Concurrency**: Append-friendly (no overwrites)
- **Size Limit**: Log can grow indefinitely
- **History**: Perfect (every state reconstructible)

**Use Cases**:
- Audit trails (compliance)
- Collaborative editing (operational transform)
- Time-travel debugging
- Distributed systems (event sourcing + CQRS)

**Example**:
```python
# Events
@dataclass
class UserCreated:
    user_id: str
    name: str

@dataclass
class UserRenamed:
    user_id: str
    new_name: str

# State
@dataclass
class UserState:
    users: dict[str, str]  # id → name

# Fold function (how events modify state)
def apply_event(state: UserState, event) -> UserState:
    if isinstance(event, UserCreated):
        return UserState(users={**state.users, event.user_id: event.name})
    elif isinstance(event, UserRenamed):
        return UserState(users={**state.users, event.user_id: event.new_name})

# Create stream agent
stream = StreamAgent(
    event_log=[],
    fold=apply_event,
    initial=UserState(users={})
)

# Append events
await stream.append_event(UserCreated("u1", "Alice"))
await stream.append_event(UserRenamed("u1", "Alicia"))

# Reconstruct current state
current = await stream.load()
assert current.users["u1"] == "Alicia"

# Time travel: see state after first event
history = await stream.history()
assert history[0].users["u1"] == "Alice"  # Before rename
```

---

## Choosing a Persistence Strategy

| Requirement | Best Choice |
|-------------|-------------|
| **Speed** (< 1ms) | VolatileAgent |
| **Durability** (survive restart) | PersistentAgent, SQLAgent |
| **Concurrency** (multi-process) | SQLAgent, RedisAgent |
| **Large State** (> 10MB) | SQLAgent, S3Agent |
| **Semantic Search** | VectorAgent |
| **Audit Trail** | StreamAgent (event sourcing) |
| **Distributed** | RedisAgent, DynamoDBAgent |
| **Offline-First** | PersistentAgent (local file) |

---

## Composition: Layered Persistence

Combine multiple D-gents for hybrid strategies:

### Example: Cache + Persistent

```python
class CachedAgent(Generic[S]):
    """
    Volatile cache backed by persistent storage.

    Reads: Check cache first, fallback to backend
    Writes: Update cache, write-through to backend
    """
    def __init__(
        self,
        cache: VolatileAgent[S],
        backend: PersistentAgent[S]
    ):
        self.cache = cache
        self.backend = backend

    async def load(self) -> S:
        try:
            # Try cache first
            return await self.cache.load()
        except StateNotFoundError:
            # Cache miss: load from backend
            state = await self.backend.load()
            await self.cache.save(state)  # Populate cache
            return state

    async def save(self, state: S) -> None:
        # Write-through: update both
        await self.cache.save(state)
        await self.backend.save(state)
```

**Performance**:
- Read hit: ~1μs (from cache)
- Read miss: ~1ms (from backend) + cache population
- Write: ~1ms (to backend)

---

## Entropy-Aware Persistence (J-gents Integration)

State size should respect entropy budgets:

```python
class EntropyConstrainedAgent(Generic[S]):
    """
    D-gent that enforces state size limits based on entropy budget.

    Deeper in promise tree = smaller max state allowed.
    """
    def __init__(
        self,
        backend: DataAgent[S],
        budget: float,
        max_size_bytes: int = 1_000_000  # 1MB at budget=1.0
    ):
        self.backend = backend
        self.budget = budget
        self.max_allowed = int(max_size_bytes * budget)

    async def save(self, state: S) -> None:
        # Serialize to measure size
        serialized = json.dumps(asdict(state) if is_dataclass(state) else state)
        size = len(serialized.encode('utf-8'))

        if size > self.max_allowed:
            raise StateError(
                f"State too large: {size} bytes > {self.max_allowed} "
                f"(budget={self.budget})"
            )

        await self.backend.save(state)
```

**Usage in J-gents**:
```python
# At depth=0: budget=1.0, max=1MB
root_dgent = EntropyConstrainedAgent(backend, budget=1.0)

# At depth=2: budget=0.33, max=330KB
child_dgent = EntropyConstrainedAgent(backend, budget=0.33)
```

---

## Testing Persistence

### Test 1: Round-Trip Integrity

```python
async def test_round_trip(dgent: DataAgent[S], sample: S):
    """State survives save/load without corruption."""
    await dgent.save(sample)
    loaded = await dgent.load()

    # Deep equality check
    assert loaded == sample

    # Ensure it's a copy, not reference
    if hasattr(sample, '__dict__'):
        assert loaded is not sample
```

### Test 2: Crash Recovery

```python
async def test_crash_recovery(dgent_factory: Callable[[], DataAgent[S]], sample: S):
    """State persists across process restarts."""

    # Save state
    dgent1 = dgent_factory()
    await dgent1.save(sample)

    # Simulate crash: delete object (but not backing storage)
    del dgent1

    # Restart: new instance, same backing storage
    dgent2 = dgent_factory()
    loaded = await dgent2.load()

    assert loaded == sample
```

### Test 3: Concurrent Access

```python
async def test_concurrent_writes(dgent: DataAgent[int]):
    """Verify behavior under concurrent writes."""

    async def increment():
        state = await dgent.load()
        await asyncio.sleep(0.01)  # Simulate work
        await dgent.save(state + 1)

    await dgent.save(0)

    # 10 concurrent increments
    await asyncio.gather(*[increment() for _ in range(10)])

    final = await dgent.load()

    # Without locking: may be < 10 due to lost updates
    # With locking: should be exactly 10
    print(f"Final count: {final}/10")
```

---

## Anti-patterns

### Anti-pattern 1: Over-Persisting

```python
# BAD: Persisting every tiny change
for i in range(1000):
    state = await dgent.load()
    state["count"] += 1
    await dgent.save(state)  # 1000 disk writes!

# GOOD: Batch updates
state = await dgent.load()
for i in range(1000):
    state["count"] += 1
await dgent.save(state)  # 1 disk write
```

### Anti-pattern 2: Storing Functions/Closures

```python
# BAD: Trying to persist non-serializable data
@dataclass
class BadState:
    callback: Callable  # Can't serialize!
    data: str

await dgent.save(BadState(lambda x: x, "hello"))  # FAILS

# GOOD: Store serializable data only
@dataclass
class GoodState:
    callback_name: str  # Store reference, not function
    data: str
```

### Anti-pattern 3: Ignoring Failures

```python
# BAD: Silently dropping state on error
try:
    await dgent.save(state)
except Exception:
    pass  # State lost!

# GOOD: Handle errors appropriately
try:
    await dgent.save(state)
except StateSerializationError as e:
    logger.error(f"Failed to save state: {e}")
    # Fallback: save to temporary location
    await backup_dgent.save(state)
```

---

## See Also

- [README.md](README.md) - D-gents overview
- [protocols.md](protocols.md) - DataAgent interface
- [symbiont.md](symbiont.md) - Using persistence in agents
- [../t-gents/](../t-gents/) - Testing persistent systems
- [../j-gents/stability.md](../j-gents/stability.md) - Entropy constraints
