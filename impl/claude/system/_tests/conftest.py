"""
Fixtures for Database Triad integration tests.

Provides both mock fixtures (always available) and container fixtures
(when testcontainers is installed) for testing the CDC pipeline.

Usage:
    # Run with mocks (always works):
    pytest impl/claude/system/_tests/

    # Run with containers (requires Docker + testcontainers):
    pytest impl/claude/system/_tests/ -m integration
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import pytest

from agents.flux.sources.outbox import (
    MockConnection,
    MockConnectionPool,
    OutboxConfig,
    OutboxSource,
)
from agents.flux.synapse import (
    CDCLagTracker,
    ChangeEvent,
    ChangeOperation,
    SynapseConfig,
    SynapseProcessor,
    SyncResult,
    create_synapse,
)

# ===========================================================================
# Mock Vector Store (Enhanced for Integration)
# ===========================================================================


@dataclass
class MockVectorStore:
    """
    Mock Qdrant-like vector store for integration testing.

    Simulates vector operations with in-memory storage.
    """

    vectors: dict[str, dict[str, tuple[list[float], dict[str, Any]]]] = field(default_factory=dict)
    upserts: list[tuple[str, str, list[float], dict[str, Any]]] = field(default_factory=list)
    deletes: list[tuple[str, str]] = field(default_factory=list)
    failure_mode: str | None = None
    failure_count: int = 0
    _current_failures: int = 0

    async def upsert(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Upsert with optional failure simulation."""
        if self.failure_mode == "always":
            raise ConnectionError("Simulated Qdrant failure")
        if self.failure_mode == "transient" and self._current_failures < self.failure_count:
            self._current_failures += 1
            raise ConnectionError("Transient Qdrant failure")

        # Store in vectors dict
        if collection not in self.vectors:
            self.vectors[collection] = {}
        self.vectors[collection][id] = (vector, payload)
        self.upserts.append((collection, id, vector, payload))

    async def delete(self, collection: str, id: str) -> None:
        """Delete with optional failure simulation."""
        if self.failure_mode == "always":
            raise ConnectionError("Simulated Qdrant failure")

        if collection in self.vectors and id in self.vectors[collection]:
            del self.vectors[collection][id]
        self.deletes.append((collection, id))

    async def get(self, collection: str, id: str) -> dict[str, Any] | None:
        """Get vector by ID."""
        if collection not in self.vectors:
            return None
        if id not in self.vectors[collection]:
            return None
        vector, payload = self.vectors[collection][id]
        return {"id": id, "vector": vector, "payload": payload}

    async def count(self, collection: str) -> int:
        """Count vectors in collection."""
        if collection not in self.vectors:
            return 0
        return len(self.vectors[collection])

    async def delete_collection(self, collection: str) -> None:
        """Delete entire collection."""
        if collection in self.vectors:
            del self.vectors[collection]

    def reset_failures(self) -> None:
        """Reset failure counter."""
        self._current_failures = 0


@dataclass
class MockEmbeddingProvider:
    """Mock embedding provider for integration tests."""

    dimension: int = 128
    calls: list[str] = field(default_factory=list)
    failure_mode: str | None = None

    async def embed(self, text: str) -> list[float]:
        """Return deterministic mock embedding."""
        if self.failure_mode == "timeout":
            await asyncio.sleep(10)  # Simulate timeout
        if self.failure_mode == "error":
            raise RuntimeError("Embedding provider error")

        self.calls.append(text)
        seed = hash(text) % 1000
        return [float(seed + i) / 1000 for i in range(self.dimension)]


# ===========================================================================
# Enhanced Mock Postgres
# ===========================================================================


@dataclass
class MockPostgres:
    """
    Mock Postgres for integration testing.

    Simulates table operations with outbox trigger.
    """

    tables: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)
    outbox_events: list[dict[str, Any]] = field(default_factory=list)
    _sequence: int = 0

    async def insert(self, table: str, data: dict[str, Any]) -> str:
        """Insert row and add to outbox."""
        self._sequence += 1
        row_id: str = str(data.get("id", f"row-{self._sequence}"))

        if table not in self.tables:
            self.tables[table] = {}
        self.tables[table][row_id] = data

        # Add to outbox (simulates trigger)
        self.outbox_events.append(
            {
                "id": self._sequence,
                "event_type": "INSERT",
                "table_name": table,
                "row_id": row_id,
                "payload": data,
                "created_at": datetime.now(timezone.utc),
            }
        )

        return row_id

    async def update(self, table: str, row_id: str, data: dict[str, Any]) -> None:
        """Update row and add to outbox."""
        self._sequence += 1

        if table not in self.tables:
            self.tables[table] = {}

        # Merge with existing data
        existing = self.tables[table].get(row_id, {})
        existing.update(data)
        self.tables[table][row_id] = existing

        self.outbox_events.append(
            {
                "id": self._sequence,
                "event_type": "UPDATE",
                "table_name": table,
                "row_id": row_id,
                "payload": existing,
                "created_at": datetime.now(timezone.utc),
            }
        )

    async def delete(self, table: str, row_id: str) -> None:
        """Delete row and add to outbox."""
        self._sequence += 1

        if table in self.tables and row_id in self.tables[table]:
            del self.tables[table][row_id]

        self.outbox_events.append(
            {
                "id": self._sequence,
                "event_type": "DELETE",
                "table_name": table,
                "row_id": row_id,
                "payload": {},
                "created_at": datetime.now(timezone.utc),
            }
        )

    def get_pending_outbox(self) -> list[dict[str, Any]]:
        """Get unprocessed outbox events."""
        return [e for e in self.outbox_events if not e.get("processed", False)]

    def mark_processed(self, event_id: int) -> None:
        """Mark event as processed."""
        for event in self.outbox_events:
            if event["id"] == event_id:
                event["processed"] = True
                event["processed_at"] = datetime.now(timezone.utc)
                break


# ===========================================================================
# Triad Fixture
# ===========================================================================


@dataclass
class TriadFixture:
    """
    Complete Database Triad fixture for end-to-end tests.

    Combines MockPostgres, MockVectorStore, Synapse, and OutboxSource.
    """

    postgres: MockPostgres
    qdrant: MockVectorStore
    embedder: MockEmbeddingProvider
    synapse_processor: SynapseProcessor
    lag_tracker: CDCLagTracker
    config: SynapseConfig

    @classmethod
    def create(
        cls,
        config: SynapseConfig | None = None,
    ) -> "TriadFixture":
        """Create a complete triad fixture."""
        postgres = MockPostgres()
        qdrant = MockVectorStore()
        embedder = MockEmbeddingProvider()
        lag_tracker = CDCLagTracker()
        synapse_config = config or SynapseConfig()

        processor = SynapseProcessor(
            config=synapse_config,
            embedding_provider=embedder,
            vector_store=qdrant,
        )

        return cls(
            postgres=postgres,
            qdrant=qdrant,
            embedder=embedder,
            synapse_processor=processor,
            lag_tracker=lag_tracker,
            config=synapse_config,
        )

    async def process_pending_events(self) -> list[SyncResult]:
        """Process all pending outbox events through Synapse."""
        results: list[SyncResult] = []

        for event_dict in self.postgres.get_pending_outbox():
            event = ChangeEvent(
                table=event_dict["table_name"],
                operation=ChangeOperation(event_dict["event_type"]),
                row_id=event_dict["row_id"],
                data=event_dict["payload"],
                timestamp_ms=int(event_dict["created_at"].timestamp() * 1000),
                sequence_id=event_dict["id"],
            )

            sync_results = await self.synapse_processor.invoke(event)
            results.extend(sync_results)

            # Record lag
            for result in sync_results:
                if result.success:
                    self.lag_tracker.record(result.lag_ms)

            # Mark as processed if successful
            if all(r.success for r in sync_results):
                self.postgres.mark_processed(event_dict["id"])

        return results

    async def process_n_events(self, n: int) -> int:
        """Process exactly n events. Returns number processed."""
        processed = 0
        pending = self.postgres.get_pending_outbox()[:n]

        for event_dict in pending:
            event = ChangeEvent(
                table=event_dict["table_name"],
                operation=ChangeOperation(event_dict["event_type"]),
                row_id=event_dict["row_id"],
                data=event_dict["payload"],
                timestamp_ms=int(event_dict["created_at"].timestamp() * 1000),
                sequence_id=event_dict["id"],
            )

            sync_results = await self.synapse_processor.invoke(event)

            if all(r.success for r in sync_results):
                self.postgres.mark_processed(event_dict["id"])
                processed += 1

        return processed

    def count_pending_outbox(self) -> int:
        """Count pending outbox events."""
        return len(self.postgres.get_pending_outbox())

    async def rebuild_qdrant_from_postgres(self, table: str = "memories") -> int:
        """Rebuild Qdrant from Postgres data."""
        count = 0
        if table not in self.postgres.tables:
            return 0

        for row_id, data in self.postgres.tables[table].items():
            event = ChangeEvent.insert(table, row_id, data)
            await self.synapse_processor.invoke(event)
            count += 1

        return count


# ===========================================================================
# Pytest Fixtures
# ===========================================================================


@pytest.fixture
def mock_postgres() -> MockPostgres:
    """Create a mock Postgres instance."""
    return MockPostgres()


@pytest.fixture
def mock_qdrant() -> MockVectorStore:
    """Create a mock Qdrant instance."""
    return MockVectorStore()


@pytest.fixture
def mock_embedder() -> MockEmbeddingProvider:
    """Create a mock embedding provider."""
    return MockEmbeddingProvider()


@pytest.fixture
def triad() -> TriadFixture:
    """Create a complete triad fixture."""
    return TriadFixture.create()


@pytest.fixture
def failing_qdrant() -> MockVectorStore:
    """Create a Qdrant that fails all operations."""
    store = MockVectorStore()
    store.failure_mode = "always"
    return store


@pytest.fixture
def transient_failing_qdrant() -> MockVectorStore:
    """Create a Qdrant that fails transiently."""
    store = MockVectorStore()
    store.failure_mode = "transient"
    store.failure_count = 2  # Fail twice, then succeed
    return store


# ===========================================================================
# Container Fixtures (Optional - requires testcontainers)
# ===========================================================================

try:
    from testcontainers.core.container import (
        DockerContainer,  # type: ignore[import-not-found]
    )
    from testcontainers.postgres import (
        PostgresContainer,  # type: ignore[import-not-found]
    )

    CONTAINERS_AVAILABLE = True

    @pytest.fixture(scope="module")
    def postgres_container():
        """Real Postgres container for integration tests."""
        with PostgresContainer("postgres:16-alpine") as pg:
            yield pg

    @pytest.fixture(scope="module")
    def qdrant_container():
        """Real Qdrant container for integration tests."""
        with DockerContainer("qdrant/qdrant:latest").with_exposed_ports(6333) as q:
            q.start()
            yield q

except ImportError:
    CONTAINERS_AVAILABLE = False

    @pytest.fixture(scope="module")
    def postgres_container():
        """Placeholder - testcontainers not available."""
        pytest.skip("testcontainers not installed")

    @pytest.fixture(scope="module")
    def qdrant_container():
        """Placeholder - testcontainers not available."""
        pytest.skip("testcontainers not installed")
