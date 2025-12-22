"""
self.grow.promote - Holon Promotion

Promotes germinating holons to permanent spec + implementation.

Stages:
1. STAGED: Holon meets promotion criteria
2. APPROVED: Human approver has approved
3. ACTIVE: Spec and impl written to disk

AGENTESE: self.grow.promote
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError, BudgetExhaustedError, GrowthError
from .nursery import NurseryNode
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GerminatingHolon,
    GrowthBudget,
    PromotionResult,
    PromotionStage,
    RollbackToken,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Path Helpers ===


def get_spec_path(context: str, entity: str, base_path: Path) -> Path:
    """Get the spec file path for a holon."""
    return base_path / "spec" / "protocols" / "agentese" / context / f"{entity}.md"


def get_impl_path(context: str, entity: str, base_path: Path) -> Path:
    """Get the implementation file path for a holon."""
    return (
        base_path
        / "impl"
        / "claude"
        / "protocols"
        / "agentese"
        / "contexts"
        / context
        / f"{entity}.py"
    )


# === Promote Node ===


@dataclass
class PromoteNode(BaseLogosNode):
    """
    self.grow.promote - Holon promotion node.

    Promotes germinating holons to permanent spec + implementation.

    Affordances:
    - manifest: View promotion status
    - stage: Stage a holon for promotion
    - approve: Approve a staged holon (admin only)
    - activate: Write spec + impl to disk

    AGENTESE: self.grow.promote.*
    """

    _handle: str = "self.grow.promote"

    # Integration points
    _budget: GrowthBudget | None = None
    _nursery: NurseryNode | None = None

    # Base path for spec/impl files
    _base_path: Path | None = None

    # Staged promotions
    _staged: dict[str, GerminatingHolon] = None  # type: ignore[assignment]

    # Rollback tokens (keyed by handle)
    _rollback_tokens: dict[str, RollbackToken] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self._staged is None:
            self._staged = {}
        if self._rollback_tokens is None:
            self._rollback_tokens = {}

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Promotion requires gardener or admin affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if archetype == "gardener":
            return ("stage", "activate", "status")
        elif archetype == "admin":
            return ("stage", "approve", "activate", "status")
        elif "promote" in affordances:
            return ("stage", "status")
        return ("status",)

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View promotion status."""
        return BasicRendering(
            summary=f"Promotions: {len(self._staged)} staged",
            content=self._format_staged(list(self._staged.values())[:5]),
            metadata={
                "staged_count": len(self._staged),
                "rollback_tokens": len(self._rollback_tokens),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle promotion aspects."""
        match aspect:
            case "stage":
                return await self._stage(observer, **kwargs)
            case "approve":
                return self._approve(observer, **kwargs)
            case "activate":
                return await self._activate(observer, **kwargs)
            case "status":
                return self._status(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _stage(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Stage a holon for promotion.

        Args:
            germination_id: ID of the germinating holon

        Returns:
            Dict with staging details
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "promote" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot promote",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Check nursery
        if self._nursery is None:
            return {"error": "Nursery not configured"}

        # Get holon
        germination_id = kwargs.get("germination_id")
        if not germination_id:
            return {"error": "germination_id required"}

        holon = self._nursery.get(germination_id)
        if holon is None:
            return {"error": f"Holon not found: {germination_id}"}

        # Check if ready for promotion
        if not holon.should_promote(self._nursery._config):
            return {
                "error": "Holon not ready for promotion",
                "usage_count": holon.usage_count,
                "success_rate": holon.success_rate,
                "min_usage": self._nursery._config.min_usage_for_promotion,
                "min_success_rate": self._nursery._config.min_success_rate_for_promotion,
            }

        # Stage
        handle = f"{holon.proposal.context}.{holon.proposal.entity}"
        self._staged[handle] = holon

        return {
            "status": "staged",
            "stage": PromotionStage.STAGED,
            "handle": handle,
            "germination_id": germination_id,
            "usage_count": holon.usage_count,
            "success_rate": holon.success_rate,
        }

    def _approve(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Approve a staged holon (admin only).

        Args:
            handle: Handle of the staged holon

        Returns:
            Dict with approval status
        """
        meta = self._umwelt_to_meta(observer)

        # Only admin can approve
        if meta.archetype != "admin":
            raise AffordanceError(
                f"Only admin can approve promotions, not '{meta.archetype}'",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        handle = kwargs.get("handle")
        if not handle:
            return {"error": "handle required"}

        holon = self._staged.get(handle)
        if holon is None:
            return {"error": f"Holon not staged: {handle}"}

        # Mark as approved by setting promoted_at (preliminary)
        holon.promoted_at = datetime.now()

        return {
            "status": "approved",
            "stage": PromotionStage.APPROVED,
            "handle": handle,
            "approver": meta.name,
        }

    async def _activate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Activate a holon (write spec + impl to disk).

        Args:
            handle: Handle of the approved holon

        Returns:
            Dict with activation details including rollback token
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "promote" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot activate",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        handle = kwargs.get("handle")
        if not handle:
            return {"error": "handle required"}

        holon = self._staged.get(handle)
        if holon is None:
            return {"error": f"Holon not staged: {handle}"}

        # Check if approved (unless gardener is activating their own)
        if holon.promoted_at is None and meta.archetype != "gardener":
            return {"error": "Holon not approved. Requires admin approval."}

        # Check budget
        if self._budget is not None:
            if not self._budget.can_afford("promote"):
                raise BudgetExhaustedError(
                    "Promotion budget exhausted",
                    remaining=self._budget.remaining,
                    requested=self._budget.config.promote_cost,
                )
            self._budget.spend("promote")

        async with tracer.start_span_async("growth.promote") as span:
            span.set_attribute("growth.phase", "promote")
            span.set_attribute("growth.promotion.stage", PromotionStage.ACTIVE)
            span.set_attribute("growth.proposal.handle", handle)

            # Determine paths
            if self._base_path is None:
                self._base_path = Path.cwd()

            context = holon.proposal.context
            entity = holon.proposal.entity
            spec_path = get_spec_path(context, entity, self._base_path)
            impl_path = get_impl_path(context, entity, self._base_path)

            # Create rollback token BEFORE writing
            rollback_token = RollbackToken.create(
                handle=handle,
                spec_path=spec_path,
                impl_path=impl_path,
            )
            self._rollback_tokens[handle] = rollback_token
            span.set_attribute("growth.promotion.rollback_token", rollback_token.token_id)

            # Generate spec content
            spec_content = holon.proposal.to_markdown()

            # Get JIT source for impl
            impl_content = holon.jit_source

            # Compute hashes
            proposal_hash = holon.proposal.content_hash
            impl_hash = hashlib.sha256(impl_content.encode()).hexdigest()

            # Write files
            try:
                spec_path.parent.mkdir(parents=True, exist_ok=True)
                spec_path.write_text(spec_content)

                impl_path.parent.mkdir(parents=True, exist_ok=True)
                impl_path.write_text(impl_content)
            except Exception as e:
                raise GrowthError(f"Failed to write promotion files: {e}") from e

            # Update rollback token with content for rollback
            rollback_token = RollbackToken.create(
                handle=handle,
                spec_path=spec_path,
                impl_path=impl_path,
                spec_content=spec_content,
                impl_content=impl_content,
            )
            # Link stored via handle (rollback_token.handle == holon handle)
            self._rollback_tokens[handle] = rollback_token

            # Mark as promoted
            holon.promoted_at = datetime.now()
            holon.rollback_token = rollback_token.token_id

            # Remove from nursery (nursery was checked at line 170)
            assert self._nursery is not None  # Verified at function entry
            self._nursery.remove(holon.germination_id)

            # Remove from staged
            del self._staged[handle]

            # Record metrics
            metrics.counter("growth.promote.invocations").add(1)
            metrics.counter("growth.promote.approved").add(1)

        return {
            "status": "activated",
            "stage": PromotionStage.ACTIVE,
            "handle": handle,
            "spec_path": str(spec_path),
            "impl_path": str(impl_path),
            "rollback_token": rollback_token.token_id,
            "proposal_hash": proposal_hash,
            "impl_hash": impl_hash,
        }

    def _status(self, **kwargs: Any) -> dict[str, Any]:
        """Get promotion status."""
        handle = kwargs.get("handle")

        if handle:
            # Get specific handle status
            if handle in self._staged:
                holon = self._staged[handle]
                return {
                    "handle": handle,
                    "stage": PromotionStage.APPROVED
                    if holon.promoted_at
                    else PromotionStage.STAGED,
                    "germination_id": holon.germination_id,
                    "usage_count": holon.usage_count,
                    "success_rate": holon.success_rate,
                }
            elif handle in self._rollback_tokens:
                token = self._rollback_tokens[handle]
                return {
                    "handle": handle,
                    "stage": PromotionStage.ACTIVE,
                    "rollback_token": token.token_id,
                    "promoted_at": token.promoted_at.isoformat(),
                    "rollback_expires_at": token.expires_at.isoformat(),
                    "is_rollback_expired": token.is_expired,
                }
            else:
                return {"error": f"Handle not found: {handle}"}

        # General status
        return {
            "staged_count": len(self._staged),
            "staged": list(self._staged.keys()),
            "active_rollback_tokens": len(self._rollback_tokens),
        }

    def _format_staged(self, holons: list[GerminatingHolon]) -> str:
        """Format staged holons for display."""
        if not holons:
            return "No staged promotions"

        lines = []
        for h in holons:
            handle = f"{h.proposal.context}.{h.proposal.entity}"
            stage = PromotionStage.APPROVED if h.promoted_at else PromotionStage.STAGED
            lines.append(f"  {handle} [{stage}]")
        return "\n".join(lines)


# === Factory ===


def create_promote_node(
    budget: GrowthBudget | None = None,
    nursery: NurseryNode | None = None,
    base_path: Path | None = None,
) -> PromoteNode:
    """
    Create a PromoteNode with optional configuration.

    Args:
        budget: Growth budget for entropy tracking
        nursery: NurseryNode for holon lookup
        base_path: Base path for spec/impl files

    Returns:
        Configured PromoteNode
    """
    node = PromoteNode(
        _budget=budget,
        _nursery=nursery,
        _base_path=base_path,
    )
    node.__post_init__()
    return node
