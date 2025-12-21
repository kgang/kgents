"""
Metabolism: The Developer Day as a Living System.

Checkpoints 0.3 and 2.1 of Metabolic Development Protocol.

Metabolism models the complete developer day as a state machine:
    DORMANT → GREETING (Coffee) → HYDRATED → WORKING → COMPOSTING → REFLECTING

Unlike isolated tools, Metabolism sees the day as an organism:
- Morning Coffee is the greeting phase (liminal transition)
- Hydration loads context from Brain + Living Docs
- Working captures patterns via Stigmergy
- Composting crystallizes learnings as gotchas
- Reflection closes the loop for next morning
- Background evidencing accumulates verification results (Checkpoint 2.1)

AGENTESE: time.metabolism.*
CLI: kg session *

See: spec/protocols/metabolic-development.md
"""

from .evidencing import (
    BackgroundEvidencing,
    CausalInsight,
    DiversityScore,
    EvidenceRun,
    InputSignature,
    StoredEvidence,
    get_background_evidencing,
    reset_background_evidencing,
    set_background_evidencing,
)
from .persistence import (
    CausalInsightRecord,
    MetabolismPersistence,
    StigmergyTraceRecord,
    StoredEvidenceRecord,
    get_metabolism_persistence,
    reset_metabolism_persistence,
    set_metabolism_persistence,
)
from .polynomial import (
    SESSION_POLYNOMIAL,
    session_directions,
    session_transition,
)
from .types import (
    CompostEntry,
    EnergyLevel,
    SessionEvent,
    SessionMetadata,
    SessionOutput,
    SessionState,
    WorkMode,
)

__all__ = [
    # State machine
    "SessionState",
    "SESSION_POLYNOMIAL",
    "session_directions",
    "session_transition",
    # Metadata
    "SessionMetadata",
    "WorkMode",
    "EnergyLevel",
    # Events and outputs
    "SessionEvent",
    "SessionOutput",
    "CompostEntry",
    # Background Evidencing (Checkpoint 2.1)
    "BackgroundEvidencing",
    "get_background_evidencing",
    "set_background_evidencing",
    "reset_background_evidencing",
    "InputSignature",
    "DiversityScore",
    "EvidenceRun",
    "StoredEvidence",
    "CausalInsight",
    # Persistence (Checkpoint 2.2)
    "MetabolismPersistence",
    "get_metabolism_persistence",
    "set_metabolism_persistence",
    "reset_metabolism_persistence",
    "StoredEvidenceRecord",
    "CausalInsightRecord",
    "StigmergyTraceRecord",
]
