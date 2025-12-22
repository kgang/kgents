"""
Synergy Event Bus: Cross-jewel communication infrastructure.

Foundation 4 of the Enlightened Crown strategy.

The synergy system enables automatic data flow between jewels.
Note: Gestalt, Gardener, Coalition, Domain, Park removed 2025-12-21.

Usage:
    from protocols.synergy import get_synergy_bus, create_crystal_formed_event

    # Emit an event
    bus = get_synergy_bus()
    event = create_crystal_formed_event(
        crystal_id="crystal-123",
        content_preview="Sample content",
    )
    await bus.emit(event)

    # Subscribe to results for UI notifications
    def on_result(event, result):
        if result.success:
            print(f"Synergy: {result.message}")

    unsubscribe = bus.subscribe_results(on_result)
"""

from .bus import (
    ResultSubscriber,
    SynergyEventBus,
    SynergyHandler,
    get_synergy_bus,
    reset_synergy_bus,
)
from .cli_output import (
    ARROW,
    CRYSTAL_ICON,
    LINK_ICON,
    SynergyNotificationContext,
    create_notification_context,
    display_synergy_notification,
    display_synergy_results,
    format_crystal_reference,
    format_synergy_arrow,
    format_synergy_header,
)
from .events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    SynergyResult,
    create_consensus_reached_event,
    create_contribution_posted_event,
    # Conversation factory functions (CLI v7 Phase 2)
    create_conversation_turn_event,
    # Brain factory functions
    create_crystal_formed_event,
    # Cursor/Presence factory functions (CLI v7 Phase 3)
    create_cursor_joined_event,
    create_cursor_left_event,
    create_cursor_updated_event,
    # Conductor factory functions (CLI v7 Phase 1)
    create_file_created_event,
    create_file_edited_event,
    create_file_read_event,
    # F-gent Flow factory functions (Phase 1)
    create_flow_completed_event,
    create_flow_started_event,
    create_hypothesis_created_event,
    create_hypothesis_synthesized_event,
    # Swarm factory functions (CLI v7 Phase 6)
    create_swarm_a2a_message_event,
    create_swarm_despawned_event,
    create_swarm_handoff_event,
    create_swarm_spawned_event,
    create_turn_completed_event,
    # Witness factory functions (8th Crown Jewel)
    create_witness_daemon_started_event,
    create_witness_daemon_stopped_event,
    create_witness_git_commit_event,
    create_witness_git_push_event,
    create_witness_thought_event,
)
from .handlers import (
    BaseSynergyHandler,
    WitnessToBrainHandler,
)

__all__ = [
    # Event types
    "SynergyEventType",
    "Jewel",
    # Data classes
    "SynergyEvent",
    "SynergyResult",
    # Factory functions - Brain
    "create_crystal_formed_event",
    # Factory functions - F-gent Flow (Phase 1)
    "create_flow_started_event",
    "create_flow_completed_event",
    "create_turn_completed_event",
    "create_hypothesis_created_event",
    "create_hypothesis_synthesized_event",
    "create_consensus_reached_event",
    "create_contribution_posted_event",
    # Bus
    "SynergyEventBus",
    "SynergyHandler",
    "ResultSubscriber",
    "get_synergy_bus",
    "reset_synergy_bus",
    # Handlers
    "BaseSynergyHandler",
    "WitnessToBrainHandler",
    # Factory functions - Witness (8th Crown Jewel)
    "create_witness_thought_event",
    "create_witness_git_commit_event",
    "create_witness_git_push_event",
    "create_witness_daemon_started_event",
    "create_witness_daemon_stopped_event",
    # Factory functions - Conductor (CLI v7 Phase 1)
    "create_file_read_event",
    "create_file_edited_event",
    "create_file_created_event",
    # Factory functions - Conversation (CLI v7 Phase 2)
    "create_conversation_turn_event",
    # Factory functions - Swarm (CLI v7 Phase 6)
    "create_swarm_spawned_event",
    "create_swarm_despawned_event",
    "create_swarm_a2a_message_event",
    "create_swarm_handoff_event",
    # Factory functions - Cursor/Presence (CLI v7 Phase 3)
    "create_cursor_joined_event",
    "create_cursor_left_event",
    "create_cursor_updated_event",
    # CLI Output (Wave 2: UI Integration)
    "display_synergy_notification",
    "display_synergy_results",
    "SynergyNotificationContext",
    "create_notification_context",
    "format_synergy_header",
    "format_crystal_reference",
    "format_synergy_arrow",
    "ARROW",
    "LINK_ICON",
    "CRYSTAL_ICON",
]
