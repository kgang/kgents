"""
PostgresVectorBackend: Native pgvector-based similarity search.

Tier 2 in the projection lattice. Uses PostgreSQL with pgvector extension.

Uses native pgvector operators:
- <-> : L2 distance
- <=> : Cosine distance (recommended for normalized embeddings)
- <#> : Inner product (negative inner product)

Characteristics:
- O(log n) search with IVFFlat index
- SQL-native filtering via WHERE clauses
- Scales to 100K-1M vectors efficiently
- Requires Postgres with pgvector extension

Requirements:
- CREATE EXTENSION IF NOT EXISTS vector;
- VECTOR(dimension) column type
- pgvector Python package

Teaching:
    gotcha: IVFFlat index needs sufficient data for good clustering.
            For small datasets (<10K), exact search may be faster.

    gotcha: Cosine distance (<=>)  returns distance (lower = more similar).
            Cosine similarity = 1 - cosine_distance.

    gotcha: pgvector stores vectors as arrays, not numpy.
            Convert list[float] → list before storing.

See: plans/pgvector-integration.md
See: spec/protocols/trail-protocol.md 4.1
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..protocol import BaseVgent
from ..types import DistanceMetric, Embedding, SearchResult, VectorEntry

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def is_pgvector_available() -> bool:
    """Check if pgvector package is installed."""
    try:
        import pgvector  # noqa: F401

        return True
    except ImportError:
        return False


# pgvector is required for PostgresVectorBackend
from pgvector.sqlalchemy import Vector


class PostgresVectorBackend(BaseVgent):
    """
    Vector storage backed by PostgreSQL with pgvector extension.

    Tier 2 in the projection lattice. Supports 100K-1M vectors with SQL filtering.

    This backend uses raw SQL for vector operations because:
    1. pgvector operators (<=> for cosine) aren't well-supported in SQLAlchemy ORM
    2. Direct SQL is more explicit and easier to debug
    3. Performance-critical path benefits from minimal abstraction

    Example:
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

        engine = create_async_engine("postgresql+asyncpg://...")
        session_factory = async_sessionmaker(engine)

        backend = PostgresVectorBackend(
            session_factory=session_factory,
            dimension=1536,
            table_name="trail_steps",
            id_column="id",
            embedding_column="embedding",
        )

        # Add vector
        await backend.add("step-123", embedding, {"trail_id": "trail-abc"})

        # Search similar
        results = await backend.search(query_embedding, limit=10)

    Architecture:
        - Uses async SQLAlchemy session factory for connection management
        - Raw SQL with text() for pgvector operators
        - Metadata stored as JSON in a separate column
        - IVFFlat index for approximate nearest neighbor
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        dimension: int = 1536,
        metric: DistanceMetric = DistanceMetric.COSINE,
        table_name: str = "trail_steps",
        id_column: str = "id",
        embedding_column: str = "embedding",
        metadata_column: str | None = None,
    ) -> None:
        """
        Initialize PostgreSQL vector backend.

        Args:
            session_factory: SQLAlchemy async session factory
            dimension: Vector dimension (default: 1536 for OpenAI text-embedding-3-small)
            metric: Distance metric (default: COSINE)
            table_name: Table containing vector data
            id_column: Column name for vector ID
            embedding_column: Column name for vector data (VECTOR type)
            metadata_column: Optional JSONB column for metadata filtering
        """
        self._session_factory = session_factory
        self._dimension = dimension
        self._metric = metric
        self._table_name = table_name
        self._id_column = id_column
        self._embedding_column = embedding_column
        self._metadata_column = metadata_column

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        return self._dimension

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        return self._metric

    def _get_distance_operator(self) -> str:
        """Get pgvector operator for the configured metric."""
        if self._metric == DistanceMetric.COSINE:
            return "<=>"  # Cosine distance
        elif self._metric == DistanceMetric.EUCLIDEAN:
            return "<->"  # L2 distance
        elif self._metric == DistanceMetric.DOT_PRODUCT:
            return "<#>"  # Negative inner product
        else:
            # Default to cosine for unknown metrics
            return "<=>"

    def _distance_to_similarity(self, distance: float) -> float:
        """Convert pgvector distance to similarity score [0, 1]."""
        if self._metric == DistanceMetric.COSINE:
            # Cosine distance is 1 - cosine_similarity
            # So similarity = 1 - distance, clamped to [0, 1]
            return max(0.0, min(1.0, 1.0 - distance))
        elif self._metric == DistanceMetric.EUCLIDEAN:
            # Convert L2 distance to similarity: 1 / (1 + distance)
            # Clamp distance to non-negative to avoid issues
            return 1.0 / (1.0 + max(0.0, distance))
        elif self._metric == DistanceMetric.DOT_PRODUCT:
            # Negative inner product: higher = more similar
            # Normalize to [0, 1] is domain-dependent
            return max(0.0, min(1.0, -distance))
        else:
            return max(0.0, min(1.0, 1.0 - distance))

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def add(
        self,
        id: str,
        embedding: Embedding | list[float],
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Add or update a vector in the database.

        Note: This backend is designed for tables that already have rows
        (like trail_steps). It updates the embedding column on existing rows.
        For inserting new rows, use your domain-specific storage adapter.

        Args:
            id: Row identifier (primary key value)
            embedding: Vector to store
            metadata: Optional metadata (stored in metadata_column if configured)

        Returns:
            The ID
        """
        emb = self._normalize_embedding(embedding)
        vector_list = list(emb.vector)

        async with self._session_factory() as session:
            # Update existing row with embedding
            # Note: We use raw SQL because SQLAlchemy ORM doesn't handle
            # pgvector VECTOR type assignment well
            if self._metadata_column and metadata:
                # Update embedding and metadata
                await session.execute(
                    text(f"""
                        UPDATE {self._table_name}
                        SET {self._embedding_column} = :embedding,
                            {self._metadata_column} = :metadata
                        WHERE {self._id_column} = :id
                    """),
                    {
                        "id": id,
                        "embedding": str(vector_list),  # pgvector accepts string representation
                        "metadata": metadata,
                    },
                )
            else:
                # Update embedding only
                await session.execute(
                    text(f"""
                        UPDATE {self._table_name}
                        SET {self._embedding_column} = :embedding
                        WHERE {self._id_column} = :id
                    """),
                    {
                        "id": id,
                        "embedding": str(vector_list),
                    },
                )
            await session.commit()

        return id

    async def add_batch(
        self,
        entries: list[tuple[str, Embedding | list[float], dict[str, str] | None]],
    ) -> list[str]:
        """
        Add multiple vectors efficiently.

        Uses a single transaction for all updates.

        Args:
            entries: List of (id, embedding, metadata) tuples

        Returns:
            List of IDs updated
        """
        if not entries:
            return []

        async with self._session_factory() as session:
            for id, embedding, metadata in entries:
                emb = self._normalize_embedding(embedding)
                vector_list = list(emb.vector)

                if self._metadata_column and metadata:
                    await session.execute(
                        text(f"""
                            UPDATE {self._table_name}
                            SET {self._embedding_column} = :embedding,
                                {self._metadata_column} = :metadata
                            WHERE {self._id_column} = :id
                        """),
                        {
                            "id": id,
                            "embedding": str(vector_list),
                            "metadata": metadata,
                        },
                    )
                else:
                    await session.execute(
                        text(f"""
                            UPDATE {self._table_name}
                            SET {self._embedding_column} = :embedding
                            WHERE {self._id_column} = :id
                        """),
                        {
                            "id": id,
                            "embedding": str(vector_list),
                        },
                    )

            await session.commit()

        return [id for id, _, _ in entries]

    async def remove(self, id: str) -> bool:
        """
        Remove embedding from a row (set to NULL).

        Does not delete the row itself - use domain storage adapter for that.

        Args:
            id: Row identifier

        Returns:
            True if embedding was cleared, False if row not found
        """
        async with self._session_factory() as session:
            result = await session.execute(
                text(f"""
                    UPDATE {self._table_name}
                    SET {self._embedding_column} = NULL
                    WHERE {self._id_column} = :id
                    RETURNING {self._id_column}
                """),
                {"id": id},
            )
            await session.commit()
            # Check if row was found by seeing if RETURNING returned anything
            return result.fetchone() is not None

    async def clear(self) -> int:
        """
        Clear all embeddings in the table (set to NULL).

        Does not delete rows - only clears the embedding column.

        Returns:
            Number of rows updated
        """
        async with self._session_factory() as session:
            # First count how many will be affected
            count_result = await session.execute(
                text(f"""
                    SELECT COUNT(*)
                    FROM {self._table_name}
                    WHERE {self._embedding_column} IS NOT NULL
                """)
            )
            count = count_result.scalar() or 0

            # Then clear
            await session.execute(
                text(f"""
                    UPDATE {self._table_name}
                    SET {self._embedding_column} = NULL
                    WHERE {self._embedding_column} IS NOT NULL
                """)
            )
            await session.commit()
            return int(count)

    # =========================================================================
    # Read Operations
    # =========================================================================

    async def get(self, id: str) -> VectorEntry | None:
        """
        Retrieve a vector by ID.

        Args:
            id: Row identifier

        Returns:
            VectorEntry if found with embedding, None otherwise
        """
        async with self._session_factory() as session:
            result = await session.execute(
                text(f"""
                    SELECT {self._id_column}, {self._embedding_column}
                    FROM {self._table_name}
                    WHERE {self._id_column} = :id
                    AND {self._embedding_column} IS NOT NULL
                """),
                {"id": id},
            )
            row = result.fetchone()

            if row is None:
                return None

            row_id, embedding_data = row

            # pgvector returns embedding as a list
            if embedding_data is None:
                return None

            # Convert pgvector result to tuple
            if hasattr(embedding_data, "tolist"):
                vector = tuple(embedding_data.tolist())
            else:
                vector = tuple(embedding_data)

            return VectorEntry(
                id=row_id,
                embedding=Embedding(
                    vector=vector,
                    dimension=len(vector),
                    source="postgres",
                ),
                metadata={},
            )

    async def search(
        self,
        query: Embedding | list[float],
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """
        Find similar vectors using pgvector operators.

        Uses native pgvector <=> (cosine distance) operator for fast search.
        IVFFlat index provides O(log n) approximate nearest neighbor.

        Args:
            query: Query vector
            limit: Maximum results to return
            filters: Optional metadata filters (requires metadata_column)
            threshold: Optional minimum similarity (0.0 to 1.0)

        Returns:
            List of SearchResult, sorted by similarity (highest first)
        """
        query_emb = self._normalize_embedding(query)
        vector_list = list(query_emb.vector)
        operator = self._get_distance_operator()

        async with self._session_factory() as session:
            # Build query with optional filters
            base_query = f"""
                SELECT
                    {self._id_column},
                    {self._embedding_column} {operator} :query AS distance
                FROM {self._table_name}
                WHERE {self._embedding_column} IS NOT NULL
            """

            params: dict[str, str | int | float | list[float]] = {
                "query": str(vector_list),
                "limit": limit,
            }

            # Add metadata filters if configured
            # Note: This is simplified - real implementation would need
            # proper SQL injection protection and type handling
            if filters and self._metadata_column:
                for key, value in filters.items():
                    base_query += f" AND {self._metadata_column}->>'{{key}}' = :filter_{key}"
                    params[f"filter_{key}"] = value

            # Add distance threshold if specified
            if threshold is not None:
                # Convert similarity threshold to distance threshold
                distance_threshold = 1.0 - threshold
                base_query += (
                    f" AND {self._embedding_column} {operator} :query < :distance_threshold"
                )
                params["distance_threshold"] = distance_threshold

            # Order by distance (ascending) and limit
            base_query += f"""
                ORDER BY {self._embedding_column} {operator} :query
                LIMIT :limit
            """

            result = await session.execute(text(base_query), params)
            rows = result.fetchall()

        # Convert to SearchResult
        results: list[SearchResult] = []
        for row_id, distance in rows:
            similarity = self._distance_to_similarity(distance)

            # Apply threshold filter (double-check, SQL might not be exact)
            if threshold is not None and similarity < threshold:
                continue

            results.append(
                SearchResult(
                    id=row_id,
                    similarity=similarity,
                    distance=distance,
                    metadata={},
                )
            )

        return results

    async def count(self) -> int:
        """
        Get number of rows with embeddings.

        Returns:
            Count of rows where embedding IS NOT NULL
        """
        async with self._session_factory() as session:
            result = await session.execute(
                text(f"""
                    SELECT COUNT(*)
                    FROM {self._table_name}
                    WHERE {self._embedding_column} IS NOT NULL
                """)
            )
            return result.scalar() or 0

    async def exists(self, id: str) -> bool:
        """
        Check if a row has an embedding.

        Args:
            id: Row identifier

        Returns:
            True if row exists with non-null embedding
        """
        async with self._session_factory() as session:
            result = await session.execute(
                text(f"""
                    SELECT 1
                    FROM {self._table_name}
                    WHERE {self._id_column} = :id
                    AND {self._embedding_column} IS NOT NULL
                    LIMIT 1
                """),
                {"id": id},
            )
            return result.fetchone() is not None

    # =========================================================================
    # pgvector-specific Methods
    # =========================================================================

    async def check_extension(self) -> bool:
        """
        Check if pgvector extension is enabled.

        Returns:
            True if pgvector extension is available
        """
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT 1 FROM pg_extension WHERE extname = 'vector'
                """)
            )
            return result.fetchone() is not None

    async def create_extension(self) -> None:
        """
        Enable pgvector extension (requires database privileges).

        Raises:
            Exception: If user lacks CREATE EXTENSION privilege
        """
        async with self._session_factory() as session:
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await session.commit()

    async def reindex(self) -> None:
        """
        Rebuild IVFFlat index for better performance.

        Call this after bulk loading vectors for optimal clustering.
        """
        index_name = f"idx_{self._table_name}_{self._embedding_column}_vector"
        async with self._session_factory() as session:
            await session.execute(text(f"REINDEX INDEX IF EXISTS {index_name}"))
            await session.commit()

    # =========================================================================
    # Introspection
    # =========================================================================

    def __repr__(self) -> str:
        return (
            f"PostgresVectorBackend("
            f"dimension={self._dimension}, "
            f"metric={self._metric.value}, "
            f"table={self._table_name}, "
            f"column={self._embedding_column})"
        )
