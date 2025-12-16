"""
Coalition Forge: No-code coalition assembly for agent tasks.

The Forge is the user-facing experience for:
1. Selecting tasks (from templates)
2. Watching coalition formation
3. Streaming dialogue
4. Receiving outputs

This module provides the visualization layer that makes coalition
dynamics visible and delightful.

Crown Jewel #2 in the Seven Jewel Crown.
See: plans/core-apps/coalition-forge.md

Wave 2 Synergy Integration:
- Coalition → Brain: Auto-capture task completions
- Brain → Coalition: Query relevant context before formation
- Coalition → Gardener: Bridge to session orchestration
"""

from agents.forge.synergy import (
    SynergyAwareForge,
    emit_coalition_formed,
    emit_task_complete,
    query_context_for_coalition,
    query_relevant_context,
)
from agents.forge.visualization import (
    BuilderEntry,
    CoalitionFormationView,
    DialogueMessage,
    DialogueSpeaker,
    DialogueState,
    DialogueStream,
    EigenvectorCompatibility,
    ForgeFormationState,
    ForgeVisualizationError,
    FormationEvent,
    FormationEventType,
    FormationStateError,
    HandoffAnimation,
    HandoffState,
    SubscriptionError,
    create_dialogue_stream,
    create_formation_view,
    create_handoff_animation,
    handle_coalition_subscribe,
    handle_dialogue_witness,
    project_dialogue_to_ascii,
    project_formation_to_ascii,
    project_handoff_to_ascii,
)

__all__ = [
    # Exceptions
    "ForgeVisualizationError",
    "FormationStateError",
    "SubscriptionError",
    # Event types
    "FormationEventType",
    "FormationEvent",
    "EigenvectorCompatibility",
    "BuilderEntry",
    # State types
    "ForgeFormationState",
    "DialogueSpeaker",
    "DialogueMessage",
    "DialogueState",
    "HandoffState",
    # Widgets
    "CoalitionFormationView",
    "DialogueStream",
    "HandoffAnimation",
    # ASCII projections
    "project_formation_to_ascii",
    "project_dialogue_to_ascii",
    "project_handoff_to_ascii",
    # AGENTESE handlers
    "handle_coalition_subscribe",
    "handle_dialogue_witness",
    # Factories
    "create_formation_view",
    "create_dialogue_stream",
    "create_handoff_animation",
    # Synergy (Wave 2: Brain integration)
    "emit_coalition_formed",
    "emit_task_complete",
    "query_relevant_context",
    "query_context_for_coalition",
    "SynergyAwareForge",
]
