"""
Tests for FileWiringTrace and trace persistence.

"Every expansion leaves a mark. Every mark is evidence."
"""

from __future__ import annotations

from datetime import datetime

import pytest

from ..portal import PortalOpenSignal
from ..trace import (
    FileTraceStore,
    FileWiringTrace,
    enable_persistence,
    get_file_trace_store,
    record_expansion,
    record_file_operation,
    reset_file_trace_store,
    sync_file_trace_store,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_store():
    """Reset global store before each test."""
    reset_file_trace_store()
    yield
    reset_file_trace_store()


@pytest.fixture
def sample_signal() -> PortalOpenSignal:
    """Create a sample PortalOpenSignal."""
    return PortalOpenSignal(
        paths_opened=["/home/user/.kgents/operads/WITNESS_OPERAD/walk.op"],
        edge_type="enables",
        parent_path="WITNESS_OPERAD/mark",
        depth=0,
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def store() -> FileTraceStore:
    """Create a fresh FileTraceStore."""
    return FileTraceStore()


# =============================================================================
# FileWiringTrace Tests
# =============================================================================


class TestFileWiringTrace:
    """Tests for FileWiringTrace dataclass."""

    def test_create_minimal(self):
        """Test creating a trace with minimal required fields."""
        trace = FileWiringTrace(
            path="WITNESS_OPERAD/mark",
            operation="read",
            timestamp=datetime.now(),
            actor="user",
        )

        assert trace.path == "WITNESS_OPERAD/mark"
        assert trace.operation == "read"
        assert trace.actor == "user"
        assert trace.diff is None
        assert trace.ghost_alternatives == ()

    def test_create_with_all_fields(self):
        """Test creating a trace with all fields."""
        trace = FileWiringTrace(
            path="WITNESS_OPERAD/walk.op",
            operation="expand",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            actor="Claude",
            diff=None,
            ghost_alternatives=("WITNESS_OPERAD/mark.op", "ASHC/proof.op"),
            edge_type="enables",
            parent_path="WITNESS_OPERAD/mark",
            depth=1,
            session_id="session-123",
        )

        assert trace.edge_type == "enables"
        assert trace.parent_path == "WITNESS_OPERAD/mark"
        assert trace.depth == 1
        assert trace.session_id == "session-123"
        assert len(trace.ghost_alternatives) == 2

    def test_frozen_immutability(self):
        """Test that traces are immutable (Law 1)."""
        trace = FileWiringTrace(
            path="test",
            operation="read",
            timestamp=datetime.now(),
            actor="user",
        )

        with pytest.raises(AttributeError):
            trace.path = "modified"  # type: ignore

    def test_from_portal_signal(self, sample_signal):
        """Test creating traces from a PortalOpenSignal."""
        traces = FileWiringTrace.from_portal_signal(
            sample_signal,
            actor="user",
            session_id="sess-abc",
        )

        assert len(traces) == 1
        trace = traces[0]

        assert trace.path == "/home/user/.kgents/operads/WITNESS_OPERAD/walk.op"
        assert trace.operation == "expand"
        assert trace.edge_type == "enables"
        assert trace.parent_path == "WITNESS_OPERAD/mark"
        assert trace.depth == 0
        assert trace.session_id == "sess-abc"
        assert trace.timestamp == sample_signal.timestamp

    def test_from_portal_signal_multiple_paths(self):
        """Test signal with multiple opened paths."""
        signal = PortalOpenSignal(
            paths_opened=["path1.op", "path2.op", "path3.op"],
            edge_type="feeds",
            parent_path="root",
            depth=0,
            timestamp=datetime.now(),
        )

        traces = FileWiringTrace.from_portal_signal(signal, actor="system")

        assert len(traces) == 3
        assert [t.path for t in traces] == ["path1.op", "path2.op", "path3.op"]
        assert all(t.edge_type == "feeds" for t in traces)

    def test_serialization_roundtrip(self):
        """Test to_dict and from_dict preserve all data."""
        original = FileWiringTrace(
            path="WITNESS_OPERAD/walk.op",
            operation="expand",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            actor="Claude",
            diff="some diff",
            ghost_alternatives=("alt1", "alt2"),
            edge_type="enables",
            parent_path="parent",
            depth=2,
            session_id="session-xyz",
        )

        data = original.to_dict()
        restored = FileWiringTrace.from_dict(data)

        assert restored.path == original.path
        assert restored.operation == original.operation
        assert restored.actor == original.actor
        assert restored.diff == original.diff
        assert restored.ghost_alternatives == original.ghost_alternatives
        assert restored.edge_type == original.edge_type
        assert restored.parent_path == original.parent_path
        assert restored.depth == original.depth
        assert restored.session_id == original.session_id


# =============================================================================
# FileTraceStore Tests
# =============================================================================


class TestFileTraceStore:
    """Tests for FileTraceStore."""

    def test_append_and_retrieve(self, store):
        """Test basic append and retrieval."""
        trace = FileWiringTrace(
            path="test.op",
            operation="read",
            timestamp=datetime.now(),
            actor="user",
        )

        store.append(trace)

        assert len(store) == 1
        assert store.all() == [trace]

    def test_append_only(self, store):
        """Test that store is append-only."""
        trace1 = FileWiringTrace(
            path="first.op",
            operation="read",
            timestamp=datetime(2024, 1, 1),
            actor="user",
        )
        trace2 = FileWiringTrace(
            path="second.op",
            operation="expand",
            timestamp=datetime(2024, 1, 2),
            actor="Claude",
        )

        store.append(trace1)
        store.append(trace2)

        all_traces = store.all()
        assert len(all_traces) == 2
        assert all_traces[0] == trace1
        assert all_traces[1] == trace2

    def test_session_index(self, store):
        """Test session-based retrieval."""
        trace1 = FileWiringTrace(
            path="a.op",
            operation="read",
            timestamp=datetime.now(),
            actor="user",
            session_id="session-1",
        )
        trace2 = FileWiringTrace(
            path="b.op",
            operation="read",
            timestamp=datetime.now(),
            actor="user",
            session_id="session-2",
        )
        trace3 = FileWiringTrace(
            path="c.op",
            operation="read",
            timestamp=datetime.now(),
            actor="user",
            session_id="session-1",
        )

        store.append(trace1)
        store.append(trace2)
        store.append(trace3)

        session_1_trail = store.get_session_trail("session-1")
        session_2_trail = store.get_session_trail("session-2")

        assert len(session_1_trail) == 2
        assert len(session_2_trail) == 1
        assert session_1_trail[0].path == "a.op"
        assert session_1_trail[1].path == "c.op"

    def test_path_index(self, store):
        """Test path-based retrieval."""
        trace1 = FileWiringTrace(
            path="WITNESS_OPERAD/mark.op",
            operation="read",
            timestamp=datetime(2024, 1, 1),
            actor="user",
        )
        trace2 = FileWiringTrace(
            path="WITNESS_OPERAD/mark.op",
            operation="expand",
            timestamp=datetime(2024, 1, 2),
            actor="Claude",
        )
        trace3 = FileWiringTrace(
            path="OTHER_OPERAD/other.op",
            operation="read",
            timestamp=datetime(2024, 1, 3),
            actor="user",
        )

        store.append(trace1)
        store.append(trace2)
        store.append(trace3)

        mark_history = store.get_path_history("WITNESS_OPERAD/mark.op")
        other_history = store.get_path_history("OTHER_OPERAD/other.op")

        assert len(mark_history) == 2
        assert len(other_history) == 1

    def test_recent(self, store):
        """Test getting recent traces."""
        for i in range(10):
            trace = FileWiringTrace(
                path=f"file{i}.op",
                operation="read",
                timestamp=datetime.now(),
                actor="user",
            )
            store.append(trace)

        recent = store.recent(3)
        assert len(recent) == 3
        assert recent[0].path == "file7.op"
        assert recent[1].path == "file8.op"
        assert recent[2].path == "file9.op"


# =============================================================================
# Global Store and API Tests
# =============================================================================


class TestGlobalStoreAPI:
    """Tests for global store and convenience functions."""

    def test_get_global_store_singleton(self):
        """Test that global store is a singleton."""
        store1 = get_file_trace_store()
        store2 = get_file_trace_store()

        assert store1 is store2

    def test_reset_clears_store(self):
        """Test that reset creates a new store."""
        store1 = get_file_trace_store()
        store1.append(
            FileWiringTrace(
                path="test",
                operation="read",
                timestamp=datetime.now(),
                actor="user",
            )
        )

        assert len(store1) == 1

        reset_file_trace_store()
        store2 = get_file_trace_store()

        assert len(store2) == 0
        assert store1 is not store2

    def test_record_expansion(self, sample_signal):
        """Test record_expansion convenience function."""
        traces = record_expansion(sample_signal, actor="Claude", session_id="sess-1")

        assert len(traces) == 1

        store = get_file_trace_store()
        assert len(store) == 1

        stored = store.all()[0]
        assert stored.operation == "expand"
        assert stored.actor == "Claude"
        assert stored.session_id == "sess-1"

    def test_record_file_operation(self):
        """Test record_file_operation for non-expansion ops."""
        trace = record_file_operation(
            path="new_file.op",
            operation="create",
            actor="Kent",
            ghost_alternatives=("other_name.op", "alternate.op"),
            session_id="sess-2",
        )

        assert trace.path == "new_file.op"
        assert trace.operation == "create"
        assert trace.actor == "Kent"
        assert trace.ghost_alternatives == ("other_name.op", "alternate.op")

        store = get_file_trace_store()
        assert len(store) == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestTraceIntegration:
    """Integration tests for trace recording."""

    def test_trail_reconstruction(self):
        """Test reconstructing a navigation trail from traces."""
        session_id = "exploration-001"

        # Simulate a navigation sequence
        signal1 = PortalOpenSignal(
            paths_opened=["WITNESS_OPERAD/mark.op"],
            edge_type="root",
            parent_path="root",
            depth=0,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
        )
        signal2 = PortalOpenSignal(
            paths_opened=["WITNESS_OPERAD/walk.op"],
            edge_type="enables",
            parent_path="WITNESS_OPERAD/mark.op",
            depth=1,
            timestamp=datetime(2024, 1, 1, 10, 1, 0),
        )
        signal3 = PortalOpenSignal(
            paths_opened=["ASHC/proof.op"],
            edge_type="feeds",
            parent_path="WITNESS_OPERAD/walk.op",
            depth=2,
            timestamp=datetime(2024, 1, 1, 10, 2, 0),
        )

        record_expansion(signal1, actor="user", session_id=session_id)
        record_expansion(signal2, actor="user", session_id=session_id)
        record_expansion(signal3, actor="user", session_id=session_id)

        store = get_file_trace_store()
        trail = store.get_session_trail(session_id)

        assert len(trail) == 3
        assert trail[0].depth == 0
        assert trail[1].depth == 1
        assert trail[2].depth == 2

        # Verify causal chain via parent_path
        assert trail[1].parent_path == "WITNESS_OPERAD/mark.op"
        assert trail[2].parent_path == "WITNESS_OPERAD/walk.op"

    def test_multiple_sessions_isolation(self):
        """Test that different sessions are isolated."""
        signal = PortalOpenSignal(
            paths_opened=["same_file.op"],
            edge_type="test",
            parent_path="root",
            depth=0,
            timestamp=datetime.now(),
        )

        record_expansion(signal, actor="user", session_id="session-A")
        record_expansion(signal, actor="Claude", session_id="session-B")
        record_expansion(signal, actor="user", session_id="session-A")

        store = get_file_trace_store()

        trail_a = store.get_session_trail("session-A")
        trail_b = store.get_session_trail("session-B")

        assert len(trail_a) == 2
        assert len(trail_b) == 1
        assert all(t.actor == "user" for t in trail_a)
        assert trail_b[0].actor == "Claude"


# =============================================================================
# Persistence Tests (Session 4)
# =============================================================================


class TestPersistence:
    """Tests for FileTraceStore persistence."""

    def test_save_and_load_roundtrip(self, tmp_path):
        """Test that save/load preserves all trace data."""
        persistence_file = tmp_path / "traces.json"

        # Create store and add traces
        store = FileTraceStore()
        store.set_persistence_path(persistence_file)

        trace1 = FileWiringTrace(
            path="WITNESS_OPERAD/mark.op",
            operation="expand",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            actor="user",
            edge_type="enables",
            parent_path="root",
            depth=0,
            session_id="session-1",
        )
        trace2 = FileWiringTrace(
            path="WITNESS_OPERAD/walk.op",
            operation="expand",
            timestamp=datetime(2024, 1, 15, 10, 31, 0),
            actor="Claude",
            edge_type="feeds",
            parent_path="WITNESS_OPERAD/mark.op",
            depth=1,
            session_id="session-1",
            ghost_alternatives=("alt1", "alt2"),
        )

        store.append(trace1)
        store.append(trace2)
        store.save()

        # Verify file was created
        assert persistence_file.exists()

        # Load into new store
        loaded = FileTraceStore.load(persistence_file)

        assert len(loaded) == 2

        # Verify first trace
        loaded_trace1 = loaded.all()[0]
        assert loaded_trace1.path == trace1.path
        assert loaded_trace1.operation == trace1.operation
        assert loaded_trace1.actor == trace1.actor
        assert loaded_trace1.edge_type == trace1.edge_type
        assert loaded_trace1.depth == trace1.depth

        # Verify second trace with ghost_alternatives
        loaded_trace2 = loaded.all()[1]
        assert loaded_trace2.ghost_alternatives == ("alt1", "alt2")

        # Verify indices were rebuilt
        assert len(loaded.get_session_trail("session-1")) == 2
        assert len(loaded.get_path_history("WITNESS_OPERAD/mark.op")) == 1

    def test_load_or_create_creates_new(self, tmp_path):
        """Test load_or_create creates new store if file doesn't exist."""
        persistence_file = tmp_path / "nonexistent.json"

        store = FileTraceStore.load_or_create(persistence_file)

        assert len(store) == 0
        assert store.persistence_path == persistence_file

    def test_load_or_create_loads_existing(self, tmp_path):
        """Test load_or_create loads from existing file."""
        persistence_file = tmp_path / "existing.json"

        # Create and save initial store
        store1 = FileTraceStore()
        store1.append(
            FileWiringTrace(
                path="test.op",
                operation="read",
                timestamp=datetime.now(),
                actor="user",
            )
        )
        store1.save(persistence_file)

        # Load via load_or_create
        store2 = FileTraceStore.load_or_create(persistence_file)

        assert len(store2) == 1
        assert store2.all()[0].path == "test.op"

    def test_sync_saves_to_persistence_path(self, tmp_path):
        """Test sync() saves to the configured persistence path."""
        persistence_file = tmp_path / "sync_test.json"

        store = FileTraceStore()
        store.set_persistence_path(persistence_file)
        store.append(
            FileWiringTrace(
                path="synced.op",
                operation="expand",
                timestamp=datetime.now(),
                actor="system",
            )
        )

        # Sync should save
        result = store.sync()

        assert result == persistence_file
        assert persistence_file.exists()

        # Verify content
        loaded = FileTraceStore.load(persistence_file)
        assert len(loaded) == 1
        assert loaded.all()[0].path == "synced.op"

    def test_sync_returns_none_without_persistence_path(self):
        """Test sync() returns None if no persistence path set."""
        store = FileTraceStore()
        store.append(
            FileWiringTrace(
                path="test.op",
                operation="read",
                timestamp=datetime.now(),
                actor="user",
            )
        )

        assert store.sync() is None

    def test_load_raises_on_missing_file(self, tmp_path):
        """Test load() raises FileNotFoundError for missing file."""
        nonexistent = tmp_path / "does_not_exist.json"

        with pytest.raises(FileNotFoundError):
            FileTraceStore.load(nonexistent)

    def test_persistence_preserves_timestamps(self, tmp_path):
        """Test that timestamp precision is preserved through persistence."""
        persistence_file = tmp_path / "timestamps.json"

        original_time = datetime(2024, 6, 15, 14, 30, 45, 123456)  # With microseconds

        store = FileTraceStore()
        store.append(
            FileWiringTrace(
                path="time_test.op",
                operation="read",
                timestamp=original_time,
                actor="user",
            )
        )
        store.save(persistence_file)

        loaded = FileTraceStore.load(persistence_file)
        loaded_trace = loaded.all()[0]

        # ISO format preserves microseconds
        assert loaded_trace.timestamp == original_time


class TestGlobalPersistenceAPI:
    """Tests for global store persistence API."""

    def test_enable_persistence_creates_store_with_path(self, tmp_path, monkeypatch):
        """Test enable_persistence sets up store with default path."""
        # Monkeypatch the default path to use tmp_path
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

        store = enable_persistence()

        assert store is not None
        assert store.persistence_path is not None
        assert "kgents" in str(store.persistence_path)
        assert "trails" in str(store.persistence_path)

    def test_sync_file_trace_store(self, tmp_path, monkeypatch):
        """Test sync_file_trace_store syncs global store."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

        # Reset to start fresh
        reset_file_trace_store()

        # Enable and record
        enable_persistence()
        record_file_operation("test.op", "read", actor="user")

        # Sync should save
        result = sync_file_trace_store()

        assert result is not None
        assert result.exists()

    def test_get_file_trace_store_with_persistence(self, tmp_path, monkeypatch):
        """Test get_file_trace_store with persistence flag."""
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

        # Reset first
        reset_file_trace_store()

        # Get with persistence
        store = get_file_trace_store(with_persistence=True)

        assert store is not None
        assert store.persistence_path is not None
