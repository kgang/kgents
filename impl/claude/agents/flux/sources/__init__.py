"""
Flux Sources: Event-driven stream generators.

Sources provide the input streams for FluxAgents. The key insight is that
sources should be EVENT-DRIVEN, not TIMER-DRIVEN:

    # BAD: Timer-driven zombie
    async def heartbeat(interval):
        while True:
            yield time.time()
            await asyncio.sleep(interval)  # Polling!

    # GOOD: Event-driven life
    async def from_events(event_bus):
        async for event in event_bus.subscribe():
            yield event

The periodic() source exists for when you ACTUALLY need a timer,
but it should not be the default pattern.
"""

from .base import Source, SourceProtocol
from .events import empty, from_events, from_iterable, from_stream
from .merged import batched, debounced, filtered, mapped, merged, skip, take
from .outbox import MockConnection, MockConnectionPool, OutboxConfig, OutboxSource
from .periodic import countdown, periodic, tick

__all__ = [
    # Base
    "Source",
    "SourceProtocol",
    # Event-driven (preferred)
    "from_events",
    "from_stream",
    "from_iterable",
    "empty",
    # Timer-based (when needed)
    "periodic",
    "countdown",
    "tick",
    # Combinators
    "merged",
    "filtered",
    "mapped",
    "batched",
    "debounced",
    "take",
    "skip",
    # Database sources
    "OutboxSource",
    "OutboxConfig",
    "MockConnection",
    "MockConnectionPool",
]
