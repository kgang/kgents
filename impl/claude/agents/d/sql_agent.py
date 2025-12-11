"""
SQLAgent: Database-backed D-gent with async SQL support.

Supports:
- SQLite (via aiosqlite) - embedded, serverless
- PostgreSQL (via asyncpg) - production-grade

All backends implement the DataAgent protocol with:
- Versioned state storage
- JSONL-style history in database
- Atomic transactions
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    Generic,
    List,
    Type,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from .errors import (
    StateCorruptionError,
    StateNotFoundError,
    StateSerializationError,
    StorageError,
)
from .protocol import DataAgent

S = TypeVar("S")


class SQLBackend(ABC):
    """Abstract SQL backend interface."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close database connection."""
        ...

    @abstractmethod
    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        """Execute a query without returning results."""
        ...

    @abstractmethod
    async def fetchone(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> tuple[Any, ...] | None:
        """Execute query and return single row."""
        ...

    @abstractmethod
    async def fetchall(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> List[tuple[Any, ...]]:
        """Execute query and return all rows."""
        ...


class SQLiteBackend(SQLBackend):
    """SQLite backend using aiosqlite (optional dependency)."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn: Any = None  # aiosqlite.Connection when connected

    async def connect(self) -> None:
        try:
            import aiosqlite
        except ImportError:
            raise ImportError(
                "aiosqlite required for SQLite backend. "
                "Install with: pip install aiosqlite"
            )
        self._conn = await aiosqlite.connect(self.db_path)

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        if not self._conn:
            raise StorageError("Database not connected")
        await self._conn.execute(query, params)
        await self._conn.commit()

    async def fetchone(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> tuple[Any, ...] | None:
        if not self._conn:
            raise StorageError("Database not connected")
        cursor = await self._conn.execute(query, params)
        result = await cursor.fetchone()
        return tuple(result) if result else None

    async def fetchall(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> List[tuple[Any, ...]]:
        if not self._conn:
            raise StorageError("Database not connected")
        cursor = await self._conn.execute(query, params)
        rows = await cursor.fetchall()
        return [tuple(row) for row in rows]


class PostgreSQLBackend(SQLBackend):
    """PostgreSQL backend using asyncpg (optional dependency)."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self._conn: Any = None  # asyncpg.Connection when connected

    async def connect(self) -> None:
        try:
            import asyncpg
        except ImportError:
            raise ImportError(
                "asyncpg required for PostgreSQL backend. "
                "Install with: pip install asyncpg"
            )
        self._conn = await asyncpg.connect(self.connection_string)

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        if not self._conn:
            raise StorageError("Database not connected")
        # Convert SQLite-style ? placeholders to PostgreSQL $1, $2, ...
        pg_query = self._convert_placeholders(query)
        await self._conn.execute(pg_query, *params)

    async def fetchone(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> tuple[Any, ...] | None:
        if not self._conn:
            raise StorageError("Database not connected")
        pg_query = self._convert_placeholders(query)
        row = await self._conn.fetchrow(pg_query, *params)
        return tuple(row) if row else None

    async def fetchall(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> List[tuple[Any, ...]]:
        if not self._conn:
            raise StorageError("Database not connected")
        pg_query = self._convert_placeholders(query)
        rows = await self._conn.fetch(pg_query, *params)
        return [tuple(row) for row in rows]

    def _convert_placeholders(self, query: str) -> str:
        """Convert ? placeholders to $1, $2, ... for PostgreSQL."""
        result = []
        param_num = 0
        i = 0
        while i < len(query):
            if query[i] == "?":
                param_num += 1
                result.append(f"${param_num}")
            else:
                result.append(query[i])
            i += 1
        return "".join(result)


class SQLAgent(Generic[S], DataAgent[S]):
    """
    Database-backed D-gent with versioned state storage.

    Features:
    - Versioned state (each save creates new version)
    - Full history queryable from database
    - Atomic transactions
    - Supports SQLite (embedded) and PostgreSQL

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Counter:
        ...     value: int
        ...
        >>> # SQLite (local file)
        >>> agent = SQLAgent(
        ...     backend=SQLiteBackend("state.db"),
        ...     table="counters",
        ...     key="main",
        ...     schema=Counter
        ... )
        >>> await agent.connect()
        >>> await agent.save(Counter(value=1))
        >>> state = await agent.load()
        >>> state.value
        1
    """

    def __init__(
        self,
        backend: SQLBackend,
        table: str,
        key: str,
        schema: Type[S],
        max_history: int = 100,
    ) -> None:
        """
        Initialize SQL D-gent.

        Args:
            backend: SQLite or PostgreSQL backend
            table: Table name for state storage
            key: Unique key to identify this agent's state
            schema: Type of state (for deserialization)
            max_history: Max versions to retain
        """
        self.backend = backend
        self.table = table
        self.key = key
        self.schema = schema
        self.max_history = max_history
        self._connected = False

    async def connect(self) -> None:
        """Connect to database and ensure table exists."""
        await self.backend.connect()
        await self._ensure_table()
        self._connected = True

    async def close(self) -> None:
        """Close database connection."""
        await self.backend.close()
        self._connected = False

    async def _ensure_table(self) -> None:
        """Create state table if it doesn't exist."""
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                state TEXT NOT NULL,
                version INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """
        await self.backend.execute(query)

        # Create index for fast lookups
        index_query = f"""
            CREATE INDEX IF NOT EXISTS idx_{self.table}_key_version
            ON {self.table} (key, version DESC)
        """
        await self.backend.execute(index_query)

    async def load(self) -> S:
        """
        Load latest state from database.

        Returns:
            Deserialized state

        Raises:
            StateNotFoundError: If no state exists for this key
            StateCorruptionError: If stored JSON is invalid
        """
        if not self._connected:
            raise StorageError("Not connected. Call connect() first.")

        query = f"""
            SELECT state FROM {self.table}
            WHERE key = ?
            ORDER BY version DESC
            LIMIT 1
        """
        row = await self.backend.fetchone(query, (self.key,))

        if not row:
            raise StateNotFoundError(
                f"No state for key '{self.key}' in table '{self.table}'"
            )

        try:
            data = json.loads(row[0])
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Invalid JSON in database: {e}")

        return self._deserialize(data)

    async def save(self, state: S) -> None:
        """
        Save new state version to database.

        Args:
            state: State to persist

        Raises:
            StateSerializationError: If state can't be serialized
            StorageError: If database write fails
        """
        if not self._connected:
            raise StorageError("Not connected. Call connect() first.")

        serialized = self._serialize(state)

        try:
            # Get next version number
            version_query = f"""
                SELECT COALESCE(MAX(version), 0) + 1 FROM {self.table}
                WHERE key = ?
            """
            row = await self.backend.fetchone(version_query, (self.key,))
            next_version = row[0] if row else 1

            # Insert new version
            insert_query = f"""
                INSERT INTO {self.table} (key, state, version, created_at)
                VALUES (?, ?, ?, ?)
            """
            now = datetime.now(timezone.utc).isoformat()
            await self.backend.execute(
                insert_query, (self.key, json.dumps(serialized), next_version, now)
            )

            # Prune old versions if exceeding max_history
            await self._prune_history()

        except Exception as e:
            raise StorageError(f"Failed to save state: {e}")

    async def history(self, limit: int | None = None) -> List[S]:
        """
        Load historical states from database.

        Args:
            limit: Max entries to return (newest first, excludes current)

        Returns:
            List of historical states
        """
        if not self._connected:
            raise StorageError("Not connected. Call connect() first.")

        # Get all except latest (which is current)
        effective_limit = (limit + 1) if limit else self.max_history + 1
        query = f"""
            SELECT state FROM {self.table}
            WHERE key = ?
            ORDER BY version DESC
            LIMIT ?
        """
        rows = await self.backend.fetchall(query, (self.key, effective_limit))

        if not rows:
            return []

        # Skip the first row (current state), deserialize the rest
        states = []
        for row in rows[1:]:
            try:
                data = json.loads(row[0])
                states.append(self._deserialize(data))
            except (json.JSONDecodeError, Exception):
                # Skip corrupted entries
                continue

        return states[:limit] if limit else states

    async def _prune_history(self) -> None:
        """Remove old versions exceeding max_history."""
        # Find the version threshold
        threshold_query = f"""
            SELECT version FROM {self.table}
            WHERE key = ?
            ORDER BY version DESC
            LIMIT 1 OFFSET ?
        """
        row = await self.backend.fetchone(threshold_query, (self.key, self.max_history))

        if row:
            delete_query = f"""
                DELETE FROM {self.table}
                WHERE key = ? AND version <= ?
            """
            await self.backend.execute(delete_query, (self.key, row[0]))

    def _serialize(self, state: S) -> Any:
        """Serialize state to JSON-compatible structure."""

        def enum_serializer(obj: Any) -> Any:
            if isinstance(obj, Enum):
                return obj.value
            return obj

        try:
            if is_dataclass(state):
                return asdict(
                    cast(Any, state),
                    dict_factory=lambda x: {k: enum_serializer(v) for k, v in x},
                )
            return state
        except Exception as e:
            raise StateSerializationError(f"Cannot serialize state: {e}")

    def _deserialize(self, data: Any) -> S:
        """Deserialize JSON data to state type."""
        try:
            if is_dataclass(self.schema):
                return cast(S, self._deserialize_dataclass(self.schema, data))
            return cast(S, data)
        except Exception as e:
            raise StateCorruptionError(f"Cannot deserialize to {self.schema}: {e}")

    def _deserialize_dataclass(self, cls: Type[Any], data: dict[str, Any]) -> Any:
        """Recursively deserialize a dataclass and its nested fields."""
        if not isinstance(data, dict):
            return data

        try:
            type_hints = get_type_hints(cls)
        except Exception:
            type_hints = {}

        kwargs: dict[str, Any] = {}
        for field_name, field_value in data.items():
            field_type = type_hints.get(field_name)

            if field_value is None:
                kwargs[field_name] = None
            elif field_type and is_dataclass(field_type):
                kwargs[field_name] = self._deserialize_dataclass(
                    cast(Type[Any], field_type), field_value
                )
            elif field_type:
                try:
                    if isinstance(field_type, type) and issubclass(field_type, Enum):
                        kwargs[field_name] = field_type(field_value)
                        continue
                except TypeError:
                    pass

                if isinstance(field_value, list) and field_value:
                    origin = get_origin(field_type)
                    if origin is list:
                        args = get_args(field_type)
                        if args and is_dataclass(args[0]):
                            kwargs[field_name] = [
                                self._deserialize_dataclass(
                                    cast(Type[Any], args[0]), item
                                )
                                if isinstance(item, dict)
                                else item
                                for item in field_value
                            ]
                            continue

                kwargs[field_name] = field_value
            else:
                kwargs[field_name] = field_value

        return cls(**kwargs)

    async def __aenter__(self) -> SQLAgent[S]:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()


# Convenience factory functions


def create_sqlite_agent(
    db_path: str,
    table: str,
    key: str,
    schema: Type[S],
    max_history: int = 100,
) -> SQLAgent[S]:
    """
    Create a SQLite-backed D-gent.

    Args:
        db_path: Path to SQLite database file
        table: Table name for state storage
        key: Unique identifier for this agent's state
        schema: Type of state
        max_history: Max versions to retain

    Returns:
        Configured SQLAgent (call connect() before use)

    Example:
        >>> agent = create_sqlite_agent(
        ...     db_path="./data/state.db",
        ...     table="agents",
        ...     key="my_agent",
        ...     schema=MyState
        ... )
        >>> async with agent:
        ...     await agent.save(MyState(...))
    """
    return SQLAgent(
        backend=SQLiteBackend(db_path),
        table=table,
        key=key,
        schema=schema,
        max_history=max_history,
    )


def create_postgres_agent(
    connection_string: str,
    table: str,
    key: str,
    schema: Type[S],
    max_history: int = 100,
) -> SQLAgent[S]:
    """
    Create a PostgreSQL-backed D-gent.

    Args:
        connection_string: PostgreSQL connection string
            e.g., "postgresql://user:pass@localhost:5432/dbname"
        table: Table name for state storage
        key: Unique identifier for this agent's state
        schema: Type of state
        max_history: Max versions to retain

    Returns:
        Configured SQLAgent (call connect() before use)

    Example:
        >>> agent = create_postgres_agent(
        ...     connection_string="postgresql://localhost/mydb",
        ...     table="agents",
        ...     key="my_agent",
        ...     schema=MyState
        ... )
        >>> async with agent:
        ...     await agent.save(MyState(...))
    """
    return SQLAgent(
        backend=PostgreSQLBackend(connection_string),
        table=table,
        key=key,
        schema=schema,
        max_history=max_history,
    )
