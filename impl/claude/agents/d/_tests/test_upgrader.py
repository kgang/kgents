"""
Tests for AutoUpgrader and migration utilities.

Tests verify:
1. Upgrade policy evaluation
2. Automatic tier promotion
3. Migration utilities
4. Statistics tracking
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path
from typing import Generator

import pytest

from ..backends.jsonl import JSONLBackend
from ..backends.memory import MemoryBackend
from ..backends.sqlite import SQLiteBackend
from ..bus import DataBus, DataEvent, DataEventType
from ..datum import Datum
from ..router import Backend
from ..upgrader import (
    AutoUpgrader,
    DatumStats,
    UpgradePolicy,
    UpgradeReason,
    migrate_data,
    verify_migration,
)

# --- Fixtures ---


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for file-based backends."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """Fresh memory backend."""
    return MemoryBackend()


@pytest.fixture
def jsonl_backend(temp_dir: Path) -> Generator[JSONLBackend, None, None]:
    """Fresh JSONL backend."""
    backend = JSONLBackend(namespace="upgrade_test", data_dir=temp_dir)
    yield backend
    backend.clear()


@pytest.fixture
def sqlite_backend(temp_dir: Path) -> Generator[SQLiteBackend, None, None]:
    """Fresh SQLite backend."""
    backend = SQLiteBackend(namespace="upgrade_test", data_dir=temp_dir)
    yield backend
    backend.clear()


@pytest.fixture
def bus() -> DataBus:
    """Fresh data bus."""
    return DataBus()


@pytest.fixture
def upgrader(
    memory_backend: MemoryBackend,
    jsonl_backend: JSONLBackend,
    sqlite_backend: SQLiteBackend,
    bus: DataBus,
) -> AutoUpgrader:
    """AutoUpgrader with memory source and both targets."""
    return AutoUpgrader(
        source=memory_backend,
        source_tier=Backend.MEMORY,
        targets={
            Backend.JSONL: jsonl_backend,
            Backend.SQLITE: sqlite_backend,
        },
        bus=bus,
        policy=UpgradePolicy(
            memory_to_jsonl_accesses=3,
            memory_to_jsonl_seconds=1.0,
            jsonl_to_sqlite_accesses=5,
            jsonl_to_sqlite_seconds=2.0,
        ),
        check_interval=0.1,  # Fast for testing
    )


# --- UpgradePolicy Tests ---


class TestUpgradePolicy:
    """Tests for UpgradePolicy dataclass."""

    def test_default_values(self) -> None:
        """Default policy has reasonable values."""
        policy = UpgradePolicy()

        assert policy.memory_to_jsonl_accesses == 3
        assert policy.memory_to_jsonl_seconds == 60.0
        assert policy.jsonl_to_sqlite_accesses == 10
        assert policy.jsonl_to_sqlite_seconds == 3600.0
        assert policy.sqlite_to_postgres_explicit_only is True

    def test_custom_values(self) -> None:
        """Policy accepts custom values."""
        policy = UpgradePolicy(
            memory_to_jsonl_accesses=1,
            memory_to_jsonl_seconds=10.0,
        )

        assert policy.memory_to_jsonl_accesses == 1
        assert policy.memory_to_jsonl_seconds == 10.0


# --- AutoUpgrader Tests ---


class TestUpgraderInit:
    """Tests for AutoUpgrader initialization."""

    def test_creates_with_defaults(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """Upgrader creates with default policy."""
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
        )

        assert upgrader.policy is not None
        assert upgrader.check_interval == 30.0

    def test_creates_with_custom_policy(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """Upgrader accepts custom policy."""
        policy = UpgradePolicy(memory_to_jsonl_accesses=1)

        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            policy=policy,
        )

        assert upgrader.policy.memory_to_jsonl_accesses == 1


class TestUpgraderShouldUpgrade:
    """Tests for upgrade decision logic."""

    def test_upgrade_on_access_count(self, upgrader: AutoUpgrader) -> None:
        """Datum upgrades after enough accesses."""
        stats = DatumStats(
            id="test",
            tier=Backend.MEMORY,
            access_count=3,
            created_at=time.time(),
        )

        result = upgrader._should_upgrade(stats, time.time())

        assert result == Backend.JSONL

    def test_upgrade_on_age(self, upgrader: AutoUpgrader) -> None:
        """Datum upgrades after enough time."""
        stats = DatumStats(
            id="test",
            tier=Backend.MEMORY,
            access_count=1,
            created_at=time.time() - 2.0,  # 2 seconds old
        )

        result = upgrader._should_upgrade(stats, time.time())

        assert result == Backend.JSONL

    def test_no_upgrade_when_new(self, upgrader: AutoUpgrader) -> None:
        """New datum doesn't upgrade."""
        stats = DatumStats(
            id="test",
            tier=Backend.MEMORY,
            access_count=1,
            created_at=time.time(),
        )

        result = upgrader._should_upgrade(stats, time.time())

        assert result is None

    def test_jsonl_to_sqlite_upgrade(self, upgrader: AutoUpgrader) -> None:
        """JSONL upgrades to SQLite."""
        stats = DatumStats(
            id="test",
            tier=Backend.JSONL,
            access_count=5,
            created_at=time.time(),
        )

        result = upgrader._should_upgrade(stats, time.time())

        assert result == Backend.SQLITE


class TestUpgraderBusIntegration:
    """Tests for DataBus integration."""

    @pytest.mark.asyncio
    async def test_tracks_put_events(
        self,
        upgrader: AutoUpgrader,
        bus: DataBus,
    ) -> None:
        """Upgrader tracks PUT events."""
        await upgrader.start()

        try:
            # Emit PUT event
            event = DataEvent.create(DataEventType.PUT, "datum-1")
            await bus.emit(event)
            await asyncio.sleep(0.05)  # Let event process

            stats = upgrader.get_datum_stats("datum-1")
            assert stats is not None
            assert stats.access_count == 1
        finally:
            await upgrader.stop()

    @pytest.mark.asyncio
    async def test_tracks_access_count(
        self,
        upgrader: AutoUpgrader,
        bus: DataBus,
    ) -> None:
        """Upgrader tracks cumulative access count."""
        await upgrader.start()

        try:
            # Emit multiple events
            for _ in range(3):
                event = DataEvent.create(DataEventType.PUT, "datum-1")
                await bus.emit(event)
                await asyncio.sleep(0.01)

            stats = upgrader.get_datum_stats("datum-1")
            assert stats is not None
            assert stats.access_count == 3
        finally:
            await upgrader.stop()

    @pytest.mark.asyncio
    async def test_removes_on_delete(
        self,
        upgrader: AutoUpgrader,
        bus: DataBus,
    ) -> None:
        """Upgrader removes tracking on DELETE."""
        await upgrader.start()

        try:
            event = DataEvent.create(DataEventType.PUT, "datum-1")
            await bus.emit(event)
            await asyncio.sleep(0.05)

            delete_event = DataEvent.create(DataEventType.DELETE, "datum-1")
            await bus.emit(delete_event)
            await asyncio.sleep(0.05)

            stats = upgrader.get_datum_stats("datum-1")
            assert stats is None
        finally:
            await upgrader.stop()


class TestUpgraderOperation:
    """Tests for upgrade operations."""

    @pytest.mark.asyncio
    async def test_force_upgrade(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
        bus: DataBus,
    ) -> None:
        """force_upgrade() upgrades immediately."""
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            bus=bus,
        )

        # Store datum in source
        d = Datum.create(b"test")
        await memory_backend.put(d)

        # Force upgrade
        success = await upgrader.force_upgrade(d.id, Backend.JSONL)

        assert success is True
        assert await jsonl_backend.get(d.id) is not None

    @pytest.mark.asyncio
    async def test_mark_important(
        self,
        upgrader: AutoUpgrader,
        bus: DataBus,
    ) -> None:
        """mark_important() flags datum."""
        await upgrader.start()

        try:
            event = DataEvent.create(DataEventType.PUT, "datum-1")
            await bus.emit(event)
            await asyncio.sleep(0.05)

            upgrader.mark_important("datum-1")

            stats = upgrader.get_datum_stats("datum-1")
            assert stats is not None
            assert stats.marked_important is True
        finally:
            await upgrader.stop()

    @pytest.mark.asyncio
    async def test_upgrade_callback(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
        bus: DataBus,
    ) -> None:
        """on_upgrade() callbacks are invoked."""
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            bus=bus,
        )

        upgrades = []

        async def track_upgrade(datum, from_tier, to_tier):
            upgrades.append((datum.id, from_tier, to_tier))

        upgrader.on_upgrade(track_upgrade)

        # Store and force upgrade
        d = Datum.create(b"test")
        await memory_backend.put(d)
        await upgrader.force_upgrade(d.id, Backend.JSONL)

        assert len(upgrades) == 1
        assert upgrades[0][0] == d.id
        assert upgrades[0][1] == Backend.MEMORY
        assert upgrades[0][2] == Backend.JSONL


class TestUpgraderStats:
    """Tests for upgrade statistics."""

    @pytest.mark.asyncio
    async def test_stats_tracking(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
        bus: DataBus,
    ) -> None:
        """Stats track upgrades."""
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            bus=bus,
        )

        # Store and upgrade
        d = Datum.create(b"test")
        await memory_backend.put(d)
        await upgrader.force_upgrade(d.id, Backend.JSONL)

        assert upgrader.stats.upgrades_memory_to_jsonl == 1
        assert upgrader.stats.last_upgrade_time is not None


# --- Migration Utilities Tests ---


class TestMigrateData:
    """Tests for migrate_data() function."""

    @pytest.mark.asyncio
    async def test_migrates_all_data(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """migrate_data() moves all data."""
        # Add data to source
        for i in range(5):
            await memory_backend.put(Datum.create(f"item-{i}".encode()))

        # Migrate
        count = await migrate_data(memory_backend, jsonl_backend)

        assert count == 5
        assert await jsonl_backend.count() == 5

    @pytest.mark.asyncio
    async def test_preserves_content(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """migrate_data() preserves datum content."""
        d = Datum.create(b"preserve me", metadata={"key": "value"})
        await memory_backend.put(d)

        await migrate_data(memory_backend, jsonl_backend)

        result = await jsonl_backend.get(d.id)
        assert result is not None
        assert result.content == b"preserve me"
        assert result.metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_delete_source_option(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """migrate_data() can delete from source."""
        d = Datum.create(b"test")
        await memory_backend.put(d)

        await migrate_data(memory_backend, jsonl_backend, delete_source=True)

        # Should be in target, not source
        assert await jsonl_backend.exists(d.id) is True
        assert await memory_backend.exists(d.id) is False

    @pytest.mark.asyncio
    async def test_batch_processing(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """migrate_data() processes in batches."""
        # Add more items than batch size
        for i in range(15):
            await memory_backend.put(Datum.create(f"item-{i}".encode()))

        # Migrate with small batch
        count = await migrate_data(memory_backend, jsonl_backend, batch_size=5)

        assert count == 15
        assert await jsonl_backend.count() == 15


class TestVerifyMigration:
    """Tests for verify_migration() function."""

    @pytest.mark.asyncio
    async def test_successful_verification(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """verify_migration() returns True when complete."""
        # Add and migrate data
        for i in range(3):
            d = Datum.create(f"item-{i}".encode())
            await memory_backend.put(d)
            await jsonl_backend.put(d)

        success, missing = await verify_migration(memory_backend, jsonl_backend)

        assert success is True
        assert missing == []

    @pytest.mark.asyncio
    async def test_detects_missing_data(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """verify_migration() detects missing data."""
        # Add to source only
        d = Datum.create(b"missing from target")
        await memory_backend.put(d)

        success, missing = await verify_migration(memory_backend, jsonl_backend)

        assert success is False
        assert d.id in missing

    @pytest.mark.asyncio
    async def test_empty_source(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
    ) -> None:
        """verify_migration() succeeds with empty source."""
        success, missing = await verify_migration(memory_backend, jsonl_backend)

        assert success is True
        assert missing == []


# --- Integration Tests ---


class TestUpgraderIntegration:
    """Integration tests for complete upgrade flows."""

    @pytest.mark.asyncio
    async def test_automatic_upgrade_on_access(
        self,
        memory_backend: MemoryBackend,
        jsonl_backend: JSONLBackend,
        bus: DataBus,
    ) -> None:
        """Datum auto-upgrades after enough accesses."""
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            bus=bus,
            policy=UpgradePolicy(
                memory_to_jsonl_accesses=2,
                memory_to_jsonl_seconds=999.0,  # Don't trigger on time
            ),
            check_interval=0.05,
        )

        # Store datum
        d = Datum.create(b"test")
        await memory_backend.put(d)

        await upgrader.start()

        try:
            # Access enough times to trigger upgrade
            event1 = DataEvent.create(DataEventType.PUT, d.id)
            await bus.emit(event1)
            await asyncio.sleep(0.02)
            event2 = DataEvent.create(DataEventType.PUT, d.id)
            await bus.emit(event2)
            await asyncio.sleep(0.02)

            # Wait for upgrade check
            await asyncio.sleep(0.1)

            # Should be in JSONL now
            assert await jsonl_backend.exists(d.id) is True
        finally:
            await upgrader.stop()
