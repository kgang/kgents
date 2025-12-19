"""
Park AGENTESE Node: @node("world.park")

Punchdrunk Westworld where hosts can say no.

Exposes Park operations through the universal gateway for
immersive, consent-first agent experiences.

AGENTESE Paths:
- world.park.manifest      - Show park status (hosts, episodes, locations)
- world.park.host.list     - List park hosts
- world.park.host.get      - Get a host by ID or name
- world.park.host.create   - Create a new host
- world.park.host.interact - Interact with a host
- world.park.host.witness  - View host memories
- world.park.episode.start - Start a visitor episode
- world.park.episode.end   - End an episode
- world.park.episode.list  - List episodes
- world.park.location.list - List park locations
- world.park.scenario.*    - Scenario management (Wave 3)

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Design DNA:
- Consent-first: Hosts can refuse uncomfortable interactions
- Observer-dependent: What you see depends on who you are
- Visible process: State machines are legible

From Westworld: "These violent delights have violent ends" (unless consent is respected)

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    # Consent debt contracts
    ConsentDebtRequest,
    ConsentDebtResponse,
    EpisodeEndRequest,
    EpisodeEndResponse,
    EpisodeListResponse,
    EpisodeStartRequest,
    EpisodeStartResponse,
    HostCreateRequest,
    HostCreateResponse,
    HostGetResponse,
    HostInteractRequest,
    HostInteractResponse,
    HostListResponse,
    HostUpdateRequest,
    HostUpdateResponse,
    HostWitnessRequest,
    HostWitnessResponse,
    LocationCreateRequest,
    LocationCreateResponse,
    LocationListResponse,
    ParkManifestResponse,
    # Scenario contracts
    ScenarioEndRequest,
    ScenarioEndResponse,
    ScenarioGetRequest,
    ScenarioGetResponse,
    ScenarioListResponse,
    ScenarioSessionListResponse,
    ScenarioStartRequest,
    ScenarioStartResponse,
    ScenarioTickRequest,
    ScenarioTickResponse,
    SessionProgress,
)
from .persistence import (
    EpisodeView,
    HostView,
    InteractionView,
    LocationView,
    MemoryView,
    ParkPersistence,
    ParkStatus,
)
from .scenario_service import (
    ScenarioService,
    ScenarioView,
    SessionView,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# ParkNode Renderings
# =============================================================================


@dataclass(frozen=True)
class ParkManifestRendering:
    """Rendering for park manifest (status overview)."""

    status: ParkStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_manifest",
            "total_hosts": self.status.total_hosts,
            "active_hosts": self.status.active_hosts,
            "total_episodes": self.status.total_episodes,
            "active_episodes": self.status.active_episodes,
            "total_memories": self.status.total_memories,
            "total_locations": self.status.total_locations,
            "consent_refusal_rate": self.status.consent_refusal_rate,
            "storage_backend": self.status.storage_backend,
        }

    def to_text(self) -> str:
        s = self.status
        refusal_pct = f"{s.consent_refusal_rate * 100:.1f}%" if s.consent_refusal_rate else "0%"
        return "\n".join(
            [
                "Punchdrunk Park",
                "=" * 40,
                f"Hosts: {s.active_hosts}/{s.total_hosts} active",
                f"Episodes: {s.active_episodes}/{s.total_episodes} active",
                f"Memories: {s.total_memories}",
                f"Locations: {s.total_locations}",
                f"Consent Refusal Rate: {refusal_pct}",
                "",
                f"Storage: {s.storage_backend}",
            ]
        )


@dataclass(frozen=True)
class HostRendering:
    """Rendering for a single park host."""

    host: HostView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_host",
            "id": self.host.id,
            "name": self.host.name,
            "character": self.host.character,
            "backstory": self.host.backstory,
            "traits": self.host.traits,
            "values": self.host.values,
            "boundaries": self.host.boundaries,
            "is_active": self.host.is_active,
            "mood": self.host.mood,
            "energy_level": self.host.energy_level,
            "current_location": self.host.current_location,
            "interaction_count": self.host.interaction_count,
            "consent_refusal_count": self.host.consent_refusal_count,
        }

    def to_text(self) -> str:
        h = self.host
        status = "active" if h.is_active else "inactive"
        energy_bar = "█" * int(h.energy_level * 10) + "░" * (10 - int(h.energy_level * 10))
        lines = [
            f"{h.name} [{h.character}] ({status})",
            "=" * 40,
            f"Location: {h.current_location or 'Unknown'}",
            f"Mood: {h.mood or 'Neutral'}",
            f"Energy: {energy_bar} {h.energy_level:.0%}",
        ]
        if h.backstory:
            lines.append(f"Backstory: {h.backstory[:100]}...")
        if h.boundaries:
            lines.append(f"Boundaries: {', '.join(h.boundaries[:3])}")
        lines.append(f"Interactions: {h.interaction_count} (refusals: {h.consent_refusal_count})")
        return "\n".join(lines)


@dataclass(frozen=True)
class HostListRendering:
    """Rendering for list of park hosts."""

    hosts: list[HostView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_host_list",
            "count": len(self.hosts),
            "hosts": [
                {
                    "id": h.id,
                    "name": h.name,
                    "character": h.character,
                    "is_active": h.is_active,
                    "location": h.current_location,
                    "mood": h.mood,
                }
                for h in self.hosts
            ],
        }

    def to_text(self) -> str:
        if not self.hosts:
            return "No hosts in the park"
        lines = [f"Park Hosts ({len(self.hosts)})", ""]
        for h in self.hosts:
            status = "●" if h.is_active else "○"
            loc = h.current_location or "?"
            lines.append(f"  {status} {h.name} [{h.character}] @ {loc}")
        return "\n".join(lines)


@dataclass(frozen=True)
class EpisodeRendering:
    """Rendering for a park episode."""

    episode: EpisodeView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_episode",
            "id": self.episode.id,
            "visitor_id": self.episode.visitor_id,
            "visitor_name": self.episode.visitor_name,
            "title": self.episode.title,
            "status": self.episode.status,
            "interaction_count": self.episode.interaction_count,
            "hosts_met": self.episode.hosts_met,
            "locations_visited": self.episode.locations_visited,
            "started_at": self.episode.started_at,
            "ended_at": self.episode.ended_at,
            "duration_seconds": self.episode.duration_seconds,
        }

    def to_text(self) -> str:
        e = self.episode
        lines = [
            f"Episode: {e.title or e.id}",
            "=" * 40,
            f"Visitor: {e.visitor_name or 'Anonymous'}",
            f"Status: {e.status}",
            f"Interactions: {e.interaction_count}",
        ]
        if e.hosts_met:
            lines.append(f"Hosts met: {', '.join(e.hosts_met)}")
        if e.locations_visited:
            lines.append(f"Locations: {', '.join(e.locations_visited)}")
        if e.duration_seconds:
            mins = e.duration_seconds // 60
            secs = e.duration_seconds % 60
            lines.append(f"Duration: {mins}m {secs}s")
        return "\n".join(lines)


@dataclass(frozen=True)
class InteractionRendering:
    """Rendering for a host interaction."""

    interaction: InteractionView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_interaction",
            "id": self.interaction.id,
            "host_name": self.interaction.host_name,
            "interaction_type": self.interaction.interaction_type,
            "visitor_input": self.interaction.visitor_input,
            "host_response": self.interaction.host_response,
            "consent_requested": self.interaction.consent_requested,
            "consent_given": self.interaction.consent_given,
            "host_emotion": self.interaction.host_emotion,
            "location": self.interaction.location,
        }

    def to_text(self) -> str:
        i = self.interaction
        consent_icon = "✓" if i.consent_given else "✗" if i.consent_given is False else " "
        lines = [
            f"[{consent_icon}] {i.host_name} [{i.interaction_type}]",
            f"Visitor: {i.visitor_input}",
            f"Host: {i.host_response or '(no response)'}",
        ]
        if i.host_emotion:
            lines.append(f"Emotion: {i.host_emotion}")
        if i.consent_reason:
            lines.append(f"Note: {i.consent_reason}")
        return "\n".join(lines)


@dataclass(frozen=True)
class MemoryListRendering:
    """Rendering for host memories."""

    memories: list[MemoryView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_memory_list",
            "count": len(self.memories),
            "memories": [
                {
                    "id": m.id,
                    "memory_type": m.memory_type,
                    "summary": m.summary,
                    "salience": m.salience,
                    "emotional_valence": m.emotional_valence,
                }
                for m in self.memories
            ],
        }

    def to_text(self) -> str:
        if not self.memories:
            return "No memories"
        lines = [f"Host Memories ({len(self.memories)})", ""]
        for m in self.memories:
            salience_bar = "█" * int(m.salience * 5)
            valence = "+" if m.emotional_valence > 0 else "-" if m.emotional_valence < 0 else "○"
            lines.append(
                f"  [{m.memory_type}] {salience_bar} {valence} {m.summary or m.content[:40]}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class LocationListRendering:
    """Rendering for park locations."""

    locations: list[LocationView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "park_location_list",
            "count": len(self.locations),
            "locations": [
                {
                    "id": l.id,
                    "name": l.name,
                    "description": l.description,
                    "atmosphere": l.atmosphere,
                    "is_open": l.is_open,
                }
                for l in self.locations
            ],
        }

    def to_text(self) -> str:
        if not self.locations:
            return "No locations in the park"
        lines = [f"Park Locations ({len(self.locations)})", ""]
        for l in self.locations:
            status = "●" if l.is_open else "○"
            atm = f" ({l.atmosphere})" if l.atmosphere else ""
            lines.append(f"  {status} {l.name}{atm}")
            if l.description:
                lines.append(f"      {l.description[:60]}...")
        return "\n".join(lines)


# =============================================================================
# ParkNode
# =============================================================================


@node(
    "world.park",
    description="Punchdrunk Park - Immersive agent simulation with consent",
    dependencies=("park_persistence", "scenario_service"),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(ParkManifestResponse),
        "host.list": Response(HostListResponse),
        "host.get": Response(HostGetResponse),
        "episode.list": Response(EpisodeListResponse),
        "location.list": Response(LocationListResponse),
        # Mutation aspects (Contract with request + response)
        "host.create": Contract(HostCreateRequest, HostCreateResponse),
        "host.update": Contract(HostUpdateRequest, HostUpdateResponse),
        "host.interact": Contract(HostInteractRequest, HostInteractResponse),
        "host.witness": Contract(HostWitnessRequest, HostWitnessResponse),
        "episode.start": Contract(EpisodeStartRequest, EpisodeStartResponse),
        "episode.end": Contract(EpisodeEndRequest, EpisodeEndResponse),
        "location.create": Contract(LocationCreateRequest, LocationCreateResponse),
        # Scenario aspects - "Westworld where hosts can say no"
        "scenario.list": Response(ScenarioListResponse),
        "scenario.get": Contract(ScenarioGetRequest, ScenarioGetResponse),
        "scenario.start": Contract(ScenarioStartRequest, ScenarioStartResponse),
        "scenario.tick": Contract(ScenarioTickRequest, ScenarioTickResponse),
        "scenario.end": Contract(ScenarioEndRequest, ScenarioEndResponse),
        "scenario.sessions": Response(ScenarioSessionListResponse),
        # Consent debt aspects
        "consent.debt": Contract(ConsentDebtRequest, ConsentDebtResponse),
        "consent.incur": Contract(ConsentDebtRequest, ConsentDebtResponse),
        "consent.apologize": Contract(ConsentDebtRequest, ConsentDebtResponse),
    },
)
class ParkNode(BaseLogosNode):
    """
    AGENTESE node for Park Crown Jewel.

    Provides immersive, consent-first agent experiences inspired by
    Punchdrunk's Sleep No More and Westworld's narrative loops.

    Core principles:
    - Consent-first: Hosts can refuse uncomfortable interactions
    - Observer-dependent: What you see depends on who you are
    - Persistent memory: Hosts remember across sessions
    - Visible process: State machines are legible

    Example:
        # Via AGENTESE gateway
        POST /agentese/world/park/host/create
        {"name": "Dolores", "character": "rancher_daughter"}

        # Via Logos directly
        await logos.invoke("world.park.host.list", observer)

        # Via CLI
        kgents park host list
    """

    def __init__(
        self,
        park_persistence: ParkPersistence,
        scenario_service: ScenarioService | None = None,
    ) -> None:
        """
        Initialize ParkNode.

        Args:
            park_persistence: Persistence layer for park entities
            scenario_service: Service for scenario management (optional for graceful fallback)

        Raises:
            TypeError: If park_persistence is not provided
        """
        self._persistence = park_persistence
        self._scenarios = scenario_service or ScenarioService()

    @property
    def handle(self) -> str:
        return "world.park"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations available to most archetypes.
        Admin operations (cleanup) restricted.
        """
        # Basic operations for all users
        base = (
            "host.list",
            "host.get",
            "episode.list",
            "location.list",
        )

        if archetype in ("developer", "admin", "system"):
            # Full access including admin operations
            return base + (
                "host.create",
                "host.interact",
                "host.witness",
                "host.update",
                "episode.start",
                "episode.end",
                "location.create",
                "scenario.list",
                "scenario.get",
                "scenario.start",
            )
        elif archetype in ("citizen", "founder"):
            # Full park experience
            return base + (
                "host.interact",
                "host.witness",
                "episode.start",
                "episode.end",
                "scenario.list",
                "scenario.start",
            )
        elif archetype in ("resident",):
            # Limited interactions
            return base + (
                "host.interact",
                "episode.start",
                "episode.end",
            )
        else:
            # Tourists can view but not interact
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest park status overview.

        AGENTESE: world.park.manifest
        """
        if self._persistence is None:
            return BasicRendering(
                summary="Park not initialized",
                content="No ParkPersistence configured",
                metadata={"error": "no_persistence"},
            )

        status = await self._persistence.manifest()
        return ParkManifestRendering(status=status)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to persistence methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._persistence is None:
            return {"error": "Park persistence not configured"}

        # === Host Operations ===

        if aspect == "host.list":
            return await self._host_list(**kwargs)

        elif aspect == "host.get":
            return await self._host_get(**kwargs)

        elif aspect == "host.create":
            return await self._host_create(**kwargs)

        elif aspect == "host.interact":
            return await self._host_interact(observer, **kwargs)

        elif aspect == "host.witness":
            return await self._host_witness(**kwargs)

        elif aspect == "host.update":
            return await self._host_update(**kwargs)

        # === Episode Operations ===

        elif aspect == "episode.start":
            return await self._episode_start(observer, **kwargs)

        elif aspect == "episode.end":
            return await self._episode_end(**kwargs)

        elif aspect == "episode.list":
            return await self._episode_list(**kwargs)

        elif aspect == "episode.get":
            return await self._episode_get(**kwargs)

        # === Location Operations ===

        elif aspect == "location.list":
            return await self._location_list(**kwargs)

        elif aspect == "location.create":
            return await self._location_create(**kwargs)

        # === Scenario Operations ===

        elif aspect == "scenario.list":
            return await self._scenario_list(**kwargs)

        elif aspect == "scenario.get":
            return await self._scenario_get(**kwargs)

        elif aspect == "scenario.start":
            return await self._scenario_start(**kwargs)

        elif aspect == "scenario.tick":
            return await self._scenario_tick(**kwargs)

        elif aspect == "scenario.end":
            return await self._scenario_end(**kwargs)

        elif aspect == "scenario.sessions":
            return await self._scenario_sessions(**kwargs)

        # === Consent Debt Operations ===

        elif aspect == "consent.debt":
            return await self._consent_debt(**kwargs)

        elif aspect == "consent.incur":
            return await self._consent_incur(**kwargs)

        elif aspect == "consent.apologize":
            return await self._consent_apologize(**kwargs)

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    # =========================================================================
    # Host Operations
    # =========================================================================

    async def _host_list(self, **kwargs: Any) -> dict[str, Any]:
        """List park hosts."""
        character = kwargs.get("character")
        location = kwargs.get("location")
        active_only = kwargs.get("active_only", True)
        limit = kwargs.get("limit", 50)

        hosts = await self._persistence.list_hosts(
            character=character,
            location=location,
            active_only=active_only,
            limit=limit,
        )
        return HostListRendering(hosts=hosts).to_dict()

    async def _host_get(self, **kwargs: Any) -> dict[str, Any]:
        """Get a host by ID or name."""
        host_id = kwargs.get("host_id") or kwargs.get("id")
        name = kwargs.get("name")

        if host_id:
            host = await self._persistence.get_host(host_id)
        elif name:
            host = await self._persistence.get_host_by_name(name)
        else:
            return {"error": "host_id or name required"}

        if host is None:
            return {"error": f"Host not found: {host_id or name}"}

        return HostRendering(host=host).to_dict()

    async def _host_create(self, **kwargs: Any) -> dict[str, Any]:
        """Create a new park host."""
        name = kwargs.get("name")
        character = kwargs.get("character")

        if not name or not character:
            return {"error": "name and character required"}

        host = await self._persistence.create_host(
            name=name,
            character=character,
            backstory=kwargs.get("backstory"),
            traits=kwargs.get("traits"),
            values=kwargs.get("values"),
            boundaries=kwargs.get("boundaries"),
            location=kwargs.get("location"),
        )
        return HostRendering(host=host).to_dict()

    async def _host_interact(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Interact with a host (core experience)."""
        episode_id = kwargs.get("episode_id")
        host_id = kwargs.get("host_id")
        visitor_input = kwargs.get("input") or kwargs.get("message")

        if not episode_id or not host_id or not visitor_input:
            return {"error": "episode_id, host_id, and input required"}

        interaction = await self._persistence.interact(
            episode_id=episode_id,
            host_id=host_id,
            visitor_input=visitor_input,
            interaction_type=kwargs.get("type", "dialogue"),
            location=kwargs.get("location"),
            check_consent=kwargs.get("check_consent", True),
        )

        if interaction is None:
            return {"error": "Interaction failed - check episode and host IDs"}

        return InteractionRendering(interaction=interaction).to_dict()

    async def _host_witness(self, **kwargs: Any) -> dict[str, Any]:
        """View host memories."""
        host_id = kwargs.get("host_id")
        if not host_id:
            return {"error": "host_id required"}

        memories = await self._persistence.recall_memories(
            host_id=host_id,
            memory_type=kwargs.get("memory_type"),
            min_salience=kwargs.get("min_salience", 0.0),
            limit=kwargs.get("limit", 20),
        )
        return MemoryListRendering(memories=memories).to_dict()

    async def _host_update(self, **kwargs: Any) -> dict[str, Any]:
        """Update host state (mood, energy, location)."""
        host_id = kwargs.get("host_id")
        if not host_id:
            return {"error": "host_id required"}

        host = await self._persistence.update_host_state(
            host_id=host_id,
            mood=kwargs.get("mood"),
            energy_level=kwargs.get("energy_level"),
            location=kwargs.get("location"),
        )

        if host is None:
            return {"error": f"Host not found: {host_id}"}

        return HostRendering(host=host).to_dict()

    # =========================================================================
    # Episode Operations
    # =========================================================================

    async def _episode_start(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start a new park episode."""
        visitor_id = self._extract_user_id(observer)
        visitor_name = kwargs.get("visitor_name") or kwargs.get("name")

        episode = await self._persistence.start_episode(
            visitor_id=visitor_id,
            visitor_name=visitor_name,
            title=kwargs.get("title"),
        )
        return EpisodeRendering(episode=episode).to_dict()

    async def _episode_end(self, **kwargs: Any) -> dict[str, Any]:
        """End a park episode."""
        episode_id = kwargs.get("episode_id")
        if not episode_id:
            return {"error": "episode_id required"}

        episode = await self._persistence.end_episode(
            episode_id=episode_id,
            summary=kwargs.get("summary"),
            status=kwargs.get("status", "completed"),
        )

        if episode is None:
            return {"error": f"Episode not found or already ended: {episode_id}"}

        return EpisodeRendering(episode=episode).to_dict()

    async def _episode_list(self, **kwargs: Any) -> dict[str, Any]:
        """List episodes."""
        visitor_id = kwargs.get("visitor_id")
        status = kwargs.get("status")
        limit = kwargs.get("limit", 20)

        episodes = await self._persistence.list_episodes(
            visitor_id=visitor_id,
            status=status,
            limit=limit,
        )

        return {
            "type": "park_episode_list",
            "count": len(episodes),
            "episodes": [
                {
                    "id": e.id,
                    "title": e.title,
                    "status": e.status,
                    "visitor_name": e.visitor_name,
                    "interaction_count": e.interaction_count,
                    "started_at": e.started_at,
                }
                for e in episodes
            ],
        }

    async def _episode_get(self, **kwargs: Any) -> dict[str, Any]:
        """Get an episode by ID."""
        episode_id = kwargs.get("episode_id") or kwargs.get("id")
        if not episode_id:
            return {"error": "episode_id required"}

        episode = await self._persistence.get_episode(episode_id)
        if episode is None:
            return {"error": f"Episode not found: {episode_id}"}

        return EpisodeRendering(episode=episode).to_dict()

    # =========================================================================
    # Location Operations
    # =========================================================================

    async def _location_list(self, **kwargs: Any) -> dict[str, Any]:
        """List park locations."""
        open_only = kwargs.get("open_only", True)
        locations = await self._persistence.list_locations(open_only=open_only)
        return LocationListRendering(locations=locations).to_dict()

    async def _location_create(self, **kwargs: Any) -> dict[str, Any]:
        """Create a park location."""
        name = kwargs.get("name")
        if not name:
            return {"error": "name required"}

        location = await self._persistence.create_location(
            name=name,
            description=kwargs.get("description"),
            atmosphere=kwargs.get("atmosphere"),
            x=kwargs.get("x"),
            y=kwargs.get("y"),
            capacity=kwargs.get("capacity"),
            connected_to=kwargs.get("connected_to"),
        )

        return {
            "type": "park_location",
            "id": location.id,
            "name": location.name,
            "description": location.description,
            "atmosphere": location.atmosphere,
            "is_open": location.is_open,
        }

    # =========================================================================
    # Scenario Operations - "Westworld where hosts can say no"
    # =========================================================================

    async def _scenario_list(self, **kwargs: Any) -> dict[str, Any]:
        """List available scenario templates."""
        scenario_type = kwargs.get("scenario_type")
        tags = kwargs.get("tags")
        difficulty = kwargs.get("difficulty")
        limit = kwargs.get("limit", 50)

        scenarios = await self._scenarios.list_scenarios(
            scenario_type=scenario_type,
            tags=tags,
            difficulty=difficulty,
            limit=limit,
        )

        return {
            "type": "scenario_list",
            "count": len(scenarios),
            "scenarios": [
                {
                    "id": s.id,
                    "name": s.name,
                    "scenario_type": s.scenario_type,
                    "difficulty": s.difficulty,
                    "estimated_duration_minutes": s.estimated_duration_minutes,
                    "citizen_count": s.citizen_count,
                    "tags": s.tags,
                }
                for s in scenarios
            ],
        }

    async def _scenario_get(self, **kwargs: Any) -> dict[str, Any]:
        """Get a scenario template by ID."""
        scenario_id = kwargs.get("scenario_id")
        if not scenario_id:
            return {"error": "scenario_id required"}

        detail = kwargs.get("detail", False)
        scenario = await self._scenarios.get_scenario(scenario_id, detail=detail)

        if scenario is None:
            return {"error": f"Scenario not found: {scenario_id}"}

        return {
            "type": "scenario_detail",
            "scenario": scenario.to_dict(),
        }

    async def _scenario_start(self, **kwargs: Any) -> dict[str, Any]:
        """Start a new scenario session."""
        scenario_id = kwargs.get("scenario_id")
        if not scenario_id:
            return {"error": "scenario_id required"}

        try:
            session = await self._scenarios.start_session(scenario_id)
            return {
                "type": "scenario_session",
                "session": self._session_view_to_dict(session),
            }
        except ValueError as e:
            return {"error": str(e)}

    async def _scenario_tick(self, **kwargs: Any) -> dict[str, Any]:
        """Advance a scenario session."""
        session_id = kwargs.get("session_id")
        if not session_id:
            return {"error": "session_id required"}

        elapsed_seconds = kwargs.get("elapsed_seconds", 1.0)

        try:
            result = await self._scenarios.tick(session_id, elapsed_seconds)
            return {
                "type": "scenario_tick",
                "phase": result.phase,
                "time_elapsed": result.time_elapsed,
                "progress": [{"criterion": k, "met": v} for k, v in result.progress.items()],
                "is_complete": result.is_complete,
            }
        except ValueError as e:
            return {"error": str(e)}

    async def _scenario_end(self, **kwargs: Any) -> dict[str, Any]:
        """End/abandon a scenario session."""
        session_id = kwargs.get("session_id")
        if not session_id:
            return {"error": "session_id required"}

        reason = kwargs.get("reason", "")

        try:
            session = await self._scenarios.abandon_session(session_id, reason)
            return {
                "type": "scenario_session",
                "session": self._session_view_to_dict(session),
            }
        except ValueError as e:
            return {"error": str(e)}

    async def _scenario_sessions(self, **kwargs: Any) -> dict[str, Any]:
        """List active scenario sessions."""
        active_only = kwargs.get("active_only", True)
        limit = kwargs.get("limit", 20)

        sessions = await self._scenarios.list_sessions(
            active_only=active_only,
            limit=limit,
        )

        return {
            "type": "scenario_session_list",
            "count": len(sessions),
            "sessions": [self._session_view_to_dict(s) for s in sessions],
        }

    def _session_view_to_dict(self, session: SessionView) -> dict[str, Any]:
        """Convert SessionView to dict for response."""
        return {
            "id": session.id,
            "template_id": session.template_id,
            "template_name": session.template_name,
            "phase": session.phase,
            "is_active": session.is_active,
            "is_terminal": session.is_terminal,
            "citizens": session.citizens,
            "time_elapsed": session.time_elapsed,
            "progress": [{"criterion": k, "met": v} for k, v in session.progress.items()],
            "started_at": session.started_at,
            "ended_at": session.ended_at,
        }

    # =========================================================================
    # Consent Debt Operations - "Westworld where hosts can say no"
    # =========================================================================

    async def _consent_debt(self, **kwargs: Any) -> dict[str, Any]:
        """Get consent debt for a citizen in a session."""
        session_id = kwargs.get("session_id")
        citizen_name = kwargs.get("citizen_name")

        if not session_id or not citizen_name:
            return {"error": "session_id and citizen_name required"}

        try:
            debt = await self._scenarios.get_consent_debt(session_id, citizen_name)
            can_inject = await self._scenarios.can_inject_beat(session_id, citizen_name)
            return {
                "type": "consent_debt",
                "citizen": citizen_name,
                "debt": debt,
                "can_inject_beat": can_inject,
                "status": "ok",
            }
        except ValueError as e:
            return {"error": str(e)}

    async def _consent_incur(self, **kwargs: Any) -> dict[str, Any]:
        """Incur consent debt for forcing a host to act."""
        session_id = kwargs.get("session_id")
        citizen_name = kwargs.get("citizen_name")
        amount = kwargs.get("amount", 0.1)

        if not session_id or not citizen_name:
            return {"error": "session_id and citizen_name required"}

        try:
            result = await self._scenarios.incur_consent_debt(session_id, citizen_name, amount)
            return {
                "type": "consent_debt",
                "citizen": result["citizen"],
                "debt": result["new_debt"],
                "can_inject_beat": result["can_inject_beat"],
                "status": "debt_incurred",
            }
        except ValueError as e:
            return {"error": str(e)}

    async def _consent_apologize(self, **kwargs: Any) -> dict[str, Any]:
        """Reduce consent debt by apologizing."""
        session_id = kwargs.get("session_id")
        citizen_name = kwargs.get("citizen_name")
        reduction = kwargs.get("amount", 0.15)  # Use 'amount' param for reduction

        if not session_id or not citizen_name:
            return {"error": "session_id and citizen_name required"}

        try:
            result = await self._scenarios.apologize(session_id, citizen_name, reduction)
            return {
                "type": "consent_debt",
                "citizen": result["citizen"],
                "debt": result["new_debt"],
                "can_inject_beat": result["can_inject_beat"],
                "status": "apology_accepted",
            }
        except ValueError as e:
            return {"error": str(e)}

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _extract_user_id(self, observer: "Observer | Umwelt[Any, Any]") -> str:
        """Extract user ID from observer."""
        if isinstance(observer, Observer):
            return f"observer:{observer.archetype}"

        dna = getattr(observer, "dna", None)
        if dna:
            user_id = getattr(dna, "user_id", None) or getattr(dna, "name", None)
            if user_id:
                return str(user_id)

        return "anonymous"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ParkNode",
    # Renderings
    "ParkManifestRendering",
    "HostRendering",
    "HostListRendering",
    "EpisodeRendering",
    "InteractionRendering",
    "MemoryListRendering",
    "LocationListRendering",
]
