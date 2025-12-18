"""
Gardener Persistence: TableAdapter + D-gent integration for Gardener Crown Jewel.

Owns domain semantics for Gardener storage:
- WHEN to persist (session lifecycle, idea capture, nurturing, lifecycle transitions)
- WHY to persist (session history + idea graphs + semantic connections)
- HOW to compose (TableAdapter for sessions/ideas, D-gent for content/connections)

AGENTESE aspects exposed:
- session.start: Begin a gardening session
- session.end: End current session
- idea.plant: Capture a new idea
- idea.nurture: Tend to an existing idea
- idea.harvest: Promote idea to next lifecycle stage
- manifest: Show garden status

Differance Integration (Phase 6C):
- start_session() → trace with alternatives (resume_previous)
- end_session() → trace with alternatives (extend)
- plant_idea() → trace with alternatives (different_lifecycle, auto_connect)
- nurture_idea() → trace with alternatives (prune, water)
- harvest_idea() → trace with alternatives (stay, compost)
- create_plot() → trace with alternatives (use_existing)
- get/list → NO traces (read-only)

See: docs/skills/metaphysical-fullstack.md
See: plans/differance-crown-jewel-wiring.md (Phase 6C)
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from agents.differance.alternatives import get_alternatives
from agents.differance.integration import DifferanceIntegration
from models.gardener import (
    GardenIdea,
    GardenPlot,
    GardenSession,
    IdeaConnection,
    IdeaLifecycle,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class SessionView:
    """View of a gardening session."""

    id: str
    title: str | None
    notes: str | None
    duration_seconds: int | None
    idea_count: int
    created_at: str
    is_active: bool


@dataclass
class IdeaView:
    """View of a garden idea."""

    id: str
    content: str
    lifecycle: str
    confidence: float
    session_id: str | None
    plot_id: str | None
    plot_name: str | None
    tags: list[str]
    nurture_count: int
    last_nurtured: str | None
    created_at: str
    connections: list["ConnectionView"] = field(default_factory=list)


@dataclass
class PlotView:
    """View of a garden plot."""

    id: str
    name: str
    description: str | None
    color: str | None
    idea_count: int
    created_at: str


@dataclass
class ConnectionView:
    """View of an idea connection."""

    id: str
    source_id: str
    target_id: str
    connection_type: str
    strength: float
    notes: str | None


@dataclass
class GardenStatus:
    """Garden health status."""

    total_sessions: int
    total_ideas: int
    total_plots: int
    ideas_by_lifecycle: dict[str, int]
    total_connections: int
    storage_backend: str


class GardenerPersistence:
    """
    Persistence layer for Gardener Crown Jewel.

    Composes:
    - TableAdapter[GardenSession]: Session lifecycle and metadata
    - TableAdapter[GardenIdea]: Idea state, lifecycle, connections
    - D-gent: Full idea content, semantic connections

    Domain Semantics:
    - Sessions group related gardening activity
    - Ideas flow: SEED → SAPLING → TREE → FLOWER → COMPOST
    - Plots provide thematic groupings
    - Connections form a semantic graph

    Example:
        persistence = GardenerPersistence(
            session_adapter=TableAdapter(GardenSession, session_factory),
            idea_adapter=TableAdapter(GardenIdea, session_factory),
            dgent=dgent_router,
        )

        session = await persistence.start_session("Morning thoughts")
        idea = await persistence.plant_idea("Category theory unifies", session.id)
    """

    def __init__(
        self,
        session_adapter: TableAdapter[GardenSession],
        idea_adapter: TableAdapter[GardenIdea],
        dgent: DgentProtocol,
    ) -> None:
        self.sessions = session_adapter
        self.ideas = idea_adapter
        self.dgent = dgent
        self._current_session_id: str | None = None
        # Differance integration for trace recording (Phase 6C)
        self._differance = DifferanceIntegration("gardener")

    # =========================================================================
    # Session Management
    # =========================================================================

    async def start_session(
        self,
        title: str | None = None,
        notes: str | None = None,
    ) -> SessionView:
        """
        Start a new gardening session.

        AGENTESE: concept.gardener.session.start

        Args:
            title: Optional session title
            notes: Optional session notes

        Returns:
            SessionView of the new session
        """
        session_id = f"session-{uuid.uuid4().hex[:12]}"

        async with self.sessions.session_factory() as session:
            garden_session = GardenSession(
                id=session_id,
                title=title,
                notes=notes,
                duration_seconds=None,
            )
            session.add(garden_session)
            await session.commit()

            self._current_session_id = session_id

            result = SessionView(
                id=session_id,
                title=title,
                notes=notes,
                duration_seconds=None,
                idea_count=0,
                created_at=garden_session.created_at.isoformat()
                if garden_session.created_at
                else "",
                is_active=True,
            )

            # Fire-and-forget trace recording (Phase 6C)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    self._differance.record(
                        operation="session_start",
                        inputs=(title or "untitled",),
                        output=session_id,
                        context=f"Started session: {title or 'untitled'}",
                        alternatives=get_alternatives("gardener", "session_start"),
                    )
                )
            except RuntimeError:
                logger.debug("No event loop for session_start trace recording")

            return result

    async def end_session(
        self,
        session_id: str | None = None,
        notes: str | None = None,
    ) -> SessionView | None:
        """
        End a gardening session.

        AGENTESE: concept.gardener.session.end

        Args:
            session_id: Session to end (or current session if None)
            notes: Optional closing notes

        Returns:
            SessionView or None if session not found
        """
        session_id = session_id or self._current_session_id
        if session_id is None:
            return None

        async with self.sessions.session_factory() as session:
            garden_session = await session.get(GardenSession, session_id)
            if garden_session is None:
                return None

            # Calculate duration
            if garden_session.created_at:
                duration = int(
                    (datetime.utcnow() - garden_session.created_at).total_seconds()
                )
                garden_session.duration_seconds = duration

            if notes:
                garden_session.notes = (garden_session.notes or "") + f"\n{notes}"

            # Count ideas in session
            count_result = await session.execute(
                select(func.count())
                .select_from(GardenIdea)
                .where(GardenIdea.session_id == session_id)
            )
            idea_count = count_result.scalar() or 0

            await session.commit()

            if self._current_session_id == session_id:
                self._current_session_id = None

            result = SessionView(
                id=session_id,
                title=garden_session.title,
                notes=garden_session.notes,
                duration_seconds=garden_session.duration_seconds,
                idea_count=idea_count,
                created_at=garden_session.created_at.isoformat()
                if garden_session.created_at
                else "",
                is_active=False,
            )

            # Fire-and-forget trace recording (Phase 6C)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    self._differance.record(
                        operation="session_end",
                        inputs=(session_id,),
                        output=f"ended:{session_id}",
                        context=f"Ended session with {idea_count} ideas",
                        alternatives=get_alternatives("gardener", "session_end"),
                    )
                )
            except RuntimeError:
                logger.debug("No event loop for session_end trace recording")

            return result

    async def get_current_session(self) -> SessionView | None:
        """Get the current active session."""
        if self._current_session_id is None:
            return None
        return await self.get_session(self._current_session_id)

    async def get_session(self, session_id: str) -> SessionView | None:
        """Get a session by ID."""
        async with self.sessions.session_factory() as session:
            garden_session = await session.get(GardenSession, session_id)
            if garden_session is None:
                return None

            # Count ideas
            count_result = await session.execute(
                select(func.count())
                .select_from(GardenIdea)
                .where(GardenIdea.session_id == session_id)
            )
            idea_count = count_result.scalar() or 0

            return SessionView(
                id=session_id,
                title=garden_session.title,
                notes=garden_session.notes,
                duration_seconds=garden_session.duration_seconds,
                idea_count=idea_count,
                created_at=garden_session.created_at.isoformat()
                if garden_session.created_at
                else "",
                is_active=(self._current_session_id == session_id),
            )

    async def list_sessions(self, limit: int = 20) -> list[SessionView]:
        """List recent gardening sessions."""
        async with self.sessions.session_factory() as session:
            stmt = (
                select(GardenSession)
                .order_by(GardenSession.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            sessions = result.scalars().all()

            views = []
            for s in sessions:
                # Count ideas for each session
                count_result = await session.execute(
                    select(func.count())
                    .select_from(GardenIdea)
                    .where(GardenIdea.session_id == s.id)
                )
                idea_count = count_result.scalar() or 0

                views.append(
                    SessionView(
                        id=s.id,
                        title=s.title,
                        notes=s.notes,
                        duration_seconds=s.duration_seconds,
                        idea_count=idea_count,
                        created_at=s.created_at.isoformat() if s.created_at else "",
                        is_active=(self._current_session_id == s.id),
                    )
                )

            return views

    # =========================================================================
    # Idea Management
    # =========================================================================

    async def plant_idea(
        self,
        content: str,
        session_id: str | None = None,
        plot_id: str | None = None,
        tags: list[str] | None = None,
        confidence: float = 0.3,
    ) -> IdeaView:
        """
        Plant a new idea in the garden.

        AGENTESE: self.garden.plant

        Args:
            content: The idea content
            session_id: Session to associate (or current session)
            plot_id: Optional plot to place idea in
            tags: Optional tags for categorization
            confidence: Initial confidence (0.0 to 1.0)

        Returns:
            IdeaView of the planted idea
        """
        idea_id = f"idea-{uuid.uuid4().hex[:12]}"
        session_id = session_id or self._current_session_id
        tags = tags or []

        # Store semantic content in D-gent
        datum = Datum(
            id=f"garden-{idea_id}",
            content=content.encode("utf-8"),
            created_at=time.time(),
            causal_parent=None,
            metadata={
                "type": "garden_idea",
                "lifecycle": IdeaLifecycle.SEED.value,
                "session_id": session_id or "",
            },
        )
        datum_id = await self.dgent.put(datum)

        async with self.ideas.session_factory() as session:
            # Get plot name if plot_id provided
            plot_name = None
            if plot_id:
                plot = await session.get(GardenPlot, plot_id)
                if plot:
                    plot_name = plot.name

            idea = GardenIdea(
                id=idea_id,
                content=content,
                lifecycle=IdeaLifecycle.SEED.value,
                confidence=confidence,
                session_id=session_id,
                plot_id=plot_id,
                datum_id=datum_id,
                tags=tags,
                nurture_count=0,
                last_nurtured=None,
            )
            session.add(idea)
            await session.commit()

            result = IdeaView(
                id=idea_id,
                content=content,
                lifecycle=IdeaLifecycle.SEED.value,
                confidence=confidence,
                session_id=session_id,
                plot_id=plot_id,
                plot_name=plot_name,
                tags=tags,
                nurture_count=0,
                last_nurtured=None,
                created_at=idea.created_at.isoformat() if idea.created_at else "",
                connections=[],
            )

            # Fire-and-forget trace recording (Phase 6C)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    self._differance.record(
                        operation="plant",
                        inputs=(content[:100],),  # Truncate for trace
                        output=idea_id,
                        context=f"Planted idea in {plot_name or 'default plot'}",
                        alternatives=get_alternatives("gardener", "plant"),
                    )
                )
            except RuntimeError:
                logger.debug("No event loop for plant trace recording")

            return result

    async def nurture_idea(
        self,
        idea_id: str,
        refinement: str | None = None,
        confidence_delta: float = 0.1,
    ) -> IdeaView | None:
        """
        Nurture an existing idea.

        AGENTESE: self.garden.nurture

        Args:
            idea_id: ID of the idea to nurture
            refinement: Optional refinement to append to content
            confidence_delta: How much to increase confidence

        Returns:
            Updated IdeaView or None if not found
        """
        async with self.ideas.session_factory() as session:
            idea = await session.get(GardenIdea, idea_id)
            if idea is None:
                return None

            # Update idea
            idea.nurture()
            idea.confidence = min(1.0, idea.confidence + confidence_delta)

            if refinement:
                idea.content = f"{idea.content}\n\n---\n\n{refinement}"

                # Update D-gent content
                if idea.datum_id:
                    datum = Datum(
                        id=idea.datum_id,
                        content=idea.content.encode("utf-8"),
                        created_at=time.time(),
                        causal_parent=None,
                        metadata={
                            "type": "garden_idea",
                            "lifecycle": idea.lifecycle,
                            "nurtured": "true",
                        },
                    )
                    await self.dgent.put(datum)

            await session.commit()

            # Get plot name
            plot_name = None
            if idea.plot_id:
                plot = await session.get(GardenPlot, idea.plot_id)
                if plot:
                    plot_name = plot.name

            return IdeaView(
                id=idea.id,
                content=idea.content,
                lifecycle=idea.lifecycle,
                confidence=idea.confidence,
                session_id=idea.session_id,
                plot_id=idea.plot_id,
                plot_name=plot_name,
                tags=idea.tags or [],
                nurture_count=idea.nurture_count,
                last_nurtured=idea.last_nurtured.isoformat()
                if idea.last_nurtured
                else None,
                created_at=idea.created_at.isoformat() if idea.created_at else "",
                connections=[],
            )

    async def harvest_idea(self, idea_id: str) -> IdeaView | None:
        """
        Promote idea to next lifecycle stage.

        AGENTESE: self.garden.harvest

        Lifecycle: SEED → SAPLING → TREE → FLOWER → COMPOST

        Returns:
            Updated IdeaView or None if not found or already at max stage
        """
        async with self.ideas.session_factory() as session:
            idea = await session.get(GardenIdea, idea_id)
            if idea is None:
                return None

            promoted = idea.promote()
            if not promoted:
                return None  # Already at COMPOST

            # Update D-gent metadata
            if idea.datum_id:
                datum = await self.dgent.get(idea.datum_id)
                if datum:
                    new_datum = Datum(
                        id=datum.id,
                        content=datum.content,
                        created_at=datum.created_at,
                        causal_parent=datum.causal_parent,
                        metadata={
                            **datum.metadata,
                            "lifecycle": idea.lifecycle,
                        },
                    )
                    await self.dgent.put(new_datum)

            await session.commit()

            # Get plot name
            plot_name = None
            if idea.plot_id:
                plot = await session.get(GardenPlot, idea.plot_id)
                if plot:
                    plot_name = plot.name

            return IdeaView(
                id=idea.id,
                content=idea.content,
                lifecycle=idea.lifecycle,
                confidence=idea.confidence,
                session_id=idea.session_id,
                plot_id=idea.plot_id,
                plot_name=plot_name,
                tags=idea.tags or [],
                nurture_count=idea.nurture_count,
                last_nurtured=idea.last_nurtured.isoformat()
                if idea.last_nurtured
                else None,
                created_at=idea.created_at.isoformat() if idea.created_at else "",
                connections=[],
            )

    async def get_idea(
        self,
        idea_id: str,
        include_connections: bool = False,
    ) -> IdeaView | None:
        """Get an idea by ID."""
        async with self.ideas.session_factory() as session:
            idea = await session.get(GardenIdea, idea_id)
            if idea is None:
                return None

            # Get plot name
            plot_name = None
            if idea.plot_id:
                plot = await session.get(GardenPlot, idea.plot_id)
                if plot:
                    plot_name = plot.name

            # Get connections if requested
            connections = []
            if include_connections:
                stmt = select(IdeaConnection).where(
                    (IdeaConnection.source_id == idea_id)
                    | (IdeaConnection.target_id == idea_id)
                )
                result = await session.execute(stmt)
                conn_rows = result.scalars().all()
                connections = [
                    ConnectionView(
                        id=c.id,
                        source_id=c.source_id,
                        target_id=c.target_id,
                        connection_type=c.connection_type,
                        strength=c.strength,
                        notes=c.notes,
                    )
                    for c in conn_rows
                ]

            return IdeaView(
                id=idea.id,
                content=idea.content,
                lifecycle=idea.lifecycle,
                confidence=idea.confidence,
                session_id=idea.session_id,
                plot_id=idea.plot_id,
                plot_name=plot_name,
                tags=idea.tags or [],
                nurture_count=idea.nurture_count,
                last_nurtured=idea.last_nurtured.isoformat()
                if idea.last_nurtured
                else None,
                created_at=idea.created_at.isoformat() if idea.created_at else "",
                connections=connections,
            )

    async def list_ideas(
        self,
        lifecycle: str | None = None,
        plot_id: str | None = None,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[IdeaView]:
        """List ideas with optional filters."""
        async with self.ideas.session_factory() as session:
            stmt = select(GardenIdea)

            if lifecycle:
                stmt = stmt.where(GardenIdea.lifecycle == lifecycle)
            if plot_id:
                stmt = stmt.where(GardenIdea.plot_id == plot_id)
            if session_id:
                stmt = stmt.where(GardenIdea.session_id == session_id)

            stmt = stmt.order_by(GardenIdea.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            ideas = result.scalars().all()

            views = []
            for idea in ideas:
                plot_name = None
                if idea.plot_id:
                    plot = await session.get(GardenPlot, idea.plot_id)
                    if plot:
                        plot_name = plot.name

                views.append(
                    IdeaView(
                        id=idea.id,
                        content=idea.content,
                        lifecycle=idea.lifecycle,
                        confidence=idea.confidence,
                        session_id=idea.session_id,
                        plot_id=idea.plot_id,
                        plot_name=plot_name,
                        tags=idea.tags or [],
                        nurture_count=idea.nurture_count,
                        last_nurtured=idea.last_nurtured.isoformat()
                        if idea.last_nurtured
                        else None,
                        created_at=idea.created_at.isoformat()
                        if idea.created_at
                        else "",
                        connections=[],
                    )
                )

            return views

    # =========================================================================
    # Plot Management
    # =========================================================================

    async def create_plot(
        self,
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> PlotView:
        """Create a new garden plot."""
        plot_id = f"plot-{uuid.uuid4().hex[:12]}"

        async with self.ideas.session_factory() as session:
            plot = GardenPlot(
                id=plot_id,
                name=name,
                description=description,
                color=color,
            )
            session.add(plot)
            await session.commit()

            return PlotView(
                id=plot_id,
                name=name,
                description=description,
                color=color,
                idea_count=0,
                created_at=plot.created_at.isoformat() if plot.created_at else "",
            )

    async def list_plots(self) -> list[PlotView]:
        """List all garden plots."""
        async with self.ideas.session_factory() as session:
            stmt = select(GardenPlot).order_by(GardenPlot.name)
            result = await session.execute(stmt)
            plots = result.scalars().all()

            views = []
            for plot in plots:
                # Count ideas in plot
                count_result = await session.execute(
                    select(func.count())
                    .select_from(GardenIdea)
                    .where(GardenIdea.plot_id == plot.id)
                )
                idea_count = count_result.scalar() or 0

                views.append(
                    PlotView(
                        id=plot.id,
                        name=plot.name,
                        description=plot.description,
                        color=plot.color,
                        idea_count=idea_count,
                        created_at=plot.created_at.isoformat()
                        if plot.created_at
                        else "",
                    )
                )

            return views

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect_ideas(
        self,
        source_id: str,
        target_id: str,
        connection_type: str = "relates_to",
        strength: float = 0.5,
        notes: str | None = None,
    ) -> ConnectionView | None:
        """Create a connection between two ideas."""
        async with self.ideas.session_factory() as session:
            # Verify both ideas exist
            source = await session.get(GardenIdea, source_id)
            target = await session.get(GardenIdea, target_id)
            if source is None or target is None:
                return None

            conn_id = f"conn-{uuid.uuid4().hex[:12]}"

            connection = IdeaConnection(
                id=conn_id,
                source_id=source_id,
                target_id=target_id,
                connection_type=connection_type,
                strength=strength,
                notes=notes,
            )
            session.add(connection)
            await session.commit()

            return ConnectionView(
                id=conn_id,
                source_id=source_id,
                target_id=target_id,
                connection_type=connection_type,
                strength=strength,
                notes=notes,
            )

    # =========================================================================
    # Garden Status
    # =========================================================================

    async def manifest(self) -> GardenStatus:
        """
        Get garden health status.

        AGENTESE: self.garden.manifest
        """
        async with self.ideas.session_factory() as session:
            # Count sessions
            session_count_result = await session.execute(
                select(func.count()).select_from(GardenSession)
            )
            total_sessions = session_count_result.scalar() or 0

            # Count ideas
            idea_count_result = await session.execute(
                select(func.count()).select_from(GardenIdea)
            )
            total_ideas = idea_count_result.scalar() or 0

            # Count plots
            plot_count_result = await session.execute(
                select(func.count()).select_from(GardenPlot)
            )
            total_plots = plot_count_result.scalar() or 0

            # Count ideas by lifecycle
            ideas_by_lifecycle = {}
            for lifecycle in IdeaLifecycle:
                lifecycle_count_result = await session.execute(
                    select(func.count())
                    .select_from(GardenIdea)
                    .where(GardenIdea.lifecycle == lifecycle.value)
                )
                count = lifecycle_count_result.scalar() or 0
                ideas_by_lifecycle[lifecycle.value] = count

            # Count connections
            conn_count_result = await session.execute(
                select(func.count()).select_from(IdeaConnection)
            )
            total_connections = conn_count_result.scalar() or 0

        return GardenStatus(
            total_sessions=total_sessions,
            total_ideas=total_ideas,
            total_plots=total_plots,
            ideas_by_lifecycle=ideas_by_lifecycle,
            total_connections=total_connections,
            storage_backend="postgres"
            if "postgres" in str(self.ideas.session_factory).lower()
            else "sqlite",
        )


__all__ = [
    "GardenerPersistence",
    "SessionView",
    "IdeaView",
    "PlotView",
    "ConnectionView",
    "GardenStatus",
]
