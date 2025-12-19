"""
Town INHABIT AGENTESE Node: @node("world.town.inhabit")

Exposes INHABIT sessions through the universal gateway for real-time
citizen inhabitation with consent tracking.

AGENTESE Paths:
- world.town.inhabit.manifest   - Show session status
- world.town.inhabit.start      - Start INHABIT session with a citizen
- world.town.inhabit.suggest    - Suggest an action (collaborative)
- world.town.inhabit.force      - Force an action (consent debt)
- world.town.inhabit.apologize  - Reduce consent debt
- world.town.inhabit.end        - End session gracefully
- world.town.inhabit.list       - List active sessions (admin)

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

From Glissant: To inhabit is not to possess. The opacity remains.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .inhabit_service import (
    InhabitService,
    InhabitSession,
    InhabitTier,
)

if TYPE_CHECKING:
    from agents.town.citizen import Citizen
    from bootstrap.umwelt import Umwelt


# =============================================================================
# InhabitNode Renderings
# =============================================================================


@dataclass(frozen=True)
class InhabitSessionRendering:
    """Rendering for INHABIT session status."""

    status: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "inhabit_session",
            **self.status,
        }

    def to_text(self) -> str:
        lines = [
            f"INHABIT Session: {self.status.get('citizen', 'Unknown')}",
            "=" * 40,
            f"Tier: {self.status.get('tier', 'unknown')}",
            f"Duration: {self.status.get('duration', 0):.0f}s / {self.status.get('time_remaining', 0):.0f}s remaining",
            "",
            "Consent:",
            f"  Debt: {self.status.get('consent', {}).get('debt', 0):.2f}",
            f"  Status: {self.status.get('consent', {}).get('status', 'unknown')}",
            f"  Can Force: {self.status.get('consent', {}).get('can_force', False)}",
        ]

        force = self.status.get("force", {})
        if force.get("enabled"):
            lines.extend(
                [
                    "",
                    "Force:",
                    f"  Used: {force.get('used', 0)} / {force.get('limit', 0)}",
                    f"  Remaining: {force.get('remaining', 0)}",
                ]
            )

        if self.status.get("expired"):
            lines.append("\n⚠️ Session Expired")

        return "\n".join(lines)


@dataclass(frozen=True)
class InhabitActionRendering:
    """Rendering for INHABIT action results."""

    action_type: str
    success: bool
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "inhabit_action",
            "action_type": self.action_type,
            "success": self.success,
            "message": self.message,
            **self.details,
        }

    def to_text(self) -> str:
        status = "✓" if self.success else "✗"
        lines = [f"[{status}] {self.action_type.upper()}: {self.message}"]

        if "debt" in self.details:
            lines.append(f"    Consent debt: {self.details['debt']:.2f}")
        if "forces_remaining" in self.details:
            lines.append(f"    Forces remaining: {self.details['forces_remaining']}")

        return "\n".join(lines)


@dataclass(frozen=True)
class InhabitListRendering:
    """Rendering for active sessions list."""

    sessions: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "inhabit_list",
            "count": len(self.sessions),
            "sessions": self.sessions,
        }

    def to_text(self) -> str:
        if not self.sessions:
            return "No active INHABIT sessions"

        lines = [f"Active INHABIT Sessions ({len(self.sessions)}):", ""]
        for sess in self.sessions:
            status = "expired" if sess.get("expired") else "active"
            debt = sess.get("consent", {}).get("debt", 0)
            lines.append(
                f"  • {sess.get('user_id', 'unknown')} → {sess.get('citizen', 'unknown')} "
                f"[{status}] debt={debt:.2f}"
            )
        return "\n".join(lines)


# =============================================================================
# InhabitNode
# =============================================================================


@node(
    "world.town.inhabit",
    description="INHABIT mode - User-Citizen merge with consent tracking",
    dependencies=("inhabit_service", "citizen_resolver"),
)
class InhabitNode(BaseLogosNode):
    """
    AGENTESE node for INHABIT Crown Jewel feature.

    INHABIT mode is where users collaborate with citizens while respecting autonomy:
    - Consent debt meter tracks relationship health
    - Force mechanic is expensive, logged, and limited
    - Citizens can resist and refuse at rupture
    - Session caps prevent abuse

    From Glissant: To inhabit is not to possess. The opacity remains.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/town/inhabit/start
        {"citizen_id": "socrates-001", "force_enabled": true}

        # Via Logos directly
        await logos.invoke("world.town.inhabit.start", observer, citizen_id="socrates-001")

        # Via CLI
        kgents town inhabit start Socrates --force-enabled
    """

    def __init__(
        self,
        inhabit_service: InhabitService,
        citizen_resolver: Any = None,  # Callable to resolve citizen by ID/name
    ) -> None:
        """
        Initialize InhabitNode.

        Args:
            inhabit_service: Service managing INHABIT sessions
            citizen_resolver: Async function to resolve Citizen by ID or name

        Raises:
            TypeError: If inhabit_service is not provided
        """
        self._service = inhabit_service
        self._resolve_citizen = citizen_resolver

    @property
    def handle(self) -> str:
        return "world.town.inhabit"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations (start, suggest, end) available to most archetypes.
        Force requires consent and privileged tier.
        Admin operations (list) restricted.
        """
        # Basic operations for users
        base = ("start", "suggest", "apologize", "end")

        if archetype in ("developer", "admin", "system"):
            # Full access including admin operations
            return base + ("force", "list", "status")
        elif archetype in ("citizen", "founder"):
            # Full INHABIT with force (if tier allows)
            return base + ("force", "status")
        elif archetype in ("resident",):
            # Basic INHABIT without force
            return base + ("status",)
        else:
            # Tourists can view but not inhabit
            return ("status",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest INHABIT status overview.

        Returns service status: active sessions count, etc.

        AGENTESE: world.town.inhabit.manifest
        """
        if self._service is None:
            return BasicRendering(
                summary="INHABIT service not initialized",
                content="No InhabitService configured",
                metadata={"error": "no_service"},
            )

        sessions = self._service.list_active_sessions()
        return InhabitListRendering(sessions=sessions)

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
        if self._service is None:
            return {"error": "INHABIT service not configured"}

        # Extract user_id from observer
        user_id = self._extract_user_id(observer)

        # === Session Lifecycle ===

        if aspect == "start":
            return await self._start_session(user_id, observer, **kwargs)

        elif aspect == "end":
            return await self._end_session(user_id)

        elif aspect == "status":
            return await self._get_status(user_id, **kwargs)

        # === Session Actions ===

        elif aspect == "suggest":
            return await self._suggest_action(user_id, **kwargs)

        elif aspect == "force":
            return await self._force_action(user_id, **kwargs)

        elif aspect == "apologize":
            return await self._apologize(user_id, **kwargs)

        # === Admin Operations ===

        elif aspect == "list":
            sessions = self._service.list_active_sessions()
            return InhabitListRendering(sessions=sessions).to_dict()

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    # =========================================================================
    # Session Lifecycle
    # =========================================================================

    async def _start_session(
        self,
        user_id: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start a new INHABIT session."""
        citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
        citizen_name = kwargs.get("name")
        force_enabled = kwargs.get("force_enabled", False)

        # Resolve citizen
        citizen = await self._get_citizen(citizen_id, citizen_name)
        if citizen is None:
            return {"error": f"Citizen not found: {citizen_id or citizen_name}"}

        # Determine tier from observer
        tier = self._extract_tier(observer)

        # Check tier permissions
        if tier == InhabitTier.TOURIST:
            return {"error": "INHABIT not available for tourist tier. Please upgrade."}

        try:
            session = self._service.start_session(
                user_id=user_id,
                citizen=citizen,
                tier=tier,
                force_enabled=force_enabled and tier != InhabitTier.RESIDENT,
            )
            return InhabitSessionRendering(status=session.get_status()).to_dict()
        except ValueError as e:
            return {"error": str(e)}

    async def _end_session(self, user_id: str) -> dict[str, Any]:
        """End a user's INHABIT session."""
        result = self._service.end_session(user_id)
        if result is None:
            return {"error": "No active session found"}

        return InhabitActionRendering(
            action_type="end",
            success=True,
            message="Session ended gracefully",
            details={"final_state": result},
        ).to_dict()

    async def _get_status(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        """Get current session status."""
        # Allow querying other user's status for admin
        target_user = kwargs.get("target_user_id") or user_id

        session = self._service.get_session(target_user)
        if session is None:
            return {"error": "No active session found"}

        return InhabitSessionRendering(status=session.get_status()).to_dict()

    # =========================================================================
    # Session Actions
    # =========================================================================

    async def _suggest_action(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        """Suggest a collaborative action."""
        session = self._service.get_session(user_id)
        if session is None:
            return {"error": "No active session. Start one first."}

        action = kwargs.get("action", "")
        if not action:
            return {"error": "action parameter required"}

        if session.is_expired():
            return {"error": "Session expired. Start a new one."}

        result = session.suggest_action(action)
        return InhabitActionRendering(
            action_type="suggest",
            success=result["success"],
            message=result["message"],
            details={
                "action": action,
                "debt": session.consent.debt,
            },
        ).to_dict()

    async def _force_action(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        """Force an action with consent debt."""
        session = self._service.get_session(user_id)
        if session is None:
            return {"error": "No active session. Start one first."}

        action = kwargs.get("action", "")
        severity = kwargs.get("severity", 0.2)

        if not action:
            return {"error": "action parameter required"}

        if session.is_expired():
            return {"error": "Session expired. Start a new one."}

        try:
            result = session.force_action(action, severity)
            return InhabitActionRendering(
                action_type="force",
                success=result["success"],
                message=result["message"],
                details={
                    "action": action,
                    "debt": result["debt"],
                    "forces_remaining": result["forces_remaining"],
                },
            ).to_dict()
        except ValueError as e:
            return {"error": str(e)}

    async def _apologize(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        """Apologize to reduce consent debt."""
        session = self._service.get_session(user_id)
        if session is None:
            return {"error": "No active session. Start one first."}

        sincerity = kwargs.get("sincerity", 0.3)

        if session.is_expired():
            return {"error": "Session expired. Start a new one."}

        result = session.apologize(sincerity)
        return InhabitActionRendering(
            action_type="apologize",
            success=True,
            message=result["message"],
            details={
                "debt": result["debt_after"],
                "debt_reduced": result["debt_before"] - result["debt_after"],
            },
        ).to_dict()

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _extract_user_id(self, observer: "Observer | Umwelt[Any, Any]") -> str:
        """Extract user ID from observer."""
        if isinstance(observer, Observer):
            # Use archetype as fallback user ID for lightweight observers
            return f"observer:{observer.archetype}"

        # Try to get from Umwelt DNA
        dna = getattr(observer, "dna", None)
        if dna:
            user_id = getattr(dna, "user_id", None) or getattr(dna, "name", None)
            if user_id:
                return str(user_id)

        return "anonymous"

    def _extract_tier(self, observer: "Observer | Umwelt[Any, Any]") -> InhabitTier:
        """Extract subscription tier from observer."""
        if isinstance(observer, Observer):
            # Map archetype to tier
            tier_map = {
                "developer": InhabitTier.FOUNDER,
                "admin": InhabitTier.FOUNDER,
                "system": InhabitTier.FOUNDER,
                "founder": InhabitTier.FOUNDER,
                "citizen": InhabitTier.CITIZEN,
                "resident": InhabitTier.RESIDENT,
            }
            return tier_map.get(observer.archetype, InhabitTier.TOURIST)

        # Try to get from Umwelt DNA
        dna = getattr(observer, "dna", None)
        if dna:
            tier_str = getattr(dna, "subscription_tier", None)
            if tier_str:
                try:
                    return InhabitTier(tier_str)
                except ValueError:
                    pass

        return InhabitTier.TOURIST

    async def _get_citizen(
        self, citizen_id: str | None, citizen_name: str | None
    ) -> "Citizen | None":
        """Resolve citizen by ID or name."""
        if self._resolve_citizen is None:
            return None

        try:
            if citizen_id:
                return await self._resolve_citizen(citizen_id=citizen_id)
            elif citizen_name:
                return await self._resolve_citizen(name=citizen_name)
        except Exception as e:
            logger.warning(f"Failed to resolve citizen (id={citizen_id}, name={citizen_name}): {e}")

        return None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "InhabitNode",
    "InhabitSessionRendering",
    "InhabitActionRendering",
    "InhabitListRendering",
]
