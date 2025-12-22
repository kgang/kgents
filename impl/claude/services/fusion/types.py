"""
Symmetric Supersession Types: Core dataclasses for dialectical fusion.

The Radical Insight (from 2025-12-21-symmetric-supersession.md):
    Kent and AI are symmetric agents in the system. The system can supersede
    Kent's decisions when it has good proofs, sound arguments, and sufficient
    evidence—but the disgust veto is absolute.

Philosophy:
    "The system should supersede Kent in his decision-making because Kent
    allows it to do so—because it has good proofs, arguments, and evidence
    (and it doesn't disgust him)."

The Symmetric Model:
    - Kent = Agent in the system (generates decisions, leaves traces, can be modeled)
    - AI = Agent in the system (generates decisions, leaves traces, can be modeled)
    - System = The fusion of both, operating on both
    - Flow = Either can propose → Either can be superseded → Fusion emerges

See: brainstorming/2025-12-21-symmetric-supersession.md
See: brainstorming/2025-12-21-agent-as-witness.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import NewType

# =============================================================================
# Type Aliases
# =============================================================================

ProposalId = NewType("ProposalId", str)
ChallengeId = NewType("ChallengeId", str)
FusionId = NewType("FusionId", str)


def new_proposal_id() -> ProposalId:
    """Generate a unique Proposal ID."""
    return ProposalId(f"prop-{uuid.uuid4().hex[:8]}")


def new_challenge_id() -> ChallengeId:
    """Generate a unique Challenge ID."""
    return ChallengeId(f"chal-{uuid.uuid4().hex[:8]}")


def new_fusion_id() -> FusionId:
    """Generate a unique Fusion ID."""
    return FusionId(f"fuse-{uuid.uuid4().hex[:8]}")


# =============================================================================
# Agent Enum
# =============================================================================


class Agent(Enum):
    """
    The symmetric agents in the system.

    The key insight: Kent and Claude are modeled identically.
    No agent has intrinsic authority over another.
    Authority derives from quality of justification.
    """

    KENT = "kent"  # The human principal
    CLAUDE = "claude"  # The AI agent
    KGENT = "k-gent"  # Digital soul (Kent's externalized preferences)
    SYSTEM = "system"  # Emergent fusion of agents


class FusionStatus(Enum):
    """
    Status of a fusion attempt.

    The dialectical process can result in:
    - SYNTHESIZED: Genuine fusion emerged
    - VETOED: Kent's disgust veto applied
    - IMPASSE: No synthesis possible after max rounds
    - IN_PROGRESS: Still in dialectical arena
    """

    IN_PROGRESS = "in_progress"
    SYNTHESIZED = "synthesized"
    VETOED = "vetoed"
    IMPASSE = "impasse"


# =============================================================================
# Proposal: Symmetric decision unit
# =============================================================================


@dataclass(frozen=True)
class Proposal:
    """
    A proposed decision from any agent.

    Proposals are symmetric: Kent's proposals have the same
    structure as Claude's proposals. This is not metaphor—it's architecture.

    The Isomorphism:
        - Both generate decisions
        - Both leave traces
        - Both can be modeled (imperfectly)
        - Both have opacity (consciousness / weights)
        - Both can be superseded (conditionally)

    Example:
        >>> kent = Proposal.create(
        ...     agent="kent",
        ...     content="Use LangChain",
        ...     reasoning="Scale, resources, production validation",
        ...     principles=["pragmatic"],
        ... )
        >>> claude = Proposal.create(
        ...     agent="claude",
        ...     content="Build kgents",
        ...     reasoning="Novel contribution, aligned with soul",
        ...     principles=["tasteful", "generative", "joy-inducing"],
        ... )
    """

    id: ProposalId
    agent: Agent
    content: str  # What is proposed
    reasoning: str  # Why this proposal
    principles: tuple[str, ...] = ()  # Which principles support this
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        agent: Agent | str,
        content: str,
        reasoning: str,
        principles: list[str] | None = None,
    ) -> Proposal:
        """Factory for creating proposals."""
        if isinstance(agent, str):
            agent = Agent(agent)
        return cls(
            id=new_proposal_id(),
            agent=agent,
            content=content,
            reasoning=reasoning,
            principles=tuple(principles or []),
        )


# =============================================================================
# Challenge: Dialectical opposition
# =============================================================================


@dataclass(frozen=True)
class Challenge:
    """
    A challenge to a proposal.

    Challenges are how agents sharpen each other. The adversarial
    structure forces:
        - Kent to articulate his reasoning (making implicit explicit)
        - AI to defend its proposals (evidence over assertion)
        - Both to update on each other's challenges
        - Neither to rest in comfortable agreement

    The adversarialism is nominative (structural) not substantive (hostile).
    Purpose is fusion, not victory.

    Example:
        >>> challenge = Challenge.create(
        ...     challenger="claude",
        ...     target_proposal=kent_proposal.id,
        ...     content="LangChain optimizes for scale, but kgents offers novel insight",
        ... )
    """

    id: ChallengeId
    challenger: Agent  # Who is challenging
    target_proposal: ProposalId  # What is being challenged
    content: str  # The challenge itself
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        challenger: Agent | str,
        target_proposal: ProposalId,
        content: str,
    ) -> Challenge:
        """Factory for creating challenges."""
        if isinstance(challenger, str):
            challenger = Agent(challenger)
        return cls(
            id=new_challenge_id(),
            challenger=challenger,
            target_proposal=target_proposal,
            content=content,
        )


# =============================================================================
# Synthesis: Emergent fusion
# =============================================================================


@dataclass(frozen=True)
class Synthesis:
    """
    The emergent fusion of proposals after dialectic.

    Synthesis transcends both original proposals. Properties:
        - Transcends both original proposals
        - Incorporates challenges from both sides
        - Has richer justification than either alone
        - Is more robust (survived adversarial testing)
        - Belongs to neither Kent nor AI (belongs to fusion)

    True fusion means the synthesis differs from both originals.
    If synthesis == original_kent or synthesis == original_ai,
    that's convergence, not fusion.

    Example:
        >>> synthesis = Synthesis(
        ...     content="Build minimal kernel, validate, then decide. LangChain is fallback.",
        ...     reasoning="Avoids philosophy without validation AND abandoning ideas untested",
        ...     incorporates_from_a="Validation and fallback option",
        ...     incorporates_from_b="Novel ideas worth testing",
        ...     transcends="Neither pure philosophy nor pure pragmatism",
        ... )
    """

    content: str  # What emerged
    reasoning: str  # Why this synthesis
    incorporates_from_a: str | None = None  # What was taken from proposal A
    incorporates_from_b: str | None = None  # What was taken from proposal B
    transcends: str | None = None  # What is new beyond both


# =============================================================================
# FusionResult: Complete dialectic record
# =============================================================================


@dataclass
class FusionResult:
    """
    Complete record of a dialectical fusion attempt.

    This is the output of the DialecticalEngine. It captures:
        - Original proposals from both agents
        - The dialectical trace (challenges exchanged)
        - The outcome (synthesis, veto, or impasse)
        - Metadata for learning and review

    Example:
        >>> result = FusionResult(
        ...     id=new_fusion_id(),
        ...     status=FusionStatus.SYNTHESIZED,
        ...     proposal_a=kent_proposal,
        ...     proposal_b=claude_proposal,
        ...     synthesis=synthesis,
        ... )
    """

    id: FusionId
    status: FusionStatus

    # Original proposals
    proposal_a: Proposal
    proposal_b: Proposal

    # The dialectical trace
    challenges: list[Challenge] = field(default_factory=list)

    # The outcome
    synthesis: Synthesis | None = None
    veto_reason: str | None = None

    # Metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    @property
    def trace(self) -> list[Challenge]:
        """Alias for challenges for API compatibility."""
        return self.challenges

    @property
    def is_genuine_fusion(self) -> bool:
        """
        True fusion means the synthesis differs from both originals.

        If synthesis content matches either proposal, that's
        convergence, not fusion.
        """
        if self.synthesis is None:
            return False
        return (
            self.synthesis.content != self.proposal_a.content
            and self.synthesis.content != self.proposal_b.content
        )

    def complete(self, synthesis: Synthesis) -> FusionResult:
        """Mark fusion as complete with synthesis."""
        self.status = FusionStatus.SYNTHESIZED
        self.synthesis = synthesis
        self.completed_at = datetime.utcnow()
        return self

    def veto(self, reason: str) -> FusionResult:
        """
        Apply disgust veto.

        The disgust veto is absolute. It cannot be argued away.
        When Kent feels disgust at a proposal:
            - The proposal is rejected
            - No amount of evidence overrides this
            - The system must find another path
        """
        self.status = FusionStatus.VETOED
        self.veto_reason = reason
        self.completed_at = datetime.utcnow()
        return self

    def impasse(self) -> FusionResult:
        """Mark as impasse (no synthesis possible)."""
        self.status = FusionStatus.IMPASSE
        self.completed_at = datetime.utcnow()
        return self


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "ProposalId",
    "ChallengeId",
    "FusionId",
    "new_proposal_id",
    "new_challenge_id",
    "new_fusion_id",
    # Enums
    "Agent",
    "FusionStatus",
    # Core types
    "Proposal",
    "Challenge",
    "Synthesis",
    "FusionResult",
]
