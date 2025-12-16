"""
Synergy Event Bus: Cross-jewel communication infrastructure.

Foundation 4 of the Enlightened Crown strategy.

The synergy system enables automatic data flow between jewels:
- Gestalt analysis → Brain captures architecture snapshot
- Gardener session complete → Brain captures learnings
- Atelier piece created → Brain captures metadata

Usage:
    from protocols.synergy import get_synergy_bus, create_analysis_complete_event

    # Emit an event
    bus = get_synergy_bus()
    event = create_analysis_complete_event(
        source_id="analysis-123",
        module_count=50,
        health_grade="B+",
        average_health=0.84,
        drift_count=2,
        root_path="/path/to/project",
    )
    await bus.emit(event)

    # Subscribe to results for UI notifications
    def on_result(event, result):
        if result.success:
            print(f"Synergy: {result.message}")

    unsubscribe = bus.subscribe_results(on_result)

CLI Output:
    ✓ Gestalt analysis complete
    ↳ Synergy: Architecture snapshot captured to Brain
    ↳ Crystal: "gestalt-impl-claude-2025-12-16"
"""

from .bus import (
    ResultSubscriber,
    SynergyEventBus,
    SynergyHandler,
    get_synergy_bus,
    reset_synergy_bus,
)
from .events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    SynergyResult,
    create_analysis_complete_event,
    create_artifact_created_event,
    create_crystal_formed_event,
    create_session_complete_event,
)
from .handlers import BaseSynergyHandler, GestaltToBrainHandler

__all__ = [
    # Event types
    "SynergyEventType",
    "Jewel",
    # Data classes
    "SynergyEvent",
    "SynergyResult",
    # Factory functions
    "create_analysis_complete_event",
    "create_crystal_formed_event",
    "create_session_complete_event",
    "create_artifact_created_event",
    # Bus
    "SynergyEventBus",
    "SynergyHandler",
    "ResultSubscriber",
    "get_synergy_bus",
    "reset_synergy_bus",
    # Handlers
    "BaseSynergyHandler",
    "GestaltToBrainHandler",
]
