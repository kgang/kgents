"""
Checkpoint Storage: Persistence backend for rollback registry.

Provides abstraction for checkpoint persistence with a default
JSON-based file storage implementation.

Storage is designed to be:
- Human-readable (JSON format)
- Git-friendly (individual files per checkpoint)
- Append-only (forward history preserved even on rollback)
- Thread-safe (file locking for concurrent access)
"""

from __future__ import annotations

import fcntl
import json
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .checkpoint import Checkpoint, CheckpointId, CheckpointSummary

logger = logging.getLogger(__name__)


class CheckpointStorage(ABC):
    """
    Abstract interface for checkpoint persistence.

    Implementations can use different backends:
    - JSON files (default)
    - SQLite database
    - Git-backed storage
    """

    @abstractmethod
    def save(self, checkpoint: Checkpoint) -> None:
        """
        Save a checkpoint.

        Args:
            checkpoint: The checkpoint to persist
        """
        ...

    @abstractmethod
    def load(self, checkpoint_id: CheckpointId) -> Checkpoint | None:
        """
        Load a checkpoint by ID.

        Args:
            checkpoint_id: The checkpoint to load

        Returns:
            The checkpoint, or None if not found
        """
        ...

    @abstractmethod
    def list_summaries(self, limit: int = 20) -> list[CheckpointSummary]:
        """
        List checkpoint summaries, most recent first.

        Args:
            limit: Maximum number of summaries to return

        Returns:
            List of checkpoint summaries
        """
        ...

    @abstractmethod
    def exists(self, checkpoint_id: CheckpointId) -> bool:
        """Check if a checkpoint exists."""
        ...

    @abstractmethod
    def get_latest_id(self) -> CheckpointId | None:
        """Get the most recent checkpoint ID, or None if empty."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of checkpoints. More efficient than len(list_summaries())."""
        ...

    def prune(self, keep_count: int = 100) -> int:
        """
        Remove old checkpoints, keeping the most recent.

        Args:
            keep_count: Number of recent checkpoints to keep

        Returns:
            Number of checkpoints removed
        """
        # Default implementation does nothing (in-memory storage doesn't need pruning)
        return 0

    def iter_checkpoints(self) -> Iterator[Checkpoint]:
        """
        Iterate over all checkpoints, most recent first.

        Default implementation loads each checkpoint individually.
        Subclasses may override for efficiency.
        """
        for summary in self.list_summaries(limit=1000):
            checkpoint = self.load(summary.id)
            if checkpoint:
                yield checkpoint


class JSONCheckpointStorage(CheckpointStorage):
    """
    JSON file-based checkpoint storage.

    Stores each checkpoint as an individual JSON file for:
    - Human readability
    - Git-friendliness (easy diffs)
    - Append-only semantics
    - Thread-safe (file locking)

    Directory structure:
        storage_path/
            index.json          # Ordered list of checkpoint IDs
            index.lock          # Lock file for concurrent access
            checkpoints/
                abc123.json     # Individual checkpoint files
                def456.json
                ...
    """

    def __init__(self, storage_path: Path) -> None:
        """
        Initialize JSON storage.

        Args:
            storage_path: Directory to store checkpoints
        """
        self._storage_path = storage_path
        self._checkpoints_dir = storage_path / "checkpoints"
        self._index_path = storage_path / "index.json"
        self._lock_path = storage_path / "index.lock"

        # Ensure directories exist
        self._checkpoints_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _lock_index(self):
        """
        Acquire exclusive lock on index for thread-safe updates.

        Uses fcntl.flock for Unix file locking.
        """
        # Ensure lock file exists
        self._lock_path.touch(exist_ok=True)

        with open(self._lock_path, "w") as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def save(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to JSON file and update index (thread-safe)."""
        # Save checkpoint file (individual file, less contention)
        checkpoint_path = self._checkpoints_dir / f"{checkpoint.id}.json"
        checkpoint_path.write_text(
            json.dumps(checkpoint.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Update index with lock to prevent race conditions
        with self._lock_index():
            index = self._load_index()
            if checkpoint.id not in index:
                index.append(checkpoint.id)
            self._save_index(index)

        logger.info(f"Saved checkpoint {checkpoint.id}")

    def load(self, checkpoint_id: CheckpointId) -> Checkpoint | None:
        """Load checkpoint from JSON file."""
        checkpoint_path = self._checkpoints_dir / f"{checkpoint_id}.json"

        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
            return None

        try:
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            return Checkpoint.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None

    def list_summaries(self, limit: int = 20) -> list[CheckpointSummary]:
        """List checkpoint summaries from index, most recent first."""
        index = self._load_index()

        summaries = []
        # Iterate in reverse (most recent last in index)
        for checkpoint_id in reversed(index[-limit:]):
            checkpoint = self.load(CheckpointId(checkpoint_id))
            if checkpoint:
                summaries.append(checkpoint.summary())

        return summaries

    def exists(self, checkpoint_id: CheckpointId) -> bool:
        """Check if checkpoint file exists."""
        checkpoint_path = self._checkpoints_dir / f"{checkpoint_id}.json"
        return checkpoint_path.exists()

    def get_latest_id(self) -> CheckpointId | None:
        """Get the most recent checkpoint ID."""
        index = self._load_index()
        if not index:
            return None
        return CheckpointId(index[-1])

    def count(self) -> int:
        """Return total number of checkpoints."""
        return len(self._load_index())

    def prune(self, keep_count: int = 100) -> int:
        """
        Remove old checkpoints, keeping the most recent.

        Args:
            keep_count: Number of recent checkpoints to keep

        Returns:
            Number of checkpoints removed
        """
        with self._lock_index():
            index = self._load_index()
            if len(index) <= keep_count:
                return 0

            to_remove = index[:-keep_count]
            to_keep = index[-keep_count:]

            # Remove checkpoint files
            removed = 0
            for checkpoint_id in to_remove:
                checkpoint_path = self._checkpoints_dir / f"{checkpoint_id}.json"
                if checkpoint_path.exists():
                    try:
                        checkpoint_path.unlink()
                        removed += 1
                        logger.info(f"Pruned checkpoint: {checkpoint_id}")
                    except OSError as e:
                        logger.warning(f"Failed to remove {checkpoint_id}: {e}")

            # Update index
            self._save_index(to_keep)
            logger.info(f"Pruned {removed} checkpoints, keeping {len(to_keep)}")

            return removed

    def _load_index(self) -> list[str]:
        """Load checkpoint index from JSON."""
        if not self._index_path.exists():
            return []

        try:
            data = json.loads(self._index_path.read_text(encoding="utf-8"))
            return data.get("checkpoints", [])
        except json.JSONDecodeError:
            logger.error("Failed to load checkpoint index, starting fresh")
            return []

    def _save_index(self, index: list[str]) -> None:
        """Save checkpoint index to JSON."""
        self._index_path.write_text(
            json.dumps({"checkpoints": index}, indent=2),
            encoding="utf-8",
        )


class InMemoryCheckpointStorage(CheckpointStorage):
    """
    In-memory checkpoint storage for testing.

    Does not persist across sessions.
    """

    def __init__(self) -> None:
        self._checkpoints: dict[CheckpointId, Checkpoint] = {}
        self._order: list[CheckpointId] = []

    def save(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to memory."""
        self._checkpoints[checkpoint.id] = checkpoint
        if checkpoint.id not in self._order:
            self._order.append(checkpoint.id)

    def load(self, checkpoint_id: CheckpointId) -> Checkpoint | None:
        """Load checkpoint from memory."""
        return self._checkpoints.get(checkpoint_id)

    def list_summaries(self, limit: int = 20) -> list[CheckpointSummary]:
        """List summaries from memory."""
        summaries = []
        for checkpoint_id in reversed(self._order[-limit:]):
            checkpoint = self._checkpoints.get(checkpoint_id)
            if checkpoint:
                summaries.append(checkpoint.summary())
        return summaries

    def exists(self, checkpoint_id: CheckpointId) -> bool:
        """Check if checkpoint exists in memory."""
        return checkpoint_id in self._checkpoints

    def get_latest_id(self) -> CheckpointId | None:
        """Get most recent checkpoint ID."""
        return self._order[-1] if self._order else None

    def count(self) -> int:
        """Return total number of checkpoints."""
        return len(self._order)


__all__ = [
    "CheckpointStorage",
    "JSONCheckpointStorage",
    "InMemoryCheckpointStorage",
]
