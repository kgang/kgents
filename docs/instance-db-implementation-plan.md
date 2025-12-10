# Instance DB Implementation Plan: ~/.kgents Canonical Database

**Status:** Specification v2.0 (Fluid Cortex)
**Date:** 2025-12-10
**Related:** `spec/protocols/membrane.md`, `spec/protocols/config.md`, `spec/protocols/umwelt.md`

---

## Executive Summary

This plan specifies the **canonical instance database** for kgents, implemented at `~/.kgents/`. The database serves as the **Pocket Cortex**—the persistent, local-first memory that spans all kgent instances across projects.

**v2.0 "Fluid Cortex"** adds:
- **Storage Provider Abstraction**: Backend-agnostic persistence layer
- **Infrastructure as Code (IaC)**: Declarative `infrastructure.yaml` configuration
- **Write-Ahead Queue (WAQ)**: Dedicated writer daemon for concurrency
- **Split Database Architecture**: Separate state/vectors from telemetry
- **Dynamic Vector Dimensions**: Model registry for embedding flexibility
- **XDG Compliance**: Proper directory standards (config/data/cache separation)
- **Future-Forward Design**: Migration path to S3, Google Drive, Obsidian, managed DBs, K8s, Helm, Terraform

### Core Principles Applied

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Single canonical location; XDG-compliant directory structure |
| **Composable** | Repository Pattern + Provider abstraction enables any backend |
| **Ethical** | Local-first default; no network unless explicitly configured |
| **Generative** | ORM models (SQLModel) generate dialect-agnostic SQL |
| **Heterarchical** | Per-project `.kgents/` + global `~/.kgents/` with permeability protocol |
| **Visibility** | O-gent integration from day one; split telemetry DB |
| **Safety** | Atomic writes, WAQ for concurrency, corruption recovery |
| **Reliability** | Alembic migrations, versioned schema, backup lifecycle |
| **Cleanup** | Automatic pruning, vacuum cycles, retention policies |

---

## Part I: Architecture Overview

### 1.1 Directory Structure (XDG Compliant)

```
~/.config/kgents/                       # Configuration (XDG_CONFIG_HOME)
├── infrastructure.yaml                 # Storage backend configuration
├── sanctuary.yaml                      # Paths excluded from observation
└── profiles/                           # Named configuration profiles
    ├── local.yaml                      # Default local profile
    └── team-aws.yaml                   # Example cloud profile

~/.local/share/kgents/                  # Data (XDG_DATA_HOME)
├── membrane.db                         # Core SQLite (state + vectors)
├── membrane.db-wal                     # WAL file (auto-managed)
├── membrane.db-shm                     # Shared memory file (auto-managed)
├── telemetry.db                        # Events/logs (separate for rotation)
└── backups/                            # Automatic backups
    ├── membrane.db.2025-12-10.bak      # Daily backups (7-day retention)
    └── membrane.db.weekly.bak          # Weekly backup (4-week retention)

~/.cache/kgents/                        # Cache/Logs (XDG_CACHE_HOME)
├── locks/                              # Process locks
│   └── membrane.lock                   # Advisory file lock
├── logs/                               # Operational logs
│   ├── vacuum.log                      # Cleanup operation logs
│   └── writer.log                      # WriterDaemon logs
└── embeddings/                         # Cached embeddings (regeneratable)

.kgents/                                # Per-project cortex (in project root)
├── cortex.db                           # Project-specific database
├── config.yaml                         # Project configuration
├── tongues/                            # G-gent domain languages
├── flows/                              # Flowfile compositions
└── state/                              # Agent state files
```

### 1.2 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                    │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │  CLI/MCP    │  │   Membrane  │  │   Mirror    │  │   O-gent    │       │
│   │  Commands   │  │   Protocol  │  │   Protocol  │  │   Observer  │       │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                         INSTANCE MANAGER                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  InstanceManager                                                     │   │
│   │  - Registration     - Health monitoring    - WriterDaemon           │   │
│   │  - Lifecycle        - Cleanup coordination - Write-Ahead Queue      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                         REPOSITORY LAYER (NEW)                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  IRelationalStore     IVectorStore     IBlobStore     ITelemetryStore│   │
│   │  (instances, shapes)  (embeddings)     (large state)  (events, logs) │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                         PROVIDER LAYER (NEW)                                 │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│   │SQLiteProvider│ │PostgresProvider│ │QdrantProvider│ │S3Provider  │      │
│   │(default)     │ │(team/cloud)  │ │(vectors)     │ │(blobs)      │      │
│   └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘      │
├─────────────────────────────────────────────────────────────────────────────┤
│                         STORAGE BACKENDS                                     │
│   SQLite+vec │ PostgreSQL+pgvector │ Qdrant │ S3/GCS │ ClickHouse │ ...   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Infrastructure as Code (IaC)

Storage backends are configured declaratively, not hardcoded:

**Scenario A: Local First (Default)**
```yaml
# ~/.config/kgents/infrastructure.yaml
profile: local-canonical

providers:
  relational:
    type: sqlite
    connection: "${XDG_DATA_HOME}/kgents/membrane.db"
    wal_mode: true

  vector:
    type: sqlite-vec
    fallback: numpy-cosine  # Graceful degradation if extension fails

  telemetry:
    type: sqlite
    connection: "${XDG_DATA_HOME}/kgents/telemetry.db"
    retention_days: 30

  blob:
    type: filesystem
    path: "${XDG_DATA_HOME}/kgents/blobs"
```

**Scenario B: Team/Cloud (Future)**
```yaml
# ~/.config/kgents/profiles/team-aws.yaml
profile: team-cortex-aws

providers:
  relational:
    type: postgres
    connection: "${env:POSTGRES_CONNECTION_STRING}"  # AWS RDS

  vector:
    type: qdrant
    host: "${env:QDRANT_HOST}"
    collection: "shared_memory"

  telemetry:
    type: clickhouse
    host: "${env:CLICKHOUSE_HOST}"

  blob:
    type: s3
    bucket: "${env:S3_BUCKET}"
    prefix: "kgents/state/"
```

**Scenario C: Obsidian Integration (Future)**
```yaml
# ~/.config/kgents/profiles/obsidian.yaml
profile: obsidian-sync

providers:
  relational:
    type: sqlite
    connection: "${OBSIDIAN_VAULT}/.kgents/membrane.db"

  blob:
    type: obsidian
    vault: "${OBSIDIAN_VAULT}"
    folder: "_kgents"
```

---

## Part II: Repository Pattern (Storage Abstraction)

### 2.1 Core Interfaces

The application never knows which database it's talking to:

```python
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from contextlib import asynccontextmanager


class IRelationalStore(ABC):
    """
    Abstracts SQLite, PostgreSQL, MySQL, or any SQL database.

    All agent state, shapes, and dreams go through this interface.
    """

    @abstractmethod
    async def execute(self, query: str, params: dict[str, Any] = None) -> int:
        """Execute query, return rows affected."""
        ...

    @abstractmethod
    async def fetch_one(self, query: str, params: dict[str, Any] = None) -> dict | None:
        """Fetch single row as dict."""
        ...

    @abstractmethod
    async def fetch_all(self, query: str, params: dict[str, Any] = None) -> list[dict]:
        """Fetch all rows as list of dicts."""
        ...

    @abstractmethod
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["IRelationalStore"]:
        """Begin transaction, auto-commit on success, rollback on exception."""
        ...


class IVectorStore(ABC):
    """
    Abstracts sqlite-vec, pgvector, Qdrant, Pinecone, or numpy fallback.

    Semantic embeddings for shapes, memories, and intents.
    """

    @abstractmethod
    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict[str, Any]
    ) -> None:
        """Insert or update vector with metadata."""
        ...

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter: dict[str, Any] = None
    ) -> list[dict]:
        """Search for similar vectors, return with distance and metadata."""
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete vector by ID."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Current embedding dimensions (from model registry)."""
        ...


class IBlobStore(ABC):
    """
    Abstracts filesystem, S3, GCS, MinIO, or Obsidian.

    Large state dumps, backup archives, exported artifacts.
    """

    @abstractmethod
    async def put(self, key: str, data: bytes, content_type: str = None) -> str:
        """Store blob, return URL/path."""
        ...

    @abstractmethod
    async def get(self, key: str) -> bytes | None:
        """Retrieve blob by key."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete blob."""
        ...

    @abstractmethod
    async def list(self, prefix: str = "") -> list[str]:
        """List keys with prefix."""
        ...


class ITelemetryStore(ABC):
    """
    Abstracts SQLite, ClickHouse, or time-series databases.

    High-velocity event logs (separate from state for independent rotation).
    """

    @abstractmethod
    async def append(self, events: list[dict]) -> int:
        """Batch append events, return count."""
        ...

    @abstractmethod
    async def query(
        self,
        event_type: str = None,
        since: str = None,
        until: str = None,
        limit: int = 1000
    ) -> list[dict]:
        """Query events with filters."""
        ...

    @abstractmethod
    async def prune(self, older_than_days: int) -> int:
        """Delete old events, return count deleted."""
        ...
```

### 2.2 Storage Provider (Dependency Injection)

```python
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class StorageProvider:
    """
    Unified access to all storage backends.

    Instantiated from infrastructure.yaml at startup.
    Injected into InstanceManager, MembraneAgent, etc.
    """
    relational: IRelationalStore
    vector: IVectorStore
    blob: IBlobStore
    telemetry: ITelemetryStore

    @classmethod
    async def from_config(cls, config_path: Path = None) -> "StorageProvider":
        """
        Load infrastructure.yaml and instantiate appropriate providers.

        Falls back to local SQLite if no config exists.
        """
        config_path = config_path or Path.home() / ".config/kgents/infrastructure.yaml"

        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
        else:
            config = cls._default_config()

        return cls(
            relational=await cls._create_relational(config["providers"]["relational"]),
            vector=await cls._create_vector(config["providers"]["vector"]),
            blob=await cls._create_blob(config["providers"]["blob"]),
            telemetry=await cls._create_telemetry(config["providers"]["telemetry"]),
        )

    @staticmethod
    def _default_config() -> dict:
        """Default local-first configuration."""
        data_home = Path.home() / ".local/share/kgents"
        return {
            "profile": "local-canonical",
            "providers": {
                "relational": {"type": "sqlite", "connection": str(data_home / "membrane.db")},
                "vector": {"type": "sqlite-vec", "fallback": "numpy-cosine"},
                "blob": {"type": "filesystem", "path": str(data_home / "blobs")},
                "telemetry": {"type": "sqlite", "connection": str(data_home / "telemetry.db")},
            }
        }
```

### 2.3 SQLite Provider Implementation (Default)

```python
import aiosqlite
from filelock import FileLock  # Cross-platform locking


class SQLiteRelationalStore(IRelationalStore):
    """
    SQLite implementation of relational store.

    Features:
    - WAL mode for concurrent reads
    - FileLock for cross-process write coordination
    - Automatic schema migration via Alembic
    """

    def __init__(self, db_path: Path, lock_path: Path = None):
        self.db_path = db_path
        self._lock = FileLock(lock_path or db_path.with_suffix(".lock"))
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Initialize connection with WAL mode."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row

        # Enable WAL and foreign keys
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA synchronous=NORMAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")

    async def execute(self, query: str, params: dict = None) -> int:
        with self._lock:
            cursor = await self._conn.execute(query, params or {})
            await self._conn.commit()
            return cursor.rowcount

    async def fetch_one(self, query: str, params: dict = None) -> dict | None:
        cursor = await self._conn.execute(query, params or {})
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def fetch_all(self, query: str, params: dict = None) -> list[dict]:
        cursor = await self._conn.execute(query, params or {})
        return [dict(row) for row in await cursor.fetchall()]

    @asynccontextmanager
    async def transaction(self):
        """Transaction with automatic rollback on exception."""
        with self._lock:
            await self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self
                await self._conn.commit()
            except Exception:
                await self._conn.rollback()
                raise


class SQLiteVecStore(IVectorStore):
    """
    sqlite-vec implementation with numpy fallback.

    Features:
    - HNSW index for fast ANN search
    - Dynamic dimensions from model registry
    - Graceful fallback to numpy cosine similarity
    """

    def __init__(self, db_path: Path, model_registry: "ModelRegistry"):
        self.db_path = db_path
        self._registry = model_registry
        self._use_vec = self._check_vec_available()

    def _check_vec_available(self) -> bool:
        """Check if sqlite-vec extension is loadable."""
        try:
            import sqlite_vec
            return True
        except ImportError:
            return False

    @property
    def dimensions(self) -> int:
        return self._registry.current_dimensions

    async def search(self, query_vector: list[float], limit: int = 10, filter: dict = None):
        if self._use_vec:
            return await self._search_vec(query_vector, limit, filter)
        else:
            return await self._search_numpy_fallback(query_vector, limit, filter)

    async def _search_numpy_fallback(self, query_vector, limit, filter):
        """Fallback: load all vectors, compute cosine similarity in numpy."""
        import numpy as np

        # Load all vectors (works for small datasets)
        all_vectors = await self._load_all_vectors(filter)
        if not all_vectors:
            return []

        query = np.array(query_vector)
        vectors = np.array([v["vector"] for v in all_vectors])

        # Cosine similarity
        similarities = np.dot(vectors, query) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(query)
        )

        # Top-k
        top_indices = np.argsort(similarities)[-limit:][::-1]
        return [
            {**all_vectors[i], "distance": 1 - similarities[i]}
            for i in top_indices
        ]
```

### 2.4 Model Registry (Dynamic Embedding Dimensions)

```python
@dataclass
class EmbeddingModel:
    """Registered embedding model."""
    name: str
    dimensions: int
    provider: str  # "local" | "openai" | "cohere" | etc.
    version: str


class ModelRegistry:
    """
    Tracks embedding models and their dimensions.

    Solves the "hardcoded 384 dimensions" problem by storing
    model metadata alongside vectors.
    """

    def __init__(self, store: IRelationalStore):
        self._store = store
        self._current: EmbeddingModel | None = None

    async def register(self, model: EmbeddingModel) -> None:
        """Register a new embedding model."""
        await self._store.execute("""
            INSERT OR REPLACE INTO embedding_models (name, dimensions, provider, version, registered_at)
            VALUES (:name, :dimensions, :provider, :version, datetime('now'))
        """, {
            "name": model.name,
            "dimensions": model.dimensions,
            "provider": model.provider,
            "version": model.version,
        })

    async def set_current(self, model_name: str) -> None:
        """Set the active embedding model."""
        model = await self._store.fetch_one(
            "SELECT * FROM embedding_models WHERE name = :name",
            {"name": model_name}
        )
        if not model:
            raise ValueError(f"Model {model_name} not registered")

        self._current = EmbeddingModel(**model)

        await self._store.execute("""
            UPDATE config SET value = :model WHERE key = 'current_embedding_model'
        """, {"model": model_name})

    @property
    def current_dimensions(self) -> int:
        """Current model's vector dimensions."""
        return self._current.dimensions if self._current else 384  # Default fallback

    async def migrate_embeddings(self, from_model: str, to_model: str) -> int:
        """
        Re-embed all vectors when switching models.

        This is expensive but necessary for model changes.
        Returns count of migrated vectors.
        """
        # Mark all embeddings as needing re-embedding
        return await self._store.execute("""
            UPDATE embedding_metadata
            SET needs_reembed = 1, target_model = :to_model
            WHERE model_name = :from_model
        """, {"from_model": from_model, "to_model": to_model})
```

---

## Part III: ORM Schema (Dialect-Agnostic)

Using SQLModel for database-agnostic table definitions:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class InstanceStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    TERMINATED = "terminated"


class Instance(SQLModel, table=True):
    """
    Track all kgent instances (processes).

    Works on SQLite, PostgreSQL, MySQL, etc.
    """
    __tablename__ = "instances"

    id: str = Field(primary_key=True)
    pid: int
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    status: InstanceStatus = Field(default=InstanceStatus.ACTIVE)

    # Context
    project_path: Optional[str] = None
    project_name: Optional[str] = None

    # Resource tracking
    invocations: int = Field(default=0)
    tokens_used: int = Field(default=0)

    # Metadata
    version: Optional[str] = None
    parent_id: Optional[str] = Field(default=None, foreign_key="instances.id")


class AgentState(SQLModel, table=True):
    """Persistent agent state (D-gent backend)."""
    __tablename__ = "agent_state"

    id: Optional[int] = Field(default=None, primary_key=True)
    instance_id: str = Field(foreign_key="instances.id")
    agent_id: str

    state: str  # JSON serialized
    version: int = Field(default=1)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddingModel(SQLModel, table=True):
    """
    Registered embedding models (solves dimension rigidity).
    """
    __tablename__ = "embedding_models"

    name: str = Field(primary_key=True)
    dimensions: int
    provider: str
    version: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddingMetadata(SQLModel, table=True):
    """
    Metadata for embeddings (separate from vector storage).
    """
    __tablename__ = "embedding_metadata"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_type: str  # 'shape' | 'memory' | 'intent'
    source_id: str
    content: str
    model_name: str
    needs_reembed: bool = Field(default=False)
    target_model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ShapeStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Shape(SQLModel, table=True):
    """Topological shapes observed by Membrane."""
    __tablename__ = "shapes"

    id: str = Field(primary_key=True)
    shape_type: str  # 'curvature' | 'void' | 'momentum' | 'dampening'

    intensity: Optional[float] = None
    persistence: Optional[float] = None
    interpretation: Optional[str] = None

    project_path: Optional[str] = None
    boundary: Optional[str] = None  # JSON array

    status: ShapeStatus = Field(default=ShapeStatus.ACTIVE)
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    embedding_id: Optional[int] = Field(default=None, foreign_key="embedding_metadata.id")


class Dream(SQLModel, table=True):
    """Dream logs from Membrane consolidation."""
    __tablename__ = "dreams"

    id: str = Field(primary_key=True)
    dreamed_at: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None

    shapes_processed: Optional[int] = None
    entropy_before: Optional[float] = None
    entropy_after: Optional[float] = None

    insights: Optional[str] = None  # JSON array
    project_path: Optional[str] = None
```

---

## Part IV: Write-Ahead Queue (Concurrency Solution)

### 4.1 The Problem

SQLite serializes writes. Multiple agents writing events/shapes simultaneously causes `SQLITE_BUSY` or high lock contention, especially with CPU-heavy vector insertions.

### 4.2 The Solution: WriterDaemon

```python
import asyncio
from dataclasses import dataclass
from typing import Any, Callable
from enum import Enum


class WriteOperation(str, Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT_VECTOR = "upsert_vector"


@dataclass
class WriteRequest:
    """A queued write operation."""
    operation: WriteOperation
    table: str
    data: dict[str, Any]
    callback: Callable[[bool], None] | None = None


class WriterDaemon:
    """
    Dedicated writer process for all database mutations.

    Agents push writes to an asyncio.Queue; the daemon batches and
    executes them sequentially. This eliminates lock contention and
    enables intelligent batching (100 events → 1 executemany).

    Properties:
    - Non-blocking for agents (fire and forget, or await callback)
    - Batched writes reduce I/O overhead
    - Single writer eliminates SQLITE_BUSY
    - Graceful shutdown with drain
    """

    def __init__(
        self,
        storage: StorageProvider,
        batch_size: int = 100,
        flush_interval: float = 0.1,  # 100ms
    ):
        self._storage = storage
        self._queue: asyncio.Queue[WriteRequest] = asyncio.Queue()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the writer daemon loop."""
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self, drain: bool = True) -> None:
        """
        Stop the daemon.

        If drain=True, processes remaining queue before stopping.
        """
        self._running = False

        if drain:
            while not self._queue.empty():
                await self._flush_batch()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def enqueue(self, request: WriteRequest) -> None:
        """Add write request to queue (non-blocking)."""
        await self._queue.put(request)

    async def _loop(self) -> None:
        """Main daemon loop: batch and flush."""
        while self._running:
            try:
                await asyncio.wait_for(
                    self._flush_batch(),
                    timeout=self._flush_interval
                )
            except asyncio.TimeoutError:
                pass  # Flush on interval even if batch not full

    async def _flush_batch(self) -> None:
        """Collect and execute a batch of writes."""
        batch: list[WriteRequest] = []

        # Collect up to batch_size requests
        while len(batch) < self._batch_size:
            try:
                request = self._queue.get_nowait()
                batch.append(request)
            except asyncio.QueueEmpty:
                break

        if not batch:
            return

        # Group by operation type for efficient execution
        await self._execute_batch(batch)

    async def _execute_batch(self, batch: list[WriteRequest]) -> None:
        """Execute batched writes, notify callbacks."""
        # Group events together for executemany
        events = [r for r in batch if r.table == "events"]
        others = [r for r in batch if r.table != "events"]

        async with self._storage.relational.transaction() as tx:
            # Batch insert events
            if events:
                await tx.execute("""
                    INSERT INTO events (instance_id, event_type, source_agent, data, timestamp)
                    VALUES (:instance_id, :event_type, :source_agent, :data, datetime('now'))
                """, [e.data for e in events])

            # Individual operations for others
            for request in others:
                await self._execute_single(tx, request)

        # Notify callbacks
        for request in batch:
            if request.callback:
                request.callback(True)
```

---

## Part V: Membrane Permeability Protocol

### 5.1 The Problem

With both `~/.kgents/` (global) and `.kgents/` (project), how does data flow between them? When does a project-specific Shape become a global memory?

### 5.2 The Solution: Explicit Permeability Rules

```python
from dataclasses import dataclass
from enum import Enum


class PermeabilityLevel(str, Enum):
    """How permeable the membrane between local and global is."""
    SEALED = "sealed"        # Nothing crosses
    OSMOTIC = "osmotic"      # High-value crosses automatically
    PERMEABLE = "permeable"  # Most things cross
    OPEN = "open"            # Everything syncs


@dataclass
class PermeabilityRule:
    """
    Rule for when local data becomes global.

    Examples:
    - Shape referenced 3+ times → promote to global
    - Shape acknowledged by user → promote to global
    - Shape older than 7 days with high intensity → promote
    """
    condition: str  # DSL expression, e.g., "references >= 3"
    action: str     # "promote" | "archive" | "delete"
    priority: int   # Higher = checked first


class MembranePermeability:
    """
    Manages data flow between project and global cortex.

    Prevents ID collisions via namespacing:
    - Global: SHAPE-{seq}-{type}
    - Local:  {project_hash}:SHAPE-{seq}-{type}

    Promotion creates new global ID, links to local origin.
    """

    def __init__(
        self,
        local_store: IRelationalStore,
        global_store: IRelationalStore,
        rules: list[PermeabilityRule] = None,
    ):
        self._local = local_store
        self._global = global_store
        self._rules = rules or self._default_rules()

    def _default_rules(self) -> list[PermeabilityRule]:
        return [
            PermeabilityRule("user_acknowledged == true", "promote", 100),
            PermeabilityRule("references >= 3", "promote", 50),
            PermeabilityRule("intensity >= 0.8 and age_days >= 7", "promote", 30),
        ]

    async def evaluate_promotion(self, shape_id: str) -> bool:
        """Check if local shape should be promoted to global."""
        shape = await self._local.fetch_one(
            "SELECT * FROM shapes WHERE id = :id",
            {"id": shape_id}
        )

        if not shape:
            return False

        for rule in sorted(self._rules, key=lambda r: -r.priority):
            if self._evaluate_condition(rule.condition, shape):
                if rule.action == "promote":
                    await self._promote_to_global(shape)
                    return True

        return False

    async def _promote_to_global(self, local_shape: dict) -> str:
        """
        Promote local shape to global cortex.

        Creates new global ID, maintains lineage link.
        """
        # Generate global ID
        global_id = await self._generate_global_id(local_shape["shape_type"])

        # Copy to global with new ID
        await self._global.execute("""
            INSERT INTO shapes (id, shape_type, intensity, persistence, interpretation,
                               status, observed_at, local_origin_id, local_origin_project)
            VALUES (:id, :shape_type, :intensity, :persistence, :interpretation,
                    'active', datetime('now'), :local_id, :project)
        """, {
            "id": global_id,
            "shape_type": local_shape["shape_type"],
            "intensity": local_shape["intensity"],
            "persistence": local_shape["persistence"],
            "interpretation": local_shape["interpretation"],
            "local_id": local_shape["id"],
            "project": local_shape["project_path"],
        })

        # Mark local as promoted
        await self._local.execute("""
            UPDATE shapes SET promoted_to_global_id = :global_id WHERE id = :local_id
        """, {"global_id": global_id, "local_id": local_shape["id"]})

        return global_id
```

---

## Part VI: Instance Lifecycle

### 6.1 Registration

```python
@dataclass
class InstanceRegistration:
    """Data for instance registration."""
    id: str                              # UUID v4
    pid: int                             # os.getpid()
    project_path: str | None             # os.getcwd() if .kgents exists
    version: str                         # kgents.__version__
    parent_id: str | None                # For spawned instances


class InstanceManager:
    """
    Manages kgent instance lifecycle.

    Now takes StorageProvider instead of db_path.
    All writes go through WriterDaemon.
    """

    def __init__(self, storage: StorageProvider, writer: WriterDaemon):
        self._storage = storage
        self._writer = writer
        self._instance_id: str | None = None
        self._heartbeat_task: asyncio.Task | None = None

    async def register(self, registration: InstanceRegistration) -> str:
        """Register this instance (uses relational store abstraction)."""
        await self._storage.relational.execute("""
            INSERT INTO instances (id, pid, started_at, last_heartbeat, status,
                                   project_path, project_name, version, parent_id)
            VALUES (:id, :pid, datetime('now'), datetime('now'), 'active',
                    :project_path, :project_name, :version, :parent_id)
        """, {
            "id": registration.id,
            "pid": registration.pid,
            "project_path": registration.project_path,
            "project_name": self._extract_project_name(registration.project_path),
            "version": registration.version,
            "parent_id": registration.parent_id,
        })

        self._instance_id = registration.id
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        return registration.id

    async def _heartbeat_loop(self, interval: float = 60.0):
        """Update heartbeat every 60 seconds (through writer daemon)."""
        while True:
            await asyncio.sleep(interval)
            await self._writer.enqueue(WriteRequest(
                operation=WriteOperation.UPDATE,
                table="instances",
                data={
                    "id": self._instance_id,
                    "last_heartbeat": "datetime('now')",
                },
            ))
```

### 6.2 Cleanup Lifecycle

```python
class CleanupManager:
    """
    Manages database cleanup and maintenance.

    Split database architecture: telemetry.db can be rotated
    independently of membrane.db (no vacuum needed for state DB).
    """

    def __init__(self, storage: StorageProvider):
        self._storage = storage

    async def prune_events(self, retention_days: int = 30) -> int:
        """Remove old events (telemetry store, independent of state)."""
        return await self._storage.telemetry.prune(older_than_days=retention_days)

    async def vacuum_state_db(self) -> None:
        """
        Vacuum state database (membrane.db).

        Only needed after major deletions (rare for state data).
        Telemetry.db can just be deleted and recreated.
        """
        await self._storage.relational.execute("VACUUM")

    async def rotate_telemetry(self) -> None:
        """
        Rotate telemetry database (delete and recreate).

        Much faster than VACUUM for log-like data.
        """
        if isinstance(self._storage.telemetry, SQLiteTelemetryStore):
            # Simply delete the file and let it recreate
            telemetry_path = self._storage.telemetry.db_path
            if telemetry_path.exists():
                telemetry_path.unlink()
            await self._storage.telemetry.connect()
```

---

## Part VII: Safety & Reliability

### 7.1 Cross-Platform Locking

```python
from filelock import FileLock  # pip install filelock (cross-platform)


class AtomicDBOperations:
    """
    All database operations are atomic.

    Uses filelock for cross-platform advisory locking
    (works on Linux, macOS, and Windows).
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        # filelock handles platform differences
        self._lock = FileLock(db_path.with_suffix(".lock"), timeout=30)

    @asynccontextmanager
    async def write_transaction(self):
        """Acquire exclusive write lock, begin transaction."""
        with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute("PRAGMA synchronous=NORMAL")
                await db.execute("PRAGMA foreign_keys=ON")

                try:
                    yield db
                    await db.commit()
                except Exception:
                    await db.rollback()
                    raise
```

### 7.2 Corruption Recovery

```python
class CorruptionRecovery:
    """Detect and recover from database corruption."""

    async def check_integrity(self) -> bool:
        """Run SQLite integrity check."""
        result = await self._storage.relational.fetch_one("PRAGMA integrity_check")
        return result and result.get("integrity_check") == "ok"

    async def attempt_recovery(self) -> bool:
        """
        Attempt to recover corrupted database.

        Strategy:
        1. Try .dump → restore
        2. Fall back to backup
        3. If both fail, start fresh with migration from legacy
        """
        backup_path = await self._latest_backup()

        try:
            dump = await self._dump_database()
            await self._recreate_database()
            await self._replay_dump(dump)
            return True
        except Exception:
            if backup_path and backup_path.exists():
                import shutil
                shutil.copy(backup_path, self.db_path)
                return await self.check_integrity()
            return False
```

---

## Part VIII: Implementation Phases

### Phase 1: Core Infrastructure + Abstractions

| Task | Components | Tests |
|------|------------|-------|
| Repository interfaces | `IRelationalStore`, `IVectorStore`, `IBlobStore`, `ITelemetryStore` | Interface tests |
| SQLite providers | `SQLiteRelationalStore`, `SQLiteVecStore`, `SQLiteTelemetryStore` | Provider tests |
| StorageProvider factory | `from_config()`, default config | Config loading tests |
| WriterDaemon | Queue, batching, flush | Concurrency tests |

**Deliverables:**
- `impl/claude/protocols/cli/instance_db/interfaces.py`
- `impl/claude/protocols/cli/instance_db/providers/sqlite.py`
- `impl/claude/protocols/cli/instance_db/storage.py`
- `impl/claude/protocols/cli/instance_db/writer.py`
- Tests: 40+

### Phase 2: ORM + Migrations

| Task | Components | Tests |
|------|------------|-------|
| SQLModel schemas | All table models | Schema validation |
| Alembic setup | Migration infrastructure | Migration tests |
| ModelRegistry | Dynamic embedding dimensions | Model swap tests |

**Deliverables:**
- `impl/claude/protocols/cli/instance_db/models.py`
- `impl/claude/protocols/cli/instance_db/migrations/`
- `impl/claude/protocols/cli/instance_db/model_registry.py`
- Tests: 30+

### Phase 3: D-gent Integration

| Task | Components | Tests |
|------|------------|-------|
| MembraneAgent refactor | Inject StorageProvider | CRUD + search tests |
| Lens integration | Umwelt + Projector updates | Isolation tests |
| Permeability protocol | Local ↔ Global sync | Promotion tests |

**Deliverables:**
- `impl/claude/protocols/cli/instance_db/membrane_agent.py`
- `impl/claude/protocols/cli/instance_db/permeability.py`
- Updates to `impl/claude/bootstrap/umwelt.py`
- Tests: 35+

### Phase 4: Cleanup, Safety, O-gent

| Task | Components | Tests |
|------|------------|-------|
| CleanupManager | Split DB rotation | Retention tests |
| CorruptionRecovery | Integrity, backup restore | Recovery tests |
| EventEmitter | Through WriterDaemon | Emission tests |
| DatabaseObserver | O-gent integration | Observer tests |

**Deliverables:**
- `impl/claude/protocols/cli/instance_db/cleanup.py`
- `impl/claude/protocols/cli/instance_db/recovery.py`
- `impl/claude/protocols/cli/instance_db/events.py`
- Tests: 30+

### Phase 5: CLI + Dashboard

| Task | Components | Tests |
|------|------------|-------|
| `kgents instances` | List active instances | CLI tests |
| `kgents cleanup` | Manual maintenance | Cleanup CLI tests |
| `kgents config providers` | View/edit infrastructure.yaml | Config CLI tests |
| InstanceDashboard | Terminal dashboard | Rendering tests |

**Deliverables:**
- `impl/claude/protocols/cli/handlers/instances.py`
- `impl/claude/protocols/cli/handlers/config.py`
- Updates to `impl/claude/protocols/cli/__main__.py`
- Tests: 20+

### Phase 6: Future Providers (Deferred)

| Provider | When | Use Case |
|----------|------|----------|
| `PostgresProvider` | Team adoption | Shared state across machines |
| `QdrantProvider` | Vector scale | >100k embeddings |
| `S3Provider` | Cloud backups | AWS integration |
| `ObsidianProvider` | PKM sync | Personal knowledge management |
| `ClickHouseProvider` | Log analytics | High-velocity telemetry |

---

## Appendix A: Migration Strategy

### A.1 From v1.0 (if implemented)

```python
async def migrate_v1_to_v2():
    """Migrate from single-DB to split-DB architecture."""
    old_db = Path.home() / ".kgents" / "membrane.db"
    new_data = Path.home() / ".local/share/kgents"
    new_config = Path.home() / ".config/kgents"

    # Create new directories
    new_data.mkdir(parents=True, exist_ok=True)
    new_config.mkdir(parents=True, exist_ok=True)

    # Move state DB
    if old_db.exists():
        shutil.move(old_db, new_data / "membrane.db")

    # Extract events to telemetry.db
    async with aiosqlite.connect(new_data / "membrane.db") as source:
        async with aiosqlite.connect(new_data / "telemetry.db") as dest:
            # Create telemetry schema
            await dest.execute(TELEMETRY_SCHEMA)

            # Copy events
            events = await source.execute("SELECT * FROM events")
            for event in await events.fetchall():
                await dest.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)", event)

    # Delete events from membrane.db
    async with aiosqlite.connect(new_data / "membrane.db") as db:
        await db.execute("DROP TABLE IF EXISTS events")
        await db.execute("VACUUM")

    # Create default infrastructure.yaml
    write_default_config(new_config / "infrastructure.yaml")
```

### A.2 Alembic Configuration

```python
# alembic/env.py
from sqlmodel import SQLModel
from impl.claude.protocols.cli.instance_db.models import *  # Import all models

target_metadata = SQLModel.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Dialect-agnostic migrations
            render_as_batch=True,  # Required for SQLite ALTER TABLE
        )

        with context.begin_transaction():
            context.run_migrations()
```

---

## Appendix B: Performance Considerations

### B.1 Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Instance registration | <50ms | Cold start path |
| Heartbeat update | <10ms | Through WriterDaemon |
| Shape save | <100ms | Includes embedding |
| Semantic search | <200ms | Top-10 results |
| Event batch write | <50ms | 100 events via executemany |
| Cleanup cycle | <5s | During idle |

### B.2 Optimizations

1. **Split Databases**: Telemetry rotation doesn't touch state DB
2. **WriterDaemon**: Eliminates lock contention, enables batching
3. **WAL Mode**: Concurrent reads during writes
4. **Prepared Statements**: Cache compiled SQL (SQLAlchemy handles this)
5. **Numpy Fallback**: Works without sqlite-vec for small datasets
6. **Connection Pool**: Reuse connections (built into aiosqlite)

---

## Appendix C: Future Provider Sketches

### C.1 S3 Blob Provider

```python
class S3BlobStore(IBlobStore):
    """AWS S3 implementation for blob storage."""

    def __init__(self, bucket: str, prefix: str = ""):
        import aioboto3
        self._session = aioboto3.Session()
        self._bucket = bucket
        self._prefix = prefix

    async def put(self, key: str, data: bytes, content_type: str = None) -> str:
        async with self._session.client("s3") as s3:
            await s3.put_object(
                Bucket=self._bucket,
                Key=f"{self._prefix}{key}",
                Body=data,
                ContentType=content_type or "application/octet-stream",
            )
        return f"s3://{self._bucket}/{self._prefix}{key}"
```

### C.2 Qdrant Vector Provider

```python
class QdrantVectorStore(IVectorStore):
    """Qdrant implementation for production-scale vectors."""

    def __init__(self, host: str, collection: str, dimensions: int):
        from qdrant_client import AsyncQdrantClient
        self._client = AsyncQdrantClient(host)
        self._collection = collection
        self._dimensions = dimensions

    async def search(self, query_vector: list[float], limit: int = 10, filter: dict = None):
        from qdrant_client.models import Filter

        results = await self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=limit,
            query_filter=Filter(**filter) if filter else None,
        )
        return [{"id": r.id, "distance": r.score, **r.payload} for r in results]
```

---

*"The Fluid Cortex flows between local and global, between SQLite and cloud, between now and future. The abstraction is the permanence."*
