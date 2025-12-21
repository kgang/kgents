"""
Interactive Text Event Definitions and DataBus Integration.

This module defines events emitted by the Document Polynomial state machine
and provides integration with the DataBus for cross-jewel coordination.

Events are emitted on state transitions to enable:
- Verification service to track document changes
- Memory service to crystallize document state
- Witness service for observability
- UI projections to update in real-time

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 3.6, 11.1, 11.2, 11.3, 11.4, 11.5
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Awaitable, Callable, Final
from uuid import uuid4

from services.interactive_text.contracts import DocumentState
from services.interactive_text.polynomial import TransitionOutput

# =============================================================================
# Event Types
# =============================================================================


class DocumentEventType(Enum):
    """Types of document events emitted by the polynomial state machine.

    These events correspond to state transitions in the DocumentPolynomial
    and are emitted through the DataBus for cross-jewel coordination.

    Requirements: 3.6, 11.1
    """

    # State transition events
    STATE_CHANGED = auto()  # Any state transition

    # VIEWING state events
    EDIT_STARTED = auto()  # VIEWING → EDITING
    DOCUMENT_REFRESHED = auto()  # VIEWING → VIEWING (refresh)
    TOKEN_HOVERED = auto()  # VIEWING → VIEWING (hover)
    TOKEN_CLICKED = auto()  # VIEWING → VIEWING (click)
    TOKEN_DRAGGED = auto()  # VIEWING → VIEWING (drag)

    # EDITING state events
    SAVE_REQUESTED = auto()  # EDITING → SYNCING
    EDIT_CANCELLED = auto()  # EDITING → VIEWING
    EDIT_CONTINUED = auto()  # EDITING → EDITING

    # SYNCING state events
    SYNC_COMPLETED = auto()  # SYNCING → VIEWING (success)
    LOCAL_FORCED = auto()  # SYNCING → VIEWING (force local)
    REMOTE_FORCED = auto()  # SYNCING → VIEWING (force remote)
    CONFLICT_DETECTED = auto()  # SYNCING → CONFLICTING

    # CONFLICTING state events
    CONFLICT_RESOLVED = auto()  # CONFLICTING → VIEWING
    CONFLICT_ABORTED = auto()  # CONFLICTING → VIEWING
    DIFF_VIEWED = auto()  # CONFLICTING → CONFLICTING


# Mapping from (state, input) to event type
_TRANSITION_TO_EVENT: dict[tuple[DocumentState, str], DocumentEventType] = {
    # VIEWING transitions
    (DocumentState.VIEWING, "edit"): DocumentEventType.EDIT_STARTED,
    (DocumentState.VIEWING, "refresh"): DocumentEventType.DOCUMENT_REFRESHED,
    (DocumentState.VIEWING, "hover"): DocumentEventType.TOKEN_HOVERED,
    (DocumentState.VIEWING, "click"): DocumentEventType.TOKEN_CLICKED,
    (DocumentState.VIEWING, "drag"): DocumentEventType.TOKEN_DRAGGED,
    # EDITING transitions
    (DocumentState.EDITING, "save"): DocumentEventType.SAVE_REQUESTED,
    (DocumentState.EDITING, "cancel"): DocumentEventType.EDIT_CANCELLED,
    (DocumentState.EDITING, "continue_edit"): DocumentEventType.EDIT_CONTINUED,
    (DocumentState.EDITING, "hover"): DocumentEventType.TOKEN_HOVERED,
    # SYNCING transitions
    (DocumentState.SYNCING, "wait"): DocumentEventType.SYNC_COMPLETED,
    (DocumentState.SYNCING, "force_local"): DocumentEventType.LOCAL_FORCED,
    (DocumentState.SYNCING, "force_remote"): DocumentEventType.REMOTE_FORCED,
    # CONFLICTING transitions
    (DocumentState.CONFLICTING, "resolve"): DocumentEventType.CONFLICT_RESOLVED,
    (DocumentState.CONFLICTING, "abort"): DocumentEventType.CONFLICT_ABORTED,
    (DocumentState.CONFLICTING, "view_diff"): DocumentEventType.DIFF_VIEWED,
}


# =============================================================================
# Document Event
# =============================================================================


@dataclass(frozen=True)
class DocumentEvent:
    """An event representing a document state transition.

    DocumentEvents are emitted by the Document Polynomial on every state
    transition. They are consumed by verification, memory, witness, and
    UI services for cross-jewel coordination.

    Attributes:
        event_id: Unique identifier for this event
        event_type: The type of document event
        document_path: Path to the document (if applicable)
        previous_state: State before the transition
        new_state: State after the transition
        input_action: The input that triggered the transition
        output: The transition output
        timestamp: When the event occurred
        source: Source identifier (e.g., "document_polynomial")
        causal_parent: ID of the event that caused this one (for ordering)
        metadata: Additional event-specific data

    Requirements: 3.6, 11.1
    """

    event_id: str
    event_type: DocumentEventType
    document_path: str | None
    previous_state: DocumentState
    new_state: DocumentState
    input_action: str
    output: dict[str, Any]  # Serialized TransitionOutput
    timestamp: float
    source: str = "document_polynomial"
    causal_parent: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: DocumentEventType,
        document_path: str | Path | None,
        previous_state: DocumentState,
        new_state: DocumentState,
        input_action: str,
        output: TransitionOutput,
        source: str = "document_polynomial",
        causal_parent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentEvent:
        """Factory for creating document events with sensible defaults.

        Args:
            event_type: The type of document event
            document_path: Path to the document
            previous_state: State before the transition
            new_state: State after the transition
            input_action: The input that triggered the transition
            output: The transition output
            source: Source identifier
            causal_parent: ID of the causing event
            metadata: Additional event data

        Returns:
            A new DocumentEvent instance
        """
        return cls(
            event_id=uuid4().hex,
            event_type=event_type,
            document_path=str(document_path) if document_path else None,
            previous_state=previous_state,
            new_state=new_state,
            input_action=input_action,
            output=output.to_dict(),
            timestamp=time.time(),
            source=source,
            causal_parent=causal_parent,
            metadata=metadata or {},
        )

    @classmethod
    def from_transition(
        cls,
        document_path: str | Path | None,
        previous_state: DocumentState,
        input_action: str,
        new_state: DocumentState,
        output: TransitionOutput,
        causal_parent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentEvent:
        """Create event from a polynomial transition.

        Automatically determines the event type from the transition.

        Args:
            document_path: Path to the document
            previous_state: State before the transition
            input_action: The input that triggered the transition
            new_state: State after the transition
            output: The transition output
            causal_parent: ID of the causing event
            metadata: Additional event data

        Returns:
            A new DocumentEvent instance
        """
        # Determine event type from transition
        key = (previous_state, input_action)
        event_type = _TRANSITION_TO_EVENT.get(key, DocumentEventType.STATE_CHANGED)

        return cls.create(
            event_type=event_type,
            document_path=document_path,
            previous_state=previous_state,
            new_state=new_state,
            input_action=input_action,
            output=output,
            causal_parent=causal_parent,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.name,
            "document_path": self.document_path,
            "previous_state": self.previous_state.value,
            "new_state": self.new_state.value,
            "input_action": self.input_action,
            "output": self.output,
            "timestamp": self.timestamp,
            "source": self.source,
            "causal_parent": self.causal_parent,
            "metadata": self.metadata,
        }


# =============================================================================
# Document Event Bus
# =============================================================================

# Type alias for event handlers
DocumentEventHandler = Callable[[DocumentEvent], Awaitable[None]]


@dataclass
class DocumentSubscriber:
    """A subscriber to document events."""

    handler: DocumentEventHandler
    id: str = field(default_factory=lambda: uuid4().hex)


DEFAULT_BUFFER_SIZE: Final[int] = 1000


class DocumentEventBus:
    """Event bus for document state transitions.

    This bus is specific to the interactive text service and emits
    DocumentEvents on polynomial state transitions. It can be bridged
    to the global DataBus for cross-jewel coordination.

    Features:
    - Multiple subscribers per event type
    - Async, non-blocking emission
    - Replay capability (for late subscribers)
    - Causal ordering guarantees

    Requirements: 3.6, 11.1
    """

    def __init__(self, buffer_size: int = DEFAULT_BUFFER_SIZE) -> None:
        self._subscribers: dict[DocumentEventType, list[DocumentSubscriber]] = defaultdict(list)
        self._all_subscribers: list[DocumentSubscriber] = []
        self._buffer: list[DocumentEvent] = []
        self._buffer_size = buffer_size
        self._lock = asyncio.Lock()
        self._emit_count = 0
        self._error_count = 0
        self._last_event_id: str | None = None

    async def emit(self, event: DocumentEvent) -> None:
        """Emit an event to all subscribers.

        Non-blocking: subscribers run in background tasks.

        Args:
            event: The document event to emit
        """
        async with self._lock:
            # Maintain bounded buffer
            if len(self._buffer) >= self._buffer_size:
                self._buffer.pop(0)
            self._buffer.append(event)
            self._emit_count += 1
            self._last_event_id = event.event_id

        # Get all handlers for this event type
        type_handlers = list(self._subscribers.get(event.event_type, []))
        all_handlers = list(self._all_subscribers)

        # Notify all handlers (non-blocking)
        for subscriber in type_handlers + all_handlers:
            asyncio.create_task(self._safe_notify(subscriber, event))

    async def emit_transition(
        self,
        document_path: str | Path | None,
        previous_state: DocumentState,
        input_action: str,
        new_state: DocumentState,
        output: TransitionOutput,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentEvent:
        """Emit an event for a polynomial transition.

        Convenience method that creates and emits a DocumentEvent
        from transition parameters.

        Args:
            document_path: Path to the document
            previous_state: State before the transition
            input_action: The input that triggered the transition
            new_state: State after the transition
            output: The transition output
            metadata: Additional event data

        Returns:
            The emitted DocumentEvent
        """
        event = DocumentEvent.from_transition(
            document_path=document_path,
            previous_state=previous_state,
            input_action=input_action,
            new_state=new_state,
            output=output,
            causal_parent=self._last_event_id,
            metadata=metadata,
        )
        await self.emit(event)
        return event

    async def _safe_notify(self, subscriber: DocumentSubscriber, event: DocumentEvent) -> None:
        """Safely notify a subscriber, catching exceptions."""
        try:
            await subscriber.handler(event)
        except Exception:
            self._error_count += 1
            # Log but don't propagate (non-blocking)
            pass

    def subscribe(
        self,
        event_type: DocumentEventType,
        handler: DocumentEventHandler,
    ) -> Callable[[], None]:
        """Subscribe to events of a specific type.

        Args:
            event_type: The type of events to subscribe to
            handler: Async function to call for each event

        Returns:
            Unsubscribe function (call to stop receiving events)
        """
        subscriber = DocumentSubscriber(handler=handler)
        self._subscribers[event_type].append(subscriber)

        def unsubscribe() -> None:
            if subscriber in self._subscribers[event_type]:
                self._subscribers[event_type].remove(subscriber)

        return unsubscribe

    def subscribe_all(
        self,
        handler: DocumentEventHandler,
    ) -> Callable[[], None]:
        """Subscribe to ALL event types.

        Args:
            handler: Async function to call for each event

        Returns:
            Unsubscribe function
        """
        subscriber = DocumentSubscriber(handler=handler)
        self._all_subscribers.append(subscriber)

        def unsubscribe() -> None:
            if subscriber in self._all_subscribers:
                self._all_subscribers.remove(subscriber)

        return unsubscribe

    async def replay(
        self,
        handler: DocumentEventHandler,
        since: float | None = None,
        event_type: DocumentEventType | None = None,
    ) -> int:
        """Replay buffered events to a handler.

        Useful for late subscribers to catch up.

        Args:
            handler: Async function to call for each event
            since: Only replay events after this timestamp (None = all)
            event_type: Only replay events of this type (None = all)

        Returns:
            Count of replayed events
        """
        count = 0
        async with self._lock:
            for event in self._buffer:
                # Apply filters
                if since is not None and event.timestamp < since:
                    continue
                if event_type is not None and event.event_type != event_type:
                    continue

                await handler(event)
                count += 1
        return count

    @property
    def latest(self) -> DocumentEvent | None:
        """Get the most recent event."""
        if self._buffer:
            return self._buffer[-1]
        return None

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "buffer_size": len(self._buffer),
            "total_emitted": self._emit_count,
            "total_errors": self._error_count,
            "subscriber_count": sum(len(subs) for subs in self._subscribers.values())
            + len(self._all_subscribers),
        }

    def clear(self) -> None:
        """Clear all subscribers and buffer (for testing)."""
        self._subscribers.clear()
        self._all_subscribers.clear()
        self._buffer.clear()
        self._emit_count = 0
        self._error_count = 0
        self._last_event_id = None


# =============================================================================
# Event-Emitting Polynomial Wrapper
# =============================================================================


class EventEmittingPolynomial:
    """Document Polynomial wrapper that emits events on transitions.

    This class wraps the DocumentPolynomial state machine and emits
    DocumentEvents through the DocumentEventBus on every transition.

    Usage:
        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/path/to/doc.md")

        # Transition emits event automatically
        new_state, output = await poly.transition(DocumentState.VIEWING, "edit")

    Requirements: 3.6, 11.1
    """

    def __init__(
        self,
        bus: DocumentEventBus,
        document_path: str | Path | None = None,
    ) -> None:
        """Initialize event-emitting polynomial.

        Args:
            bus: The event bus to emit events to
            document_path: Path to the document (for event metadata)
        """
        self.bus = bus
        self.document_path = document_path

    async def transition(
        self,
        state: DocumentState,
        input_action: str,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[DocumentState, TransitionOutput, DocumentEvent]:
        """Perform transition and emit event.

        Args:
            state: Current document state
            input_action: The input action to process
            metadata: Additional event metadata

        Returns:
            Tuple of (new_state, output, event)
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        # Perform the transition
        new_state, output = DocumentPolynomial.transition(state, input_action)

        # Emit event
        event = await self.bus.emit_transition(
            document_path=self.document_path,
            previous_state=state,
            input_action=input_action,
            new_state=new_state,
            output=output,
            metadata=metadata,
        )

        return new_state, output, event


# =============================================================================
# Global Bus Instance
# =============================================================================

_global_document_bus: DocumentEventBus | None = None


def get_document_event_bus() -> DocumentEventBus:
    """Get the global document event bus instance."""
    global _global_document_bus
    if _global_document_bus is None:
        _global_document_bus = DocumentEventBus()
    return _global_document_bus


def reset_document_event_bus() -> None:
    """Reset the global document event bus (for testing)."""
    global _global_document_bus
    if _global_document_bus is not None:
        _global_document_bus.clear()
    _global_document_bus = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Event types
    "DocumentEventType",
    # Event class
    "DocumentEvent",
    # Event bus
    "DocumentEventBus",
    "DocumentEventHandler",
    "DocumentSubscriber",
    # Event-emitting polynomial
    "EventEmittingPolynomial",
    # Global bus
    "get_document_event_bus",
    "reset_document_event_bus",
]
