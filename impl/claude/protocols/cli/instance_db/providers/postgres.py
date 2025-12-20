"""
PostgreSQL-based Storage Providers.

Production-grade implementations of the repository interfaces:
- PostgresRelationalStore: Core state storage with connection pooling
- PostgresVectorStore: pgvector-based similarity search (future)

Environment Variables (checked in order):
- KGENTS_DATABASE_URL: Canonical URL (postgresql+asyncpg://...)
- KGENTS_POSTGRES_URL: Legacy URL (postgresql://...) - DEPRECATED

These providers enable crown jewels to persist to Postgres when available.
"""

from __future__ import annotations

import asyncio
import os
import re
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncIterator

# Optional asyncpg import
try:
    import asyncpg
    from asyncpg import Connection, Pool

    ASYNCPG_AVAILABLE = True
except ImportError:
    asyncpg = None
    Pool = Any
    Connection = Any
    ASYNCPG_AVAILABLE = False

if TYPE_CHECKING:
    from ..interfaces import IRelationalStore

# Environment variable for Postgres connection
ENV_POSTGRES_URL = "KGENTS_POSTGRES_URL"


class PostgresRelationalStore:
    """
    PostgreSQL-based relational store with connection pooling.

    Features:
    - Named parameter support (:name syntax, converted to $N)
    - Connection pooling via asyncpg
    - Transaction support with auto-commit/rollback
    - ACID guarantees

    Usage:
        url = os.environ.get("KGENTS_POSTGRES_URL")
        store = PostgresRelationalStore(url)
        await store.execute(
            "INSERT INTO captures (id, content) VALUES (:id, :content)",
            {"id": "capture_1", "content": "Hello World"}
        )
    """

    def __init__(
        self,
        url: str,
        min_pool_size: int = 2,
        max_pool_size: int = 10,
        namespace: str = "kgents",
    ):
        """
        Initialize PostgreSQL store.

        Args:
            url: PostgreSQL connection URL
            min_pool_size: Minimum connections in pool
            max_pool_size: Maximum connections in pool
            namespace: Schema namespace (currently unused, for future multi-tenant)
        """
        if not ASYNCPG_AVAILABLE:
            raise ImportError(
                "asyncpg is required for PostgresRelationalStore. Install with: pip install asyncpg"
            )

        self._url = url
        self._min_pool_size = min_pool_size
        self._max_pool_size = max_pool_size
        self._namespace = namespace

        self._pool: Pool | None = None
        self._init_lock = asyncio.Lock()

    async def _ensure_pool(self) -> Pool:
        """Get or create the connection pool."""
        if self._pool is None:
            async with self._init_lock:
                if self._pool is None:
                    self._pool = await asyncpg.create_pool(
                        self._url,
                        min_size=self._min_pool_size,
                        max_size=self._max_pool_size,
                    )
        return self._pool

    def _convert_params(self, query: str, params: dict[str, Any] | None) -> tuple[str, list[Any]]:
        """
        Convert :name params to $N placeholders for PostgreSQL.

        Example:
            "INSERT INTO foo (id, name) VALUES (:id, :name)"
            {"id": 1, "name": "test"}
            →
            "INSERT INTO foo (id, name) VALUES ($1, $2)"
            [1, "test"]
        """
        if params is None:
            return query, []

        # Find all :name patterns (but not ::cast)
        pattern = re.compile(r"(?<!:):(\w+)")
        names = pattern.findall(query)

        # Track unique names in order
        seen_names: list[str] = []
        name_to_idx: dict[str, int] = {}

        for name in names:
            if name not in name_to_idx:
                name_to_idx[name] = len(seen_names) + 1
                seen_names.append(name)

        # Replace :name with $N
        def replacer(match: re.Match[str]) -> str:
            name = match.group(1)
            return f"${name_to_idx[name]}"

        converted_query = pattern.sub(replacer, query)

        # Build positional params in order
        positional = [params.get(name) for name in seen_names]

        return converted_query, positional

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        """Execute query, return rows affected."""
        pool = await self._ensure_pool()

        # Check if this is a multi-statement script
        semicolon_count = query.count(";")
        if semicolon_count > 1 and params is None:
            # Execute each statement separately
            async with pool.acquire() as conn:
                statements = [s.strip() for s in query.split(";") if s.strip()]
                for stmt in statements:
                    await conn.execute(stmt)
                return 0

        converted_query, positional = self._convert_params(query, params)

        async with pool.acquire() as conn:
            result = await conn.execute(converted_query, *positional)
            # asyncpg returns "INSERT 0 1" or "UPDATE 3" etc.
            # Extract the number
            try:
                return int(result.split()[-1])
            except (ValueError, IndexError):
                return 0

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Fetch single row as dict."""
        pool = await self._ensure_pool()
        converted_query, positional = self._convert_params(query, params)

        async with pool.acquire() as conn:
            row = await conn.fetchrow(converted_query, *positional)
            if row is None:
                return None
            return dict(row)

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Fetch all rows as list of dicts."""
        pool = await self._ensure_pool()
        converted_query, positional = self._convert_params(query, params)

        async with pool.acquire() as conn:
            rows = await conn.fetch(converted_query, *positional)
            return [dict(row) for row in rows]

    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        """Execute query for each param set (batch insert/update)."""
        if not params_list:
            return 0

        pool = await self._ensure_pool()

        # Convert first param set to get the query pattern
        converted_query, _ = self._convert_params(query, params_list[0])

        # Get param names from query
        pattern = re.compile(r"(?<!:):(\w+)")
        names = pattern.findall(query)

        # Build unique names in order
        seen: list[str] = []
        for name in names:
            if name not in seen:
                seen.append(name)

        # Convert all param sets to positional
        positional_list = [tuple(params.get(name) for name in seen) for params in params_list]

        async with pool.acquire() as conn:
            # asyncpg doesn't have executemany, use copy for bulk inserts
            # or execute in a transaction for smaller batches
            async with conn.transaction():
                for positional in positional_list:
                    await conn.execute(converted_query, *positional)

            return len(params_list)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["IRelationalStore"]:
        """Begin transaction with auto-commit/rollback."""
        pool = await self._ensure_pool()

        async with pool.acquire() as conn:
            tx = _PostgresTransaction(conn, self._convert_params)
            async with conn.transaction():
                yield tx  # type: ignore[misc]

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def health_check(self) -> dict[str, Any]:
        """Check database health and return stats."""
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            # Simple health check
            result = await conn.fetchval("SELECT 1")
            return {
                "connected": result == 1,
                "pool_size": pool.get_size(),
                "pool_min": self._min_pool_size,
                "pool_max": self._max_pool_size,
            }

    def __repr__(self) -> str:
        # Don't expose connection URL (may contain password)
        return f"PostgresRelationalStore(namespace={self._namespace!r})"


class _PostgresTransaction:
    """Transaction-scoped store for nested operations."""

    def __init__(
        self,
        conn: Connection,
        convert_params: Any,
    ) -> None:
        self._conn = conn
        self._convert_params = convert_params

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        converted_query, positional = self._convert_params(query, params)
        result = await self._conn.execute(converted_query, *positional)
        try:
            return int(result.split()[-1])
        except (ValueError, IndexError):
            return 0

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        converted_query, positional = self._convert_params(query, params)
        row = await self._conn.fetchrow(converted_query, *positional)
        return dict(row) if row else None

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        converted_query, positional = self._convert_params(query, params)
        rows = await self._conn.fetch(converted_query, *positional)
        return [dict(row) for row in rows]

    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        if not params_list:
            return 0
        converted_query, _ = self._convert_params(query, params_list[0])
        pattern = re.compile(r"(?<!:):(\w+)")
        names = pattern.findall(query)
        seen: list[str] = []
        for name in names:
            if name not in seen:
                seen.append(name)
        for params in params_list:
            positional = tuple(params.get(name) for name in seen)
            await self._conn.execute(converted_query, *positional)
        return len(params_list)


# =============================================================================
# Factory Functions
# =============================================================================


def get_postgres_url() -> str | None:
    """
    Get Postgres URL from environment.

    Checks in order:
    1. KGENTS_DATABASE_URL (canonical) - strips async driver prefix for asyncpg
    2. KGENTS_POSTGRES_URL (legacy)

    Returns:
        Postgres URL in asyncpg format (postgresql://...), or None if not set.
    """
    # Check canonical URL first
    if url := os.environ.get("KGENTS_DATABASE_URL"):
        if url.startswith("postgresql"):
            # Strip async driver prefix for asyncpg direct use
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        # Not a Postgres URL, fall through to check legacy
        return None

    # Check legacy URL
    return os.environ.get(ENV_POSTGRES_URL)


def is_postgres_available() -> bool:
    """Check if Postgres is available (asyncpg installed + URL set)."""
    return ASYNCPG_AVAILABLE and get_postgres_url() is not None


async def create_postgres_store() -> PostgresRelationalStore | None:
    """
    Create a PostgresRelationalStore if available.

    Returns:
        PostgresRelationalStore if Postgres is configured, None otherwise.
    """
    url = get_postgres_url()
    if url is None:
        return None

    if not ASYNCPG_AVAILABLE:
        return None

    return PostgresRelationalStore(url)
