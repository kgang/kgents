"""
CrystalStore: Append-Only Ledger for Crystals.

The store enforces the Crystal laws:
- Law 1 (Mark Immutability): Marks are never deleted—we only add crystals
- Law 2 (Provenance Chain): Every crystal references its sources
- Law 3 (Level Consistency): Level N crystals only source from level N-1

Pattern 7 from crown-jewel-patterns.md: Append-Only History
"History is a ledger. Modifications are new entries, not edits."

Philosophy:
    The CrystalStore is an append-only ledger. You can add crystals,
    but you cannot modify or delete them. This provides:
    - Complete audit trail of compression decisions
    - Provenance integrity (trace any insight to source marks)
    - Temporal zoom capability (L3 → L2 → L1 → L0 → Marks)

Persistence:
    JSONL format at ~/.local/share/kgents/witness/crystals.jsonl
    Each line is a complete Crystal JSON object.

See: spec/protocols/witness-crystallization.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from .crystal import Crystal, CrystalId, CrystalLevel, generate_crystal_id
from .mark import Mark, MarkId

logger = logging.getLogger("kgents.witness.crystal_store")


# =============================================================================
# Exceptions
# =============================================================================


class CrystalStoreError(Exception):
    """Base exception for crystal store errors."""

    pass


class DuplicateCrystalError(CrystalStoreError):
    """Raised when attempting to add a crystal with an existing ID."""

    def __init__(self, crystal_id: CrystalId):
        self.crystal_id = crystal_id
        super().__init__(f"Crystal with ID {crystal_id} already exists")


class CrystalNotFoundError(CrystalStoreError):
    """Raised when a referenced crystal is not found."""

    def __init__(self, crystal_id: CrystalId):
        self.crystal_id = crystal_id
        super().__init__(f"Crystal with ID {crystal_id} not found")


class LevelConsistencyError(CrystalStoreError):
    """Raised when source crystals are not from level N-1."""

    def __init__(self, crystal_level: CrystalLevel, source_level: CrystalLevel):
        self.crystal_level = crystal_level
        self.source_level = source_level
        super().__init__(
            f"Level {crystal_level.value} crystal cannot source from "
            f"level {source_level.value} (expected {crystal_level.value - 1})"
        )


# =============================================================================
# Query Types
# =============================================================================


@dataclass(frozen=True)
class CrystalQuery:
    """
    Query parameters for crystal retrieval.

    All parameters are optional. Multiple parameters combine with AND logic.
    """

    # Level filter
    level: CrystalLevel | None = None

    # Time range (on crystallized_at)
    after: datetime | None = None
    before: datetime | None = None

    # Session filter
    session_id: str | None = None

    # Topic filter (any match)
    topics: tuple[str, ...] | None = None

    # Confidence threshold
    min_confidence: float | None = None

    # Limit and offset for pagination
    limit: int | None = None
    offset: int = 0

    def matches(self, crystal: Crystal) -> bool:
        """Check if a crystal matches this query."""
        # Level filter
        if self.level is not None and crystal.level != self.level:
            return False

        # Time range (crystallized_at)
        if self.after and crystal.crystallized_at <= self.after:
            return False
        if self.before and crystal.crystallized_at >= self.before:
            return False

        # Session filter
        if self.session_id and crystal.session_id != self.session_id:
            return False

        # Topic filter (any match)
        if self.topics:
            if not any(topic in crystal.topics for topic in self.topics):
                return False

        # Confidence threshold
        if self.min_confidence is not None and crystal.confidence < self.min_confidence:
            return False

        return True


# =============================================================================
# CrystalStore: Append-Only Ledger
# =============================================================================


@dataclass
class CrystalStore:
    """
    Append-only ledger for Crystals.

    Enforces all Crystal laws:
    - Law 2: Provenance Chain (validate source references exist)
    - Law 3: Level Consistency (Level N sources only from Level N-1)

    The store maintains:
    - Primary index by ID
    - Secondary index by level (for hierarchy queries)
    - Timeline index (for recency queries)

    Example:
        >>> store = CrystalStore()
        >>> crystal = Crystal.from_crystallization(...)
        >>> store.append(crystal)
        >>> retrieved = store.get(crystal.id)
        >>> assert retrieved == crystal
        >>> session_crystals = store.by_level(CrystalLevel.SESSION)
    """

    # Primary storage: ID → Crystal
    _crystals: dict[CrystalId, Crystal] = field(default_factory=dict)

    # Level index: Level → list of IDs
    _by_level: dict[CrystalLevel, list[CrystalId]] = field(default_factory=dict)

    # Timeline: Ordered list of IDs by crystallized_at
    _timeline: list[CrystalId] = field(default_factory=list)

    # Persistence path (if any)
    _persistence_path: Path | None = None

    def __post_init__(self) -> None:
        """Initialize secondary indices."""
        # Ensure level index has all levels
        for level in CrystalLevel:
            if level not in self._by_level:
                self._by_level[level] = []

    # =========================================================================
    # Core Operations
    # =========================================================================

    def append(self, crystal: Crystal) -> None:
        """
        Append a Crystal to the ledger.

        Validates:
        - No duplicate IDs
        - Source crystal references exist (for level 1+)
        - Level consistency (sources are from level N-1)

        Raises:
            DuplicateCrystalError: If a crystal with this ID exists
            CrystalNotFoundError: If a source crystal doesn't exist
            LevelConsistencyError: If source crystals are wrong level
        """
        # Check for duplicate
        if crystal.id in self._crystals:
            raise DuplicateCrystalError(crystal.id)

        # Validate source crystals for level 1+
        if crystal.level != CrystalLevel.SESSION:
            expected_source_level = CrystalLevel(crystal.level.value - 1)
            for source_id in crystal.source_crystals:
                source = self.get(source_id)
                if source is None:
                    raise CrystalNotFoundError(source_id)
                if source.level != expected_source_level:
                    raise LevelConsistencyError(crystal.level, source.level)

        # Append to primary storage
        self._crystals[crystal.id] = crystal

        # Update level index
        self._by_level[crystal.level].append(crystal.id)

        # Update timeline (maintain sorted order by crystallized_at)
        self._timeline.append(crystal.id)

        logger.debug(
            f"Appended crystal {crystal.id}: level={crystal.level.name}, "
            f"sources={crystal.source_count}"
        )

    def get(self, crystal_id: CrystalId) -> Crystal | None:
        """Get a Crystal by ID."""
        return self._crystals.get(crystal_id)

    def get_or_raise(self, crystal_id: CrystalId) -> Crystal:
        """Get a Crystal by ID, raising if not found."""
        crystal = self.get(crystal_id)
        if crystal is None:
            raise CrystalNotFoundError(crystal_id)
        return crystal

    def by_level(self, level: CrystalLevel) -> list[Crystal]:
        """Get all crystals at a specific level."""
        ids = self._by_level.get(level, [])
        return [self._crystals[cid] for cid in ids if cid in self._crystals]

    def query(self, query: CrystalQuery) -> Iterator[Crystal]:
        """
        Query crystals matching the given criteria.

        Returns an iterator over matching crystals in chronological order.
        """
        count = 0
        skipped = 0

        for crystal_id in self._timeline:
            crystal = self._crystals[crystal_id]

            if not query.matches(crystal):
                continue

            # Handle offset
            if skipped < query.offset:
                skipped += 1
                continue

            # Handle limit
            if query.limit and count >= query.limit:
                return

            yield crystal
            count += 1

    def count(self, query: CrystalQuery | None = None) -> int:
        """Count crystals matching the query (or all if no query)."""
        if query is None:
            return len(self._crystals)
        return sum(1 for _ in self.query(query))

    def all(self) -> Iterator[Crystal]:
        """Iterate over all crystals in chronological order."""
        for crystal_id in self._timeline:
            yield self._crystals[crystal_id]

    def recent(self, limit: int = 10, level: CrystalLevel | None = None) -> list[Crystal]:
        """Get the most recent crystals, optionally filtered by level."""
        if level is not None:
            level_ids = self._by_level.get(level, [])
            return [self._crystals[cid] for cid in level_ids[-limit:]]
        return [self._crystals[cid] for cid in self._timeline[-limit:]]

    # =========================================================================
    # Provenance Navigation (Temporal Zoom)
    # =========================================================================

    def expand(self, crystal_id: CrystalId) -> list[Crystal | MarkId]:
        """
        Expand a crystal to its sources.

        For level 0: Returns list of MarkIds (the original marks)
        For level 1+: Returns list of source Crystals

        This enables "temporal zoom" - drilling down from epoch to raw marks.
        """
        crystal = self.get_or_raise(crystal_id)

        if crystal.level == CrystalLevel.SESSION:
            # Return mark IDs (caller can look them up in MarkStore)
            return list(crystal.source_marks)
        else:
            # Return source crystals
            return [self.get_or_raise(source_id) for source_id in crystal.source_crystals]

    def expand_to_marks(self, crystal_id: CrystalId) -> list[MarkId]:
        """
        Recursively expand a crystal all the way down to source marks.

        Traverses the entire provenance chain from any level to the original marks.
        """
        crystal = self.get_or_raise(crystal_id)

        if crystal.level == CrystalLevel.SESSION:
            return list(crystal.source_marks)

        # Recursively expand source crystals
        all_marks: list[MarkId] = []
        for source_id in crystal.source_crystals:
            all_marks.extend(self.expand_to_marks(source_id))
        return all_marks

    def get_hierarchy(self, crystal_id: CrystalId) -> dict[str, Any]:
        """
        Get the full hierarchy for a crystal (for visualization).

        Returns a tree structure showing the compression hierarchy.
        """
        crystal = self.get_or_raise(crystal_id)

        result: dict[str, Any] = {
            "id": str(crystal.id),
            "level": crystal.level.name,
            "insight": crystal.insight[:100] + "..."
            if len(crystal.insight) > 100
            else crystal.insight,
            "confidence": crystal.confidence,
            "children": [],
        }

        if crystal.level == CrystalLevel.SESSION:
            # Terminal level - show mark count
            result["mark_count"] = len(crystal.source_marks)
        else:
            # Recursive expansion
            for source_id in crystal.source_crystals:
                try:
                    child = self.get_hierarchy(source_id)
                    result["children"].append(child)
                except CrystalNotFoundError:
                    result["children"].append(
                        {
                            "id": str(source_id),
                            "error": "not found",
                        }
                    )

        return result

    # =========================================================================
    # Uncrystallized Detection
    # =========================================================================

    def get_uncrystallized_crystals(
        self,
        level: CrystalLevel,
        since: datetime | None = None,
    ) -> list[Crystal]:
        """
        Find crystals at level N-1 that haven't been crystallized into level N yet.

        Used by auto_crystallize to find what needs compression.
        """
        if level == CrystalLevel.SESSION:
            raise ValueError("Use marks for SESSION level, not crystals")

        source_level = CrystalLevel(level.value - 1)
        source_crystals = self.by_level(source_level)

        # Filter by time if specified
        if since:
            source_crystals = [c for c in source_crystals if c.crystallized_at >= since]

        # Find which source crystals are already included in a higher-level crystal
        used_sources: set[CrystalId] = set()
        for crystal in self.by_level(level):
            used_sources.update(crystal.source_crystals)

        # Return unused source crystals
        return [c for c in source_crystals if c.id not in used_sources]

    # =========================================================================
    # Persistence
    # =========================================================================

    def save(self, path: Path | str) -> None:
        """Save the store to a JSONL file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w") as f:
            for crystal in self.all():
                f.write(json.dumps(crystal.to_dict(), default=str) + "\n")

        self._persistence_path = path
        logger.info(f"Saved {len(self._crystals)} crystals to {path}")

    @classmethod
    def load(cls, path: Path | str) -> CrystalStore:
        """Load a store from a JSONL file."""
        path = Path(path)

        if not path.exists():
            logger.info(f"No crystal store at {path}, creating new")
            store = cls()
            store._persistence_path = path
            return store

        store = cls()
        store._persistence_path = path

        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    crystal = Crystal.from_dict(data)
                    # Direct append without validation (trusted data)
                    store._crystals[crystal.id] = crystal
                    store._by_level[crystal.level].append(crystal.id)
                    store._timeline.append(crystal.id)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Skipping malformed crystal line: {e}")

        logger.info(f"Loaded {len(store._crystals)} crystals from {path}")
        return store

    def sync(self) -> None:
        """Sync to persistence path if set."""
        if self._persistence_path:
            self.save(self._persistence_path)

    # =========================================================================
    # Statistics
    # =========================================================================

    def stats(self) -> dict[str, Any]:
        """Get store statistics."""
        level_counts = {level.name: len(ids) for level, ids in self._by_level.items()}

        # Calculate total compression ratio
        total_marks = sum(len(c.source_marks) for c in self.by_level(CrystalLevel.SESSION))

        # Average confidence by level
        confidence_by_level = {}
        for level in CrystalLevel:
            crystals = self.by_level(level)
            if crystals:
                avg_conf = sum(c.confidence for c in crystals) / len(crystals)
                confidence_by_level[level.name] = round(avg_conf, 2)

        return {
            "total_crystals": len(self._crystals),
            "by_level": level_counts,
            "total_source_marks": total_marks,
            "avg_confidence_by_level": confidence_by_level,
        }

    def __len__(self) -> int:
        """Return the number of crystals in the store."""
        return len(self._crystals)

    def __contains__(self, crystal_id: CrystalId) -> bool:
        """Check if a crystal ID exists in the store."""
        return crystal_id in self._crystals


# =============================================================================
# Global Store Factory
# =============================================================================

_global_store: CrystalStore | None = None


def get_crystal_store() -> CrystalStore:
    """Get the global crystal store (singleton)."""
    global _global_store
    if _global_store is None:
        # Default persistence path
        from pathlib import Path

        default_path = Path.home() / ".local" / "share" / "kgents" / "witness" / "crystals.jsonl"
        _global_store = CrystalStore.load(default_path)
    return _global_store


def set_crystal_store(store: CrystalStore) -> None:
    """Set the global crystal store (for testing)."""
    global _global_store
    _global_store = store


def reset_crystal_store() -> None:
    """Reset the global crystal store (for testing)."""
    global _global_store
    _global_store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Exceptions
    "CrystalStoreError",
    "DuplicateCrystalError",
    "CrystalNotFoundError",
    "LevelConsistencyError",
    # Query
    "CrystalQuery",
    # Store
    "CrystalStore",
    # Global factory
    "get_crystal_store",
    "set_crystal_store",
    "reset_crystal_store",
]
