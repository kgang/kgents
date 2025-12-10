# Instance DB Implementation Plan v3.0: The Bicameral Engine

## The Unified Cortex: Infrastructure × Semantics × Nervous System

**Status:** Design Document v3.0
**Date:** 2025-12-10
**Location:** `protocols/cli/instance_db/` (Phase 1 OPERATIONAL) → `impl/claude/infra/` (Future)

---

## Executive Summary

This document specifies the **Bicameral Engine**—an evolution of the Unified Cortex that addresses three critical risks identified in architectural review:

1. **Split-Brain Consistency Risk** → Coherency Protocol
2. **Synapse Latency Trap** → Spinal Cord (Reflex Layer)
3. **Interrupt Problem in Dreaming** → Lucid Dreaming + Interruptible Maintenance

The Bicameral Engine introduces:
- **Spinal Cord**: Fast-path for low-value signals (bypass the brain)
- **Hippocampus**: Short-term consolidation before long-term storage
- **Coherency Protocol**: Cross-hemisphere validation preventing Ghost Memories
- **Lucid Dreaming**: Interactive optimization that asks clarifying questions
- **Schema Neurogenesis**: Database schema that grows from experience

From the original critique:
> "A cortex doesn't just store; it predicts, forgets, and hallucinates."

We now add:
> "A cortex also has reflexes, short-term memory, and learns new structures."

---

## Part I: Current State (Phase 1 OPERATIONAL)

### 1.1 What's Already Working

**Location**: `protocols/cli/instance_db/` (85 tests passing)

| Component | File | Status | Tests |
|-----------|------|--------|-------|
| Interfaces | `interfaces.py` | ✅ Operational | 16 |
| Storage Provider | `storage.py` | ✅ Operational | 16 |
| Lifecycle Manager | `lifecycle.py` | ✅ Operational | 20 |
| SQLite Provider | `providers/sqlite.py` | ✅ Operational | 33 |

**CLI Integration** (AUTO-BOOTSTRAP):
- `kgents <command>` auto-bootstraps cortex on startup
- Instance registration + telemetry logging
- Graceful shutdown with `--no-bootstrap` escape hatch
- First-run messaging (Transparent Infrastructure principle)
- Wipe command with confirmation (`kgents wipe local|global|all`)

### 1.2 Architecture Diagram (Current)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE UNIFIED CORTEX v2.0                           │
├──────────────────────────┬─────────────────┬────────────────────────────────┤
│     LEFT HEMISPHERE      │ CORPUS CALLOSUM │       RIGHT HEMISPHERE          │
│     (The Bookkeeper)     │   (Synapse)     │       (The Poet)                │
├──────────────────────────┼─────────────────┼────────────────────────────────┤
│  • ACID transactions     │ • Signal routing│  • Approximate similarity       │
│  • Exact queries         │ • (PLANNED)     │  • Semantic voids              │
│  • Relational schema     │                 │  • Geodesics (paths)           │
│  • Instance tracking     │                 │  • Memory Garden               │
├──────────────────────────┼─────────────────┼────────────────────────────────┤
│  protocols/cli/          │ (Phase 2)       │  agents/d/                     │
│  instance_db/            │                 │  └── unified.py                │
│  └── storage.py          │                 │  └── manifold.py               │
│  └── lifecycle.py        │                 │  └── garden.py                 │
└──────────────────────────┴─────────────────┴────────────────────────────────┘
```

---

## Part II: The Bicameral Engine (v3.0 Enhancements)

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE BICAMERAL ENGINE v3.0                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │   SIGNALS    │                                                           │
│  │  (All Input) │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                    SPINAL CORD (Reflex Layer)                     │       │
│  │  • Heartbeats → Fast Store (bypass brain)                        │       │
│  │  • Raw I/O    → Fast Store (bypass brain)                        │       │
│  │  • CPU metrics → Fast Store (bypass brain)                       │       │
│  │  • Semantic signals → ↓ Ascending pathway to Cortex              │       │
│  └──────────────────────────────────────┬───────────────────────────┘       │
│                                          │                                   │
│         ┌────────────────────────────────▼────────────────────────────┐     │
│         │                        HIPPOCAMPUS                           │     │
│         │              (Short-Term Consolidation)                      │     │
│         │  • Session context (in-memory/Redis)                        │     │
│         │  • "Day log" - holds recent memories                        │     │
│         │  • Flushes to Cortex during Dreaming                        │     │
│         └────────────────────────────────┬────────────────────────────┘     │
│                                          │                                   │
│  ┌───────────────────────────────────────▼──────────────────────────────┐   │
│  │                           SYNAPSE (Event Bus)                         │   │
│  │                                                                       │   │
│  │  • Active Inference: surprise = |actual - predicted|                 │   │
│  │  • High surprise → Fast path (immediate dispatch)                    │   │
│  │  • Low surprise  → Batch path (garden queue)                         │   │
│  │  • Flashbulb threshold → Priority persistence                        │   │
│  └───────────────────────┬───────────────────────────┬──────────────────┘   │
│                          │                           │                       │
│         ┌────────────────▼────────┐     ┌───────────▼─────────────────┐    │
│         │    LEFT HEMISPHERE      │     │     RIGHT HEMISPHERE         │    │
│         │    (The Bookkeeper)     │◄───►│     (The Poet)               │    │
│         ├─────────────────────────┤     ├─────────────────────────────┤    │
│         │ • SQLite (ACID)         │     │ • Vector Store (Semantic)   │    │
│         │ • Instance tracking     │  C  │ • Embedding search          │    │
│         │ • Schema (rigid)        │  O  │ • Fuzzy matching            │    │
│         │                         │  H  │                              │    │
│         │ • Source of truth for   │  E  │ • Pointers to Left          │    │
│         │   "what exists"         │  R  │ • Ghost detection           │    │
│         │                         │  E  │                              │    │
│         │                         │  N  │                              │    │
│         │                         │  C  │                              │    │
│         │                         │  Y  │                              │    │
│         └─────────────────────────┘     └─────────────────────────────┘    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        LUCID DREAMER                                  │   │
│  │  • Interruptible maintenance (yields to High Surprise)               │   │
│  │  • Ambiguity resolution → Morning Briefing queue                     │   │
│  │  • Schema Neurogenesis → Proposes new columns from patterns          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Critical Risk Mitigations

#### Risk 1: Split-Brain Consistency

**Problem:** Left Hemisphere (SQL) and Right Hemisphere (Vector) can diverge.
**Failure Mode:** Vector search returns pointer to deleted/changed SQL row.

**Solution: Coherency Protocol**

```python
class BicameralMemory:
    """
    Cross-hemisphere recall with coherency validation.
    """

    async def recall(self, query: str) -> list[Fact]:
        # 1. Right Hemisphere finds relevant IDs (semantic search)
        vector_results = await self.right_hemi.search(query)
        ids = [r.id for r in vector_results]

        # 2. Left Hemisphere validates reality (source of truth)
        rows = await self.left_hemi.fetch_by_ids(ids)

        valid_memories = []
        for vec_result in vector_results:
            row = rows.get(vec_result.id)

            if row is None:
                # Ghost Memory: Exists in Vector, deleted in SQL
                # Self-healing: Remove stale vector entry
                await self._heal_ghost(vec_result.id)
                continue

            # 3. Staleness Check: Has the row changed since embedding?
            if row.content_hash != vec_result.metadata.get('content_hash'):
                # Flag for re-embedding (don't block recall)
                self._flag_for_reembedding(row.id)

            valid_memories.append(row)

        return valid_memories

    async def _heal_ghost(self, ghost_id: str) -> None:
        """Remove orphaned vector entry (self-healing)."""
        await self.right_hemi.delete(ghost_id)
        await self.telemetry.log("memory.ghost_healed", {"id": ghost_id})
```

#### Risk 2: Synapse Latency Trap

**Problem:** Running `predictive_model.evaluate()` on every signal creates bottleneck.
**Failure Mode:** 10,000 telemetry signals × 1ms each = 10 seconds blocking.

**Solution: Spinal Cord (Reflex Layer)**

```python
class NervousSystem:
    """
    Two-tier signal routing: Reflexes vs. Cortical processing.
    """

    # Signals that bypass the brain entirely (O(1) routing)
    REFLEX_PATTERNS = {
        "telemetry.heartbeat",
        "io.raw.read",
        "io.raw.write",
        "system.cpu_metrics",
        "system.memory_metrics",
    }

    async def transmit(self, signal: Signal) -> None:
        # 1. Spinal Reflex: Pattern match (O(1))
        if signal.type in self.REFLEX_PATTERNS:
            # Bypass cortex, go straight to fast store
            return await self.fast_store.append(signal)

        # 2. Ascending Pathway: Send to Synapse for cortical processing
        return await self.cortex.synapse.fire(signal)
```

**Configuration:**

```yaml
# infrastructure.yaml
nervous_system:
  spinal_reflexes:
    - "telemetry.heartbeat"
    - "io.raw.read"
    - "io.raw.write"
    - "system.cpu_metrics"
    - "system.memory_metrics"
```

#### Risk 3: Interrupt Problem in Dreaming

**Problem:** Maintenance at 3 AM blocks if user starts urgent session at 3:05 AM.
**Failure Mode:** Database locked during re-indexing; system unresponsive.

**Solution: Interruptible Lucid Dreaming**

```python
class LucidDreamer:
    """
    Interruptible maintenance with ambiguity resolution.
    """

    def __init__(self, synapse: Synapse, interrupt_check_ms: int = 100):
        self._synapse = synapse
        self._interrupt_check_ms = interrupt_check_ms
        self._morning_briefing: list[Question] = []

    async def rem_cycle(self) -> DreamReport:
        """
        REM cycle with interrupt checks.
        """
        report = DreamReport()

        # 1. Interruptible re-indexing (chunked)
        async for chunk in self._chunked_reindex():
            # Check for high-surprise signal (user activity)
            if await self._should_interrupt():
                report.interrupted = True
                report.reason = "High-surprise signal detected"
                return report

            await self._process_chunk(chunk)
            report.chunks_processed += 1

        # 2. Lucid phase: Identify ambiguities
        clusters = await self._find_ambiguous_clusters()
        for cluster in clusters:
            question = self._formulate_question(cluster)
            self._morning_briefing.append(question)

        # 3. Schema Neurogenesis: Detect recurring patterns
        migrations = await self._propose_schema_migrations()
        report.proposed_migrations = migrations

        return report

    async def _should_interrupt(self) -> bool:
        """Check if high-surprise signal arrived."""
        recent = await self._synapse.peek_recent(
            window_ms=self._interrupt_check_ms
        )
        return any(s.surprise > self._flashbulb_threshold for s in recent)

    async def _chunked_reindex(self):
        """Yield index chunks for interruptible processing."""
        # Use PRAGMA incremental_vacuum instead of blocking VACUUM
        # Chunk vector re-indexing into small batches
        ...
```

### 2.3 The Hippocampus (Short-Term Consolidation)

**Problem:** Jumping from Synapse directly to Long-Term Storage loses session context.
**Solution:** High-speed ephemeral layer that holds the "Day Log."

```python
class Hippocampus:
    """
    Short-term memory consolidation.

    Holds current session context before encoding to long-term storage.
    Flushes to Cortex during Dreaming.
    """

    def __init__(self, backend: str = "memory"):
        # In-memory by default, Redis for distributed
        self._store = self._create_backend(backend)
        self._current_epoch: LetheEpoch | None = None

    async def remember(self, signal: Signal) -> None:
        """Store in short-term memory."""
        await self._store.append(signal)

    async def flush_to_cortex(self, cortex: Cortex) -> FlushResult:
        """
        Transfer short-term memories to long-term storage.
        Called during Dreaming.
        """
        signals = await self._store.drain()

        for signal in signals:
            await cortex.synapse.fire(signal, bypass_hippocampus=True)

        # Create Lethe Epoch for this day's memories
        self._current_epoch = await cortex.lethe.seal_epoch()

        return FlushResult(
            signals_transferred=len(signals),
            epoch_id=self._current_epoch.epoch_id,
        )
```

### 2.4 Schema Neurogenesis

**Concept:** The database schema should grow based on the agent's experiences.

```python
class SchemaNeurogenesis:
    """
    Propose schema migrations based on detected patterns.
    """

    async def analyze_blobs(self) -> list[MigrationProposal]:
        """
        Find JSON blobs with recurring structure and propose columns.
        """
        proposals = []

        # Find all JSON columns
        json_columns = await self._find_json_columns()

        for table, column in json_columns:
            # Sample recent rows
            samples = await self._sample_json_values(table, column, limit=100)

            # Detect common keys
            key_frequency = Counter()
            for sample in samples:
                for key in sample.keys():
                    key_frequency[key] += 1

            # If key appears in >80% of samples, propose column
            for key, count in key_frequency.items():
                if count / len(samples) > 0.8:
                    proposals.append(MigrationProposal(
                        table=table,
                        action="add_column",
                        column_name=key,
                        column_type=self._infer_type(samples, key),
                        confidence=count / len(samples),
                    ))

        return proposals
```

---

## Part III: Implementation Phases (Revised)

### Phase 1: Core Infrastructure ✅ COMPLETE (85 tests)

**Status:** OPERATIONAL
**Location:** `protocols/cli/instance_db/`

Already implemented:
- `interfaces.py` - IRelationalStore, IVectorStore, IBlobStore, ITelemetryStore
- `storage.py` - StorageProvider, XDGPaths, InfrastructureConfig
- `lifecycle.py` - LifecycleManager, OperationMode, quick_bootstrap
- `providers/sqlite.py` - SQLite + Numpy + Filesystem implementations

CLI Integration:
- Auto-bootstrap on `kgents` command start
- `kgents wipe local|global|all` with confirmation
- Transparent Infrastructure messaging (first-run, verbose, degraded mode)

### Phase 1.5: Spinal Cord (NEW) (~20 tests)

**Priority:** HIGH (prevents Synapse latency trap)

| Task | Description | Tests |
|------|-------------|-------|
| `NervousSystem` class | Two-tier routing | 8 |
| Reflex pattern matching | O(1) bypass logic | 6 |
| Fast store integration | Direct to telemetry | 6 |

**Deliverables:**
- `protocols/cli/instance_db/nervous.py`
- Configuration: `spinal_reflexes` in infrastructure.yaml

### Phase 2: Synapse + Active Inference (~40 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `Synapse` class | Event bus with signal routing | 15 |
| `PredictiveModel` | O(1) exponential smoothing (NOT heavy ML) | 10 |
| Active Inference routing | High/low surprise paths | 10 |
| Metrics collection | Signal counts, surprise distribution | 5 |

**Constraint:** PredictiveModel MUST be O(1) or O(log n). Use T-Digest for statistics.

**Deliverables:**
- `protocols/cli/instance_db/synapse.py`
- Tests: `_tests/test_synapse.py`

### Phase 2.5: Hippocampus (NEW) (~25 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `Hippocampus` class | Short-term consolidation | 10 |
| Memory backend (in-memory) | Default implementation | 5 |
| Flush to cortex | Transfer to long-term | 5 |
| Lethe Epoch creation | Seal day's memories | 5 |

**Deliverables:**
- `protocols/cli/instance_db/hippocampus.py`
- Configuration: `hippocampus.flush_strategy` in infrastructure.yaml

### Phase 3: D-gent Backend Adapters + Coherency (~70 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `InstanceDBVectorBackend` | Wrap IVectorStore | 15 |
| `InstanceDBRelationalBackend` | Wrap IRelationalStore | 15 |
| `BicameralMemory` | Cross-hemisphere recall | 15 |
| **Coherency Protocol** | Ghost detection + healing | 15 |
| `UnifiedMemory.from_cortex()` | Factory method | 10 |

**Critical:** Implement Ghost Memory detection and self-healing.

**Deliverables:**
- `agents/d/infra_backends.py`
- `agents/d/bicameral.py`

### Phase 4: Composting + Lethe Protocol (~45 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `CompostBin` | Sketching-based compression | 15 |
| `LetheStore` | Cryptographic amnesia | 15 |
| `NutrientBlock` | Compressed statistics | 10 |
| Integration with MemoryGarden | Lifecycle mapping | 5 |

**Deliverables:**
- `protocols/cli/instance_db/compost.py`
- `protocols/cli/instance_db/lethe.py`

### Phase 5: Lucid Dreaming + Neurogenesis (~50 tests)

| Task | Description | Tests |
|------|-------------|-------|
| `LucidDreamer` | Interruptible maintenance | 15 |
| Interrupt checking | Yield to high-surprise | 10 |
| Ambiguity resolution | Morning Briefing queue | 10 |
| `SchemaNeurogenesis` | Propose schema migrations | 10 |
| `NightWatch` scheduler | REM cycle scheduling | 5 |

**Deliverables:**
- `protocols/cli/instance_db/dreamer.py`
- `protocols/cli/instance_db/neurogenesis.py`

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

## Part IV: Configuration (Infrastructure-as-Code)

### 4.1 Full Configuration Schema

```yaml
# ~/.config/kgents/infrastructure.yaml
profile: local-canonical

# === NERVOUS SYSTEM (Phase 1.5) ===
nervous_system:
  spinal_reflexes:
    - "telemetry.heartbeat"
    - "io.raw.read"
    - "io.raw.write"
    - "system.cpu_metrics"
    - "system.memory_metrics"

# === HIPPOCAMPUS (Phase 2.5) ===
hippocampus:
  type: "memory"  # or "redis" for distributed
  flush_strategy: "on_sleep"  # Flush to disk when session ends
  max_size_mb: 100

# === SYNAPSE (Phase 2) ===
synapse:
  buffer_size: 1000
  batch_interval_ms: 100

# === ACTIVE INFERENCE (Phase 2) ===
inference:
  surprise_threshold: 0.5
  flashbulb_threshold: 0.9
  model: exponential_smoothing
  # CONSTRAINT: Must be O(1) - no heavy ML models here

# === DREAMING (Phase 5) ===
dreaming:
  mode: "lucid"  # Enable interactive ambiguity resolution
  neurogenesis: true  # Allow suggesting schema changes
  interruption_check_ms: 100  # Check for user activity during maintenance
  interval_hours: 24
  time_utc: "03:00"

# === PROVIDERS (Phase 1 - OPERATIONAL) ===
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
    threshold: 1000  # Switch to sqlite-vec above this

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

# === COHERENCY (Phase 3) ===
coherency:
  ghost_healing: true  # Auto-remove orphaned vectors
  staleness_check: true  # Flag stale embeddings for refresh
  content_hash_field: "content_hash"
```

---

## Part V: Test Summary

| Phase | Tests | Status |
|-------|-------|--------|
| 1. Core Infrastructure | 85 | ✅ Complete |
| 1.5 Spinal Cord | ~20 | ⏳ NEW |
| 2. Synapse + Active Inference | ~40 | ⏳ Pending |
| 2.5 Hippocampus | ~25 | ⏳ NEW |
| 3. D-gent Adapters + Coherency | ~70 | ⏳ Pending (expanded) |
| 4. Composting + Lethe | ~45 | ⏳ Pending |
| 5. Lucid Dreaming + Neurogenesis | ~50 | ⏳ Pending (expanded) |
| 6. Observability + Dashboard | ~35 | ⏳ Pending |
| **Total** | **~370** | |

---

## Part VI: Migration Path from Current State

### 6.1 Immediate Actions (No Breaking Changes)

These can be implemented without modifying existing code:

1. **Add `nervous.py`** - Spinal Cord layer wraps existing lifecycle
2. **Add `hippocampus.py`** - In-memory session context
3. **Add config sections** - New YAML keys are ignored by existing code

### 6.2 Phase 3 Breaking Changes

When implementing Coherency Protocol:

1. **Vector metadata must include `content_hash`**
   - Migration: Backfill existing vectors with null hash (skip staleness check)

2. **Ghost healing requires vector delete capability**
   - Already implemented in `NumpyVectorStore.delete()`

### 6.3 Future Location Migration

Eventually move from `protocols/cli/instance_db/` to `impl/claude/infra/`:

```python
# protocols/cli/instance_db/__init__.py (FUTURE)
"""
DEPRECATED: Use impl/claude/infra/ instead.
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

## Part VII: The Bicameral Vision

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE BICAMERAL ENGINE v3.0                            │
│                                                                              │
│     "I dreamt about our project last night, and I realized                  │
│      I'm confused about X. Can you help me understand?"                     │
│                                                                              │
│     Reflexes · Remembers · Forgets · Dreams · Learns · Grows                │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The Spinal Cord** keeps the system responsive by routing noise away from the brain.

**The Hippocampus** holds the day's memories, ready for consolidation.

**The Synapse** routes signals based on surprise—novel information gets priority.

**The Coherency Protocol** ensures the two hemispheres stay synchronized.

**The Lucid Dreamer** doesn't just maintain—it reflects, questions, and proposes new structures.

*"The cortex remembers. The cortex forgets. The cortex dreams. The cortex grows."*

---

## Appendix A: Key Algorithms

### A.1 Exponential Smoothing (O(1))

```python
def update(self, key: str, actual: float) -> float:
    """O(1) prediction update."""
    predicted = self.predictions.get(key, 0.5)
    surprise = abs(actual - predicted)
    self.predictions[key] = self.alpha * actual + (1 - self.alpha) * predicted
    return surprise
```

### A.2 T-Digest for Quantiles

Use `tdigest` library for streaming quantile estimation:

```python
from tdigest import TDigest

digest = TDigest()
for value in stream:
    digest.update(value)

p50 = digest.percentile(50)
p99 = digest.percentile(99)
```

### A.3 Count-Min Sketch for Frequency

Use `probables` or similar for frequency estimation:

```python
from probables import CountMinSketch

sketch = CountMinSketch(width=1000, depth=5)
for item in stream:
    sketch.add(item)

count = sketch.check(item)  # Approximate frequency
```

---

## Appendix B: References

1. **Active Inference**: Friston, K. (2010). "The free-energy principle: a unified brain theory?"
2. **Cryptographic Amnesia**: "Cryptographic Deletion" in secure data systems
3. **T-Digest**: Dunning, T. & Ertl, O. (2019). "Computing Extremely Accurate Quantiles Using t-Digests"
4. **Count-Min Sketch**: Cormode, G. & Muthukrishnan, S. (2005). "An improved data stream summary: the count-min sketch"
