"""
AGENTESE Self Covenant Context: Negotiated Permission Contract.

Permission-related nodes for self.covenant.* paths:
- CovenantNode: Permission negotiation and management

This node provides AGENTESE access to the Covenant primitive for
explicit, revocable permission contracts.

AGENTESE Paths:
    self.covenant.manifest  - Show active covenants
    self.covenant.propose   - Propose a new covenant
    self.covenant.grant     - Grant a covenant (human action)
    self.covenant.revoke    - Revoke a covenant
    self.covenant.check     - Check if operation is permitted

See: services/witness/covenant.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass
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

_covenant_store: dict[str, Any] = {}


def _get_covenant(covenant_id: str) -> Any | None:
    """Get covenant by ID."""
    return _covenant_store.get(covenant_id)


def _add_covenant(covenant: Any) -> None:
    """Add covenant to store."""
    _covenant_store[str(covenant.id)] = covenant


# =============================================================================
# CovenantNode: AGENTESE Interface to Covenant
# =============================================================================


COVENANT_AFFORDANCES: tuple[str, ...] = ("manifest", "propose", "grant", "revoke", "check")


@node(
    "self.covenant",
    description="Negotiated permission contracts with review gates",
)
@dataclass
class CovenantNode(BaseLogosNode):
    """
    self.covenant - Negotiated permission contracts.

    A Covenant is a formal agreement between human and agent that:
    - Defines what operations are permitted
    - Specifies review gates for sensitive operations
    - Can be proposed, granted, and revoked

    Laws (from covenant.py):
    - Law 1 (Required): Sensitive operations require a granted Covenant
    - Law 2 (Revocable): Covenants can be revoked at any time
    - Law 3 (Gated): Review gates trigger on threshold

    AGENTESE: self.covenant.*
    """

    _handle: str = "self.covenant"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Covenant affordances available to all archetypes."""
        return COVENANT_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show active and recent covenants.

        Returns:
            List of covenants with status and permissions
        """
        from services.witness.covenant import CovenantStatus

        # Collect stats
        total = len(_covenant_store)
        granted = sum(1 for c in _covenant_store.values() if c.status == CovenantStatus.GRANTED)
        revoked = sum(1 for c in _covenant_store.values() if c.status == CovenantStatus.REVOKED)

        recent = sorted(
            _covenant_store.values(),
            key=lambda c: c.granted_at or c.proposed_at,
            reverse=True,
        )[:5]

        manifest_data = {
            "path": self.handle,
            "description": "Negotiated permission contracts",
            "total_covenants": total,
            "granted_count": granted,
            "revoked_count": revoked,
            "recent": [
                {
                    "id": str(c.id),
                    "status": c.status.name,
                    "permissions_count": len(c.permissions) if hasattr(c, "permissions") else 0,
                    "gates_count": len(c.review_gates),
                    "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                }
                for c in recent
            ],
            "laws": [
                "Law 1: Sensitive operations require a granted Covenant",
                "Law 2: Covenants can be revoked at any time",
                "Law 3: Review gates trigger on threshold",
            ],
        }

        return BasicRendering(
            summary="Covenants (Permission Contracts)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Covenant-specific aspects."""
        match aspect:
            case "propose":
                return self._propose_covenant(**kwargs)
            case "grant":
                return self._grant_covenant(**kwargs)
            case "revoke":
                return self._revoke_covenant(**kwargs)
            case "check":
                return self._check_permission(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Propose a new covenant for human review",
    )
    def _propose_covenant(
        self,
        permissions: list[str] | None = None,
        description: str = "",
        gates: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Propose a new Covenant for human review.

        Args:
            permissions: List of permission patterns (e.g., ["file_read", "git_status"])
            description: Human-readable description of what this covenant permits
            gates: Review gates to add

        Returns:
            Proposed Covenant info
        """
        from services.witness.covenant import Covenant, CovenantStatus, ReviewGate

        # Parse gates
        review_gates: list[ReviewGate] = []
        if gates:
            for gate_data in gates:
                gate = ReviewGate(
                    trigger=gate_data.get("trigger", ""),
                    description=gate_data.get("description", ""),
                    threshold=gate_data.get("threshold", 1),
                )
                review_gates.append(gate)

        # Create covenant
        covenant = Covenant.propose(
            permissions=tuple(permissions) if permissions else (),
            description=description,
            review_gates=tuple(review_gates),
        )

        # Store
        _add_covenant(covenant)

        return {
            "id": str(covenant.id),
            "status": covenant.status.name,
            "permissions": list(permissions) if permissions else [],
            "description": description,
            "gates_count": len(review_gates),
            "proposed_at": covenant.proposed_at.isoformat(),
            "message": "Covenant proposed. Awaiting human review to grant.",
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Grant a proposed covenant (human action)",
    )
    def _grant_covenant(
        self,
        covenant_id: str = "",
    ) -> dict[str, Any]:
        """
        Grant a proposed Covenant.

        This is typically a human action - granting permission.
        """
        if not covenant_id:
            return {"error": "covenant_id is required"}

        covenant = _get_covenant(covenant_id)
        if covenant is None:
            return {"error": f"Covenant {covenant_id} not found"}

        from services.witness.covenant import CovenantStatus

        if covenant.status != CovenantStatus.PROPOSED:
            return {
                "error": f"Covenant must be PROPOSED to grant (current: {covenant.status.name})",
            }

        covenant.grant()

        return {
            "covenant_id": covenant_id,
            "status": covenant.status.name,
            "granted_at": covenant.granted_at.isoformat() if covenant.granted_at else None,
            "message": "Covenant granted. Operations are now permitted.",
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Revoke a covenant (Law 2: always possible)",
    )
    def _revoke_covenant(
        self,
        covenant_id: str = "",
        reason: str = "",
    ) -> dict[str, Any]:
        """
        Revoke a Covenant.

        Law 2: Covenants can be revoked at any time.
        """
        if not covenant_id:
            return {"error": "covenant_id is required"}

        covenant = _get_covenant(covenant_id)
        if covenant is None:
            return {"error": f"Covenant {covenant_id} not found"}

        covenant.revoke(reason=reason)

        return {
            "covenant_id": covenant_id,
            "status": covenant.status.name,
            "revoked_at": covenant.revoked_at.isoformat() if hasattr(covenant, "revoked_at") and covenant.revoked_at else None,
            "reason": reason,
            "message": "Covenant revoked. Operations are no longer permitted.",
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Check if an operation is permitted",
    )
    def _check_permission(
        self,
        covenant_id: str = "",
        operation: str = "",
    ) -> dict[str, Any]:
        """
        Check if an operation is permitted by a Covenant.

        Law 1: Sensitive operations require a granted Covenant.
        """
        if not covenant_id:
            return {"error": "covenant_id is required"}
        if not operation:
            return {"error": "operation is required"}

        covenant = _get_covenant(covenant_id)
        if covenant is None:
            return {"permitted": False, "reason": f"Covenant {covenant_id} not found"}

        from services.witness.covenant import CovenantStatus

        if covenant.status != CovenantStatus.GRANTED:
            return {
                "permitted": False,
                "reason": f"Covenant not granted (status: {covenant.status.name})",
            }

        # Check if operation matches any permission
        permissions = covenant.permissions if hasattr(covenant, "permissions") else ()
        permitted = operation in permissions or any(
            p.endswith("*") and operation.startswith(p[:-1]) for p in permissions
        )

        return {
            "covenant_id": covenant_id,
            "operation": operation,
            "permitted": permitted,
            "reason": "Operation matches permission" if permitted else "Operation not in permissions",
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Covenants (Permission Contracts)",
            "=" * 40,
            "",
            f"Total: {data['total_covenants']}",
            f"Granted: {data['granted_count']}",
            f"Revoked: {data['revoked_count']}",
            "",
        ]

        if data["recent"]:
            lines.append("Recent Covenants:")
            for c in data["recent"]:
                status_icon = "o" if c["status"] == "GRANTED" else "x"
                lines.append(f"  {status_icon} {c['id'][:20]} [{c['status']}]")
                lines.append(f"    Gates: {c['gates_count']}, Perms: {c['permissions_count']}")
        else:
            lines.append("No covenants yet. Use propose to create one.")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CovenantNode",
]
