"""
Dawn Cockpit Focus Management.

Manages focus items across three buckets (TODAY, WEEK, SOMEDAY) with
bucket-dependent staleness detection.

Core Insight: Staleness is bucket-dependent, not wall-clock.
- TODAY items are stale after 36 hours
- WEEK items are stale after 7 days
- SOMEDAY items are never stale

All types are frozen dataclasses for immutability. Operations like
touch/promote/demote return new instances.

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

import uuid
from builtins import list as List  # Avoid shadowing in FocusManager.list()
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class Bucket(Enum):
    """
    Focus item buckets with cadence semantics.

    Each bucket has a different staleness threshold and item count target:
    - TODAY: 1-3 items, stale after 36 hours
    - WEEK: 3-7 items, stale after 7 days
    - SOMEDAY: Unbounded, never stale
    """

    TODAY = "today"
    WEEK = "week"
    SOMEDAY = "someday"

    @property
    def staleness_threshold(self) -> timedelta | None:
        """Return staleness threshold for this bucket (None = never stale)."""
        return {
            Bucket.TODAY: timedelta(hours=36),
            Bucket.WEEK: timedelta(days=7),
            Bucket.SOMEDAY: None,
        }[self]

    def demote(self) -> Bucket:
        """Return the bucket one level down (toward SOMEDAY)."""
        return {
            Bucket.TODAY: Bucket.WEEK,
            Bucket.WEEK: Bucket.SOMEDAY,
            Bucket.SOMEDAY: Bucket.SOMEDAY,  # Floor
        }[self]

    def promote(self) -> Bucket:
        """Return the bucket one level up (toward TODAY)."""
        return {
            Bucket.TODAY: Bucket.TODAY,  # Ceiling
            Bucket.WEEK: Bucket.TODAY,
            Bucket.SOMEDAY: Bucket.WEEK,
        }[self]


@dataclass(frozen=True)
class FocusItem:
    """
    A reference to work that deserves attention.

    FocusItems are immutable. Operations like touch(), promote(), demote()
    return new instances with updated values.

    Attributes:
        id: Unique identifier (8-char UUID prefix)
        label: Human-readable label
        target: AGENTESE path OR file path
        bucket: Which bucket this item lives in
        added_at: When the item was created
        last_touched: When the item was last interacted with
    """

    id: str
    label: str
    target: str
    bucket: Bucket
    added_at: datetime
    last_touched: datetime

    @property
    def is_stale(self) -> bool:
        """
        Check if item is stale based on bucket cadence.

        Staleness is determined by last_touched, not added_at:
        - TODAY: stale if last_touched > 36 hours ago
        - WEEK: stale if last_touched > 7 days ago
        - SOMEDAY: never stale
        """
        threshold = self.bucket.staleness_threshold
        if threshold is None:
            return False
        age = datetime.now() - self.last_touched
        return age > threshold

    def touch(self) -> FocusItem:
        """Return new item with updated last_touched timestamp."""
        return FocusItem(
            id=self.id,
            label=self.label,
            target=self.target,
            bucket=self.bucket,
            added_at=self.added_at,
            last_touched=datetime.now(),
        )

    def promote(self) -> FocusItem:
        """Return new item in promoted bucket (toward TODAY)."""
        return FocusItem(
            id=self.id,
            label=self.label,
            target=self.target,
            bucket=self.bucket.promote(),
            added_at=self.added_at,
            last_touched=datetime.now(),
        )

    def demote(self) -> FocusItem:
        """Return new item in demoted bucket (toward SOMEDAY)."""
        return FocusItem(
            id=self.id,
            label=self.label,
            target=self.target,
            bucket=self.bucket.demote(),
            added_at=self.added_at,
            last_touched=datetime.now(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "label": self.label,
            "target": self.target,
            "bucket": self.bucket.value,
            "added_at": self.added_at.isoformat(),
            "last_touched": self.last_touched.isoformat(),
            "is_stale": self.is_stale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FocusItem:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            label=data["label"],
            target=data["target"],
            bucket=Bucket(data["bucket"]),
            added_at=datetime.fromisoformat(data["added_at"]),
            last_touched=datetime.fromisoformat(data["last_touched"]),
        )


class FocusManager:
    """
    Manages focus items across buckets.

    This is an in-memory manager. Phase 2 adds persistence via D-gent.

    Usage:
        manager = FocusManager()
        item = manager.add("path/to/file.md", label="My Focus")
        manager.promote(item.id)
        stale = manager.get_stale()
    """

    def __init__(self) -> None:
        """Initialize empty focus manager."""
        self._items: dict[str, FocusItem] = {}

    def list(self, bucket: Bucket | None = None) -> List[FocusItem]:
        """
        List focus items, optionally filtered by bucket.

        Returns items sorted by added_at descending (newest first).
        """
        items = list(self._items.values())
        if bucket is not None:
            items = [i for i in items if i.bucket == bucket]
        return sorted(items, key=lambda i: i.added_at, reverse=True)

    def add(
        self,
        target: str,
        label: str | None = None,
        bucket: Bucket = Bucket.TODAY,
    ) -> FocusItem:
        """
        Add a new focus item.

        Args:
            target: AGENTESE path or file path
            label: Human-readable label (inferred from target if not provided)
            bucket: Which bucket to add to (default: TODAY)

        Returns:
            The created FocusItem
        """
        now = datetime.now()
        item = FocusItem(
            id=str(uuid.uuid4())[:8],
            label=label or target.split("/")[-1],
            target=target,
            bucket=bucket,
            added_at=now,
            last_touched=now,
        )
        self._items[item.id] = item
        return item

    def get(self, item_id: str) -> FocusItem | None:
        """Get a focus item by ID."""
        return self._items.get(item_id)

    def remove(self, item_id: str) -> bool:
        """
        Remove a focus item.

        Returns True if item was removed, False if not found.
        """
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def touch(self, item_id: str) -> FocusItem | None:
        """
        Touch a focus item (update last_touched).

        Returns the updated item, or None if not found.
        """
        item = self._items.get(item_id)
        if item is None:
            return None
        touched = item.touch()
        self._items[item_id] = touched
        return touched

    def promote(self, item_id: str) -> FocusItem | None:
        """
        Promote a focus item to higher bucket.

        Returns the promoted item, or None if not found.
        """
        item = self._items.get(item_id)
        if item is None:
            return None
        promoted = item.promote()
        self._items[item_id] = promoted
        return promoted

    def demote(self, item_id: str) -> FocusItem | None:
        """
        Demote a focus item to lower bucket.

        Returns the demoted item, or None if not found.
        """
        item = self._items.get(item_id)
        if item is None:
            return None
        demoted = item.demote()
        self._items[item_id] = demoted
        return demoted

    def get_stale(self) -> List[FocusItem]:
        """Get all stale items (for hygiene checking)."""
        return [i for i in self._items.values() if i.is_stale]

    def clear(self) -> None:
        """Clear all items (for testing)."""
        self._items.clear()

    def __len__(self) -> int:
        """Return total number of items."""
        return len(self._items)


__all__ = [
    "Bucket",
    "FocusItem",
    "FocusManager",
]
