"""
AGENTESE Self Grant Context: Negotiated Permission Contract.

Permission-related nodes for self.grant.* paths:
- GrantNode: Permission negotiation and management

This node provides AGENTESE access to the Grant primitive for
explicit, revocable permission contracts.

AGENTESE Paths:
    self.grant.manifest  - Show active grants
    self.grant.propose   - Propose a new grant
    self.grant.grant     - Grant a permission (human action)
    self.grant.revoke    - Revoke a grant
    self.grant.check     - Check if operation is permitted

See: services/witness/grant.py
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

_grant_store: dict[str, Any] = {}


def _get_grant(grant_id: str) -> Any | None:
    """Get grant by ID."""
    return _grant_store.get(grant_id)


def _add_grant(grant: Any) -> None:
    """Add grant to store."""
    _grant_store[str(grant.id)] = grant


# =============================================================================
# GrantNode: AGENTESE Interface to Grant
# =============================================================================


GRANT_AFFORDANCES: tuple[str, ...] = ("manifest", "propose", "grant", "revoke", "check")


@node(
    "self.grant",
    description="Negotiated permission contracts with review gates",
)
@dataclass
class GrantNode(BaseLogosNode):
    """
    self.grant - Negotiated permission contracts.

    A Grant is a formal agreement between human and agent that:
    - Defines what operations are permitted
    - Specifies review gates for sensitive operations
    - Can be proposed, granted, and revoked

    Laws (from grant.py):
    - Law 1 (Required): Sensitive operations require a granted Grant
    - Law 2 (Revocable): Grants can be revoked at any time
    - Law 3 (Gated): Review gates trigger on threshold

    AGENTESE: self.grant.*
    """

    _handle: str = "self.grant"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Grant affordances available to all archetypes."""
        return GRANT_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Show active and recent grants.

        Returns:
            List of grants with status and permissions
        """
        from services.witness.grant import GrantStatus

        # Collect stats
        total = len(_grant_store)
        granted = sum(1 for c in _grant_store.values() if c.status == GrantStatus.GRANTED)
        revoked = sum(1 for c in _grant_store.values() if c.status == GrantStatus.REVOKED)

        recent = sorted(
            _grant_store.values(),
            key=lambda c: c.granted_at or c.proposed_at,
            reverse=True,
        )[:5]

        manifest_data = {
            "path": self.handle,
            "description": "Negotiated permission contracts",
            "total_grants": total,
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
                "Law 1: Sensitive operations require a granted Grant",
                "Law 2: Grants can be revoked at any time",
                "Law 3: Review gates trigger on threshold",
            ],
        }

        return BasicRendering(
            summary="Grants (Permission Contracts)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Grant-specific aspects."""
        match aspect:
            case "propose":
                return self._propose_grant(**kwargs)
            case "grant":
                return self._grant_permission(**kwargs)
            case "revoke":
                return self._revoke_grant(**kwargs)
            case "check":
                return self._check_permission(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Propose a new grant for human review",
    )
    def _propose_grant(
        self,
        permissions: list[str] | None = None,
        description: str = "",
        gates: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Propose a new Grant for human review.

        Args:
            permissions: List of permission patterns (e.g., ["file_read", "git_status"])
            description: Human-readable description of what this grant permits
            gates: Review gates to add

        Returns:
            Proposed Grant info
        """
        from services.witness.grant import Grant, ReviewGate

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

        # Create grant
        grant = Grant.propose(
            permissions=tuple(permissions) if permissions else (),
            description=description,
            review_gates=tuple(review_gates),
        )

        # Store
        _add_grant(grant)

        return {
            "id": str(grant.id),
            "status": grant.status.name,
            "permissions": list(permissions) if permissions else [],
            "description": description,
            "gates_count": len(review_gates),
            "proposed_at": grant.proposed_at.isoformat(),
            "message": "Grant proposed. Awaiting human review to grant.",
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Grant a proposed permission (human action)",
    )
    def _grant_permission(
        self,
        grant_id: str = "",
    ) -> dict[str, Any]:
        """
        Grant a proposed Grant.

        This is typically a human action - granting permission.
        """
        if not grant_id:
            return {"error": "grant_id is required"}

        grant = _get_grant(grant_id)
        if grant is None:
            return {"error": f"Grant {grant_id} not found"}

        from services.witness.grant import GrantStatus

        if grant.status != GrantStatus.PROPOSED:
            return {
                "error": f"Grant must be PROPOSED to grant (current: {grant.status.name})",
            }

        grant.grant()

        return {
            "grant_id": grant_id,
            "status": grant.status.name,
            "granted_at": grant.granted_at.isoformat() if grant.granted_at else None,
            "message": "Grant granted. Operations are now permitted.",
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Revoke a grant (Law 2: always possible)",
    )
    def _revoke_grant(
        self,
        grant_id: str = "",
        reason: str = "",
    ) -> dict[str, Any]:
        """
        Revoke a Grant.

        Law 2: Grants can be revoked at any time.
        """
        if not grant_id:
            return {"error": "grant_id is required"}

        grant = _get_grant(grant_id)
        if grant is None:
            return {"error": f"Grant {grant_id} not found"}

        grant.revoke(reason=reason)

        return {
            "grant_id": grant_id,
            "status": grant.status.name,
            "revoked_at": grant.revoked_at.isoformat()
            if hasattr(grant, "revoked_at") and grant.revoked_at
            else None,
            "reason": reason,
            "message": "Grant revoked. Operations are no longer permitted.",
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Check if an operation is permitted",
    )
    def _check_permission(
        self,
        grant_id: str = "",
        operation: str = "",
    ) -> dict[str, Any]:
        """
        Check if an operation is permitted by a Grant.

        Law 1: Sensitive operations require a granted Grant.
        """
        if not grant_id:
            return {"error": "grant_id is required"}
        if not operation:
            return {"error": "operation is required"}

        grant = _get_grant(grant_id)
        if grant is None:
            return {"permitted": False, "reason": f"Grant {grant_id} not found"}

        from services.witness.grant import GrantStatus

        if grant.status != GrantStatus.GRANTED:
            return {
                "permitted": False,
                "reason": f"Grant not granted (status: {grant.status.name})",
            }

        # Check if operation matches any permission
        permissions = grant.permissions if hasattr(grant, "permissions") else ()
        permitted = operation in permissions or any(
            p.endswith("*") and operation.startswith(p[:-1]) for p in permissions
        )

        return {
            "grant_id": grant_id,
            "operation": operation,
            "permitted": permitted,
            "reason": "Operation matches permission"
            if permitted
            else "Operation not in permissions",
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Grants (Permission Contracts)",
            "=" * 40,
            "",
            f"Total: {data['total_grants']}",
            f"Granted: {data['granted_count']}",
            f"Revoked: {data['revoked_count']}",
            "",
        ]

        if data["recent"]:
            lines.append("Recent Grants:")
            for c in data["recent"]:
                status_icon = "o" if c["status"] == "GRANTED" else "x"
                lines.append(f"  {status_icon} {c['id'][:20]} [{c['status']}]")
                lines.append(f"    Gates: {c['gates_count']}, Perms: {c['permissions_count']}")
        else:
            lines.append("No grants yet. Use propose to create one.")

        return "\n".join(lines)


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================

# Old name → new name (for gradual migration)
CovenantNode = GrantNode

# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GrantNode",
    "CovenantNode",  # Backwards compat
]
