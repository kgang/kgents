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
- gestalt.py: Topology, CodeBlock, CodeLink
- coalition.py: Coalition, CoalitionMember, CoalitionProposal
- park.py: Host, Memory, Episode, Interaction
"""

# ASHC Crown Jewel
from .ashc import VerifiedLemmaModel
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
    # Gestalt
    "Topology",
    "CodeBlock",
    "CodeLink",
    "TopologySnapshot",
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
