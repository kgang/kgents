"""
Test script to verify Backend protocol implementation.

This demonstrates that all three backends (Memory, SQLite, Postgres) correctly
implement the Backend protocol from the Unified Data Crystal Architecture spec.
"""

import asyncio
import time
from pathlib import Path

from agents.d.datum import Datum
from agents.d.universe.backend import Query
from agents.d.universe.backends import MemoryBackend, SQLiteBackend


async def test_backend(backend: MemoryBackend | SQLiteBackend, name: str) -> None:
    """Test a backend implementation."""
    print(f"\n{'=' * 60}")
    print(f"Testing {name} Backend")
    print(f"{'=' * 60}")

    # Check availability
    available = await backend.is_available()
    print(f"✓ is_available: {available}")

    # Create test data
    datum1 = Datum.create(
        content=b"Test data 1",
        metadata={"author": "kent", "tags": "test,important"},
    )
    datum2 = Datum.create(
        content=b"Test data 2",
        metadata={"author": "claude", "tags": "test"},
    )
    datum3 = Datum.create(
        content=b"Test data 3",
        metadata={"author": "kent", "status": "active"},
    )

    # Store data
    await backend.store(datum1)
    await backend.store(datum2)
    await backend.store(datum3)
    print("✓ Stored 3 data")

    # Get by ID
    retrieved = await backend.get(datum1.id)
    assert retrieved is not None
    assert retrieved.content == b"Test data 1"
    print("✓ Retrieved datum by ID")

    # Query with author filter
    results = await backend.query(Query(author="kent"))
    assert len(results) == 2
    print(f"✓ Query by author: found {len(results)} data")

    # Query with tags filter
    results = await backend.query(Query(tags=frozenset(["important"])))
    assert len(results) == 1
    print(f"✓ Query by tags: found {len(results)} datum")

    # Query with metadata where filter
    results = await backend.query(Query(where={"status": "active"}))
    assert len(results) == 1
    print(f"✓ Query with where filter: found {len(results)} datum")

    # Query with limit
    results = await backend.query(Query(limit=2))
    assert len(results) == 2
    print(f"✓ Query with limit: got {len(results)} data")

    # Query with timestamp filter
    now = time.time()
    results = await backend.query(Query(after=now - 60))
    assert len(results) == 3
    print(f"✓ Query with timestamp: found {len(results)} data")

    # Delete
    deleted = await backend.delete(datum1.id)
    assert deleted is True
    print("✓ Deleted datum")

    # Verify deletion
    retrieved = await backend.get(datum1.id)
    assert retrieved is None
    print("✓ Verified deletion")

    # Get stats
    stats = await backend.stats()
    print(f"✓ Stats: {stats.total_datums} data, {stats.size_bytes} bytes")
    print(f"  Backend: {stats.name}")
    print(f"  Persistent: {stats.is_persistent}")
    print(f"  Available: {stats.is_available}")

    print(f"\n✅ {name} Backend: ALL TESTS PASSED")


async def main() -> None:
    """Run tests on all available backends."""
    print("\n" + "=" * 60)
    print("Backend Protocol Implementation Test")
    print("=" * 60)

    # Test Memory Backend
    memory_backend = MemoryBackend()
    await test_backend(memory_backend, "Memory")

    # Test SQLite Backend
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        sqlite_backend = SQLiteBackend(namespace="test", data_dir=Path(tmpdir))
        await test_backend(sqlite_backend, "SQLite")
        sqlite_backend.close()

    # Test Postgres Backend (if available)
    try:
        import os

        from agents.d.universe.backends import PostgresBackend

        url = os.getenv("KGENTS_DATABASE_URL")
        if url and "postgresql" in url:
            postgres_backend = PostgresBackend(url=url, namespace="test_backend")
            if await postgres_backend.is_available():
                await test_backend(postgres_backend, "Postgres")  # type: ignore[arg-type]
                await postgres_backend.close()
            else:
                print("\n⚠️  Postgres backend unavailable (connection failed)")
        else:
            print("\n⚠️  Postgres backend skipped (no KGENTS_DATABASE_URL)")
    except ImportError:
        print("\n⚠️  Postgres backend unavailable (asyncpg not installed)")

    print("\n" + "=" * 60)
    print("ALL BACKEND TESTS COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
