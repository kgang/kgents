"""
SQLAlchemy ORM Models for kgents Application State.

Part of the Dual-Track Architecture:
- D-gent Track: Agent memory (schema-free, append-only, lenses)
- Alembic Track: Application state (typed models, migrations, foreign keys)

The TableAdapter bridges these tracks via DgentProtocol interface.

AGENTESE: self.data.table.*

Crown Jewel Tables:
- brain.py: Crystal, Tag, BrainSettings
- town.py: Citizen, Conversation, ConversationTurn
- gardener.py: GardenIdea, GardenSession, GardenPlot
- gestalt.py: Topology, CodeBlock, CodeLink
- atelier.py: Workshop, Exhibition, Artisan, Gallery
- coalition.py: Coalition, CoalitionMember, CoalitionProposal
- park.py: Host, Memory, Episode, Interaction
"""

# Atelier Crown Jewel
# ASHC Crown Jewel
from .ashc import VerifiedLemmaModel
from .atelier import ArtifactContribution, Artisan, Exhibition, GalleryItem, Workshop
from .base import (
    Base,
    CausalMixin,
    TimestampMixin,
    close_db,
    get_async_session,
    get_engine,
    init_db,
)

# Brain Crown Jewel
from .brain import (
    BrainSettings,
    Crystal,
    CrystalTag,
    ExtinctionEvent,
    ExtinctionTeaching,
    TeachingCrystal,
)

# Coalition Crown Jewel
from .coalition import (
    Coalition,
    CoalitionMember,
    CoalitionOutput,
    CoalitionProposal,
    ProposalVote,
)

# Gardener Crown Jewel
from .gardener import (
    GardenIdea,
    GardenPlot,
    GardenSession,
    IdeaConnection,
    IdeaLifecycle,
)

# Gestalt Crown Jewel
from .gestalt import CodeBlock, CodeLink, Topology, TopologySnapshot

# Park Crown Jewel
from .park import Episode, Host, HostMemory, Interaction, ParkLocation

# Town Crown Jewel
from .town import Citizen, CitizenRelationship, Conversation, ConversationTurn

__all__ = [
    # Base infrastructure
    "Base",
    "TimestampMixin",
    "CausalMixin",
    "get_async_session",
    "get_engine",
    "init_db",
    "close_db",
    # Brain
    "Crystal",
    "CrystalTag",
    "BrainSettings",
    "TeachingCrystal",
    "ExtinctionEvent",
    "ExtinctionTeaching",
    # Town
    "Citizen",
    "Conversation",
    "ConversationTurn",
    "CitizenRelationship",
    # Gardener
    "IdeaLifecycle",
    "GardenSession",
    "GardenIdea",
    "GardenPlot",
    "IdeaConnection",
    # Gestalt
    "Topology",
    "CodeBlock",
    "CodeLink",
    "TopologySnapshot",
    # Atelier
    "Workshop",
    "Artisan",
    "Exhibition",
    "GalleryItem",
    "ArtifactContribution",
    # Coalition
    "Coalition",
    "CoalitionMember",
    "CoalitionProposal",
    "ProposalVote",
    "CoalitionOutput",
    # Park
    "Host",
    "HostMemory",
    "Episode",
    "Interaction",
    "ParkLocation",
    # ASHC
    "VerifiedLemmaModel",
]
