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

Note: gestalt.py, coalition.py, park.py removed 2025-12-21.
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

# Town Crown Jewel
from .town import Citizen, CitizenRelationship, Conversation, ConversationTurn

# Trail Protocol
from .trail import (
    TrailRow,
    TrailStepRow,
    TrailAnnotationRow,
    TrailForkRow,
    TrailEvidenceRow,
    TrailCommitmentRow,
)

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
    # ASHC
    "VerifiedLemmaModel",
    # Trail
    "TrailRow",
    "TrailStepRow",
    "TrailAnnotationRow",
    "TrailForkRow",
    "TrailEvidenceRow",
    "TrailCommitmentRow",
]
