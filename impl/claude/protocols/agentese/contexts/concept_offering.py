"""
AGENTESE Concept Offering Context: Explicit Context Contract.

Context-related nodes for concept.offering.* paths:
- OfferingNode: Budget-constrained context management

This node provides AGENTESE access to the Offering primitive for
explicit, priced context contracts.

AGENTESE Paths:
    concept.offering.manifest  - Show active offerings
    concept.offering.create    - Create a new offering
    concept.offering.consume   - Consume resources from an offering
    concept.offering.extend    - Extend an offering's budget/expiry
    concept.offering.status    - Check offering validity

See: services/witness/offering.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# =============================================================================
# Global Store Instance
# =============================================================================

_offering_store: dict[str, Any] = {}


def _get_offering(offering_id: str) -> Any | None:
    """Get offering by ID."""
    return _offering_store.get(offering_id)


def _add_offering(offering: Any) -> None:
    """Add offering to store."""
    _offering_store[str(offering.id)] = offering


def _update_offering(offering_id: str, new_offering: Any) -> None:
    """Update offering in store."""
    _offering_store[offering_id] = new_offering


# =============================================================================
# OfferingNode: AGENTESE Interface to Offering
# =============================================================================


OFFERING_AFFORDANCES: tuple[str, ...] = ("manifest", "create", "consume", "extend", "status")


@node(
    "concept.offering",
    description="Explicit context contracts with budget constraints",
)
@dataclass
class OfferingNode(BaseLogosNode):
    """
    concept.offering - Explicit context contracts.

    An Offering defines:
    - What handles are accessible (scope)
    - What resources can be consumed (budget)
    - When access expires (expiry)

    Laws (from offering.py):
    - Law 1 (Budget Enforcement): Exceeding budget triggers review
    - Law 2 (Immutability): Offerings are frozen after creation
    - Law 3 (Expiry Honored): Expired Offerings deny access

    AGENTESE: concept.offering.*
    """

    _handle: str = "concept.offering"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Offering affordances available to all archetypes."""
        return OFFERING_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show active offerings.

        Returns:
            List of offerings with budget status
        """
        # Collect stats
        total = len(_offering_store)
        valid = sum(1 for o in _offering_store.values() if o.is_valid())
        exhausted = sum(1 for o in _offering_store.values() if o.budget.is_exhausted)

        recent = sorted(
            _offering_store.values(),
            key=lambda o: o.created_at,
            reverse=True,
        )[:5]

        manifest_data = {
            "path": self.handle,
            "description": "Explicit context contracts with budget",
            "total_offerings": total,
            "valid_count": valid,
            "exhausted_count": exhausted,
            "recent": [
                {
                    "id": str(o.id),
                    "is_valid": o.is_valid(),
                    "budget": {
                        "tokens": o.budget.tokens,
                        "operations": o.budget.operations,
                        "time_seconds": o.budget.time_seconds,
                    },
                    "expires_at": o.expires_at.isoformat() if o.expires_at else None,
                }
                for o in recent
            ],
            "laws": [
                "Law 1: Exceeding budget triggers review (not silent failure)",
                "Law 2: Offerings are frozen after creation",
                "Law 3: Expired Offerings deny access",
            ],
        }

        return BasicRendering(
            summary="Offerings (Context Contracts)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Offering-specific aspects."""
        match aspect:
            case "create":
                return self._create_offering(**kwargs)
            case "consume":
                return self._consume_offering(**kwargs)
            case "extend":
                return self._extend_offering(**kwargs)
            case "status":
                return self._check_status(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Create a new offering with budget constraints",
    )
    def _create_offering(
        self,
        tokens: int | None = None,
        operations: int | None = None,
        time_seconds: float | None = None,
        expires_in_minutes: int | None = None,
        scoped_handles: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new Offering.

        Args:
            tokens: Max LLM tokens to consume
            operations: Max discrete operations
            time_seconds: Max wall-clock time
            expires_in_minutes: When this offering expires
            scoped_handles: AGENTESE handles this offering provides access to

        Returns:
            Created Offering info
        """
        from services.witness.offering import Budget, Offering

        # Create budget
        budget = Budget(
            tokens=tokens,
            operations=operations,
            time_seconds=time_seconds,
        )

        # Calculate expiry
        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)

        # Create offering
        offering = Offering.create(
            budget=budget,
            scoped_handles=tuple(scoped_handles) if scoped_handles else (),
            expires_at=expires_at,
        )

        # Store
        _add_offering(offering)

        return {
            "id": str(offering.id),
            "budget": {
                "tokens": tokens,
                "operations": operations,
                "time_seconds": time_seconds,
            },
            "scoped_handles": list(scoped_handles) if scoped_handles else [],
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_valid": offering.is_valid(),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Consume resources from an offering (Law 1: exceeding triggers review)",
    )
    def _consume_offering(
        self,
        offering_id: str = "",
        tokens: int = 0,
        operations: int = 0,
        time_seconds: float = 0.0,
    ) -> dict[str, Any]:
        """
        Consume resources from an Offering.

        Law 1: Exceeding budget triggers review, not silent failure.
        Law 2: Returns a new Offering (immutability).
        """
        if not offering_id:
            return {"error": "offering_id is required"}

        offering = _get_offering(offering_id)
        if offering is None:
            return {"error": f"Offering {offering_id} not found"}

        # Check validity
        if not offering.is_valid():
            return {
                "error": "Offering is no longer valid",
                "is_expired": offering.is_expired if hasattr(offering, "is_expired") else None,
                "is_exhausted": offering.budget.is_exhausted,
            }

        # Try to consume
        try:
            new_offering = offering.consume(
                tokens=tokens,
                operations=operations,
                time_seconds=time_seconds,
            )
            # Update store with new offering (Law 2: immutability)
            _update_offering(offering_id, new_offering)

            return {
                "offering_id": offering_id,
                "consumed": {
                    "tokens": tokens,
                    "operations": operations,
                    "time_seconds": time_seconds,
                },
                "remaining": {
                    "tokens": new_offering.budget.tokens,
                    "operations": new_offering.budget.operations,
                    "time_seconds": new_offering.budget.time_seconds,
                },
                "is_valid": new_offering.is_valid(),
            }
        except Exception as e:
            # Law 1: Budget exceeded triggers review
            return {
                "error": "budget_exceeded",
                "message": str(e),
                "action_required": "Review and extend offering, or create new one",
            }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Extend an offering's budget or expiry",
    )
    def _extend_offering(
        self,
        offering_id: str = "",
        add_tokens: int = 0,
        add_operations: int = 0,
        add_time_seconds: float = 0.0,
        extend_expiry_minutes: int = 0,
    ) -> dict[str, Any]:
        """
        Extend an Offering's budget or expiry.

        Creates a new Offering with extended limits (Law 2: immutability).
        """
        if not offering_id:
            return {"error": "offering_id is required"}

        offering = _get_offering(offering_id)
        if offering is None:
            return {"error": f"Offering {offering_id} not found"}

        # Create extended offering
        new_offering = offering.extend(
            add_tokens=add_tokens,
            add_operations=add_operations,
            add_time_seconds=add_time_seconds,
            extend_expiry_minutes=extend_expiry_minutes,
        )

        # Update store
        _update_offering(offering_id, new_offering)

        return {
            "offering_id": offering_id,
            "extended": {
                "tokens": add_tokens,
                "operations": add_operations,
                "time_seconds": add_time_seconds,
                "expiry_minutes": extend_expiry_minutes,
            },
            "new_budget": {
                "tokens": new_offering.budget.tokens,
                "operations": new_offering.budget.operations,
                "time_seconds": new_offering.budget.time_seconds,
            },
            "expires_at": new_offering.expires_at.isoformat() if new_offering.expires_at else None,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Check offering validity and remaining budget",
    )
    def _check_status(
        self,
        offering_id: str = "",
    ) -> dict[str, Any]:
        """
        Check status of an Offering.

        Law 3: Expired Offerings deny access.
        """
        if not offering_id:
            return {"error": "offering_id is required"}

        offering = _get_offering(offering_id)
        if offering is None:
            return {"error": f"Offering {offering_id} not found"}

        return {
            "offering_id": offering_id,
            "is_valid": offering.is_valid(),
            "is_exhausted": offering.budget.is_exhausted,
            "budget": {
                "tokens": offering.budget.tokens,
                "operations": offering.budget.operations,
                "time_seconds": offering.budget.time_seconds,
            },
            "expires_at": offering.expires_at.isoformat() if offering.expires_at else None,
            "scoped_handles": list(offering.scoped_handles) if hasattr(offering, "scoped_handles") else [],
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Offerings (Context Contracts)",
            "=" * 40,
            "",
            f"Total: {data['total_offerings']}",
            f"Valid: {data['valid_count']}",
            f"Exhausted: {data['exhausted_count']}",
            "",
        ]

        if data["recent"]:
            lines.append("Recent Offerings:")
            for o in data["recent"]:
                status_icon = "o" if o["is_valid"] else "x"
                budget = o["budget"]
                budget_str = f"T:{budget['tokens'] or '?'} O:{budget['operations'] or '?'}"
                lines.append(f"  {status_icon} {o['id'][:20]} [{budget_str}]")
        else:
            lines.append("No offerings yet. Use create to make one.")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "OfferingNode",
]
