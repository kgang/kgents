"""
Synergy Event Bus: Cross-jewel communication infrastructure.

Foundation 4 of the Enlightened Crown strategy.

The synergy system enables automatic data flow between jewels:
- Gestalt analysis → Brain captures architecture snapshot
- Gardener session complete → Brain captures learnings
- Coalition task complete → Brain captures results

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
    # Wave 0-1 factory functions
    create_analysis_complete_event,
    create_artifact_created_event,
    # Wave 2: Coalition factory functions
    create_coalition_formed_event,
    create_consensus_reached_event,
    create_contribution_posted_event,
    # Conversation factory functions (CLI v7 Phase 2)
    create_conversation_turn_event,
    create_crystal_formed_event,
    # Cursor/Presence factory functions (CLI v7 Phase 3)
    create_cursor_joined_event,
    create_cursor_left_event,
    create_cursor_updated_event,
    # Conductor factory functions (CLI v7 Phase 1)
    create_file_created_event,
    create_file_edited_event,
    create_file_read_event,
    create_flow_completed_event,
    # F-gent Flow factory functions (Phase 1)
    create_flow_started_event,
    create_hypothesis_created_event,
    create_hypothesis_synthesized_event,
    create_session_complete_event,
    create_swarm_a2a_message_event,
    create_swarm_despawned_event,
    create_swarm_handoff_event,
    # Swarm factory functions (CLI v7 Phase 6)
    create_swarm_spawned_event,
    create_task_complete_event,
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
    BrainToCoalitionHandler,
    CoalitionToBrainHandler,
    GestaltToBrainHandler,
    WitnessToBrainHandler,
)

__all__ = [
    # Event types
    "SynergyEventType",
    "Jewel",
    # Data classes
    "SynergyEvent",
    "SynergyResult",
    # Factory functions - Wave 0-1
    "create_analysis_complete_event",
    "create_crystal_formed_event",
    "create_session_complete_event",
    "create_artifact_created_event",
    # Factory functions - Wave 2: Coalition
    "create_coalition_formed_event",
    "create_task_complete_event",
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
    # Handlers - Wave 0-1
    "BaseSynergyHandler",
    "GestaltToBrainHandler",
    # Handlers - Wave 2
    "CoalitionToBrainHandler",
    "BrainToCoalitionHandler",
    # Handlers - Witness (8th Crown Jewel)
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
