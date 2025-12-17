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
)

__all__ = [
    # Base infrastructure
    "Base",
    "TimestampMixin",
    "CausalMixin",
    "get_async_session",
    "get_engine",
    "init_db",
]
