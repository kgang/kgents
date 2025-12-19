"""
Park Persistence: TableAdapter + D-gent integration for Park Crown Jewel.

Owns domain semantics for Park storage:
- WHEN to persist (host creation, memory formation, episode lifecycle, interactions)
- WHY to persist (persistent agent memory + consent tracking + immersive experience)
- HOW to compose (TableAdapter for entities, D-gent for deep memory)

AGENTESE aspects exposed:
- manifest: Show park status
- host.create: Create a new host
- host.interact: Interact with a host
- host.witness: View host memory
- episode.start/end: Session lifecycle
- consent.check: Verify consent boundaries

Punchdrunk + Westworld: Hosts have agency, persistent memory, and can refuse.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from models.park import (
    Episode,
    Host,
    HostMemory,
    Interaction,
    ParkLocation,
)

if TYPE_CHECKING:
    pass


@dataclass
class HostView:
    """View of a park host."""

    id: str
    name: str
    character: str
    backstory: str | None
    traits: dict[str, Any]
    values: list[str]
    boundaries: list[str]
    is_active: bool
    mood: str | None
    energy_level: float
    current_location: str | None
    interaction_count: int
    consent_refusal_count: int
    created_at: str


@dataclass
class MemoryView:
    """View of a host memory."""

    id: str
    host_id: str
    memory_type: str
    content: str
    summary: str | None
    salience: float
    emotional_valence: float
    access_count: int
    created_at: str


@dataclass
class EpisodeView:
    """View of a park episode."""

    id: str
    visitor_id: str | None
    visitor_name: str | None
    title: str | None
    status: str
    interaction_count: int
    hosts_met: list[str]
    locations_visited: list[str]
    started_at: str
    ended_at: str | None
    duration_seconds: int | None


@dataclass
class InteractionView:
    """View of a host interaction."""

    id: str
    episode_id: str
    host_id: str
    host_name: str
    interaction_type: str
    visitor_input: str
    host_response: str | None
    consent_requested: bool
    consent_given: bool | None
    consent_reason: str | None
    location: str | None
    host_emotion: str | None
    created_at: str


@dataclass
class LocationView:
    """View of a park location."""

    id: str
    name: str
    description: str | None
    atmosphere: str | None
    position: tuple[float | None, float | None]
    is_open: bool
    capacity: int | None
    connected_locations: list[str]


@dataclass
class ParkStatus:
    """Park health status."""

    total_hosts: int
    active_hosts: int
    total_episodes: int
    active_episodes: int
    total_memories: int
    total_locations: int
    consent_refusal_rate: float
    storage_backend: str


class ParkPersistence:
    """
    Persistence layer for Park Crown Jewel.

    Composes:
    - TableAdapter[Host]: Host state, traits, boundaries
    - TableAdapter[Episode]: Session lifecycle
    - D-gent: Deep memory content, semantic connections

    Domain Semantics:
    - Hosts are autonomous agents with boundaries
    - Episodes are bounded visitor sessions
    - Memories persist and influence behavior
    - Consent is core (hosts can refuse)

    Punchdrunk + Westworld Pattern:
    - Immersive experiences
    - Persistent memory across sessions
    - Agency for NPCs (can refuse uncomfortable interactions)
    - Observer-dependent perception

    Example:
        persistence = ParkPersistence(
            host_adapter=TableAdapter(Host, session_factory),
            episode_adapter=TableAdapter(Episode, session_factory),
            dgent=dgent_router,
        )

        host = await persistence.create_host("Dolores", character="rancher_daughter")
        episode = await persistence.start_episode(visitor_name="William")
        interaction = await persistence.interact(episode.id, host.id, "Hello Dolores")
    """

    def __init__(
        self,
        host_adapter: TableAdapter[Host],
        episode_adapter: TableAdapter[Episode],
        dgent: DgentProtocol,
    ) -> None:
        self.hosts = host_adapter
        self.episodes = episode_adapter
        self.dgent = dgent

    # =========================================================================
    # Host Management
    # =========================================================================

    async def create_host(
        self,
        name: str,
        character: str,
        backstory: str | None = None,
        traits: dict[str, Any] | None = None,
        values: list[str] | None = None,
        boundaries: list[str] | None = None,
        location: str | None = None,
    ) -> HostView:
        """
        Create a new park host.

        AGENTESE: world.park.host.create

        Args:
            name: Host name (unique)
            character: Character archetype
            backstory: Background narrative
            traits: Personality traits
            values: Core values
            boundaries: Things the host won't do
            location: Initial location in park

        Returns:
            HostView of the created host
        """
        host_id = f"host-{uuid.uuid4().hex[:12]}"

        async with self.hosts.session_factory() as session:
            host = Host(
                id=host_id,
                name=name,
                character=character,
                backstory=backstory,
                traits=traits or {},
                values=values or [],
                boundaries=boundaries or [],
                is_active=True,
                mood=None,
                energy_level=1.0,
                current_location=location,
                interaction_count=0,
                consent_refusal_count=0,
                memory_datum_id=None,
            )
            session.add(host)
            await session.commit()

            return HostView(
                id=host_id,
                name=name,
                character=character,
                backstory=backstory,
                traits=traits or {},
                values=values or [],
                boundaries=boundaries or [],
                is_active=True,
                mood=None,
                energy_level=1.0,
                current_location=location,
                interaction_count=0,
                consent_refusal_count=0,
                created_at=host.created_at.isoformat() if host.created_at else "",
            )

    async def get_host(self, host_id: str) -> HostView | None:
        """Get a host by ID."""
        async with self.hosts.session_factory() as session:
            host = await session.get(Host, host_id)
            if host is None:
                return None

            return self._host_to_view(host)

    async def get_host_by_name(self, name: str) -> HostView | None:
        """Get a host by name."""
        async with self.hosts.session_factory() as session:
            stmt = select(Host).where(Host.name == name)
            result = await session.execute(stmt)
            host = result.scalar_one_or_none()
            if host is None:
                return None

            return self._host_to_view(host)

    async def list_hosts(
        self,
        character: str | None = None,
        location: str | None = None,
        active_only: bool = True,
        limit: int = 50,
    ) -> list[HostView]:
        """List hosts with optional filters."""
        async with self.hosts.session_factory() as session:
            stmt = select(Host)

            if character:
                stmt = stmt.where(Host.character == character)
            if location:
                stmt = stmt.where(Host.current_location == location)
            if active_only:
                stmt = stmt.where(Host.is_active)

            stmt = stmt.order_by(Host.name).limit(limit)
            result = await session.execute(stmt)
            hosts = result.scalars().all()

            return [self._host_to_view(h) for h in hosts]

    async def update_host_state(
        self,
        host_id: str,
        mood: str | None = None,
        energy_level: float | None = None,
        location: str | None = None,
    ) -> HostView | None:
        """Update host state (mood, energy, location)."""
        async with self.hosts.session_factory() as session:
            host = await session.get(Host, host_id)
            if host is None:
                return None

            if mood is not None:
                host.mood = mood
            if energy_level is not None:
                host.energy_level = max(0.0, min(1.0, energy_level))
            if location is not None:
                host.current_location = location

            await session.commit()
            return self._host_to_view(host)

    # =========================================================================
    # Memory Management
    # =========================================================================

    async def form_memory(
        self,
        host_id: str,
        content: str,
        memory_type: str = "event",
        salience: float = 0.5,
        emotional_valence: float = 0.0,
        episode_id: str | None = None,
        visitor_id: str | None = None,
    ) -> MemoryView | None:
        """
        Form a new memory for a host.

        AGENTESE: world.park.host.remember

        Args:
            host_id: Host forming the memory
            content: Memory content
            memory_type: Type ("event", "person", "place", "emotion", "insight")
            salience: Importance (0-1)
            emotional_valence: Emotion (-1 to 1)
            episode_id: Source episode
            visitor_id: Related visitor

        Returns:
            MemoryView or None if host not found
        """
        async with self.hosts.session_factory() as session:
            host = await session.get(Host, host_id)
            if host is None:
                return None

            memory_id = f"memory-{uuid.uuid4().hex[:12]}"

            # Store in D-gent for semantic retrieval
            datum = Datum(
                id=f"park-memory-{memory_id}",
                content=content.encode("utf-8"),
                created_at=time.time(),
                causal_parent=host.memory_datum_id,  # Link to previous memory
                metadata={
                    "type": "host_memory",
                    "host_id": host_id,
                    "memory_type": memory_type,
                    "salience": str(salience),
                },
            )
            datum_id = await self.dgent.put(datum)

            # Create summary (first 100 chars)
            summary = content[:100].strip()
            if len(content) > 100:
                summary += "..."

            memory = HostMemory(
                id=memory_id,
                host_id=host_id,
                memory_type=memory_type,
                content=content,
                summary=summary,
                salience=salience,
                emotional_valence=emotional_valence,
                access_count=0,
                last_accessed=None,
                episode_id=episode_id,
                visitor_id=visitor_id,
                datum_id=datum_id,
            )
            session.add(memory)

            # Update host's memory chain head
            host.memory_datum_id = datum_id

            await session.commit()

            return MemoryView(
                id=memory_id,
                host_id=host_id,
                memory_type=memory_type,
                content=content,
                summary=summary,
                salience=salience,
                emotional_valence=emotional_valence,
                access_count=0,
                created_at=memory.created_at.isoformat() if memory.created_at else "",
            )

    async def recall_memories(
        self,
        host_id: str,
        memory_type: str | None = None,
        min_salience: float = 0.0,
        limit: int = 20,
    ) -> list[MemoryView]:
        """
        Recall host memories.

        AGENTESE: world.park.host.witness

        Args:
            host_id: Host to query
            memory_type: Filter by type
            min_salience: Minimum salience threshold
            limit: Maximum memories

        Returns:
            List of MemoryView ordered by salience
        """
        async with self.hosts.session_factory() as session:
            stmt = (
                select(HostMemory)
                .where(HostMemory.host_id == host_id)
                .where(HostMemory.salience >= min_salience)
            )

            if memory_type:
                stmt = stmt.where(HostMemory.memory_type == memory_type)

            stmt = stmt.order_by(HostMemory.salience.desc()).limit(limit)
            result = await session.execute(stmt)
            memories = result.scalars().all()

            # Update access counts
            for m in memories:
                m.access_count += 1
                m.last_accessed = datetime.now(UTC)

            await session.commit()

            return [self._memory_to_view(m) for m in memories]

    async def decay_memories(
        self,
        host_id: str,
        decay_rate: float = 0.05,
        min_salience: float = 0.1,
    ) -> int:
        """
        Decay memory salience over time.

        Returns count of memories decayed.
        """
        async with self.hosts.session_factory() as session:
            stmt = select(HostMemory).where(
                HostMemory.host_id == host_id,
                HostMemory.salience > min_salience,
            )
            result = await session.execute(stmt)
            memories = result.scalars().all()

            decayed = 0
            for m in memories:
                m.salience = max(min_salience, m.salience - decay_rate)
                decayed += 1

            await session.commit()
            return decayed

    # =========================================================================
    # Episode Management
    # =========================================================================

    async def start_episode(
        self,
        visitor_id: str | None = None,
        visitor_name: str | None = None,
        title: str | None = None,
    ) -> EpisodeView:
        """
        Start a new park episode.

        AGENTESE: world.park.episode.start

        Args:
            visitor_id: Optional visitor identifier
            visitor_name: Optional visitor display name
            title: Optional episode title

        Returns:
            EpisodeView of the new episode
        """
        episode_id = f"episode-{uuid.uuid4().hex[:12]}"

        async with self.episodes.session_factory() as session:
            episode = Episode(
                id=episode_id,
                visitor_id=visitor_id,
                visitor_name=visitor_name,
                title=title,
                summary=None,
                status="active",
                duration_seconds=None,
                interaction_count=0,
                hosts_met=[],
                locations_visited=[],
            )
            session.add(episode)
            await session.commit()

            return EpisodeView(
                id=episode_id,
                visitor_id=visitor_id,
                visitor_name=visitor_name,
                title=title,
                status="active",
                interaction_count=0,
                hosts_met=[],
                locations_visited=[],
                started_at=episode.started_at.isoformat() if episode.started_at else "",
                ended_at=None,
                duration_seconds=None,
            )

    async def end_episode(
        self,
        episode_id: str,
        summary: str | None = None,
        status: str = "completed",
    ) -> EpisodeView | None:
        """
        End a park episode.

        AGENTESE: world.park.episode.end

        Args:
            episode_id: Episode to end
            summary: Optional summary
            status: Ending status ("completed", "abandoned")

        Returns:
            EpisodeView or None
        """
        async with self.episodes.session_factory() as session:
            episode = await session.get(Episode, episode_id)
            if episode is None or episode.status != "active":
                return None

            episode.status = status
            episode.ended_at = datetime.now(UTC)
            episode.summary = summary

            # Calculate duration
            if episode.started_at:
                duration = (episode.ended_at - episode.started_at).total_seconds()
                episode.duration_seconds = int(duration)

            await session.commit()

            return self._episode_to_view(episode)

    async def get_episode(self, episode_id: str) -> EpisodeView | None:
        """Get an episode by ID."""
        async with self.episodes.session_factory() as session:
            episode = await session.get(Episode, episode_id)
            if episode is None:
                return None

            return self._episode_to_view(episode)

    async def list_episodes(
        self,
        visitor_id: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> list[EpisodeView]:
        """List episodes with optional filters."""
        async with self.episodes.session_factory() as session:
            stmt = select(Episode)

            if visitor_id:
                stmt = stmt.where(Episode.visitor_id == visitor_id)
            if status:
                stmt = stmt.where(Episode.status == status)

            stmt = stmt.order_by(Episode.started_at.desc()).limit(limit)
            result = await session.execute(stmt)
            episodes = result.scalars().all()

            return [self._episode_to_view(e) for e in episodes]

    # =========================================================================
    # Interaction Management
    # =========================================================================

    async def interact(
        self,
        episode_id: str,
        host_id: str,
        visitor_input: str,
        interaction_type: str = "dialogue",
        location: str | None = None,
        check_consent: bool = True,
    ) -> InteractionView | None:
        """
        Create an interaction with a host.

        AGENTESE: world.park.host.interact

        Consent is CORE: if check_consent=True and the interaction crosses
        a host boundary, the host will refuse and the interaction records this.

        Args:
            episode_id: Active episode
            host_id: Host to interact with
            visitor_input: What the visitor said/did
            interaction_type: Type ("dialogue", "action", "observation", "gift")
            location: Where the interaction occurred
            check_consent: Whether to check host boundaries

        Returns:
            InteractionView or None if episode/host not found
        """
        async with self.hosts.session_factory() as session:
            episode = await session.get(Episode, episode_id)
            host = await session.get(Host, host_id)

            if episode is None or episode.status != "active":
                return None
            if host is None or not host.is_active:
                return None

            interaction_id = f"interact-{uuid.uuid4().hex[:12]}"

            # Check consent if needed
            consent_requested = False
            consent_given = None
            consent_reason = None

            if check_consent and host.boundaries:
                # Check if input crosses any boundary
                input_lower = visitor_input.lower()
                for boundary in host.boundaries:
                    if boundary.lower() in input_lower:
                        consent_requested = True
                        consent_given = False
                        consent_reason = f"Host declined: '{boundary}' is a boundary"
                        host.consent_refusal_count += 1
                        break

            # Generate host response (for now, placeholder)
            # In real implementation, this would use the K-gent soul
            host_response = None
            host_emotion = None

            if consent_given is False:
                host_response = f"I'm sorry, but I can't do that. {consent_reason}"
                host_emotion = "uncomfortable"
            else:
                # Placeholder response
                host_response = f"*{host.name} considers your words*"
                host_emotion = host.mood or "neutral"

            # Create interaction record
            interaction = Interaction(
                id=interaction_id,
                episode_id=episode_id,
                host_id=host_id,
                interaction_type=interaction_type,
                visitor_input=visitor_input,
                host_response=host_response,
                consent_requested=consent_requested,
                consent_given=consent_given,
                consent_reason=consent_reason,
                location=location or host.current_location,
                host_emotion=host_emotion,
                visitor_sentiment=None,
            )
            session.add(interaction)

            # Update host interaction count
            host.interaction_count += 1

            # Update episode
            episode.interaction_count += 1
            if host.name not in (episode.hosts_met or []):
                episode.hosts_met = (episode.hosts_met or []) + [host.name]
            if location and location not in (episode.locations_visited or []):
                episode.locations_visited = (episode.locations_visited or []) + [location]

            await session.commit()

            return InteractionView(
                id=interaction_id,
                episode_id=episode_id,
                host_id=host_id,
                host_name=host.name,
                interaction_type=interaction_type,
                visitor_input=visitor_input,
                host_response=host_response,
                consent_requested=consent_requested,
                consent_given=consent_given,
                consent_reason=consent_reason,
                location=location or host.current_location,
                host_emotion=host_emotion,
                created_at=interaction.created_at.isoformat() if interaction.created_at else "",
            )

    async def list_interactions(
        self,
        episode_id: str | None = None,
        host_id: str | None = None,
        limit: int = 50,
    ) -> list[InteractionView]:
        """List interactions with optional filters."""
        async with self.hosts.session_factory() as session:
            stmt = select(Interaction, Host.name).join(Host)

            if episode_id:
                stmt = stmt.where(Interaction.episode_id == episode_id)
            if host_id:
                stmt = stmt.where(Interaction.host_id == host_id)

            stmt = stmt.order_by(Interaction.created_at).limit(limit)
            result = await session.execute(stmt)
            rows = result.all()

            return [
                InteractionView(
                    id=i.id,
                    episode_id=i.episode_id,
                    host_id=i.host_id,
                    host_name=name,
                    interaction_type=i.interaction_type,
                    visitor_input=i.visitor_input,
                    host_response=i.host_response,
                    consent_requested=i.consent_requested,
                    consent_given=i.consent_given,
                    consent_reason=i.consent_reason,
                    location=i.location,
                    host_emotion=i.host_emotion,
                    created_at=i.created_at.isoformat() if i.created_at else "",
                )
                for i, name in rows
            ]

    # =========================================================================
    # Location Management
    # =========================================================================

    async def create_location(
        self,
        name: str,
        description: str | None = None,
        atmosphere: str | None = None,
        x: float | None = None,
        y: float | None = None,
        capacity: int | None = None,
        connected_to: list[str] | None = None,
    ) -> LocationView:
        """Create a park location."""
        location_id = f"location-{uuid.uuid4().hex[:12]}"

        async with self.hosts.session_factory() as session:
            location = ParkLocation(
                id=location_id,
                name=name,
                description=description,
                atmosphere=atmosphere,
                x=x,
                y=y,
                connected_locations=connected_to or [],
                is_open=True,
                capacity=capacity,
            )
            session.add(location)
            await session.commit()

            return LocationView(
                id=location_id,
                name=name,
                description=description,
                atmosphere=atmosphere,
                position=(x, y),
                is_open=True,
                capacity=capacity,
                connected_locations=connected_to or [],
            )

    async def list_locations(self, open_only: bool = True) -> list[LocationView]:
        """List park locations."""
        async with self.hosts.session_factory() as session:
            stmt = select(ParkLocation)
            if open_only:
                stmt = stmt.where(ParkLocation.is_open)
            stmt = stmt.order_by(ParkLocation.name)
            result = await session.execute(stmt)
            locations = result.scalars().all()

            return [
                LocationView(
                    id=l.id,
                    name=l.name,
                    description=l.description,
                    atmosphere=l.atmosphere,
                    position=(l.x, l.y),
                    is_open=l.is_open,
                    capacity=l.capacity,
                    connected_locations=l.connected_locations or [],
                )
                for l in locations
            ]

    # =========================================================================
    # Health Status
    # =========================================================================

    async def manifest(self) -> ParkStatus:
        """
        Get park health status.

        AGENTESE: world.park.manifest
        """
        async with self.hosts.session_factory() as session:
            # Count hosts
            total_hosts_result = await session.execute(select(func.count()).select_from(Host))
            total_hosts = total_hosts_result.scalar() or 0

            active_hosts_result = await session.execute(
                select(func.count()).select_from(Host).where(Host.is_active)
            )
            active_hosts = active_hosts_result.scalar() or 0

            # Count episodes
            total_episodes_result = await session.execute(select(func.count()).select_from(Episode))
            total_episodes = total_episodes_result.scalar() or 0

            active_episodes_result = await session.execute(
                select(func.count()).select_from(Episode).where(Episode.status == "active")
            )
            active_episodes = active_episodes_result.scalar() or 0

            # Count memories
            total_memories_result = await session.execute(
                select(func.count()).select_from(HostMemory)
            )
            total_memories = total_memories_result.scalar() or 0

            # Count locations
            total_locations_result = await session.execute(
                select(func.count()).select_from(ParkLocation)
            )
            total_locations = total_locations_result.scalar() or 0

            # Calculate consent refusal rate
            total_interactions_result = await session.execute(
                select(func.count()).select_from(Interaction)
            )
            total_interactions = total_interactions_result.scalar() or 0

            refusals_result = await session.execute(
                select(func.count()).select_from(Interaction).where(not Interaction.consent_given)
            )
            refusals = refusals_result.scalar() or 0

            consent_refusal_rate = refusals / total_interactions if total_interactions > 0 else 0.0

        return ParkStatus(
            total_hosts=total_hosts,
            active_hosts=active_hosts,
            total_episodes=total_episodes,
            active_episodes=active_episodes,
            total_memories=total_memories,
            total_locations=total_locations,
            consent_refusal_rate=consent_refusal_rate,
            storage_backend="postgres"
            if "postgres" in str(self.hosts.session_factory).lower()
            else "sqlite",
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _host_to_view(self, host: Host) -> HostView:
        """Convert Host model to HostView."""
        return HostView(
            id=host.id,
            name=host.name,
            character=host.character,
            backstory=host.backstory,
            traits=host.traits or {},
            values=host.values or [],
            boundaries=host.boundaries or [],
            is_active=host.is_active,
            mood=host.mood,
            energy_level=host.energy_level,
            current_location=host.current_location,
            interaction_count=host.interaction_count,
            consent_refusal_count=host.consent_refusal_count,
            created_at=host.created_at.isoformat() if host.created_at else "",
        )

    def _memory_to_view(self, memory: HostMemory) -> MemoryView:
        """Convert HostMemory model to MemoryView."""
        return MemoryView(
            id=memory.id,
            host_id=memory.host_id,
            memory_type=memory.memory_type,
            content=memory.content,
            summary=memory.summary,
            salience=memory.salience,
            emotional_valence=memory.emotional_valence,
            access_count=memory.access_count,
            created_at=memory.created_at.isoformat() if memory.created_at else "",
        )

    def _episode_to_view(self, episode: Episode) -> EpisodeView:
        """Convert Episode model to EpisodeView."""
        return EpisodeView(
            id=episode.id,
            visitor_id=episode.visitor_id,
            visitor_name=episode.visitor_name,
            title=episode.title,
            status=episode.status,
            interaction_count=episode.interaction_count,
            hosts_met=episode.hosts_met or [],
            locations_visited=episode.locations_visited or [],
            started_at=episode.started_at.isoformat() if episode.started_at else "",
            ended_at=episode.ended_at.isoformat() if episode.ended_at else None,
            duration_seconds=episode.duration_seconds,
        )


__all__ = [
    "ParkPersistence",
    "HostView",
    "MemoryView",
    "EpisodeView",
    "InteractionView",
    "LocationView",
    "ParkStatus",
]
