"""
AGENTESE Self Semaphore Context

Semaphore-related nodes for self.semaphore.* paths.

Provides access to semaphore tokens that require human intervention:
- pending: List pending semaphores for this agent
- yield: Create a new semaphore (agent yields control)
- status: Get status of a specific semaphore

Integration with Purgatory:
The SemaphoreNode bridges the AGENTESE path system with the
Agent Semaphore system, allowing agents to query and create
semaphores through the standard AGENTESE interface.

Extracted from self_.py for maintainability.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Semaphore Affordances ===

SEMAPHORE_AFFORDANCES: tuple[str, ...] = ("pending", "yield", "status")


# === Semaphore Node ===


@dataclass
class SemaphoreNode(BaseLogosNode):
    """
    self.semaphore - Agent's pending semaphores.

    Provides access to semaphore tokens that require human intervention:
    - pending: List pending semaphores for this agent
    - yield: Create a new semaphore (agent yields control)
    - status: Get status of a specific semaphore

    Integration with Purgatory:
    The SemaphoreNode bridges the AGENTESE path system with the
    Agent Semaphore system, allowing agents to query and create
    semaphores through the standard AGENTESE interface.

    AGENTESE: self.semaphore.*
    """

    _handle: str = "self.semaphore"

    # Integration points
    _purgatory: Any = None  # Purgatory instance for token storage

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Semaphore affordances available to all archetypes."""
        return SEMAPHORE_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View pending semaphores for this agent."""
        pending = await self._get_pending(observer)
        return BasicRendering(
            summary="Pending Semaphores",
            content=f"Pending: {len(pending)} semaphores awaiting response",
            metadata={
                "pending_count": len(pending),
                "semaphore_ids": [t.get("id") for t in pending],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle semaphore-specific aspects."""
        match aspect:
            case "pending":
                return await self._get_pending(observer, **kwargs)
            case "yield":
                return await self._yield_semaphore(observer, **kwargs)
            case "status":
                return await self._get_status(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_pending(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List pending semaphores for this agent.

        Returns list of token summaries (not full token objects to avoid
        leaking frozen state).
        """
        if self._purgatory is None:
            return []

        try:
            tokens = self._purgatory.list_pending()
            # Filter by agent if agent_id is available in observer
            agent_id = kwargs.get("agent_id")
            if agent_id:
                # Would need to track agent_id in token for filtering
                pass

            # Return summaries, not full tokens
            return [
                {
                    "id": t.id,
                    "reason": t.reason.value if hasattr(t.reason, "value") else str(t.reason),
                    "prompt": t.prompt,
                    "options": t.options,
                    "severity": t.severity,
                    "deadline": t.deadline.isoformat() if t.deadline else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in tokens
            ]
        except Exception:
            return []

    async def _yield_semaphore(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new semaphore (agent yields control).

        This is the AGENTESE interface for creating semaphores.
        Agents call this when they need human intervention.

        Args:
            reason: Why the semaphore is needed (approval_needed, context_required, etc.)
            prompt: Human-readable question/prompt
            options: Optional list of options to present
            severity: info, warning, or critical
            deadline: Optional deadline as ISO string or timedelta
            escalation: Optional escalation contact

        Returns:
            Dict with token_id and status
        """
        if self._purgatory is None:
            return {
                "error": "Purgatory not configured",
                "note": "SemaphoreNode requires Purgatory integration",
            }

        try:
            # Import here to avoid circular imports
            from agents.flux.semaphore import SemaphoreReason, SemaphoreToken

            # Parse reason
            reason_str = kwargs.get("reason", "approval_needed")
            try:
                reason = SemaphoreReason(reason_str)
            except ValueError:
                reason = SemaphoreReason.APPROVAL_NEEDED

            # Parse deadline
            deadline = None
            deadline_arg = kwargs.get("deadline")
            if deadline_arg:
                from datetime import timedelta

                if isinstance(deadline_arg, timedelta):
                    deadline = datetime.now() + deadline_arg
                elif isinstance(deadline_arg, str):
                    deadline = datetime.fromisoformat(deadline_arg)

            # Create token
            token: SemaphoreToken[Any] = SemaphoreToken(
                reason=reason,
                prompt=kwargs.get("prompt", ""),
                options=kwargs.get("options", []),
                severity=kwargs.get("severity", "info"),
                deadline=deadline,
                escalation=kwargs.get("escalation"),
            )

            # Save to purgatory
            await self._purgatory.save(token)

            return {
                "token_id": token.id,
                "status": "pending",
                "reason": reason.value,
                "prompt": token.prompt,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get status of a specific semaphore.

        Args:
            token_id: The semaphore token ID

        Returns:
            Token status dict or error
        """
        token_id = kwargs.get("token_id")
        if not token_id:
            return {"error": "token_id required"}

        if self._purgatory is None:
            return {"error": "Purgatory not configured"}

        try:
            token = self._purgatory.get(token_id)
            if token is None:
                return {"error": "Token not found", "token_id": token_id}

            return {
                "token_id": token.id,
                "status": (
                    "resolved"
                    if token.is_resolved
                    else "cancelled"
                    if token.is_cancelled
                    else "voided"
                    if token.is_voided
                    else "pending"
                ),
                "reason": token.reason.value
                if hasattr(token.reason, "value")
                else str(token.reason),
                "prompt": token.prompt,
                "severity": token.severity,
                "created_at": token.created_at.isoformat() if token.created_at else None,
                "resolved_at": token.resolved_at.isoformat() if token.resolved_at else None,
                "cancelled_at": token.cancelled_at.isoformat() if token.cancelled_at else None,
                "voided_at": token.voided_at.isoformat() if token.voided_at else None,
            }
        except Exception as e:
            return {"error": str(e)}
