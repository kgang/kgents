"""
Tests for LifecycleManager.

Tests bootstrap, shutdown, mode detection, and instance management.
"""

import pytest
import asyncio
import os
import socket
from datetime import datetime, timedelta
from pathlib import Path

from ..lifecycle import (
    LifecycleManager,
    OperationMode,
    LifecycleState,
    quick_bootstrap,
)


class TestOperationMode:
    """Tests for OperationMode enum."""

    def test_mode_values(self):
        """Should have expected mode values."""
        assert OperationMode.DB_LESS.value == "db_less"
        assert OperationMode.LOCAL_ONLY.value == "local"
        assert OperationMode.GLOBAL_ONLY.value == "global"
        assert OperationMode.FULL.value == "full"

    def test_mode_string_comparison(self):
        """Modes should compare as strings."""
        assert OperationMode.DB_LESS == "db_less"
        assert OperationMode.GLOBAL_ONLY == "global"


class TestLifecycleState:
    """Tests for LifecycleState dataclass."""

    def test_create_minimal_state(self):
        """Should create state with minimal fields."""
        state = LifecycleState(
            mode=OperationMode.DB_LESS,
            global_db_exists=False,
            project_db_exists=False,
            storage_provider=None,
            instance_id=None,
        )

        assert state.mode == OperationMode.DB_LESS
        assert state.storage_provider is None
        assert state.errors == []

    def test_create_full_state(self):
        """Should create state with all fields."""
        state = LifecycleState(
            mode=OperationMode.FULL,
            global_db_exists=True,
            project_db_exists=True,
            storage_provider=None,  # Would be real provider in practice
            instance_id="inst-123",
            project_path=Path("/some/project"),
            project_hash="abc123",
            errors=["warning: something"],
        )

        assert state.mode == OperationMode.FULL
        assert state.instance_id == "inst-123"
        assert state.project_hash == "abc123"
        assert len(state.errors) == 1


class TestLifecycleManagerModeDetection:
    """Tests for mode detection logic."""

    @pytest.mark.asyncio
    async def test_db_less_mode_no_files(self, tmp_path, monkeypatch):
        """Should detect DB-less mode when nothing exists."""
        # Set up empty XDG paths
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()

        assert state.mode == OperationMode.DB_LESS
        assert state.storage_provider is None

    @pytest.mark.asyncio
    async def test_global_mode_when_db_exists(self, tmp_path, monkeypatch):
        """Should detect global mode when only global DB exists."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()

        assert state.mode == OperationMode.GLOBAL_ONLY
        assert state.global_db_exists is True
        assert state.project_db_exists is False

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_local_mode_when_project_db_only(self, tmp_path, monkeypatch):
        """Should detect local mode when only project DB exists."""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / ".kgents").mkdir()
        (project_path / ".kgents" / "cortex.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap(project_path)

        assert state.mode == OperationMode.LOCAL_ONLY
        assert state.project_db_exists is True
        assert state.global_db_exists is False

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_full_mode_when_both_exist(self, tmp_path, monkeypatch):
        """Should detect full mode when both DBs exist."""
        # Global DB
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        # Project DB
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / ".kgents").mkdir()
        (project_path / ".kgents" / "cortex.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap(project_path)

        assert state.mode == OperationMode.FULL
        assert state.global_db_exists is True
        assert state.project_db_exists is True

        await manager.shutdown()


class TestLifecycleManagerBootstrap:
    """Tests for bootstrap sequence."""

    @pytest.mark.asyncio
    async def test_bootstrap_creates_directories(self, tmp_path, monkeypatch):
        """Should create XDG directories during bootstrap."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        # Pre-create global DB marker so we don't stay in DB-less mode
        (tmp_path / "data" / "kgents").mkdir(parents=True)
        (tmp_path / "data" / "kgents" / "membrane.db").touch()

        manager = LifecycleManager()
        await manager.bootstrap()

        assert (tmp_path / "config" / "kgents").exists()
        assert (tmp_path / "data" / "kgents").exists()
        assert (tmp_path / "cache" / "kgents").exists()

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_bootstrap_registers_instance(self, tmp_path, monkeypatch):
        """Should register instance in database."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()

        assert state.instance_id is not None
        assert state.storage_provider is not None

        # Verify instance in database
        instances = await state.storage_provider.relational.fetch_all(
            "SELECT * FROM instances WHERE id = :id",
            {"id": state.instance_id},
        )
        assert len(instances) == 1
        assert instances[0]["hostname"] == socket.gethostname()
        assert instances[0]["pid"] == os.getpid()
        assert instances[0]["status"] == "active"

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_bootstrap_computes_project_hash(self, tmp_path, monkeypatch):
        """Should compute stable project hash."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        project_path = tmp_path / "my-project"
        project_path.mkdir()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap(project_path)

        assert state.project_hash is not None
        assert len(state.project_hash) == 8  # First 8 chars of SHA256

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_bootstrap_logs_startup_event(self, tmp_path, monkeypatch):
        """Should log startup telemetry event."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()

        events = await state.storage_provider.telemetry.query(
            event_type="instance.started"
        )
        assert len(events) >= 1
        assert events[0].instance_id == state.instance_id

        await manager.shutdown()


class TestLifecycleManagerShutdown:
    """Tests for shutdown sequence."""

    @pytest.mark.asyncio
    async def test_shutdown_marks_instance_terminated(self, tmp_path, monkeypatch):
        """Should mark instance as terminated on shutdown."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()
        instance_id = state.instance_id

        # Get storage before shutdown

        # Re-connect to verify
        await manager.shutdown()

        # Re-open DB to verify
        from ..providers.sqlite import SQLiteRelationalStore

        store = SQLiteRelationalStore(data_dir / "membrane.db")
        row = await store.fetch_one(
            "SELECT status FROM instances WHERE id = :id",
            {"id": instance_id},
        )
        assert row["status"] == "terminated"
        await store.close()

    @pytest.mark.asyncio
    async def test_shutdown_logs_event(self, tmp_path, monkeypatch):
        """Should log shutdown telemetry event."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        await manager.bootstrap()
        await manager.shutdown()

        # Re-open to check telemetry
        from ..providers.sqlite import SQLiteTelemetryStore

        store = SQLiteTelemetryStore(data_dir / "telemetry.db")
        events = await store.query(event_type="instance.stopped")
        assert len(events) >= 1
        await store.close()

    @pytest.mark.asyncio
    async def test_shutdown_runs_handlers(self, tmp_path, monkeypatch):
        """Should run registered shutdown handlers."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        handler_called = []

        async def my_handler():
            handler_called.append(True)

        manager = LifecycleManager()
        await manager.bootstrap()
        manager.on_shutdown(my_handler)
        await manager.shutdown()

        assert handler_called == [True]

    @pytest.mark.asyncio
    async def test_shutdown_safe_when_not_bootstrapped(self):
        """Should not raise when shutting down without bootstrap."""
        manager = LifecycleManager()
        await manager.shutdown()  # Should not raise


class TestLifecycleManagerHeartbeat:
    """Tests for heartbeat functionality."""

    @pytest.mark.asyncio
    async def test_heartbeat_updates_timestamp(self, tmp_path, monkeypatch):
        """Should update last_heartbeat timestamp."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()

        # Get initial heartbeat
        initial = await state.storage_provider.relational.fetch_one(
            "SELECT last_heartbeat FROM instances WHERE id = :id",
            {"id": state.instance_id},
        )

        # Wait a tiny bit
        await asyncio.sleep(0.01)

        # Update heartbeat
        await manager.heartbeat()

        # Check updated
        updated = await state.storage_provider.relational.fetch_one(
            "SELECT last_heartbeat FROM instances WHERE id = :id",
            {"id": state.instance_id},
        )

        assert updated["last_heartbeat"] > initial["last_heartbeat"]

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_heartbeat_safe_when_not_bootstrapped(self):
        """Should not raise when heartbeat called without bootstrap."""
        manager = LifecycleManager()
        await manager.heartbeat()  # Should not raise


class TestLifecycleManagerCleanup:
    """Tests for stale instance cleanup."""

    @pytest.mark.asyncio
    async def test_cleanup_stale_instances(self, tmp_path, monkeypatch):
        """Should mark stale instances."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager = LifecycleManager()
        state = await manager.bootstrap()

        # Insert a fake stale instance
        stale_time = (datetime.now() - timedelta(minutes=10)).isoformat()
        await state.storage_provider.relational.execute(
            """
            INSERT INTO instances (id, hostname, pid, started_at, last_heartbeat, status)
            VALUES (:id, :hostname, :pid, :started_at, :last_heartbeat, :status)
            """,
            {
                "id": "stale-instance",
                "hostname": "old-host",
                "pid": 99999,
                "started_at": stale_time,
                "last_heartbeat": stale_time,
                "status": "active",
            },
        )

        # Run cleanup
        cleaned = await manager.cleanup_stale_instances(stale_minutes=5)
        assert cleaned == 1

        # Verify status changed
        row = await state.storage_provider.relational.fetch_one(
            "SELECT status FROM instances WHERE id = :id",
            {"id": "stale-instance"},
        )
        assert row["status"] == "stale"

        await manager.shutdown()


class TestQuickBootstrap:
    """Tests for quick_bootstrap convenience function."""

    @pytest.mark.asyncio
    async def test_quick_bootstrap(self, tmp_path, monkeypatch):
        """Should return manager and state tuple."""
        data_dir = tmp_path / "data" / "kgents"
        data_dir.mkdir(parents=True)
        (data_dir / "membrane.db").touch()

        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        manager, state = await quick_bootstrap()

        assert manager is not None
        assert state is not None
        assert state.instance_id is not None

        await manager.shutdown()
