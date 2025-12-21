"""
Bus Bridge: Cross-bus event forwarding for CLI v7 Phase 7 (Live Flux).

This module bridges events between the WitnessSynergyBus (used by A2A)
and the global SynergyBus (used for cross-jewel coordination).

The bridge enables:
- A2A messages visible in the global event stream
- Swarm activity tracked across all Crown Jewels
- Real-time updates for CLI/Web/Canvas

Architecture:
    WitnessSynergyBus (a2a.*)  ──bridge──>  Global SynergyBus
           │                                      │
           │                                      ▼
           │                              EventBus (fan-out)
           ▼                                      │
    A2AChannel receive                    CLI/TUI/Web/Canvas

Teaching:
    gotcha: wire_a2a_to_global_synergy() is idempotent - calling it twice
            returns the SAME unsubscribe function. This prevents duplicate
            bridging but means you cannot create multiple independent bridges.
            (Evidence: test_bus_bridge.py::TestBusBridgeLifecycle::test_double_wire_is_idempotent)

    gotcha: Malformed A2A events do NOT crash the bridge - graceful degradation.
            Missing fields like from_agent/to_agent are replaced with "unknown".
            The bridge continues processing after errors, so a bad event won't
            break the entire A2A visibility pipeline.
            (Evidence: test_bus_bridge.py::TestBridgeErrorHandling::test_malformed_event_doesnt_crash_bridge)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from protocols.synergy import (
    SynergyEventType,
    create_swarm_a2a_message_event,
    create_swarm_handoff_event,
    get_synergy_bus,
)
from services.witness.bus import get_synergy_bus as get_witness_bus

logger = logging.getLogger("kgents.conductor.bus_bridge")

# Unsubscribe handle
_bridge_unsubscribe: Callable[[], None] | None = None


def wire_a2a_to_global_synergy() -> Callable[[], None]:
    """
    Bridge A2A events from WitnessSynergyBus to global SynergyBus.

    This enables cross-jewel visibility of swarm A2A communication.

    Returns:
        Unsubscribe function to stop bridging.

    Usage:
        unsubscribe = wire_a2a_to_global_synergy()
        # ... later ...
        unsubscribe()  # Stop bridging
    """
    global _bridge_unsubscribe

    if _bridge_unsubscribe is not None:
        logger.debug("A2A bridge already wired, skipping")
        return _bridge_unsubscribe

    witness_bus = get_witness_bus()
    global_bus = get_synergy_bus()

    async def bridge_a2a(topic: str, event: dict[str, Any]) -> None:
        """Bridge A2A events to global SynergyBus."""
        if not topic.startswith("a2a."):
            return

        try:
            # Determine event type from topic
            if topic == "a2a.handoff":
                synergy_event = create_swarm_handoff_event(
                    handoff_id=event.get("message_id", str(uuid.uuid4())),
                    from_agent=event.get("from_agent", "unknown"),
                    to_agent=event.get("to_agent", "unknown"),
                    context_keys=list(event.get("payload", {}).keys()),
                    conversation_turns=len(event.get("conversation_context", [])),
                )
            else:
                # Generic A2A message
                synergy_event = create_swarm_a2a_message_event(
                    message_id=event.get("message_id", str(uuid.uuid4())),
                    from_agent=event.get("from_agent", "unknown"),
                    to_agent=event.get("to_agent", "*"),
                    message_type=event.get("message_type", "NOTIFY"),
                    payload_preview=str(event.get("payload", {}))[:100],
                )

            # Fire and forget to global bus
            await global_bus.emit(synergy_event)
            logger.debug(f"Bridged A2A event: {topic} -> {synergy_event.event_type.value}")

        except Exception as e:
            # Log but don't fail - graceful degradation
            logger.warning(f"Failed to bridge A2A event: {e}")

    # Subscribe to all a2a.* topics
    unsubscribe = witness_bus.subscribe("a2a.*", bridge_a2a)
    _bridge_unsubscribe = unsubscribe

    logger.info("A2A → Global SynergyBus bridge wired")
    return unsubscribe


def unwire_a2a_bridge() -> None:
    """Stop the A2A bridge."""
    global _bridge_unsubscribe
    if _bridge_unsubscribe is not None:
        _bridge_unsubscribe()
        _bridge_unsubscribe = None
        logger.info("A2A → Global SynergyBus bridge unwired")


def is_bridge_active() -> bool:
    """Check if the A2A bridge is currently active."""
    return _bridge_unsubscribe is not None


__all__ = [
    "wire_a2a_to_global_synergy",
    "unwire_a2a_bridge",
    "is_bridge_active",
]
