"""
Town Citizen AGENTESE Node: @node("world.town.citizen")

A navigable sub-path for the citizen registry within Agent Town.
Delegates to TownPersistence but provides its own manifest.

AGENTESE Paths:
- world.town.citizen.manifest   - Citizen registry overview
- world.town.citizen.list       - List all citizens
- world.town.citizen.get        - Get citizen by ID or name
- world.town.citizen.create     - Create new citizen
- world.town.citizen.update     - Update citizen attributes

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- Enables deep navigation (world.town → world.town.citizen)
- Sub-nodes provide focused views of parent data

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    CitizenCreateRequest,
    CitizenCreateResponse,
    CitizenGetResponse,
    CitizenListResponse,
    CitizenUpdateRequest,
    CitizenUpdateResponse,
)
from .node import CitizenListRendering, CitizenRendering
from .persistence import TownPersistence

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === CitizenNode Rendering ===


@dataclass(frozen=True)
class CitizenManifestRendering:
    """Rendering for citizen registry manifest."""

    total_citizens: int
    active_citizens: int
    archetypes: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "citizen_manifest",
            "total_citizens": self.total_citizens,
            "active_citizens": self.active_citizens,
            "archetypes": self.archetypes,
        }

    def to_text(self) -> str:
        lines = [
            "Citizen Registry",
            "================",
            f"Total: {self.total_citizens}",
            f"Active: {self.active_citizens}",
            "",
            "Archetypes:",
        ]
        for archetype, count in sorted(self.archetypes.items()):
            lines.append(f"  {archetype}: {count}")
        return "\n".join(lines)


# === Citizen Manifest Response ===


@dataclass(frozen=True)
class CitizenManifestResponse:
    """Response type for citizen manifest."""

    total_citizens: int
    active_citizens: int
    archetypes: dict[str, int]


# === CitizenNode ===


@node(
    "world.town.citizen",
    description="Citizen Registry - browse and manage town citizens",
    dependencies=("town_persistence",),
    contracts={
        "manifest": Response(CitizenManifestResponse),
        "list": Response(CitizenListResponse),
        "get": Response(CitizenGetResponse),
        "create": Contract(CitizenCreateRequest, CitizenCreateResponse),
        "update": Contract(CitizenUpdateRequest, CitizenUpdateResponse),
    },
    examples=[
        ("list", {}, "Browse citizens"),
        ("get", {"name": "Socrates"}, "Find Socrates"),
    ],
)
class CitizenNode(BaseLogosNode):
    """
    AGENTESE node for Town Citizen Registry.

    Provides a focused view into citizen data, complementing the parent
    world.town node. Enables deep navigation in the OS Shell:

        world.town → world.town.citizen → (select citizen)

    Example:
        # Via AGENTESE gateway
        GET /agentese/world/town/citizen/manifest

        # Via Logos directly
        await logos.invoke("world.town.citizen.list", observer)

        # Via CLI
        kgents town citizen list
    """

    def __init__(self, town_persistence: TownPersistence) -> None:
        """
        Initialize CitizenNode.

        Args:
            town_persistence: The persistence layer (injected by container)
        """
        self._persistence = town_persistence

    @property
    def handle(self) -> str:
        return "world.town.citizen"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        base = ("list", "get")
        if archetype in ("developer", "admin", "system"):
            return base + ("create", "update")
        return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest citizen registry overview.

        AGENTESE: world.town.citizen.manifest
        """
        if self._persistence is None:
            return CitizenManifestRendering(
                total_citizens=0,
                active_citizens=0,
                archetypes={},
            )

        # Get all citizens to compute stats
        citizens = await self._persistence.list_citizens(limit=1000)

        # Count by archetype
        archetypes: dict[str, int] = {}
        active_count = 0
        for c in citizens:
            archetypes[c.archetype] = archetypes.get(c.archetype, 0) + 1
            if c.is_active:
                active_count += 1

        return CitizenManifestRendering(
            total_citizens=len(citizens),
            active_citizens=active_count,
            archetypes=archetypes,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if self._persistence is None:
            return {"error": "Town persistence not configured"}

        if aspect == "list":
            active_only = kwargs.get("active_only", False)
            archetype_filter = kwargs.get("archetype")
            limit = kwargs.get("limit", 50)

            citizens = await self._persistence.list_citizens(
                active_only=active_only,
                archetype=archetype_filter,
                limit=limit,
            )
            return CitizenListRendering(citizens=citizens, total=len(citizens)).to_dict()

        elif aspect == "get":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            name = kwargs.get("name")

            if citizen_id:
                citizen = await self._persistence.get_citizen(citizen_id)
            elif name:
                citizen = await self._persistence.get_citizen_by_name(name)
            else:
                return {"error": "citizen_id or name required"}

            if citizen is None:
                return {"error": f"Citizen not found: {citizen_id or name}"}
            return CitizenRendering(citizen=citizen).to_dict()

        elif aspect == "create":
            name = kwargs.get("name")
            archetype = kwargs.get("archetype", "default")
            description = kwargs.get("description")
            traits = kwargs.get("traits")

            if not name:
                return {"error": "name required"}

            citizen = await self._persistence.create_citizen(
                name=name,
                archetype=archetype,
                description=description,
                traits=traits,
            )
            return CitizenRendering(citizen=citizen).to_dict()

        elif aspect == "update":
            citizen_id = kwargs.get("citizen_id") or kwargs.get("id")
            if not citizen_id:
                return {"error": "citizen_id required"}

            citizen = await self._persistence.update_citizen(
                citizen_id=citizen_id,
                description=kwargs.get("description"),
                traits=kwargs.get("traits"),
                is_active=kwargs.get("is_active"),
            )
            if citizen is None:
                return {"error": f"Citizen not found: {citizen_id}"}
            return CitizenRendering(citizen=citizen).to_dict()

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "CitizenNode",
    "CitizenManifestRendering",
    "CitizenManifestResponse",
]
