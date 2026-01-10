"""
D-gent Backends: Storage implementations for the projection lattice.

The projection lattice (from least to most durable):
1. MemoryBackend - In-memory, ephemeral (Tier 0)
2. JSONLBackend - Append-only file (Tier 1)
3. SQLiteBackend - Single-file database (Tier 2)
4. PostgresBackend - Full database (Tier 3-4)

All backends implement DgentProtocol (5 methods).
"""

from .jsonl import JSONLBackend
from .memory import MemoryBackend
from .sqlite import SQLiteBackend

__all__ = [
    "MemoryBackend",
    "JSONLBackend",
    "SQLiteBackend",
]

# PostgresBackend is optional (requires asyncpg)
try:
    from .postgres import PostgresBackend

    __all__.append("PostgresBackend")
except ImportError:
    PostgresBackend = None  # type: ignore[assignment, misc]
