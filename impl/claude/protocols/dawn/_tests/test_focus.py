"""Tests for Dawn Cockpit focus management."""

from datetime import datetime, timedelta

import pytest

from protocols.dawn.focus import Bucket, FocusItem, FocusManager


class TestBucket:
    """Tests for Bucket enum."""

    def test_staleness_thresholds(self) -> None:
        """Each bucket has appropriate staleness threshold."""
        assert Bucket.TODAY.staleness_threshold == timedelta(hours=36)
        assert Bucket.WEEK.staleness_threshold == timedelta(days=7)
        assert Bucket.SOMEDAY.staleness_threshold is None

    def test_demote_today_to_week(self) -> None:
        """Demote TODAY moves to WEEK."""
        assert Bucket.TODAY.demote() == Bucket.WEEK

    def test_demote_week_to_someday(self) -> None:
        """Demote WEEK moves to SOMEDAY."""
        assert Bucket.WEEK.demote() == Bucket.SOMEDAY

    def test_demote_someday_stays_someday(self) -> None:
        """Demote SOMEDAY stays at SOMEDAY (floor)."""
        assert Bucket.SOMEDAY.demote() == Bucket.SOMEDAY

    def test_promote_someday_to_week(self) -> None:
        """Promote SOMEDAY moves to WEEK."""
        assert Bucket.SOMEDAY.promote() == Bucket.WEEK

    def test_promote_week_to_today(self) -> None:
        """Promote WEEK moves to TODAY."""
        assert Bucket.WEEK.promote() == Bucket.TODAY

    def test_promote_today_stays_today(self) -> None:
        """Promote TODAY stays at TODAY (ceiling)."""
        assert Bucket.TODAY.promote() == Bucket.TODAY


class TestFocusItem:
    """Tests for FocusItem dataclass."""

    def test_staleness_today_fresh(self) -> None:
        """Fresh TODAY item is not stale."""
        now = datetime.now()
        item = FocusItem(
            id="test1",
            label="Test",
            target="path/to/file",
            bucket=Bucket.TODAY,
            added_at=now,
            last_touched=now,
        )
        assert not item.is_stale

    def test_staleness_today_stale(self) -> None:
        """TODAY items are stale after 36 hours."""
        now = datetime.now()
        item = FocusItem(
            id="test2",
            label="Test",
            target="path/to/file",
            bucket=Bucket.TODAY,
            added_at=now - timedelta(hours=40),
            last_touched=now - timedelta(hours=40),
        )
        assert item.is_stale

    def test_staleness_week_fresh(self) -> None:
        """WEEK items within 7 days are not stale."""
        now = datetime.now()
        item = FocusItem(
            id="test1",
            label="Test",
            target="path/to/file",
            bucket=Bucket.WEEK,
            added_at=now - timedelta(days=5),
            last_touched=now - timedelta(days=5),
        )
        assert not item.is_stale

    def test_staleness_week_stale(self) -> None:
        """WEEK items are stale after 7 days."""
        now = datetime.now()
        item = FocusItem(
            id="test2",
            label="Test",
            target="path/to/file",
            bucket=Bucket.WEEK,
            added_at=now - timedelta(days=10),
            last_touched=now - timedelta(days=10),
        )
        assert item.is_stale

    def test_staleness_someday_never(self) -> None:
        """SOMEDAY items are never stale."""
        now = datetime.now()
        item = FocusItem(
            id="test",
            label="Test",
            target="path/to/file",
            bucket=Bucket.SOMEDAY,
            added_at=now - timedelta(days=365),
            last_touched=now - timedelta(days=365),
        )
        assert not item.is_stale

    def test_touch_updates_last_touched(self) -> None:
        """Touch returns new item with updated timestamp."""
        old_time = datetime.now() - timedelta(hours=2)
        item = FocusItem(
            id="test",
            label="Test",
            target="path",
            bucket=Bucket.TODAY,
            added_at=old_time,
            last_touched=old_time,
        )
        touched = item.touch()
        assert touched.last_touched > item.last_touched
        assert touched.id == item.id  # Same identity

    def test_touch_preserves_identity(self) -> None:
        """Touch preserves all fields except last_touched."""
        item = FocusItem(
            id="test",
            label="Test Label",
            target="path/to/file",
            bucket=Bucket.WEEK,
            added_at=datetime.now(),
            last_touched=datetime.now() - timedelta(hours=1),
        )
        touched = item.touch()
        assert touched.id == item.id
        assert touched.label == item.label
        assert touched.target == item.target
        assert touched.bucket == item.bucket
        assert touched.added_at == item.added_at

    def test_promote_changes_bucket(self) -> None:
        """Promote returns item in higher bucket."""
        item = FocusItem(
            id="test",
            label="Test",
            target="path",
            bucket=Bucket.WEEK,
            added_at=datetime.now(),
            last_touched=datetime.now(),
        )
        promoted = item.promote()
        assert promoted.bucket == Bucket.TODAY

    def test_demote_changes_bucket(self) -> None:
        """Demote returns item in lower bucket."""
        item = FocusItem(
            id="test",
            label="Test",
            target="path",
            bucket=Bucket.TODAY,
            added_at=datetime.now(),
            last_touched=datetime.now(),
        )
        demoted = item.demote()
        assert demoted.bucket == Bucket.WEEK

    def test_to_dict_has_all_fields(self) -> None:
        """to_dict includes all expected fields."""
        item = FocusItem(
            id="test",
            label="Test",
            target="path/to/file",
            bucket=Bucket.TODAY,
            added_at=datetime.now(),
            last_touched=datetime.now(),
        )
        data = item.to_dict()
        assert "id" in data
        assert "label" in data
        assert "target" in data
        assert "bucket" in data
        assert "added_at" in data
        assert "last_touched" in data
        assert "is_stale" in data

    def test_to_dict_roundtrip(self) -> None:
        """Item can be serialized and deserialized."""
        item = FocusItem(
            id="test",
            label="Test",
            target="path/to/file",
            bucket=Bucket.TODAY,
            added_at=datetime.now(),
            last_touched=datetime.now(),
        )
        data = item.to_dict()
        restored = FocusItem.from_dict(data)
        assert restored.id == item.id
        assert restored.label == item.label
        assert restored.bucket == item.bucket


class TestFocusManager:
    """Tests for FocusManager."""

    def test_add_creates_item(self) -> None:
        """Add creates a new focus item."""
        manager = FocusManager()
        item = manager.add("path/to/file.md", label="My File")
        assert item.label == "My File"
        assert item.target == "path/to/file.md"
        assert item.bucket == Bucket.TODAY  # Default

    def test_add_infers_label_from_path(self) -> None:
        """Add infers label from target if not provided."""
        manager = FocusManager()
        item = manager.add("path/to/important-file.md")
        assert item.label == "important-file.md"

    def test_add_to_specific_bucket(self) -> None:
        """Add can target a specific bucket."""
        manager = FocusManager()
        item = manager.add("file.md", bucket=Bucket.WEEK)
        assert item.bucket == Bucket.WEEK

    def test_list_all(self) -> None:
        """List returns all items."""
        manager = FocusManager()
        manager.add("file1.md")
        manager.add("file2.md")
        manager.add("file3.md")
        assert len(manager.list()) == 3

    def test_list_by_bucket(self) -> None:
        """List can filter by bucket."""
        manager = FocusManager()
        manager.add("today.md", bucket=Bucket.TODAY)
        manager.add("week.md", bucket=Bucket.WEEK)
        manager.add("someday.md", bucket=Bucket.SOMEDAY)

        assert len(manager.list(bucket=Bucket.TODAY)) == 1
        assert len(manager.list(bucket=Bucket.WEEK)) == 1
        assert len(manager.list(bucket=Bucket.SOMEDAY)) == 1

    def test_get_by_id(self) -> None:
        """Get returns item by ID."""
        manager = FocusManager()
        item = manager.add("file.md")
        retrieved = manager.get(item.id)
        assert retrieved is not None
        assert retrieved.id == item.id

    def test_get_nonexistent_returns_none(self) -> None:
        """Get returns None for nonexistent ID."""
        manager = FocusManager()
        assert manager.get("nonexistent") is None

    def test_remove(self) -> None:
        """Remove deletes item by ID."""
        manager = FocusManager()
        item = manager.add("file.md")
        assert manager.remove(item.id)
        assert manager.get(item.id) is None

    def test_remove_nonexistent_returns_false(self) -> None:
        """Remove returns False for nonexistent ID."""
        manager = FocusManager()
        assert not manager.remove("nonexistent")

    def test_touch_via_manager(self) -> None:
        """Manager can touch items."""
        manager = FocusManager()
        item = manager.add("file.md")
        original_touched = item.last_touched

        # Small delay to ensure time difference
        import time

        time.sleep(0.01)

        touched = manager.touch(item.id)
        assert touched is not None
        assert touched.last_touched > original_touched

    def test_promote_via_manager(self) -> None:
        """Manager can promote items."""
        manager = FocusManager()
        item = manager.add("file.md", bucket=Bucket.WEEK)
        promoted = manager.promote(item.id)
        assert promoted is not None
        assert promoted.bucket == Bucket.TODAY

    def test_demote_via_manager(self) -> None:
        """Manager can demote items."""
        manager = FocusManager()
        item = manager.add("file.md", bucket=Bucket.TODAY)
        demoted = manager.demote(item.id)
        assert demoted is not None
        assert demoted.bucket == Bucket.WEEK

    def test_get_stale_empty_when_fresh(self) -> None:
        """get_stale returns empty when all items are fresh."""
        manager = FocusManager()
        manager.add("fresh.md")
        assert len(manager.get_stale()) == 0

    def test_len(self) -> None:
        """len returns total item count."""
        manager = FocusManager()
        assert len(manager) == 0
        manager.add("file1.md")
        assert len(manager) == 1
        manager.add("file2.md")
        assert len(manager) == 2

    def test_clear(self) -> None:
        """Clear removes all items."""
        manager = FocusManager()
        manager.add("file1.md")
        manager.add("file2.md")
        manager.clear()
        assert len(manager) == 0
