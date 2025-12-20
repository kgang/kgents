"""
Conductor Crown Jewel: Session orchestration for CLI v7.

The Conductor manages:
- ConversationWindow: Bounded history with context strategies
- Summarizer: LLM-powered context compression
- WindowPersistence: D-gent storage for window state
- Agent Presence: Visible cursor states and activity indicators
- Cursor Behaviors: Personality-driven agent movement (Phase 5B)
- Agent Swarms: Role-based multi-agent coordination (Phase 6)
- ConductorFlux: Cross-phase event integration (Phase 7)
- Session: Multi-turn collaborative sessions

Per CLI v7 Implementation Plan Phases 2, 3, 5B, 6, 7.

AGENTESE: self.conductor.*
"""

from __future__ import annotations

from .a2a import (
    A2AChannel,
    A2AMessage,
    A2AMessageType,
    A2ARegistry,
    A2ATopics,
    get_a2a_registry,
    reset_a2a_registry,
)
from .behaviors import (
    AGENTESEGraph,
    BehaviorAnimator,
    BehaviorModulator,
    CursorBehavior,
    FocusPoint,
    HumanFocusTracker,
    Position,
)
from .bus_bridge import (
    is_bridge_active,
    unwire_a2a_bridge,
    wire_a2a_to_global_synergy,
)

# Phase 7: Live Flux
from .flux import (
    ConductorEvent,
    ConductorEventSubscriber,
    ConductorEventType,
    ConductorFlux,
    get_conductor_flux,
    reset_conductor_flux,
    start_conductor_flux,
)
from .persistence import (
    WindowPersistence,
    get_window_persistence,
    reset_window_persistence,
)
from .presence import (
    AgentCursor,
    CircadianPhase,
    CursorState,
    PresenceChannel,
    PresenceEventType,
    PresenceUpdate,
    get_presence_channel,
    render_presence_footer,
    reset_presence_channel,
)
from .summarizer import (
    SummarizationResult,
    Summarizer,
    create_summarizer,
)

# Phase 6: Swarms
from .swarm import (
    COORDINATOR,
    IMPLEMENTER,
    PLANNER,
    RESEARCHER,
    REVIEWER,
    SpawnDecision,
    SpawnSignal,
    SwarmRole,
    SwarmSpawner,
    create_swarm_role,
)
from .window import (
    ContextMessage,
    ConversationWindow,
    WindowSnapshot,
    create_window_from_config,
)

__all__ = [
    # Window (Phase 2)
    "ConversationWindow",
    "ContextMessage",
    "WindowSnapshot",
    "create_window_from_config",
    # Summarizer (Phase 2)
    "Summarizer",
    "SummarizationResult",
    "create_summarizer",
    # Persistence (Phase 2)
    "WindowPersistence",
    "get_window_persistence",
    "reset_window_persistence",
    # Presence (Phase 3)
    "CursorState",
    "CircadianPhase",
    "AgentCursor",
    "PresenceEventType",
    "PresenceUpdate",
    "PresenceChannel",
    "get_presence_channel",
    "reset_presence_channel",
    "render_presence_footer",
    # Behaviors (Phase 5B)
    "CursorBehavior",
    "Position",
    "FocusPoint",
    "HumanFocusTracker",
    "AGENTESEGraph",
    "BehaviorAnimator",
    "BehaviorModulator",
    # Swarms (Phase 6)
    "SwarmRole",
    "SwarmSpawner",
    "SpawnSignal",
    "SpawnDecision",
    "RESEARCHER",
    "PLANNER",
    "IMPLEMENTER",
    "REVIEWER",
    "COORDINATOR",
    "create_swarm_role",
    # A2A (Phase 6)
    "A2AChannel",
    "A2AMessage",
    "A2AMessageType",
    "A2ATopics",
    "A2ARegistry",
    "get_a2a_registry",
    "reset_a2a_registry",
    # ConductorFlux (Phase 7)
    "ConductorFlux",
    "ConductorEvent",
    "ConductorEventType",
    "ConductorEventSubscriber",
    "get_conductor_flux",
    "reset_conductor_flux",
    "start_conductor_flux",
    # Bus Bridge (Phase 7)
    "wire_a2a_to_global_synergy",
    "unwire_a2a_bridge",
    "is_bridge_active",
]
