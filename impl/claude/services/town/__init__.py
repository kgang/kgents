"""
Town Crown Jewel: Agent Simulation Westworld.

Agent Town is a multi-agent simulation where citizens have polynomial state,
form coalitions, and engage in emergent dialogue.

AGENTESE Paths:
- world.town.manifest             - Show town status
- world.town.citizen.list         - List all citizens
- world.town.citizen.get          - Get citizen by ID or name
- world.town.citizen.create       - Create new citizen
- world.town.citizen.update       - Update citizen attributes
- world.town.converse             - Start conversation with citizen
- world.town.turn                 - Add turn to conversation
- world.town.history              - Get dialogue history
- world.town.relationships        - Get citizen relationships
- world.town.gossip               - Inter-citizen dialogue stream
- world.town.inhabit.manifest     - Show INHABIT session status
- world.town.inhabit.start        - Start INHABIT session
- world.town.inhabit.suggest      - Suggest action (collaborative)
- world.town.inhabit.force        - Force action (consent debt)
- world.town.inhabit.apologize    - Reduce consent debt
- world.town.inhabit.end          - End session gracefully
- world.town.workshop.manifest    - Show workshop status
- world.town.workshop.assign      - Assign task to builders
- world.town.workshop.advance     - Advance workshop one step
- world.town.workshop.complete    - Complete current task
- world.town.workshop.builders    - List available builders
- world.town.coalition.manifest   - Coalition system overview
- world.town.coalition.list       - List all coalitions
- world.town.coalition.get        - Get coalition by ID
- world.town.coalition.detect     - Detect coalitions via k-clique percolation
- world.town.coalition.bridges    - Get bridge citizens
- world.town.coalition.decay      - Apply decay to coalitions
- world.town.collective.*         - Town collective memory

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
- coalition_node.py     - AGENTESE node for Coalition (@node decorator)
- workshop_service.py   - Builder coordination (task execution flow)
- workshop_node.py      - AGENTESE node for Workshop (@node decorator)

See: docs/skills/metaphysical-fullstack.md
"""

from .budget_service import (
    SUBSCRIPTION_TIERS,
    BudgetStore,
    ConsentState,
    InMemoryBudgetStore,
    RedisBudgetStore,
    SubscriptionTier,
    UserBudgetInfo,
    create_budget_store,
)
from .coalition_node import (
    CoalitionListRendering,
    CoalitionManifestRendering,
    CoalitionNode,
    CoalitionRendering,
)
from .coalition_service import (
    Coalition,
    CoalitionService,
    ReputationGraph,
    detect_coalitions,
    find_k_cliques,
    percolate_cliques,
)
from .dialogue_service import (
    ARCHETYPE_SYSTEM_PROMPTS,
    TEMPLATE_DIALOGUES,
    CitizenBudget,
    DialogueBudgetConfig,
    DialogueContext,
    DialogueResult,
    DialogueService,
    DialogueTier,
    create_dialogue_service,
)
from .inhabit_node import (
    InhabitActionRendering,
    InhabitListRendering,
    InhabitNode,
    InhabitSessionRendering,
)
from .inhabit_service import (
    AlignmentScore,
    InhabitResponse,
    InhabitService,
    InhabitSession,
    InhabitTier,
    calculate_alignment,
    generate_inner_voice,
)
from .memory_service import (
    CollectiveEvent,
    ConversationEntry,
    PersistentCitizenMemory,
    TownCollectiveMemory,
    create_collective_memory,
    create_persistent_memory,
    save_citizen_state,
)
from .node import (
    CitizenListRendering,
    CitizenRendering,
    ConversationRendering,
    RelationshipListRendering,
    TownManifestRendering,
    TownNode,
)
from .persistence import (
    CitizenView,
    ConversationView,
    RelationshipView,
    TownPersistence,
    TownStatus,
    TurnView,
)
from .workshop_node import (
    WorkshopBuildersRendering,
    WorkshopManifestRendering,
    WorkshopNode,
)
from .workshop_service import (
    WorkshopEventView,
    WorkshopFluxView,
    WorkshopPlanView,
    WorkshopService,
    WorkshopTaskView,
    WorkshopView,
    create_workshop_service,
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
    # Coalition Node
    "CoalitionNode",
    "CoalitionManifestRendering",
    "CoalitionRendering",
    "CoalitionListRendering",
    # Workshop Service
    "WorkshopService",
    "create_workshop_service",
    "WorkshopView",
    "WorkshopTaskView",
    "WorkshopPlanView",
    "WorkshopEventView",
    "WorkshopFluxView",
    # Workshop Node
    "WorkshopNode",
    "WorkshopManifestRendering",
    "WorkshopBuildersRendering",
]
