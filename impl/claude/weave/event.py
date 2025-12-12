"""
Event - An immutable event in the Weave.

Events are the atomic units of the Weave. They are:
- Immutable (frozen dataclass)
- Hashable (can be used in sets)
- Timestamped
- Attributed to a source agent
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Event(Generic[T]):
    """
    An event in the Weave.

    Events are immutable records of things that happened.
    They carry:
    - id: Unique identifier
    - content: The event payload (generic)
    - timestamp: When it occurred
    - source: Which agent emitted it

    Frozen for hashability in sets and dicts.
    """

    id: str
    content: T
    timestamp: float
    source: str

    @classmethod
    def create(
        cls,
        content: T,
        source: str,
        event_id: str | None = None,
        timestamp: float | None = None,
    ) -> "Event[T]":
        """
        Factory method to create an event.

        Args:
            content: The event payload
            source: Agent that emitted this event
            event_id: Optional ID (generated if not provided)
            timestamp: Optional timestamp (current time if not provided)

        Returns:
            A new Event instance
        """
        return cls(
            id=event_id or str(uuid.uuid4()),
            content=content,
            timestamp=timestamp or time.time(),
            source=source,
        )


@dataclass(frozen=True)
class KnotEvent(Event[None]):
    """
    A synchronization point in the Weave.

    Knots are special events where multiple concurrent
    threads must synchronize before proceeding.

    They have:
    - No content (None)
    - source="weave" (system generated)
    - Depend on multiple preceding events
    """

    @classmethod
    def create_knot(
        cls,
        event_ids: frozenset[str],
        timestamp: float | None = None,
    ) -> "KnotEvent":
        """
        Create a knot synchronization event.

        Args:
            event_ids: Events that must complete before knot
            timestamp: Optional timestamp

        Returns:
            A new KnotEvent instance
        """
        knot_id = f"knot-{hash(event_ids)}"
        return cls(
            id=knot_id,
            content=None,
            timestamp=timestamp or time.time(),
            source="weave",
        )


def generate_id() -> str:
    """Generate a unique event ID."""
    return str(uuid.uuid4())
