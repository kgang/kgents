"""
EventBus system for decoupled screen-to-screen communication.

Ported from zenportal patterns to enable reactive, composable dashboard architecture.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar, cast

# ===== Base Event =====


@dataclass
class Event:
    """Base class for all events in the system."""

    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Ensure timestamp is set."""
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.now()


# ===== Screen Navigation Events =====


@dataclass
class ScreenNavigationEvent(Event):
    """Emitted when navigating between screens.

    Attributes:
        target_screen: The screen being navigated to
        source_screen: The screen being navigated from (optional)
        focus_element: Element to focus on arrival (optional)
    """

    target_screen: str = ""
    source_screen: str | None = None
    focus_element: str | None = None


# ===== Agent Focus Events =====


@dataclass
class AgentFocusedEvent(Event):
    """Emitted when an agent is selected/focused.

    Attributes:
        agent_id: The unique identifier of the focused agent
    """

    agent_id: str = ""


# ===== Metrics Events =====


@dataclass
class MetricsUpdatedEvent(Event):
    """Emitted when dashboard metrics are updated.

    Attributes:
        metrics: Dictionary of metric name to value
    """

    metrics: dict[str, Any] = field(default_factory=dict)


# ===== LOD (Level of Detail) Events =====


@dataclass
class LODChangedEvent(Event):
    """Emitted when the Level of Detail changes.

    Attributes:
        old_lod: Previous LOD level
        new_lod: New LOD level
    """

    old_lod: int = 0
    new_lod: int = 0


# ===== Fever/Entropy Events =====


@dataclass
class FeverTriggeredEvent(Event):
    """Emitted when entropy exceeds threshold and fever overlay should show.

    The Accursed Share made visible: compaction, creativity, and chaos
    all manifest when entropy rises beyond sustainable levels.

    Attributes:
        entropy: Current entropy level (0.0-1.0+)
        pressure: Metabolic pressure that triggered the event
        trigger: What caused the fever ("pressure_overflow", "manual", "compaction")
        oblique_strategy: Creative strategy drawn from the void (optional)
    """

    entropy: float = 0.0
    pressure: float = 0.0
    trigger: str = "pressure_overflow"
    oblique_strategy: str | None = None


# ===== EventBus Implementation =====


E = TypeVar("E", bound=Event)


class EventBus:
    """Singleton event bus for pub-sub messaging across screens.

    Features:
    - Type-safe event subscription by event class
    - Duplicate handler prevention
    - Error isolation (one handler's exception doesn't affect others)
    - Singleton pattern with reset() for testing

    Example:
        >>> bus = EventBus.get()
        >>> def handle_nav(event: ScreenNavigationEvent):
        ...     print(f"Navigating to {event.target_screen}")
        >>> bus.subscribe(ScreenNavigationEvent, handle_nav)
        >>> bus.emit(ScreenNavigationEvent(target_screen="cockpit"))
    """

    _instance: "EventBus | None" = None

    def __init__(self) -> None:
        """Initialize empty subscriber dict.

        Note: Use EventBus.get() instead of direct instantiation.
        """
        self._subscribers: dict[type[Event], list[Callable[[Event], None]]] = (
            defaultdict(list)
        )

    @classmethod
    def get(cls) -> "EventBus":
        """Get the singleton EventBus instance.

        Returns:
            The global EventBus instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (primarily for testing).

        This clears all subscribers and creates a fresh EventBus.
        """
        cls._instance = None

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        """Subscribe a handler to an event type.

        Duplicate subscriptions are prevented automatically.

        Args:
            event_type: The class of event to subscribe to
            handler: Callable that takes the event as its only argument

        Example:
            >>> def on_focus(event: AgentFocusedEvent):
            ...     print(f"Agent {event.agent_id} focused")
            >>> EventBus.get().subscribe(AgentFocusedEvent, on_focus)
        """
        handlers = self._subscribers[event_type]
        # Cast handler to match list type - E is a subtype of Event
        handler_cast = cast(Callable[[Event], None], handler)

        # Prevent duplicate subscriptions
        if handler_cast not in handlers:
            handlers.append(handler_cast)

    def emit(self, event: E) -> None:
        """Emit an event to all subscribed handlers.

        Handlers are called in subscription order. If a handler raises an
        exception, it is caught and logged, but other handlers continue.

        Args:
            event: The event instance to emit

        Example:
            >>> bus = EventBus.get()
            >>> bus.emit(LODChangedEvent(old_lod=1, new_lod=2))
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Error isolation: one handler's failure doesn't prevent others
                # In production, this should use proper logging
                import sys

                print(
                    f"Error in event handler {handler.__name__}: {e}", file=sys.stderr
                )

    def unsubscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        """Unsubscribe a handler from an event type.

        If the handler is not subscribed, this is a no-op.

        Args:
            event_type: The class of event to unsubscribe from
            handler: The handler to remove

        Example:
            >>> def temp_handler(event: MetricsUpdatedEvent):
            ...     pass
            >>> bus = EventBus.get()
            >>> bus.subscribe(MetricsUpdatedEvent, temp_handler)
            >>> bus.unsubscribe(MetricsUpdatedEvent, temp_handler)
        """
        handlers = self._subscribers.get(event_type, [])
        # Cast handler to match list type - E is a subtype of Event
        handler_cast = cast(Callable[[Event], None], handler)

        if handler_cast in handlers:
            handlers.remove(handler_cast)

    def clear_all(self) -> None:
        """Remove all subscribers from all event types.

        Useful for cleanup in tests or when resetting application state.
        """
        self._subscribers.clear()

    def get_subscriber_count(self, event_type: type[E]) -> int:
        """Get the number of handlers subscribed to an event type.

        Args:
            event_type: The event class to check

        Returns:
            Number of subscribed handlers
        """
        return len(self._subscribers.get(event_type, []))
