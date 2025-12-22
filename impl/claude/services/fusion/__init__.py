"""
Fusion Crown Jewel: Symmetric Supersession & Dialectical Synthesis.

The fusion service operationalizes the Symmetric Supersession doctrine:
- Kent and AI are symmetric agents
- Either can propose, either can be superseded
- Synthesis emerges from dialectical challenge
- The disgust veto is absolute

The Constitutional Model (from 2025-12-21-symmetric-supersession.md):
    ARTICLE I: SYMMETRIC AGENCY
        All agents in the system (Kent, AI) are modeled identically.
        No agent has intrinsic authority over another.
        Authority derives from quality of justification.

    ARTICLE IV: THE DISGUST VETO
        Kent's somatic disgust is an absolute veto.
        It cannot be argued away or evidence'd away.
        It is the ethical floor beneath which no decision may fall.

    ARTICLE VI: FUSION AS GOAL
        The goal is not Kent's decisions or AI's decisions.
        The goal is fused decisions better than either alone.
        Individual ego is dissolved into shared purpose.

Example usage:
    >>> from services.fusion import FusionService, Agent
    >>>
    >>> fusion = FusionService()
    >>> kent = fusion.propose("kent", "Use LangChain", "Scale and resources")
    >>> claude = fusion.propose("claude", "Build kgents", "Novel contribution")
    >>>
    >>> result = await fusion.simple_fuse(
    ...     kent, claude,
    ...     synthesis_content="Build minimal kernel, then decide",
    ...     synthesis_reasoning="Avoids both risks",
    ... )

See: brainstorming/2025-12-21-symmetric-supersession.md
See: brainstorming/2025-12-21-agent-as-witness.md
"""

from .engine import DialecticalEngine
from .node import FusionNode
from .service import FusionService
from .types import (
    Agent,
    Challenge,
    ChallengeId,
    FusionId,
    FusionResult,
    FusionStatus,
    Proposal,
    ProposalId,
    Synthesis,
    new_challenge_id,
    new_fusion_id,
    new_proposal_id,
)
from .veto import (
    DisgustSignal,
    DisgustVeto,
    VetoSource,
)

__all__ = [
    # Enums
    "Agent",
    "FusionStatus",
    "VetoSource",
    # Types
    "Challenge",
    "ChallengeId",
    "FusionId",
    "FusionResult",
    "Proposal",
    "ProposalId",
    "Synthesis",
    "DisgustSignal",
    # Factories
    "new_challenge_id",
    "new_fusion_id",
    "new_proposal_id",
    # Classes
    "DisgustVeto",
    "DialecticalEngine",
    "FusionService",
    "FusionNode",
]
