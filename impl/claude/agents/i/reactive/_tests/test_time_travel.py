"""Tests for Signal time-travel (snapshot/restore) functionality."""

from __future__ import annotations

import time

import pytest
from agents.i.reactive.signal import Signal, Snapshot


class TestSnapshot:
    """Tests for Snapshot dataclass."""

    def test_snapshot_is_frozen(self) -> None:
        """Snapshot is immutable (frozen dataclass)."""
        snap = Snapshot(value=42, timestamp=1.0, generation=5)
        with pytest.raises(Exception):  # FrozenInstanceError
            snap.value = 100  # type: ignore[misc]

    def test_snapshot_stores_value(self) -> None:
        """Snapshot captures the value."""
        snap = Snapshot(value="hello", timestamp=0.0, generation=0)
        assert snap.value == "hello"

    def test_snapshot_stores_timestamp(self) -> None:
        """Snapshot records timestamp."""
        snap = Snapshot(value=1, timestamp=123.456, generation=0)
        assert snap.timestamp == 123.456

    def test_snapshot_stores_generation(self) -> None:
        """Snapshot records generation count."""
        snap = Snapshot(value=1, timestamp=0.0, generation=42)
        assert snap.generation == 42


class TestSignalSnapshot:
    """Tests for Signal.snapshot() method."""

    def test_snapshot_captures_current_value(self) -> None:
        """Snapshot captures the signal's current value."""
        sig = Signal.of(42)
        snap = sig.snapshot()
        assert snap.value == 42

    def test_snapshot_captures_initial_generation(self) -> None:
        """Initial signal has generation 0."""
        sig = Signal.of("test")
        snap = sig.snapshot()
        assert snap.generation == 0

    def test_snapshot_generation_increments_on_set(self) -> None:
        """Generation increments each time value changes."""
        sig = Signal.of(0)
        assert sig.generation == 0

        sig.set(1)
        assert sig.generation == 1

        sig.set(2)
        assert sig.generation == 2

    def test_snapshot_generation_no_increment_same_value(self) -> None:
        """Generation does not increment when setting same value."""
        sig = Signal.of(5)
        sig.set(5)  # Same value
        sig.set(5)  # Same again
        assert sig.generation == 0

    def test_snapshot_captures_timestamp(self) -> None:
        """Snapshot records monotonic timestamp."""
        sig = Signal.of(100)
        before = time.monotonic()
        snap = sig.snapshot()
        after = time.monotonic()

        assert before <= snap.timestamp <= after

    def test_snapshot_is_independent_of_signal(self) -> None:
        """Snapshot is independent—changing signal doesn't affect it."""
        sig = Signal.of(10)
        snap = sig.snapshot()
        sig.set(999)

        assert snap.value == 10  # Original value
        assert sig.value == 999  # New value


class TestSignalRestore:
    """Tests for Signal.restore() method."""

    def test_restore_returns_to_snapshot_value(self) -> None:
        """Restore sets signal back to snapshot's value."""
        sig = Signal.of(42)
        snap = sig.snapshot()
        sig.set(100)
        sig.restore(snap)

        assert sig.value == 42

    def test_restore_notifies_subscribers(self) -> None:
        """Restore triggers subscriber notification."""
        sig = Signal.of(1)
        snap = sig.snapshot()
        sig.set(999)

        received: list[int] = []
        sig.subscribe(lambda v: received.append(v))

        sig.restore(snap)  # Back to 1
        assert received == [1]

    def test_restore_no_notify_if_same_value(self) -> None:
        """Restore doesn't notify if value unchanged."""
        sig = Signal.of(5)
        snap = sig.snapshot()
        # Don't change value

        received: list[int] = []
        sig.subscribe(lambda v: received.append(v))

        sig.restore(snap)  # Value is still 5
        assert received == []  # No notification

    def test_restore_generation_continues_forward(self) -> None:
        """Restoring doesn't reset generation—it continues forward."""
        sig = Signal.of(0)
        snap = sig.snapshot()  # gen 0
        sig.set(1)  # gen 1
        sig.set(2)  # gen 2

        sig.restore(snap)  # Restore to value 0, but gen becomes 3
        assert sig.value == 0
        assert sig.generation == 3  # Incremented, not reset


class TestTimeTravelScenarios:
    """Integration tests for time-travel scenarios."""

    def test_multiple_snapshots(self) -> None:
        """Can take multiple snapshots at different times."""
        sig = Signal.of(0)
        snap0 = sig.snapshot()

        sig.set(10)
        snap10 = sig.snapshot()

        sig.set(20)
        snap20 = sig.snapshot()

        sig.set(100)

        # Restore to different points
        sig.restore(snap10)
        assert sig.value == 10

        sig.restore(snap0)
        assert sig.value == 0

        sig.restore(snap20)
        assert sig.value == 20

    def test_snapshot_with_complex_value(self) -> None:
        """Snapshots work with complex values (lists, dicts)."""
        sig = Signal.of({"count": 0, "items": []})
        snap = sig.snapshot()

        sig.set({"count": 5, "items": ["a", "b"]})
        assert sig.value["count"] == 5

        sig.restore(snap)
        assert sig.value["count"] == 0
        assert sig.value["items"] == []

    def test_branching_exploration(self) -> None:
        """Simulate exploring two branches from same point."""
        sig = Signal.of(0)

        # Take checkpoint
        checkpoint = sig.snapshot()

        # Explore path A
        sig.set(1)
        sig.update(lambda x: x + 10)
        path_a_result = sig.value  # 11

        # Return to checkpoint, explore path B
        sig.restore(checkpoint)
        sig.set(2)
        sig.update(lambda x: x * 10)
        path_b_result = sig.value  # 20

        assert path_a_result == 11
        assert path_b_result == 20

    def test_snapshot_restore_with_subscriber(self) -> None:
        """Full scenario: subscriber sees all changes including restore."""
        sig = Signal.of(0)
        history: list[int] = []
        sig.subscribe(lambda v: history.append(v))

        sig.set(1)  # [1]
        snap = sig.snapshot()
        sig.set(2)  # [1, 2]
        sig.set(3)  # [1, 2, 3]
        sig.restore(snap)  # [1, 2, 3, 1]

        assert history == [1, 2, 3, 1]

    def test_snapshot_timestamp_ordering(self) -> None:
        """Later snapshots have later timestamps."""
        sig = Signal.of(0)
        snap1 = sig.snapshot()
        sig.set(1)
        snap2 = sig.snapshot()
        sig.set(2)
        snap3 = sig.snapshot()

        assert snap1.timestamp <= snap2.timestamp <= snap3.timestamp
