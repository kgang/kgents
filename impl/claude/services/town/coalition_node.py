"""
Coalition AGENTESE Node: @node("world.town.coalition")

Wraps CoalitionService as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- world.town.coalition.manifest - Coalition system overview
- world.town.coalition.list     - List all coalitions
- world.town.coalition.get      - Get coalition by ID
- world.town.coalition.detect   - Detect coalitions from citizens
- world.town.coalition.decay    - Apply decay to all coalitions
- world.town.coalition.bridges  - Get bridge citizens

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
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

from .coalition_service import Coalition, CoalitionService
from .contracts import (
    BridgeCitizensResponse,
    CoalitionDecayResponse,
    CoalitionDetail,
    CoalitionDetectRequest,
    CoalitionDetectResponse,
    CoalitionListResponse,
    CoalitionManifestResponse,
    CoalitionSummary,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Coalition Node Rendering ===


@dataclass(frozen=True)
class CoalitionManifestRendering:
    """Rendering for coalition system manifest."""

    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "coalition_manifest",
            **self.summary,
        }

    def to_text(self) -> str:
        lines = [
            "Coalition System Status",
            "======================",
            f"Total Coalitions: {self.summary.get('total_coalitions', 0)}",
            f"Alive Coalitions: {self.summary.get('alive_coalitions', 0)}",
            f"Total Members: {self.summary.get('total_members', 0)}",
            f"Bridge Citizens: {self.summary.get('bridge_citizens', 0)}",
            f"Average Strength: {self.summary.get('avg_strength', 0.0):.2f}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class CoalitionRendering:
    """Rendering for coalition details."""

    coalition: Coalition

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "coalition",
            "id": self.coalition.id,
            "name": self.coalition.name,
            "members": list(self.coalition.members),
            "strength": self.coalition.strength,
            "purpose": self.coalition.purpose,
            "size": self.coalition.size,
            "formed_at": self.coalition.formed_at.isoformat(),
        }

    def to_text(self) -> str:
        lines = [
            f"Coalition: {self.coalition.name}",
            f"ID: {self.coalition.id}",
            f"Members: {self.coalition.size}",
            f"Strength: {self.coalition.strength:.2f}",
            f"Purpose: {self.coalition.purpose}",
            f"Formed: {self.coalition.formed_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            "Members:",
        ]
        for member_id in sorted(self.coalition.members):
            lines.append(f"  - {member_id}")
        return "\n".join(lines)


@dataclass(frozen=True)
class CoalitionListRendering:
    """Rendering for coalition list."""

    coalitions: list[Coalition]
    bridge_citizens: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "coalition_list",
            "total": len(self.coalitions),
            "coalitions": [
                {
                    "id": c.id,
                    "name": c.name,
                    "size": c.size,
                    "strength": c.strength,
                    "purpose": c.purpose,
                    "is_alive": c.is_alive(),
                }
                for c in self.coalitions
            ],
            "bridge_citizens": self.bridge_citizens,
        }

    def to_text(self) -> str:
        if not self.coalitions:
            return "No coalitions detected"
        lines = [f"Coalitions ({len(self.coalitions)}):", ""]
        for c in self.coalitions:
            status = "✓" if c.is_alive() else "✗"
            strength_bar = "█" * int(c.strength * 10)
            lines.append(
                f"  {status} {c.name} ({c.size} members) [{strength_bar}] {c.strength:.2f}"
            )
        if self.bridge_citizens:
            lines.extend(
                [
                    "",
                    f"Bridge Citizens ({len(self.bridge_citizens)}):",
                    ", ".join(sorted(self.bridge_citizens)),
                ]
            )
        return "\n".join(lines)


# === Coalition Node ===


@node(
    "world.town.coalition",
    description="Coalition detection and reputation system using k-clique percolation",
    dependencies=("coalition_service",),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(CoalitionManifestResponse),
        "list": Response(CoalitionListResponse),
        "get": Response(CoalitionDetail),
        "bridges": Response(BridgeCitizensResponse),
        # Mutation aspects (Contract with request + response)
        "detect": Contract(CoalitionDetectRequest, CoalitionDetectResponse),
        "decay": Response(CoalitionDecayResponse),
    },
)
class CoalitionNode(BaseLogosNode):
    """
    AGENTESE node for Coalition Detection Crown Jewel.

    Exposes CoalitionService through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/town/coalition/detect
        {"similarity_threshold": 0.8, "k": 3}

        # Via Logos directly
        await logos.invoke("world.town.coalition.detect", observer, k=3)

        # Via CLI
        kgents town coalition detect --k 3
    """

    def __init__(self, coalition_service: CoalitionService) -> None:
        """
        Initialize CoalitionNode.

        CoalitionService is REQUIRED. Use ServiceContainer for full DI.

        Args:
            coalition_service: The coalition service (injected by container)

        Raises:
            TypeError: If coalition_service is not provided (intentional for fallback)
        """
        self._service = coalition_service

    @property
    def handle(self) -> str:
        return "world.town.coalition"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations (list, get, manifest) available to all archetypes.
        Mutation operations (detect, decay) restricted to privileged archetypes.
        """
        # Core operations available to all archetypes
        base = ("manifest", "list", "get", "bridges")

        if archetype in ("developer", "admin", "system"):
            # Full access including mutations
            return base + ("detect", "decay")
        elif archetype in ("researcher", "analyst"):
            # Read access plus detection (non-destructive)
            return base + ("detect",)
        else:
            # Standard read-only access
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest coalition system status to observer.

        AGENTESE: world.town.coalition.manifest
        """
        if self._service is None:
            return BasicRendering(
                summary="Coalition system not initialized",
                content="No coalition service configured",
                metadata={"error": "no_service"},
            )

        summary = self._service.summary()
        return CoalitionManifestRendering(summary=summary)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to coalition service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._service is None:
            return {"error": "Coalition service not configured"}

        # === Coalition Operations ===

        if aspect == "list":
            coalitions = list(self._service.coalitions.values())
            bridge_citizens = self._service.get_bridge_citizens()

            # Convert to contract types
            summaries = [
                CoalitionSummary(
                    id=c.id,
                    name=c.name,
                    member_count=c.size,
                    strength=c.strength,
                    purpose=c.purpose,
                )
                for c in coalitions
            ]

            return {
                "coalitions": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "member_count": s.member_count,
                        "strength": s.strength,
                        "purpose": s.purpose,
                    }
                    for s in summaries
                ],
                "total": len(summaries),
                "bridge_citizens": bridge_citizens,
            }

        elif aspect == "get":
            coalition_id = kwargs.get("coalition_id") or kwargs.get("id")
            if not coalition_id:
                return {"error": "coalition_id required"}

            coalition = self._service.get_coalition(coalition_id)
            if coalition is None:
                return {"error": f"Coalition not found: {coalition_id}"}

            return CoalitionRendering(coalition=coalition).to_dict()

        elif aspect == "detect":
            # Requires citizens dict - need to get from TownPersistence
            # For now, return placeholder
            similarity_threshold = kwargs.get("similarity_threshold", 0.8)
            k = kwargs.get("k", 3)

            # This would normally come from TownPersistence or be passed in
            citizens = kwargs.get("citizens", {})
            if not citizens:
                return {
                    "error": "Citizens dict required for detection",
                    "hint": "Pass citizens or wire to TownPersistence",
                }

            # Update service config
            self._service._similarity_threshold = similarity_threshold
            self._service._k = k

            # Detect coalitions
            coalitions = self._service.detect(citizens)

            # Convert to contract types
            details = [
                CoalitionDetail(
                    id=c.id,
                    name=c.name,
                    members=list(c.members),
                    strength=c.strength,
                    purpose=c.purpose,
                    formed_at=c.formed_at.isoformat(),
                    centroid=(
                        {
                            "warmth": c._centroid.warmth,
                            "curiosity": c._centroid.curiosity,
                            "trust": c._centroid.trust,
                            "creativity": c._centroid.creativity,
                            "patience": c._centroid.patience,
                            "resilience": c._centroid.resilience,
                            "ambition": c._centroid.ambition,
                        }
                        if c._centroid
                        else None
                    ),
                )
                for c in coalitions
            ]

            return {
                "coalitions": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "members": d.members,
                        "strength": d.strength,
                        "purpose": d.purpose,
                        "formed_at": d.formed_at,
                        "centroid": d.centroid,
                    }
                    for d in details
                ],
                "detected_count": len(details),
            }

        elif aspect == "bridges":
            bridge_citizens = self._service.get_bridge_citizens()
            return {
                "bridge_citizens": bridge_citizens,
                "count": len(bridge_citizens),
            }

        elif aspect == "decay":
            rate = kwargs.get("rate", 0.05)
            pruned = self._service.decay_all(rate)
            return {
                "pruned_count": pruned,
                "remaining_count": len(self._service.coalitions),
                "decay_rate": rate,
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "CoalitionNode",
    "CoalitionManifestRendering",
    "CoalitionRendering",
    "CoalitionListRendering",
]
