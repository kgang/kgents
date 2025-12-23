"""
Cosmos: The append-only shared reality.

The cosmos is NOT a mutable filesystem. It is an append-only log
of committed states. Every save appends a new version. 'Current'
cosmos is a pointer to the latest version.

Philosophy:
    "The cosmos never overwrites. Every save appends.
     The past is immutable. The future is uncommitted."
    "The proof IS the decision. The mark IS the witness."

Integration with Witness (Phase 2):
    Every commit can carry a MarkId linking to the full witness trace.
    This enables:
    - Audit trail: Who changed what, when, and WHY
    - Replay: Reconstruct editing sessions from marks
    - Blame: Trace any content to its justification

See: spec/protocols/k-block.md
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, NewType

if TYPE_CHECKING:
    from services.witness import MarkId

    from .kblock import KBlock, KBlockId

# -----------------------------------------------------------------------------
# Type Aliases
# -----------------------------------------------------------------------------

VersionId = NewType("VersionId", str)


def generate_version_id() -> VersionId:
    """Generate a unique version identifier."""
    return VersionId(f"v_{uuid.uuid4().hex[:12]}")


# -----------------------------------------------------------------------------
# Blame Entry (Phase 2: Witness-Enabled History)
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class BlameEntry:
    """
    A single entry in the blame trace.

    Combines cosmos version info with witness context for
    "git blame meets Witness" functionality.

    The mark_id links to the full Witness trace where you can find:
    - Toulmin proof (data → warrant → claim)
    - Causal links to other marks
    - Umwelt snapshot (what the actor could perceive)
    """

    version_id: VersionId
    actor: str
    reasoning: str | None
    mark_id: str | None
    timestamp: datetime
    summary: str  # First line of change for quick preview

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API responses."""
        return {
            "version_id": self.version_id,
            "actor": self.actor,
            "reasoning": self.reasoning,
            "mark_id": self.mark_id,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
        }


# -----------------------------------------------------------------------------
# Cosmos Entry
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CosmosEntry:
    """
    A single entry in the append-only cosmos log.

    Each entry represents a committed state of content at a path.
    Entries are immutable once created.

    Phase 2 Enhancement:
        mark_id links to the Witness system, enabling full traceability.
        The mark contains Toulmin proof structure (data → warrant → claim)
        explaining WHY this change was made.
    """

    version_id: VersionId
    path: str
    content: str
    content_hash: str
    parent_version: VersionId | None  # Previous version of this path
    timestamp: datetime
    actor: str  # "Kent", "Claude", "system"
    reasoning: str | None = None  # Why this change was made
    mark_id: str | None = None  # MarkId linking to Witness trace (Phase 2)

    @classmethod
    def create(
        cls,
        path: str,
        content: str,
        parent_version: VersionId | None,
        actor: str = "system",
        reasoning: str | None = None,
        mark_id: str | None = None,
    ) -> "CosmosEntry":
        """Create a new cosmos entry."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(
            version_id=generate_version_id(),
            path=path,
            content=content,
            content_hash=content_hash,
            parent_version=parent_version,
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            reasoning=reasoning,
            mark_id=mark_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "version_id": self.version_id,
            "path": self.path,
            "content": self.content,
            "content_hash": self.content_hash,
            "parent_version": self.parent_version,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "reasoning": self.reasoning,
            "mark_id": self.mark_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CosmosEntry":
        """Deserialize from persistence."""
        return cls(
            version_id=VersionId(data["version_id"]),
            path=data["path"],
            content=data["content"],
            content_hash=data["content_hash"],
            parent_version=VersionId(data["parent_version"])
            if data.get("parent_version")
            else None,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            actor=data["actor"],
            reasoning=data.get("reasoning"),
            mark_id=data.get("mark_id"),
        )


# -----------------------------------------------------------------------------
# Append-Only Log
# -----------------------------------------------------------------------------


@dataclass
class AppendOnlyLog:
    """
    In-memory append-only log of cosmos entries.

    This is the Phase 0 implementation. Persistence to disk
    will be added in Phase 2.
    """

    entries: list[CosmosEntry] = field(default_factory=list)
    _by_version: dict[VersionId, CosmosEntry] = field(default_factory=dict)

    def append(self, entry: CosmosEntry) -> VersionId:
        """Append an entry to the log. Returns version ID."""
        self.entries.append(entry)
        self._by_version[entry.version_id] = entry
        return entry.version_id

    def get(self, version_id: VersionId) -> CosmosEntry | None:
        """Get entry by version ID."""
        return self._by_version.get(version_id)

    def walk_back(self, path: str, from_version: VersionId | None) -> list[CosmosEntry]:
        """
        Walk backwards through history for a path.

        Returns all versions of the path from most recent to oldest.
        """
        if from_version is None:
            return []

        result = []
        current = self.get(from_version)

        while current is not None:
            if current.path == path:
                result.append(current)
            current = self.get(current.parent_version) if current.parent_version else None

        return result

    def latest_for_path(self, path: str) -> CosmosEntry | None:
        """Get most recent entry for a path."""
        # Walk backwards through all entries (inefficient, but correct for Phase 0)
        for entry in reversed(self.entries):
            if entry.path == path:
                return entry
        return None

    def __len__(self) -> int:
        return len(self.entries)


# -----------------------------------------------------------------------------
# Semantic Index
# -----------------------------------------------------------------------------


@dataclass
class SemanticIndex:
    """
    Index for fast path -> latest version lookup.

    Separate from the log to allow efficient queries.
    """

    _path_to_latest: dict[str, VersionId] = field(default_factory=dict)
    _path_to_versions: dict[str, list[VersionId]] = field(default_factory=dict)

    def update(self, path: str, version_id: VersionId) -> None:
        """Update index after a commit."""
        self._path_to_latest[path] = version_id
        if path not in self._path_to_versions:
            self._path_to_versions[path] = []
        self._path_to_versions[path].append(version_id)

    def get_latest(self, path: str) -> VersionId | None:
        """Get latest version ID for path."""
        return self._path_to_latest.get(path)

    def get_versions(self, path: str) -> list[VersionId]:
        """Get all version IDs for path (oldest to newest)."""
        return self._path_to_versions.get(path, [])

    def all_paths(self) -> list[str]:
        """Get all known paths."""
        return list(self._path_to_latest.keys())


# -----------------------------------------------------------------------------
# Cosmos
# -----------------------------------------------------------------------------


@dataclass
class Cosmos:
    """
    The shared reality — an append-only log of committed content.

    Key insight: The cosmos never overwrites. Every 'save' appends a new
    version. 'Current' cosmos is a pointer to the latest version.

    This enables:
    - Perfect time travel (any version is accessible)
    - Branching (fork from any point)
    - Audit trail (every change is traceable)
    """

    log: AppendOnlyLog = field(default_factory=AppendOnlyLog)
    index: SemanticIndex = field(default_factory=SemanticIndex)

    # Active K-Blocks referencing this cosmos
    active_blocks: dict[str, "KBlockId"] = field(default_factory=dict)  # path -> KBlockId

    # Dependency graph (which paths reference which)
    dependents: dict[str, set[str]] = field(default_factory=dict)  # path -> paths that reference it

    # ---------------------------------------------------------------------
    # Read Operations
    # ---------------------------------------------------------------------

    async def read(self, path: str, version: VersionId | None = None) -> str | None:
        """
        Read content at version (default: latest).

        If the path doesn't exist in the cosmos log yet, falls back to
        reading from the filesystem. This allows K-Blocks to be created
        for files that haven't been edited through the cosmos yet.

        Returns None if path doesn't exist anywhere.
        """
        if version is not None:
            entry = self.log.get(version)
            return entry.content if entry and entry.path == path else None

        # Get latest version from cosmos log
        latest = self.index.get_latest(path)
        if latest is not None:
            entry = self.log.get(latest)
            return entry.content if entry else None

        # Fallback: read from SovereignStore (ingested copies)
        # NOTE: We no longer fall back to filesystem! Content must be explicitly
        # ingested into the sovereign store. This enforces inbound sovereignty.
        try:
            from services.providers import get_sovereign_store

            store = await get_sovereign_store()
            entity = await store.get_current(path)
            if entity is not None:
                # SovereignEntity stores content as bytes, decode to str
                return (
                    entity.content.decode("utf-8")
                    if isinstance(entity.content, bytes)
                    else entity.content
                )
        except Exception:
            pass  # SovereignStore not available or path not found

        # Return None if not in cosmos OR sovereign store
        # Frontend should show "not ingested" UI when content is None
        return None

    async def exists(self, path: str) -> bool:
        """Check if path exists in cosmos."""
        return self.index.get_latest(path) is not None

    # ---------------------------------------------------------------------
    # Write Operations
    # ---------------------------------------------------------------------

    async def commit(
        self,
        path: str,
        content: str,
        actor: str = "system",
        reasoning: str | None = None,
        mark_id: str | None = None,
    ) -> VersionId:
        """
        Commit new content to cosmos.

        This is the ONLY way to write to the cosmos.
        Returns the new version ID.

        Args:
            path: Cosmos path (e.g., "spec/protocols/k-block.md")
            content: The content to commit
            actor: Who is making this change ("Kent", "Claude", "system")
            reasoning: Human-readable explanation of why
            mark_id: Optional MarkId linking to Witness trace for full audit trail

        Phase 2 Enhancement:
            When mark_id is provided, the entry links to the full Witness trace.
            This enables blame(), history traversal, and session replay.
        """
        # Get parent version (if exists)
        parent_version = self.index.get_latest(path)

        # Create entry
        entry = CosmosEntry.create(
            path=path,
            content=content,
            parent_version=parent_version,
            actor=actor,
            reasoning=reasoning,
            mark_id=mark_id,
        )

        # Append to log
        version_id = self.log.append(entry)

        # Update index
        self.index.update(path, version_id)

        return version_id

    # ---------------------------------------------------------------------
    # History Operations
    # ---------------------------------------------------------------------

    async def history(self, path: str) -> list[CosmosEntry]:
        """
        Get all versions of a path, newest first.
        """
        versions = self.index.get_versions(path)
        entries = [self.log.get(v) for v in reversed(versions)]
        return [e for e in entries if e is not None]

    async def travel(self, version: VersionId) -> "CosmosView":
        """
        Return a cosmos view at a historical version.

        The view sees the cosmos as it was at that version.
        """
        return CosmosView(cosmos=self, as_of=version)

    async def diff(self, v1: VersionId, v2: VersionId) -> str | None:
        """
        Compute diff between two versions.

        Returns unified diff string, or None if versions not found.
        """
        import difflib

        e1 = self.log.get(v1)
        e2 = self.log.get(v2)

        if e1 is None or e2 is None:
            return None

        diff_lines = list(
            difflib.unified_diff(
                e1.content.splitlines(keepends=True),
                e2.content.splitlines(keepends=True),
                fromfile=f"{e1.path}@{v1}",
                tofile=f"{e2.path}@{v2}",
            )
        )
        return "".join(diff_lines)

    # ---------------------------------------------------------------------
    # Witness-Enabled History (Phase 2)
    # ---------------------------------------------------------------------

    async def blame(self, path: str, limit: int = 10) -> list["BlameEntry"]:
        """
        Get traced history for a path with witness context.

        Returns BlameEntry instances that include:
        - version_id: Which version
        - actor: Who made the change
        - reasoning: Why they made it
        - mark_id: Link to full Witness trace (for Toulmin proof access)
        - timestamp: When it happened
        - summary: First line of content change

        This is the Phase 2 "git blame meets witness" feature.

        Args:
            path: Cosmos path to trace
            limit: Maximum entries to return (default 10)

        Returns:
            List of BlameEntry, newest first
        """
        entries = await self.history(path)
        blame_entries: list[BlameEntry] = []

        for i, entry in enumerate(entries[:limit]):
            # Compute summary (first line of diff with parent)
            summary = ""
            if entry.parent_version:
                parent = self.log.get(entry.parent_version)
                if parent:
                    # Get first changed line as summary
                    old_lines = parent.content.splitlines()
                    new_lines = entry.content.splitlines()
                    for old, new in zip(old_lines, new_lines):
                        if old != new:
                            summary = (
                                f"Changed: {new[:60]}..." if len(new) > 60 else f"Changed: {new}"
                            )
                            break
                    else:
                        # Check for additions
                        if len(new_lines) > len(old_lines):
                            added = new_lines[len(old_lines)]
                            summary = (
                                f"Added: {added[:60]}..." if len(added) > 60 else f"Added: {added}"
                            )
            else:
                # Initial commit
                first_line = entry.content.split("\n")[0] if entry.content else ""
                summary = (
                    f"Initial: {first_line[:60]}..."
                    if len(first_line) > 60
                    else f"Initial: {first_line}"
                )

            blame_entries.append(
                BlameEntry(
                    version_id=entry.version_id,
                    actor=entry.actor,
                    reasoning=entry.reasoning,
                    mark_id=entry.mark_id,
                    timestamp=entry.timestamp,
                    summary=summary,
                )
            )

        return blame_entries

    async def get_mark_ids_for_path(self, path: str) -> list[str]:
        """
        Get all MarkIds associated with changes to a path.

        Useful for bulk-loading witness traces for a file's history.

        Returns:
            List of MarkIds (strings), newest first, excluding None values
        """
        entries = await self.history(path)
        return [e.mark_id for e in entries if e.mark_id is not None]

    # ---------------------------------------------------------------------
    # K-Block Registry
    # ---------------------------------------------------------------------

    def register_block(self, path: str, block_id: "KBlockId") -> None:
        """Register an active K-Block for a path."""
        self.active_blocks[path] = block_id

    def unregister_block(self, path: str) -> None:
        """Unregister K-Block for a path."""
        self.active_blocks.pop(path, None)

    def get_active_block(self, path: str) -> "KBlockId | None":
        """Get active K-Block ID for path."""
        return self.active_blocks.get(path)

    def get_all_active_blocks(self) -> dict[str, "KBlockId"]:
        """Get all active K-Blocks."""
        return dict(self.active_blocks)

    # ---------------------------------------------------------------------
    # Dependency Tracking
    # ---------------------------------------------------------------------

    def add_dependent(self, path: str, dependent_path: str) -> None:
        """Record that dependent_path references path."""
        if path not in self.dependents:
            self.dependents[path] = set()
        self.dependents[path].add(dependent_path)

    def get_dependents(self, path: str) -> set[str]:
        """Get paths that reference the given path."""
        return self.dependents.get(path, set())

    # ---------------------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------------------

    @property
    def total_entries(self) -> int:
        """Total entries in log."""
        return len(self.log)

    @property
    def unique_paths(self) -> int:
        """Number of unique paths."""
        return len(self.index.all_paths())


# -----------------------------------------------------------------------------
# Cosmos View (Historical)
# -----------------------------------------------------------------------------


@dataclass
class CosmosView:
    """
    A read-only view of the cosmos at a specific version.

    Used for time travel.
    """

    cosmos: Cosmos
    as_of: VersionId

    async def read(self, path: str) -> str | None:
        """Read content as it was at this version."""
        # Find the latest version of this path that's <= as_of
        versions = self.cosmos.index.get_versions(path)

        for v in reversed(versions):
            entry = self.cosmos.log.get(v)
            if entry and entry.timestamp <= self._get_timestamp():
                return entry.content

        return None

    def _get_timestamp(self) -> datetime:
        """Get timestamp of the as_of version."""
        entry = self.cosmos.log.get(self.as_of)
        return entry.timestamp if entry else datetime.min.replace(tzinfo=timezone.utc)


# -----------------------------------------------------------------------------
# Global Cosmos Instance
# -----------------------------------------------------------------------------

_cosmos: Cosmos | None = None


def get_cosmos() -> Cosmos:
    """Get the global cosmos instance."""
    global _cosmos
    if _cosmos is None:
        _cosmos = Cosmos()
    return _cosmos


def set_cosmos(cosmos: Cosmos) -> None:
    """Set the global cosmos instance (for testing)."""
    global _cosmos
    _cosmos = cosmos


def reset_cosmos() -> None:
    """Reset the global cosmos instance (for testing)."""
    global _cosmos
    _cosmos = None
