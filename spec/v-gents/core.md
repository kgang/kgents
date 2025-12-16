# V-gent Core: Vector Agents for Semantic Search

> *"V-gent is geometry. It maps meaning to distance."*

**Status**: NEW — Clean separation of vector operations from L-gent catalog.

---

## Purpose

V-gent provides **semantic vector operations** as a dedicated agent genus. Previously, vector operations were embedded within L-gent (Library), but this conflated two distinct concerns:

| Concern | Agent | Responsibility |
|---------|-------|----------------|
| **Semantic Catalog** | L-gent | Knowledge curation, lineage, lattice |
| **Vector Operations** | V-gent | Embeddings, similarity search, indexing |

The key insight: **vectors are infrastructure, not knowledge**. L-gent is a librarian; V-gent is the filing system.

---

## The Core Abstraction

```python
@dataclass
class Embedding:
    """
    A semantic vector with dimension and optional metadata.

    Embeddings capture meaning in geometric space.
    Similar meanings → nearby vectors.
    """
    vector: tuple[float, ...]   # Immutable for hashability
    dimension: int              # len(vector)
    source: str                 # What generated this ("openai/text-embedding-3-small", "local/hash", etc.)
    metadata: dict[str, str]    # Optional: model version, timestamp, etc.

    def __post_init__(self):
        if len(self.vector) != self.dimension:
            raise ValueError(f"Vector length {len(self.vector)} != dimension {self.dimension}")

    def similarity(self, other: "Embedding", metric: "DistanceMetric" = None) -> float:
        """Compute similarity to another embedding."""
        if self.dimension != other.dimension:
            raise ValueError("Dimension mismatch")
        metric = metric or DistanceMetric.COSINE
        return metric.similarity(self.vector, other.vector)


class DistanceMetric(Enum):
    """Distance metrics for vector comparison."""

    COSINE = "cosine"           # Most common for text embeddings
    EUCLIDEAN = "euclidean"     # Geometric distance
    DOT_PRODUCT = "dot_product" # Fast, assumes normalized vectors
    MANHATTAN = "manhattan"     # L1 norm (sparse data)

    def similarity(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """Compute similarity (higher = more similar)."""
        if self == DistanceMetric.COSINE:
            return _cosine_similarity(a, b)
        elif self == DistanceMetric.DOT_PRODUCT:
            return _dot_product(a, b)
        elif self == DistanceMetric.EUCLIDEAN:
            # Convert distance to similarity: 1 / (1 + distance)
            return 1.0 / (1.0 + _euclidean_distance(a, b))
        elif self == DistanceMetric.MANHATTAN:
            return 1.0 / (1.0 + _manhattan_distance(a, b))
        raise ValueError(f"Unknown metric: {self}")
```

---

## The VectorIndex

```python
@dataclass
class VectorEntry:
    """
    A vector stored in an index with its identifier.
    """
    id: str                     # Unique identifier
    embedding: Embedding        # The vector
    metadata: dict[str, str]    # Filterable metadata


@dataclass
class SearchResult:
    """
    Result from a vector search.
    """
    id: str                     # Entry identifier
    similarity: float           # Similarity score (0.0 to 1.0)
    distance: float             # Raw distance (metric-dependent)
    metadata: dict[str, str]    # Entry metadata


class VectorIndex:
    """
    A searchable collection of vectors.

    This is the core V-gent abstraction. A VectorIndex:
    - Stores vectors with IDs and metadata
    - Supports similarity search
    - Supports metadata filtering
    - May be backed by memory, disk, or external service
    """

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this index."""
        ...

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        ...

    @property
    def count(self) -> int:
        """Number of vectors in the index."""
        ...
```

---

## The Protocol

```python
@runtime_checkable
class VgentProtocol(Protocol):
    """
    The minimal interface every V-gent backend implements.

    Seven methods for vector operations:
    - add: Insert vector with ID and metadata
    - add_batch: Insert multiple vectors efficiently
    - search: Find similar vectors
    - get: Retrieve vector by ID
    - remove: Delete vector by ID
    - clear: Remove all vectors
    - count: Get number of vectors
    """

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        ...

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        ...

    # --- Write Operations ---

    async def add(
        self,
        id: str,
        embedding: Embedding | list[float],
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Add a vector to the index.

        Args:
            id: Unique identifier for this vector
            embedding: The vector (Embedding or raw list)
            metadata: Optional filterable metadata

        Returns:
            The ID (same as input, for chaining)

        Note:
            If ID already exists, the vector is updated.
        """
        ...

    async def add_batch(
        self,
        entries: list[tuple[str, Embedding | list[float], dict[str, str] | None]],
    ) -> list[str]:
        """
        Add multiple vectors efficiently.

        Args:
            entries: List of (id, embedding, metadata) tuples

        Returns:
            List of IDs added

        Note:
            More efficient than repeated add() calls for bulk ingestion.
        """
        ...

    async def remove(self, id: str) -> bool:
        """
        Remove a vector by ID.

        Args:
            id: The vector ID to remove

        Returns:
            True if removed, False if not found
        """
        ...

    async def clear(self) -> int:
        """
        Remove all vectors from the index.

        Returns:
            Number of vectors removed
        """
        ...

    # --- Read Operations ---

    async def get(self, id: str) -> VectorEntry | None:
        """
        Retrieve a vector by ID.

        Args:
            id: The vector ID

        Returns:
            VectorEntry if found, None otherwise
        """
        ...

    async def search(
        self,
        query: Embedding | list[float],
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """
        Find similar vectors.

        Args:
            query: The query vector
            limit: Maximum results to return
            filters: Optional metadata filters (exact match)
            threshold: Optional minimum similarity (0.0 to 1.0)

        Returns:
            List of SearchResult, sorted by similarity (highest first)
        """
        ...

    async def count(self) -> int:
        """
        Get number of vectors in the index.

        Returns:
            Total vector count
        """
        ...

    # --- Introspection ---

    async def exists(self, id: str) -> bool:
        """
        Check if a vector exists.

        Args:
            id: The vector ID

        Returns:
            True if exists, False otherwise
        """
        ...
```

---

## The Embedder Protocol

V-gent is agnostic to how embeddings are generated. Any embedder can be used:

```python
class EmbedderProtocol(Protocol):
    """
    Protocol for embedding generators.

    V-gent doesn't generate embeddings—it stores and searches them.
    This protocol defines what an embedder must provide.
    """

    @property
    def dimension(self) -> int:
        """Output dimension of embeddings."""
        ...

    @property
    def source(self) -> str:
        """Identifier for this embedder (e.g., "openai/text-embedding-3-small")."""
        ...

    async def embed(self, text: str) -> Embedding:
        """
        Generate embedding for text.

        Args:
            text: Input text to embed

        Returns:
            Embedding with vector and metadata
        """
        ...

    async def embed_batch(self, texts: list[str]) -> list[Embedding]:
        """
        Generate embeddings for multiple texts.

        More efficient than repeated embed() calls.
        """
        ...
```

**Key Separation**: V-gent stores and searches vectors. Embedders create them. L-gent coordinates both.

---

## Polynomial Structure

V-gent is a **pure Agent[Query, Results]**, not a PolyAgent. It has no state-dependent behavior:

```
VgentProtocol: Query → Results
```

Where:
- **Query**: `(embedding, limit, filters, threshold)`
- **Results**: `list[SearchResult]`

The index state is implicit in the backend, not a polynomial mode. This is intentional—vector search is stateless computation over a dataset.

If state-dependent behavior is needed (e.g., adaptive indexing, query routing), wrap V-gent in a PolyAgent:

```python
# Pure V-gent: stateless search
results = await vgent.search(query)

# Wrapped in PolyAgent for adaptive routing
class AdaptiveSearchAgent(PolyAgent[SearchMode, Query, Results]):
    """Route queries based on mode: fast, accurate, hybrid."""
    ...
```

---

## Mathematical Properties

### Metric Space Laws

V-gent operates over metric spaces. The distance metric MUST satisfy:

1. **Identity**: `d(x, x) = 0`
2. **Symmetry**: `d(x, y) = d(y, x)`
3. **Triangle Inequality**: `d(x, z) ≤ d(x, y) + d(y, z)`
4. **Non-negativity**: `d(x, y) ≥ 0`

Similarity is typically `1 - d(x, y)` or `1 / (1 + d(x, y))`.

### Idempotence

`add(id, embedding)` is idempotent: calling it twice with the same id and embedding has the same effect as calling it once.

### Monotonicity

`count()` is monotonically non-decreasing under `add()`, monotonically non-increasing under `remove()`.

---

## AGENTESE Paths

V-gent exposes these paths under `self.vector.*`:

| Path | Description |
|------|-------------|
| `self.vector.add[id, embedding]` | Store vector |
| `self.vector.search[query]` | Similarity search |
| `self.vector.get[id]` | Retrieve by ID |
| `self.vector.remove[id]` | Delete by ID |
| `self.vector.clear` | Clear index |
| `self.vector.count` | Get count |
| `self.vector.dimension` | Get dimension |
| `self.vector.metric` | Get distance metric |

---

## What V-gent Is

- **Vector storage**: Efficient storage of high-dimensional vectors
- **Similarity search**: Find nearest neighbors by distance
- **Metadata filtering**: Filter results by tags/labels
- **Backend abstraction**: Same API whether memory, disk, or cloud

## What V-gent Is NOT

- **Not an embedder**: V-gent doesn't create vectors, just stores them
- **Not a catalog**: V-gent doesn't know what vectors mean, just their geometry
- **Not a database**: No schema, no transactions, no joins
- **Not memory management**: No lifecycle, no relevance decay (that's M-gent)

---

## See Also

- `spec/v-gents/backends.md` — Backend implementations (Memory, D-gent, Qdrant)
- `spec/v-gents/integrations.md` — Integration with L-gent, M-gent, D-gent
- `spec/l-gents/README.md` — L-gent uses V-gent for semantic search
- `spec/m-gents/architecture.md` — M-gent uses V-gent for associative recall
