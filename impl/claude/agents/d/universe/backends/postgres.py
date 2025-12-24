"""
PostgresBackend: PostgreSQL database adapter for Unified Data Crystal.

Wraps the existing agents.d.backends.PostgresBackend with the new Backend protocol.

Characteristics:
- Priority: 10 (highest - production preferred)
- Persistent: Yes (distributed, replicated)
- Available: When KGENTS_DATABASE_URL is set and reachable
- Performance: O(log n) for indexed queries, connection pooling

Use cases:
- Production deployments
- Multi-user applications
- Distributed systems
- High availability setups
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ...datum import Datum
from ..backend import BackendStats, Query

logger = logging.getLogger(__name__)

# Conditional import - asyncpg may not be installed
try:
    from ...backends.postgres import PostgresBackend as LegacyPostgresBackend

    ASYNCPG_AVAILABLE = True
except ImportError:
    LegacyPostgresBackend = None
    ASYNCPG_AVAILABLE = False


class PostgresBackend:
    """
    PostgreSQL database backend adapter.

    Wraps agents.d.backends.PostgresBackend to implement the new Backend protocol.

    Priority: 10 (highest priority - preferred for production)
    Persistent: Yes
    Available: When connection URL is provided and database is reachable
    """

    name: str = "postgres"
    priority: int = 10

    def __init__(
        self,
        url: str | None = None,
        namespace: str = "default",
        min_pool_size: int = 2,
        max_pool_size: int = 10,
    ) -> None:
        """
        Initialize PostgreSQL backend.

        Args:
            url: PostgreSQL connection URL (e.g., postgresql://user:pass@host:port/db)
                 If None, uses KGENTS_DATABASE_URL environment variable
            namespace: Namespace for this data store
            min_pool_size: Minimum connections in pool
            max_pool_size: Maximum connections in pool

        Raises:
            ImportError: If asyncpg is not installed
            ValueError: If no URL provided and KGENTS_DATABASE_URL not set
        """
        if not ASYNCPG_AVAILABLE:
            raise ImportError(
                "asyncpg is required for PostgresBackend. Install with: pip install asyncpg"
            )

        # Get URL from parameter or environment
        if url is None:
            url = os.getenv("KGENTS_DATABASE_URL")
            if url is None:
                raise ValueError(
                    "PostgreSQL URL required. Provide 'url' parameter or set KGENTS_DATABASE_URL"
                )

        # Normalize URL - asyncpg expects 'postgresql://' not 'postgresql+asyncpg://'
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://")

        self._backend = LegacyPostgresBackend(
            url=url,
            namespace=namespace,
            min_pool_size=min_pool_size,
            max_pool_size=max_pool_size,
        )
        self.namespace = namespace
        self._url = url  # Store for logging (don't expose in repr)
        logger.debug(f"PostgresBackend initialized: namespace={namespace}")

    async def store(self, datum: Datum) -> None:
        """Store datum in PostgreSQL database."""
        await self._backend.put(datum)

    async def put(self, datum: Datum) -> str:
        """Store datum and return ID. Alias for store() with return value."""
        await self._backend.put(datum)
        return datum.id

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from PostgreSQL database."""
        return await self._backend.get(id)

    async def query(self, q: Query) -> list[Datum]:
        """
        Query data in PostgreSQL with efficient SQL filtering.

        Uses JSONB operators for metadata queries and proper indexes.
        """
        async with self._backend._connection() as conn:
            # Build SQL query dynamically based on filters
            sql = "SELECT * FROM data WHERE 1=1"
            params: list[Any] = []
            param_idx = 1

            # Prefix filter (uses text_pattern_ops index)
            if q.prefix is not None:
                sql += f" AND id LIKE ${param_idx}"
                params.append(f"{q.prefix}%")
                param_idx += 1

            # Timestamp filters (uses created_at index)
            if q.after is not None:
                sql += f" AND created_at > ${param_idx}"
                params.append(q.after)
                param_idx += 1

            if q.before is not None:
                sql += f" AND created_at < ${param_idx}"
                params.append(q.before)
                param_idx += 1

            # Author filter (JSONB query)
            if q.author is not None:
                sql += f" AND metadata->>'author' = ${param_idx}"
                params.append(q.author)
                param_idx += 1

            # Source filter (JSONB query)
            if q.source is not None:
                sql += f" AND metadata->>'source' = ${param_idx}"
                params.append(q.source)
                param_idx += 1

            # Where filters (JSONB key-value pairs)
            if q.where:
                for key, value in q.where.items():
                    sql += f" AND metadata->>'{key}' = ${param_idx}"
                    params.append(value)
                    param_idx += 1

            # Order and pagination
            sql += f" ORDER BY created_at DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
            params.append(q.limit)
            params.append(q.offset)

            rows = await conn.fetch(sql, *params)
            results = [self._backend._row_to_datum(row) for row in rows]

            # Tags filter (post-filter since tags are comma-separated in metadata)
            if q.tags:
                filtered = []
                for datum in results:
                    datum_tags_str = datum.metadata.get("tags", "")
                    datum_tags = set(datum_tags_str.split(",")) if datum_tags_str else set()
                    if q.tags.issubset(datum_tags):
                        filtered.append(datum)
                return filtered

            return results

    async def delete(self, id: str) -> bool:
        """Delete datum from PostgreSQL database."""
        return await self._backend.delete(id)

    async def count(self) -> int:
        """Count total datums in PostgreSQL database."""
        return await self._backend.count()

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[Datum]:
        """List datums with optional filters."""
        return await self._backend.list(prefix=prefix, after=after, limit=limit)

    async def is_available(self) -> bool:
        """
        Check if PostgreSQL backend is available.

        Attempts to establish a connection with timeout.
        Returns True if connection succeeds, False otherwise.
        """
        try:
            # Try to get pool and execute a simple query
            pool = await self._backend._ensure_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.warning(f"PostgresBackend unavailable: {e}")
            return False

    async def stats(self) -> BackendStats:
        """Get current PostgreSQL backend statistics."""
        try:
            health = await self._backend.health_check()

            return BackendStats(
                name=self.name,
                total_datums=health["count"],
                size_bytes=health["size_bytes"],
                is_persistent=True,
                is_available=health["connected"],
            )
        except Exception as e:
            logger.error(f"Failed to get Postgres stats: {e}")
            return BackendStats(
                name=self.name,
                total_datums=0,
                size_bytes=0,
                is_persistent=True,
                is_available=False,
                error=str(e),
            )

    async def vacuum(self) -> None:
        """Vacuum the database to reclaim space."""
        await self._backend.vacuum()

    async def close(self) -> None:
        """Close the connection pool."""
        await self._backend.close()

    async def health_check(self) -> dict[str, Any]:
        """Check database health and return detailed stats."""
        return await self._backend.health_check()

    def __repr__(self) -> str:
        # Don't expose connection URL (may contain password)
        return f"PostgresBackend(namespace={self.namespace!r})"

    async def __aenter__(self) -> "PostgresBackend":
        """Async context manager entry."""
        await self._backend._ensure_schema()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
