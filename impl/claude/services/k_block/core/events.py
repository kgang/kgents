"""
K-Block Event Sourcing: Head-First Design for Performance.

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Every action leaves a trace. Nothing is truly deleted.

Kent's Decision (2025-01-17):
    Persistence model = Event Sourced
    "Every edit is an event. Full history, replayable."

Design Principle (HEAD-FIRST):
    The common case (get current state) must be O(1), not O(n).

    - HEAD POINTER: Always stores the current canonical content
    - EVENTS: Store reverse deltas (undo operations)
    - HISTORY: Apply reverse deltas backward from head to reconstruct past states

    To get current state: return head (O(1))
    To get state at time T: start from head, apply reverse deltas back to T

    This inverts the traditional event sourcing model where you replay
    from genesis. Instead, we store the result and can rewind on demand.

Event Types:
    - CREATE: K-Block created (genesis) — stores initial content
    - EDIT: Content changed — stores reverse delta (how to undo)
    - LINK: Edge created to another K-Block
    - UNLINK: Edge removed
    - CHECKPOINT: Named restore point created
    - COMMIT: Changes committed to cosmos
    - DISCARD: Changes discarded
    - FORK: K-Block forked

See: spec/protocols/k-block.md
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .kblock import EditDelta, KBlock, KBlockId


# =============================================================================
# Event Types
# =============================================================================


class KBlockEventType(Enum):
    """
    K-Block event taxonomy.

    Each event type represents an atomic, immutable action on a K-Block.
    Events store REVERSE DELTAS — how to undo the operation to get previous state.

    HEAD-FIRST PRINCIPLE:
        Events don't describe "what happened" — they describe "how to undo".
        This allows O(1) access to current state while preserving full history.
    """

    # Genesis
    CREATE = "create"  # K-Block created — stores genesis content (no reverse)

    # Content (stores reverse delta for undo)
    EDIT = "edit"  # EditDelta applied — reverse_delta undoes this edit
    SET_CONTENT = "set_content"  # Bulk replacement — stores previous content

    # Graph (Kent's decision: K-Blocks reference, not contain)
    LINK = "link"  # Edge created — reverse removes edge
    UNLINK = "unlink"  # Edge removed — reverse restores edge

    # Checkpoints
    CHECKPOINT = "checkpoint"  # Named restore point — stores content snapshot
    REWIND = "rewind"  # Reverted to checkpoint — stores pre-rewind content

    # Harness operations
    COMMIT = "commit"  # Changes committed to cosmos
    DISCARD = "discard"  # Changes discarded — stores discarded content
    FORK = "fork"  # K-Block forked


# =============================================================================
# Head Pointer (Current Canonical State)
# =============================================================================


@dataclass
class KBlockHead:
    """
    The current canonical state of a K-Block.

    This is the "head pointer" — always contains the latest content.
    Accessing current state is O(1): just return head.content.

    The head is mutable (updated on each operation), while events are immutable.

    Invariants:
        - head.content == current working copy
        - head.sequence == latest event sequence number
        - head.links == current set of linked K-Block IDs
    """

    kblock_id: str
    content: str
    sequence: int  # Latest event sequence number
    links: set[str] = field(default_factory=set)  # Current linked K-Block IDs
    path: str = ""
    kind: str = "file"
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "kblock_id": self.kblock_id,
            "content": self.content,
            "sequence": self.sequence,
            "links": list(self.links),
            "path": self.path,
            "kind": self.kind,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KBlockHead":
        """Deserialize from persistence."""
        return cls(
            kblock_id=data["kblock_id"],
            content=data["content"],
            sequence=data["sequence"],
            links=set(data.get("links", [])),
            path=data.get("path", ""),
            kind=data.get("kind", "file"),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


# =============================================================================
# Event Data Classes
# =============================================================================


@dataclass(frozen=True)
class KBlockEvent:
    """
    Immutable event in the K-Block event log.

    Events are the source of truth. State is derived by replaying events.
    Each event has a unique ID, timestamp, and payload specific to its type.

    Invariants:
        - Events are immutable (frozen dataclass)
        - Events are append-only (never modified or deleted)
        - Event order is determined by sequence_number
        - Replay(events) = current state

    Example:
        >>> event = KBlockEvent.create(kblock_id, KBlockEventType.EDIT, {...})
        >>> store.append(event)
        >>> state = replay(store.get_events(kblock_id))
    """

    id: str  # Unique event ID
    kblock_id: str  # Which K-Block this event belongs to
    event_type: KBlockEventType
    payload: dict[str, Any]  # Type-specific data
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sequence_number: int = 0  # Order within K-Block's event stream

    @classmethod
    def create(
        cls,
        kblock_id: str,
        event_type: KBlockEventType,
        payload: dict[str, Any],
        sequence_number: int = 0,
    ) -> "KBlockEvent":
        """Create a new event with auto-generated ID."""
        return cls(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            kblock_id=kblock_id,
            event_type=event_type,
            payload=payload,
            sequence_number=sequence_number,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "id": self.id,
            "kblock_id": self.kblock_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "sequence_number": self.sequence_number,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KBlockEvent":
        """Deserialize from persistence."""
        return cls(
            id=data["id"],
            kblock_id=data["kblock_id"],
            event_type=KBlockEventType(data["event_type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sequence_number=data.get("sequence_number", 0),
        )


# =============================================================================
# Event Store Protocol
# =============================================================================


@runtime_checkable
class EventStoreProtocol(Protocol):
    """
    Protocol for K-Block event storage (HEAD-FIRST DESIGN).

    Key principle: Current state is O(1), history is O(n) on demand.

    Implementations may use:
    - In-memory (for testing)
    - File-based (for local dev)
    - PostgreSQL (for production)

    HEAD-FIRST CONTRACT:
        1. get_head() returns current state in O(1)
        2. append() updates head AND stores reverse delta
        3. get_state_at() reconstructs historical state by rewinding from head
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Head Management (O(1) access to current state)
    # ─────────────────────────────────────────────────────────────────────────

    def get_head(self, kblock_id: str) -> KBlockHead | None:
        """Get current state in O(1). Returns None if K-Block doesn't exist."""
        ...

    def set_head(self, head: KBlockHead) -> None:
        """Update the head pointer (called internally by append)."""
        ...

    # ─────────────────────────────────────────────────────────────────────────
    # Event Log (append-only, stores reverse deltas)
    # ─────────────────────────────────────────────────────────────────────────

    def append(self, event: KBlockEvent, new_head: KBlockHead) -> None:
        """
        Append an event AND update head atomically.

        The event's payload contains the REVERSE DELTA — how to undo this operation.
        The new_head contains the CURRENT STATE after the operation.

        This ensures:
            - Current state is always available via get_head() in O(1)
            - History can be reconstructed by applying reverse deltas
        """
        ...

    def get_events(
        self,
        kblock_id: str,
        since_sequence: int = 0,
    ) -> list[KBlockEvent]:
        """Get events for a K-Block, optionally since a sequence number."""
        ...

    def get_latest_sequence(self, kblock_id: str) -> int:
        """Get the latest sequence number for a K-Block."""
        ...


# =============================================================================
# In-Memory Event Store (for testing)
# =============================================================================


class InMemoryEventStore:
    """
    In-memory event store for testing (HEAD-FIRST DESIGN).

    Stores:
    - _heads: Current state for each K-Block (O(1) access)
    - _events: Reverse delta log for history reconstruction

    Not persistent - lost on process exit.
    """

    def __init__(self) -> None:
        self._heads: dict[str, KBlockHead] = {}
        self._events: dict[str, list[KBlockEvent]] = {}

    # ─────────────────────────────────────────────────────────────────────────
    # Head Management
    # ─────────────────────────────────────────────────────────────────────────

    def get_head(self, kblock_id: str) -> KBlockHead | None:
        """Get current state in O(1)."""
        return self._heads.get(kblock_id)

    def set_head(self, head: KBlockHead) -> None:
        """Update the head pointer."""
        self._heads[head.kblock_id] = head

    # ─────────────────────────────────────────────────────────────────────────
    # Event Log
    # ─────────────────────────────────────────────────────────────────────────

    def append(self, event: KBlockEvent, new_head: KBlockHead) -> None:
        """Append event AND update head atomically."""
        if event.kblock_id not in self._events:
            self._events[event.kblock_id] = []

        # Auto-assign sequence number
        next_seq = len(self._events[event.kblock_id])
        event_with_seq = KBlockEvent(
            id=event.id,
            kblock_id=event.kblock_id,
            event_type=event.event_type,
            payload=event.payload,
            timestamp=event.timestamp,
            sequence_number=next_seq,
        )
        self._events[event.kblock_id].append(event_with_seq)

        # Update head with correct sequence
        new_head.sequence = next_seq
        self._heads[event.kblock_id] = new_head

    def get_events(
        self,
        kblock_id: str,
        since_sequence: int = 0,
    ) -> list[KBlockEvent]:
        """Get events for a K-Block, optionally since a sequence number."""
        events = self._events.get(kblock_id, [])
        return [e for e in events if e.sequence_number >= since_sequence]

    def get_latest_sequence(self, kblock_id: str) -> int:
        """Get the latest sequence number for a K-Block."""
        head = self._heads.get(kblock_id)
        if head is None:
            return -1
        return head.sequence

    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._heads.clear()
        self._events.clear()


# =============================================================================
# File-Based Event Store (for local development)
# =============================================================================


class FileEventStore:
    """
    File-based event store for local development (HEAD-FIRST DESIGN).

    Directory structure:
        {base_path}/
            heads/
                {kblock_id}.json     # Current state (O(1) read)
            events/
                {kblock_id}.jsonl    # Reverse delta log

    HEAD-FIRST: heads/ are read first for current state.
    events/ are only read when reconstructing history.
    """

    def __init__(self, base_path: Path | str) -> None:
        self.base_path = Path(base_path)
        self.heads_dir = self.base_path / "heads"
        self.events_dir = self.base_path / "events"
        self.heads_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

    def _safe_id(self, kblock_id: str) -> str:
        """Sanitize kblock_id for filesystem."""
        return kblock_id.replace("/", "_").replace("\\", "_")

    def _head_file(self, kblock_id: str) -> Path:
        """Get the head file path for a K-Block."""
        return self.heads_dir / f"{self._safe_id(kblock_id)}.json"

    def _event_file(self, kblock_id: str) -> Path:
        """Get the event file path for a K-Block."""
        return self.events_dir / f"{self._safe_id(kblock_id)}.jsonl"

    # ─────────────────────────────────────────────────────────────────────────
    # Head Management
    # ─────────────────────────────────────────────────────────────────────────

    def get_head(self, kblock_id: str) -> KBlockHead | None:
        """Get current state in O(1) — just read the head file."""
        head_file = self._head_file(kblock_id)
        if not head_file.exists():
            return None
        with head_file.open("r", encoding="utf-8") as f:
            return KBlockHead.from_dict(json.load(f))

    def set_head(self, head: KBlockHead) -> None:
        """Update the head pointer."""
        head_file = self._head_file(head.kblock_id)
        # Atomic write via temp file
        temp_file = head_file.with_suffix(".tmp")
        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(head.to_dict(), f)
        temp_file.rename(head_file)

    # ─────────────────────────────────────────────────────────────────────────
    # Event Log
    # ─────────────────────────────────────────────────────────────────────────

    def append(self, event: KBlockEvent, new_head: KBlockHead) -> None:
        """Append event AND update head atomically."""
        # Get next sequence number
        current_head = self.get_head(event.kblock_id)
        next_seq = (current_head.sequence + 1) if current_head else 0

        event_with_seq = KBlockEvent(
            id=event.id,
            kblock_id=event.kblock_id,
            event_type=event.event_type,
            payload=event.payload,
            timestamp=event.timestamp,
            sequence_number=next_seq,
        )

        # Append event to log
        event_file = self._event_file(event.kblock_id)
        with event_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event_with_seq.to_dict()) + "\n")

        # Update head with correct sequence
        new_head.sequence = next_seq
        self.set_head(new_head)

    def get_events(
        self,
        kblock_id: str,
        since_sequence: int = 0,
    ) -> list[KBlockEvent]:
        """Get events for a K-Block, optionally since a sequence number."""
        event_file = self._event_file(kblock_id)
        if not event_file.exists():
            return []

        events = []
        with event_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event = KBlockEvent.from_dict(json.loads(line))
                if event.sequence_number >= since_sequence:
                    events.append(event)

        return events

    def get_latest_sequence(self, kblock_id: str) -> int:
        """Get the latest sequence number for a K-Block."""
        head = self.get_head(kblock_id)
        if head is None:
            return -1
        return head.sequence


# =============================================================================
# Event Emitter (for K-Block integration)
# =============================================================================


class KBlockEventEmitter:
    """
    Helper for emitting K-Block events (HEAD-FIRST DESIGN).

    Emitting an event requires providing BOTH:
    1. The event with reverse delta (for history)
    2. The new head (current state after operation)

    This ensures O(1) access to current state while preserving full history.

    Usage:
        >>> store = InMemoryEventStore()
        >>> emitter = KBlockEventEmitter(store)
        >>> head = emitter.emit_create("kb_123", "path", "content")
        >>> head = emitter.emit_edit("kb_123", head, "insert", 0, new_text="Hello")
    """

    def __init__(self, store: EventStoreProtocol) -> None:
        self.store = store

    def emit_create(
        self,
        kblock_id: str,
        path: str,
        content: str,
        kind: str = "file",
    ) -> KBlockHead:
        """
        Emit a CREATE event (genesis).

        Returns the new head (which IS the genesis state).
        CREATE is special: no reverse delta needed since it's the origin.
        """
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.CREATE,
            payload={
                "genesis_content": content,  # Store for reference
                "path": path,
                "kind": kind,
            },
        )

        # Genesis head
        head = KBlockHead(
            kblock_id=kblock_id,
            content=content,
            sequence=0,
            path=path,
            kind=kind,
        )

        self.store.append(event, head)
        return head

    def emit_edit(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        operation: str,
        position: int,
        old_text: str = "",
        new_text: str = "",
    ) -> KBlockHead:
        """
        Emit an EDIT event with REVERSE DELTA.

        The event payload stores how to UNDO this edit:
        - insert → reverse is delete
        - delete → reverse is insert
        - replace → reverse is replace with old_text

        Returns updated head with new content.
        """
        # Compute new content
        content = current_head.content
        if operation == "insert":
            new_content = content[:position] + new_text + content[position:]
            # Reverse: delete the inserted text
            reverse_op = "delete"
            reverse_old = new_text
            reverse_new = ""
        elif operation == "delete":
            end = position + len(old_text)
            new_content = content[:position] + content[end:]
            # Reverse: insert the deleted text
            reverse_op = "insert"
            reverse_old = ""
            reverse_new = old_text
        elif operation == "replace":
            end = position + len(old_text)
            new_content = content[:position] + new_text + content[end:]
            # Reverse: replace new_text with old_text
            reverse_op = "replace"
            reverse_old = new_text
            reverse_new = old_text
        else:
            raise ValueError(f"Unknown operation: {operation}")

        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.EDIT,
            payload={
                # Reverse delta (how to undo)
                "reverse_operation": reverse_op,
                "reverse_position": position,
                "reverse_old_text": reverse_old,
                "reverse_new_text": reverse_new,
                # Forward delta (for audit/debugging)
                "forward_operation": operation,
                "forward_old_text": old_text,
                "forward_new_text": new_text,
            },
        )

        # New head with updated content
        new_head = KBlockHead(
            kblock_id=kblock_id,
            content=new_content,
            sequence=current_head.sequence,  # Will be updated by store.append
            links=current_head.links.copy(),
            path=current_head.path,
            kind=current_head.kind,
        )

        self.store.append(event, new_head)
        return new_head

    def emit_set_content(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        new_content: str,
    ) -> KBlockHead:
        """
        Emit a SET_CONTENT event (bulk replacement).

        Reverse delta is the previous content.
        """
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.SET_CONTENT,
            payload={
                "previous_content": current_head.content,  # Reverse delta
            },
        )

        new_head = KBlockHead(
            kblock_id=kblock_id,
            content=new_content,
            sequence=current_head.sequence,
            links=current_head.links.copy(),
            path=current_head.path,
            kind=current_head.kind,
        )

        self.store.append(event, new_head)
        return new_head

    def emit_link(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        target_id: str,
        edge_type: str = "reference",
    ) -> KBlockHead:
        """Emit a LINK event (edge created). Reverse removes the edge."""
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.LINK,
            payload={
                "target_id": target_id,
                "edge_type": edge_type,
            },
        )

        new_links = current_head.links.copy()
        new_links.add(target_id)

        new_head = KBlockHead(
            kblock_id=kblock_id,
            content=current_head.content,
            sequence=current_head.sequence,
            links=new_links,
            path=current_head.path,
            kind=current_head.kind,
        )

        self.store.append(event, new_head)
        return new_head

    def emit_unlink(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        target_id: str,
    ) -> KBlockHead:
        """Emit an UNLINK event (edge removed). Reverse restores the edge."""
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.UNLINK,
            payload={
                "target_id": target_id,
            },
        )

        new_links = current_head.links.copy()
        new_links.discard(target_id)

        new_head = KBlockHead(
            kblock_id=kblock_id,
            content=current_head.content,
            sequence=current_head.sequence,
            links=new_links,
            path=current_head.path,
            kind=current_head.kind,
        )

        self.store.append(event, new_head)
        return new_head

    def emit_checkpoint(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        checkpoint_id: str,
        checkpoint_name: str,
    ) -> KBlockHead:
        """Emit a CHECKPOINT event. Stores content snapshot for quick rewind."""
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.CHECKPOINT,
            payload={
                "checkpoint_id": checkpoint_id,
                "checkpoint_name": checkpoint_name,
                "content_snapshot": current_head.content,  # Snapshot for fast rewind
            },
        )

        # Head unchanged (checkpoint is metadata, not content change)
        self.store.append(event, current_head)
        return current_head

    def emit_commit(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        version_id: str,
        content_hash: str,
    ) -> KBlockHead:
        """Emit a COMMIT event (changes committed to cosmos)."""
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.COMMIT,
            payload={
                "version_id": version_id,
                "content_hash": content_hash,
            },
        )

        self.store.append(event, current_head)
        return current_head

    def emit_discard(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        discarded_content: str,
    ) -> KBlockHead:
        """Emit a DISCARD event. Stores discarded content for recovery."""
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.DISCARD,
            payload={
                "discarded_content": discarded_content,
            },
        )

        self.store.append(event, current_head)
        return current_head

    def emit_fork(
        self,
        kblock_id: str,
        current_head: KBlockHead,
        new_kblock_id: str,
    ) -> KBlockHead:
        """Emit a FORK event (K-Block forked)."""
        event = KBlockEvent.create(
            kblock_id=kblock_id,
            event_type=KBlockEventType.FORK,
            payload={
                "new_kblock_id": new_kblock_id,
                "fork_point_sequence": current_head.sequence,
            },
        )

        self.store.append(event, current_head)
        return current_head


# =============================================================================
# Rewind: Head → Historical State (HEAD-FIRST DESIGN)
# =============================================================================


def get_content_at_sequence(
    store: EventStoreProtocol,
    kblock_id: str,
    target_sequence: int,
) -> str | None:
    """
    Get content at a specific sequence number by rewinding from head.

    HEAD-FIRST DESIGN:
        1. Get current head (O(1))
        2. Get events from target_sequence to head
        3. Apply reverse deltas backward to reconstruct historical state

    Args:
        store: Event store
        kblock_id: K-Block ID
        target_sequence: The sequence number to rewind to

    Returns:
        Content at target_sequence, or None if K-Block doesn't exist

    Example:
        >>> content = get_content_at_sequence(store, "kb_123", 5)
        >>> # Returns content as it was at sequence 5
    """
    head = store.get_head(kblock_id)
    if head is None:
        return None

    if target_sequence >= head.sequence:
        # Target is current or future — just return head
        return head.content

    # Get events from target+1 to head (these need to be undone)
    events = store.get_events(kblock_id, since_sequence=target_sequence + 1)

    # Apply reverse deltas in REVERSE ORDER (newest first)
    content = head.content
    for event in sorted(events, key=lambda e: e.sequence_number, reverse=True):
        content = _apply_reverse_delta(content, event)

    return content


def _apply_reverse_delta(content: str, event: KBlockEvent) -> str:
    """
    Apply a reverse delta to content, returning the previous state.

    This is the inverse of the forward operation.
    """
    if event.event_type == KBlockEventType.EDIT:
        op = event.payload.get("reverse_operation", "")
        pos = event.payload.get("reverse_position", 0)
        old_text = event.payload.get("reverse_old_text", "")
        new_text = event.payload.get("reverse_new_text", "")

        if op == "insert":
            result: str = content[:pos] + str(new_text) + content[pos:]
            return result
        elif op == "delete":
            end = pos + len(str(old_text))
            result = content[:pos] + content[end:]
            return result
        elif op == "replace":
            end = pos + len(str(old_text))
            result = content[:pos] + str(new_text) + content[end:]
            return result

    elif event.event_type == KBlockEventType.SET_CONTENT:
        # Reverse is the previous content
        previous: str = str(event.payload.get("previous_content", content))
        return previous

    # Events that don't change content just pass through
    return content


def get_current_content(store: EventStoreProtocol, kblock_id: str) -> str | None:
    """
    Get current content in O(1).

    This is the primary access pattern — HEAD-FIRST makes this fast.

    Args:
        store: Event store
        kblock_id: K-Block ID

    Returns:
        Current content, or None if K-Block doesn't exist
    """
    head = store.get_head(kblock_id)
    return head.content if head else None


def get_links_at_sequence(
    store: EventStoreProtocol,
    kblock_id: str,
    target_sequence: int,
) -> set[str] | None:
    """
    Get links at a specific sequence number by rewinding from head.

    Args:
        store: Event store
        kblock_id: K-Block ID
        target_sequence: The sequence number to rewind to

    Returns:
        Set of linked K-Block IDs at target_sequence
    """
    head = store.get_head(kblock_id)
    if head is None:
        return None

    if target_sequence >= head.sequence:
        return head.links.copy()

    # Get events from target+1 to head
    events = store.get_events(kblock_id, since_sequence=target_sequence + 1)

    # Apply reverse link operations in REVERSE ORDER
    links = head.links.copy()
    for event in sorted(events, key=lambda e: e.sequence_number, reverse=True):
        if event.event_type == KBlockEventType.LINK:
            # Reverse of LINK is to remove the link
            target_id = event.payload.get("target_id")
            if target_id:
                links.discard(target_id)
        elif event.event_type == KBlockEventType.UNLINK:
            # Reverse of UNLINK is to add the link back
            target_id = event.payload.get("target_id")
            if target_id:
                links.add(target_id)

    return links


# =============================================================================
# Legacy Compatibility: replay_content (forward from genesis)
# =============================================================================


def replay_content(events: list[KBlockEvent]) -> str:
    """
    LEGACY: Replay events forward from genesis.

    NOTE: For HEAD-FIRST design, use get_current_content() for O(1) access
    to current state, or get_content_at_sequence() to reconstruct history.

    This function is kept for compatibility with code that expects
    forward replay semantics.

    Args:
        events: List of KBlockEvents in sequence order

    Returns:
        The reconstructed content string
    """
    content = ""

    for event in sorted(events, key=lambda e: e.sequence_number):
        if event.event_type == KBlockEventType.CREATE:
            content = event.payload.get("genesis_content", "")

        elif event.event_type == KBlockEventType.SET_CONTENT:
            # Forward: we stored previous_content as reverse, so we need forward
            # For legacy, we assume there's a content field or we skip
            # In HEAD-FIRST, this is not the primary path
            pass  # SET_CONTENT reverse is previous_content

        elif event.event_type == KBlockEventType.EDIT:
            # Use forward operation for legacy replay
            op = event.payload.get("forward_operation", "")
            pos = event.payload.get("reverse_position", 0)  # Position is same
            old_text = event.payload.get("forward_old_text", "")
            new_text = event.payload.get("forward_new_text", "")

            if op == "insert":
                content = content[:pos] + new_text + content[pos:]
            elif op == "delete":
                end = pos + len(old_text)
                content = content[:pos] + content[end:]
            elif op == "replace":
                end = pos + len(old_text)
                content = content[:pos] + new_text + content[end:]

    return content


def replay_links(events: list[KBlockEvent]) -> set[str]:
    """
    LEGACY: Replay events to reconstruct links (forward from genesis).

    NOTE: For HEAD-FIRST design, use get_current_content() or get_links_at_sequence().
    """
    links: set[str] = set()

    for event in sorted(events, key=lambda e: e.sequence_number):
        if event.event_type == KBlockEventType.LINK:
            target_id = event.payload.get("target_id")
            if target_id:
                links.add(target_id)
        elif event.event_type == KBlockEventType.UNLINK:
            target_id = event.payload.get("target_id")
            if target_id:
                links.discard(target_id)

    return links


# =============================================================================
# Module-Level Store (singleton pattern)
# =============================================================================

_event_store: EventStoreProtocol | None = None


def set_event_store(store: EventStoreProtocol | None) -> None:
    """Set the global event store for K-Block operations."""
    global _event_store
    _event_store = store


def get_event_store() -> EventStoreProtocol | None:
    """Get the current event store, if configured."""
    return _event_store


def get_emitter() -> KBlockEventEmitter | None:
    """Get an emitter for the current event store."""
    store = get_event_store()
    if store is None:
        return None
    return KBlockEventEmitter(store)
