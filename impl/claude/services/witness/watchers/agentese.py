"""
AgenteseWatcher: Event-Driven Cross-Jewel Visibility.

Subscribes to WitnessSynergyBus to observe AGENTESE invocations
from all Crown Jewels (Town, Brain, Park, etc.).

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

Integration:
- Subscribes to WitnessSynergyBus with wildcard patterns
- Parses AGENTESE paths: world.town.citizen.create → (path, aspect, jewel)
- Emits AgenteseEvent to WitnessPolynomial for processing

Usage:
    from services.witness.bus import get_witness_synergy_bus
    bus = get_witness_synergy_bus()
    watcher = AgenteseWatcher(bus)

    async for event in watcher.watch():
        print(f"AGENTESE: {event.path} → {event.aspect}")

See: docs/skills/agentese-path.md
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from queue import Empty, Queue
from typing import TYPE_CHECKING, Any

from services.witness.polynomial import AgenteseEvent
from services.witness.watchers.base import BaseWatcher

if TYPE_CHECKING:
    from services.witness.bus import WitnessSynergyBus

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class AgenteseConfig:
    """Configuration for AgenteseWatcher."""

    # Topic patterns to subscribe to (wildcards supported)
    topic_patterns: tuple[str, ...] = (
        "world.*",
        "self.*",
        "concept.*",
        "void.*",
        "time.*",
    )

    # Jewel name extraction patterns
    # Maps topic prefix → jewel name
    jewel_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "world.town": "Town",
            "world.park": "Park",
            "world.atelier": "Atelier",
            "self.memory": "Brain",
            "self.soul": "K-gent",
            "concept.design": "Gestalt",
        }
    )


# =============================================================================
# AGENTESE Path Parser
# =============================================================================


def parse_agentese_path(topic: str) -> tuple[str, str, str | None]:
    """
    Parse an AGENTESE topic into (path, aspect, jewel).

    Examples:
        "world.town.citizen.create" → ("world.town.citizen", "create", "Town")
        "self.memory.capture" → ("self.memory", "capture", "Brain")
        "unknown.path.action" → ("unknown.path", "action", None)

    Returns:
        (path, aspect, jewel) tuple
    """
    parts = topic.split(".")

    if len(parts) < 2:
        return (topic, "unknown", None)

    # Last part is typically the aspect (verb)
    aspect = parts[-1]
    path = ".".join(parts[:-1])

    # Try to determine jewel from prefix
    jewel = None
    for prefix, jewel_name in AgenteseConfig().jewel_mapping.items():
        if topic.startswith(prefix):
            jewel = jewel_name
            break

    return (path, aspect, jewel)


def parse_agentese_path_with_config(
    topic: str, config: AgenteseConfig
) -> tuple[str, str, str | None]:
    """Parse with custom config (for testing)."""
    parts = topic.split(".")

    if len(parts) < 2:
        return (topic, "unknown", None)

    aspect = parts[-1]
    path = ".".join(parts[:-1])

    jewel = None
    for prefix, jewel_name in config.jewel_mapping.items():
        if topic.startswith(prefix):
            jewel = jewel_name
            break

    return (path, aspect, jewel)


# =============================================================================
# AgenteseWatcher
# =============================================================================


class AgenteseWatcher(BaseWatcher[AgenteseEvent]):
    """
    Event-driven AGENTESE watcher.

    Subscribes to WitnessSynergyBus and converts cross-jewel events
    to AgenteseEvent for the witness polynomial.

    This provides visibility into all AGENTESE invocations across
    the kgents system.

    Usage:
        from services.witness.bus import get_witness_synergy_bus

        bus = get_witness_synergy_bus()
        watcher = AgenteseWatcher(bus)
        watcher.add_handler(lambda e: print(f"Saw: {e.path}"))
        await watcher.start()
    """

    def __init__(
        self,
        bus: "WitnessSynergyBus | None" = None,
        config: AgenteseConfig | None = None,
    ) -> None:
        super().__init__()
        self._bus = bus
        self.config = config or AgenteseConfig()

        # Event queue (async-safe)
        self._queue: Queue[AgenteseEvent] = Queue()

        # Track unsubscribe functions for cleanup
        self._unsubscribes: list[callable] = []

    async def _on_start(self) -> None:
        """Subscribe to SynergyBus topics."""
        if self._bus is None:
            # Try to get the global bus
            try:
                from services.witness.bus import get_witness_synergy_bus

                self._bus = get_witness_synergy_bus()
            except Exception as e:
                logger.warning(f"Could not get global SynergyBus: {e}")
                return

        # Subscribe to configured topic patterns
        for pattern in self.config.topic_patterns:
            unsub = self._bus.subscribe(pattern, self._handle_event)
            self._unsubscribes.append(unsub)

        logger.info(f"AgenteseWatcher subscribed to {len(self.config.topic_patterns)} patterns")

    async def _handle_event(self, topic: str, event: Any) -> None:
        """Handle incoming SynergyBus event."""
        try:
            # Parse the topic
            path, aspect, jewel = parse_agentese_path_with_config(topic, self.config)

            # Create AgenteseEvent
            agentese_event = AgenteseEvent(
                path=path,
                aspect=aspect,
                jewel=jewel,
            )

            # Queue for emission (thread-safe)
            self._queue.put(agentese_event)

        except Exception as e:
            logger.warning(f"Error handling AGENTESE event {topic}: {e}")
            self.stats.record_error()

    async def _watch_loop(self) -> None:
        """Main watch loop - drain queue and emit events."""
        while not self._stop_event.is_set():
            # Drain queue (non-blocking)
            while True:
                try:
                    event = self._queue.get_nowait()
                    self._emit(event)
                except Empty:
                    break

            # Small sleep to prevent busy loop
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=0.1,  # Check queue every 100ms
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue watching

    async def _cleanup(self) -> None:
        """Unsubscribe from all topics."""
        for unsub in self._unsubscribes:
            try:
                unsub()
            except Exception as e:
                logger.debug(f"Error during unsubscribe: {e}")

        self._unsubscribes.clear()
        logger.info("AgenteseWatcher stopped")


# =============================================================================
# Factory Functions
# =============================================================================


def create_agentese_watcher(
    bus: "WitnessSynergyBus | None" = None,
    patterns: tuple[str, ...] | None = None,
) -> AgenteseWatcher:
    """Create a configured AGENTESE watcher."""
    config = AgenteseConfig()
    if patterns:
        config = AgenteseConfig(topic_patterns=patterns)

    return AgenteseWatcher(bus=bus, config=config)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AgenteseWatcher",
    "AgenteseConfig",
    "parse_agentese_path",
    "parse_agentese_path_with_config",
    "create_agentese_watcher",
]
