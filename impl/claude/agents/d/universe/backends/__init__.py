"""
Backend implementations for Unified Data Crystal Architecture.

All backends implement the Backend protocol from ..backend.

Available backends (by priority):
1. PostgresBackend (priority=10) - Production, distributed
2. SQLiteBackend (priority=50) - Local, persistent
3. MemoryBackend (priority=100) - Ephemeral, fallback

Usage:
    from agents.d.universe.backends import MemoryBackend, SQLiteBackend, PostgresBackend

    # Create backends
    memory = MemoryBackend()
    sqlite = SQLiteBackend(namespace="myapp")
    postgres = PostgresBackend(url="postgresql://...")

    # Check availability
    if await postgres.is_available():
        await postgres.store(datum)
"""

from .memory import MemoryBackend
from .sqlite import SQLiteBackend

__all__ = [
    "MemoryBackend",
    "SQLiteBackend",
]

# PostgresBackend is optional (requires asyncpg)
try:
    from .postgres import PostgresBackend

    __all__.append("PostgresBackend")
except ImportError:
    PostgresBackend = None  # type: ignore[assignment, misc]
