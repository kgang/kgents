"""
Commission AGENTESE Node: @node("world.forge.commission")

Exposes CommissionService through the AGENTESE gateway.

AGENTESE Paths:
- world.forge.commission.manifest  - List commissions
- world.forge.commission.create    - Create new commission
- world.forge.commission.get       - Get commission by ID
- world.forge.commission.start     - Start K-gent review
- world.forge.commission.advance   - Advance to next artisan
- world.forge.commission.pause     - Pause commission
- world.forge.commission.resume    - Resume commission
- world.forge.commission.cancel    - Cancel commission

The Commission Workflow (The Heart of the Forge):
1. Kent describes intent (create)
2. K-gent reviews (start → PENDING → DESIGNING)
3. Each artisan works in sequence (advance)
4. K-gent approves final artifact (advance → COMPLETE)

"The Forge is where Kent builds with Kent."

See: spec/protocols/metaphysical-forge.md
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

from .commission import Commission, CommissionService, CommissionStatus
from .contracts import (
    CommissionAdvanceRequest,
    CommissionAdvanceResponse,
    CommissionCancelRequest,
    CommissionCancelResponse,
    CommissionCreateRequest,
    CommissionCreateResponse,
    CommissionGetRequest,
    CommissionGetResponse,
    CommissionListResponse,
    CommissionPauseRequest,
    CommissionPauseResponse,
    CommissionResumeRequest,
    CommissionResumeResponse,
    CommissionStartRequest,
    CommissionStartResponse,
)

if TYPE_CHECKING:
    pass


# === Rendering Types ===


@dataclass(frozen=True)
class CommissionRendering:
    """Rendering for commission details."""

    commission: Commission

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "commission",
            **self.commission.to_dict(),
        }

    def to_text(self) -> str:
        c = self.commission
        lines = [
            f"Commission: {c.name or c.id}",
            f"Status: {c.status.value}",
            f"Intent: {c.intent[:100]}{'...' if len(c.intent) > 100 else ''}",
            "",
            "Artisans:",
        ]

        artisan_order = [
            "kgent",
            "architect",
            "smith",
            "herald",
            "projector",
            "sentinel",
            "witness",
        ]

        for artisan in artisan_order:
            if artisan in c.artisan_outputs:
                output = c.artisan_outputs[artisan]
                status_icon = {
                    "pending": "○",
                    "working": "●",
                    "complete": "✓",
                    "failed": "✗",
                    "skipped": "○",
                }.get(output.status, "?")
                lines.append(f"  {status_icon} {artisan.capitalize()}: {output.status}")
            else:
                lines.append(f"  ○ {artisan.capitalize()}: pending")

        if c.soul_annotation:
            lines.append("")
            lines.append(f"K-gent: {c.soul_annotation}")

        return "\n".join(lines)


@dataclass(frozen=True)
class CommissionListRendering:
    """Rendering for list of commissions."""

    commissions: list[Commission]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "commission_list",
            "count": len(self.commissions),
            "commissions": [c.to_dict() for c in self.commissions],
        }

    def to_text(self) -> str:
        if not self.commissions:
            return "No commissions found."

        lines = [f"Commissions ({len(self.commissions)}):"]
        for c in self.commissions:
            status_icon = {
                "pending": "○",
                "designing": "🎨",
                "implementing": "🔧",
                "exposing": "📢",
                "projecting": "📺",
                "securing": "🛡️",
                "verifying": "🧪",
                "reviewing": "👁️",
                "complete": "✓",
                "rejected": "✗",
                "failed": "💥",
            }.get(c.status.value, "?")
            name = c.name or c.id[:12]
            lines.append(f"  {status_icon} {name}: {c.status.value}")

        return "\n".join(lines)


# === CommissionNode ===


@node(
    "world.forge.commission",
    description="Commission workflow for building agents",
    dependencies=("commission_service",),
    contracts={
        # Perception aspects
        "manifest": Response(CommissionListResponse),
        # Mutation aspects
        "create": Contract(CommissionCreateRequest, CommissionCreateResponse),
        "get": Contract(CommissionGetRequest, CommissionGetResponse),
        "start": Contract(CommissionStartRequest, CommissionStartResponse),
        "advance": Contract(CommissionAdvanceRequest, CommissionAdvanceResponse),
        "pause": Contract(CommissionPauseRequest, CommissionPauseResponse),
        "resume": Contract(CommissionResumeRequest, CommissionResumeResponse),
        "cancel": Contract(CommissionCancelRequest, CommissionCancelResponse),
    },
)
class CommissionNode(BaseLogosNode):
    """
    AGENTESE node for Commission workflow.

    This is the heart of the Forge - where Kent's intent becomes running agents.

    DI Requirements:
    - commission_service: CommissionService (required)
    """

    def __init__(self, commission_service: CommissionService) -> None:
        """
        Initialize CommissionNode.

        Args:
            commission_service: The CommissionService instance
        """
        self.service = commission_service

    @property
    def handle(self) -> str:
        """The AGENTESE path for this node."""
        return "world.forge.commission"

    async def get_handle_info(self, observer: Observer) -> dict[str, Any]:
        """Return handle description for world.forge.commission."""
        meta = self._umwelt_to_meta(observer)
        return {
            "path": "world.forge.commission",
            "description": "Commission workflow for building metaphysical fullstack agents",
            "observer": {"archetype": observer.archetype},
            "affordances": self.affordances(meta),
            "features": {
                "kgent_governance": self.service.soul is not None,
            },
        }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return available affordances based on observer archetype."""
        archetype_lower = archetype.lower() if archetype else "spectator"

        # All archetypes can view
        base = ("manifest", "get")

        if archetype_lower in ("developer", "admin", "system"):
            # Full access for developers
            return base + ("create", "start", "advance", "pause", "resume", "cancel")

        if archetype_lower == "curator":
            # Curators can view and manage
            return base + ("create", "start", "advance", "pause", "resume")

        # Read-only for others
        return base

    async def manifest(self, observer: Observer) -> Renderable:
        """
        AGENTESE: world.forge.commission.manifest

        Returns list of commissions.
        """
        commissions = await self.service.list()
        return CommissionListRendering(commissions)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to appropriate handlers."""

        if aspect == "create":
            intent = kwargs.get("intent")
            if not intent:
                return BasicRendering(
                    "intent is required",
                    {"error": "missing_param", "param": "intent"},
                )
            commission = await self.service.create(
                intent=intent,
                name=kwargs.get("name"),
            )
            return CommissionRendering(commission)

        if aspect == "get":
            commission_id = kwargs.get("commission_id")
            if not commission_id:
                return BasicRendering(
                    "commission_id is required",
                    {"error": "missing_param", "param": "commission_id"},
                )
            commission = await self.service.get(commission_id)
            if commission is None:
                return BasicRendering(
                    f"Commission not found: {commission_id}",
                    {"error": "not_found", "commission_id": commission_id},
                )
            return CommissionRendering(commission)

        if aspect == "start":
            commission_id = kwargs.get("commission_id")
            if not commission_id:
                return BasicRendering(
                    "commission_id is required",
                    {"error": "missing_param", "param": "commission_id"},
                )
            commission = await self.service.start_review(commission_id)
            if commission is None:
                return BasicRendering(
                    f"Cannot start commission: {commission_id}",
                    {"error": "start_failed", "commission_id": commission_id},
                )
            return CommissionRendering(commission)

        if aspect == "advance":
            commission_id = kwargs.get("commission_id")
            if not commission_id:
                return BasicRendering(
                    "commission_id is required",
                    {"error": "missing_param", "param": "commission_id"},
                )
            commission = await self.service.advance(commission_id)
            if commission is None:
                return BasicRendering(
                    f"Cannot advance commission: {commission_id}",
                    {"error": "advance_failed", "commission_id": commission_id},
                )
            return CommissionRendering(commission)

        if aspect == "pause":
            commission_id = kwargs.get("commission_id")
            if not commission_id:
                return BasicRendering(
                    "commission_id is required",
                    {"error": "missing_param", "param": "commission_id"},
                )
            commission = await self.service.pause(commission_id)
            if commission is None:
                return BasicRendering(
                    f"Cannot pause commission: {commission_id}",
                    {"error": "pause_failed", "commission_id": commission_id},
                )
            return CommissionRendering(commission)

        if aspect == "resume":
            commission_id = kwargs.get("commission_id")
            if not commission_id:
                return BasicRendering(
                    "commission_id is required",
                    {"error": "missing_param", "param": "commission_id"},
                )
            commission = await self.service.resume(commission_id)
            if commission is None:
                return BasicRendering(
                    f"Cannot resume commission: {commission_id}",
                    {"error": "resume_failed", "commission_id": commission_id},
                )
            return CommissionRendering(commission)

        if aspect == "cancel":
            commission_id = kwargs.get("commission_id")
            if not commission_id:
                return BasicRendering(
                    "commission_id is required",
                    {"error": "missing_param", "param": "commission_id"},
                )
            success = await self.service.cancel(
                commission_id,
                reason=kwargs.get("reason"),
            )
            if not success:
                return BasicRendering(
                    f"Cannot cancel commission: {commission_id}",
                    {"error": "cancel_failed", "commission_id": commission_id},
                )
            return BasicRendering(
                f"Commission cancelled: {commission_id}",
                {"success": True, "commission_id": commission_id},
            )

        # Unknown aspect
        return BasicRendering(
            f"Unknown commission aspect: {aspect}",
            {"error": "unknown_aspect", "aspect": aspect},
        )


__all__ = [
    "CommissionNode",
    "CommissionRendering",
    "CommissionListRendering",
]
