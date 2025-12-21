"""
AGENTESE Concept Scope Context: Explicit Context Contract.

Context-related nodes for concept.scope.* paths:
- ScopeNode: Budget-constrained context management

This node provides AGENTESE access to the Scope primitive for
explicit, priced context contracts.

AGENTESE Paths:
    concept.scope.manifest  - Show active scopes
    concept.scope.create    - Create a new scope
    concept.scope.consume   - Consume resources from a scope
    concept.scope.extend    - Extend a scope's budget/expiry
    concept.scope.status    - Check scope validity

See: services/witness/scope.py
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

_scope_store: dict[str, Any] = {}


def _get_scope(scope_id: str) -> Any | None:
    """Get scope by ID."""
    return _scope_store.get(scope_id)


def _add_scope(scope: Any) -> None:
    """Add scope to store."""
    _scope_store[str(scope.id)] = scope


def _update_scope(scope_id: str, new_scope: Any) -> None:
    """Update scope in store."""
    _scope_store[scope_id] = new_scope


# =============================================================================
# ScopeNode: AGENTESE Interface to Scope
# =============================================================================


SCOPE_AFFORDANCES: tuple[str, ...] = ("manifest", "create", "consume", "extend", "status")


@node(
    "concept.scope",
    description="Explicit context contracts with budget constraints",
)
@dataclass
class ScopeNode(BaseLogosNode):
    """
    concept.scope - Explicit context contracts.

    A Scope defines:
    - What handles are accessible (scope)
    - What resources can be consumed (budget)
    - When access expires (expiry)

    Laws (from scope.py):
    - Law 1 (Budget Enforcement): Exceeding budget triggers review
    - Law 2 (Immutability): Scopes are frozen after creation
    - Law 3 (Expiry Honored): Expired Scopes deny access

    AGENTESE: concept.scope.*
    """

    _handle: str = "concept.scope"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Scope affordances available to all archetypes."""
        return SCOPE_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show active scopes.

        Returns:
            List of scopes with budget status
        """
        # Collect stats
        total = len(_scope_store)
        valid = sum(1 for o in _scope_store.values() if o.is_valid())
        exhausted = sum(1 for o in _scope_store.values() if o.budget.is_exhausted)

        recent = sorted(
            _scope_store.values(),
            key=lambda o: o.created_at,
            reverse=True,
        )[:5]

        manifest_data = {
            "path": self.handle,
            "description": "Explicit context contracts with budget",
            "total_scopes": total,
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
                "Law 2: Scopes are frozen after creation",
                "Law 3: Expired Scopes deny access",
            ],
        }

        return BasicRendering(
            summary="Scopes (Context Contracts)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Scope-specific aspects."""
        match aspect:
            case "create":
                return self._create_scope(**kwargs)
            case "consume":
                return self._consume_scope(**kwargs)
            case "extend":
                return self._extend_scope(**kwargs)
            case "status":
                return self._check_status(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Create a new scope with budget constraints",
    )
    def _create_scope(
        self,
        tokens: int | None = None,
        operations: int | None = None,
        time_seconds: float | None = None,
        expires_in_minutes: int | None = None,
        scoped_handles: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new Scope.

        Args:
            tokens: Max LLM tokens to consume
            operations: Max discrete operations
            time_seconds: Max wall-clock time
            expires_in_minutes: When this scope expires
            scoped_handles: AGENTESE handles this scope provides access to

        Returns:
            Created Scope info
        """
        from services.witness.scope import Budget, Scope

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

        # Create scope
        scope = Scope.create(
            description="AGENTESE scope",
            budget=budget,
            scoped_handles=tuple(scoped_handles) if scoped_handles else (),
            expires_at=expires_at,
        )

        # Store
        _add_scope(scope)

        return {
            "id": str(scope.id),
            "budget": {
                "tokens": tokens,
                "operations": operations,
                "time_seconds": time_seconds,
            },
            "scoped_handles": list(scoped_handles) if scoped_handles else [],
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_valid": scope.is_valid(),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Consume resources from a scope (Law 1: exceeding triggers review)",
    )
    def _consume_scope(
        self,
        scope_id: str = "",
        tokens: int = 0,
        operations: int = 0,
        time_seconds: float = 0.0,
    ) -> dict[str, Any]:
        """
        Consume resources from a Scope.

        Law 1: Exceeding budget triggers review, not silent failure.
        Law 2: Returns a new Scope (immutability).
        """
        if not scope_id:
            return {"error": "scope_id is required"}

        scope = _get_scope(scope_id)
        if scope is None:
            return {"error": f"Scope {scope_id} not found"}

        # Check validity
        if not scope.is_valid():
            return {
                "error": "Scope is no longer valid",
                "is_expired": scope.is_expired if hasattr(scope, "is_expired") else None,
                "is_exhausted": scope.budget.is_exhausted,
            }

        # Try to consume
        try:
            new_scope = scope.consume(
                tokens=tokens,
                operations=operations,
                time_seconds=time_seconds,
            )
            # Update store with new scope (Law 2: immutability)
            _update_scope(scope_id, new_scope)

            return {
                "scope_id": scope_id,
                "consumed": {
                    "tokens": tokens,
                    "operations": operations,
                    "time_seconds": time_seconds,
                },
                "remaining": {
                    "tokens": new_scope.budget.tokens,
                    "operations": new_scope.budget.operations,
                    "time_seconds": new_scope.budget.time_seconds,
                },
                "is_valid": new_scope.is_valid(),
            }
        except Exception as e:
            # Law 1: Budget exceeded triggers review
            return {
                "error": "budget_exceeded",
                "message": str(e),
                "action_required": "Review and extend scope, or create new one",
            }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Extend a scope's budget or expiry",
    )
    def _extend_scope(
        self,
        scope_id: str = "",
        add_tokens: int = 0,
        add_operations: int = 0,
        add_time_seconds: float = 0.0,
        extend_expiry_minutes: int = 0,
    ) -> dict[str, Any]:
        """
        Extend a Scope's budget or expiry.

        Creates a new Scope with extended limits (Law 2: immutability).
        """
        if not scope_id:
            return {"error": "scope_id is required"}

        scope = _get_scope(scope_id)
        if scope is None:
            return {"error": f"Scope {scope_id} not found"}

        # Create extended scope
        new_scope = scope.extend(
            add_tokens=add_tokens,
            add_operations=add_operations,
            add_time_seconds=add_time_seconds,
            extend_expiry_minutes=extend_expiry_minutes,
        )

        # Update store
        _update_scope(scope_id, new_scope)

        return {
            "scope_id": scope_id,
            "extended": {
                "tokens": add_tokens,
                "operations": add_operations,
                "time_seconds": add_time_seconds,
                "expiry_minutes": extend_expiry_minutes,
            },
            "new_budget": {
                "tokens": new_scope.budget.tokens,
                "operations": new_scope.budget.operations,
                "time_seconds": new_scope.budget.time_seconds,
            },
            "expires_at": new_scope.expires_at.isoformat() if new_scope.expires_at else None,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Check scope validity and remaining budget",
    )
    def _check_status(
        self,
        scope_id: str = "",
    ) -> dict[str, Any]:
        """
        Check status of a Scope.

        Law 3: Expired Scopes deny access.
        """
        if not scope_id:
            return {"error": "scope_id is required"}

        scope = _get_scope(scope_id)
        if scope is None:
            return {"error": f"Scope {scope_id} not found"}

        return {
            "scope_id": scope_id,
            "is_valid": scope.is_valid(),
            "is_exhausted": scope.budget.is_exhausted,
            "budget": {
                "tokens": scope.budget.tokens,
                "operations": scope.budget.operations,
                "time_seconds": scope.budget.time_seconds,
            },
            "expires_at": scope.expires_at.isoformat() if scope.expires_at else None,
            "scoped_handles": list(scope.scoped_handles)
            if hasattr(scope, "scoped_handles")
            else [],
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Scopes (Context Contracts)",
            "=" * 40,
            "",
            f"Total: {data['total_scopes']}",
            f"Valid: {data['valid_count']}",
            f"Exhausted: {data['exhausted_count']}",
            "",
        ]

        if data["recent"]:
            lines.append("Recent Scopes:")
            for o in data["recent"]:
                status_icon = "o" if o["is_valid"] else "x"
                budget = o["budget"]
                budget_str = f"T:{budget['tokens'] or '?'} O:{budget['operations'] or '?'}"
                lines.append(f"  {status_icon} {o['id'][:20]} [{budget_str}]")
        else:
            lines.append("No scopes yet. Use create to make one.")

        return "\n".join(lines)


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================

# Old name → new name (for gradual migration)
OfferingNode = ScopeNode

# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ScopeNode",
    "OfferingNode",  # Backwards compat
]
