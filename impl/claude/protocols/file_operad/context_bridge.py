"""
Context Bridge: Connect Portal Tokens to Agent Context.

This module bridges portal expansion signals to context events,
enabling "these files are now open" semantics for agents.

Spec: spec/protocols/portal-token.md section 6 (PortalOpenSignal.to_context_event)

Teaching:
    gotcha: ContextEvent is frozen (immutable). Creating a new event
            for each expansion ensures thread-safety and enables
            event replay.
            (Evidence: test_context_bridge.py::test_context_event_immutability)

    gotcha: The bridge is bidirectional—you can go from PortalOpenSignal
            to ContextEvent and potentially back. This enables trail
            reconstruction from context events.
            (Evidence: test_context_bridge.py::test_roundtrip_conversion)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .portal import PortalOpenSignal


# =============================================================================
# Types
# =============================================================================


ContextEventType = Literal["files_opened", "files_closed", "focus_changed"]


# =============================================================================
# Data Structures
# =============================================================================


@dataclass(frozen=True)
class ContextEvent:
    """
    Event representing a change in agent context.

    When a portal expands, this event tells the agent:
    - Which files are now "open" (in focus)
    - Why they were opened (the edge type followed)
    - How deep in the exploration we are

    Immutable by design—events are facts, not mutable state.

    From spec/protocols/portal-token.md:
        "This signal updates agent context (these files are now 'open')"

    Laws:
        1. Immutability: Events cannot be modified after creation
        2. Completeness: All fields required for context reconstruction
        3. Reversibility: Can reconstruct portal signal from event
    """

    type: ContextEventType
    paths: tuple[str, ...]  # Immutable sequence of paths
    reason: str  # Human-readable description
    depth: int  # Nesting depth in exploration
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Optional metadata for advanced use cases
    parent_path: str = ""  # What led to this context change
    edge_type: str = ""  # The hyperedge type followed

    @classmethod
    def files_opened(
        cls,
        paths: list[str] | tuple[str, ...],
        reason: str,
        depth: int,
        parent_path: str = "",
        edge_type: str = "",
    ) -> "ContextEvent":
        """Factory for files_opened events."""
        return cls(
            type="files_opened",
            paths=tuple(paths) if isinstance(paths, list) else paths,
            reason=reason,
            depth=depth,
            parent_path=parent_path,
            edge_type=edge_type,
        )

    @classmethod
    def files_closed(
        cls,
        paths: list[str] | tuple[str, ...],
        reason: str,
        depth: int,
    ) -> "ContextEvent":
        """Factory for files_closed events (portal collapse)."""
        return cls(
            type="files_closed",
            paths=tuple(paths) if isinstance(paths, list) else paths,
            reason=reason,
            depth=depth,
        )

    @classmethod
    def focus_changed(
        cls,
        paths: list[str] | tuple[str, ...],
        reason: str,
        depth: int,
    ) -> "ContextEvent":
        """Factory for focus_changed events."""
        return cls(
            type="focus_changed",
            paths=tuple(paths) if isinstance(paths, list) else paths,
            reason=reason,
            depth=depth,
        )

    @classmethod
    def from_portal_signal(cls, signal: "PortalOpenSignal") -> "ContextEvent":
        """
        Convert a PortalOpenSignal to a ContextEvent.

        This is the primary bridge from portal expansion to context update.
        """
        return cls.files_opened(
            paths=signal.paths_opened,
            reason=f"Followed [{signal.edge_type}] from {signal.parent_path}",
            depth=signal.depth,
            parent_path=signal.parent_path,
            edge_type=signal.edge_type,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage or transmission."""
        return {
            "type": self.type,
            "paths": list(self.paths),
            "reason": self.reason,
            "depth": self.depth,
            "timestamp": self.timestamp.isoformat(),
            "parent_path": self.parent_path,
            "edge_type": self.edge_type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextEvent":
        """Deserialize from storage."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now(timezone.utc)

        return cls(
            type=data["type"],
            paths=tuple(data["paths"]),
            reason=data["reason"],
            depth=data["depth"],
            timestamp=timestamp,
            parent_path=data.get("parent_path", ""),
            edge_type=data.get("edge_type", ""),
        )


# =============================================================================
# Bridge Functions
# =============================================================================


def portal_signal_to_context_event(signal: "PortalOpenSignal") -> ContextEvent:
    """
    Convert a portal expansion signal to a context event.

    This is the bridge function from file_operad to agent context.
    """
    return ContextEvent.from_portal_signal(signal)


# =============================================================================
# Context Accumulator
# =============================================================================


@dataclass
class ContextAccumulator:
    """
    Tracks which files are currently "open" in agent context.

    The accumulator maintains a set of currently visible paths and
    a history of context events. It can be used to:
    - Track what files an agent has explored
    - Determine if a file is currently in context
    - Replay context changes for debugging/auditing

    Laws:
        1. Monotonic history: event_history only grows (append-only)
        2. State derived: open_paths is always derivable from event_history
        3. Idempotent apply: Applying same event twice is a no-op

    Usage:
        accumulator = ContextAccumulator()

        # Apply events as they arrive
        accumulator.apply(ContextEvent.files_opened(["/path/to/file.py"], ...))

        # Check if file is open
        if accumulator.is_open("/path/to/file.py"):
            # File is in current context
            ...

        # Get all open files
        for path in accumulator.open_paths:
            print(f"Currently open: {path}")
    """

    open_paths: set[str] = field(default_factory=set)
    event_history: list[ContextEvent] = field(default_factory=list)
    _event_ids: set[str] = field(default_factory=set, repr=False)

    def apply(self, event: ContextEvent) -> bool:
        """
        Apply a context event to update state.

        Returns True if the event was applied (new event),
        False if it was a duplicate (idempotent).

        Args:
            event: The ContextEvent to apply

        Returns:
            True if event was new and applied, False if duplicate
        """
        # Generate a unique ID for deduplication
        event_id = f"{event.type}:{','.join(event.paths)}:{event.timestamp.isoformat()}"
        if event_id in self._event_ids:
            return False  # Already applied

        self._event_ids.add(event_id)
        self.event_history.append(event)

        match event.type:
            case "files_opened":
                self.open_paths.update(event.paths)
            case "files_closed":
                self.open_paths.difference_update(event.paths)
            case "focus_changed":
                # Focus change replaces all open paths
                self.open_paths = set(event.paths)

        return True

    def is_open(self, path: str) -> bool:
        """Check if a path is currently open."""
        return path in self.open_paths

    def close_all(self) -> ContextEvent:
        """
        Close all currently open files.

        Returns the ContextEvent that was created and applied.
        """
        if not self.open_paths:
            # Nothing to close
            return ContextEvent.files_closed(
                paths=(),
                reason="No files to close",
                depth=0,
            )

        event = ContextEvent.files_closed(
            paths=tuple(self.open_paths),
            reason="Close all",
            depth=0,
        )
        self.apply(event)
        return event

    @property
    def open_count(self) -> int:
        """Number of currently open files."""
        return len(self.open_paths)

    @property
    def event_count(self) -> int:
        """Total number of events applied."""
        return len(self.event_history)

    def summary(self) -> str:
        """Return a human-readable summary of current state."""
        lines = [f"Open files: {self.open_count}"]
        for path in sorted(self.open_paths):
            lines.append(f"  - {path}")
        lines.append(f"Total events: {self.event_count}")
        return "\n".join(lines)


__all__ = [
    "ContextEvent",
    "ContextEventType",
    "ContextAccumulator",
    "portal_signal_to_context_event",
]
