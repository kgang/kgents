"""
Tests for context bridge: portal signals to context events.

"Portal expansion updates agent context—these files are now 'open'."
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from protocols.file_operad.context_bridge import (
    ContextAccumulator,
    ContextEvent,
    portal_signal_to_context_event,
)
from protocols.file_operad.portal import PortalOpenSignal

# =============================================================================
# ContextEvent Tests
# =============================================================================


class TestContextEvent:
    """Tests for ContextEvent data structure."""

    def test_create_files_opened(self) -> None:
        """Create a files_opened event."""
        event = ContextEvent.files_opened(
            paths=["/path/to/file1.op", "/path/to/file2.op"],
            reason="Followed [tests] from main.op",
            depth=1,
        )

        assert event.type == "files_opened"
        assert len(event.paths) == 2
        assert event.paths[0] == "/path/to/file1.op"
        assert event.reason == "Followed [tests] from main.op"
        assert event.depth == 1

    def test_create_files_closed(self) -> None:
        """Create a files_closed event."""
        event = ContextEvent.files_closed(
            paths=("/path/to/file.op",),
            reason="Portal collapsed",
            depth=0,
        )

        assert event.type == "files_closed"
        assert len(event.paths) == 1

    def test_create_focus_changed(self) -> None:
        """Create a focus_changed event."""
        event = ContextEvent.focus_changed(
            paths=["new_focus.op"],
            reason="Navigation",
            depth=2,
        )

        assert event.type == "focus_changed"

    def test_immutability(self) -> None:
        """ContextEvent is immutable (frozen dataclass)."""
        event = ContextEvent.files_opened(
            paths=["file.op"],
            reason="Test",
            depth=0,
        )

        with pytest.raises(AttributeError):
            event.type = "files_closed"  # type: ignore

        with pytest.raises(AttributeError):
            event.paths = ("new.op",)  # type: ignore

    def test_paths_are_tuple(self) -> None:
        """Paths are stored as immutable tuple."""
        event = ContextEvent.files_opened(
            paths=["a.op", "b.op"],  # List input
            reason="Test",
            depth=0,
        )

        assert isinstance(event.paths, tuple)
        assert event.paths == ("a.op", "b.op")


# =============================================================================
# Portal Signal Conversion Tests
# =============================================================================


class TestPortalSignalConversion:
    """Tests for converting PortalOpenSignal to ContextEvent."""

    def test_from_portal_signal(self) -> None:
        """Convert PortalOpenSignal to ContextEvent."""
        signal = PortalOpenSignal(
            paths_opened=["WITNESS_OPERAD/walk.op"],
            edge_type="enables",
            parent_path="WITNESS_OPERAD/mark.op",
            depth=1,
        )

        event = ContextEvent.from_portal_signal(signal)

        assert event.type == "files_opened"
        assert event.paths == ("WITNESS_OPERAD/walk.op",)
        assert "[enables]" in event.reason
        assert "WITNESS_OPERAD/mark.op" in event.reason
        assert event.depth == 1
        assert event.edge_type == "enables"
        assert event.parent_path == "WITNESS_OPERAD/mark.op"

    def test_portal_signal_to_context_event_function(self) -> None:
        """Test the bridge function."""
        signal = PortalOpenSignal(
            paths_opened=["file.op"],
            edge_type="tests",
            parent_path="root.op",
            depth=0,
        )

        event = portal_signal_to_context_event(signal)

        assert event.type == "files_opened"
        assert event.paths == ("file.op",)

    def test_signal_to_context_event_method(self) -> None:
        """Test the to_context_event method on PortalOpenSignal."""
        signal = PortalOpenSignal(
            paths_opened=["a.op", "b.op"],
            edge_type="imports",
            parent_path="main.op",
            depth=2,
        )

        event = signal.to_context_event()

        assert event.type == "files_opened"
        assert len(event.paths) == 2
        assert event.depth == 2

    def test_multiple_paths_preserved(self) -> None:
        """Multiple paths from signal are preserved in event."""
        signal = PortalOpenSignal(
            paths_opened=["a.op", "b.op", "c.op"],
            edge_type="related",
            parent_path="root.op",
            depth=1,
        )

        event = signal.to_context_event()

        assert len(event.paths) == 3
        assert "a.op" in event.paths
        assert "b.op" in event.paths
        assert "c.op" in event.paths


# =============================================================================
# Serialization Tests
# =============================================================================


class TestContextEventSerialization:
    """Tests for ContextEvent serialization."""

    def test_to_dict(self) -> None:
        """Serialize event to dictionary."""
        event = ContextEvent.files_opened(
            paths=["file.op"],
            reason="Test",
            depth=1,
            parent_path="parent.op",
            edge_type="tests",
        )

        data = event.to_dict()

        assert data["type"] == "files_opened"
        assert data["paths"] == ["file.op"]
        assert data["reason"] == "Test"
        assert data["depth"] == 1
        assert data["parent_path"] == "parent.op"
        assert data["edge_type"] == "tests"
        assert "timestamp" in data

    def test_from_dict(self) -> None:
        """Deserialize event from dictionary."""
        data = {
            "type": "files_opened",
            "paths": ["file.op"],
            "reason": "Test",
            "depth": 1,
            "timestamp": "2025-12-22T10:00:00+00:00",
            "parent_path": "parent.op",
            "edge_type": "tests",
        }

        event = ContextEvent.from_dict(data)

        assert event.type == "files_opened"
        assert event.paths == ("file.op",)
        assert event.reason == "Test"
        assert event.depth == 1
        assert event.timestamp.year == 2025

    def test_roundtrip(self) -> None:
        """Serialize and deserialize preserves data."""
        original = ContextEvent.files_opened(
            paths=["a.op", "b.op"],
            reason="Roundtrip test",
            depth=2,
            parent_path="root.op",
            edge_type="enables",
        )

        data = original.to_dict()
        restored = ContextEvent.from_dict(data)

        assert restored.type == original.type
        assert restored.paths == original.paths
        assert restored.reason == original.reason
        assert restored.depth == original.depth
        assert restored.parent_path == original.parent_path
        assert restored.edge_type == original.edge_type


# =============================================================================
# ContextAccumulator Tests
# =============================================================================


class TestContextAccumulator:
    """Tests for ContextAccumulator state tracking."""

    def test_initial_state(self) -> None:
        """Accumulator starts empty."""
        accumulator = ContextAccumulator()

        assert accumulator.open_count == 0
        assert accumulator.event_count == 0
        assert len(accumulator.open_paths) == 0

    def test_apply_files_opened(self) -> None:
        """Apply files_opened event adds paths."""
        accumulator = ContextAccumulator()
        event = ContextEvent.files_opened(
            paths=["/a.py", "/b.py"],
            reason="Test",
            depth=1,
        )

        result = accumulator.apply(event)

        assert result is True  # New event
        assert accumulator.open_count == 2
        assert accumulator.is_open("/a.py")
        assert accumulator.is_open("/b.py")
        assert not accumulator.is_open("/c.py")

    def test_apply_files_closed(self) -> None:
        """Apply files_closed event removes paths."""
        accumulator = ContextAccumulator()

        # First open some files
        open_event = ContextEvent.files_opened(
            paths=["/a.py", "/b.py", "/c.py"],
            reason="Open",
            depth=1,
        )
        accumulator.apply(open_event)
        assert accumulator.open_count == 3

        # Then close some
        close_event = ContextEvent.files_closed(
            paths=["/a.py", "/b.py"],
            reason="Close",
            depth=0,
        )
        accumulator.apply(close_event)

        assert accumulator.open_count == 1
        assert not accumulator.is_open("/a.py")
        assert not accumulator.is_open("/b.py")
        assert accumulator.is_open("/c.py")

    def test_apply_focus_changed(self) -> None:
        """Apply focus_changed event replaces all paths."""
        accumulator = ContextAccumulator()

        # Open some files
        open_event = ContextEvent.files_opened(
            paths=["/a.py", "/b.py"],
            reason="Open",
            depth=1,
        )
        accumulator.apply(open_event)
        assert accumulator.open_count == 2

        # Focus change replaces
        focus_event = ContextEvent.focus_changed(
            paths=["/x.py", "/y.py", "/z.py"],
            reason="Focus",
            depth=0,
        )
        accumulator.apply(focus_event)

        assert accumulator.open_count == 3
        assert not accumulator.is_open("/a.py")
        assert not accumulator.is_open("/b.py")
        assert accumulator.is_open("/x.py")
        assert accumulator.is_open("/y.py")
        assert accumulator.is_open("/z.py")

    def test_idempotent_apply(self) -> None:
        """Applying same event twice is a no-op (idempotent)."""
        accumulator = ContextAccumulator()
        event = ContextEvent.files_opened(
            paths=["/a.py"],
            reason="Test",
            depth=1,
        )

        # First apply
        result1 = accumulator.apply(event)
        assert result1 is True
        assert accumulator.event_count == 1

        # Second apply (same event) - should be no-op
        result2 = accumulator.apply(event)
        assert result2 is False  # Duplicate
        assert accumulator.event_count == 1  # Still 1
        assert accumulator.open_count == 1  # Still 1 file

    def test_event_history_monotonic(self) -> None:
        """Event history only grows (append-only)."""
        accumulator = ContextAccumulator()

        events = [
            ContextEvent.files_opened(paths=["/a.py"], reason="1", depth=0),
            ContextEvent.files_opened(paths=["/b.py"], reason="2", depth=1),
            ContextEvent.files_closed(paths=["/a.py"], reason="3", depth=0),
        ]

        for event in events:
            accumulator.apply(event)

        assert accumulator.event_count == 3
        assert accumulator.event_history[0].reason == "1"
        assert accumulator.event_history[1].reason == "2"
        assert accumulator.event_history[2].reason == "3"

    def test_close_all(self) -> None:
        """close_all() closes all open files."""
        accumulator = ContextAccumulator()

        # Open some files
        accumulator.apply(
            ContextEvent.files_opened(
                paths=["/a.py", "/b.py", "/c.py"],
                reason="Open",
                depth=1,
            )
        )
        assert accumulator.open_count == 3

        # Close all
        event = accumulator.close_all()

        assert accumulator.open_count == 0
        assert event.type == "files_closed"
        assert len(event.paths) == 3

    def test_close_all_empty(self) -> None:
        """close_all() on empty accumulator returns event with no paths."""
        accumulator = ContextAccumulator()

        event = accumulator.close_all()

        assert event.type == "files_closed"
        assert len(event.paths) == 0
        assert accumulator.open_count == 0

    def test_summary(self) -> None:
        """summary() returns human-readable state."""
        accumulator = ContextAccumulator()
        accumulator.apply(
            ContextEvent.files_opened(
                paths=["/path/to/file.py"],
                reason="Test",
                depth=1,
            )
        )

        summary = accumulator.summary()

        assert "Open files: 1" in summary
        assert "/path/to/file.py" in summary
        assert "Total events: 1" in summary

    def test_multiple_open_events(self) -> None:
        """Multiple open events accumulate paths."""
        accumulator = ContextAccumulator()

        accumulator.apply(
            ContextEvent.files_opened(
                paths=["/a.py"],
                reason="First",
                depth=1,
            )
        )
        accumulator.apply(
            ContextEvent.files_opened(
                paths=["/b.py", "/c.py"],
                reason="Second",
                depth=2,
            )
        )

        assert accumulator.open_count == 3
        assert accumulator.is_open("/a.py")
        assert accumulator.is_open("/b.py")
        assert accumulator.is_open("/c.py")
