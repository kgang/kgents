"""
Collective AGENTESE Node: @node("world.town.collective")

Exposes collective town operations that span multiple citizens:
- Gossip propagation across regions
- Collective actions (town-wide events)
- Sheaf-based emergence metrics
- Cross-region coordination

AGENTESE Paths:
- world.town.collective.manifest   - Collective metrics overview
- world.town.collective.gossip     - Propagate gossip between citizens
- world.town.collective.emergence  - Get sheaf emergence metrics
- world.town.collective.activity   - Region activity summary
- world.town.collective.step       - Advance simulation step

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from protocols.agentese.contract import Contract, Response

logger = logging.getLogger(__name__)
from typing import TYPE_CHECKING

from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
from agents.town.context import (
    ALL_REGION_CONTEXTS,
    RUMOR_DISTANCE,
    RegionType,
    TownContext,
)
from agents.town.sheaf import RegionView, TownSheaf, TownState, create_town_sheaf
from protocols.agentese.registry import node

from .bus_wiring import TownBusManager, get_town_bus_manager
from .events import (
    GossipSpread,
    RegionActivity,
    SimulationStep,
)

# =============================================================================
# Contract Types
# =============================================================================


@dataclass(frozen=True)
class CollectiveManifestResponse:
    """Response for collective manifest."""

    total_citizens: int
    total_regions: int
    active_regions: int
    emergence_score: float
    rituality: float
    trust_density: float
    region_balance: float


@dataclass(frozen=True)
class GossipRequest:
    """Request to spread gossip."""

    source_citizen: str
    target_citizen: str
    content: str
    accuracy: float = 1.0
    source_region: str | None = None
    target_region: str | None = None


@dataclass(frozen=True)
class GossipResponse:
    """Response after spreading gossip."""

    event_id: str
    source_citizen: str
    target_citizen: str
    spread_successful: bool
    regions_reached: list[str]


@dataclass(frozen=True)
class EmergenceResponse:
    """Response for emergence metrics."""

    culture_motifs: list[dict[str, Any]]
    rituality: float
    trust_density: float
    coalition_overlap: float
    region_balance: float
    motif_count: int


@dataclass(frozen=True)
class ActivitySummary:
    """Summary of activity in a region."""

    region: str
    citizen_count: int
    recent_conversations: int
    activity_level: str  # "quiet", "moderate", "active", "bustling"


@dataclass(frozen=True)
class ActivityResponse:
    """Response for region activity."""

    regions: list[ActivitySummary]
    total_activity: int
    most_active_region: str | None


@dataclass(frozen=True)
class SimulationStepRequest:
    """Request to advance simulation."""

    steps: int = 1


@dataclass(frozen=True)
class SimulationStepResponse:
    """Response after simulation step."""

    step_number: int
    active_citizens: int
    interactions: int
    coalitions_changed: int
    events_emitted: int


# =============================================================================
# Renderings
# =============================================================================


@dataclass(frozen=True)
class CollectiveManifestRendering:
    """Rendering for collective manifest."""

    response: CollectiveManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "collective_manifest",
            "total_citizens": self.response.total_citizens,
            "total_regions": self.response.total_regions,
            "active_regions": self.response.active_regions,
            "emergence_score": round(self.response.emergence_score, 3),
            "rituality": round(self.response.rituality, 3),
            "trust_density": round(self.response.trust_density, 3),
            "region_balance": round(self.response.region_balance, 3),
        }

    def to_text(self) -> str:
        r = self.response
        lines = [
            "Town Collective Status",
            "======================",
            f"Citizens: {r.total_citizens}",
            f"Regions: {r.active_regions}/{r.total_regions} active",
            "",
            "Emergence Metrics:",
            f"  Emergence Score: {r.emergence_score:.1%}",
            f"  Rituality: {r.rituality:.1%}",
            f"  Trust Density: {r.trust_density:.1%}",
            f"  Region Balance: {r.region_balance:.1%}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class EmergenceRendering:
    """Rendering for emergence metrics."""

    response: EmergenceResponse

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "emergence",
            "culture_motifs": self.response.culture_motifs,
            "rituality": self.response.rituality,
            "trust_density": self.response.trust_density,
            "coalition_overlap": self.response.coalition_overlap,
            "region_balance": self.response.region_balance,
            "motif_count": self.response.motif_count,
        }

    def to_text(self) -> str:
        r = self.response
        lines = [
            "Emergence Metrics",
            "================",
            f"Rituality: {r.rituality:.1%}",
            f"Trust Density: {r.trust_density:.1%}",
            f"Coalition Overlap: {r.coalition_overlap:.1%}",
            f"Region Balance: {r.region_balance:.1%}",
            "",
            f"Culture Motifs: {r.motif_count}",
        ]
        for motif in r.culture_motifs[:3]:
            lines.append(f"  {motif.get('type', 'unknown')}: {motif.get('count', 0)}")
        return "\n".join(lines)


# =============================================================================
# CollectiveNode
# =============================================================================


@node(
    "world.town.collective",
    description="Collective town operations - gossip, emergence, cross-region coordination",
    dependencies=("town_sheaf", "bus_manager"),
    contracts={
        "manifest": Response(CollectiveManifestResponse),
        "gossip": Contract(GossipRequest, GossipResponse),
        "emergence": Response(EmergenceResponse),
        "activity": Response(ActivityResponse),
        "step": Contract(SimulationStepRequest, SimulationStepResponse),
    },
)
class CollectiveNode(BaseLogosNode):
    """
    AGENTESE node for Collective Town operations.

    Handles operations that span multiple citizens and regions:
    - Gossip propagation using RUMOR_DISTANCE graph
    - Emergence metrics from TownSheaf
    - Cross-region coordination
    - Simulation stepping

    Example:
        # Spread gossip
        await logos.invoke("world.town.collective.gossip", observer,
            source_citizen="alice", target_citizen="bob",
            content="Carol found treasure")

        # Get emergence metrics
        await logos.invoke("world.town.collective.emergence", observer)
    """

    def __init__(
        self,
        sheaf: TownSheaf | None = None,
        bus_manager: TownBusManager | None = None,
    ) -> None:
        """
        Initialize CollectiveNode.

        Args:
            sheaf: Town sheaf for emergence detection
            bus_manager: Bus manager for event emission
        """
        self._sheaf = sheaf or create_town_sheaf()
        self._bus_manager = bus_manager or get_town_bus_manager()

        # State tracking (bounded to prevent memory leaks)
        self._citizen_locations: dict[str, str] = {}  # citizen_id -> region
        self._region_activity: dict[str, int] = {}  # region -> conversation count
        self._step_number: int = 0
        self._max_citizens: int = 10000  # Bound to prevent unbounded growth

    @property
    def handle(self) -> str:
        return "world.town.collective"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        base = ("manifest", "emergence", "activity")

        if archetype in ("developer", "admin", "system"):
            return base + ("gossip", "step")
        elif archetype in ("researcher", "analyst"):
            return base + ("gossip",)  # Can analyze gossip
        else:
            return base

    # === State Management ===

    def set_citizen_location(self, citizen_id: str, region: str) -> None:
        """Update citizen location.

        Raises:
            ValueError: If citizen limit exceeded and citizen is new
        """
        if (
            citizen_id not in self._citizen_locations
            and len(self._citizen_locations) >= self._max_citizens
        ):
            logger.warning(f"Citizen limit ({self._max_citizens}) reached, cannot add {citizen_id}")
            raise ValueError(f"Citizen limit exceeded: {self._max_citizens}")
        self._citizen_locations[citizen_id] = region

    def record_conversation(self, region: str) -> None:
        """Record a conversation in a region."""
        self._region_activity[region] = self._region_activity.get(region, 0) + 1

    def get_region_views(self) -> dict[TownContext, RegionView]:
        """Build region views from current state."""
        views: dict[TownContext, RegionView] = {}

        for region_ctx in ALL_REGION_CONTEXTS:
            region_name = region_ctx.name
            citizens_in_region = frozenset(
                cid for cid, loc in self._citizen_locations.items() if loc == region_name
            )

            views[region_ctx] = RegionView(
                region=region_ctx,
                citizens=citizens_in_region,
                relationships={},  # Would be populated from persistence
                events=(),
                coalition_memberships={},
            )

        return views

    # === Manifest ===

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest collective status.

        AGENTESE: world.town.collective.manifest
        """
        views = self.get_region_views()

        # Try to glue views for emergence
        try:
            state = self._sheaf.glue(views)
            emergence = state.emergence
        except Exception as e:
            logger.warning(f"Failed to glue sheaf views for manifest: {e}")
            emergence = {}

        # Count active regions
        active_regions = sum(1 for v in views.values() if v.citizen_count() > 0)

        # Compute emergence score (average of metrics)
        emergence_values = [
            emergence.get("rituality", 0.0),
            emergence.get("trust_density", 0.0),
            emergence.get("region_balance", 0.0),
        ]
        emergence_score = sum(emergence_values) / len(emergence_values) if emergence_values else 0.0

        response = CollectiveManifestResponse(
            total_citizens=len(self._citizen_locations),
            total_regions=len(ALL_REGION_CONTEXTS),
            active_regions=active_regions,
            emergence_score=emergence_score,
            rituality=emergence.get("rituality", 0.0),
            trust_density=emergence.get("trust_density", 0.0),
            region_balance=emergence.get("region_balance", 0.0),
        )

        return CollectiveManifestRendering(response=response)

    # === Aspect Invocations ===

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""

        # === Gossip ===
        if aspect == "gossip":
            return await self._handle_gossip(kwargs)

        # === Emergence ===
        elif aspect == "emergence":
            return await self._handle_emergence()

        # === Activity ===
        elif aspect == "activity":
            return await self._handle_activity()

        # === Step ===
        elif aspect == "step":
            return await self._handle_step(kwargs)

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_gossip(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle gossip spread."""
        source_citizen = kwargs.get("source_citizen")
        target_citizen = kwargs.get("target_citizen")
        content = kwargs.get("content", "")
        accuracy = kwargs.get("accuracy", 1.0)

        if not source_citizen or not target_citizen:
            return {"error": "source_citizen and target_citizen required"}

        # Get regions
        source_region = kwargs.get(
            "source_region", self._citizen_locations.get(source_citizen, "inn")
        )
        target_region = kwargs.get(
            "target_region", self._citizen_locations.get(target_citizen, "plaza")
        )

        # Check if gossip can spread (rumor distance)
        source_region_type = (
            RegionType(source_region) if source_region in [r.value for r in RegionType] else None
        )
        target_region_type = (
            RegionType(target_region) if target_region in [r.value for r in RegionType] else None
        )

        spread_successful = True
        regions_reached = [target_region]

        if source_region_type and target_region_type:
            # Check if in rumor distance
            if target_region_type not in RUMOR_DISTANCE.get(source_region_type, set()):
                # Not in direct rumor distance, may need intermediary
                spread_successful = accuracy > 0.5  # Reduced accuracy for indirect

        # Create and emit event
        event = GossipSpread.create(
            source_citizen=source_citizen,
            target_citizen=target_citizen,
            rumor_content=content,
            accuracy=accuracy,
            source_region=source_region,
            target_region=target_region,
        )

        await self._bus_manager.data_bus.emit(event)

        return {
            "event_id": event.event_id,
            "source_citizen": source_citizen,
            "target_citizen": target_citizen,
            "spread_successful": spread_successful,
            "regions_reached": regions_reached,
        }

    async def _handle_emergence(self) -> dict[str, Any]:
        """Handle emergence metrics request."""
        views = self.get_region_views()

        try:
            state = self._sheaf.glue(views)
            emergence = state.emergence
        except Exception as e:
            logger.warning(f"Failed to glue sheaf views for emergence: {e}")
            emergence = {
                "culture_motifs": [],
                "rituality": 0.0,
                "trust_density": 0.0,
                "coalition_overlap": 0.0,
                "region_balance": 0.0,
            }

        motifs = emergence.get("culture_motifs", [])

        response = EmergenceResponse(
            culture_motifs=motifs,
            rituality=emergence.get("rituality", 0.0),
            trust_density=emergence.get("trust_density", 0.0),
            coalition_overlap=emergence.get("coalition_overlap", 0.0),
            region_balance=emergence.get("region_balance", 0.0),
            motif_count=len(motifs),
        )

        return EmergenceRendering(response=response).to_dict()

    async def _handle_activity(self) -> dict[str, Any]:
        """Handle region activity request."""
        summaries: list[ActivitySummary] = []

        for region_ctx in ALL_REGION_CONTEXTS:
            region_name = region_ctx.name
            citizen_count = sum(1 for loc in self._citizen_locations.values() if loc == region_name)
            conversations = self._region_activity.get(region_name, 0)

            # Determine activity level
            if conversations == 0 and citizen_count == 0:
                level = "quiet"
            elif conversations < 5:
                level = "moderate"
            elif conversations < 10:
                level = "active"
            else:
                level = "bustling"

            summaries.append(
                ActivitySummary(
                    region=region_name,
                    citizen_count=citizen_count,
                    recent_conversations=conversations,
                    activity_level=level,
                )
            )

        # Find most active
        total = sum(self._region_activity.values())
        most_active = (
            max(summaries, key=lambda s: s.recent_conversations).region if summaries else None
        )

        return {
            "regions": [
                {
                    "region": s.region,
                    "citizen_count": s.citizen_count,
                    "recent_conversations": s.recent_conversations,
                    "activity_level": s.activity_level,
                }
                for s in summaries
            ],
            "total_activity": total,
            "most_active_region": most_active,
        }

    async def _handle_step(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle simulation step."""
        steps = kwargs.get("steps", 1)

        # Track events emitted
        events_emitted = 0

        for _ in range(steps):
            self._step_number += 1

            # Emit step event
            event = SimulationStep.create(
                step_number=self._step_number,
                active_citizens=len(self._citizen_locations),
                interactions=sum(self._region_activity.values()),
                coalitions_changed=0,
            )
            await self._bus_manager.data_bus.emit(event)
            events_emitted += 1

        return {
            "step_number": self._step_number,
            "active_citizens": len(self._citizen_locations),
            "interactions": sum(self._region_activity.values()),
            "coalitions_changed": 0,
            "events_emitted": events_emitted,
        }


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "CollectiveNode",
    "CollectiveManifestResponse",
    "GossipRequest",
    "GossipResponse",
    "EmergenceResponse",
    "ActivityResponse",
    "SimulationStepResponse",
    "CollectiveManifestRendering",
    "EmergenceRendering",
]
