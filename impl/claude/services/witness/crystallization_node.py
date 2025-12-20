"""
Time Witness AGENTESE Node: @node("time.witness")

Experience crystallization node — complementary to self.witness (trust-gated agency).

AGENTESE Paths:
- time.witness.manifest   - Crystallization status, session info, crystal count
- time.witness.attune     - Start observation session
- time.witness.mark       - Create user marker for current session
- time.witness.crystallize - Trigger crystallization of accumulated observations
- time.witness.timeline   - Get timeline of crystals
- time.witness.crystal    - Query specific crystal
- time.witness.territory  - Codebase activity heat map

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- Two witness aspects: trust agency (self) + crystallization (time)
- Crystallization transforms ephemeral events into durable memory

Philosophy:
    "The Witness sees. Time captures. Together, experience crystallizes."

See: docs/skills/metaphysical-fullstack.md
See: plans/witness-muse-implementation.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    AttuneRequest,
    AttuneResponse,
    CrystalItem,
    CrystallizeRequest,
    CrystallizeResponse,
    CrystalQueryRequest,
    CrystalQueryResponse,
    MarkRequest,
    MarkResponse,
    TerritoryRequest,
    TerritoryResponse,
    ThoughtItem,
    TimelineRequest,
    TimelineResponse,
)
from .crystal import ExperienceCrystal, Narrative
from .persistence import WitnessPersistence
from .sheaf import EventSource, LocalObservation, WitnessSheaf

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Manifest Response ===


@dataclass
class TimeWitnessManifestResponse:
    """Manifest response for time.witness."""

    active_session: str | None
    session_started_at: str | None
    total_crystals: int
    crystals_this_session: int
    pending_observations: int
    last_crystallization: str | None
    status: str  # "observing", "idle", "crystallizing"


# === TimeWitnessNode Rendering ===


@dataclass(frozen=True)
class TimeWitnessManifestRendering:
    """Rendering for time.witness manifest."""

    manifest: TimeWitnessManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "time_witness_manifest",
            "active_session": self.manifest.active_session,
            "session_started_at": self.manifest.session_started_at,
            "total_crystals": self.manifest.total_crystals,
            "crystals_this_session": self.manifest.crystals_this_session,
            "pending_observations": self.manifest.pending_observations,
            "last_crystallization": self.manifest.last_crystallization,
            "status": self.manifest.status,
        }

    def to_text(self) -> str:
        lines = [
            "Time Witness Status",
            "==================",
            f"Active Session: {self.manifest.active_session or 'None'}",
            f"Status: {self.manifest.status}",
            f"Total Crystals: {self.manifest.total_crystals}",
            f"This Session: {self.manifest.crystals_this_session}",
            f"Pending Observations: {self.manifest.pending_observations}",
        ]
        if self.manifest.last_crystallization:
            lines.append(f"Last Crystallization: {self.manifest.last_crystallization}")
        return "\n".join(lines)


# === TimeWitnessNode ===


@node(
    "time.witness",
    description="Time Witness - Experience crystallization and temporal memory",
    dependencies=("witness_persistence",),
    contracts={
        # Perception aspects
        "manifest": Response(TimeWitnessManifestResponse),
        # Mutation aspects
        "attune": Contract(AttuneRequest, AttuneResponse),
        "mark": Contract(MarkRequest, MarkResponse),
        "crystallize": Contract(CrystallizeRequest, CrystallizeResponse),
        "timeline": Contract(TimelineRequest, TimelineResponse),
        "crystal": Contract(CrystalQueryRequest, CrystalQueryResponse),
        "territory": Contract(TerritoryRequest, TerritoryResponse),
    },
    examples=[
        ("manifest", {}, "Get crystallization status"),
        ("attune", {"session_name": "feature-work"}, "Start observation session"),
        (
            "mark",
            {"content": "Breakthrough moment!", "tags": ["milestone"]},
            "Mark significant moment",
        ),
        ("crystallize", {"session_id": "abc123"}, "Trigger crystallization"),
        ("timeline", {"limit": 10}, "Get recent crystals"),
        ("territory", {"hours": 24}, "Get codebase heat map"),
    ],
)
class TimeWitnessNode(BaseLogosNode):
    """
    AGENTESE node for experience crystallization (time.witness context).

    Separate from self.witness (trust-gated agency). This node handles:
    - Observation session management (attune)
    - User markers for significant moments (mark)
    - Crystallization triggers (crystallize)
    - Timeline queries (timeline, crystal)
    - Codebase activity maps (territory)

    Example:
        # Start observing a work session
        POST /agentese/time/witness/attune
        {"session_name": "refactoring-auth"}

        # Mark a significant moment
        POST /agentese/time/witness/mark
        {"content": "Finally got tests passing!", "tags": ["milestone"]}

        # Trigger crystallization
        POST /agentese/time/witness/crystallize
        {"session_id": "abc123"}

        # Query timeline
        GET /agentese/time/witness/timeline
        {"limit": 10}
    """

    def __init__(
        self,
        witness_persistence: WitnessPersistence,
    ) -> None:
        """
        Initialize TimeWitnessNode.

        Args:
            witness_persistence: The persistence layer (injected by container)
        """
        self._persistence = witness_persistence
        self._sheaf = WitnessSheaf()

        # In-memory session state (would be persisted in production)
        self._active_session: str | None = None
        self._session_started_at: datetime | None = None
        self._pending_observations: list[LocalObservation] = []
        self._crystals: list[ExperienceCrystal] = []
        self._markers: list[dict[str, Any]] = []
        self._last_crystallization: datetime | None = None

    @property
    def handle(self) -> str:
        return "time.witness"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Crystallization is less restrictive than trust agency:
        - developer/operator: Full access
        - architect/researcher: Full access (crystallization is observational)
        - newcomer: Can view but not crystallize
        - guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access
        if archetype_lower in (
            "developer",
            "operator",
            "admin",
            "system",
            "architect",
            "researcher",
        ):
            return (
                "manifest",
                "attune",
                "mark",
                "crystallize",
                "timeline",
                "crystal",
                "territory",
            )

        # Newcomers: read-only
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return (
                "manifest",
                "timeline",
                "crystal",
                "territory",
            )

        # Guest: minimal
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest crystallization status to observer.

        AGENTESE: time.witness.manifest
        """
        # Determine status
        if self._active_session:
            status = "observing"
        elif self._pending_observations:
            status = "crystallizing"
        else:
            status = "idle"

        manifest = TimeWitnessManifestResponse(
            active_session=self._active_session,
            session_started_at=self._session_started_at.isoformat()
            if self._session_started_at
            else None,
            total_crystals=len(self._crystals),
            crystals_this_session=sum(
                1 for c in self._crystals if c.session_id == self._active_session
            )
            if self._active_session
            else 0,
            pending_observations=len(self._pending_observations),
            last_crystallization=self._last_crystallization.isoformat()
            if self._last_crystallization
            else None,
            status=status,
        )

        return TimeWitnessManifestRendering(manifest=manifest)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "attune":
            return await self._handle_attune(kwargs)
        elif aspect == "mark":
            return await self._handle_mark(kwargs)
        elif aspect == "crystallize":
            return await self._handle_crystallize(kwargs)
        elif aspect == "timeline":
            return await self._handle_timeline(kwargs)
        elif aspect == "crystal":
            return await self._handle_crystal_query(kwargs)
        elif aspect == "territory":
            return await self._handle_territory(kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_attune(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle attune aspect - start observation session."""
        session_name = kwargs.get("session_name", "")
        session_id = f"session-{uuid4().hex[:8]}"
        now = datetime.now(UTC)

        # If there's an existing session, crystallize it first
        if self._active_session and self._pending_observations:
            await self._handle_crystallize({"session_id": self._active_session, "force": True})

        self._active_session = session_id
        self._session_started_at = now
        self._pending_observations = []

        return {
            "session_id": session_id,
            "started_at": now.isoformat(),
            "attuned": True,
        }

    async def _handle_mark(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle mark aspect - create user marker."""
        content = kwargs.get("content", "")
        tags = kwargs.get("tags", [])

        if not content:
            return {"error": "content required"}

        marker_id = f"marker-{uuid4().hex[:8]}"
        now = datetime.now(UTC)

        marker = {
            "marker_id": marker_id,
            "content": content,
            "tags": tags,
            "timestamp": now.isoformat(),
            "session_id": self._active_session,
        }
        self._markers.append(marker)

        return {
            "marker_id": marker_id,
            "content": content,
            "tags": tags,
            "timestamp": now.isoformat(),
        }

    async def _handle_crystallize(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle crystallize aspect - trigger crystallization."""
        session_id = kwargs.get("session_id", self._active_session or "")
        markers = kwargs.get("markers", [])
        force = kwargs.get("force", False)

        # Get thoughts from persistence
        thoughts = await self._persistence.get_thoughts(limit=100)

        if not thoughts and not force:
            return {"error": "No observations to crystallize"}

        # Add session markers
        session_markers = [m["content"] for m in self._markers if m.get("session_id") == session_id]
        all_markers = list(markers) + session_markers

        # Create crystal
        crystal = ExperienceCrystal.from_thoughts(
            thoughts=list(thoughts),
            session_id=session_id,
            markers=all_markers,
        )

        self._crystals.append(crystal)
        self._last_crystallization = datetime.now(UTC)
        self._pending_observations = []

        # Clear markers for this session
        self._markers = [m for m in self._markers if m.get("session_id") != session_id]

        return {
            "crystal_id": crystal.crystal_id,
            "session_id": crystal.session_id,
            "thought_count": crystal.thought_count,
            "topics": list(crystal.topics),
            "mood": crystal.mood.to_dict(),
            "narrative_summary": crystal.narrative.summary,
            "crystallized_at": crystal.crystallized_at.isoformat(),
        }

    async def _handle_timeline(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle timeline aspect - get crystal timeline."""
        limit = kwargs.get("limit", 20)
        session_id = kwargs.get("session_id")
        since_str = kwargs.get("since")

        # Filter crystals
        crystals = self._crystals

        if session_id:
            crystals = [c for c in crystals if c.session_id == session_id]

        if since_str:
            try:
                since = datetime.fromisoformat(since_str)
                crystals = [c for c in crystals if c.crystallized_at >= since]
            except ValueError:
                pass

        # Sort by crystallization time (newest first)
        crystals = sorted(crystals, key=lambda c: c.crystallized_at, reverse=True)[:limit]

        # Convert to items
        items = [
            {
                "crystal_id": c.crystal_id,
                "session_id": c.session_id,
                "thought_count": c.thought_count,
                "started_at": c.started_at.isoformat() if c.started_at else None,
                "ended_at": c.ended_at.isoformat() if c.ended_at else None,
                "duration_minutes": c.duration_minutes,
                "topics": list(c.topics),
                "mood_brightness": c.mood.brightness,
                "mood_dominant_quality": c.mood.dominant_quality,
                "narrative_summary": c.narrative.summary,
                "crystallized_at": c.crystallized_at.isoformat(),
            }
            for c in crystals
        ]

        return {
            "count": len(items),
            "crystals": items,
        }

    async def _handle_crystal_query(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle crystal aspect - query specific crystal."""
        crystal_id = kwargs.get("crystal_id")
        session_id = kwargs.get("session_id")
        topics = kwargs.get("topics", [])

        crystal: ExperienceCrystal | None = None

        if crystal_id:
            crystal = next((c for c in self._crystals if c.crystal_id == crystal_id), None)
        elif session_id:
            crystal = next((c for c in self._crystals if c.session_id == session_id), None)
        elif topics:
            # Find crystal with matching topics
            topic_set = set(topics)
            crystal = next((c for c in self._crystals if topic_set & c.topics), None)

        if not crystal:
            return {
                "found": False,
                "crystal": None,
                "thoughts": [],
                "topology": {},
                "mood": {},
                "narrative": {},
            }

        return {
            "found": True,
            "crystal": {
                "crystal_id": crystal.crystal_id,
                "session_id": crystal.session_id,
                "thought_count": crystal.thought_count,
                "started_at": crystal.started_at.isoformat() if crystal.started_at else None,
                "ended_at": crystal.ended_at.isoformat() if crystal.ended_at else None,
                "duration_minutes": crystal.duration_minutes,
                "topics": list(crystal.topics),
                "mood_brightness": crystal.mood.brightness,
                "mood_dominant_quality": crystal.mood.dominant_quality,
                "narrative_summary": crystal.narrative.summary,
                "crystallized_at": crystal.crystallized_at.isoformat(),
            },
            "thoughts": [
                {
                    "content": t.content,
                    "source": t.source,
                    "tags": list(t.tags),
                    "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                }
                for t in crystal.thoughts
            ],
            "topology": crystal.topology.to_dict(),
            "mood": crystal.mood.to_dict(),
            "narrative": crystal.narrative.to_dict(),
        }

    async def _handle_territory(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle territory aspect - codebase activity heat map."""
        session_id = kwargs.get("session_id")
        hours = kwargs.get("hours", 24)

        # Filter crystals by time window
        cutoff = datetime.now(UTC).replace(tzinfo=None) - __import__("datetime").timedelta(
            hours=hours
        )
        crystals = [c for c in self._crystals if c.crystallized_at >= cutoff]

        if session_id:
            crystals = [c for c in crystals if c.session_id == session_id]

        if not crystals:
            return {
                "primary_path": ".",
                "heat": {},
                "total_crystals": 0,
                "time_window_hours": hours,
            }

        # Aggregate heat maps
        combined_heat: dict[str, float] = {}
        for crystal in crystals:
            for path, heat_val in crystal.topology.heat.items():
                combined_heat[path] = combined_heat.get(path, 0) + heat_val

        # Normalize
        if combined_heat:
            max_heat = max(combined_heat.values())
            combined_heat = {p: h / max_heat for p, h in combined_heat.items()}

        # Find primary path
        primary_path = (
            max(combined_heat.keys(), key=lambda p: combined_heat[p]) if combined_heat else "."
        )

        return {
            "primary_path": primary_path,
            "heat": combined_heat,
            "total_crystals": len(crystals),
            "time_window_hours": hours,
        }

    # === External API for Flux Integration ===

    def observe(self, observation: LocalObservation) -> None:
        """
        Add an observation from a watcher.

        Called by WitnessFlux when events are captured.
        """
        self._pending_observations.append(observation)

    def get_crystals(self) -> list[ExperienceCrystal]:
        """Get all crystals (for Muse integration)."""
        return list(self._crystals)


# === Exports ===

__all__ = [
    "TimeWitnessNode",
    "TimeWitnessManifestResponse",
    "TimeWitnessManifestRendering",
]
