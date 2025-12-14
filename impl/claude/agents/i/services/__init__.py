"""
Services layer for the kgents dashboard.

Provides decoupled communication patterns (EventBus), dependency injection
(DashboardServices), and other cross-cutting concerns.
"""

from .container import DashboardServices
from .events import (
    AgentFocusedEvent,
    Event,
    EventBus,
    FeverTriggeredEvent,
    LODChangedEvent,
    MetricsUpdatedEvent,
    ScreenNavigationEvent,
)

__all__ = [
    "Event",
    "EventBus",
    "ScreenNavigationEvent",
    "AgentFocusedEvent",
    "MetricsUpdatedEvent",
    "LODChangedEvent",
    "FeverTriggeredEvent",
    "DashboardServices",
]
