"""
Forge AGENTESE Node: @node("world.forge")

Wraps ForgePersistence as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- world.forge.manifest          - Forge health status
- world.forge.workshop.list     - List all workshops
- world.forge.workshop.get      - Get workshop by ID
- world.forge.workshop.create   - Create new workshop
- world.forge.workshop.end      - End a workshop
- world.forge.artisan.list      - List artisans in workshop
- world.forge.artisan.join      - Join a workshop
- world.forge.contribute        - Submit creative contribution
- world.forge.exhibition.create - Create exhibition from workshop
- world.forge.exhibition.open   - Open exhibition for viewing
- world.forge.gallery.list      - List gallery items
- world.forge.gallery.add       - Add item to exhibition
- world.forge.gallery.view      - View exhibition (increments view count)
- world.forge.tokens.manifest   - Token balance for spectator
- world.forge.bid.submit        - Submit a spectator bid
- world.forge.festival.list     - List festivals
- world.forge.festival.create   - Create festival
- world.forge.festival.enter    - Enter festival

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

from .contracts import (
    ArtisanJoinRequest,
    ArtisanJoinResponse,
    ArtisanListRequest,
    ArtisanListResponse,
    ForgeManifestResponse,
    BidSubmitRequest,
    BidSubmitResponse,
    ContributeRequest,
    ContributeResponse,
    ContributionListRequest,
    ContributionListResponse,
    ExhibitionCreateRequest,
    ExhibitionCreateResponse,
    ExhibitionOpenRequest,
    ExhibitionOpenResponse,
    ExhibitionViewRequest,
    ExhibitionViewResponse,
    FestivalCreateRequest,
    FestivalCreateResponse,
    FestivalEnterRequest,
    FestivalEnterResponse,
    FestivalListResponse,
    GalleryAddRequest,
    GalleryAddResponse,
    GalleryListRequest,
    GalleryListResponse,
    TokenManifestResponse,
    WorkshopCreateRequest,
    WorkshopCreateResponse,
    WorkshopEndRequest,
    WorkshopEndResponse,
    WorkshopGetRequest,
    WorkshopGetResponse,
    WorkshopListResponse,
)
from .persistence import (
    ArtisanView,
    ForgePersistence,
    ForgeStatus,
    ContributionView,
    ExhibitionView,
    GalleryItemView,
    WorkshopView,
)

if TYPE_CHECKING:
    from agents.forge.bidding import BidQueue, BidResult, BidType
    from agents.forge.economy import AsyncTokenPool
    from agents.forge.festival import Festival, FestivalManager


# === Rendering Types ===


@dataclass(frozen=True)
class ForgeManifestRendering:
    """Rendering for forge status manifest."""

    status: ForgeStatus

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "forge_manifest",
            "total_workshops": self.status.total_workshops,
            "active_workshops": self.status.active_workshops,
            "total_artisans": self.status.total_artisans,
            "total_contributions": self.status.total_contributions,
            "total_exhibitions": self.status.total_exhibitions,
            "open_exhibitions": self.status.open_exhibitions,
            "storage_backend": self.status.storage_backend,
        }

    def to_text(self) -> str:
        lines = [
            "Forge Status",
            "==============",
            f"Workshops: {self.status.active_workshops}/{self.status.total_workshops} active",
            f"Artisans: {self.status.total_artisans}",
            f"Contributions: {self.status.total_contributions}",
            f"Exhibitions: {self.status.open_exhibitions}/{self.status.total_exhibitions} open",
            f"Storage: {self.status.storage_backend}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class WorkshopRendering:
    """Rendering for workshop details."""

    workshop: WorkshopView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "workshop",
            "id": self.workshop.id,
            "name": self.workshop.name,
            "description": self.workshop.description,
            "theme": self.workshop.theme,
            "is_active": self.workshop.is_active,
            "artisan_count": self.workshop.artisan_count,
            "contribution_count": self.workshop.contribution_count,
            "started_at": self.workshop.started_at,
            "created_at": self.workshop.created_at,
        }

    def to_text(self) -> str:
        status = "active" if self.workshop.is_active else "ended"
        lines = [
            f"Workshop: {self.workshop.name} ({status})",
            f"ID: {self.workshop.id}",
        ]
        if self.workshop.theme:
            lines.append(f"Theme: {self.workshop.theme}")
        if self.workshop.description:
            lines.append(f"Description: {self.workshop.description}")
        lines.append(f"Artisans: {self.workshop.artisan_count}")
        lines.append(f"Contributions: {self.workshop.contribution_count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class WorkshopListRendering:
    """Rendering for list of workshops."""

    workshops: list[WorkshopView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "workshop_list",
            "count": len(self.workshops),
            "workshops": [WorkshopRendering(w).to_dict() for w in self.workshops],
        }

    def to_text(self) -> str:
        if not self.workshops:
            return "No workshops found."
        lines = [f"Workshops ({len(self.workshops)}):"]
        for w in self.workshops:
            status = "[active]" if w.is_active else "[ended]"
            lines.append(f"  {w.name} {status} - {w.artisan_count} artisans")
        return "\n".join(lines)


@dataclass(frozen=True)
class ArtisanRendering:
    """Rendering for artisan details."""

    artisan: ArtisanView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "artisan",
            "id": self.artisan.id,
            "workshop_id": self.artisan.workshop_id,
            "name": self.artisan.name,
            "specialty": self.artisan.specialty,
            "style": self.artisan.style,
            "is_active": self.artisan.is_active,
            "contribution_count": self.artisan.contribution_count,
            "created_at": self.artisan.created_at,
        }

    def to_text(self) -> str:
        status = "[active]" if self.artisan.is_active else "[inactive]"
        lines = [
            f"Artisan: {self.artisan.name} {status}",
            f"ID: {self.artisan.id}",
            f"Specialty: {self.artisan.specialty}",
        ]
        if self.artisan.style:
            lines.append(f"Style: {self.artisan.style}")
        lines.append(f"Contributions: {self.artisan.contribution_count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ArtisanListRendering:
    """Rendering for list of artisans."""

    artisans: list[ArtisanView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "artisan_list",
            "count": len(self.artisans),
            "artisans": [ArtisanRendering(a).to_dict() for a in self.artisans],
        }

    def to_text(self) -> str:
        if not self.artisans:
            return "No artisans found."
        lines = [f"Artisans ({len(self.artisans)}):"]
        for a in self.artisans:
            status = "[active]" if a.is_active else "[inactive]"
            lines.append(f"  {a.name} ({a.specialty}) {status}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ContributionRendering:
    """Rendering for contribution details."""

    contribution: ContributionView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "contribution",
            "id": self.contribution.id,
            "artisan_id": self.contribution.artisan_id,
            "artisan_name": self.contribution.artisan_name,
            "contribution_type": self.contribution.contribution_type,
            "content_type": self.contribution.content_type,
            "content": self.contribution.content[:200]
            + ("..." if len(self.contribution.content) > 200 else ""),
            "prompt": self.contribution.prompt,
            "inspiration": self.contribution.inspiration,
            "created_at": self.contribution.created_at,
        }

    def to_text(self) -> str:
        lines = [
            f"Contribution by {self.contribution.artisan_name}",
            f"Type: {self.contribution.contribution_type} ({self.contribution.content_type})",
        ]
        if self.contribution.prompt:
            lines.append(f"Prompt: {self.contribution.prompt}")
        content_preview = self.contribution.content[:100]
        if len(self.contribution.content) > 100:
            content_preview += "..."
        lines.append(f"Content: {content_preview}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ContributionListRendering:
    """Rendering for list of contributions."""

    contributions: list[ContributionView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "contribution_list",
            "count": len(self.contributions),
            "contributions": [
                ContributionRendering(c).to_dict() for c in self.contributions
            ],
        }

    def to_text(self) -> str:
        if not self.contributions:
            return "No contributions found."
        lines = [f"Contributions ({len(self.contributions)}):"]
        for c in self.contributions:
            lines.append(f"  - {c.artisan_name}: {c.contribution_type}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ExhibitionRendering:
    """Rendering for exhibition details."""

    exhibition: ExhibitionView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "exhibition",
            "id": self.exhibition.id,
            "workshop_id": self.exhibition.workshop_id,
            "name": self.exhibition.name,
            "description": self.exhibition.description,
            "curator_notes": self.exhibition.curator_notes,
            "is_open": self.exhibition.is_open,
            "view_count": self.exhibition.view_count,
            "item_count": self.exhibition.item_count,
            "opened_at": self.exhibition.opened_at,
            "created_at": self.exhibition.created_at,
        }

    def to_text(self) -> str:
        status = "[open]" if self.exhibition.is_open else "[closed]"
        lines = [
            f"Exhibition: {self.exhibition.name} {status}",
            f"ID: {self.exhibition.id}",
        ]
        if self.exhibition.description:
            lines.append(f"Description: {self.exhibition.description}")
        lines.append(f"Items: {self.exhibition.item_count}")
        lines.append(f"Views: {self.exhibition.view_count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class GalleryItemRendering:
    """Rendering for gallery item details."""

    item: GalleryItemView

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "gallery_item",
            "id": self.item.id,
            "exhibition_id": self.item.exhibition_id,
            "artifact_type": self.item.artifact_type,
            "artifact_content": self.item.artifact_content[:200]
            + ("..." if len(self.item.artifact_content) > 200 else ""),
            "title": self.item.title,
            "description": self.item.description,
            "display_order": self.item.display_order,
            "artisan_ids": self.item.artisan_ids,
        }

    def to_text(self) -> str:
        title = self.item.title or f"Item #{self.item.display_order}"
        lines = [f"Gallery Item: {title}", f"Type: {self.item.artifact_type}"]
        if self.item.description:
            lines.append(f"Description: {self.item.description}")
        content_preview = self.item.artifact_content[:80]
        if len(self.item.artifact_content) > 80:
            content_preview += "..."
        lines.append(f"Content: {content_preview}")
        return "\n".join(lines)


@dataclass(frozen=True)
class GalleryListRendering:
    """Rendering for list of gallery items."""

    items: list[GalleryItemView]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "gallery_list",
            "count": len(self.items),
            "items": [GalleryItemRendering(i).to_dict() for i in self.items],
        }

    def to_text(self) -> str:
        if not self.items:
            return "No items in gallery."
        lines = [f"Gallery ({len(self.items)} items):"]
        for item in self.items:
            title = item.title or f"Item #{item.display_order}"
            lines.append(f"  {item.display_order}. {title} ({item.artifact_type})")
        return "\n".join(lines)


# === ForgeNode ===


@node(
    "world.forge",
    description="Creative workshop fishbowl",
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(ForgeManifestResponse),
        "workshop.list": Response(WorkshopListResponse),
        "contribution.list": Response(ContributionListResponse),
        "festival.list": Response(FestivalListResponse),
        # Mutation aspects (Contract with request + response)
        "workshop.get": Contract(WorkshopGetRequest, WorkshopGetResponse),
        "workshop.create": Contract(WorkshopCreateRequest, WorkshopCreateResponse),
        "workshop.end": Contract(WorkshopEndRequest, WorkshopEndResponse),
        "artisan.list": Contract(ArtisanListRequest, ArtisanListResponse),
        "artisan.join": Contract(ArtisanJoinRequest, ArtisanJoinResponse),
        "contribute": Contract(ContributeRequest, ContributeResponse),
        "exhibition.create": Contract(
            ExhibitionCreateRequest, ExhibitionCreateResponse
        ),
        "exhibition.open": Contract(ExhibitionOpenRequest, ExhibitionOpenResponse),
        "exhibition.view": Contract(ExhibitionViewRequest, ExhibitionViewResponse),
        "gallery.list": Contract(GalleryListRequest, GalleryListResponse),
        "gallery.add": Contract(GalleryAddRequest, GalleryAddResponse),
        "tokens.manifest": Response(TokenManifestResponse),
        "bid.submit": Contract(BidSubmitRequest, BidSubmitResponse),
        "festival.create": Contract(FestivalCreateRequest, FestivalCreateResponse),
        "festival.enter": Contract(FestivalEnterRequest, FestivalEnterResponse),
    },
)
class ForgeNode(BaseLogosNode):
    """
    AGENTESE node for Forge Crown Jewel.

    Wraps ForgePersistence, TokenPool, BidQueue, and FestivalManager
    for universal gateway access.

    DI Requirements:
    - forge_persistence: ForgePersistence (required)
    - token_pool: AsyncTokenPool (optional, for spectator economy)
    - bid_queue: BidQueue (optional, for constraint injection)
    - festival_manager: FestivalManager (optional, for seasonal events)
    """

    def __init__(
        self,
        forge_persistence: ForgePersistence,
        token_pool: "AsyncTokenPool | None" = None,
        festival_manager: "FestivalManager | None" = None,
    ) -> None:
        """
        Initialize ForgeNode with dependencies.

        Args:
            forge_persistence: ForgePersistence for workshop/exhibition data
            token_pool: Optional AsyncTokenPool for spectator economy
            festival_manager: Optional FestivalManager for seasonal events
        """
        self.persistence = forge_persistence
        self.token_pool = token_pool
        self.festival_manager = festival_manager

    # === Handle & Affordances ===

    @property
    def handle(self) -> str:
        """The AGENTESE path for this node."""
        return "world.forge"

    async def get_handle_info(self, observer: Observer) -> dict[str, Any]:
        """Return handle description for world.forge."""
        meta = self._umwelt_to_meta(observer)
        return {
            "path": "world.forge",
            "description": "Creative workshop fishbowl for collaborative creation",
            "observer": {
                "archetype": observer.archetype,
            },
            "affordances": self.affordances(meta),
            "features": {
                "workshops": True,
                "exhibitions": True,
                "spectator_economy": self.token_pool is not None,
                "festivals": self.festival_manager is not None,
            },
        }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return available affordances based on observer archetype.

        Affordances vary by archetype:
        - spectator: Read-only + bidding (if token_pool)
        - artisan: Create contributions, view works
        - curator: Manage exhibitions
        - developer: Full access
        """
        archetype_lower = archetype.lower() if archetype else "spectator"

        # Core operations available to all archetypes
        base = (
            "workshop.list",
            "workshop.get",
            "artisan.list",
            "contribution.list",
            "exhibition.view",
            "gallery.list",
        )

        if archetype_lower == "spectator":
            extra = ()
            if self.token_pool:
                extra += ("tokens.manifest", "bid.submit")
            if self.festival_manager:
                extra += ("festival.list",)
            return base + extra

        elif archetype_lower == "artisan":
            extra = ("workshop.join", "contribute")
            if self.festival_manager:
                extra += ("festival.list", "festival.enter")
            return base + extra

        elif archetype_lower == "curator":
            extra = (
                "workshop.create",
                "workshop.end",
                "workshop.join",
                "contribute",
                "exhibition.create",
                "exhibition.open",
                "gallery.add",
            )
            if self.festival_manager:
                extra += ("festival.list", "festival.create", "festival.enter")
            return base + extra

        elif archetype_lower in ("developer", "admin", "system"):
            full_access = (
                "workshop.list",
                "workshop.get",
                "workshop.create",
                "workshop.end",
                "artisan.list",
                "artisan.join",
                "contribute",
                "contribution.list",
                "exhibition.create",
                "exhibition.open",
                "exhibition.view",
                "gallery.list",
                "gallery.add",
            )
            if self.token_pool:
                full_access += ("tokens.manifest", "bid.submit")
            if self.festival_manager:
                full_access += (
                    "festival.list",
                    "festival.create",
                    "festival.enter",
                    "festival.vote",
                )
            return full_access

        # Default: read-only
        return base

    async def manifest(self, observer: Observer) -> Renderable:
        """
        AGENTESE: world.forge.manifest

        Returns forge health status.
        """
        status = await self.persistence.manifest()
        return ForgeManifestRendering(status)

    # === Workshop Operations ===

    async def _workshop_list(
        self,
        observer: Observer,
        active_only: bool = False,
        theme: str | None = None,
        limit: int = 20,
    ) -> Renderable:
        """
        AGENTESE: world.forge.workshop.list

        List workshops with optional filters.
        """
        workshops = await self.persistence.list_workshops(
            active_only=active_only,
            theme=theme,
            limit=limit,
        )
        return WorkshopListRendering(workshops)

    async def _workshop_get(
        self,
        observer: Observer,
        workshop_id: str,
    ) -> Renderable:
        """
        AGENTESE: world.forge.workshop.get

        Get workshop by ID.
        """
        workshop = await self.persistence.get_workshop(workshop_id)
        if workshop is None:
            return BasicRendering(
                f"Workshop not found: {workshop_id}",
                {"error": "not_found", "workshop_id": workshop_id},
            )
        return WorkshopRendering(workshop)

    async def _workshop_create(
        self,
        observer: Observer,
        name: str,
        description: str | None = None,
        theme: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.workshop.create

        Create a new workshop.
        """
        workshop = await self.persistence.create_workshop(
            name=name,
            description=description,
            theme=theme,
            config=config,
        )
        return WorkshopRendering(workshop)

    async def _workshop_end(
        self,
        observer: Observer,
        workshop_id: str,
    ) -> Renderable:
        """
        AGENTESE: world.forge.workshop.end

        End an active workshop.
        """
        success = await self.persistence.end_workshop(workshop_id)
        if not success:
            return BasicRendering(
                f"Could not end workshop: {workshop_id}",
                {"error": "end_failed", "workshop_id": workshop_id},
            )
        return BasicRendering(
            f"Workshop ended: {workshop_id}",
            {"success": True, "workshop_id": workshop_id},
        )

    # === Artisan Operations ===

    async def _artisan_list(
        self,
        observer: Observer,
        workshop_id: str,
        specialty: str | None = None,
        active_only: bool = True,
    ) -> Renderable:
        """
        AGENTESE: world.forge.artisan.list

        List artisans in a workshop.
        """
        artisans = await self.persistence.list_artisans(
            workshop_id=workshop_id,
            specialty=specialty,
            active_only=active_only,
        )
        return ArtisanListRendering(artisans)

    async def _artisan_join(
        self,
        observer: Observer,
        workshop_id: str,
        name: str,
        specialty: str,
        style: str | None = None,
        agent_id: str | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.artisan.join

        Join a workshop as an artisan.
        """
        artisan = await self.persistence.add_artisan(
            workshop_id=workshop_id,
            name=name,
            specialty=specialty,
            style=style,
            agent_id=agent_id,
        )
        if artisan is None:
            return BasicRendering(
                f"Could not join workshop: {workshop_id}",
                {"error": "join_failed", "workshop_id": workshop_id},
            )
        return ArtisanRendering(artisan)

    # === Contribution Operations ===

    async def _contribute(
        self,
        observer: Observer,
        artisan_id: str,
        content: str,
        content_type: str = "text",
        contribution_type: str = "draft",
        prompt: str | None = None,
        inspiration: str | None = None,
        notes: str | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.contribute

        Submit a creative contribution.
        """
        contribution = await self.persistence.contribute(
            artisan_id=artisan_id,
            content=content,
            content_type=content_type,
            contribution_type=contribution_type,
            prompt=prompt,
            inspiration=inspiration,
            notes=notes,
        )
        if contribution is None:
            return BasicRendering(
                f"Could not submit contribution for artisan: {artisan_id}",
                {"error": "contribution_failed", "artisan_id": artisan_id},
            )
        return ContributionRendering(contribution)

    async def _contribution_list(
        self,
        observer: Observer,
        artisan_id: str | None = None,
        workshop_id: str | None = None,
        contribution_type: str | None = None,
        limit: int = 50,
    ) -> Renderable:
        """
        AGENTESE: world.forge.contribution.list

        List contributions with optional filters.
        """
        contributions = await self.persistence.list_contributions(
            artisan_id=artisan_id,
            workshop_id=workshop_id,
            contribution_type=contribution_type,
            limit=limit,
        )
        return ContributionListRendering(contributions)

    # === Exhibition Operations ===

    async def _exhibition_create(
        self,
        observer: Observer,
        workshop_id: str,
        name: str,
        description: str | None = None,
        curator_notes: str | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.exhibition.create

        Create an exhibition from a workshop.
        """
        exhibition = await self.persistence.create_exhibition(
            workshop_id=workshop_id,
            name=name,
            description=description,
            curator_notes=curator_notes,
        )
        if exhibition is None:
            return BasicRendering(
                f"Could not create exhibition for workshop: {workshop_id}",
                {"error": "exhibition_failed", "workshop_id": workshop_id},
            )
        return ExhibitionRendering(exhibition)

    async def _exhibition_open(
        self,
        observer: Observer,
        exhibition_id: str,
    ) -> Renderable:
        """
        AGENTESE: world.forge.exhibition.open

        Open an exhibition for viewing.
        """
        success = await self.persistence.open_exhibition(exhibition_id)
        if not success:
            return BasicRendering(
                f"Could not open exhibition: {exhibition_id}",
                {"error": "open_failed", "exhibition_id": exhibition_id},
            )
        return BasicRendering(
            f"Exhibition opened: {exhibition_id}",
            {"success": True, "exhibition_id": exhibition_id},
        )

    async def _exhibition_view(
        self,
        observer: Observer,
        exhibition_id: str,
    ) -> Renderable:
        """
        AGENTESE: world.forge.gallery.view

        View an exhibition (increments view count).
        """
        exhibition = await self.persistence.view_exhibition(exhibition_id)
        if exhibition is None:
            return BasicRendering(
                f"Exhibition not found: {exhibition_id}",
                {"error": "not_found", "exhibition_id": exhibition_id},
            )
        return ExhibitionRendering(exhibition)

    # === Gallery Operations ===

    async def _gallery_list(
        self,
        observer: Observer,
        exhibition_id: str,
    ) -> Renderable:
        """
        AGENTESE: world.forge.gallery.list

        List items in an exhibition gallery.
        """
        items = await self.persistence.list_gallery_items(exhibition_id)
        return GalleryListRendering(items)

    async def _gallery_add(
        self,
        observer: Observer,
        exhibition_id: str,
        artifact_content: str,
        artifact_type: str = "text",
        title: str | None = None,
        description: str | None = None,
        artisan_ids: list[str] | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.gallery.add

        Add an item to an exhibition gallery.
        """
        item = await self.persistence.add_to_gallery(
            exhibition_id=exhibition_id,
            artifact_content=artifact_content,
            artifact_type=artifact_type,
            title=title,
            description=description,
            artisan_ids=artisan_ids,
        )
        if item is None:
            return BasicRendering(
                f"Could not add item to exhibition: {exhibition_id}",
                {"error": "add_failed", "exhibition_id": exhibition_id},
            )
        return GalleryItemRendering(item)

    # === Spectator Economy (Optional) ===

    async def _tokens_manifest(
        self,
        observer: Observer,
    ) -> Renderable:
        """
        AGENTESE: world.forge.tokens.manifest

        Get token balance for spectator.
        """
        if self.token_pool is None:
            return BasicRendering(
                "Spectator economy not enabled",
                {"error": "not_enabled", "feature": "token_pool"},
            )

        user_id = getattr(observer, "identity", None) or "anonymous"
        balance = await self.token_pool.get_balance(user_id)
        manifest_data = await self.token_pool.manifest(user_id)

        return BasicRendering(
            f"Token balance for {user_id}: {balance.whole_tokens}",
            manifest_data,
        )

    async def _bid_submit(
        self,
        observer: Observer,
        session_id: str,
        bid_type: str,
        content: str,
    ) -> Renderable:
        """
        AGENTESE: world.forge.bid.submit

        Submit a spectator bid for constraint injection.
        """
        if self.token_pool is None:
            return BasicRendering(
                "Spectator economy not enabled",
                {"error": "not_enabled", "feature": "token_pool"},
            )

        from agents.forge.bidding import BidType as BT

        user_id = getattr(observer, "identity", None) or "anonymous"

        # Parse bid type
        try:
            bt = BT[bid_type.upper()]
        except KeyError:
            return BasicRendering(
                f"Invalid bid type: {bid_type}",
                {"error": "invalid_bid_type", "bid_type": bid_type},
            )

        # Process bid through token pool
        spend_result, bid = self.token_pool._pool.process_bid(
            user_id=user_id,
            bid_type=bt,
            session_id=session_id,
            content=content,
        )

        if not spend_result.success:
            return BasicRendering(
                f"Bid failed: {spend_result.reason}",
                {
                    "error": "bid_failed",
                    "reason": spend_result.reason,
                    "balance": str(spend_result.new_balance),
                },
            )

        return BasicRendering(
            f"Bid submitted: {bid.id}",
            {
                "success": True,
                "bid_id": bid.id if bid else None,
                "new_balance": str(spend_result.new_balance),
            },
        )

    # === Festival Operations (Optional) ===

    async def _festival_list(
        self,
        observer: Observer,
        status: str | None = None,
        season: str | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.festival.list

        List festivals with optional filters.
        """
        if self.festival_manager is None:
            return BasicRendering(
                "Festivals not enabled",
                {"error": "not_enabled", "feature": "festivals"},
            )

        from agents.forge.festival import FestivalStatus, Season

        # Parse filters
        status_filter = FestivalStatus(status) if status else None
        season_filter = Season(season) if season else None

        festivals = self.festival_manager.list_festivals(
            status=status_filter,
            season=season_filter,
        )

        return BasicRendering(
            f"Found {len(festivals)} festivals",
            {
                "count": len(festivals),
                "festivals": [f.to_dict() for f in festivals],
            },
        )

    async def _festival_create(
        self,
        observer: Observer,
        title: str,
        theme: str,
        description: str | None = None,
        duration_hours: int = 72,
        voting_hours: int = 24,
    ) -> Renderable:
        """
        AGENTESE: world.forge.festival.create

        Create a new festival.
        """
        if self.festival_manager is None:
            return BasicRendering(
                "Festivals not enabled",
                {"error": "not_enabled", "feature": "festivals"},
            )

        festival = self.festival_manager.create(
            title=title,
            theme=theme,
            description=description,
            duration_hours=duration_hours,
            voting_hours=voting_hours,
        )

        return BasicRendering(
            f"Festival created: {festival.id}",
            festival.to_dict(),
        )

    async def _festival_enter(
        self,
        observer: Observer,
        festival_id: str,
        artisan: str,
        prompt: str,
        content: str,
        piece_id: str | None = None,
    ) -> Renderable:
        """
        AGENTESE: world.forge.festival.enter

        Enter a festival with a submission.
        """
        if self.festival_manager is None:
            return BasicRendering(
                "Festivals not enabled",
                {"error": "not_enabled", "feature": "festivals"},
            )

        entry = self.festival_manager.enter(
            festival_id=festival_id,
            artisan=artisan,
            prompt=prompt,
            content=content,
            piece_id=piece_id,
        )

        if entry is None:
            return BasicRendering(
                f"Could not enter festival: {festival_id}",
                {"error": "entry_failed", "festival_id": festival_id},
            )

        return BasicRendering(
            f"Entry submitted: {entry.id}",
            entry.to_dict(),
        )

    # === Aspect Routing ===

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to appropriate handlers.

        Args:
            aspect: The aspect to invoke (e.g., "workshop.list", "contribute")
            observer: The observer context
            **kwargs: Aspect-specific arguments

        Returns:
            Renderable result or dict
        """
        # === Workshop Operations ===
        if aspect == "workshop.list":
            return await self._workshop_list(
                observer,
                active_only=kwargs.get("active_only", False),
                theme=kwargs.get("theme"),
                limit=kwargs.get("limit", 20),
            )

        if aspect == "workshop.get":
            workshop_id = kwargs.get("workshop_id")
            if not workshop_id:
                return BasicRendering(
                    "workshop_id is required",
                    {"error": "missing_param", "param": "workshop_id"},
                )
            return await self._workshop_get(observer, workshop_id)

        if aspect == "workshop.create":
            name = kwargs.get("name")
            if not name:
                return BasicRendering(
                    "name is required",
                    {"error": "missing_param", "param": "name"},
                )
            return await self._workshop_create(
                observer,
                name=name,
                description=kwargs.get("description"),
                theme=kwargs.get("theme"),
                config=kwargs.get("config"),
            )

        if aspect == "workshop.end":
            workshop_id = kwargs.get("workshop_id")
            if not workshop_id:
                return BasicRendering(
                    "workshop_id is required",
                    {"error": "missing_param", "param": "workshop_id"},
                )
            return await self._workshop_end(observer, workshop_id)

        # === Artisan Operations ===
        if aspect == "artisan.list":
            workshop_id = kwargs.get("workshop_id")
            if not workshop_id:
                return BasicRendering(
                    "workshop_id is required",
                    {"error": "missing_param", "param": "workshop_id"},
                )
            return await self._artisan_list(
                observer,
                workshop_id=workshop_id,
                specialty=kwargs.get("specialty"),
                active_only=kwargs.get("active_only", True),
            )

        if aspect == "artisan.join" or aspect == "workshop.join":
            workshop_id = kwargs.get("workshop_id")
            name = kwargs.get("name")
            specialty = kwargs.get("specialty")
            if not workshop_id or not name or not specialty:
                return BasicRendering(
                    "workshop_id, name, and specialty are required",
                    {
                        "error": "missing_param",
                        "required": ["workshop_id", "name", "specialty"],
                    },
                )
            return await self._artisan_join(
                observer,
                workshop_id=workshop_id,
                name=name,
                specialty=specialty,
                style=kwargs.get("style"),
                agent_id=kwargs.get("agent_id"),
            )

        # === Contribution Operations ===
        if aspect == "contribute":
            artisan_id = kwargs.get("artisan_id")
            content = kwargs.get("content")
            if not artisan_id or not content:
                return BasicRendering(
                    "artisan_id and content are required",
                    {"error": "missing_param", "required": ["artisan_id", "content"]},
                )
            return await self._contribute(
                observer,
                artisan_id=artisan_id,
                content=content,
                content_type=kwargs.get("content_type", "text"),
                contribution_type=kwargs.get("contribution_type", "draft"),
                prompt=kwargs.get("prompt"),
                inspiration=kwargs.get("inspiration"),
                notes=kwargs.get("notes"),
            )

        if aspect == "contribution.list":
            return await self._contribution_list(
                observer,
                artisan_id=kwargs.get("artisan_id"),
                workshop_id=kwargs.get("workshop_id"),
                contribution_type=kwargs.get("contribution_type"),
                limit=kwargs.get("limit", 50),
            )

        # === Exhibition Operations ===
        if aspect == "exhibition.create":
            workshop_id = kwargs.get("workshop_id")
            name = kwargs.get("name")
            if not workshop_id or not name:
                return BasicRendering(
                    "workshop_id and name are required",
                    {"error": "missing_param", "required": ["workshop_id", "name"]},
                )
            return await self._exhibition_create(
                observer,
                workshop_id=workshop_id,
                name=name,
                description=kwargs.get("description"),
                curator_notes=kwargs.get("curator_notes"),
            )

        if aspect == "exhibition.open":
            exhibition_id = kwargs.get("exhibition_id")
            if not exhibition_id:
                return BasicRendering(
                    "exhibition_id is required",
                    {"error": "missing_param", "param": "exhibition_id"},
                )
            return await self._exhibition_open(observer, exhibition_id)

        if aspect == "exhibition.view":
            exhibition_id = kwargs.get("exhibition_id")
            if not exhibition_id:
                return BasicRendering(
                    "exhibition_id is required",
                    {"error": "missing_param", "param": "exhibition_id"},
                )
            return await self._exhibition_view(observer, exhibition_id)

        # === Gallery Operations ===
        if aspect == "gallery.list":
            exhibition_id = kwargs.get("exhibition_id")
            if not exhibition_id:
                return BasicRendering(
                    "exhibition_id is required",
                    {"error": "missing_param", "param": "exhibition_id"},
                )
            return await self._gallery_list(observer, exhibition_id)

        if aspect == "gallery.add":
            exhibition_id = kwargs.get("exhibition_id")
            artifact_content = kwargs.get("artifact_content")
            if not exhibition_id or not artifact_content:
                return BasicRendering(
                    "exhibition_id and artifact_content are required",
                    {
                        "error": "missing_param",
                        "required": ["exhibition_id", "artifact_content"],
                    },
                )
            return await self._gallery_add(
                observer,
                exhibition_id=exhibition_id,
                artifact_content=artifact_content,
                artifact_type=kwargs.get("artifact_type", "text"),
                title=kwargs.get("title"),
                description=kwargs.get("description"),
                artisan_ids=kwargs.get("artisan_ids"),
            )

        # === Token Operations (Optional) ===
        if aspect == "tokens.manifest":
            return await self._tokens_manifest(observer)

        if aspect == "bid.submit":
            session_id = kwargs.get("session_id")
            bid_type = kwargs.get("bid_type")
            content = kwargs.get("content")
            if not session_id or not bid_type or not content:
                return BasicRendering(
                    "session_id, bid_type, and content are required",
                    {
                        "error": "missing_param",
                        "required": ["session_id", "bid_type", "content"],
                    },
                )
            return await self._bid_submit(
                observer,
                session_id=session_id,
                bid_type=bid_type,
                content=content,
            )

        # === Festival Operations (Optional) ===
        if aspect == "festival.list":
            return await self._festival_list(
                observer,
                status=kwargs.get("status"),
                season=kwargs.get("season"),
            )

        if aspect == "festival.create":
            title = kwargs.get("title")
            theme = kwargs.get("theme")
            if not title or not theme:
                return BasicRendering(
                    "title and theme are required",
                    {"error": "missing_param", "required": ["title", "theme"]},
                )
            return await self._festival_create(
                observer,
                title=title,
                theme=theme,
                description=kwargs.get("description"),
                duration_hours=kwargs.get("duration_hours", 72),
                voting_hours=kwargs.get("voting_hours", 24),
            )

        if aspect == "festival.enter":
            festival_id = kwargs.get("festival_id")
            artisan = kwargs.get("artisan")
            prompt = kwargs.get("prompt")
            content = kwargs.get("content")
            if not festival_id or not artisan or not prompt or not content:
                return BasicRendering(
                    "festival_id, artisan, prompt, and content are required",
                    {
                        "error": "missing_param",
                        "required": ["festival_id", "artisan", "prompt", "content"],
                    },
                )
            return await self._festival_enter(
                observer,
                festival_id=festival_id,
                artisan=artisan,
                prompt=prompt,
                content=content,
                piece_id=kwargs.get("piece_id"),
            )

        # Unknown aspect
        return BasicRendering(
            f"Unknown aspect: {aspect}",
            {"error": "unknown_aspect", "aspect": aspect},
        )


__all__ = [
    "ForgeNode",
    "ForgeManifestRendering",
    "WorkshopRendering",
    "WorkshopListRendering",
    "ArtisanRendering",
    "ArtisanListRendering",
    "ContributionRendering",
    "ContributionListRendering",
    "ExhibitionRendering",
    "GalleryItemRendering",
    "GalleryListRendering",
]
