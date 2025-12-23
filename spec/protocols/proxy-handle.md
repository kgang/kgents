# Proxy Handle Protocol

**Status:** Draft
**Implementation:** `impl/claude/services/proxy/` (0 tests — new)
**Extends:** AD-015 (Proxy Handles & Transparent Batch Processes)

## Purpose

Proxy handles provide **epistemic hygiene** for computed data. Every expensive computation produces a proxy handle—an independent artifact with its own identity, lifecycle, and provenance. This makes data staleness, computation state, and refresh mechanics **explicit and transparent** to both humans and agents.

The alternative—hidden caching with implicit refresh—is hostile to agents because they cannot reason about what they cannot see.

## Core Insight

> *"The representation of an object is distinct from the object itself. Agents work with projections of truth, not truth itself—so make the projection visible."*

A proxy handle is **not a cache**. A cache is an optimization; a proxy handle is an **ontological claim** about the nature of computed data.

## The Deeper Principle: Epistemic Transparency

AD-015 established:
1. Hidden computation is hostile to agents
2. Explicit triggers > implicit magic
3. Proxy handles have independent lifecycles
4. Transparency enables agent reasoning

This protocol operationalizes that philosophy into a reusable foundation.

## Type Signatures

### ProxyHandle[T]

```python
@dataclass
class ProxyHandle(Generic[T]):
    """
    A proxy handle is a representation of computed data.

    It is NOT the source. It is a lens on the source.
    It has its own lifecycle, independent of what it represents.
    """

    # Identity
    handle_id: str                    # Unique identifier (UUID)
    source_type: SourceType           # What this is a proxy for

    # Lifecycle
    status: HandleStatus              # EMPTY | COMPUTING | FRESH | STALE | ERROR
    created_at: datetime
    expires_at: datetime | None       # None = never expires
    source_hash: str | None           # Hash of source at computation time

    # Data
    data: T | None                    # The computed data
    error: str | None                 # If status == ERROR

    # Provenance (who, when, how long)
    computed_by: str                  # Who/what computed this
    computation_duration: float       # How long it took (seconds)
    computation_count: int            # How many times refreshed

    # Access tracking
    last_accessed: datetime
    access_count: int

    def is_fresh(self) -> bool: ...
    def is_stale(self) -> bool: ...
    def is_computing(self) -> bool: ...
```

### HandleStatus State Machine

```
                    ┌─────────────┐
                    │    EMPTY    │ ← Initial state, no handle exists
                    └──────┬──────┘
                           │ compute()
                           ▼
                    ┌─────────────┐
         ┌─────────│  COMPUTING  │─────────┐
         │         └──────┬──────┘         │
         │ error          │ success        │ timeout
         ▼                ▼                ▼
   ┌─────────────┐ ┌─────────────┐  ┌─────────────┐
   │    ERROR    │ │    FRESH    │  │    ERROR    │
   └─────────────┘ └──────┬──────┘  └─────────────┘
                          │ time passes / source changes
                          ▼
                   ┌─────────────┐
                   │    STALE    │
                   └──────┬──────┘
                          │ refresh()
                          ▼
                   ┌─────────────┐
                   │  COMPUTING  │ → (cycle continues)
                   └─────────────┘
```

### SourceType

```python
class SourceType(str, Enum):
    """Known proxy handle source types."""

    # Existing
    SPEC_CORPUS = "spec_corpus"           # Spec ledger analysis

    # New capabilities
    WITNESS_GRAPH = "witness_graph"       # Witness mark summaries
    CODEBASE_GRAPH = "codebase_graph"     # Codebase topology analysis
    TOWN_SNAPSHOT = "town_snapshot"       # Agent town state
    MEMORY_CRYSTALS = "memory_crystals"   # K-gent memory summaries
    CUSTOM = "custom"                     # Extension point
```

### ProxyHandleStore

```python
class ProxyHandleStore(Protocol):
    """
    Manages proxy handle lifecycle across the system.

    Responsibilities:
    - Store handles (in-memory with optional persistence)
    - Track staleness via source hash comparison
    - Coordinate computation (prevent duplicate work)
    - Emit events for transparency
    """

    async def get(self, source_type: SourceType) -> ProxyHandle[Any] | None:
        """Get existing handle, or None if doesn't exist."""
        ...

    async def get_or_raise(self, source_type: SourceType) -> ProxyHandle[Any]:
        """Get existing handle, or raise NoProxyHandleError."""
        ...

    async def compute(
        self,
        source_type: SourceType,
        compute_fn: Callable[[], Awaitable[T]],
        *,
        force: bool = False,
        ttl: timedelta | None = None,
        human_label: str,  # Required: no anonymous debris
    ) -> ProxyHandle[T]:
        """
        AD-015: Explicit computation is the ONLY way to create/refresh handles.

        This method is idempotent: concurrent calls for same source_type
        will await the same computation.
        """
        ...

    async def invalidate(self, source_type: SourceType) -> None:
        """Mark a handle as STALE (source changed)."""
        ...

    async def delete(self, source_type: SourceType) -> bool:
        """Remove a handle entirely."""
        ...

    def subscribe(self, callback: ProxyHandleEventCallback) -> Unsubscribe:
        """Subscribe to lifecycle events for transparency."""
        ...
```

### ProxyHandleEvent

```python
@dataclass
class ProxyHandleEvent:
    """Events emitted during proxy handle lifecycle."""

    event_type: Literal[
        "computation_started",    # compute() called
        "computation_completed",  # compute() succeeded
        "computation_failed",     # compute() errored
        "handle_accessed",        # get() called
        "handle_stale",           # TTL expired or source changed
        "handle_invalidated",     # invalidate() called
        "handle_deleted",         # delete() called
    ]
    source_type: SourceType
    handle_id: str | None
    timestamp: datetime
    details: dict[str, Any]
```

## Laws/Invariants

### Law 1: Explicit Computation

Proxy handles are NEVER auto-computed. A handle is created ONLY by calling `compute()`:

```python
# WRONG: Implicit computation
def get_data():
    if not cached:
        cached = expensive_compute()  # Hidden!
    return cached

# RIGHT: Explicit computation
handle = await store.get_or_raise("spec_corpus")  # Raises if no handle
# User/agent explicitly triggers: await store.compute("spec_corpus", ...)
```

### Law 2: Provenance Preservation

Every handle knows who created it and when:

```python
assert handle.computed_by is not None
assert handle.created_at is not None
assert handle.computation_duration >= 0
```

### Law 3: Event Transparency

Every state transition emits exactly one event:

```python
# computation_started → computation_completed | computation_failed
# No silent transitions
```

### Law 4: No Anonymous Debris

Every handle requires a human-readable label (follows `LifecycleCacheEntry` pattern):

```python
# WRONG
await store.compute("spec_corpus", fn)

# RIGHT
await store.compute("spec_corpus", fn, human_label="Spec corpus analysis")
```

### Law 5: Idempotent Computation

Concurrent `compute()` calls for the same source_type await the same computation:

```python
# These await the same computation, don't race
task1 = asyncio.create_task(store.compute("spec_corpus", fn))
task2 = asyncio.create_task(store.compute("spec_corpus", fn))
handle1 = await task1
handle2 = await task2
assert handle1.handle_id == handle2.handle_id
```

## Integration

### AGENTESE Paths

```python
# Proxy handle operations
self.proxy.list                 # List all handles with status
self.proxy.status/{source_type} # Get handle status
self.proxy.compute/{source_type}  # Trigger computation
self.proxy.invalidate/{source_type}  # Mark as stale

# Example: Spec corpus
self.proxy.compute/spec_corpus  # Replaces: kg spec analyze
```

### Event Bus Integration

Proxy handle events emit to WitnessSynergyBus:

```python
WitnessTopics.PROXY_STARTED = "witness.proxy.started"
WitnessTopics.PROXY_COMPLETED = "witness.proxy.completed"
WitnessTopics.PROXY_FAILED = "witness.proxy.failed"
WitnessTopics.PROXY_STALE = "witness.proxy.stale"
```

### Reactive Invalidation (Phase 2)

The ProxyReactor enables **event-driven staleness** — handles are invalidated when their sources change, not just when TTL expires. This inverts staleness detection from pull to push.

```
WitnessSynergyBus ──publish──▶ ProxyReactor._on_source_changed()
                                      │
                                      │ await store.invalidate()
                                      ▼
                               ProxyHandleStore
                                      │
                                      │ emit event
                                      ▼
                               WitnessSynergyBus ──▶ (cycle continues)
```

#### Source-to-Topic Mapping

```python
# Each SourceType maps to topics that trigger invalidation
InvalidationTrigger(
    topic="witness.spec.deprecated",    # Spec file deprecated
    source_types=(SourceType.SPEC_CORPUS,),
)
InvalidationTrigger(
    topic="witness.git.commit",         # Git commit (filtered by path)
    source_types=(SourceType.SPEC_CORPUS, SourceType.CODEBASE_GRAPH),
    filter_fn=lambda e: any(f.startswith("spec/") for f in e.get("files", [])),
)
```

#### Why Reactive > Polling

| Approach | Detection Latency | Resource Usage | Complexity |
|----------|-------------------|----------------|------------|
| **TTL-only** | Up to TTL duration | Low | Simple |
| **Poll on access** | Immediate | High (check every access) | Moderate |
| **Reactive** | Immediate | Low (event-driven) | Moderate |

The insight: Instead of checking "is source stale?" on every access, we listen for "source changed" events and pre-emptively invalidate

### CLI Integration

```bash
# Unified CLI commands
kg proxy list                       # List all proxy handles
kg proxy status spec_corpus         # Check handle status
kg proxy compute spec_corpus        # Trigger computation
kg proxy invalidate spec_corpus     # Mark as stale

# Migration aliases (backwards compatible)
kg spec analyze → kg proxy compute spec_corpus
```

### API Integration

```python
class DataNotComputedResponse(BaseModel):
    """AD-015: Standard response when proxy handle missing."""
    success: bool = False
    needs_computation: bool = True
    source_type: str
    compute_endpoint: str
    message: str
    hint: str = "AD-015: Analysis is explicit. Run compute to generate."
```

### Frontend Integration

```typescript
interface UseProxyHandleOptions<T> {
  sourceType: SourceType;
  fetchFn: () => Promise<T | DataNotComputedResponse>;
  computeFn: () => Promise<void>;
}

function useProxyHandle<T>({ sourceType, fetchFn, computeFn }: UseProxyHandleOptions<T>) {
  // Returns: { data, needsComputation, isComputing, error, compute, refresh }
}
```

## Domains

### Current (Refactor)

| Domain | Source Type | Current State | After |
|--------|-------------|---------------|-------|
| **Spec Ledger** | `spec_corpus` | Ad-hoc `LedgerCache` | Generic `ProxyHandle` |

### New Capabilities

| Domain | Source Type | Description |
|--------|-------------|-------------|
| **Witness Graph** | `witness_graph` | Summarized witness marks |
| **Codebase Graph** | `codebase_graph` | Codebase topology analysis |
| **Town Snapshot** | `town_snapshot` | Agent town state dump |
| **Memory Crystals** | `memory_crystals` | K-gent memory summaries |

## Anti-Patterns

1. **Hidden Computation**: Calling `compute()` automatically in `get()`. Violates Law 1.

2. **Magic Caching**: Using proxies as transparent caches. The handle IS the artifact.

3. **Silent Refresh**: Refreshing handles without emitting events. Violates Law 3.

4. **Anonymous Handles**: Creating handles without human-readable labels. Violates Law 4.

5. **Eager Computation**: Pre-computing handles at startup. Let users/agents decide.

## Reusable Infrastructure

This protocol reuses existing patterns:

| Pattern | Source | How Used |
|---------|--------|----------|
| **LifecycleCacheEntry** | `infra/ghost/lifecycle.py` | TTL, human labels, access tracking |
| **WitnessSynergyBus** | `services/witness/bus.py` | Event emission |
| **EphemeralAgentCache** | `services/foundry/cache.py` | LRU mechanics, metrics |
| **TableAdapter** | `agents/d/adapters/table_adapter.py` | Optional DB persistence |

## Implementation Reference

See: `impl/claude/services/proxy/`

---

*"The map is not the territory. The proxy is not the truth. But we navigate by maps and work with proxies—so make them visible."*
