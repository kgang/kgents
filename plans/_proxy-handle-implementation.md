# Proxy Handle Implementation Plan

**Spec:** `spec/protocols/proxy-handle.md`
**Priority:** High — Foundation for epistemic hygiene across all computed data
**Estimated Effort:** 3-4 sessions

---

## Executive Summary

Transform the ad-hoc spec ledger caching into a **foundational abstraction** that any service can use. Every expensive computation produces a `ProxyHandle[T]` — an artifact with explicit identity, lifecycle, and provenance. This makes staleness, computation state, and refresh mechanics visible to agents.

### The Radical Insight

**Backwards incompatibility is acceptable** because:
1. The current `LedgerCache` is internal, not a public API
2. The CLI command can alias (`kg spec analyze` → `kg proxy compute spec_corpus`)
3. The API response is already structured for this (`needs_scan: true`)
4. The frontend hook already handles the `needsComputation` state

We can make the **semantics cleaner** without breaking user workflows.

---

## Phase 1: Core Infrastructure (Session 1)

### 1.1 Create Service Directory

```
impl/claude/services/proxy/
├── __init__.py
├── types.py          # ProxyHandle, HandleStatus, SourceType, ProxyHandleEvent
├── store.py          # ProxyHandleStore implementation
├── exceptions.py     # NoProxyHandleError, ComputationError
├── node.py           # AGENTESE node: self.proxy.*
└── _tests/
    ├── test_types.py
    ├── test_store.py
    └── test_node.py
```

### 1.2 Types (`types.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Generic, TypeVar
import uuid

T = TypeVar("T")


class HandleStatus(str, Enum):
    """Proxy handle lifecycle states."""
    EMPTY = "empty"           # No handle exists
    COMPUTING = "computing"   # Computation in progress
    FRESH = "fresh"           # Valid data available
    STALE = "stale"           # TTL expired or source changed
    ERROR = "error"           # Computation failed


class SourceType(str, Enum):
    """Known proxy handle source types."""
    SPEC_CORPUS = "spec_corpus"
    WITNESS_GRAPH = "witness_graph"
    CODEBASE_GRAPH = "codebase_graph"
    TOWN_SNAPSHOT = "town_snapshot"
    MEMORY_CRYSTALS = "memory_crystals"
    CUSTOM = "custom"


@dataclass
class ProxyHandle(Generic[T]):
    """
    A proxy handle is a representation of computed data.
    See spec/protocols/proxy-handle.md for full specification.
    """
    # Identity
    handle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType = SourceType.CUSTOM
    human_label: str = ""  # Required at creation time

    # Lifecycle
    status: HandleStatus = HandleStatus.EMPTY
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    source_hash: str | None = None

    # Data
    data: T | None = None
    error: str | None = None

    # Provenance
    computed_by: str = "system"
    computation_duration: float = 0.0
    computation_count: int = 0

    # Access tracking
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def __post_init__(self) -> None:
        if not self.human_label:
            raise ValueError("human_label is required (no anonymous debris)")
        if self.expires_at is None:
            self.expires_at = self.created_at + self.ttl

    def is_fresh(self) -> bool:
        return self.status == HandleStatus.FRESH and datetime.now() < self.expires_at

    def is_stale(self) -> bool:
        return self.status == HandleStatus.STALE or (
            self.status == HandleStatus.FRESH and datetime.now() >= self.expires_at
        )

    def is_computing(self) -> bool:
        return self.status == HandleStatus.COMPUTING

    def access(self) -> None:
        self.last_accessed = datetime.now()
        self.access_count += 1
```

### 1.3 Store (`store.py`)

Key implementation notes:

1. **Idempotent Computation**: Use `asyncio.Lock` per source_type to prevent duplicate work
2. **Event Emission**: Non-blocking via `asyncio.create_task()`
3. **Persistence**: Optional JSONL file at `~/.local/share/kgents/proxy/handles.jsonl`
4. **Thread Safety**: `threading.RLock` for in-memory dict access

```python
class ProxyHandleStore:
    """
    Manages proxy handle lifecycle.
    See spec/protocols/proxy-handle.md for full specification.
    """

    def __init__(
        self,
        persist_path: Path | None = None,
        default_ttl: timedelta = timedelta(minutes=5),
    ) -> None:
        self._handles: dict[SourceType, ProxyHandle[Any]] = {}
        self._compute_locks: dict[SourceType, asyncio.Lock] = {}
        self._lock = threading.RLock()
        self._callbacks: list[ProxyHandleEventCallback] = []
        self._persist_path = persist_path
        self._default_ttl = default_ttl

    async def compute(
        self,
        source_type: SourceType,
        compute_fn: Callable[[], Awaitable[T]],
        *,
        force: bool = False,
        ttl: timedelta | None = None,
        human_label: str,
    ) -> ProxyHandle[T]:
        """AD-015: Explicit computation is the ONLY way to create/refresh handles."""
        # Idempotency: concurrent calls await same computation
        lock = self._get_or_create_lock(source_type)

        async with lock:
            existing = self._handles.get(source_type)
            if existing and existing.is_fresh() and not force:
                existing.access()
                return existing

            # Emit start event
            await self._emit(ProxyHandleEvent(
                event_type="computation_started",
                source_type=source_type,
                handle_id=None,
                timestamp=datetime.now(),
                details={"force": force},
            ))

            start_time = time.time()
            try:
                data = await compute_fn()
                duration = time.time() - start_time

                handle = ProxyHandle[T](
                    source_type=source_type,
                    human_label=human_label,
                    status=HandleStatus.FRESH,
                    data=data,
                    ttl=ttl or self._default_ttl,
                    computed_by="system",
                    computation_duration=duration,
                    computation_count=(existing.computation_count + 1) if existing else 1,
                )
                self._handles[source_type] = handle
                await self._persist_if_enabled()

                await self._emit(ProxyHandleEvent(
                    event_type="computation_completed",
                    source_type=source_type,
                    handle_id=handle.handle_id,
                    timestamp=datetime.now(),
                    details={"duration": duration},
                ))

                return handle

            except Exception as e:
                handle = ProxyHandle[T](
                    source_type=source_type,
                    human_label=human_label,
                    status=HandleStatus.ERROR,
                    error=str(e),
                )
                self._handles[source_type] = handle

                await self._emit(ProxyHandleEvent(
                    event_type="computation_failed",
                    source_type=source_type,
                    handle_id=handle.handle_id,
                    timestamp=datetime.now(),
                    details={"error": str(e)},
                ))

                raise
```

### 1.4 DI Registration

In `services/providers.py`:

```python
from services.proxy.store import ProxyHandleStore

_proxy_store: ProxyHandleStore | None = None

def get_proxy_handle_store() -> ProxyHandleStore:
    global _proxy_store
    if _proxy_store is None:
        _proxy_store = ProxyHandleStore()
    return _proxy_store

# Register with container
container.register("proxy_handle_store", get_proxy_handle_store, singleton=True)
```

---

## Phase 2: Event Integration (Session 2)

### 2.1 Add Witness Topics

In `services/witness/bus.py`:

```python
class WitnessTopics:
    # ... existing ...

    # Proxy handle lifecycle
    PROXY_STARTED = "witness.proxy.started"
    PROXY_COMPLETED = "witness.proxy.completed"
    PROXY_FAILED = "witness.proxy.failed"
    PROXY_STALE = "witness.proxy.stale"
    PROXY_ALL = "witness.proxy.*"
```

### 2.2 Wire Events

In `store.py`:

```python
async def _emit(self, event: ProxyHandleEvent) -> None:
    """Non-blocking event emission to WitnessSynergyBus."""
    try:
        bus = get_synergy_bus()
        topic = {
            "computation_started": WitnessTopics.PROXY_STARTED,
            "computation_completed": WitnessTopics.PROXY_COMPLETED,
            "computation_failed": WitnessTopics.PROXY_FAILED,
            "handle_stale": WitnessTopics.PROXY_STALE,
        }.get(event.event_type)

        if topic and bus:
            asyncio.create_task(bus.publish(topic, event.to_dict()))
    except Exception:
        pass  # Graceful degradation: event emission never blocks
```

---

## Phase 3: Spec Ledger Migration (Session 2-3)

### 3.1 Refactor LedgerNode

Replace ad-hoc `_cache` with `ProxyHandleStore`:

```python
# services/living_spec/ledger_node.py

class LedgerNode:
    def __init__(self, proxy_store: ProxyHandleStore | None = None):
        self.proxy_store = proxy_store or get_proxy_handle_store()

    async def scan(self, force: bool = False) -> dict[str, Any]:
        """AD-015: Explicit analysis via ProxyHandleStore."""
        handle = await self.proxy_store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=self._analyze_corpus,
            force=force,
            ttl=timedelta(minutes=5),
            human_label="Spec corpus analysis",
        )
        return self._format_scan_response(handle)

    async def ledger(self, **kwargs) -> dict[str, Any]:
        """AD-015: Get existing handle or raise."""
        handle = await self.proxy_store.get_or_raise(SourceType.SPEC_CORPUS)
        return self._filter_and_format(handle.data, **kwargs)
```

### 3.2 Update API

In `protocols/api/spec_ledger.py`, replace `NoPreComputedDataError` catch with generic `NoProxyHandleError`.

### 3.3 Maintain Backwards Compatibility

```python
# Alias for migration period
from services.proxy.exceptions import NoProxyHandleError

NoPreComputedDataError = NoProxyHandleError  # Deprecated alias
```

---

## Phase 4: AGENTESE Node (Session 3)

### 4.1 Create Node

```python
# services/proxy/node.py

@node(
    path="self.proxy",
    effects=["read", "compute"],
    description="Proxy handle lifecycle management",
)
class ProxyNode:
    def __init__(self, proxy_store: ProxyHandleStore | None = None):
        self.store = proxy_store or get_proxy_handle_store()

    @aspect("list")
    async def list_handles(self) -> dict[str, Any]:
        """List all proxy handles with status."""
        handles = self.store.all()
        return {
            "handles": [
                {
                    "source_type": h.source_type.value,
                    "status": h.status.value,
                    "human_label": h.human_label,
                    "created_at": h.created_at.isoformat(),
                    "is_fresh": h.is_fresh(),
                }
                for h in handles
            ]
        }

    @aspect("status/{source_type}")
    async def get_status(self, source_type: str) -> dict[str, Any]:
        """Get handle status for a source type."""
        st = SourceType(source_type)
        handle = await self.store.get(st)
        if not handle:
            return {"exists": False, "source_type": source_type}
        return {
            "exists": True,
            "source_type": source_type,
            "status": handle.status.value,
            "is_fresh": handle.is_fresh(),
            "expires_in": (handle.expires_at - datetime.now()).total_seconds() if handle.expires_at else None,
        }
```

### 4.2 Register Node

In `protocols/agentese/gateway.py`, import and register the node.

---

## Phase 5: CLI Integration (Session 3)

### 5.1 Add Commands

```python
# protocols/cli/handlers/proxy_thin.py

@click.group(name="proxy")
def proxy_group():
    """Proxy handle lifecycle management."""
    pass

@proxy_group.command(name="list")
def list_handles():
    """List all proxy handles."""
    # Invoke AGENTESE: self.proxy.list
    ...

@proxy_group.command(name="status")
@click.argument("source_type")
def get_status(source_type: str):
    """Get handle status."""
    # Invoke AGENTESE: self.proxy.status/{source_type}
    ...

@proxy_group.command(name="compute")
@click.argument("source_type")
@click.option("--force", is_flag=True, help="Force recomputation")
def compute(source_type: str, force: bool):
    """Trigger computation."""
    # Invoke AGENTESE: self.proxy.compute/{source_type}
    ...
```

### 5.2 Migration Alias

```python
# In legacy.py or spec handler
# kg spec analyze → kg proxy compute spec_corpus
@spec_group.command(name="analyze")
def analyze_legacy():
    """[Deprecated] Use 'kg proxy compute spec_corpus' instead."""
    click.echo("Redirecting to: kg proxy compute spec_corpus")
    invoke_agentese("self.proxy.compute/spec_corpus")
```

---

## Phase 6: Frontend Integration (Session 4)

### 6.1 Generic Hook

```typescript
// api/useProxyHandle.ts

interface UseProxyHandleOptions<T> {
  sourceType: SourceType;
  fetchFn: () => Promise<T | DataNotComputedResponse>;
  computeFn: () => Promise<void>;
}

export function useProxyHandle<T>({
  sourceType,
  fetchFn,
  computeFn,
}: UseProxyHandleOptions<T>): UseProxyHandleReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [needsComputation, setNeedsComputation] = useState(false);
  const [isComputing, setIsComputing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetch() {
      try {
        const response = await fetchFn();
        if (isNeedsComputation(response)) {
          setNeedsComputation(true);
          setData(null);
        } else {
          setData(response as T);
          setNeedsComputation(false);
        }
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
      }
    }
    fetch();
  }, [fetchFn]);

  const compute = useCallback(async () => {
    setIsComputing(true);
    try {
      await computeFn();
      // Refetch after computation
      const response = await fetchFn();
      setData(response as T);
      setNeedsComputation(false);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsComputing(false);
    }
  }, [computeFn, fetchFn]);

  return { data, needsComputation, isComputing, error, compute };
}
```

### 6.2 Refactor Existing Hooks

```typescript
// membrane/chart/useAstronomicalData.ts

export function useAstronomicalData(options: AstronomicalDataOptions) {
  const { stars, connections, ...proxyState } = useProxyHandle({
    sourceType: SourceType.SPEC_CORPUS,
    fetchFn: () => getLedger(options),
    computeFn: () => scanCorpus(true),
  });

  // Transform data...
  return { stars, connections, ...proxyState };
}
```

### 6.3 Reusable Component

```tsx
// components/ProxyHandleGate.tsx

interface ProxyHandleGateProps {
  needsComputation: boolean;
  isComputing: boolean;
  onCompute: () => void;
  computeLabel?: string;
  children: React.ReactNode;
}

export function ProxyHandleGate({
  needsComputation,
  isComputing,
  onCompute,
  computeLabel = "Generate Data",
  children,
}: ProxyHandleGateProps) {
  if (isComputing) {
    return <LoadingSpinner message="Computing..." />;
  }

  if (needsComputation) {
    return (
      <EmptyState
        icon={<ComputeIcon />}
        title="Data Not Available"
        description="This data needs to be computed. Click the button to generate."
        action={<Button onClick={onCompute}>{computeLabel}</Button>}
      />
    );
  }

  return <>{children}</>;
}
```

---

## Phase 7: New Domains (Future Sessions)

### 7.1 Witness Graph Proxy

```python
# services/witnessed_graph/proxy.py

async def compute_witness_graph_proxy(
    persistence: WitnessPersistence,
    proxy_store: ProxyHandleStore,
) -> ProxyHandle[WitnessGraphSummary]:
    """Compute summarized witness graph proxy handle."""
    return await proxy_store.compute(
        source_type=SourceType.WITNESS_GRAPH,
        compute_fn=lambda: summarize_witness_marks(persistence),
        ttl=timedelta(minutes=10),
        human_label="Witness graph summary",
    )
```

### 7.2 Codebase Graph Proxy (New Capability!)

```python
# services/codebase/proxy.py

async def compute_codebase_graph_proxy(
    root: Path,
    proxy_store: ProxyHandleStore,
) -> ProxyHandle[CodebaseGraph]:
    """Compute codebase topology analysis."""
    return await proxy_store.compute(
        source_type=SourceType.CODEBASE_GRAPH,
        compute_fn=lambda: analyze_codebase(root),
        ttl=timedelta(minutes=30),  # Longer TTL, expensive
        human_label="Codebase topology analysis",
    )
```

---

## Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| **Abstraction exists** | `ProxyHandle[T]` is a real, usable type |
| **Store works** | `ProxyHandleStore` manages lifecycle correctly |
| **Spec ledger refactored** | Uses generic pattern, not ad-hoc code |
| **CLI unified** | `kg proxy` commands work for all source types |
| **Frontend reusable** | `useProxyHandle` hook works for any data |
| **Events emitted** | All lifecycle transitions emit to WitnessSynergyBus |
| **Tests pass** | >90% coverage on proxy service |

---

## Testing Strategy

### Unit Tests

- `test_types.py`: ProxyHandle state machine, expiration logic
- `test_store.py`: Idempotent computation, event emission, persistence
- `test_node.py`: AGENTESE aspects work correctly

### Integration Tests

- Spec ledger migration works end-to-end
- CLI commands invoke correct AGENTESE paths
- Frontend hooks receive correct data shapes

### Property-Based Tests

- Concurrent `compute()` calls are idempotent
- TTL expiration triggers staleness
- Event count matches state transitions

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Breaking spec ledger API** | Add deprecated aliases, gradual migration |
| **Event storm** | Batch events, rate limit per source_type |
| **Memory pressure** | Optional persistence, LRU eviction for many handles |
| **Test flakiness** | Use time-travel for TTL tests, not `time.sleep()` |

---

## File Changes Summary

**New files:**
- `impl/claude/services/proxy/__init__.py`
- `impl/claude/services/proxy/types.py`
- `impl/claude/services/proxy/store.py`
- `impl/claude/services/proxy/exceptions.py`
- `impl/claude/services/proxy/node.py`
- `impl/claude/services/proxy/_tests/test_*.py`
- `impl/claude/web/src/api/useProxyHandle.ts`
- `impl/claude/web/src/components/ProxyHandleGate.tsx`

**Modified files:**
- `impl/claude/services/providers.py` (add `get_proxy_handle_store`)
- `impl/claude/services/witness/bus.py` (add PROXY_* topics)
- `impl/claude/services/living_spec/ledger_node.py` (use ProxyHandleStore)
- `impl/claude/protocols/api/spec_ledger.py` (use NoProxyHandleError)
- `impl/claude/protocols/cli/handlers/legacy.py` (add proxy group)
- `impl/claude/protocols/agentese/gateway.py` (register proxy node)
- `impl/claude/web/src/membrane/chart/useAstronomicalData.ts` (use useProxyHandle)

---

*"The proof IS the decision. The mark IS the witness. The proxy IS the handle."*
