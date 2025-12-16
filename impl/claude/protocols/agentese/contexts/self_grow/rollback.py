"""
self.grow.rollback - Promotion Rollback

Rolls back promoted holons using their rollback tokens.

AGENTESE: self.grow.rollback
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError, RollbackError
from .schemas import (
    SELF_GROW_AFFORDANCES,
    PromotionStage,
    RollbackResult,
    RollbackToken,
)
from .telemetry import metrics, tracer

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Rollback Node ===


@dataclass
class RollbackNode(BaseLogosNode):
    """
    self.grow.rollback - Promotion rollback node.

    Rolls back promoted holons using their rollback tokens.

    Affordances:
    - manifest: View available rollback tokens
    - revert: Roll back a promoted holon
    - tokens: List active rollback tokens
    - expire: Clean up expired tokens

    AGENTESE: self.grow.rollback.*
    """

    _handle: str = "self.grow.rollback"

    # Rollback tokens (shared with promote node, keyed by handle)
    _rollback_tokens: dict[str, RollbackToken] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self._rollback_tokens is None:
            self._rollback_tokens = {}

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Rollback requires gardener or admin affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if "rollback" in affordances:
            return ("revert", "tokens", "expire")
        return ("tokens",)  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View rollback status."""
        active = [t for t in self._rollback_tokens.values() if not t.is_expired]
        expired = [t for t in self._rollback_tokens.values() if t.is_expired]

        return BasicRendering(
            summary=f"Rollback Tokens: {len(active)} active, {len(expired)} expired",
            content=self._format_tokens(active[:5]),
            metadata={
                "active_count": len(active),
                "expired_count": len(expired),
                "tokens": [
                    {
                        "token_id": t.token_id,
                        "handle": t.handle,
                        "promoted_at": t.promoted_at.isoformat(),
                        "expires_at": t.expires_at.isoformat(),
                        "is_expired": t.is_expired,
                    }
                    for t in active[:10]
                ],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle rollback aspects."""
        match aspect:
            case "revert":
                return await self._revert(observer, **kwargs)
            case "tokens":
                return self._list_tokens(**kwargs)
            case "expire":
                return self._expire_tokens(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _revert(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Roll back a promoted holon.

        Args:
            handle: Handle of the holon to roll back
            token_id: Rollback token ID (alternative to handle)

        Returns:
            Dict with rollback result
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "rollback" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot rollback",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Find token
        handle = kwargs.get("handle")
        token_id = kwargs.get("token_id")

        token: RollbackToken | None = None
        if handle:
            token = self._rollback_tokens.get(handle)
        elif token_id:
            for t in self._rollback_tokens.values():
                if t.token_id == token_id:
                    token = t
                    break

        if token is None:
            raise RollbackError(
                f"Rollback token not found for handle={handle} or token_id={token_id}",
                token_id=token_id,
            )

        # Check if expired
        if token.is_expired:
            raise RollbackError(
                f"Rollback token expired at {token.expires_at.isoformat()}",
                token_id=token.token_id,
            )

        async with tracer.start_span_async("growth.rollback") as span:
            span.set_attribute("growth.phase", "rollback")
            span.set_attribute("growth.rollback.handle", token.handle)
            span.set_attribute("growth.rollback.token_id", token.token_id)

            restored_spec = False
            restored_impl = False
            errors = []

            # Delete spec file if it exists
            if token.spec_path.exists():
                try:
                    token.spec_path.unlink()
                    restored_spec = True
                except Exception as e:
                    errors.append(f"Failed to delete spec: {e}")

            # Delete impl file if it exists
            if token.impl_path.exists():
                try:
                    token.impl_path.unlink()
                    restored_impl = True
                except Exception as e:
                    errors.append(f"Failed to delete impl: {e}")

            # Remove the token
            if token.handle in self._rollback_tokens:
                del self._rollback_tokens[token.handle]

            # Record metrics
            metrics.counter("growth.rollback.invocations").add(1)

            if errors:
                span.set_status("ERROR", "; ".join(errors))
                return {
                    "status": "partial",
                    "handle": token.handle,
                    "restored_spec": restored_spec,
                    "restored_impl": restored_impl,
                    "errors": errors,
                }

        return {
            "status": "rolled_back",
            "handle": token.handle,
            "restored_spec": restored_spec,
            "restored_impl": restored_impl,
        }

    def _list_tokens(self, **kwargs: Any) -> dict[str, Any]:
        """List rollback tokens."""
        include_expired = kwargs.get("include_expired", False)
        limit = kwargs.get("limit", 20)

        tokens = list(self._rollback_tokens.values())
        if not include_expired:
            tokens = [t for t in tokens if not t.is_expired]

        return {
            "tokens": [
                {
                    "token_id": t.token_id,
                    "handle": t.handle,
                    "promoted_at": t.promoted_at.isoformat(),
                    "expires_at": t.expires_at.isoformat(),
                    "is_expired": t.is_expired,
                }
                for t in tokens[:limit]
            ],
            "total": len(tokens),
            "total_expired": sum(
                1 for t in self._rollback_tokens.values() if t.is_expired
            ),
        }

    def _expire_tokens(self, **kwargs: Any) -> dict[str, Any]:
        """Clean up expired tokens."""
        expired = [
            handle
            for handle, token in self._rollback_tokens.items()
            if token.is_expired
        ]

        for handle in expired:
            del self._rollback_tokens[handle]

        return {
            "status": "cleaned",
            "expired_count": len(expired),
            "expired_handles": expired,
            "remaining": len(self._rollback_tokens),
        }

    def add_token(self, token: RollbackToken) -> None:
        """Add a rollback token (called by promote node)."""
        self._rollback_tokens[token.handle] = token

    def get_token(self, handle: str) -> RollbackToken | None:
        """Get a rollback token by handle."""
        return self._rollback_tokens.get(handle)

    def _format_tokens(self, tokens: list[RollbackToken]) -> str:
        """Format tokens for display."""
        if not tokens:
            return "No active rollback tokens"

        lines = []
        for t in tokens:
            lines.append(
                f"  {t.handle}"
                + f" [promoted {t.promoted_at.strftime('%Y-%m-%d')}]"
                + f" expires {t.expires_at.strftime('%Y-%m-%d')}"
            )
        return "\n".join(lines)


# === Factory ===


def create_rollback_node(
    rollback_tokens: dict[str, RollbackToken] | None = None,
) -> RollbackNode:
    """
    Create a RollbackNode with optional configuration.

    Args:
        rollback_tokens: Shared rollback token dict (from promote node)

    Returns:
        Configured RollbackNode
    """
    node = RollbackNode(_rollback_tokens=rollback_tokens)
    node.__post_init__()
    return node
