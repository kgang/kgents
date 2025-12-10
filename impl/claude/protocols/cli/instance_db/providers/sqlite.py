"""
SQLite-based Storage Providers.

Local-first implementations of the repository interfaces:
- SQLiteRelationalStore: Core state storage with WAL mode
- NumpyVectorStore: Vector similarity with pure numpy (no deps)
- FilesystemBlobStore: File-based blob storage
- SQLiteTelemetryStore: Event logging with time-based queries

These are the default providers for ~/.kgents/
"""

from __future__ import annotations

import asyncio
import json
import re
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, AsyncIterator

import aiosqlite
import numpy as np

from ..interfaces import (
    IRelationalStore,
    IVectorStore,
    IBlobStore,
    ITelemetryStore,
    VectorSearchResult,
    TelemetryEvent,
)


# =============================================================================
# SQLiteRelationalStore
# =============================================================================


class SQLiteRelationalStore(IRelationalStore):
    """
    SQLite-based relational store with WAL mode.

    Features:
    - Named parameter support (:name syntax)
    - WAL mode for concurrent reads
    - Transaction support with auto-commit/rollback
    - Connection pooling (single connection, async-safe)
    """

    def __init__(self, db_path: Path | str, wal_mode: bool = True):
        self._db_path = Path(db_path)
        self._wal_mode = wal_mode
        self._conn: aiosqlite.Connection | None = None
        self._lock = asyncio.Lock()

    async def _ensure_connection(self) -> aiosqlite.Connection:
        """Get or create connection."""
        if self._conn is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(str(self._db_path))
            self._conn.row_factory = aiosqlite.Row

            if self._wal_mode:
                await self._conn.execute("PRAGMA journal_mode=WAL")
                await self._conn.execute("PRAGMA synchronous=NORMAL")

            # Performance pragmas
            await self._conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            await self._conn.execute("PRAGMA temp_store=MEMORY")

        return self._conn

    def _convert_params(
        self, query: str, params: dict[str, Any] | None
    ) -> tuple[str, tuple]:
        """
        Convert :name params to ? placeholders for SQLite.

        SQLite's aiosqlite doesn't support named params directly,
        so we convert them to positional.
        """
        if params is None:
            return query, ()

        # Find all :name patterns
        pattern = re.compile(r":(\w+)")
        names = pattern.findall(query)

        # Replace with ?
        converted_query = pattern.sub("?", query)

        # Build positional params in order
        positional = tuple(params.get(name) for name in names)

        return converted_query, positional

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        """Execute query, return rows affected."""
        conn = await self._ensure_connection()

        # Check if this is a multi-statement script (contains multiple ;)
        # Count semicolons outside of strings/comments
        semicolon_count = query.count(";")
        if semicolon_count > 1 and params is None:
            # Use executescript for multi-statement queries
            async with self._lock:
                await conn.executescript(query)
                await conn.commit()
                return 0

        converted_query, positional = self._convert_params(query, params)

        async with self._lock:
            cursor = await conn.execute(converted_query, positional)
            await conn.commit()
            return cursor.rowcount

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict | None:
        """Fetch single row as dict."""
        conn = await self._ensure_connection()
        converted_query, positional = self._convert_params(query, params)

        async with self._lock:
            cursor = await conn.execute(converted_query, positional)
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(row)

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict]:
        """Fetch all rows as list of dicts."""
        conn = await self._ensure_connection()
        converted_query, positional = self._convert_params(query, params)

        async with self._lock:
            cursor = await conn.execute(converted_query, positional)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        """Execute query for each param set."""
        if not params_list:
            return 0

        conn = await self._ensure_connection()

        # Convert first param set to get the query pattern
        converted_query, _ = self._convert_params(query, params_list[0])

        # Get param names from query
        pattern = re.compile(r":(\w+)")
        names = pattern.findall(query)

        # Convert all param sets to positional
        positional_list = [
            tuple(params.get(name) for name in names) for params in params_list
        ]

        async with self._lock:
            await conn.executemany(converted_query, positional_list)
            await conn.commit()
            return len(params_list)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[IRelationalStore]:
        """Begin transaction with auto-commit/rollback."""
        conn = await self._ensure_connection()

        # Create a transaction-scoped wrapper
        tx = _SQLiteTransaction(conn, self._lock, self._convert_params)

        async with self._lock:
            await conn.execute("BEGIN")
            try:
                yield tx
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    async def close(self) -> None:
        """Close the connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None


class _SQLiteTransaction:
    """Transaction-scoped store for nested operations."""

    def __init__(self, conn: aiosqlite.Connection, lock: asyncio.Lock, convert_params):
        self._conn = conn
        self._lock = lock
        self._convert_params = convert_params

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        converted_query, positional = self._convert_params(query, params)
        cursor = await self._conn.execute(converted_query, positional)
        return cursor.rowcount

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict | None:
        converted_query, positional = self._convert_params(query, params)
        cursor = await self._conn.execute(converted_query, positional)
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict]:
        converted_query, positional = self._convert_params(query, params)
        cursor = await self._conn.execute(converted_query, positional)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        if not params_list:
            return 0
        converted_query, _ = self._convert_params(query, params_list[0])
        pattern = re.compile(r":(\w+)")
        names = pattern.findall(query)
        positional_list = [
            tuple(params.get(name) for name in names) for params in params_list
        ]
        await self._conn.executemany(converted_query, positional_list)
        return len(params_list)


# =============================================================================
# NumpyVectorStore
# =============================================================================


@dataclass
class _VectorEntry:
    """Internal vector storage entry."""

    id: str
    vector: np.ndarray
    metadata: dict[str, Any]


class NumpyVectorStore(IVectorStore):
    """
    Pure numpy vector store (no external dependencies).

    Uses cosine similarity for search.
    Persists to JSON file for durability.

    Suitable for <1000 vectors. Beyond that, consider sqlite-vec.
    """

    def __init__(self, storage_path: Path | str, dimensions: int = 384):
        self._storage_path = Path(storage_path)
        self._dimensions = dimensions
        self._vectors: dict[str, _VectorEntry] = {}
        self._dirty = False
        self._lock = asyncio.Lock()

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def initialize(self) -> None:
        """Load vectors from storage."""
        if self._storage_path.exists():
            async with self._lock:
                data = json.loads(self._storage_path.read_text())
                for entry in data.get("vectors", []):
                    self._vectors[entry["id"]] = _VectorEntry(
                        id=entry["id"],
                        vector=np.array(entry["vector"], dtype=np.float32),
                        metadata=entry.get("metadata", {}),
                    )
                self._dimensions = data.get("dimensions", self._dimensions)

    async def _save(self) -> None:
        """Save vectors to storage."""
        if not self._dirty:
            return

        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "dimensions": self._dimensions,
            "vectors": [
                {
                    "id": e.id,
                    "vector": e.vector.tolist(),
                    "metadata": e.metadata,
                }
                for e in self._vectors.values()
            ],
        }

        self._storage_path.write_text(json.dumps(data))
        self._dirty = False

    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Insert or update vector."""
        async with self._lock:
            self._vectors[id] = _VectorEntry(
                id=id,
                vector=np.array(vector, dtype=np.float32),
                metadata=metadata,
            )
            self._dirty = True
            await self._save()

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search using cosine similarity."""
        if not self._vectors:
            return []

        query = np.array(query_vector, dtype=np.float32)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return []
        query = query / query_norm

        results: list[tuple[float, _VectorEntry]] = []

        async with self._lock:
            for entry in self._vectors.values():
                # Apply metadata filter
                if filter:
                    if not all(entry.metadata.get(k) == v for k, v in filter.items()):
                        continue

                # Cosine similarity
                entry_norm = np.linalg.norm(entry.vector)
                if entry_norm == 0:
                    continue
                normalized = entry.vector / entry_norm
                similarity = float(np.dot(query, normalized))

                # Convert to distance (lower is better)
                distance = 1.0 - similarity
                results.append((distance, entry))

        # Sort by distance (ascending)
        results.sort(key=lambda x: x[0])

        return [
            VectorSearchResult(
                id=entry.id,
                distance=distance,
                metadata=entry.metadata,
            )
            for distance, entry in results[:limit]
        ]

    async def delete(self, id: str) -> bool:
        """Delete vector by ID."""
        async with self._lock:
            if id in self._vectors:
                del self._vectors[id]
                self._dirty = True
                await self._save()
                return True
            return False

    async def count(self) -> int:
        """Return total vector count."""
        return len(self._vectors)

    async def close(self) -> None:
        """Save and close."""
        async with self._lock:
            if self._dirty:
                await self._save()


# =============================================================================
# FilesystemBlobStore
# =============================================================================


class FilesystemBlobStore(IBlobStore):
    """
    File-based blob storage.

    Simple directory structure with key as relative path.
    Supports content type tracking via .meta files.
    """

    def __init__(self, base_path: Path | str):
        self._base_path = Path(base_path)

    def _key_to_path(self, key: str) -> Path:
        """Convert key to filesystem path."""
        # Sanitize key to prevent path traversal
        clean_key = key.lstrip("/").replace("..", "")
        return self._base_path / clean_key

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        """Store blob, return path."""
        path = self._key_to_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write data
        path.write_bytes(data)

        # Write metadata if content type provided
        if content_type:
            meta_path = path.with_suffix(path.suffix + ".meta")
            meta_path.write_text(json.dumps({"content_type": content_type}))

        return str(path)

    async def get(self, key: str) -> bytes | None:
        """Retrieve blob by key."""
        path = self._key_to_path(key)
        if path.exists():
            return path.read_bytes()
        return None

    async def delete(self, key: str) -> bool:
        """Delete blob."""
        path = self._key_to_path(key)
        if path.exists():
            path.unlink()
            # Also delete metadata if exists
            meta_path = path.with_suffix(path.suffix + ".meta")
            if meta_path.exists():
                meta_path.unlink()
            return True
        return False

    async def list(self, prefix: str = "") -> list[str]:
        """List keys with prefix."""
        if not self._base_path.exists():
            return []

        search_path = self._base_path / prefix if prefix else self._base_path
        if not search_path.exists():
            return []

        results = []
        for path in search_path.rglob("*"):
            if path.is_file() and not path.suffix == ".meta":
                # Convert back to key
                key = str(path.relative_to(self._base_path))
                results.append(key)

        return sorted(results)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self._key_to_path(key).exists()

    async def close(self) -> None:
        """No-op for filesystem."""
        pass


# =============================================================================
# SQLiteTelemetryStore
# =============================================================================


# Schema for telemetry database
TELEMETRY_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    instance_id TEXT,
    project_hash TEXT,
    data TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_instance ON events(instance_id);
"""


class SQLiteTelemetryStore(ITelemetryStore):
    """
    SQLite-based telemetry storage.

    Optimized for:
    - High-velocity appends (batch insert)
    - Time-range queries
    - Efficient pruning
    """

    def __init__(self, db_path: Path | str):
        self._db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def _ensure_connection(self) -> aiosqlite.Connection:
        """Get or create connection with schema."""
        if self._conn is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(str(self._db_path))
            self._conn.row_factory = aiosqlite.Row

            # WAL mode for concurrent access
            await self._conn.execute("PRAGMA journal_mode=WAL")
            await self._conn.execute("PRAGMA synchronous=NORMAL")

        if not self._initialized:
            await self._conn.executescript(TELEMETRY_SCHEMA)
            await self._conn.commit()
            self._initialized = True

        return self._conn

    async def append(self, events: list[TelemetryEvent]) -> int:
        """Batch append events."""
        if not events:
            return 0

        conn = await self._ensure_connection()

        rows = [
            (
                e.event_type,
                e.timestamp,
                e.instance_id,
                e.project_hash,
                json.dumps(e.data),
            )
            for e in events
        ]

        async with self._lock:
            await conn.executemany(
                """
                INSERT INTO events (event_type, timestamp, instance_id, project_hash, data)
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
            await conn.commit()

        return len(events)

    async def query(
        self,
        event_type: str | None = None,
        since: str | None = None,
        until: str | None = None,
        instance_id: str | None = None,
        limit: int = 1000,
    ) -> list[TelemetryEvent]:
        """Query events with filters."""
        conn = await self._ensure_connection()

        conditions = []
        params: list[Any] = []

        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)

        if since:
            conditions.append("timestamp >= ?")
            params.append(since)

        if until:
            conditions.append("timestamp <= ?")
            params.append(until)

        if instance_id:
            conditions.append("instance_id = ?")
            params.append(instance_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        query = f"""
            SELECT event_type, timestamp, instance_id, project_hash, data
            FROM events
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        """

        async with self._lock:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()

        return [
            TelemetryEvent(
                event_type=row["event_type"],
                timestamp=row["timestamp"],
                instance_id=row["instance_id"],
                project_hash=row["project_hash"],
                data=json.loads(row["data"]),
            )
            for row in rows
        ]

    async def prune(self, older_than_days: int) -> int:
        """Delete old events."""
        conn = await self._ensure_connection()

        cutoff = (datetime.now() - timedelta(days=older_than_days)).isoformat()

        async with self._lock:
            cursor = await conn.execute(
                "DELETE FROM events WHERE timestamp < ?",
                (cutoff,),
            )
            await conn.commit()
            return cursor.rowcount

    async def count(self, event_type: str | None = None) -> int:
        """Count events, optionally by type."""
        conn = await self._ensure_connection()

        if event_type:
            query = "SELECT COUNT(*) as cnt FROM events WHERE event_type = ?"
            params: tuple = (event_type,)
        else:
            query = "SELECT COUNT(*) as cnt FROM events"
            params = ()

        async with self._lock:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

    async def close(self) -> None:
        """Close the connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None


# =============================================================================
# In-Memory Providers (for testing/fallback)
# =============================================================================


class InMemoryRelationalStore(IRelationalStore):
    """In-memory relational store for testing."""

    def __init__(self):
        self._tables: dict[str, list[dict]] = {}
        self._lock = asyncio.Lock()

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> int:
        # Minimal implementation for testing
        return 0

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict | None:
        return None

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict]:
        return []

    async def executemany(self, query: str, params_list: list[dict[str, Any]]) -> int:
        return 0

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[IRelationalStore]:
        yield self

    async def close(self) -> None:
        pass


class InMemoryVectorStore(IVectorStore):
    """In-memory vector store for testing."""

    def __init__(self, dimensions: int = 384):
        self._dimensions = dimensions
        self._vectors: dict[str, tuple[list[float], dict]] = {}

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def upsert(
        self, id: str, vector: list[float], metadata: dict[str, Any]
    ) -> None:
        self._vectors[id] = (vector, metadata)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        return []

    async def delete(self, id: str) -> bool:
        if id in self._vectors:
            del self._vectors[id]
            return True
        return False

    async def count(self) -> int:
        return len(self._vectors)

    async def close(self) -> None:
        pass


class InMemoryBlobStore(IBlobStore):
    """In-memory blob store for testing."""

    def __init__(self):
        self._blobs: dict[str, bytes] = {}

    async def put(self, key: str, data: bytes, content_type: str | None = None) -> str:
        self._blobs[key] = data
        return key

    async def get(self, key: str) -> bytes | None:
        return self._blobs.get(key)

    async def delete(self, key: str) -> bool:
        if key in self._blobs:
            del self._blobs[key]
            return True
        return False

    async def list(self, prefix: str = "") -> list[str]:
        return [k for k in self._blobs.keys() if k.startswith(prefix)]

    async def exists(self, key: str) -> bool:
        return key in self._blobs

    async def close(self) -> None:
        pass


class InMemoryTelemetryStore(ITelemetryStore):
    """In-memory telemetry store for testing."""

    def __init__(self):
        self._events: list[TelemetryEvent] = []

    async def append(self, events: list[TelemetryEvent]) -> int:
        self._events.extend(events)
        return len(events)

    async def query(
        self,
        event_type: str | None = None,
        since: str | None = None,
        until: str | None = None,
        instance_id: str | None = None,
        limit: int = 1000,
    ) -> list[TelemetryEvent]:
        results = self._events[:]

        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if since:
            results = [e for e in results if e.timestamp >= since]
        if until:
            results = [e for e in results if e.timestamp <= until]
        if instance_id:
            results = [e for e in results if e.instance_id == instance_id]

        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    async def prune(self, older_than_days: int) -> int:
        cutoff = (datetime.now() - timedelta(days=older_than_days)).isoformat()
        before = len(self._events)
        self._events = [e for e in self._events if e.timestamp >= cutoff]
        return before - len(self._events)

    async def count(self, event_type: str | None = None) -> int:
        if event_type:
            return sum(1 for e in self._events if e.event_type == event_type)
        return len(self._events)

    async def close(self) -> None:
        pass
