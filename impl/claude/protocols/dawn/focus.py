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

Teaching:
    gotcha: Focus items are persisted to XDG_DATA_HOME/kgents/dawn/focus.json.
            Call save() after mutations, or use auto_persist=True (default).
            (Evidence: spec/protocols/dawn-cockpit.md § Focus Management)

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from builtins import list as List  # Avoid shadowing in FocusManager.list()
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


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


def _get_focus_path() -> Path:
    """Get the path for focus persistence file."""
    xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
    focus_dir = Path(xdg_data) / "kgents" / "dawn"
    focus_dir.mkdir(parents=True, exist_ok=True)
    return focus_dir / "focus.json"


class FocusManager:
    """
    Manages focus items across buckets with optional persistence.

    Focus items are persisted to ~/.local/share/kgents/dawn/focus.json.

    Usage:
        manager = FocusManager()
        manager.load()               # Load existing items from disk
        item = manager.add("path/to/file.md", label="My Focus")
        manager.promote(item.id)     # Mutations auto-persist
        stale = manager.get_stale()

    Teaching:
        gotcha: With auto_persist=True (default), mutations automatically save.
                For batch operations, use auto_persist=False and call save() once.
                (Evidence: spec/protocols/dawn-cockpit.md § Focus Management)
    """

    def __init__(self, auto_persist: bool = True) -> None:
        """
        Initialize focus manager.

        Args:
            auto_persist: If True, automatically save after add/remove/touch/promote/demote.
        """
        self._items: dict[str, FocusItem] = {}
        self._auto_persist = auto_persist

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
        if self._auto_persist:
            self.save()
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
            if self._auto_persist:
                self.save()
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
        if self._auto_persist:
            self.save()
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
        if self._auto_persist:
            self.save()
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
        if self._auto_persist:
            self.save()
        return demoted

    def get_stale(self) -> List[FocusItem]:
        """Get all stale items (for hygiene checking)."""
        return [i for i in self._items.values() if i.is_stale]

    def clear(self) -> None:
        """Clear all items (for testing)."""
        self._items.clear()
        if self._auto_persist:
            self.save()

    def __len__(self) -> int:
        """Return total number of items."""
        return len(self._items)

    # === Persistence ===

    def save(self) -> None:
        """Save focus items to disk."""
        path = _get_focus_path()
        data = [item.to_dict() for item in self._items.values()]
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(data)} focus items to {path}")
        except Exception as e:
            logger.error(f"Failed to save focus items: {e}")

    def load(self) -> None:
        """Load focus items from disk."""
        path = _get_focus_path()
        if not path.exists():
            logger.debug(f"No focus file at {path}")
            return

        try:
            with open(path) as f:
                data = json.load(f)

            for item_data in data:
                item = FocusItem.from_dict(item_data)
                self._items[item.id] = item

            logger.debug(f"Loaded {len(data)} focus items from {path}")
        except Exception as e:
            logger.error(f"Failed to load focus items: {e}")


__all__ = [
    "Bucket",
    "FocusItem",
    "FocusManager",
]
