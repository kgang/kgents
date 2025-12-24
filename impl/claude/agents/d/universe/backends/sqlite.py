"""
SQLiteBackend: SQLite database adapter for Unified Data Crystal.

Wraps the existing agents.d.backends.SQLiteBackend with the new Backend protocol.

Characteristics:
- Priority: 50 (middle - local persistence)
- Persistent: Yes (survives process restart)
- Available: When data directory is writable
- Performance: O(log n) for indexed queries

Use cases:
- Local development
- Single-user applications
- Testing with persistence
- Offline operation
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ...backends.sqlite import SQLiteBackend as LegacySQLiteBackend
from ...datum import Datum
from ..backend import BackendStats, Query

logger = logging.getLogger(__name__)


class SQLiteBackend:
    """
    SQLite database backend adapter.

    Wraps agents.d.backends.SQLiteBackend to implement the new Backend protocol.

    Priority: 50 (middle priority - preferred for local persistence)
    Persistent: Yes
    Available: When data directory is writable
    """

    name: str = "sqlite"
    priority: int = 50

    def __init__(
        self,
        namespace: str = "default",
        data_dir: Path | None = None,
    ) -> None:
        """
        Initialize SQLite backend.

        Args:
            namespace: Name for this data store (becomes filename)
            data_dir: Directory for data files (default: ~/.kgents/data/)
        """
        self._backend = LegacySQLiteBackend(namespace=namespace, data_dir=data_dir)
        self.namespace = namespace
        logger.debug(f"SQLiteBackend initialized: namespace={namespace}")

    async def store(self, datum: Datum) -> None:
        """Store datum in SQLite database."""
        await self._backend.put(datum)

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from SQLite database."""
        return await self._backend.get(id)

    async def query(self, q: Query) -> list[Datum]:
        """
        Query data in SQLite with efficient SQL filtering.

        Uses SQL WHERE clauses for efficient filtering instead of post-filtering.
        """
        async with self._backend._lock:

            def do_query() -> list[Datum]:
                with self._backend._get_connection() as conn:
                    # Build SQL query dynamically based on filters
                    sql = "SELECT * FROM data WHERE 1=1"
                    params: list[str | float] = []

                    # Prefix filter
                    if q.prefix is not None:
                        sql += " AND id LIKE ?"
                        params.append(f"{q.prefix}%")

                    # Timestamp filters
                    if q.after is not None:
                        sql += " AND created_at > ?"
                        params.append(q.after)

                    if q.before is not None:
                        sql += " AND created_at < ?"
                        params.append(q.before)

                    # Author filter (in metadata JSON)
                    if q.author is not None:
                        sql += " AND json_extract(metadata, '$.author') = ?"
                        params.append(q.author)

                    # Source filter (in metadata JSON)
                    if q.source is not None:
                        sql += " AND json_extract(metadata, '$.source') = ?"
                        params.append(q.source)

                    # Where filters (metadata key-value pairs)
                    if q.where:
                        for key, value in q.where.items():
                            sql += f" AND json_extract(metadata, '$.{key}') = ?"
                            params.append(value)

                    # Order and pagination
                    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                    params.append(q.limit)
                    params.append(q.offset)

                    cursor = conn.execute(sql, params)
                    rows = cursor.fetchall()

                    # Convert rows to data
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

            return await asyncio.to_thread(do_query)

    async def delete(self, id: str) -> bool:
        """Delete datum from SQLite database."""
        return await self._backend.delete(id)

    async def is_available(self) -> bool:
        """
        Check if SQLite backend is available.

        Returns True if data directory exists or can be created and is writable.
        """
        try:
            # Try to ensure directory exists
            self._backend._ensure_dir()

            # Check if directory is writable
            test_file = self._backend.data_dir / ".write_test"
            test_file.touch()
            test_file.unlink()

            return True
        except (OSError, PermissionError) as e:
            logger.warning(f"SQLiteBackend unavailable: {e}")
            return False

    async def stats(self) -> BackendStats:
        """Get current SQLite backend statistics."""
        try:
            count = await self._backend.count()

            # Get database file size
            size = 0
            if self._backend.path.exists():
                size = self._backend.path.stat().st_size

            return BackendStats(
                name=self.name,
                total_datums=count,
                size_bytes=size,
                is_persistent=True,
                is_available=True,
            )
        except Exception as e:
            logger.error(f"Failed to get SQLite stats: {e}")
            return BackendStats(
                name=self.name,
                total_datums=0,
                size_bytes=0,
                is_persistent=True,
                is_available=False,
                error=str(e),
            )

    async def vacuum(self) -> int:
        """
        Vacuum the database to reclaim space.

        Returns bytes saved (approximate).
        """
        return await self._backend.vacuum()

    def close(self) -> None:
        """Close the database connection."""
        self._backend.close()

    def clear(self) -> None:
        """Clear all data and reset (for testing)."""
        self._backend.clear()

    def __repr__(self) -> str:
        return f"SQLiteBackend(namespace={self.namespace!r}, path={self._backend.path})"

    def __del__(self) -> None:
        """Cleanup on garbage collection."""
        self.close()
