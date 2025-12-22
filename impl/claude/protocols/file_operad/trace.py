"""
FileWiringTrace: Persistent Trail of Portal Expansions

"Every expansion leaves a mark. Every mark is evidence."

When portals expand, we record the trail. This creates:
1. Persistent evidence of what was explored (for ASHC)
2. Session continuity (resume where you left off)
3. Pattern discovery (which paths get taken together?)

The WiringTrace captures:
- path: Which file was opened
- operation: What happened (create, read, update, delete, annotate, link)
- timestamp: When
- actor: Who (Kent, Claude, system)
- diff: What changed (for updates)
- ghost_alternatives: Paths NOT taken (Differance)

Integration points:
- PortalOpenSignal → FileWiringTrace (on every expansion)
- FileWiringTrace → D-gent (persistence via MarkStore)
- FileWiringTrace → ASHC (evidence for proof compilation)

Session 4 Update (2025-12-22):
- Added JSON persistence (save/load) following MarkStore pattern
- XDG-compliant storage at ~/.local/share/kgents/trails/file_traces.json
- Cross-session trail continuity

See: spec/protocols/file-operad.md (FileWiringTrace ~line 329)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .portal import PortalOpenSignal

logger = logging.getLogger("kgents.file_operad.trace")


# =============================================================================
# Types
# =============================================================================

OperationType = Literal[
    "create",
    "read",
    "update",
    "delete",
    "annotate",
    "link",
    "expand",
    # Session 5: Sandbox operations
    "sandbox_create",
    "sandbox_promote",
    "sandbox_discard",
]


# =============================================================================
# FileWiringTrace: The Atomic Unit of Exploration
# =============================================================================


@dataclass(frozen=True)
class FileWiringTrace:
    """
    Record of a single file operation.

    Frozen to enforce Law 1 (Immutability): Traces cannot be modified after creation.

    From spec:
        @dataclass
        class FileWiringTrace:
            path: str
            operation: Literal["create", "read", "update", "delete", "annotate", "link"]
            timestamp: datetime
            actor: str                    # "Kent" | "Claude" | system
            diff: str | None              # For updates
            ghost_alternatives: list[str] # Paths not taken (Differance)

    Extended with:
        - edge_type: The semantic edge that led here (enables, feeds, etc.)
        - parent_path: Where we came from (for trail reconstruction)
        - depth: How deep in the expansion tree
        - session_id: For grouping related traces
    """

    # Core fields from spec
    path: str
    operation: OperationType
    timestamp: datetime
    actor: str  # "Kent" | "Claude" | "system"
    diff: str | None = None
    ghost_alternatives: tuple[str, ...] = ()  # Using tuple for frozen dataclass

    # Extended fields for portal navigation
    edge_type: str | None = None  # enables, feeds, refines, etc.
    parent_path: str | None = None  # Where we came from
    depth: int = 0
    session_id: str | None = None

    @classmethod
    def from_portal_signal(
        cls,
        signal: "PortalOpenSignal",
        actor: str = "system",
        session_id: str | None = None,
    ) -> list["FileWiringTrace"]:
        """
        Create traces from a PortalOpenSignal.

        One trace per opened path.
        """
        traces = []
        for path in signal.paths_opened:
            trace = cls(
                path=path,
                operation="expand",  # Portal expansion is a "read" variant
                timestamp=signal.timestamp,
                actor=actor,
                edge_type=signal.edge_type,
                parent_path=signal.parent_path,
                depth=signal.depth,
                session_id=session_id,
            )
            traces.append(trace)
        return traces

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "path": self.path,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "diff": self.diff,
            "ghost_alternatives": list(self.ghost_alternatives),
            "edge_type": self.edge_type,
            "parent_path": self.parent_path,
            "depth": self.depth,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FileWiringTrace":
        """Deserialize from storage."""
        return cls(
            path=data["path"],
            operation=data["operation"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            actor=data["actor"],
            diff=data.get("diff"),
            ghost_alternatives=tuple(data.get("ghost_alternatives", [])),
            edge_type=data.get("edge_type"),
            parent_path=data.get("parent_path"),
            depth=data.get("depth", 0),
            session_id=data.get("session_id"),
        )


# =============================================================================
# FileTraceStore: In-Memory + Persistent Trail
# =============================================================================


def _get_default_persistence_path() -> Path:
    """
    Get the default persistence path for file traces.

    XDG-compliant: ~/.local/share/kgents/trails/file_traces.json
    """
    data_home = Path.home() / ".local" / "share"
    xdg_data = Path(os.environ.get("XDG_DATA_HOME", data_home))
    return xdg_data / "kgents" / "trails" / "file_traces.json"


@dataclass
class FileTraceStore:
    """
    Append-only store for FileWiringTraces.

    Pattern 7: Append-Only History
    "History is a ledger. Modifications are new entries, not edits."

    Provides:
    - In-memory cache for fast queries
    - JSON persistence for cross-session continuity
    - Session grouping for context reconstruction

    Persistence:
    - save(path): Serialize all traces to JSON
    - load(path): Load traces from JSON (class method)
    - sync(): Save to persistence path if set
    """

    # In-memory storage (append-only)
    _traces: list[FileWiringTrace] = field(default_factory=list)

    # Index by session for fast session queries
    _by_session: dict[str, list[FileWiringTrace]] = field(default_factory=dict)

    # Index by path for pattern discovery
    _by_path: dict[str, list[FileWiringTrace]] = field(default_factory=dict)

    # Persistence path (if any)
    _persistence_path: Path | None = None

    def append(self, trace: FileWiringTrace) -> None:
        """
        Append a trace to the store.

        Updates all indices.
        """
        self._traces.append(trace)

        # Update session index
        if trace.session_id:
            if trace.session_id not in self._by_session:
                self._by_session[trace.session_id] = []
            self._by_session[trace.session_id].append(trace)

        # Update path index
        if trace.path not in self._by_path:
            self._by_path[trace.path] = []
        self._by_path[trace.path].append(trace)

        logger.debug(f"Recorded trace: {trace.operation} → {trace.path}")

    def get_session_trail(self, session_id: str) -> list[FileWiringTrace]:
        """Get all traces for a session, in order."""
        return list(self._by_session.get(session_id, []))

    def get_path_history(self, path: str) -> list[FileWiringTrace]:
        """Get all traces for a path (across sessions)."""
        return list(self._by_path.get(path, []))

    def recent(self, limit: int = 20) -> list[FileWiringTrace]:
        """Get most recent traces."""
        return self._traces[-limit:]

    def all(self) -> list[FileWiringTrace]:
        """Get all traces in chronological order."""
        return list(self._traces)

    def __len__(self) -> int:
        return len(self._traces)

    # =========================================================================
    # Persistence (Session 4)
    # =========================================================================

    def save(self, path: Path | str | None = None) -> Path:
        """
        Save the store to a JSON file.

        Args:
            path: Where to save. If None, uses _persistence_path if set,
                  otherwise uses default XDG path.

        Returns:
            Path where traces were saved.
        """
        if path:
            save_path = Path(path)
        elif self._persistence_path:
            save_path = self._persistence_path
        else:
            save_path = _get_default_persistence_path()

        # Ensure parent directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": 1,
            "format": "file_trace_store",
            "saved_at": datetime.now().isoformat(),
            "count": len(self._traces),
            "traces": [trace.to_dict() for trace in self._traces],
        }

        save_path.write_text(json.dumps(data, indent=2, default=str))
        self._persistence_path = save_path
        logger.info(f"Saved {len(self._traces)} traces to {save_path}")

        return save_path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "FileTraceStore":
        """
        Load a store from a JSON file.

        Args:
            path: Where to load from. Uses default XDG path if not specified.

        Returns:
            FileTraceStore with loaded traces.

        Raises:
            FileNotFoundError: If persistence file doesn't exist.
        """
        load_path = Path(path) if path else _get_default_persistence_path()

        if not load_path.exists():
            raise FileNotFoundError(f"No persistence file at {load_path}")

        data = json.loads(load_path.read_text())

        store = cls()
        store._persistence_path = load_path

        # Load traces without validation (data was validated on append)
        for trace_data in data.get("traces", []):
            trace = FileWiringTrace.from_dict(trace_data)
            # Direct append to storage (skip normal append to avoid double-indexing)
            store._traces.append(trace)

            # Update indices
            if trace.session_id:
                if trace.session_id not in store._by_session:
                    store._by_session[trace.session_id] = []
                store._by_session[trace.session_id].append(trace)

            if trace.path not in store._by_path:
                store._by_path[trace.path] = []
            store._by_path[trace.path].append(trace)

        logger.info(f"Loaded {len(store._traces)} traces from {load_path}")
        return store

    @classmethod
    def load_or_create(cls, path: Path | str | None = None) -> "FileTraceStore":
        """
        Load from persistence if exists, otherwise create new.

        This is the recommended way to get a store with persistence.
        """
        try:
            return cls.load(path)
        except FileNotFoundError:
            store = cls()
            store._persistence_path = Path(path) if path else _get_default_persistence_path()
            return store

    def sync(self) -> Path | None:
        """
        Sync to persistence path if set.

        Returns:
            Path where synced, or None if no persistence path set.
        """
        if self._persistence_path:
            return self.save(self._persistence_path)
        return None

    @property
    def persistence_path(self) -> Path | None:
        """Get the current persistence path."""
        return self._persistence_path

    def set_persistence_path(self, path: Path | str) -> None:
        """Set the persistence path."""
        self._persistence_path = Path(path)


# =============================================================================
# Global Store (Singleton)
# =============================================================================

_global_store: FileTraceStore | None = None
_persistence_enabled: bool = False


def get_file_trace_store(with_persistence: bool = False) -> FileTraceStore:
    """
    Get the global file trace store.

    Args:
        with_persistence: If True and store doesn't exist, load from persistence.
                         Default False for backwards compatibility.

    Returns:
        The global FileTraceStore singleton.
    """
    global _global_store, _persistence_enabled

    if _global_store is None:
        if with_persistence:
            _global_store = FileTraceStore.load_or_create()
            _persistence_enabled = True
        else:
            _global_store = FileTraceStore()

    return _global_store


def enable_persistence() -> FileTraceStore:
    """
    Enable persistence for the global store.

    If a store already exists in-memory, this sets its persistence path.
    If no store exists, loads from persistence file if available.

    Returns:
        The global store with persistence enabled.
    """
    global _global_store, _persistence_enabled

    if _global_store is None:
        _global_store = FileTraceStore.load_or_create()
    else:
        _global_store.set_persistence_path(_get_default_persistence_path())

    _persistence_enabled = True
    return _global_store


def sync_file_trace_store() -> Path | None:
    """
    Sync the global store to persistence (if enabled).

    Returns:
        Path where synced, or None if persistence not enabled.
    """
    if _global_store is not None and _persistence_enabled:
        return _global_store.sync()
    return None


def reset_file_trace_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store, _persistence_enabled
    _global_store = None
    _persistence_enabled = False


# =============================================================================
# Trace Recording API
# =============================================================================


def record_expansion(
    signal: "PortalOpenSignal",
    actor: str = "system",
    session_id: str | None = None,
) -> list[FileWiringTrace]:
    """
    Record portal expansion to the trace store.

    This is the main entry point for wiring PortalOpenSignal → persistence.

    Args:
        signal: The PortalOpenSignal from portal expansion
        actor: Who triggered the expansion (Kent, Claude, system)
        session_id: Optional session ID for grouping

    Returns:
        List of created FileWiringTrace objects
    """
    store = get_file_trace_store()
    traces = FileWiringTrace.from_portal_signal(signal, actor, session_id)

    for trace in traces:
        store.append(trace)

    return traces


def record_file_operation(
    path: str,
    operation: OperationType,
    actor: str = "system",
    diff: str | None = None,
    ghost_alternatives: tuple[str, ...] = (),
    session_id: str | None = None,
) -> FileWiringTrace:
    """
    Record a file operation (create, update, delete, etc.).

    Use this for non-expansion operations.
    """
    trace = FileWiringTrace(
        path=path,
        operation=operation,
        timestamp=datetime.now(),
        actor=actor,
        diff=diff,
        ghost_alternatives=ghost_alternatives,
        session_id=session_id,
    )

    store = get_file_trace_store()
    store.append(trace)

    return trace


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "OperationType",
    # Data structures
    "FileWiringTrace",
    "FileTraceStore",
    # Global store management
    "get_file_trace_store",
    "reset_file_trace_store",
    "enable_persistence",
    "sync_file_trace_store",
    # Recording API
    "record_expansion",
    "record_file_operation",
]
