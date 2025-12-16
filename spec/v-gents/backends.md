# V-gent Backends: The Projection Lattice for Vectors

> *"Same search, different plumbing."*

---

## Purpose

V-gent backends provide concrete implementations of `VgentProtocol`. Like D-gent's projection lattice for raw data, V-gent has a projection lattice for vectors—from ephemeral in-memory to production-grade vector databases.

---

## The Projection Lattice

```
                    ┌─────────────┐
                    │   Qdrant    │  (Dedicated vector DB)
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Postgres   │  (pgvector extension)
                    │  + pgvector │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   D-gent    │  (Vectors as Datum)
                    │  + Index    │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   Memory    │  (Ephemeral, fast)
                    └─────────────┘
```

**Graceful Degradation**: If preferred backend unavailable, descend the lattice.
**Auto-Upgrade**: Background process can promote vectors to more capable tiers.

---

## Backend Tiers

### Tier 0: MemoryVectorBackend (Ephemeral)

In-memory vector storage. Fast but lost on restart.

```python
class MemoryVectorBackend:
    """
    In-memory vector storage.

    Use for:
    - Testing
    - Small datasets (< 10K vectors)
    - Ephemeral operations

    Characteristics:
    - O(n) search (linear scan)
    - O(1) add/remove
    - No persistence
    - No external dependencies
    """

    def __init__(self, dimension: int, metric: DistanceMetric = DistanceMetric.COSINE):
        self._dimension = dimension
        self._metric = metric
        self._store: dict[str, VectorEntry] = {}

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def metric(self) -> DistanceMetric:
        return self._metric

    async def add(self, id: str, embedding: Embedding | list[float], metadata: dict[str, str] | None = None) -> str:
        vector = embedding.vector if isinstance(embedding, Embedding) else tuple(embedding)
        self._store[id] = VectorEntry(
            id=id,
            embedding=Embedding(vector=vector, dimension=len(vector), source="unknown"),
            metadata=metadata or {},
        )
        return id

    async def search(self, query: Embedding | list[float], limit: int = 10, filters: dict[str, str] | None = None, threshold: float | None = None) -> list[SearchResult]:
        query_vec = query.vector if isinstance(query, Embedding) else tuple(query)

        results = []
        for entry in self._store.values():
            # Apply metadata filters
            if filters and not self._matches_filters(entry.metadata, filters):
                continue

            similarity = self._metric.similarity(query_vec, entry.embedding.vector)

            if threshold is not None and similarity < threshold:
                continue

            results.append(SearchResult(
                id=entry.id,
                similarity=similarity,
                distance=1.0 - similarity,  # Approximate
                metadata=entry.metadata,
            ))

        # Sort by similarity (descending) and take top N
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:limit]
```

### Tier 1: DgentVectorBackend (Persisted via D-gent)

Vectors stored as D-gent Datum with an in-memory index.

```python
class DgentVectorBackend:
    """
    Vector storage backed by D-gent.

    Use for:
    - Medium datasets (10K - 100K vectors)
    - Persistence without external dependencies
    - Integration with D-gent projection lattice

    Architecture:
        - Vectors stored as Datum (bytes = serialized vector)
        - Metadata stored in Datum.metadata
        - In-memory index rebuilt on startup
        - Index updates are atomic with Datum writes

    Path: ~/.kgents/vectors/{namespace}/

    Characteristics:
    - O(n) search (linear scan of in-memory index)
    - Persists across restarts
    - Inherits D-gent's graceful degradation
    """

    def __init__(
        self,
        dgent: DgentProtocol,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        namespace: str = "vectors",
    ):
        self.dgent = dgent
        self._dimension = dimension
        self._metric = metric
        self._namespace = namespace
        self._index: dict[str, tuple[float, ...]] = {}  # id → vector (in-memory)

    async def _load_index(self) -> None:
        """Rebuild in-memory index from D-gent on startup."""
        data = await self.dgent.list(prefix=f"{self._namespace}:", limit=1_000_000)
        for datum in data:
            vector = self._deserialize_vector(datum.content)
            self._index[datum.id] = vector

    async def add(self, id: str, embedding: Embedding | list[float], metadata: dict[str, str] | None = None) -> str:
        vector = embedding.vector if isinstance(embedding, Embedding) else tuple(embedding)

        # Store in D-gent
        full_id = f"{self._namespace}:{id}"
        datum = Datum(
            id=full_id,
            content=self._serialize_vector(vector),
            created_at=time.time(),
            causal_parent=None,
            metadata=metadata or {},
        )
        await self.dgent.put(datum)

        # Update in-memory index
        self._index[id] = vector
        return id

    async def search(self, query: Embedding | list[float], limit: int = 10, filters: dict[str, str] | None = None, threshold: float | None = None) -> list[SearchResult]:
        query_vec = query.vector if isinstance(query, Embedding) else tuple(query)

        # Linear scan of in-memory index
        results = []
        for id, vector in self._index.items():
            similarity = self._metric.similarity(query_vec, vector)

            if threshold is not None and similarity < threshold:
                continue

            # Fetch metadata from D-gent if filters needed
            if filters:
                datum = await self.dgent.get(f"{self._namespace}:{id}")
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

        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:limit]

    def _serialize_vector(self, vector: tuple[float, ...]) -> bytes:
        """Serialize vector to bytes (e.g., msgpack or numpy)."""
        import struct
        return struct.pack(f"{len(vector)}f", *vector)

    def _deserialize_vector(self, data: bytes) -> tuple[float, ...]:
        """Deserialize bytes to vector."""
        import struct
        n = len(data) // 4  # 4 bytes per float
        return struct.unpack(f"{n}f", data)
```

### Tier 2: PostgresVectorBackend (pgvector)

PostgreSQL with pgvector extension for production workloads.

```python
class PostgresVectorBackend:
    """
    Vector storage using PostgreSQL + pgvector.

    Use for:
    - Large datasets (100K - 10M vectors)
    - Production workloads
    - When Postgres is already in infrastructure

    Requires:
    - PostgreSQL with pgvector extension
    - KGENTS_POSTGRES_URL environment variable

    Schema:
        CREATE EXTENSION vector;
        CREATE TABLE vectors_{namespace} (
            id TEXT PRIMARY KEY,
            embedding vector({dimension}),
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE INDEX ON vectors_{namespace} USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);

    Characteristics:
    - O(log n) search with IVF index
    - ACID transactions
    - Concurrent access
    - SQL-based filtering
    """

    def __init__(self, connection_url: str, namespace: str, dimension: int):
        self.url = connection_url
        self.namespace = namespace
        self._dimension = dimension
        self._pool = None  # asyncpg connection pool

    async def search(self, query: Embedding | list[float], limit: int = 10, filters: dict[str, str] | None = None, threshold: float | None = None) -> list[SearchResult]:
        query_vec = query.vector if isinstance(query, Embedding) else tuple(query)

        # Build SQL query
        sql = f"""
            SELECT id, embedding, metadata,
                   1 - (embedding <=> $1::vector) AS similarity
            FROM vectors_{self.namespace}
            WHERE 1=1
        """
        params = [list(query_vec)]

        # Add metadata filters
        if filters:
            for i, (key, value) in enumerate(filters.items()):
                sql += f" AND metadata->>'{key}' = ${i+2}"
                params.append(value)

        # Add threshold filter
        if threshold is not None:
            sql += f" AND 1 - (embedding <=> $1::vector) >= ${len(params)+1}"
            params.append(threshold)

        sql += f" ORDER BY similarity DESC LIMIT {limit}"

        # Execute
        rows = await self._pool.fetch(sql, *params)

        return [
            SearchResult(
                id=row["id"],
                similarity=row["similarity"],
                distance=1.0 - row["similarity"],
                metadata=row["metadata"],
            )
            for row in rows
        ]
```

### Tier 3: QdrantBackend (Dedicated Vector DB)

Qdrant for maximum scale and features.

```python
class QdrantBackend:
    """
    Vector storage using Qdrant.

    Use for:
    - Very large datasets (10M+ vectors)
    - Maximum performance
    - Advanced filtering (numeric ranges, geo, etc.)
    - Distributed deployment

    Requires:
    - Qdrant server (docker, cloud, or self-hosted)
    - KGENTS_QDRANT_URL environment variable

    Characteristics:
    - Sub-linear search (HNSW index)
    - Payload-based filtering
    - Horizontal scaling
    - Snapshot/backup support
    """

    def __init__(self, url: str, collection_name: str, dimension: int):
        self.url = url
        self.collection_name = collection_name
        self._dimension = dimension
        self._client = None  # qdrant_client.QdrantClient

    async def ensure_collection(self) -> None:
        """Create collection if not exists."""
        from qdrant_client.models import Distance, VectorParams

        collections = await self._client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            await self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self._dimension,
                    distance=Distance.COSINE,
                ),
            )

    async def search(self, query: Embedding | list[float], limit: int = 10, filters: dict[str, str] | None = None, threshold: float | None = None) -> list[SearchResult]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        query_vec = query.vector if isinstance(query, Embedding) else list(query)

        # Build Qdrant filter
        qdrant_filter = None
        if filters:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filters.items()
            ]
            qdrant_filter = Filter(must=conditions)

        results = await self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vec,
            query_filter=qdrant_filter,
            limit=limit,
            score_threshold=threshold,
        )

        return [
            SearchResult(
                id=str(hit.id),
                similarity=hit.score,
                distance=1.0 - hit.score,
                metadata=hit.payload or {},
            )
            for hit in results
        ]
```

---

## The VgentRouter

Like DgentRouter, VgentRouter selects the best available backend:

```python
class VgentRouter:
    """
    Routes vector operations to the best available backend.

    Selection order:
    1. Explicit override (if provided)
    2. Environment detection (KGENTS_VGENT_BACKEND)
    3. Availability probe (try preferred, fallback on failure)

    Usage:
        router = VgentRouter(dimension=768)  # Auto-select
        router = VgentRouter(dimension=768, preferred=VectorBackend.QDRANT)

        await router.add("doc1", embedding)
        results = await router.search(query)
    """

    def __init__(
        self,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        preferred: VectorBackend | None = None,
        fallback_chain: list[VectorBackend] | None = None,
        namespace: str = "default",
    ):
        self.dimension = dimension
        self.metric = metric
        self.preferred = preferred
        self.fallback_chain = fallback_chain or [
            VectorBackend.DGENT,
            VectorBackend.MEMORY,
        ]
        self.namespace = namespace
        self._backend: VgentProtocol | None = None

    async def _select_backend(self) -> VgentProtocol:
        """Select best available backend."""
        # Check environment
        env_backend = os.environ.get("KGENTS_VGENT_BACKEND")
        if env_backend:
            try:
                backend = VectorBackend[env_backend.upper()]
                if await self._is_available(backend):
                    return self._create_backend(backend)
            except KeyError:
                pass

        # Try preferred
        if self.preferred and await self._is_available(self.preferred):
            return self._create_backend(self.preferred)

        # Try fallback chain
        for backend in self.fallback_chain:
            if await self._is_available(backend):
                return self._create_backend(backend)

        # Last resort: memory
        return MemoryVectorBackend(self.dimension, self.metric)

    async def _is_available(self, backend: VectorBackend) -> bool:
        """Check if backend is available."""
        if backend == VectorBackend.MEMORY:
            return True
        elif backend == VectorBackend.DGENT:
            # Always available (uses D-gent's projection)
            return True
        elif backend == VectorBackend.POSTGRES:
            # Check for pgvector
            url = os.environ.get("KGENTS_POSTGRES_URL")
            if not url:
                return False
            # TODO: Actually check pgvector extension
            return True
        elif backend == VectorBackend.QDRANT:
            url = os.environ.get("KGENTS_QDRANT_URL")
            return bool(url)
        return False


class VectorBackend(Enum):
    """Available vector backends."""
    MEMORY = auto()
    DGENT = auto()
    POSTGRES = auto()
    QDRANT = auto()
```

---

## Embedding Providers

V-gent is embedding-agnostic, but common providers:

```python
class OpenAIEmbedder:
    """OpenAI embedding models."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._dimension = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }[model]

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def source(self) -> str:
        return f"openai/{self.model}"

    async def embed(self, text: str) -> Embedding:
        from openai import AsyncOpenAI
        client = AsyncOpenAI()
        response = await client.embeddings.create(input=text, model=self.model)
        return Embedding(
            vector=tuple(response.data[0].embedding),
            dimension=self._dimension,
            source=self.source,
        )


class HashEmbedder:
    """
    Deterministic hash-based pseudo-embeddings.

    NOT semantically meaningful—just for testing and fallback.
    """

    def __init__(self, dimension: int = 64):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def source(self) -> str:
        return "local/hash"

    async def embed(self, text: str) -> Embedding:
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        # Convert bytes to floats
        floats = []
        for i in range(self._dimension):
            byte_val = h[i % len(h)]
            floats.append((byte_val / 255.0) * 2 - 1)  # -1 to 1
        return Embedding(
            vector=tuple(floats),
            dimension=self._dimension,
            source=self.source,
        )


class SentenceTransformerEmbedder:
    """
    Local embedding via sentence-transformers.

    No API calls, runs locally.
    """

    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model_name = model
        self._model = SentenceTransformer(model)
        self._dimension = self._model.get_sentence_embedding_dimension()

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def source(self) -> str:
        return f"sentence-transformers/{self.model_name}"

    async def embed(self, text: str) -> Embedding:
        # sentence-transformers is sync, wrap in executor
        import asyncio
        loop = asyncio.get_event_loop()
        vector = await loop.run_in_executor(None, self._model.encode, text)
        return Embedding(
            vector=tuple(float(x) for x in vector),
            dimension=self._dimension,
            source=self.source,
        )
```

---

## Backend Selection Strategy

| Dataset Size | Recommended Backend | Reason |
|--------------|---------------------|--------|
| < 1K | Memory | No persistence needed |
| 1K - 10K | Memory or D-gent | Simple, local |
| 10K - 100K | D-gent | Persistence, no external deps |
| 100K - 1M | Postgres/pgvector | SQL filtering, ACID |
| 1M+ | Qdrant | Dedicated, distributed |

---

## See Also

- `spec/v-gents/core.md` — Core protocol and types
- `spec/v-gents/integrations.md` — Cross-agent integration
- `spec/d-gents/architecture.md` — D-gent projection lattice (analogous pattern)
