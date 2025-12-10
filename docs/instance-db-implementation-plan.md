# Instance DB Implementation Plan v2.0

## The Unified Cortex: Infrastructure × Semantics

**Status:** Design Document v2.0
**Date:** 2025-12-10
**Location:** `impl/claude/infra/` (Infrastructure) + `agents/d/` (Semantics)

---

## Executive Summary

This document specifies the **Unified Cortex**—a marriage of Infrastructure (Instance DB) with Semantics (D-gents). The result is not a "File System" model of memory, but an "Operating System" model that **predicts**, **forgets**, and **dreams**.

From the critique:
> "A cortex doesn't just store; it predicts, forgets, and hallucinates."

We address three critical gaps:
1. **UnifiedMemory Monolith Risk** → Hemispheric separation (Left/Right/Corpus Callosum)
2. **Compost Implementation Gap** → Cryptographic Amnesia (Lethe Protocol)
3. **Transaction Boundary Problem** → Synapse Event Bus + Eventual Consistency

---

## Part I: Architectural Overview

### 1.1 The Three Hemispheres

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE UNIFIED CORTEX                                 │
├──────────────────────────┬─────────────────┬────────────────────────────────┤
│     LEFT HEMISPHERE      │ CORPUS CALLOSUM │       RIGHT HEMISPHERE          │
│     (The Bookkeeper)     │   (Synapse)     │       (The Poet)                │
├──────────────────────────┼─────────────────┼────────────────────────────────┤
│  • ACID transactions     │ • Signal routing│  • Approximate similarity       │
│  • Exact queries         │ • Active Inference│ • Semantic voids              │
│  • Relational schema     │ • Surprise detection│ • Geodesics (paths)         │
│  • Instance tracking     │ • Backpressure  │  • Memory Garden               │
├──────────────────────────┼─────────────────┼────────────────────────────────┤
│  impl/claude/infra/      │ infra/synapse.py│  agents/d/                     │
│  └── storage.py          │                 │  └── unified.py                │
│  └── lifecycle.py        │                 │  └── manifold.py               │
│  └── providers/          │                 │  └── garden.py                 │
└──────────────────────────┴─────────────────┴────────────────────────────────┘
```

### 1.2 Layer Responsibilities

| Layer | Location | Responsibility | Examples |
|-------|----------|----------------|----------|
| **Infrastructure** | `infra/` | Bytes, rows, lifecycle | SQLite, XDG paths, heartbeat |
| **Synapse** | `infra/synapse.py` | Signal routing, prediction | Active Inference, surprise |
| **Semantics** | `agents/d/` | Meaning, memory modes | VectorAgent, MemoryGarden |
| **Application** | `**/` | User-facing features | CLI, MCP, agents |

### 1.3 The Synapse Event Bus

From the critique:
> "Instead of direct method calls between D-gents and Storage, introduce a lightweight signal layer."

```python
class Synapse:
    async def fire(self, signal: Signal) -> None:
        # 1. Active Inference: Calculate Surprise
        surprise = self.predictive_model.evaluate(signal)

        # 2. Routing: High surprise → Fast path
        #             Low surprise  → Batch path
        if surprise > threshold:
            await self.fast_path.emit(signal)
        else:
            await self.garden.queue(signal)
```

**Benefits:**
- Decouples agent intent from storage mechanism
- Enables smart batching (low-surprise signals are batched)
- Provides observability (all signals are traceable)
- Implements backpressure (buffer overflow → graceful degradation)

---

## Part II: Infrastructure Layer (`impl/claude/infra/`)

### 2.1 Module Structure

```
impl/claude/infra/
├── __init__.py          # Public API
├── ground.py            # Ground bootstrap agent (XDG, config)
├── lifecycle.py         # LifecycleManager (bootstrap, shutdown)
├── storage.py           # StorageProvider (Left Hemisphere)
├── synapse.py           # Synapse event bus (Corpus Callosum)
└── providers/
    └── __init__.py      # Provider factory + SQLite implementations
```

### 2.2 Ground: The Bootstrap Seed

From spec/bootstrap.md:
> `Ground: Void → Facts`

```python
@dataclass
class Ground:
    paths: XDGPaths              # ~/.config/kgents, ~/.local/share/kgents
    config: InfrastructureConfig # infrastructure.yaml
    platform: str                # darwin, linux, windows
    hostname: str
    pid: int
    env: dict[str, str]          # KGENTS_* variables
```

### 2.3 Storage Protocols

Four protocols define the Left Hemisphere interface:

| Protocol | Purpose | Implementation |
|----------|---------|----------------|
| `IRelationalStore` | SQL operations | SQLiteRelationalStore |
| `IVectorStore` | Embedding storage | NumpyVectorStore |
| `IBlobStore` | Large binary data | FilesystemBlobStore |
| `ITelemetryStore` | Event logging | SQLiteTelemetryStore |

### 2.4 Lifecycle States

```python
class OperationMode(Enum):
    FULL = "full"           # Global + Project DB
    GLOBAL_ONLY = "global"  # ~/.local/share/kgents/membrane.db only
    LOCAL_ONLY = "local"    # .kgents/cortex.db only
    DB_LESS = "db_less"     # In-memory fallback (ephemeral)
```

**Graceful Degradation:**
- System ALWAYS works
- Capabilities scale with available infrastructure
- No hard failures—only reduced features

---

## Part III: Critical Enhancements from Critique

### 3.1 Active Inference (Surprise-Based Routing)

From the critique:
> "D-gents shouldn't just *store* data; they should generate *Predictions*."

**Implementation:**

```python
@dataclass
class PredictiveModel:
    alpha: float = 0.3  # Exponential smoothing factor
    predictions: dict[str, float]

    def predict(self, key: str) -> float:
        return self.predictions.get(key, 0.5)

    def update(self, key: str, actual: float) -> float:
        predicted = self.predict(key)
        surprise = abs(actual - predicted)
        self.predictions[key] = self.alpha * actual + (1 - self.alpha) * predicted
        return surprise
```

**Routing Logic:**
- **Low Surprise (expected):** Batch to Garden queue
- **High Surprise (novel):** Immediate dispatch + W-gent alert
- **Flashbulb Threshold:** Priority persistence for extreme surprise

### 3.2 Cryptographic Amnesia (Lethe Protocol)

From the critique:
> "Encrypt distinct memory 'epochs' with ephemeral keys. To 'compost' the raw data, simply delete the key."

**The Problem:** GDPR "Right to be Forgotten" conflicts with append-only event stores.

**The Solution:**

```python
@dataclass
class LetheEpoch:
    epoch_id: str
    key: bytes              # Ephemeral encryption key
    start_time: datetime
    end_time: datetime | None
    status: Literal["active", "sealed", "composted"]

class LetheStore:
    """
    Cryptographic amnesia implementation.

    - Events encrypted per-epoch
    - Composting = delete key (data becomes noise)
    - Statistics preserved via sketching
    """

    async def compost(self, epoch_id: str) -> CompostResult:
        epoch = self.epochs[epoch_id]

        # 1. Extract statistics via sketching
        stats = await self._sketch_epoch(epoch_id)

        # 2. Delete the encryption key
        del epoch.key
        epoch.status = "composted"

        # 3. Raw data is now high-entropy noise (unrecoverable)
        return CompostResult(
            epoch_id=epoch_id,
            stats_preserved=stats,
            bytes_forgotten=epoch.size,
        )
```

**Joy-Inducing Interpretation:**
> "You don't 'delete' the memory; you 'release the spirit' (the key) back into the void, leaving the 'body' (ciphertext) as compost."

### 3.3 Probabilistic Composting (Sketching)

From the critique:
> "Use Count-Min Sketch and T-Digest algorithms to compress raw events into statistical summaries."

```python
class CompostBin:
    """
    Sketching-based composting.

    Raw Logs (1GB) → Histogram + Quantiles (10KB)
    """

    async def compost(self, raw_events: list[Event]) -> NutrientBlock:
        sketch = CountMinSketch()
        digest = TDigest()

        for event in raw_events:
            sketch.add(event.semantic_hash)
            digest.add(event.numeric_value)

        return NutrientBlock(
            period=(raw_events[0].timestamp, raw_events[-1].timestamp),
            frequency_sketch=sketch.serialize(),
            quantile_digest=digest.serialize(),
            event_count=len(raw_events),
        )
```

### 3.4 The Dreaming Interface

From the critique:
> "Database optimization is not 'maintenance'; it is *Dreaming*."

```python
class IDreamer(Protocol):
    """
    Runs during system idle time (Hypnagogic state).
    """

    async def rem_cycle(self) -> DreamReport:
        """
        REM cycle operations:
        1. Re-index HNSW graphs (optimize vector search)
        2. Merge LSM tree segments (optimize relational storage)
        3. Propagate compost (Lifecycle management)
        4. Run predictive model retraining
        """
        ...
```

**Scheduling:**
```yaml
# infrastructure.yaml
dreaming:
  interval_hours: 24
  time_utc: "03:00"  # 3 AM UTC (low activity)
```

---

## Part IV: D-gent Integration

### 4.1 Backend Adapters

D-gents use Infrastructure via adapters:

```python
class InstanceDBVectorBackend:
    """
    D-gent VectorAgent backend using infra/IVectorStore.
    """

    def __init__(self, store: IVectorStore, embedder: Callable):
        self._store = store
        self._embedder = embedder

    async def add(self, id: str, state: S) -> None:
        embedding = self._embedder(state)
        await self._store.upsert(id, embedding, {"state": serialize(state)})

    async def search(self, query: S, limit: int) -> list[tuple[str, S, float]]:
        embedding = self._embedder(query)
        results = await self._store.search(embedding, limit)
        return [(r.id, deserialize(r.metadata["state"]), r.distance) for r in results]
```

### 4.2 UnifiedMemory.from_cortex()

```python
class UnifiedMemory(Generic[S]):
    @classmethod
    def from_cortex(
        cls,
        state: LifecycleState,
        config: MemoryConfig,
        namespace: str = "unified",
        embedder: Callable | None = None,
    ) -> UnifiedMemory[S]:
        """
        Create UnifiedMemory backed by Cortex infrastructure.

        This is the bridge between Infrastructure and Semantics.
        """
        memory = cls(VolatileAgent(_state=None), config)

        if state.storage_provider:
            memory._semantic_backend = InstanceDBVectorBackend(
                store=state.storage_provider.vector,
                embedder=embedder,
            )
            memory._temporal_backend = InstanceDBStreamBackend(
                store=state.storage_provider.telemetry,
            )

        return memory
```

---

## Part V: Implementation Phases

### Phase 1: Core Infrastructure ✅ COMPLETE (85 tests)

**What was implemented:**
- `protocols/cli/instance_db/interfaces.py` - Protocol definitions
- `protocols/cli/instance_db/storage.py` - StorageProvider + XDGPaths
- `protocols/cli/instance_db/lifecycle.py` - LifecycleManager
- `protocols/cli/instance_db/providers/sqlite.py` - SQLite implementations

**⚠️ REWORK REQUIRED for v2.0:**

| Component | Current State | Rework Needed |
|-----------|---------------|---------------|
| Location | `protocols/cli/instance_db/` | Move to `impl/claude/infra/` |
| Synapse | Not implemented | Add `synapse.py` with Active Inference |
| Ground | Implicit in storage.py | Extract to `ground.py` as bootstrap agent |
| Prediction | Not implemented | Add to Synapse |
| Composting | Basic pruning only | Add sketching + Lethe protocol |

### Phase 2: Synapse + Active Inference (~40 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `Synapse` class | Event bus with signal routing | 15 |
| `PredictiveModel` | Exponential smoothing predictor | 10 |
| Active Inference routing | High/low surprise paths | 10 |
| Metrics collection | Signal counts, surprise distribution | 5 |

**Deliverables:**
- `infra/synapse.py` (already created in v2.0 skeleton)
- Tests: `infra/_tests/test_synapse.py`

### Phase 3: D-gent Backend Adapters (~55 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `InstanceDBRelationalBackend` | Wrap IRelationalStore for SQLAgent | 15 |
| `InstanceDBVectorBackend` | Wrap IVectorStore for VectorAgent | 15 |
| `InstanceDBStreamBackend` | Wrap ITelemetryStore for StreamAgent | 15 |
| `UnifiedMemory.from_cortex()` | Factory method | 10 |

**Deliverables:**
- `agents/d/infra_backends.py`
- Updates to `agents/d/unified.py`

### Phase 4: Composting + Lethe Protocol (~45 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `CompostBin` | Sketching-based compression | 15 |
| `LetheStore` | Cryptographic amnesia | 15 |
| `NutrientBlock` | Compressed statistics | 10 |
| Integration with MemoryGarden | Lifecycle mapping | 5 |

**Deliverables:**
- `infra/compost.py`
- `infra/lethe.py`

### Phase 5: Dreaming + Maintenance (~30 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `IDreamer` protocol | Maintenance interface | 5 |
| `NightWatch` scheduler | REM cycle scheduling | 10 |
| Index optimization | HNSW reindexing | 5 |
| Compost propagation | Lifecycle transitions | 10 |

**Deliverables:**
- `infra/dreamer.py`

### Phase 6: Observability + Dashboard (~35 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `DgentObserver` | O-gent wrapper for D-gent ops | 15 |
| Panopticon integration | W-gent dashboard updates | 10 |
| Metrics export | Prometheus/OpenTelemetry | 10 |

**Deliverables:**
- Updates to `agents/o/`
- Updates to `agents/w/value_dashboard.py`

---

## Part VI: Migration Path

### 6.1 Phase 1 Rework Checklist

The following changes are needed to align Phase 1 with v2.0 architecture:

```
[ ] Create impl/claude/infra/ directory structure
    [x] __init__.py
    [x] ground.py (extract from storage.py)
    [x] synapse.py (new)
    [x] storage.py (adapt from protocols/cli/instance_db/storage.py)
    [x] lifecycle.py (adapt from protocols/cli/instance_db/lifecycle.py)
    [x] providers/__init__.py (bridge to existing providers)

[ ] Update imports across codebase
    [ ] protocols/cli/ should import from infra/
    [ ] agents/d/ adapters should use infra/ interfaces

[ ] Deprecate protocols/cli/instance_db/
    [ ] Keep as compatibility shim (imports from infra/)
    [ ] Add deprecation warnings
    [ ] Remove in next major version

[ ] Add missing functionality
    [ ] Synapse Active Inference (DONE in skeleton)
    [ ] Ground bootstrap agent (DONE in skeleton)
    [ ] Surprise threshold in config (DONE in skeleton)
```

### 6.2 Backward Compatibility

```python
# protocols/cli/instance_db/__init__.py (FUTURE)
"""
DEPRECATED: Use impl/claude/infra/ instead.

This module is a compatibility shim that will be removed in v3.0.
"""
import warnings
warnings.warn(
    "protocols/cli/instance_db is deprecated. Use impl/claude/infra/ instead.",
    DeprecationWarning,
    stacklevel=2,
)

from infra import *
```

---

## Part VII: Configuration (Infrastructure-as-Code)

### 7.1 Default Configuration

```yaml
# ~/.config/kgents/infrastructure.yaml
profile: local-canonical

providers:
  relational:
    type: sqlite
    connection: "${XDG_DATA_HOME}/kgents/membrane.db"
    wal_mode: true

  vector:
    type: numpy
    path: "${XDG_DATA_HOME}/kgents/vectors.json"
    dimensions: 384
    fallback: numpy-cosine
    threshold: 1000

  blob:
    type: filesystem
    path: "${XDG_DATA_HOME}/kgents/blobs"

  telemetry:
    type: sqlite
    connection: "${XDG_DATA_HOME}/kgents/telemetry.db"
    retention:
      hot_days: 30
      warm_days: 365
      compost_strategy: sketch

synapse:
  buffer_size: 1000
  batch_interval_ms: 100

inference:
  surprise_threshold: 0.5
  model: exponential_smoothing

dreaming:
  interval_hours: 24
  time_utc: "03:00"
```

### 7.2 Team/Cloud Configuration

```yaml
# infrastructure.yaml (team deployment)
profile: team-cloud

providers:
  relational:
    type: postgres
    connection: "${DATABASE_URL}"

  vector:
    type: qdrant
    connection: "${QDRANT_URL}"
    dimensions: 1536  # OpenAI embedding size

  blob:
    type: s3
    bucket: "${S3_BUCKET}"
    prefix: "kgents/"

  telemetry:
    type: clickhouse
    connection: "${CLICKHOUSE_URL}"
```

---

## Part VIII: Open Questions (Resolved)

### 8.1 Transaction Boundaries → Eventual Consistency

From the critique:
> "You cannot have ACID across the Unified Cortex. You need Sagas or Eventual Consistency by design."

**Resolution:** Accept eventual consistency. The Synapse provides ordering guarantees within a single signal, but cross-signal consistency is eventual.

### 8.2 Namespace Collision → Prefixed Isolation

**Resolution:** All D-gent operations include namespace prefix:
- Tables: `{namespace}_shapes`, `{namespace}_dreams`
- Vectors: `{namespace}:{id}`
- Events: `dgent.{namespace}.{event_type}`

### 8.3 Performance → Batching + Caching

**Resolution:**
- Low-surprise signals are batched (Synapse)
- Hot data uses `CachedAgent` pattern (D-gent)
- Cold data uses async fire-and-forget

---

## Appendix A: Test Summary

| Phase | Tests | Status |
|-------|-------|--------|
| 1. Core Infrastructure | 85 | ✅ Complete (needs migration) |
| 2. Synapse + Active Inference | ~40 | ⏳ Pending |
| 3. D-gent Backend Adapters | ~55 | ⏳ Pending |
| 4. Composting + Lethe | ~45 | ⏳ Pending |
| 5. Dreaming + Maintenance | ~30 | ⏳ Pending |
| 6. Observability + Dashboard | ~35 | ⏳ Pending |
| **Total** | **~290** | |

---

## Appendix B: The Cortical Vision

```
                    ┌─────────────────────────────────────────┐
                    │           THE UNIFIED CORTEX            │
                    │                                         │
                    │  "One memory, many modes, infinite joy" │
                    │                                         │
                    │    Predicts · Forgets · Dreams          │
                    └─────────────────────────────────────────┘
```

*"The cortex remembers. The cortex forgets. The cortex dreams. The cortex grows."*
