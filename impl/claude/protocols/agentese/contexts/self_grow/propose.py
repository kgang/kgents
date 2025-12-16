"""
self.grow.propose - Proposal Generation

Generates spec proposals for new holons based on recognized gaps.

AGENTESE: self.grow.propose
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GapRecognition,
    GrowthBudget,
    HolonProposal,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Proposal Generation ===


def generate_default_affordances(
    context: str,
    entity: str,
    gap: GapRecognition | None = None,
) -> dict[str, list[str]]:
    """
    Generate default affordances based on context and gap evidence.

    Uses analogues from gap recognition if available.
    """
    # Base affordances by context
    context_defaults: dict[str, dict[str, list[str]]] = {
        "world": {
            "default": ["manifest", "witness"],
            "scholar": ["manifest", "witness", "inspect"],
            "architect": ["manifest", "witness", "inspect", "refine"],
            "gardener": ["manifest", "witness", "inspect", "refine", "define"],
        },
        "self": {
            "default": ["manifest", "witness"],
            "scholar": ["manifest", "witness", "status"],
            "architect": ["manifest", "witness", "status", "configure"],
            "gardener": ["manifest", "witness", "status", "configure", "evolve"],
        },
        "concept": {
            "default": ["manifest"],
            "scholar": ["manifest", "witness", "explore"],
            "architect": ["manifest", "witness", "explore", "refine"],
            "gardener": ["manifest", "witness", "explore", "refine", "define"],
        },
        "void": {
            "default": ["manifest"],
            "scholar": ["manifest", "witness"],
            "gardener": ["manifest", "witness", "sip", "tithe"],
        },
        "time": {
            "default": ["manifest"],
            "scholar": ["manifest", "witness", "history"],
            "architect": ["manifest", "witness", "history", "project"],
            "gardener": ["manifest", "witness", "history", "project", "schedule"],
        },
    }

    return context_defaults.get(context, context_defaults["world"]).copy()


def generate_default_behaviors(
    context: str,
    entity: str,
    gap: GapRecognition | None = None,
) -> dict[str, str]:
    """
    Generate default behavior descriptions.
    """
    behaviors = {
        "manifest": f"Collapse {entity} into observer-appropriate representation.",
        "witness": f"View the history and trace of {entity}.",
    }

    # Add context-specific behaviors
    if context == "world":
        behaviors["inspect"] = f"Examine the properties of {entity}."
    elif context == "self":
        behaviors["status"] = f"Get current status of {entity}."
    elif context == "concept":
        behaviors["explore"] = f"Navigate the conceptual space around {entity}."
    elif context == "void":
        behaviors["sip"] = f"Draw entropy from {entity}."
        behaviors["tithe"] = f"Tithe to {entity} in gratitude."
    elif context == "time":
        behaviors["history"] = f"View the temporal history of {entity}."

    return behaviors


def generate_proposal_from_gap(
    gap: GapRecognition,
    proposed_by: str,
    *,
    why_exists: str | None = None,
    affordances: dict[str, list[str]] | None = None,
    behaviors: dict[str, str] | None = None,
) -> HolonProposal:
    """
    Generate a holon proposal from a recognized gap.

    Args:
        gap: The gap recognition that triggered this proposal
        proposed_by: Observer name who is proposing
        why_exists: Optional justification (auto-generated if not provided)
        affordances: Optional affordances (auto-generated if not provided)
        behaviors: Optional behaviors (auto-generated if not provided)

    Returns:
        HolonProposal ready for validation
    """
    # Generate justification if not provided
    if why_exists is None:
        if gap.evidence_count >= 10:
            evidence_phrase = f"Strong evidence ({gap.evidence_count} occurrences)"
        elif gap.evidence_count >= 5:
            evidence_phrase = f"Moderate evidence ({gap.evidence_count} occurrences)"
        else:
            evidence_phrase = f"Initial evidence ({gap.evidence_count} occurrences)"

        why_exists = (
            f"Agents frequently need {gap.context}.{gap.holon}. "
            f"{evidence_phrase} from {gap.archetype_diversity} archetype(s). "
            f"Fills the gap between existing holons."
        )
        if gap.analogues:
            why_exists += f" Similar to: {', '.join(gap.analogues[:3])}."

    # Generate affordances if not provided
    if affordances is None:
        affordances = generate_default_affordances(gap.context, gap.holon, gap)

    # Generate behaviors if not provided
    if behaviors is None:
        behaviors = generate_default_behaviors(gap.context, gap.holon, gap)

    # Create proposal
    return HolonProposal(
        proposal_id=str(uuid.uuid4()),
        gap=gap,
        proposed_by=proposed_by,
        proposed_at=datetime.now(),
        entity=gap.holon,
        context=gap.context,
        why_exists=why_exists,
        affordances=affordances,
        behaviors=behaviors,
        relations={
            "composes_with": gap.analogues[:3] if gap.analogues else [],
        },
    )


# === Propose Node ===


@dataclass
class ProposeNode(BaseLogosNode):
    """
    self.grow.propose - Proposal generation node.

    Creates holon proposals from recognized gaps.

    Affordances:
    - manifest: View pending proposals
    - draft: Create a new proposal from a gap
    - edit: Modify an existing proposal
    - withdraw: Withdraw a proposal

    AGENTESE: self.grow.propose.*
    """

    _handle: str = "self.grow.propose"

    # Budget for entropy tracking
    _budget: GrowthBudget | None = None

    # Pending proposals
    _proposals: dict[str, HolonProposal] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Proposal requires gardener or architect affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if "propose" in affordances:
            return ("draft", "edit", "withdraw", "list")
        return ("list",)  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View pending proposals."""
        return BasicRendering(
            summary=f"Pending Proposals: {len(self._proposals)}",
            content=self._format_proposals(list(self._proposals.values())[:5]),
            metadata={
                "proposal_count": len(self._proposals),
                "proposals": [
                    {
                        "proposal_id": p.proposal_id,
                        "handle": f"{p.context}.{p.entity}",
                        "proposed_by": p.proposed_by,
                        "proposed_at": p.proposed_at.isoformat(),
                    }
                    for p in list(self._proposals.values())[:10]
                ],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle proposal aspects."""
        match aspect:
            case "draft":
                return await self._draft(observer, **kwargs)
            case "edit":
                return self._edit(observer, **kwargs)
            case "withdraw":
                return self._withdraw(observer, **kwargs)
            case "list":
                return self._list(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _draft(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new proposal from a gap.

        Args:
            gap: GapRecognition to base the proposal on
            why_exists: Optional justification
            affordances: Optional affordances
            behaviors: Optional behaviors

        Returns:
            Dict with proposal details
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "propose" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot propose",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Get gap
        gap = kwargs.get("gap")
        if gap is None:
            # Allow creating proposals without a gap (manual proposal)
            entity = kwargs.get("entity")
            context = kwargs.get("context")
            if not entity or not context:
                return {"error": "Either gap or (entity, context) required"}

            gap = GapRecognition.create(context=context, holon=entity)

        # Check budget
        if self._budget is not None:
            if not self._budget.can_afford("propose"):
                from .exceptions import BudgetExhaustedError

                raise BudgetExhaustedError(
                    "Proposal budget exhausted",
                    remaining=self._budget.remaining,
                    requested=self._budget.config.propose_cost,
                )
            self._budget.spend("propose")

        # Start span
        async with tracer.start_span_async("growth.propose") as span:
            span.set_attribute("growth.phase", "propose")
            span.set_attribute("growth.proposal.context", gap.context)
            span.set_attribute("growth.proposal.entity", gap.holon)

            # Generate proposal
            proposal = generate_proposal_from_gap(
                gap,
                proposed_by=meta.name,
                why_exists=kwargs.get("why_exists"),
                affordances=kwargs.get("affordances"),
                behaviors=kwargs.get("behaviors"),
            )

            span.set_attribute(
                "growth.proposal.handle", f"{proposal.context}.{proposal.entity}"
            )
            span.set_attribute("growth.proposal.hash", proposal.content_hash)

            # Store proposal
            self._proposals[proposal.proposal_id] = proposal

            # Record metrics
            metrics.counter("growth.propose.invocations").add(1)

        return {
            "status": "drafted",
            "proposal_id": proposal.proposal_id,
            "handle": f"{proposal.context}.{proposal.entity}",
            "content_hash": proposal.content_hash,
            "why_exists": proposal.why_exists,
            "affordances": proposal.affordances,
            "behaviors": proposal.behaviors,
        }

    def _edit(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Edit an existing proposal.

        Args:
            proposal_id: ID of proposal to edit
            why_exists: New justification
            affordances: New affordances
            behaviors: New behaviors

        Returns:
            Dict with updated proposal details
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "propose" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot edit proposals",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        proposal_id = kwargs.get("proposal_id")
        if not proposal_id:
            return {"error": "proposal_id required"}

        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return {"error": f"Proposal not found: {proposal_id}"}

        # Update fields
        if "why_exists" in kwargs:
            proposal.why_exists = kwargs["why_exists"]
        if "affordances" in kwargs:
            proposal.affordances = kwargs["affordances"]
        if "behaviors" in kwargs:
            proposal.behaviors = kwargs["behaviors"]

        # Recompute hash
        proposal.content_hash = proposal.compute_hash()

        return {
            "status": "edited",
            "proposal_id": proposal.proposal_id,
            "content_hash": proposal.content_hash,
        }

    def _withdraw(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Withdraw a proposal.

        Args:
            proposal_id: ID of proposal to withdraw

        Returns:
            Dict with withdrawal status
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "propose" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot withdraw proposals",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        proposal_id = kwargs.get("proposal_id")
        if not proposal_id:
            return {"error": "proposal_id required"}

        if proposal_id not in self._proposals:
            return {"error": f"Proposal not found: {proposal_id}"}

        del self._proposals[proposal_id]

        return {
            "status": "withdrawn",
            "proposal_id": proposal_id,
        }

    def _list(self, **kwargs: Any) -> dict[str, Any]:
        """List all proposals."""
        limit = kwargs.get("limit", 20)
        proposals = list(self._proposals.values())[:limit]

        return {
            "proposals": [
                {
                    "proposal_id": p.proposal_id,
                    "handle": f"{p.context}.{p.entity}",
                    "proposed_by": p.proposed_by,
                    "proposed_at": p.proposed_at.isoformat(),
                    "content_hash": p.content_hash,
                }
                for p in proposals
            ],
            "total": len(self._proposals),
        }

    def _format_proposals(self, proposals: list[HolonProposal]) -> str:
        """Format proposals for display."""
        if not proposals:
            return "No pending proposals"

        lines = []
        for p in proposals:
            lines.append(
                f"  {p.context}.{p.entity}"
                + f" by {p.proposed_by}"
                + f" [{p.proposed_at.strftime('%Y-%m-%d')}]"
            )
        return "\n".join(lines)


# === Factory ===


def create_propose_node(
    budget: GrowthBudget | None = None,
) -> ProposeNode:
    """
    Create a ProposeNode with optional configuration.

    Args:
        budget: Growth budget for entropy tracking

    Returns:
        Configured ProposeNode
    """
    return ProposeNode(_budget=budget)
