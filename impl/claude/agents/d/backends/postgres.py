"""
PostgresBackend: PostgreSQL database storage for D-gent.

Tier 3-4 in the projection lattice. Production-grade, highly durable.

Requires: asyncpg (optional dependency)
Connection: KGENTS_POSTGRES_URL environment variable

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import asyncio
import base64
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

try:
    import asyncpg
    from asyncpg import Pool, Connection

    ASYNCPG_AVAILABLE = True
except ImportError:
    asyncpg = None  # type: ignore
    Pool = Any  # type: ignore
    Connection = Any  # type: ignore
    ASYNCPG_AVAILABLE = False

from ..datum import Datum
from ..protocol import BaseDgent

SCHEMA: str = """
CREATE TABLE IF NOT EXISTS data (
    id TEXT PRIMARY KEY,
    content BYTEA NOT NULL,
    created_at DOUBLE PRECISION NOT NULL,
    causal_parent TEXT REFERENCES data(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_data_created ON data(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_parent ON data(causal_parent) WHERE causal_parent IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_data_id_prefix ON data(id text_pattern_ops);
"""


class PostgresBackend(BaseDgent):
    """
    PostgreSQL database backend using asyncpg.

    - Production-grade: Connection pooling, prepared statements
    - ACID: Full transaction support
    - Durable: WAL, replication support
    - Queryable: Full SQL including JSONB queries

    Schema:
        CREATE TABLE data (
            id TEXT PRIMARY KEY,
            content BYTEA NOT NULL,
            created_at DOUBLE PRECISION NOT NULL,
            causal_parent TEXT REFERENCES data(id),
            metadata JSONB DEFAULT '{}'
        );

    Connection: Set KGENTS_POSTGRES_URL environment variable.
    """

    def __init__(
        self,
        url: str,
        namespace: str = "default",
        min_pool_size: int = 2,
        max_pool_size: int = 10,
    ) -> None:
        """
        Initialize PostgreSQL backend.

        Args:
            url: PostgreSQL connection URL (e.g., postgresql://user:pass@host:port/db)
            namespace: Namespace for this data store (used as schema prefix)
            min_pool_size: Minimum connections in pool
            max_pool_size: Maximum connections in pool
        """
        if not ASYNCPG_AVAILABLE:
            raise ImportError(
                "asyncpg is required for PostgresBackend. "
                "Install with: pip install asyncpg"
            )

        self.url = url
        self.namespace = namespace
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size

        self._pool: Pool | None = None
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_pool(self) -> Pool:
        """Get or create the connection pool."""
        if self._pool is None:
            async with self._init_lock:
                if self._pool is None:
                    self._pool = await asyncpg.create_pool(
                        self.url,
                        min_size=self.min_pool_size,
                        max_size=self.max_pool_size,
                    )
        return self._pool

    async def _ensure_schema(self) -> None:
        """Create schema if not exists."""
        if self._initialized:
            return

        # First ensure pool exists (outside the lock to avoid deadlock)
        pool = await self._ensure_pool()

        async with self._init_lock:
            if self._initialized:
                return

            async with pool.acquire() as conn:
                # Execute each statement separately (asyncpg doesn't support multi-statement)
                statements = [s.strip() for s in SCHEMA.split(";") if s.strip()]
                for stmt in statements:
                    await conn.execute(stmt)

            self._initialized = True

    @asynccontextmanager
    async def _connection(self) -> AsyncGenerator[Connection, None]:
        """Get a connection from the pool."""
        await self._ensure_schema()
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            yield conn

    def _row_to_datum(self, row: asyncpg.Record) -> Datum:
        """Convert a database row to Datum."""
        metadata = row["metadata"] or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        return Datum(
            id=row["id"],
            content=bytes(row["content"]),
            created_at=row["created_at"],
            causal_parent=row["causal_parent"],
            metadata=metadata,
        )

    async def put(self, datum: Datum) -> str:
        """Store datum in PostgreSQL database."""
        async with self._connection() as conn:
            metadata_json = json.dumps(datum.metadata) if datum.metadata else "{}"

            await conn.execute(
                """
                INSERT INTO data (id, content, created_at, causal_parent, metadata)
                VALUES ($1, $2, $3, $4, $5::jsonb)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    created_at = EXCLUDED.created_at,
                    causal_parent = EXCLUDED.causal_parent,
                    metadata = EXCLUDED.metadata
                """,
                datum.id,
                datum.content,
                datum.created_at,
                datum.causal_parent,
                metadata_json,
            )

            return datum.id

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from PostgreSQL database."""
        async with self._connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM data WHERE id = $1",
                id,
            )

            if row is None:
                return None

            return self._row_to_datum(row)

    async def delete(self, id: str) -> bool:
        """Delete datum from PostgreSQL database."""
        async with self._connection() as conn:
            result = await conn.execute(
                "DELETE FROM data WHERE id = $1",
                id,
            )

            # asyncpg returns "DELETE X" where X is row count
            return result == "DELETE 1"

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[Datum]:
        """List data with filters, sorted by created_at descending."""
        async with self._connection() as conn:
            query = "SELECT * FROM data WHERE 1=1"
            params: list[Any] = []
            param_idx = 1

            if prefix is not None:
                query += f" AND id LIKE ${param_idx}"
                params.append(f"{prefix}%")
                param_idx += 1

            if after is not None:
                query += f" AND created_at > ${param_idx}"
                params.append(after)
                param_idx += 1

            query += f" ORDER BY created_at DESC LIMIT ${param_idx}"
            params.append(limit)

            rows = await conn.fetch(query, *params)
            return [self._row_to_datum(row) for row in rows]

    async def causal_chain(self, id: str) -> list[Datum]:
        """Get causal ancestors of a datum using recursive CTE."""
        async with self._connection() as conn:
            # Use recursive CTE to get full chain
            rows = await conn.fetch(
                """
                WITH RECURSIVE chain AS (
                    SELECT id, content, created_at, causal_parent, metadata, 0 as depth
                    FROM data
                    WHERE id = $1

                    UNION ALL

                    SELECT d.id, d.content, d.created_at, d.causal_parent, d.metadata, c.depth + 1
                    FROM data d
                    INNER JOIN chain c ON d.id = c.causal_parent
                )
                SELECT id, content, created_at, causal_parent, metadata
                FROM chain
                ORDER BY depth DESC
                """,
                id,
            )

            return [self._row_to_datum(row) for row in rows]

    async def exists(self, id: str) -> bool:
        """Check existence efficiently."""
        async with self._connection() as conn:
            result = await conn.fetchval(
                "SELECT 1 FROM data WHERE id = $1 LIMIT 1",
                id,
            )
            return result is not None

    async def count(self) -> int:
        """Count data efficiently."""
        async with self._connection() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM data")
            return result or 0

    async def vacuum(self) -> None:
        """
        Vacuum the database to reclaim space.

        Note: VACUUM in PostgreSQL cannot run inside a transaction.
        """
        async with self._connection() as conn:
            # VACUUM cannot be run in a transaction
            await conn.execute("VACUUM ANALYZE data")

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            self._initialized = False

    async def health_check(self) -> dict[str, Any]:
        """Check database health and return stats."""
        async with self._connection() as conn:
            # Get basic stats
            count = await conn.fetchval("SELECT COUNT(*) FROM data")
            size = await conn.fetchval(
                "SELECT pg_total_relation_size('data')"
            )

            return {
                "connected": True,
                "count": count or 0,
                "size_bytes": size or 0,
                "pool_size": self._pool.get_size() if self._pool else 0,
                "pool_min": self.min_pool_size,
                "pool_max": self.max_pool_size,
            }

    def __repr__(self) -> str:
        # Don't expose connection URL (may contain password)
        return f"PostgresBackend(namespace={self.namespace!r})"

    async def __aenter__(self) -> "PostgresBackend":
        """Async context manager entry."""
        await self._ensure_schema()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
