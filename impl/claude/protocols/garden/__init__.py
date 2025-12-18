"""
Garden Protocol: Next-Generation Planning System.

The Garden Protocol transforms planning from task-tracking to cultivation.
Key insight: The unit of planning is the session, not the plan file.

Core concepts:
- **Seasons**: SPROUTING → BLOOMING → FRUITING → COMPOSTING → DORMANT
- **Mood**: Emotional state (excited, curious, focused, stuck, dreaming...)
- **Letter**: Conversation with future self (replaces session_notes)
- **Resonates With**: Semantic connections (replaces blocking/enables)
- **Entropy**: Void budget tracking for serendipity

AGENTESE Paths:
- self.forest.plan.{name}.manifest - Plan view
- self.forest.plan.{name}.letter - Letter to future self
- self.forest.plan.{name}.tend - Update plan with gesture
- self.forest.plan.{name}.dream - Generate connections (dormant only)

See: spec/protocols/garden-protocol.md
"""

from .node import (
    # Node
    PLAN_AFFORDANCES,
    PlanNode,
    find_resonances,
    get_plan_node,
    # Helpers
    load_plan,
    save_plan,
)
from .operad import (
    # Operad
    GARDEN_OPERAD,
    # Types
    PlanState,
    create_garden_operad,
)
from .session import (
    # Affordances
    SESSION_AFFORDANCES,
    # Session State
    ActiveSession,
    # Node
    SessionNode,
    get_active_session,
    get_session_node,
    list_recent_sessions,
    # Persistence
    load_session,
    # Propagation
    propagate_session_to_plans,
    save_session,
    set_active_session,
)
from .sheaf import (
    CoherenceError,
    CompatibilityResult,
    # Sheaf
    GardenSheaf,
    # Types
    PlanView,
    ProjectView,
    # Convenience
    check_project_coherence,
)
from .types import (
    # Dataclasses
    EntropyBudget,
    EntropySip,
    GardenInput,
    GardenPlanHeader,
    # Polynomial
    GardenPolynomial,
    Gesture,
    GestureType,
    Mood,
    # Enums
    Season,
    SessionHeader,
    Trajectory,
    migrate_forest_to_garden,
    # Parser
    parse_garden_header,
)

__all__ = [
    # Enums
    "Season",
    "Trajectory",
    "Mood",
    "GardenInput",
    "GestureType",
    # Dataclasses
    "EntropyBudget",
    "EntropySip",
    "GardenPlanHeader",
    "Gesture",
    "SessionHeader",
    # Polynomial
    "GardenPolynomial",
    # Parser
    "parse_garden_header",
    "migrate_forest_to_garden",
    # PlanNode
    "PLAN_AFFORDANCES",
    "PlanNode",
    "get_plan_node",
    "load_plan",
    "save_plan",
    "find_resonances",
    # SessionNode
    "SESSION_AFFORDANCES",
    "SessionNode",
    "get_session_node",
    "ActiveSession",
    "get_active_session",
    "set_active_session",
    "load_session",
    "save_session",
    "list_recent_sessions",
    "propagate_session_to_plans",
    # Operad
    "PlanState",
    "GARDEN_OPERAD",
    "create_garden_operad",
    # Sheaf
    "PlanView",
    "ProjectView",
    "CoherenceError",
    "CompatibilityResult",
    "GardenSheaf",
    "check_project_coherence",
]
