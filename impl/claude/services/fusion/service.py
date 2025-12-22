"""
FusionService: Main API for Symmetric Supersession.

The main service layer for dialectical fusion. This is the entry point
for the Symmetric Supersession system.

The Constitutional Model (from 2025-12-21-symmetric-supersession.md):
    ARTICLE I: SYMMETRIC AGENCY
        All agents in the system (Kent, AI) are modeled identically.
        No agent has intrinsic authority over another.
        Authority derives from quality of justification.

    ARTICLE II: ADVERSARIAL COOPERATION
        Agents challenge each other's proposals.
        Challenge is nominative (structural) not substantive (hostile).
        Purpose is fusion, not victory.

    ARTICLE III: SUPERSESSION RIGHTS
        Any agent may be superseded by another.
        Supersession requires: valid proofs, sound arguments, sufficient evidence.
        Supersession is blocked by: somatic disgust (Kent), constitutional violation (AI).

    ARTICLE IV: THE DISGUST VETO
        Kent's somatic disgust is an absolute veto.
        It cannot be argued away or evidence'd away.
        It is the ethical floor beneath which no decision may fall.

    ARTICLE V: TRUST ACCUMULATION
        Trust is earned through demonstrated alignment.
        Trust is lost through demonstrated misalignment.
        Trust level determines scope of permitted supersession.

    ARTICLE VI: FUSION AS GOAL
        The goal is not Kent's decisions or AI's decisions.
        The goal is fused decisions better than either alone.
        Individual ego is dissolved into shared purpose.

Example usage:
    >>> fusion = FusionService(witness=witness_persistence)
    >>>
    >>> kent = fusion.propose("kent", "Use LangChain", "Scale and resources")
    >>> claude = fusion.propose("claude", "Build kgents", "Novel contribution")
    >>>
    >>> result = await fusion.simple_fuse(
    ...     kent, claude,
    ...     synthesis_content="Build minimal kernel, then decide",
    ...     synthesis_reasoning="Avoids both risks",
    ... )
    >>>
    >>> if kent_feels_disgust(result.synthesis):
    ...     result = await fusion.veto(result, "Visceral wrongness")

See: brainstorming/2025-12-21-symmetric-supersession.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable

from .engine import DialecticalEngine
from .types import (
    Agent,
    Challenge,
    FusionId,
    FusionResult,
    Proposal,
    ProposalId,
    Synthesis,
)
from .veto import DisgustVeto

if TYPE_CHECKING:
    from services.witness import WitnessPersistence


# =============================================================================
# FusionService
# =============================================================================


@dataclass
class FusionService:
    """
    Service for symmetric supersession via dialectical fusion.

    This is the main API for the fusion system. It provides:
    - Proposal creation (symmetric for all agents)
    - Dialectical fusion (with optional challenger/synthesizer)
    - Simple fusion (Phase 0: manual synthesis)
    - Disgust veto (absolute veto mechanism)

    The service maintains in-memory storage for proposals and fusions
    in Phase 0. Future phases will use D-gent persistence.

    Example:
        >>> fusion = FusionService(witness=witness_persistence)
        >>> kent = fusion.propose("kent", "Option A", "Reasoning for A")
        >>> claude = fusion.propose("claude", "Option B", "Reasoning for B")
        >>> result = await fusion.simple_fuse(
        ...     kent, claude,
        ...     synthesis_content="Blend of A and B",
        ...     synthesis_reasoning="Takes best of both",
        ... )
    """

    witness: WitnessPersistence | None = None
    disgust_veto: DisgustVeto = field(default_factory=DisgustVeto)
    engine: DialecticalEngine = field(init=False)

    # Phase 0: In-memory storage
    _proposals: dict[ProposalId, Proposal] = field(default_factory=dict, repr=False)
    _fusions: dict[FusionId, FusionResult] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self.engine = DialecticalEngine(
            witness=self.witness,
            veto=self.disgust_veto,
        )

    def propose(
        self,
        agent: Agent | str,
        content: str,
        reasoning: str,
        principles: list[str] | None = None,
    ) -> Proposal:
        """
        Create a proposal from an agent.

        Proposals are symmetric: Kent's proposals have the same
        structure as Claude's proposals.

        Args:
            agent: The proposing agent ("kent", "claude", "k-gent")
            content: What is being proposed
            reasoning: Why this proposal makes sense
            principles: Which principles support this proposal

        Returns:
            A new Proposal object
        """
        proposal = Proposal.create(
            agent=agent,
            content=content,
            reasoning=reasoning,
            principles=principles,
        )
        self._proposals[proposal.id] = proposal
        return proposal

    def get_proposal(self, proposal_id: ProposalId) -> Proposal | None:
        """Get a proposal by ID."""
        return self._proposals.get(proposal_id)

    def get_fusion(self, fusion_id: FusionId) -> FusionResult | None:
        """Get a fusion result by ID."""
        return self._fusions.get(fusion_id)

    async def fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        *,
        challenger: Callable[[Proposal, Agent], Awaitable[Challenge]] | None = None,
        synthesizer: Callable[[Proposal, Proposal, list[Challenge]], Awaitable[Synthesis | None]]
        | None = None,
    ) -> FusionResult:
        """
        Run dialectical fusion on two proposals.

        This is the full dialectical engine. Provide challenger and
        synthesizer callbacks for automatic dialectic.

        Args:
            proposal_a: First proposal
            proposal_b: Second proposal
            challenger: Async function to generate challenges
            synthesizer: Async function to attempt synthesis

        Returns:
            FusionResult with synthesis, impasse, or in_progress
        """
        result = await self.engine.fuse(
            proposal_a,
            proposal_b,
            challenger=challenger,
            synthesizer=synthesizer,
        )
        self._fusions[result.id] = result
        return result

    async def simple_fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        synthesis_content: str,
        synthesis_reasoning: str,
        incorporates_from_a: str | None = None,
        incorporates_from_b: str | None = None,
        transcends: str | None = None,
    ) -> FusionResult:
        """
        Simple fusion with manual synthesis (Phase 0).

        Use this when you have the synthesis already (from human
        decision or simple logic). This is the primary API for Phase 0.

        Args:
            proposal_a: First proposal
            proposal_b: Second proposal
            synthesis_content: What the synthesis proposes
            synthesis_reasoning: Why this synthesis makes sense
            incorporates_from_a: What was taken from proposal A
            incorporates_from_b: What was taken from proposal B
            transcends: What is new beyond both proposals

        Returns:
            FusionResult with the synthesis
        """
        synthesis = Synthesis(
            content=synthesis_content,
            reasoning=synthesis_reasoning,
            incorporates_from_a=incorporates_from_a,
            incorporates_from_b=incorporates_from_b,
            transcends=transcends,
        )
        result = await self.engine.simple_fuse(
            proposal_a,
            proposal_b,
            synthesis,
        )
        self._fusions[result.id] = result
        return result

    async def veto(
        self,
        result: FusionResult,
        reason: str,
    ) -> FusionResult:
        """
        Apply Kent's disgust veto.

        The disgust veto is absolute. It cannot be argued away.
        This is the ethical floor beneath which no decision may fall.

        Args:
            result: The FusionResult to veto
            reason: Why this triggers disgust

        Returns:
            The vetoed FusionResult
        """
        result = await self.engine.apply_veto(result, reason)
        self._fusions[result.id] = result
        return result

    def list_proposals(self, agent: Agent | str | None = None) -> list[Proposal]:
        """
        List all proposals, optionally filtered by agent.

        Args:
            agent: Filter by agent (optional)

        Returns:
            List of proposals
        """
        if agent is None:
            return list(self._proposals.values())

        if isinstance(agent, str):
            agent = Agent(agent)

        return [p for p in self._proposals.values() if p.agent == agent]

    def list_fusions(self) -> list[FusionResult]:
        """List all fusion results."""
        return list(self._fusions.values())

    def clear(self) -> None:
        """Clear all proposals and fusions (for testing)."""
        self._proposals.clear()
        self._fusions.clear()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "FusionService",
]
