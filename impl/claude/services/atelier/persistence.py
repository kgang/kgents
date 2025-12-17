"""
Atelier Persistence: TableAdapter + D-gent integration for Atelier Crown Jewel.

Owns domain semantics for Atelier storage:
- WHEN to persist (workshop creation, artisan joins, contributions, exhibitions)
- WHY to persist (creative process visibility + artifact curation + collaboration tracking)
- HOW to compose (TableAdapter for structure, D-gent for creative content)

AGENTESE aspects exposed:
- manifest: Show atelier status
- workshop.create: Start a new workshop
- workshop.join: Add an artisan
- artifact.contribute: Submit creative work
- exhibition.open: Open gallery for viewing

Punchdrunk-inspired: Spectators can observe the creative process in real-time.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from models.atelier import (
    Artisan,
    ArtifactContribution,
    Exhibition,
    GalleryItem,
    Workshop,
)

if TYPE_CHECKING:
    pass


@dataclass
class WorkshopView:
    """View of a creative workshop."""

    id: str
    name: str
    description: str | None
    theme: str | None
    is_active: bool
    artisan_count: int
    contribution_count: int
    started_at: str | None
    created_at: str


@dataclass
class ArtisanView:
    """View of an artisan."""

    id: str
    workshop_id: str
    name: str
    specialty: str
    style: str | None
    is_active: bool
    contribution_count: int
    created_at: str


@dataclass
class ContributionView:
    """View of an artifact contribution."""

    id: str
    artisan_id: str
    artisan_name: str
    contribution_type: str
    content_type: str
    content: str
    prompt: str | None
    inspiration: str | None
    created_at: str


@dataclass
class ExhibitionView:
    """View of an exhibition."""

    id: str
    workshop_id: str
    name: str
    description: str | None
    curator_notes: str | None
    is_open: bool
    view_count: int
    item_count: int
    opened_at: str | None
    created_at: str


@dataclass
class GalleryItemView:
    """View of a gallery item."""

    id: str
    exhibition_id: str
    artifact_type: str
    artifact_content: str
    title: str | None
    description: str | None
    display_order: int
    artisan_ids: list[str]


@dataclass
class AtelierStatus:
    """Atelier health status."""

    total_workshops: int
    active_workshops: int
    total_artisans: int
    total_contributions: int
    total_exhibitions: int
    open_exhibitions: int
    storage_backend: str


class AtelierPersistence:
    """
    Persistence layer for Atelier Crown Jewel.

    Composes:
    - TableAdapter[Workshop]: Workshop state and configuration
    - TableAdapter[Artisan]: Artisan membership and activity
    - D-gent: Creative content, semantic connections

    Domain Semantics:
    - Workshops are collaborative creative spaces
    - Artisans are agents with specialties
    - Contributions are the creative artifacts
    - Exhibitions curate and showcase work

    Fishbowl Pattern:
    - Process is visible (spectators can watch)
    - Collaboration is tracked
    - Works can be exhibited

    Example:
        persistence = AtelierPersistence(
            workshop_adapter=TableAdapter(Workshop, session_factory),
            artisan_adapter=TableAdapter(Artisan, session_factory),
            dgent=dgent_router,
        )

        workshop = await persistence.create_workshop("Poetry Circle", theme="nature")
        artisan = await persistence.add_artisan(workshop.id, "Blake", "poet")
    """

    def __init__(
        self,
        workshop_adapter: TableAdapter[Workshop],
        artisan_adapter: TableAdapter[Artisan],
        dgent: DgentProtocol,
    ) -> None:
        self.workshops = workshop_adapter
        self.artisans = artisan_adapter
        self.dgent = dgent

    # =========================================================================
    # Workshop Management
    # =========================================================================

    async def create_workshop(
        self,
        name: str,
        description: str | None = None,
        theme: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> WorkshopView:
        """
        Create a new creative workshop.

        AGENTESE: world.atelier.workshop.create

        Args:
            name: Workshop name
            description: Optional description
            theme: Creative theme
            config: Additional configuration

        Returns:
            WorkshopView of the created workshop
        """
        workshop_id = f"workshop-{uuid.uuid4().hex[:12]}"

        async with self.workshops.session_factory() as session:
            workshop = Workshop(
                id=workshop_id,
                name=name,
                description=description,
                theme=theme,
                is_active=True,
                started_at=datetime.utcnow(),
                ended_at=None,
                config=config or {},
            )
            session.add(workshop)
            await session.commit()

            return WorkshopView(
                id=workshop_id,
                name=name,
                description=description,
                theme=theme,
                is_active=True,
                artisan_count=0,
                contribution_count=0,
                started_at=workshop.started_at.isoformat() if workshop.started_at else None,
                created_at=workshop.created_at.isoformat() if workshop.created_at else "",
            )

    async def get_workshop(self, workshop_id: str) -> WorkshopView | None:
        """Get a workshop by ID."""
        async with self.workshops.session_factory() as session:
            workshop = await session.get(Workshop, workshop_id)
            if workshop is None:
                return None

            # Count artisans
            artisan_count = await session.execute(
                select(func.count())
                .select_from(Artisan)
                .where(Artisan.workshop_id == workshop_id)
            )

            # Count contributions
            contrib_count = await session.execute(
                select(func.count())
                .select_from(ArtifactContribution)
                .join(Artisan)
                .where(Artisan.workshop_id == workshop_id)
            )

            return WorkshopView(
                id=workshop.id,
                name=workshop.name,
                description=workshop.description,
                theme=workshop.theme,
                is_active=workshop.is_active,
                artisan_count=artisan_count.scalar() or 0,
                contribution_count=contrib_count.scalar() or 0,
                started_at=workshop.started_at.isoformat() if workshop.started_at else None,
                created_at=workshop.created_at.isoformat() if workshop.created_at else "",
            )

    async def list_workshops(
        self,
        active_only: bool = False,
        theme: str | None = None,
        limit: int = 20,
    ) -> list[WorkshopView]:
        """List workshops with optional filters."""
        async with self.workshops.session_factory() as session:
            stmt = select(Workshop)

            if active_only:
                stmt = stmt.where(Workshop.is_active == True)
            if theme:
                stmt = stmt.where(Workshop.theme == theme)

            stmt = stmt.order_by(Workshop.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            workshops = result.scalars().all()

            views = []
            for w in workshops:
                # Count artisans for each
                artisan_count = await session.execute(
                    select(func.count())
                    .select_from(Artisan)
                    .where(Artisan.workshop_id == w.id)
                )
                views.append(
                    WorkshopView(
                        id=w.id,
                        name=w.name,
                        description=w.description,
                        theme=w.theme,
                        is_active=w.is_active,
                        artisan_count=artisan_count.scalar() or 0,
                        contribution_count=0,  # Simplified for list
                        started_at=w.started_at.isoformat() if w.started_at else None,
                        created_at=w.created_at.isoformat() if w.created_at else "",
                    )
                )

            return views

    async def end_workshop(self, workshop_id: str) -> bool:
        """End an active workshop."""
        async with self.workshops.session_factory() as session:
            workshop = await session.get(Workshop, workshop_id)
            if workshop is None:
                return False

            workshop.is_active = False
            workshop.ended_at = datetime.utcnow()
            await session.commit()
            return True

    # =========================================================================
    # Artisan Management
    # =========================================================================

    async def add_artisan(
        self,
        workshop_id: str,
        name: str,
        specialty: str,
        style: str | None = None,
        agent_id: str | None = None,
    ) -> ArtisanView | None:
        """
        Add an artisan to a workshop.

        AGENTESE: world.atelier.workshop.join

        Args:
            workshop_id: Workshop to join
            name: Artisan name
            specialty: Creative specialty ("poet", "painter", "composer", etc.)
            style: Optional creative style
            agent_id: Link to Town citizen or external agent

        Returns:
            ArtisanView or None if workshop not found
        """
        async with self.artisans.session_factory() as session:
            workshop = await session.get(Workshop, workshop_id)
            if workshop is None or not workshop.is_active:
                return None

            artisan_id = f"artisan-{uuid.uuid4().hex[:12]}"

            artisan = Artisan(
                id=artisan_id,
                workshop_id=workshop_id,
                name=name,
                specialty=specialty,
                style=style,
                is_active=True,
                contribution_count=0,
                agent_id=agent_id,
            )
            session.add(artisan)
            await session.commit()

            return ArtisanView(
                id=artisan_id,
                workshop_id=workshop_id,
                name=name,
                specialty=specialty,
                style=style,
                is_active=True,
                contribution_count=0,
                created_at=artisan.created_at.isoformat() if artisan.created_at else "",
            )

    async def get_artisan(self, artisan_id: str) -> ArtisanView | None:
        """Get an artisan by ID."""
        async with self.artisans.session_factory() as session:
            artisan = await session.get(Artisan, artisan_id)
            if artisan is None:
                return None

            return self._artisan_to_view(artisan)

    async def list_artisans(
        self,
        workshop_id: str,
        specialty: str | None = None,
        active_only: bool = True,
    ) -> list[ArtisanView]:
        """List artisans in a workshop."""
        async with self.artisans.session_factory() as session:
            stmt = select(Artisan).where(Artisan.workshop_id == workshop_id)

            if specialty:
                stmt = stmt.where(Artisan.specialty == specialty)
            if active_only:
                stmt = stmt.where(Artisan.is_active == True)

            stmt = stmt.order_by(Artisan.created_at)
            result = await session.execute(stmt)
            artisans = result.scalars().all()

            return [self._artisan_to_view(a) for a in artisans]

    # =========================================================================
    # Contribution Management
    # =========================================================================

    async def contribute(
        self,
        artisan_id: str,
        content: str,
        content_type: str = "text",
        contribution_type: str = "draft",
        prompt: str | None = None,
        inspiration: str | None = None,
        notes: str | None = None,
    ) -> ContributionView | None:
        """
        Submit a creative contribution.

        AGENTESE: world.atelier.artifact.contribute

        Stores both queryable metadata and semantic content.

        Args:
            artisan_id: Contributing artisan
            content: Creative content
            content_type: Type ("text", "image", "audio", "code")
            contribution_type: Stage ("draft", "revision", "final")
            prompt: Original creative prompt
            inspiration: What inspired the work
            notes: Additional notes

        Returns:
            ContributionView or None if artisan not found
        """
        async with self.artisans.session_factory() as session:
            artisan = await session.get(Artisan, artisan_id)
            if artisan is None or not artisan.is_active:
                return None

            contribution_id = f"contrib-{uuid.uuid4().hex[:12]}"

            # Store semantic content in D-gent
            datum = Datum(
                id=f"atelier-{contribution_id}",
                content=content.encode("utf-8"),
                created_at=time.time(),
                causal_parent=None,
                metadata={
                    "type": "atelier_contribution",
                    "artisan_id": artisan_id,
                    "content_type": content_type,
                    "contribution_type": contribution_type,
                },
            )
            datum_id = await self.dgent.put(datum)

            # Create contribution record
            contribution = ArtifactContribution(
                id=contribution_id,
                artisan_id=artisan_id,
                contribution_type=contribution_type,
                content_type=content_type,
                content=content,
                prompt=prompt,
                inspiration=inspiration,
                notes=notes,
                datum_id=datum_id,
            )
            session.add(contribution)

            # Update artisan contribution count
            artisan.contribution_count += 1

            await session.commit()

            return ContributionView(
                id=contribution_id,
                artisan_id=artisan_id,
                artisan_name=artisan.name,
                contribution_type=contribution_type,
                content_type=content_type,
                content=content,
                prompt=prompt,
                inspiration=inspiration,
                created_at=contribution.created_at.isoformat()
                if contribution.created_at
                else "",
            )

    async def list_contributions(
        self,
        artisan_id: str | None = None,
        workshop_id: str | None = None,
        contribution_type: str | None = None,
        limit: int = 50,
    ) -> list[ContributionView]:
        """List contributions with optional filters."""
        async with self.artisans.session_factory() as session:
            stmt = select(ArtifactContribution, Artisan.name).join(Artisan)

            if artisan_id:
                stmt = stmt.where(ArtifactContribution.artisan_id == artisan_id)
            if workshop_id:
                stmt = stmt.where(Artisan.workshop_id == workshop_id)
            if contribution_type:
                stmt = stmt.where(
                    ArtifactContribution.contribution_type == contribution_type
                )

            stmt = stmt.order_by(ArtifactContribution.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            rows = result.all()

            return [
                ContributionView(
                    id=c.id,
                    artisan_id=c.artisan_id,
                    artisan_name=name,
                    contribution_type=c.contribution_type,
                    content_type=c.content_type,
                    content=c.content,
                    prompt=c.prompt,
                    inspiration=c.inspiration,
                    created_at=c.created_at.isoformat() if c.created_at else "",
                )
                for c, name in rows
            ]

    # =========================================================================
    # Exhibition Management
    # =========================================================================

    async def create_exhibition(
        self,
        workshop_id: str,
        name: str,
        description: str | None = None,
        curator_notes: str | None = None,
    ) -> ExhibitionView | None:
        """
        Create an exhibition for a workshop.

        AGENTESE: world.atelier.exhibition.create

        Args:
            workshop_id: Source workshop
            name: Exhibition name
            description: Description for visitors
            curator_notes: Curatorial context

        Returns:
            ExhibitionView or None if workshop not found
        """
        async with self.workshops.session_factory() as session:
            workshop = await session.get(Workshop, workshop_id)
            if workshop is None:
                return None

            exhibition_id = f"exhibit-{uuid.uuid4().hex[:12]}"

            exhibition = Exhibition(
                id=exhibition_id,
                workshop_id=workshop_id,
                name=name,
                description=description,
                curator_notes=curator_notes,
                is_open=False,
                opened_at=None,
                closed_at=None,
                view_count=0,
            )
            session.add(exhibition)
            await session.commit()

            return ExhibitionView(
                id=exhibition_id,
                workshop_id=workshop_id,
                name=name,
                description=description,
                curator_notes=curator_notes,
                is_open=False,
                view_count=0,
                item_count=0,
                opened_at=None,
                created_at=exhibition.created_at.isoformat()
                if exhibition.created_at
                else "",
            )

    async def open_exhibition(self, exhibition_id: str) -> bool:
        """
        Open an exhibition for viewing.

        AGENTESE: world.atelier.exhibition.open
        """
        async with self.workshops.session_factory() as session:
            exhibition = await session.get(Exhibition, exhibition_id)
            if exhibition is None or exhibition.is_open:
                return False

            exhibition.is_open = True
            exhibition.opened_at = datetime.utcnow()
            await session.commit()
            return True

    async def add_to_gallery(
        self,
        exhibition_id: str,
        artifact_content: str,
        artifact_type: str = "text",
        title: str | None = None,
        description: str | None = None,
        artisan_ids: list[str] | None = None,
    ) -> GalleryItemView | None:
        """
        Add an item to an exhibition gallery.

        AGENTESE: world.atelier.gallery.add

        Args:
            exhibition_id: Target exhibition
            artifact_content: The creative content
            artifact_type: Type of artifact
            title: Display title
            description: Item description
            artisan_ids: Contributing artisans

        Returns:
            GalleryItemView or None
        """
        async with self.workshops.session_factory() as session:
            exhibition = await session.get(Exhibition, exhibition_id)
            if exhibition is None:
                return None

            item_id = f"gallery-{uuid.uuid4().hex[:12]}"

            # Determine display order
            count_result = await session.execute(
                select(func.count())
                .select_from(GalleryItem)
                .where(GalleryItem.exhibition_id == exhibition_id)
            )
            display_order = (count_result.scalar() or 0) + 1

            item = GalleryItem(
                id=item_id,
                exhibition_id=exhibition_id,
                artifact_type=artifact_type,
                artifact_content=artifact_content,
                artifact_metadata={},
                display_order=display_order,
                title=title,
                description=description,
                artisan_ids=artisan_ids or [],
            )
            session.add(item)
            await session.commit()

            return GalleryItemView(
                id=item_id,
                exhibition_id=exhibition_id,
                artifact_type=artifact_type,
                artifact_content=artifact_content,
                title=title,
                description=description,
                display_order=display_order,
                artisan_ids=artisan_ids or [],
            )

    async def view_exhibition(self, exhibition_id: str) -> ExhibitionView | None:
        """
        View an exhibition (increments view count).

        AGENTESE: world.atelier.gallery.view
        """
        async with self.workshops.session_factory() as session:
            exhibition = await session.get(Exhibition, exhibition_id)
            if exhibition is None:
                return None

            # Increment view count
            exhibition.view_count += 1

            # Count items
            item_count_result = await session.execute(
                select(func.count())
                .select_from(GalleryItem)
                .where(GalleryItem.exhibition_id == exhibition_id)
            )

            await session.commit()

            return ExhibitionView(
                id=exhibition.id,
                workshop_id=exhibition.workshop_id,
                name=exhibition.name,
                description=exhibition.description,
                curator_notes=exhibition.curator_notes,
                is_open=exhibition.is_open,
                view_count=exhibition.view_count,
                item_count=item_count_result.scalar() or 0,
                opened_at=exhibition.opened_at.isoformat()
                if exhibition.opened_at
                else None,
                created_at=exhibition.created_at.isoformat()
                if exhibition.created_at
                else "",
            )

    async def list_gallery_items(
        self,
        exhibition_id: str,
    ) -> list[GalleryItemView]:
        """List items in an exhibition gallery."""
        async with self.workshops.session_factory() as session:
            stmt = (
                select(GalleryItem)
                .where(GalleryItem.exhibition_id == exhibition_id)
                .order_by(GalleryItem.display_order)
            )
            result = await session.execute(stmt)
            items = result.scalars().all()

            return [
                GalleryItemView(
                    id=i.id,
                    exhibition_id=i.exhibition_id,
                    artifact_type=i.artifact_type,
                    artifact_content=i.artifact_content,
                    title=i.title,
                    description=i.description,
                    display_order=i.display_order,
                    artisan_ids=i.artisan_ids or [],
                )
                for i in items
            ]

    # =========================================================================
    # Health Status
    # =========================================================================

    async def manifest(self) -> AtelierStatus:
        """
        Get atelier health status.

        AGENTESE: world.atelier.manifest
        """
        async with self.workshops.session_factory() as session:
            # Count workshops
            total_workshops_result = await session.execute(
                select(func.count()).select_from(Workshop)
            )
            total_workshops = total_workshops_result.scalar() or 0

            active_workshops_result = await session.execute(
                select(func.count())
                .select_from(Workshop)
                .where(Workshop.is_active == True)
            )
            active_workshops = active_workshops_result.scalar() or 0

            # Count artisans
            total_artisans_result = await session.execute(
                select(func.count()).select_from(Artisan)
            )
            total_artisans = total_artisans_result.scalar() or 0

            # Count contributions
            total_contributions_result = await session.execute(
                select(func.count()).select_from(ArtifactContribution)
            )
            total_contributions = total_contributions_result.scalar() or 0

            # Count exhibitions
            total_exhibitions_result = await session.execute(
                select(func.count()).select_from(Exhibition)
            )
            total_exhibitions = total_exhibitions_result.scalar() or 0

            open_exhibitions_result = await session.execute(
                select(func.count())
                .select_from(Exhibition)
                .where(Exhibition.is_open == True)
            )
            open_exhibitions = open_exhibitions_result.scalar() or 0

        return AtelierStatus(
            total_workshops=total_workshops,
            active_workshops=active_workshops,
            total_artisans=total_artisans,
            total_contributions=total_contributions,
            total_exhibitions=total_exhibitions,
            open_exhibitions=open_exhibitions,
            storage_backend="postgres"
            if "postgres" in str(self.workshops.session_factory).lower()
            else "sqlite",
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _artisan_to_view(self, artisan: Artisan) -> ArtisanView:
        """Convert Artisan model to ArtisanView."""
        return ArtisanView(
            id=artisan.id,
            workshop_id=artisan.workshop_id,
            name=artisan.name,
            specialty=artisan.specialty,
            style=artisan.style,
            is_active=artisan.is_active,
            contribution_count=artisan.contribution_count,
            created_at=artisan.created_at.isoformat() if artisan.created_at else "",
        )


__all__ = [
    "AtelierPersistence",
    "WorkshopView",
    "ArtisanView",
    "ContributionView",
    "ExhibitionView",
    "GalleryItemView",
    "AtelierStatus",
]
