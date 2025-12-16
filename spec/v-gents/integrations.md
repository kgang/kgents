# V-gent Integrations: Cross-Agent Coordination

> *"V-gent is infrastructure. Every agent that needs similarity search uses it."*

---

## Purpose

V-gent doesn't exist in isolation—it's the **shared vector infrastructure** that multiple agents depend on. This document specifies how V-gent integrates with L-gent (catalog), M-gent (memory), D-gent (persistence), and other consumers.

---

## Architecture Overview

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                     Agent Layer                              │
                    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
                    │  │ L-gent  │  │ M-gent  │  │ K-gent  │  │ AssociativeQuery│ │
                    │  │(Catalog)│  │(Memory) │  │ (Soul)  │  │   (Generic)     │ │
                    │  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘ │
                    │       │            │            │                 │          │
                    │       └────────────┼────────────┼─────────────────┘          │
                    │                    │            │                            │
                    │                    ▼            ▼                            │
                    │              ┌─────────────────────┐                         │
                    │              │      V-gent         │                         │
                    │              │  (Vector Protocol)  │                         │
                    │              └──────────┬──────────┘                         │
                    │                         │                                    │
                    └─────────────────────────┼────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┼────────────────────────────────────┐
                    │                    Backend Layer                             │
                    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
                    │  │ Memory  │  │ D-gent  │  │pgvector │  │ Qdrant  │         │
                    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │
                    └──────────────────────────────────────────────────────────────┘
```

---

## V × L: V-gent + L-gent Integration

**Pattern**: L-gent delegates all vector operations to V-gent.

### Before (Current)

L-gent has embedded vector backends (`vector_backend.py`, `vector_db.py`):

```python
# Current: L-gent owns vector operations
class VectorCatalog:
    def __init__(self, embedder, catalog, vector_backend):
        self.catalog = catalog
        self.vector_backend = vector_backend  # Embedded in L-gent
```

### After (V-gent)

L-gent uses V-gent as a service:

```python
# New: L-gent uses V-gent
class SemanticCatalog:
    """
    L-gent catalog with V-gent for semantic search.

    Separation:
    - L-gent: Catalog metadata, lineage, lattice relationships
    - V-gent: Vector storage, similarity search
    - Embedder: Vector generation (L-gent or external)
    """

    def __init__(
        self,
        vgent: VgentProtocol,
        embedder: EmbedderProtocol,
    ):
        self.vgent = vgent
        self.embedder = embedder
        self.registry: dict[str, CatalogEntry] = {}

    async def register(self, entry: CatalogEntry) -> str:
        """Register entry and index for semantic search."""
        # Store in catalog registry
        self.registry[entry.id] = entry

        # Generate embedding
        searchable_text = self._make_searchable_text(entry)
        embedding = await self.embedder.embed(searchable_text)

        # Index in V-gent
        await self.vgent.add(
            id=entry.id,
            embedding=embedding,
            metadata={
                "name": entry.name,
                "entity_type": entry.entity_type.value,
                "status": entry.status.value,
            },
        )

        return entry.id

    async def search(
        self,
        intent: str,
        entity_type: EntityType | None = None,
        limit: int = 10,
    ) -> list[SemanticResult]:
        """Search catalog by semantic similarity."""
        # Generate query embedding
        query_embedding = await self.embedder.embed(intent)

        # Build filters
        filters = {}
        if entity_type:
            filters["entity_type"] = entity_type.value

        # Search V-gent
        results = await self.vgent.search(
            query=query_embedding,
            limit=limit,
            filters=filters,
        )

        # Enrich with full catalog entries
        return [
            SemanticResult(
                id=r.id,
                entry=self.registry.get(r.id),
                similarity=r.similarity,
            )
            for r in results
            if r.id in self.registry
        ]
```

### Migration Path

1. Extract `VectorBackend` protocol from `agents/l/vector_backend.py`
2. Move to `agents/v/protocol.py` as `VgentProtocol`
3. Update L-gent to inject V-gent rather than own it
4. Keep backward compatibility via adapter

---

## V × M: V-gent + M-gent Integration

**Pattern**: M-gent uses V-gent for associative recall.

### Current (AssociativeMemory)

M-gent embeds vector operations:

```python
# Current: M-gent maintains its own index
class AssociativeMemory:
    _memories: dict[str, Memory]  # Includes embeddings

    async def recall(self, cue: str, limit: int = 5) -> list[RecallResult]:
        cue_embedding = await self.embedder(cue)
        # Linear scan of _memories for similarity
        ...
```

### After (V-gent)

M-gent delegates to V-gent:

```python
class AssociativeMemory:
    """
    Memory with V-gent-backed associative recall.

    Separation:
    - M-gent: Memory lifecycle, relevance decay, consolidation
    - V-gent: Embedding storage, similarity search
    - D-gent: Raw content persistence
    """

    def __init__(
        self,
        dgent: DgentProtocol,
        vgent: VgentProtocol,
        embedder: EmbedderProtocol,
    ):
        self.dgent = dgent
        self.vgent = vgent
        self.embedder = embedder
        self._lifecycle: dict[str, Lifecycle] = {}  # memory_id → lifecycle state

    async def remember(
        self,
        content: bytes,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store content as a memory."""
        # Store raw content in D-gent
        datum = Datum.create(content=content, metadata=metadata or {})
        datum_id = await self.dgent.put(datum)

        # Generate embedding
        text = content.decode("utf-8", errors="ignore")
        embedding = await self.embedder.embed(text)

        # Index in V-gent
        await self.vgent.add(
            id=datum_id,
            embedding=embedding,
            metadata={"lifecycle": Lifecycle.ACTIVE.value, **(metadata or {})},
        )

        # Track lifecycle
        self._lifecycle[datum_id] = Lifecycle.ACTIVE

        return datum_id

    async def recall(
        self,
        cue: str,
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[RecallResult]:
        """Associative recall by semantic similarity."""
        # Generate query embedding
        query_embedding = await self.embedder.embed(cue)

        # Filter out DREAMING memories (not accessible during consolidation)
        # This requires metadata filtering in V-gent
        accessible_lifecycles = [Lifecycle.ACTIVE.value, Lifecycle.DORMANT.value]

        # Search V-gent
        results = await self.vgent.search(
            query=query_embedding,
            limit=limit * 2,  # Over-fetch for lifecycle filtering
            threshold=threshold,
        )

        # Filter by lifecycle and enrich
        recall_results = []
        for r in results:
            lifecycle = self._lifecycle.get(r.id, Lifecycle.DORMANT)
            if lifecycle.value not in accessible_lifecycles:
                continue

            # Fetch content from D-gent
            datum = await self.dgent.get(r.id)

            recall_results.append(RecallResult(
                memory_id=r.id,
                similarity=r.similarity,
                content=datum.content if datum else None,
                lifecycle=lifecycle,
            ))

            if len(recall_results) >= limit:
                break

        return recall_results
```

---

## V × D: V-gent + D-gent Integration

**Pattern**: V-gent backends can use D-gent for persistence.

### DgentVectorBackend

Vectors stored as D-gent Datum:

```python
class DgentVectorBackend(VgentProtocol):
    """
    V-gent backend using D-gent for persistence.

    Vector data stored as Datum:
    - id: "vgent:{namespace}:{vector_id}"
    - content: Serialized vector (struct pack of floats)
    - metadata: Vector metadata + dimension + metric

    Benefits:
    - Inherits D-gent's projection lattice (Memory → JSONL → SQLite → Postgres)
    - Single persistence layer
    - Causal linking available if needed
    """

    def __init__(
        self,
        dgent: DgentProtocol,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        namespace: str = "default",
    ):
        self.dgent = dgent
        self._dimension = dimension
        self._metric = metric
        self._namespace = namespace
        self._index: dict[str, tuple[float, ...]] = {}  # In-memory for search

    async def add(self, id: str, embedding: Embedding | list[float], metadata: dict[str, str] | None = None) -> str:
        vector = embedding.vector if isinstance(embedding, Embedding) else tuple(embedding)

        # Store in D-gent
        datum = Datum(
            id=f"vgent:{self._namespace}:{id}",
            content=self._serialize(vector),
            created_at=time.time(),
            causal_parent=None,
            metadata={
                "dimension": str(self._dimension),
                "metric": self._metric.value,
                **(metadata or {}),
            },
        )
        await self.dgent.put(datum)

        # Update in-memory index
        self._index[id] = vector

        return id

    async def search(self, query: Embedding | list[float], limit: int = 10, filters: dict[str, str] | None = None, threshold: float | None = None) -> list[SearchResult]:
        query_vec = query.vector if isinstance(query, Embedding) else tuple(query)

        # Linear scan of in-memory index
        scored = []
        for id, vector in self._index.items():
            similarity = self._metric.similarity(query_vec, vector)
            if threshold is None or similarity >= threshold:
                scored.append((id, similarity))

        # Sort and take top N
        scored.sort(key=lambda x: x[1], reverse=True)

        # Fetch metadata from D-gent if filters needed
        results = []
        for id, similarity in scored[:limit * 2]:
            if filters:
                datum = await self.dgent.get(f"vgent:{self._namespace}:{id}")
                if not datum or not self._matches_filters(datum.metadata, filters):
                    continue
                metadata = datum.metadata
            else:
                metadata = {}

            results.append(SearchResult(
                id=id,
                similarity=similarity,
                distance=1.0 - similarity,
                metadata=metadata,
            ))

            if len(results) >= limit:
                break

        return results

    async def load_index(self) -> None:
        """Rebuild in-memory index from D-gent on startup."""
        data = await self.dgent.list(prefix=f"vgent:{self._namespace}:", limit=1_000_000)
        for datum in data:
            vector_id = datum.id.split(":", 2)[2]  # Extract original ID
            vector = self._deserialize(datum.content)
            self._index[vector_id] = vector
```

### Projection Alignment

V-gent and D-gent projection lattices align:

| D-gent Backend | V-gent Backend | Notes |
|----------------|----------------|-------|
| Memory | Memory | Both ephemeral |
| JSONL | D-gent | V-gent uses D-gent's JSONL |
| SQLite | D-gent | V-gent uses D-gent's SQLite |
| Postgres | Postgres/pgvector | May differ (pgvector is specialized) |
| — | Qdrant | V-gent only (specialized vector DB) |

---

## V × K: V-gent + K-gent Integration

**Pattern**: K-gent uses V-gent for belief/memory similarity.

```python
class SoulVectorIndex:
    """
    K-gent's use of V-gent for belief retrieval.

    The soul stores:
    - Core beliefs (high relevance, cherished)
    - Session context (normal relevance)
    - Creative seeds (experimental)

    All are vectorized for associative recall.
    """

    def __init__(self, vgent: VgentProtocol, embedder: EmbedderProtocol):
        self.vgent = vgent
        self.embedder = embedder

    async def index_belief(self, belief_id: str, belief_text: str, metadata: dict[str, str]) -> None:
        """Index a belief for similarity search."""
        embedding = await self.embedder.embed(belief_text)
        await self.vgent.add(
            id=belief_id,
            embedding=embedding,
            metadata={"type": "belief", **metadata},
        )

    async def recall_beliefs(self, topic: str, limit: int = 5) -> list[str]:
        """Find beliefs relevant to a topic."""
        query = await self.embedder.embed(topic)
        results = await self.vgent.search(
            query=query,
            limit=limit,
            filters={"type": "belief"},
        )
        return [r.id for r in results]
```

---

## Embedding Generation: L-gent vs External

**Question**: Where do embeddings come from?

**Options**:

1. **L-gent Embedder**: L-gent owns embedding generation, V-gent just stores
2. **External Embedder**: Each consumer brings their own embedder
3. **V-gent Embedder**: V-gent provides default embedder (not recommended)

**Recommendation**: Option 2 (External Embedder)

```python
# Each consumer brings their own embedder
catalog = SemanticCatalog(
    vgent=vgent,
    embedder=OpenAIEmbedder(model="text-embedding-3-small"),
)

memory = AssociativeMemory(
    dgent=dgent,
    vgent=vgent,
    embedder=SentenceTransformerEmbedder(model="all-MiniLM-L6-v2"),
)
```

**Rationale**:
- Different use cases need different embedders
- L-gent may use large model for catalog (quality)
- M-gent may use small model for memory (speed)
- V-gent stays pure (just geometry)

---

## Shared V-gent Instance

Multiple agents can share a V-gent instance with namespace isolation:

```python
# Shared V-gent with namespace isolation
vgent = VgentRouter(dimension=384)

# L-gent namespace
l_gent_vgent = NamespacedVgent(vgent, namespace="catalog")

# M-gent namespace
m_gent_vgent = NamespacedVgent(vgent, namespace="memory")

# K-gent namespace
k_gent_vgent = NamespacedVgent(vgent, namespace="soul")


class NamespacedVgent(VgentProtocol):
    """Wrapper that prefixes IDs with namespace."""

    def __init__(self, vgent: VgentProtocol, namespace: str):
        self.vgent = vgent
        self.namespace = namespace

    async def add(self, id: str, embedding: Embedding | list[float], metadata: dict[str, str] | None = None) -> str:
        full_id = f"{self.namespace}:{id}"
        await self.vgent.add(full_id, embedding, metadata)
        return id  # Return original ID

    async def search(self, query: Embedding | list[float], limit: int = 10, filters: dict[str, str] | None = None, threshold: float | None = None) -> list[SearchResult]:
        # Add namespace filter
        ns_filters = {"namespace": self.namespace, **(filters or {})}
        results = await self.vgent.search(query, limit, ns_filters, threshold)

        # Strip namespace from IDs
        return [
            SearchResult(
                id=r.id.removeprefix(f"{self.namespace}:"),
                similarity=r.similarity,
                distance=r.distance,
                metadata=r.metadata,
            )
            for r in results
        ]
```

---

## AGENTESE Integration

V-gent paths under `self.vector.*`:

```python
# Register V-gent paths in AGENTESE
async def register_vgent_paths(logos: Logos, vgent: VgentProtocol):
    """Wire V-gent into AGENTESE."""

    @logos.register("self.vector.add")
    async def vector_add(id: str, embedding: list[float], metadata: dict[str, str] | None = None):
        return await vgent.add(id, embedding, metadata)

    @logos.register("self.vector.search")
    async def vector_search(query: list[float], limit: int = 10, threshold: float | None = None):
        return await vgent.search(query, limit, threshold=threshold)

    @logos.register("self.vector.get")
    async def vector_get(id: str):
        return await vgent.get(id)

    @logos.register("self.vector.remove")
    async def vector_remove(id: str):
        return await vgent.remove(id)

    @logos.register("self.vector.count")
    async def vector_count():
        return await vgent.count()
```

---

## Migration Checklist

### Phase 1: Extract Protocol

- [ ] Create `agents/v/__init__.py`
- [ ] Create `agents/v/protocol.py` with `VgentProtocol`
- [ ] Create `agents/v/types.py` with `Embedding`, `SearchResult`, etc.

### Phase 2: Implement Backends

- [ ] Create `agents/v/backends/memory.py`
- [ ] Create `agents/v/backends/dgent.py`
- [ ] Create `agents/v/router.py`

### Phase 3: Update L-gent

- [ ] Update `agents/l/vector_backend.py` to use V-gent
- [ ] Update `agents/l/vector_db.py` to use V-gent
- [ ] Mark old vector code as deprecated

### Phase 4: Update M-gent

- [ ] Update `agents/m/associative.py` to use V-gent
- [ ] Update tests

### Phase 5: Add External Backends

- [ ] Create `agents/v/backends/qdrant.py` (optional)
- [ ] Create `agents/v/backends/pgvector.py` (optional)

---

## See Also

- `spec/v-gents/core.md` — Core protocol and types
- `spec/v-gents/backends.md` — Backend implementations
- `spec/l-gents/README.md` — L-gent catalog (consumes V-gent)
- `spec/m-gents/architecture.md` — M-gent memory (consumes V-gent)
- `spec/d-gents/architecture.md` — D-gent persistence (V-gent backend option)
