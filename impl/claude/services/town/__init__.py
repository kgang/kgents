"""
Town Crown Jewel: Agent Simulation Westworld.

Agent Town is a multi-agent simulation where citizens have polynomial state,
form coalitions, and engage in emergent dialogue.

AGENTESE Paths:
- world.town.manifest           - Show town status
- world.town.citizen.list       - List all citizens
- world.town.citizen.get        - Get citizen by ID or name
- world.town.citizen.create     - Create new citizen
- world.town.citizen.update     - Update citizen attributes
- world.town.converse           - Start conversation with citizen
- world.town.turn               - Add turn to conversation
- world.town.history            - Get dialogue history
- world.town.relationships      - Get citizen relationships
- world.town.gossip             - Inter-citizen dialogue stream
- world.town.inhabit.manifest   - Show INHABIT session status
- world.town.inhabit.start      - Start INHABIT session
- world.town.inhabit.suggest    - Suggest action (collaborative)
- world.town.inhabit.force      - Force action (consent debt)
- world.town.inhabit.apologize  - Reduce consent debt
- world.town.inhabit.end        - End session gracefully
- world.town.collective.*       - Town collective memory

Dual-Track Storage:
- SQLAlchemy tables (models/town.py) - Citizen state, relations, coalitions
- D-gent datums - Dialogue history, semantic memory

Services (Metaphysical Fullstack AD-009):
- persistence.py        - TableAdapter + D-gent for entities
- memory_service.py     - Citizen/collective episodic memory
- budget_service.py     - Credits, subscriptions, consent tracking
- inhabit_service.py    - INHABIT mode session management
- inhabit_node.py       - AGENTESE node for INHABIT (@node decorator)
- dialogue_service.py   - LLM-backed dialogue generation
- coalition_service.py  - k-clique coalition detection, EigenTrust reputation
- workshop_service.py   - Builder coordination (task execution flow)

See: docs/skills/metaphysical-fullstack.md
"""

from .persistence import (
    CitizenView,
    ConversationView,
    RelationshipView,
    TownPersistence,
    TownStatus,
    TurnView,
)
from .node import (
    TownNode,
    TownManifestRendering,
    CitizenRendering,
    CitizenListRendering,
    ConversationRendering,
    RelationshipListRendering,
)
from .inhabit_node import (
    InhabitNode,
    InhabitSessionRendering,
    InhabitActionRendering,
    InhabitListRendering,
)
from .memory_service import (
    ConversationEntry,
    PersistentCitizenMemory,
    CollectiveEvent,
    TownCollectiveMemory,
    create_persistent_memory,
    create_collective_memory,
    save_citizen_state,
)
from .budget_service import (
    BudgetStore,
    ConsentState,
    InMemoryBudgetStore,
    RedisBudgetStore,
    SubscriptionTier,
    SUBSCRIPTION_TIERS,
    UserBudgetInfo,
    create_budget_store,
)
from .inhabit_service import (
    InhabitTier,
    InhabitSession,
    InhabitResponse,
    AlignmentScore,
    InhabitService,
    calculate_alignment,
    generate_inner_voice,
)
from .dialogue_service import (
    DialogueTier,
    DialogueContext,
    DialogueResult,
    CitizenBudget,
    DialogueBudgetConfig,
    DialogueService,
    create_dialogue_service,
    ARCHETYPE_SYSTEM_PROMPTS,
    TEMPLATE_DIALOGUES,
)
from .coalition_service import (
    Coalition,
    ReputationGraph,
    find_k_cliques,
    percolate_cliques,
    detect_coalitions,
    CoalitionService,
)
from .workshop_service import (
    WorkshopService,
    create_workshop_service,
    WorkshopView,
    WorkshopTaskView,
    WorkshopPlanView,
    WorkshopEventView,
    WorkshopFluxView,
)

__all__ = [
    # Persistence
    "TownPersistence",
    "TownStatus",
    "CitizenView",
    "ConversationView",
    "TurnView",
    "RelationshipView",
    # AGENTESE Nodes
    "TownNode",
    "TownManifestRendering",
    "CitizenRendering",
    "CitizenListRendering",
    "ConversationRendering",
    "RelationshipListRendering",
    # INHABIT Node
    "InhabitNode",
    "InhabitSessionRendering",
    "InhabitActionRendering",
    "InhabitListRendering",
    # Memory Service
    "ConversationEntry",
    "PersistentCitizenMemory",
    "CollectiveEvent",
    "TownCollectiveMemory",
    "create_persistent_memory",
    "create_collective_memory",
    "save_citizen_state",
    # Budget Service
    "BudgetStore",
    "ConsentState",
    "InMemoryBudgetStore",
    "RedisBudgetStore",
    "SubscriptionTier",
    "SUBSCRIPTION_TIERS",
    "UserBudgetInfo",
    "create_budget_store",
    # INHABIT Service
    "InhabitTier",
    "InhabitSession",
    "InhabitResponse",
    "AlignmentScore",
    "InhabitService",
    "calculate_alignment",
    "generate_inner_voice",
    # Dialogue Service
    "DialogueTier",
    "DialogueContext",
    "DialogueResult",
    "CitizenBudget",
    "DialogueBudgetConfig",
    "DialogueService",
    "create_dialogue_service",
    "ARCHETYPE_SYSTEM_PROMPTS",
    "TEMPLATE_DIALOGUES",
    # Coalition Service
    "Coalition",
    "ReputationGraph",
    "find_k_cliques",
    "percolate_cliques",
    "detect_coalitions",
    "CoalitionService",
    # Workshop Service
    "WorkshopService",
    "create_workshop_service",
    "WorkshopView",
    "WorkshopTaskView",
    "WorkshopPlanView",
    "WorkshopEventView",
    "WorkshopFluxView",
]
