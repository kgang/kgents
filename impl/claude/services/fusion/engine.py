"""
DialecticalEngine: The engine that produces fused decisions through dialectic.

The Dialectical Pattern (from 2025-12-21-symmetric-supersession.md):
    THESIS (Kent's view)
           │
           ▼
    ┌──────────────────────────────────────┐
    │         DIALECTICAL ARENA            │
    │                                       │
    │   Kent challenges AI's proposals     │
    │   AI challenges Kent's proposals     │
    │   Each must justify to the other     │
    │   Friction produces heat             │
    │   Heat illuminates truth             │
    │                                       │
    └──────────────────────────────────────┘
           │
           ▼
    ANTITHESIS (AI's view)
           │
           ▼
    ┌──────────────────────────────────────┐
    │         SYNTHESIS EMERGES            │
    │                                       │
    │   Neither Kent's original view       │
    │   Nor AI's original view             │
    │   But something that transcends both │
    │                                       │
    └──────────────────────────────────────┘
           │
           ▼
        FUSION
    (Enlightened decision)

Why Adversarial?
    Because agreement is cheap. A system that only confirms views is:
    - Sycophantic (violates Ethical principle)
    - Non-generative (violates Generative principle)
    - Boring (violates Joy-Inducing principle)

Why Nominative?
    Because the purpose is not opposition but fusion. This is:
    - Mutual sharpening ("iron sharpens iron")
    - Collaborative truth-seeking
    - Ego dissolution into shared purpose

Phase 0: Manual challenge/synthesis.
Future phases: LLM-generated challenges, automatic synthesis attempts.

See: brainstorming/2025-12-21-symmetric-supersession.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable

from .types import (
    Agent,
    Challenge,
    FusionResult,
    FusionStatus,
    Proposal,
    Synthesis,
    new_fusion_id,
)
from .veto import DisgustVeto

if TYPE_CHECKING:
    from services.witness import WitnessPersistence
    from services.witness.polynomial import Thought


# =============================================================================
# DialecticalEngine
# =============================================================================


@dataclass
class DialecticalEngine:
    """
    The engine that produces fused decisions through dialectic.

    Phase 0: Manual challenge/synthesis.
    Future phases: LLM-generated challenges, automatic synthesis attempts.

    The engine:
    1. Accepts proposals from both agents
    2. Facilitates dialectical challenges
    3. Attempts synthesis
    4. Respects the disgust veto

    All steps are recorded as thoughts via the Witness service.

    Example:
        >>> engine = DialecticalEngine(witness=witness_persistence, veto=DisgustVeto())
        >>> result = await engine.simple_fuse(kent_proposal, claude_proposal, synthesis)
        >>> assert result.status == FusionStatus.SYNTHESIZED
    """

    witness: WitnessPersistence | None = None
    veto: DisgustVeto | None = None
    max_rounds: int = 3

    def __post_init__(self) -> None:
        if self.veto is None:
            self.veto = DisgustVeto()

    async def _record_thought(
        self,
        content: str,
        source: str = "fusion",
        tags: tuple[str, ...] = (),
    ) -> None:
        """
        Record a thought via the Witness service.

        Fire-and-forget: doesn't block if witness is unavailable.
        """
        if self.witness is None:
            return

        try:
            from datetime import UTC, datetime

            from services.witness.polynomial import Thought

            thought = Thought(
                content=content,
                source=source,
                tags=tags,
                timestamp=datetime.now(UTC),
            )
            await self.witness.save_thought(thought)
        except Exception:
            # Graceful degradation: fusion works even if witness fails
            pass

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
        Run dialectical process to fuse two proposals.

        This is the full dialectical engine with optional callbacks for
        generating challenges and synthesis attempts.

        Args:
            proposal_a: First proposal (typically Kent's)
            proposal_b: Second proposal (typically Claude's)
            challenger: Function to generate challenges (optional)
            synthesizer: Function to attempt synthesis (optional)

        Returns:
            FusionResult with synthesis or impasse
        """
        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=proposal_a,
            proposal_b=proposal_b,
        )

        # Record proposals as thoughts
        await self._record_thought(
            f"Proposal from {proposal_a.agent.value}: {proposal_a.content}\n"
            f"Reasoning: {proposal_a.reasoning}",
            source=f"fusion.{proposal_a.agent.value}",
            tags=("proposal", proposal_a.agent.value, *proposal_a.principles),
        )
        await self._record_thought(
            f"Proposal from {proposal_b.agent.value}: {proposal_b.content}\n"
            f"Reasoning: {proposal_b.reasoning}",
            source=f"fusion.{proposal_b.agent.value}",
            tags=("proposal", proposal_b.agent.value, *proposal_b.principles),
        )

        # Run dialectical rounds
        for round_num in range(self.max_rounds):
            # A challenges B
            if challenger:
                challenge_a = await challenger(proposal_b, proposal_a.agent)
                result.challenges.append(challenge_a)
                await self._record_thought(
                    f"Challenge from {challenge_a.challenger.value}: {challenge_a.content}",
                    source=f"fusion.{challenge_a.challenger.value}",
                    tags=("challenge", challenge_a.challenger.value),
                )

                # B challenges A
                challenge_b = await challenger(proposal_a, proposal_b.agent)
                result.challenges.append(challenge_b)
                await self._record_thought(
                    f"Challenge from {challenge_b.challenger.value}: {challenge_b.content}",
                    source=f"fusion.{challenge_b.challenger.value}",
                    tags=("challenge", challenge_b.challenger.value),
                )

            # Attempt synthesis
            if synthesizer:
                synthesis = await synthesizer(proposal_a, proposal_b, result.challenges)
                if synthesis:
                    result.complete(synthesis)
                    await self._record_thought(
                        f"Synthesis emerged: {synthesis.content}\nReasoning: {synthesis.reasoning}",
                        source="fusion.system",
                        tags=("synthesis", "fusion"),
                    )
                    return result

        # No synthesis achieved
        if result.synthesis is None:
            result.impasse()
            await self._record_thought(
                f"Dialectic ended in impasse after {self.max_rounds} rounds",
                source="fusion.system",
                tags=("impasse", "fusion"),
            )

        return result

    async def simple_fuse(
        self,
        proposal_a: Proposal,
        proposal_b: Proposal,
        manual_synthesis: Synthesis,
    ) -> FusionResult:
        """
        Simple fusion with manually provided synthesis.

        Use this for Phase 0 when we don't have LLM-generated
        challenges and synthesis yet.

        This is the primary API for Phase 0.

        Args:
            proposal_a: First proposal
            proposal_b: Second proposal
            manual_synthesis: The synthesis (provided by human or simple logic)

        Returns:
            FusionResult with the synthesis
        """
        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=proposal_a,
            proposal_b=proposal_b,
        )

        # Record proposals
        await self._record_thought(
            f"Proposal from {proposal_a.agent.value}: {proposal_a.content}\n"
            f"Reasoning: {proposal_a.reasoning}",
            source=f"fusion.{proposal_a.agent.value}",
            tags=("proposal", proposal_a.agent.value),
        )
        await self._record_thought(
            f"Proposal from {proposal_b.agent.value}: {proposal_b.content}\n"
            f"Reasoning: {proposal_b.reasoning}",
            source=f"fusion.{proposal_b.agent.value}",
            tags=("proposal", proposal_b.agent.value),
        )

        # Record synthesis
        result.complete(manual_synthesis)
        await self._record_thought(
            f"Synthesis: {manual_synthesis.content}\nReasoning: {manual_synthesis.reasoning}",
            source="fusion.system",
            tags=("synthesis", "fusion"),
        )

        return result

    async def apply_veto(
        self,
        result: FusionResult,
        reason: str,
    ) -> FusionResult:
        """
        Apply Kent's disgust veto to a fusion result.

        The disgust veto is absolute. It cannot be argued away.
        This is the ethical floor beneath which no decision may fall.

        Args:
            result: The FusionResult to veto
            reason: Why this triggers disgust

        Returns:
            The vetoed FusionResult
        """
        assert self.veto is not None

        # Record the veto signal
        signal = self.veto.explicit_veto(reason)

        # Apply veto to result
        result.veto(reason)

        # Record as thought
        await self._record_thought(
            f"VETO: {reason}\nIntensity: {signal.intensity:.2f}",
            source="fusion.kent",
            tags=("veto", "disgust", "ethical"),
        )

        return result


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "DialecticalEngine",
]
