"""
Fusion AGENTESE Node: @node("self.fusion")

Exposes the Symmetric Supersession dialectical fusion system via AGENTESE.

AGENTESE Paths:
- self.fusion.manifest  - Fusion system status
- self.fusion.propose   - Create a proposal from any agent
- self.fusion.fuse      - Run dialectical fusion on two proposals
- self.fusion.veto      - Apply Kent's disgust veto

The Constitutional Model (from 2025-12-21-symmetric-supersession.md):
    - Kent and AI are symmetric agents in the system
    - Either can propose, either can be superseded
    - Fusion emerges from dialectical process
    - The disgust veto is absolute

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: brainstorming/2025-12-21-symmetric-supersession.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .service import FusionService
from .types import Agent, FusionId, FusionStatus, ProposalId

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Contract Dataclasses
# =============================================================================


@dataclass(frozen=True)
class FusionManifestResponse:
    """Response for fusion manifest."""

    total_proposals: int
    total_fusions: int
    pending_fusions: int
    synthesized_fusions: int
    vetoed_fusions: int


@dataclass(frozen=True)
class ProposeRequest:
    """Request to create a proposal."""

    agent: str  # "kent", "claude", "k-gent"
    content: str
    reasoning: str
    principles: list[str] | None = None


@dataclass(frozen=True)
class ProposeResponse:
    """Response after creating a proposal."""

    proposal_id: str
    agent: str
    content: str
    reasoning: str


@dataclass(frozen=True)
class FuseRequest:
    """Request to fuse two proposals."""

    proposal_a_id: str
    proposal_b_id: str
    synthesis_content: str | None = None
    synthesis_reasoning: str | None = None
    incorporates_from_a: str | None = None
    incorporates_from_b: str | None = None
    transcends: str | None = None


@dataclass(frozen=True)
class FusionResponse:
    """Response after fusion attempt."""

    fusion_id: str
    status: str
    synthesis_content: str | None = None
    synthesis_reasoning: str | None = None
    is_genuine_fusion: bool = False


@dataclass(frozen=True)
class VetoRequest:
    """Request to apply disgust veto."""

    fusion_id: str
    reason: str


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class FusionManifestRendering:
    """Rendering for fusion status manifest."""

    total_proposals: int
    total_fusions: int
    pending_fusions: int
    synthesized_fusions: int
    vetoed_fusions: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "fusion_manifest",
            "total_proposals": self.total_proposals,
            "total_fusions": self.total_fusions,
            "pending_fusions": self.pending_fusions,
            "synthesized_fusions": self.synthesized_fusions,
            "vetoed_fusions": self.vetoed_fusions,
        }

    def to_text(self) -> str:
        lines = [
            "Fusion Status (Symmetric Supersession)",
            "======================================",
            f"Total Proposals: {self.total_proposals}",
            f"Total Fusions: {self.total_fusions}",
            f"  Synthesized: {self.synthesized_fusions}",
            f"  Vetoed: {self.vetoed_fusions}",
            f"  Pending: {self.pending_fusions}",
        ]
        return "\n".join(lines)


# =============================================================================
# FusionNode
# =============================================================================


@node(
    "self.fusion",
    description="Dialectical fusion for symmetric supersession - Kent and AI as symmetric agents",
    dependencies=("fusion_service",),
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(FusionManifestResponse),
        # Mutation aspects (Contract with request + response)
        "propose": Contract(ProposeRequest, ProposeResponse),
        "fuse": Contract(FuseRequest, FusionResponse),
        "veto": Contract(VetoRequest, FusionResponse),
    },
    examples=[
        ("manifest", {}, "View fusion status"),
        (
            "propose",
            {
                "agent": "kent",
                "content": "Use existing framework",
                "reasoning": "Pragmatic choice",
            },
            "Create Kent proposal",
        ),
        (
            "propose",
            {
                "agent": "claude",
                "content": "Build novel system",
                "reasoning": "Novel contribution",
            },
            "Create Claude proposal",
        ),
    ],
)
class FusionNode(BaseLogosNode):
    """
    AGENTESE node for Symmetric Supersession (Dialectical Fusion).

    Exposes FusionService through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    The philosophical insight:
        Kent and AI are symmetric agents. Either can propose.
        Either can be superseded. Fusion emerges from dialectic.
        The disgust veto is absolute.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/fusion/propose
        {"agent": "kent", "content": "Use LangChain", "reasoning": "Scale"}

        # Via Logos directly
        await logos.invoke("self.fusion.propose", observer, agent="kent", ...)

        # Via CLI
        kgents fusion propose --agent kent --content "..." --reasoning "..."
    """

    def __init__(self, fusion_service: FusionService) -> None:
        """
        Initialize FusionNode.

        Args:
            fusion_service: The FusionService (injected by container)
        """
        self._fusion = fusion_service

    @property
    def handle(self) -> str:
        return "self.fusion"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Fusion is a symmetric system, but veto is Kent-only.
        - developer/operator: Full access including veto
        - architect: Can propose and fuse, no veto
        - newcomer: Can view manifest only
        - guest: Can view manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators (Kent's trusted proxies)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "propose", "fuse", "veto")

        # Architects: can propose and fuse, no veto
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "propose", "fuse")

        # Newcomers/reviewers: read-only observation
        if archetype_lower in ("newcomer", "casual", "reviewer", "security"):
            return ("manifest",)

        # Guest (default): manifest only
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest fusion system status to observer.

        AGENTESE: self.fusion.manifest
        """
        fusions = self._fusion.list_fusions()

        synthesized = sum(1 for f in fusions if f.status == FusionStatus.SYNTHESIZED)
        vetoed = sum(1 for f in fusions if f.status == FusionStatus.VETOED)
        pending = sum(1 for f in fusions if f.status == FusionStatus.IN_PROGRESS)

        return FusionManifestRendering(
            total_proposals=len(self._fusion._proposals),
            total_fusions=len(fusions),
            pending_fusions=pending,
            synthesized_fusions=synthesized,
            vetoed_fusions=vetoed,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "propose":
            agent = kwargs.get("agent", "")
            content = kwargs.get("content", "")
            reasoning = kwargs.get("reasoning", "")
            principles = kwargs.get("principles", [])

            if not agent or not content:
                return {"error": "agent and content required"}

            proposal = self._fusion.propose(
                agent=agent,
                content=content,
                reasoning=reasoning,
                principles=principles,
            )

            return {
                "proposal_id": proposal.id,
                "agent": proposal.agent.value,
                "content": proposal.content,
                "reasoning": proposal.reasoning,
            }

        elif aspect == "fuse":
            proposal_a_id = kwargs.get("proposal_a_id", "")
            proposal_b_id = kwargs.get("proposal_b_id", "")
            synthesis_content = kwargs.get("synthesis_content")
            synthesis_reasoning = kwargs.get("synthesis_reasoning")
            incorporates_from_a = kwargs.get("incorporates_from_a")
            incorporates_from_b = kwargs.get("incorporates_from_b")
            transcends = kwargs.get("transcends")

            if not proposal_a_id or not proposal_b_id:
                return {"error": "proposal_a_id and proposal_b_id required"}

            proposal_a = self._fusion.get_proposal(ProposalId(proposal_a_id))
            proposal_b = self._fusion.get_proposal(ProposalId(proposal_b_id))

            if not proposal_a:
                return {"error": f"Proposal not found: {proposal_a_id}"}
            if not proposal_b:
                return {"error": f"Proposal not found: {proposal_b_id}"}

            if synthesis_content and synthesis_reasoning:
                # Simple fusion with provided synthesis
                result = await self._fusion.simple_fuse(
                    proposal_a,
                    proposal_b,
                    synthesis_content=synthesis_content,
                    synthesis_reasoning=synthesis_reasoning,
                    incorporates_from_a=incorporates_from_a,
                    incorporates_from_b=incorporates_from_b,
                    transcends=transcends,
                )
            else:
                # Full dialectical fusion (without synthesizer, will end in impasse)
                result = await self._fusion.fuse(proposal_a, proposal_b)

            return {
                "fusion_id": result.id,
                "status": result.status.value,
                "synthesis_content": result.synthesis.content if result.synthesis else None,
                "synthesis_reasoning": result.synthesis.reasoning if result.synthesis else None,
                "is_genuine_fusion": result.is_genuine_fusion,
            }

        elif aspect == "veto":
            fusion_id = kwargs.get("fusion_id", "")
            reason = kwargs.get("reason", "")

            if not fusion_id or not reason:
                return {"error": "fusion_id and reason required"}

            existing_result = self._fusion.get_fusion(FusionId(fusion_id))
            if not existing_result:
                return {"error": f"Fusion not found: {fusion_id}"}

            vetoed_result = await self._fusion.veto(existing_result, reason)

            return {
                "fusion_id": vetoed_result.id,
                "status": vetoed_result.status.value,
                "synthesis_content": None,
                "synthesis_reasoning": None,
                "is_genuine_fusion": False,
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "FusionNode",
    "FusionManifestResponse",
    "ProposeRequest",
    "ProposeResponse",
    "FuseRequest",
    "FusionResponse",
    "VetoRequest",
]
