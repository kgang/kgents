"""
PatternStore: Qdrant-backed semantic pattern storage.

Provides semantic search over HypnagogicCycle patterns using the Database Triad:
- PostgreSQL for durable storage (via SQLPersonaGarden)
- Qdrant for semantic similarity search (ASSOCIATOR)
- Redis for hot pattern cache (SPARK)

Key capability: Find semantically similar patterns even if the words differ.

Usage:
    from agents.k.pattern_store import PatternStore, get_pattern_store

    store = await get_pattern_store()
    await store.index_pattern(pattern)
    similar = await store.find_similar("categorical reasoning", top_k=5)

AGENTESE: self.soul.patterns.resonance
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Protocol

from .hypnagogia import Pattern, PatternMaturity

logger = logging.getLogger(__name__)


# =============================================================================
# Protocols
# =============================================================================


class EmbeddingProvider(Protocol):
    """Protocol for computing embeddings."""

    async def embed(self, text: str) -> list[float]:
        """Compute embedding vector for text."""
        ...


class VectorClient(Protocol):
    """Protocol for vector operations."""

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Upsert a vector with payload."""
        ...

    async def delete(self, collection: str, id: str) -> None:
        """Delete a vector by ID."""
        ...

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int,
        filter_: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        ...


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class PatternStoreConfig:
    """Configuration for the pattern store."""

    # Qdrant settings
    qdrant_url: str = "http://localhost:6333"
    collection: str = "kgent_patterns"

    # Embedding settings
    embedding_provider: str = "mock"  # mock, openai
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimension: int = 1536

    # Search settings
    default_top_k: int = 5
    similarity_threshold: float = 0.7

    # Caching
    use_cache: bool = False
    cache_ttl_seconds: int = 300

    @classmethod
    def from_env(cls) -> "PatternStoreConfig":
        """Load configuration from environment."""
        return cls(
            qdrant_url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
            collection=os.environ.get("PATTERN_COLLECTION", "kgent_patterns"),
            embedding_provider=os.environ.get("EMBEDDING_PROVIDER", "mock"),
            embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-ada-002"),
            embedding_dimension=int(os.environ.get("EMBEDDING_DIMENSION", "1536")),
        )


# =============================================================================
# Search Results
# =============================================================================


@dataclass
class PatternMatch:
    """A pattern match from semantic search."""

    pattern: Pattern
    score: float  # Similarity score 0-1
    id: str

    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence match."""
        return self.score >= 0.85


@dataclass
class SearchResult:
    """Result of a pattern search."""

    query: str
    matches: list[PatternMatch]
    search_time_ms: float
    total_indexed: int

    @property
    def has_matches(self) -> bool:
        return len(self.matches) > 0

    @property
    def best_match(self) -> PatternMatch | None:
        return self.matches[0] if self.matches else None


# =============================================================================
# Mock Implementations
# =============================================================================


class MockEmbedder:
    """Mock embedder for testing."""

    def __init__(self, dimension: int = 1536) -> None:
        self._dimension = dimension

    async def embed(self, text: str) -> list[float]:
        """Create deterministic mock embedding."""
        seed = hash(text) % 10000
        return [float(seed + i) / 10000 for i in range(self._dimension)]


class MockVectorClient:
    """Mock Qdrant client for testing."""

    def __init__(self) -> None:
        self._collections: dict[str, dict[str, tuple[list[float], dict[str, Any]]]] = {}

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        if collection not in self._collections:
            self._collections[collection] = {}
        self._collections[collection][id] = (vector, payload)

    async def delete(self, collection: str, id: str) -> None:
        if collection in self._collections:
            self._collections[collection].pop(id, None)

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int,
        filter_: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if collection not in self._collections:
            return []

        results: list[dict[str, Any]] = []
        for id_, (vector, payload) in self._collections[collection].items():
            # Simple cosine similarity approximation
            dot = sum(q * v for q, v in zip(query_vector, vector))
            mag_q = sum(q**2 for q in query_vector) ** 0.5
            mag_v = sum(v**2 for v in vector) ** 0.5
            score: float = dot / (mag_q * mag_v) if mag_q * mag_v > 0 else 0.0

            results.append(
                {
                    "id": id_,
                    "score": score,
                    "payload": payload,
                }
            )

        # Sort by score descending (cast to handle dict value type)
        def get_score(x: dict[str, Any]) -> float:
            return float(x.get("score", 0.0))

        results.sort(key=get_score, reverse=True)
        return results[:top_k]


# =============================================================================
# Qdrant Implementation
# =============================================================================


class QdrantVectorClient:
    """Real Qdrant client implementation."""

    def __init__(self, url: str, collection: str, dimension: int = 1536) -> None:
        self._url = url
        self._collection = collection
        self._dimension = dimension
        self._client: Any = None

    async def connect(self) -> None:
        """Connect to Qdrant and ensure collection exists."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            self._client = QdrantClient(url=self._url)

            # Ensure collection exists
            collections = self._client.get_collections().collections
            if not any(c.name == self._collection for c in collections):
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(
                        size=self._dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {self._collection}")

            logger.info(f"Connected to Qdrant at {self._url}")

        except ImportError:
            raise RuntimeError("qdrant-client required: pip install qdrant-client")

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        if self._client is None:
            await self.connect()

        from qdrant_client.models import PointStruct

        self._client.upsert(
            collection_name=collection,
            points=[PointStruct(id=id, vector=vector, payload=payload)],
        )

    async def delete(self, collection: str, id: str) -> None:
        if self._client is None:
            await self.connect()

        from qdrant_client.models import PointIdsList

        self._client.delete(
            collection_name=collection,
            points_selector=PointIdsList(points=[id]),
        )

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int,
        filter_: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if self._client is None:
            await self.connect()

        results = self._client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload,
            }
            for r in results
        ]


# =============================================================================
# OpenAI Embedder
# =============================================================================


class OpenAIEmbedder:
    """OpenAI embeddings provider."""

    def __init__(self, model: str = "text-embedding-ada-002") -> None:
        self._model = model
        self._client: Any = None

    async def connect(self) -> None:
        """Initialize OpenAI client."""
        try:
            import openai

            self._client = openai
            logger.info(f"Using OpenAI embeddings: {self._model}")
        except ImportError:
            raise RuntimeError("openai required: pip install openai")

    async def embed(self, text: str) -> list[float]:
        """Compute embedding using OpenAI API."""
        if self._client is None:
            await self.connect()

        response = self._client.embeddings.create(
            input=text,
            model=self._model,
        )
        return list(response.data[0].embedding)


# =============================================================================
# Pattern Store
# =============================================================================


class PatternStore:
    """
    Semantic pattern storage backed by Qdrant.

    Enables finding semantically similar patterns across K-gent's
    accumulated knowledge, even when the exact words differ.

    Example:
        >>> store = await PatternStore.create()
        >>> await store.index_pattern(pattern)
        >>> similar = await store.find_similar("logical reasoning")
        >>> for match in similar.matches:
        ...     print(f"{match.pattern.content} ({match.score:.2f})")
    """

    def __init__(
        self,
        config: PatternStoreConfig,
        embedder: EmbeddingProvider,
        vector_client: VectorClient,
    ) -> None:
        self._config = config
        self._embedder = embedder
        self._vector_client = vector_client
        self._indexed_count = 0

    @classmethod
    async def create(
        cls,
        config: PatternStoreConfig | None = None,
    ) -> "PatternStore":
        """
        Create a PatternStore with appropriate backends.

        Automatically selects:
        - MockEmbedder/MockVectorClient if mock mode
        - OpenAI/Qdrant if production mode
        """
        cfg = config or PatternStoreConfig.from_env()

        # Select embedder (using Protocol types for flexibility)
        embedder: EmbeddingProvider
        if cfg.embedding_provider == "openai":
            openai_embedder = OpenAIEmbedder(cfg.embedding_model)
            await openai_embedder.connect()
            embedder = openai_embedder
        else:
            embedder = MockEmbedder(cfg.embedding_dimension)

        # Select vector client (using Protocol types for flexibility)
        vector_client: VectorClient
        if cfg.qdrant_url.startswith("mock://"):
            vector_client = MockVectorClient()
        else:
            qdrant_client = QdrantVectorClient(
                url=cfg.qdrant_url,
                collection=cfg.collection,
                dimension=cfg.embedding_dimension,
            )
            await qdrant_client.connect()
            vector_client = qdrant_client

        return cls(
            config=cfg,
            embedder=embedder,
            vector_client=vector_client,
        )

    async def index_pattern(self, pattern: Pattern) -> None:
        """
        Index a pattern for semantic search.

        The pattern's content is embedded and stored in Qdrant
        along with metadata for filtering.
        """
        # Compute embedding
        vector = await self._embedder.embed(pattern.content)

        # Build payload
        payload = {
            "content": pattern.content,
            "maturity": pattern.maturity.value,
            "occurrences": pattern.occurrences,
            "first_seen": pattern.first_seen.isoformat(),
            "last_seen": pattern.last_seen.isoformat(),
            "evidence": pattern.evidence[:10],  # Limit evidence size
            "eigenvector_affinities": pattern.eigenvector_affinities,
        }

        # Upsert to Qdrant
        await self._vector_client.upsert(
            collection=self._config.collection,
            id=pattern.id,
            vector=vector,
            payload=payload,
        )

        self._indexed_count += 1
        logger.debug(f"Indexed pattern: {pattern.id}")

    async def remove_pattern(self, pattern_id: str) -> None:
        """Remove a pattern from the index."""
        await self._vector_client.delete(
            collection=self._config.collection,
            id=pattern_id,
        )
        self._indexed_count -= 1

    async def find_similar(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
        maturity_filter: PatternMaturity | None = None,
    ) -> SearchResult:
        """
        Find patterns semantically similar to the query.

        Args:
            query: Natural language query
            top_k: Maximum results to return
            min_score: Minimum similarity score (0-1)
            maturity_filter: Only return patterns of this maturity

        Returns:
            SearchResult with matching patterns
        """
        start_time = time.time()

        # Compute query embedding
        query_vector = await self._embedder.embed(query)

        # Build filter
        filter_: dict[str, Any] | None = None
        if maturity_filter:
            filter_ = {"maturity": maturity_filter.value}

        # Search
        k = top_k or self._config.default_top_k
        results = await self._vector_client.search(
            collection=self._config.collection,
            query_vector=query_vector,
            top_k=k,
            filter_=filter_,
        )

        # Convert to PatternMatch objects
        threshold = min_score or self._config.similarity_threshold
        matches: list[PatternMatch] = []

        for r in results:
            if r["score"] < threshold:
                continue

            payload = r["payload"]
            pattern = Pattern(
                content=payload["content"],
                occurrences=payload.get("occurrences", 1),
                maturity=PatternMaturity(payload.get("maturity", "seed")),
                first_seen=datetime.fromisoformat(payload["first_seen"]),
                last_seen=datetime.fromisoformat(payload["last_seen"]),
                evidence=payload.get("evidence", []),
                eigenvector_affinities=payload.get("eigenvector_affinities", {}),
            )

            matches.append(
                PatternMatch(
                    pattern=pattern,
                    score=r["score"],
                    id=r["id"],
                )
            )

        elapsed_ms = (time.time() - start_time) * 1000

        return SearchResult(
            query=query,
            matches=matches,
            search_time_ms=elapsed_ms,
            total_indexed=self._indexed_count,
        )

    async def index_all_patterns(self, patterns: dict[str, Pattern]) -> int:
        """
        Index all patterns from a HypnagogicCycle.

        Args:
            patterns: Dictionary of pattern_id -> Pattern

        Returns:
            Number of patterns indexed
        """
        count = 0
        for pattern in patterns.values():
            if pattern.maturity != PatternMaturity.COMPOST:
                await self.index_pattern(pattern)
                count += 1
        return count

    async def find_related_to_eigenvector(
        self,
        eigenvector: str,
        threshold: float = 0.3,
    ) -> list[PatternMatch]:
        """
        Find patterns with affinity to a specific eigenvector.

        Args:
            eigenvector: Eigenvector name (e.g., "categorical", "aesthetic")
            threshold: Minimum affinity score

        Returns:
            Patterns with affinity to this eigenvector
        """
        # This requires a filter query on eigenvector_affinities
        # For now, do a broad search and filter client-side
        result = await self.find_similar(
            query=eigenvector,
            top_k=50,
            min_score=0.0,
        )

        return [
            m
            for m in result.matches
            if m.pattern.eigenvector_affinities.get(eigenvector, 0) >= threshold
        ]

    @property
    def indexed_count(self) -> int:
        """Number of indexed patterns."""
        return self._indexed_count


# =============================================================================
# Factory Functions
# =============================================================================


_store_instance: PatternStore | None = None


async def get_pattern_store(
    config: PatternStoreConfig | None = None,
) -> PatternStore:
    """Get or create the global PatternStore instance."""
    global _store_instance

    if _store_instance is None:
        _store_instance = await PatternStore.create(config)

    return _store_instance


async def close_pattern_store() -> None:
    """Close the global PatternStore instance."""
    global _store_instance
    _store_instance = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PatternStore",
    "PatternStoreConfig",
    "PatternMatch",
    "SearchResult",
    "get_pattern_store",
    "close_pattern_store",
]
