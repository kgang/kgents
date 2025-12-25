"""
SQLiteBackend: SQLite database storage for D-gent.

Tier 2 in the projection lattice. ACID, queryable, single-file.
Path: ~/.kgents/data/{namespace}.db

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import asyncio
import base64
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Final, Generator, List

from ..datum import Datum
from ..protocol import BaseDgent

DEFAULT_DATA_DIR: Final[Path] = Path.home() / ".kgents" / "data"

SCHEMA: Final[str] = """
CREATE TABLE IF NOT EXISTS data (
    id TEXT PRIMARY KEY,
    content BLOB NOT NULL,
    created_at REAL NOT NULL,
    causal_parent TEXT,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_created ON data(created_at);
CREATE INDEX IF NOT EXISTS idx_parent ON data(causal_parent);
"""


class SQLiteBackend(BaseDgent):
    """
    SQLite database backend.

    - ACID: Full transaction support
    - Queryable: SQL for complex queries
    - Single-file: Easy backup/restore
    - Durable: Survives process restarts

    Schema:
        CREATE TABLE data (
            id TEXT PRIMARY KEY,
            content BLOB NOT NULL,
            created_at REAL NOT NULL,
            causal_parent TEXT,
            metadata TEXT  -- JSON
        );

    File location: ~/.kgents/data/{namespace}.db
    """

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
        self.namespace = namespace
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self.path = self.data_dir / f"{namespace}.db"

        self._connection: sqlite3.Connection | None = None
        self._lock = asyncio.Lock()

    def _ensure_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get or create database connection."""
        if self._connection is None:
            self._ensure_dir()
            self._connection = sqlite3.connect(
                str(self.path),
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.executescript(SCHEMA)
            self._connection.commit()

        yield self._connection

    def _row_to_datum(self, row: sqlite3.Row) -> Datum:
        """Convert a database row to Datum."""
        metadata = {}
        if row["metadata"]:
            try:
                metadata = json.loads(row["metadata"])
            except json.JSONDecodeError:
                pass

        return Datum(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
            causal_parent=row["causal_parent"],
            metadata=metadata,
        )

    async def put(self, datum: Datum) -> str:
        """Store datum in SQLite database."""
        async with self._lock:

            def do_put() -> str:
                with self._get_connection() as conn:
                    metadata_json = json.dumps(datum.metadata) if datum.metadata else None

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO data (id, content, created_at, causal_parent, metadata)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            datum.id,
                            datum.content,
                            datum.created_at,
                            datum.causal_parent,
                            metadata_json,
                        ),
                    )
                    conn.commit()
                    return datum.id

            return await asyncio.to_thread(do_put)

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from SQLite database."""
        async with self._lock:

            def do_get() -> Datum | None:
                with self._get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT * FROM data WHERE id = ?",
                        (id,),
                    )
                    row = cursor.fetchone()

                    if row is None:
                        return None

                    return self._row_to_datum(row)

            return await asyncio.to_thread(do_get)

    async def delete(self, id: str) -> bool:
        """Delete datum from SQLite database."""
        async with self._lock:

            def do_delete() -> bool:
                with self._get_connection() as conn:
                    cursor = conn.execute(
                        "DELETE FROM data WHERE id = ?",
                        (id,),
                    )
                    conn.commit()
                    return cursor.rowcount > 0

            return await asyncio.to_thread(do_delete)

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
        schema: str | None = None,
    ) -> List[Datum]:
        """List data with filters, sorted by created_at descending.

        Args:
            prefix: Filter by ID prefix
            after: Filter by created_at timestamp
            limit: Maximum results
            schema: Filter by schema in metadata (uses JSON extract)
        """
        async with self._lock:

            def do_list() -> List[Datum]:
                with self._get_connection() as conn:
                    query = "SELECT * FROM data WHERE 1=1"
                    params: list[str | float] = []

                    if prefix is not None:
                        query += " AND id LIKE ?"
                        params.append(f"{prefix}%")

                    if after is not None:
                        query += " AND created_at > ?"
                        params.append(after)

                    # Filter by schema in metadata JSON
                    if schema is not None:
                        query += " AND json_extract(metadata, '$.schema') = ?"
                        params.append(schema)

                    query += " ORDER BY created_at DESC LIMIT ?"
                    params.append(limit)

                    cursor = conn.execute(query, params)
                    return [self._row_to_datum(row) for row in cursor.fetchall()]

            return await asyncio.to_thread(do_list)

    async def causal_chain(self, id: str) -> List[Datum]:
        """Get causal ancestors of a datum using recursive CTE."""
        async with self._lock:

            def do_chain() -> List[Datum]:
                with self._get_connection() as conn:
                    # Use recursive CTE to get full chain
                    cursor = conn.execute(
                        """
                        WITH RECURSIVE chain(id, content, created_at, causal_parent, metadata, depth) AS (
                            SELECT id, content, created_at, causal_parent, metadata, 0
                            FROM data
                            WHERE id = ?

                            UNION ALL

                            SELECT d.id, d.content, d.created_at, d.causal_parent, d.metadata, c.depth + 1
                            FROM data d
                            INNER JOIN chain c ON d.id = c.causal_parent
                        )
                        SELECT id, content, created_at, causal_parent, metadata
                        FROM chain
                        ORDER BY depth DESC
                        """,
                        (id,),
                    )

                    return [self._row_to_datum(row) for row in cursor.fetchall()]

            return await asyncio.to_thread(do_chain)

    async def exists(self, id: str) -> bool:
        """Check existence efficiently."""
        async with self._lock:

            def do_exists() -> bool:
                with self._get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT 1 FROM data WHERE id = ? LIMIT 1",
                        (id,),
                    )
                    return cursor.fetchone() is not None

            return await asyncio.to_thread(do_exists)

    async def count(self) -> int:
        """Count data efficiently."""
        async with self._lock:

            def do_count() -> int:
                with self._get_connection() as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM data")
                    row = cursor.fetchone()
                    return row[0] if row else 0

            return await asyncio.to_thread(do_count)

    async def vacuum(self) -> int:
        """
        Vacuum the database to reclaim space.

        Returns bytes saved (approximate).
        """
        async with self._lock:

            def do_vacuum() -> int:
                original_size = self.path.stat().st_size if self.path.exists() else 0

                with self._get_connection() as conn:
                    conn.execute("VACUUM")

                new_size = self.path.stat().st_size if self.path.exists() else 0
                return original_size - new_size

            return await asyncio.to_thread(do_vacuum)

    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def clear(self) -> None:
        """Clear all data and reset (for testing)."""
        self.close()
        if self.path.exists():
            self.path.unlink()

    def __repr__(self) -> str:
        return f"SQLiteBackend(namespace={self.namespace!r}, path={self.path})"

    def __del__(self) -> None:
        """Cleanup on garbage collection."""
        self.close()
