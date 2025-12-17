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

from .base import (
    Base,
    CausalMixin,
    TimestampMixin,
    get_async_session,
    get_engine,
    init_db,
    close_db,
)

# Brain Crown Jewel
from .brain import Crystal, CrystalTag, BrainSettings

# Town Crown Jewel
from .town import Citizen, Conversation, ConversationTurn, CitizenRelationship

# Gardener Crown Jewel
from .gardener import (
    IdeaLifecycle,
    GardenSession,
    GardenIdea,
    GardenPlot,
    IdeaConnection,
)

# Gestalt Crown Jewel
from .gestalt import Topology, CodeBlock, CodeLink, TopologySnapshot

# Atelier Crown Jewel
from .atelier import Workshop, Artisan, Exhibition, GalleryItem, ArtifactContribution

# Coalition Crown Jewel
from .coalition import (
    Coalition,
    CoalitionMember,
    CoalitionProposal,
    ProposalVote,
    CoalitionOutput,
)

# Park Crown Jewel
from .park import Host, HostMemory, Episode, Interaction, ParkLocation

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
]
