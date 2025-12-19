"""
AGENTESE Atelier Context: Creative Workshop Crown Jewel Integration.

The world.atelier context provides access to the Atelier creative workshop:
- world.atelier.manifest - Show workshop status
- world.atelier.workshop.create - Start a new workshop
- world.atelier.workshop.join - Add an artisan to workshop
- world.atelier.artifact.contribute - Submit creative work
- world.atelier.gallery - Browse completed works
- world.atelier.exhibition.open - Open gallery for viewing

This module defines AtelierNode which handles atelier-level operations.

AGENTESE: world.atelier.*

Principle Alignment:
- Joy-Inducing: Creative collaboration and artifact curation
- Composable: Workshops compose artisans, artisans compose contributions
- Ethical: Fishbowl transparency in creative process

Design DNA (from Crown Jewels):
- Fishbowl transparency: Process is visible
- Collaborative: Multiple participants can contribute
- Exhibition-ready: Works can be showcased
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from services.atelier import AtelierPersistence, AtelierStatus

    from bootstrap.umwelt import Umwelt


# Atelier affordances available at world.atelier.*
ATELIER_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "workshop_create",
    "workshop_join",
    "workshop_list",
    "workshop_end",
    "contribute",
    "contributions",
    "exhibition_create",
    "exhibition_open",
    "gallery_add",
    "gallery_view",
    "gallery_items",
)


# =============================================================================
# AtelierNode
# =============================================================================


@dataclass
class AtelierNode(BaseLogosNode):
    """
    world.atelier - Creative Workshop interface.

    The Atelier Crown Jewel provides:
    - Workshop management (create, join, end)
    - Artifact contribution tracking
    - Exhibition curation
    - Gallery viewing

    Storage:
    - services/atelier/persistence.py (AtelierPersistence)
    - Uses TableAdapter for structure, D-gent for creative content

    Fishbowl Pattern:
    - Process is visible (spectators can watch)
    - Collaboration is tracked
    - Works can be exhibited
    """

    _handle: str = "world.atelier"

    # Persistence layer (injected from service)
    _persistence: "AtelierPersistence | None" = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Atelier affordances - mostly available to all archetypes."""
        return ATELIER_AFFORDANCES

    # =========================================================================
    # Core Aspects
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("atelier_state")],
        help="Show workshop status and health metrics",
        examples=["kg atelier", "kg atelier status"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Show atelier status."""
        if self._persistence is None:
            return BasicRendering(
                summary="Atelier: Not Configured",
                content=(
                    "Atelier persistence not configured.\n"
                    "Configure with AtelierPersistence in services/atelier/"
                ),
                metadata={"status": "not_configured"},
            )

        status = await self._persistence.manifest()
        return self._format_status(status)

    # =========================================================================
    # Workshop Management
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("workshops")],
        help="Create a new creative workshop",
        examples=[
            'kg atelier workshop create "Poetry Circle" --theme nature',
            'kg atelier workshop create "Haiku Lab"',
        ],
    )
    async def workshop_create(
        self,
        observer: "Umwelt[Any, Any]",
        name: str,
        description: str | None = None,
        theme: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Create a new workshop."""
        if self._persistence is None:
            return self._not_configured()

        workshop = await self._persistence.create_workshop(
            name=name,
            description=description,
            theme=theme,
        )

        return BasicRendering(
            summary=f"Workshop Created: {workshop.name}",
            content=(
                f"ID: {workshop.id}\n"
                f"Name: {workshop.name}\n"
                f"Theme: {workshop.theme or 'None'}\n"
                f"Description: {workshop.description or 'None'}\n\n"
                f"Add artisans with: kg atelier workshop join {workshop.id} <name> <specialty>"
            ),
            metadata={
                "status": "created",
                "workshop_id": workshop.id,
                "name": workshop.name,
                "theme": workshop.theme,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("artisans")],
        help="Add an artisan to a workshop",
        examples=[
            "kg atelier workshop join workshop-abc123 Blake poet",
            "kg atelier workshop join workshop-abc123 Escher visualist --style surrealist",
        ],
    )
    async def workshop_join(
        self,
        observer: "Umwelt[Any, Any]",
        workshop_id: str,
        name: str,
        specialty: str,
        style: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Add an artisan to a workshop."""
        if self._persistence is None:
            return self._not_configured()

        artisan = await self._persistence.add_artisan(
            workshop_id=workshop_id,
            name=name,
            specialty=specialty,
            style=style,
        )

        if artisan is None:
            return BasicRendering(
                summary="Workshop Not Found",
                content=f"Workshop '{workshop_id}' not found or not active.",
                metadata={"status": "not_found", "workshop_id": workshop_id},
            )

        return BasicRendering(
            summary=f"Artisan Joined: {artisan.name}",
            content=(
                f"ID: {artisan.id}\n"
                f"Name: {artisan.name}\n"
                f"Specialty: {artisan.specialty}\n"
                f"Style: {artisan.style or 'None'}\n"
                f"Workshop: {artisan.workshop_id}\n\n"
                f'Contribute with: kg atelier contribute {artisan.id} "content"'
            ),
            metadata={
                "status": "joined",
                "artisan_id": artisan.id,
                "name": artisan.name,
                "workshop_id": workshop_id,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("workshops")],
        help="List workshops",
        examples=[
            "kg atelier workshop list",
            "kg atelier workshop list --active",
            "kg atelier workshop list --theme nature",
        ],
    )
    async def workshop_list(
        self,
        observer: "Umwelt[Any, Any]",
        active_only: bool = False,
        theme: str | None = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> Renderable:
        """List workshops."""
        if self._persistence is None:
            return self._not_configured()

        workshops = await self._persistence.list_workshops(
            active_only=active_only,
            theme=theme,
            limit=limit,
        )

        if not workshops:
            return BasicRendering(
                summary="No Workshops Found",
                content=(
                    "No workshops found with the given criteria.\n\n"
                    'Create one with: kg atelier workshop create "Name" --theme theme'
                ),
                metadata={"status": "empty", "count": 0},
            )

        lines = ["[WORKSHOPS]", "=" * 50]
        for w in workshops:
            status = "[ACTIVE]" if w.is_active else "[ENDED]"
            lines.append(f"\n{status} {w.name} ({w.id})")
            if w.theme:
                lines.append(f"  Theme: {w.theme}")
            lines.append(f"  Artisans: {w.artisan_count}")
            lines.append(f"  Contributions: {w.contribution_count}")

        return BasicRendering(
            summary=f"Found {len(workshops)} workshops",
            content="\n".join(lines),
            metadata={
                "count": len(workshops),
                "workshops": [
                    {
                        "id": w.id,
                        "name": w.name,
                        "theme": w.theme,
                        "is_active": w.is_active,
                        "artisan_count": w.artisan_count,
                    }
                    for w in workshops
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("workshops")],
        help="End an active workshop",
        examples=["kg atelier workshop end workshop-abc123"],
    )
    async def workshop_end(
        self,
        observer: "Umwelt[Any, Any]",
        workshop_id: str,
        **kwargs: Any,
    ) -> Renderable:
        """End a workshop."""
        if self._persistence is None:
            return self._not_configured()

        success = await self._persistence.end_workshop(workshop_id)

        if not success:
            return BasicRendering(
                summary="Workshop Not Found",
                content=f"Workshop '{workshop_id}' not found.",
                metadata={"status": "not_found", "workshop_id": workshop_id},
            )

        return BasicRendering(
            summary=f"Workshop Ended: {workshop_id}",
            content=(
                f"Workshop {workshop_id} has been ended.\n\n"
                "Consider creating an exhibition with: kg atelier exhibition create"
            ),
            metadata={"status": "ended", "workshop_id": workshop_id},
        )

    # =========================================================================
    # Contribution Management
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("contributions"),
            Effect.WRITES("dgent_content"),
        ],
        help="Submit a creative contribution",
        examples=[
            'kg atelier contribute artisan-abc "A haiku about persistence"',
            'kg atelier contribute artisan-abc "draft poem" --type draft',
        ],
    )
    async def contribute(
        self,
        observer: "Umwelt[Any, Any]",
        artisan_id: str,
        content: str,
        content_type: str = "text",
        contribution_type: str = "draft",
        prompt: str | None = None,
        inspiration: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Submit a creative contribution."""
        if self._persistence is None:
            return self._not_configured()

        contribution = await self._persistence.contribute(
            artisan_id=artisan_id,
            content=content,
            content_type=content_type,
            contribution_type=contribution_type,
            prompt=prompt,
            inspiration=inspiration,
        )

        if contribution is None:
            return BasicRendering(
                summary="Artisan Not Found",
                content=f"Artisan '{artisan_id}' not found or not active.",
                metadata={"status": "not_found", "artisan_id": artisan_id},
            )

        preview = content[:80] + "..." if len(content) > 80 else content

        return BasicRendering(
            summary=f"Contribution Submitted: {contribution.id}",
            content=(
                f"ID: {contribution.id}\n"
                f"Artisan: {contribution.artisan_name}\n"
                f"Type: {contribution.contribution_type} ({contribution.content_type})\n"
                f"Preview: {preview}"
            ),
            metadata={
                "status": "contributed",
                "contribution_id": contribution.id,
                "artisan_id": artisan_id,
                "contribution_type": contribution_type,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("contributions")],
        help="List contributions",
        examples=[
            "kg atelier contributions",
            "kg atelier contributions --artisan artisan-abc",
            "kg atelier contributions --workshop workshop-abc",
        ],
    )
    async def contributions(
        self,
        observer: "Umwelt[Any, Any]",
        artisan_id: str | None = None,
        workshop_id: str | None = None,
        contribution_type: str | None = None,
        limit: int = 50,
        **kwargs: Any,
    ) -> Renderable:
        """List contributions."""
        if self._persistence is None:
            return self._not_configured()

        items = await self._persistence.list_contributions(
            artisan_id=artisan_id,
            workshop_id=workshop_id,
            contribution_type=contribution_type,
            limit=limit,
        )

        if not items:
            return BasicRendering(
                summary="No Contributions Found",
                content="No contributions found with the given criteria.",
                metadata={"status": "empty", "count": 0},
            )

        lines = ["[CONTRIBUTIONS]", "=" * 50]
        for c in items:
            preview = c.content[:50].replace("\n", " ")
            lines.append(f"\n[{c.contribution_type.upper()}] {c.artisan_name}")
            lines.append(f"  ID: {c.id}")
            lines.append(f"  Preview: {preview}...")

        return BasicRendering(
            summary=f"Found {len(items)} contributions",
            content="\n".join(lines),
            metadata={
                "count": len(items),
                "contributions": [
                    {
                        "id": c.id,
                        "artisan_name": c.artisan_name,
                        "contribution_type": c.contribution_type,
                        "content_type": c.content_type,
                    }
                    for c in items
                ],
            },
        )

    # =========================================================================
    # Exhibition Management
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exhibitions")],
        help="Create an exhibition for a workshop",
        examples=[
            'kg atelier exhibition create workshop-abc "Summer Show"',
            'kg atelier exhibition create workshop-abc "Haiku Gallery" --notes "Best of 2025"',
        ],
    )
    async def exhibition_create(
        self,
        observer: "Umwelt[Any, Any]",
        workshop_id: str,
        name: str,
        description: str | None = None,
        curator_notes: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Create an exhibition."""
        if self._persistence is None:
            return self._not_configured()

        exhibition = await self._persistence.create_exhibition(
            workshop_id=workshop_id,
            name=name,
            description=description,
            curator_notes=curator_notes,
        )

        if exhibition is None:
            return BasicRendering(
                summary="Workshop Not Found",
                content=f"Workshop '{workshop_id}' not found.",
                metadata={"status": "not_found", "workshop_id": workshop_id},
            )

        return BasicRendering(
            summary=f"Exhibition Created: {exhibition.name}",
            content=(
                f"ID: {exhibition.id}\n"
                f"Name: {exhibition.name}\n"
                f"Status: DRAFT (not yet open)\n\n"
                f'Add items with: kg atelier gallery add {exhibition.id} "content"\n'
                f"Open with: kg atelier exhibition open {exhibition.id}"
            ),
            metadata={
                "status": "created",
                "exhibition_id": exhibition.id,
                "name": exhibition.name,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("exhibitions")],
        help="Open an exhibition for viewing",
        examples=["kg atelier exhibition open exhibit-abc123"],
    )
    async def exhibition_open(
        self,
        observer: "Umwelt[Any, Any]",
        exhibition_id: str,
        **kwargs: Any,
    ) -> Renderable:
        """Open an exhibition."""
        if self._persistence is None:
            return self._not_configured()

        success = await self._persistence.open_exhibition(exhibition_id)

        if not success:
            return BasicRendering(
                summary="Exhibition Not Found",
                content=f"Exhibition '{exhibition_id}' not found or already open.",
                metadata={"status": "not_found", "exhibition_id": exhibition_id},
            )

        return BasicRendering(
            summary=f"Exhibition Opened: {exhibition_id}",
            content=(
                f"Exhibition {exhibition_id} is now open for viewing!\n\n"
                f"View with: kg atelier gallery view {exhibition_id}"
            ),
            metadata={"status": "opened", "exhibition_id": exhibition_id},
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("gallery_items")],
        help="Add an item to an exhibition gallery",
        examples=[
            'kg atelier gallery add exhibit-abc "A haiku about persistence"',
            'kg atelier gallery add exhibit-abc "code" --type code --title "Fibonacci"',
        ],
    )
    async def gallery_add(
        self,
        observer: "Umwelt[Any, Any]",
        exhibition_id: str,
        artifact_content: str,
        artifact_type: str = "text",
        title: str | None = None,
        description: str | None = None,
        artisan_ids: list[str] | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Add an item to gallery."""
        if self._persistence is None:
            return self._not_configured()

        item = await self._persistence.add_to_gallery(
            exhibition_id=exhibition_id,
            artifact_content=artifact_content,
            artifact_type=artifact_type,
            title=title,
            description=description,
            artisan_ids=artisan_ids,
        )

        if item is None:
            return BasicRendering(
                summary="Exhibition Not Found",
                content=f"Exhibition '{exhibition_id}' not found.",
                metadata={"status": "not_found", "exhibition_id": exhibition_id},
            )

        return BasicRendering(
            summary=f"Gallery Item Added: {item.id}",
            content=(
                f"ID: {item.id}\n"
                f"Title: {item.title or 'Untitled'}\n"
                f"Type: {item.artifact_type}\n"
                f"Display Order: {item.display_order}"
            ),
            metadata={
                "status": "added",
                "item_id": item.id,
                "exhibition_id": exhibition_id,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("exhibitions"), Effect.WRITES("view_count")],
        help="View an exhibition (increments view count)",
        examples=["kg atelier gallery view exhibit-abc123"],
    )
    async def gallery_view(
        self,
        observer: "Umwelt[Any, Any]",
        exhibition_id: str,
        **kwargs: Any,
    ) -> Renderable:
        """View an exhibition."""
        if self._persistence is None:
            return self._not_configured()

        exhibition = await self._persistence.view_exhibition(exhibition_id)

        if exhibition is None:
            return BasicRendering(
                summary="Exhibition Not Found",
                content=f"Exhibition '{exhibition_id}' not found.",
                metadata={"status": "not_found", "exhibition_id": exhibition_id},
            )

        status = "OPEN" if exhibition.is_open else "DRAFT"

        return BasicRendering(
            summary=f"{exhibition.name} [{status}]",
            content=(
                f"ID: {exhibition.id}\n"
                f"Status: {status}\n"
                f"Items: {exhibition.item_count}\n"
                f"Views: {exhibition.view_count}\n"
                f"Curator Notes: {exhibition.curator_notes or 'None'}\n\n"
                f"View items with: kg atelier gallery items {exhibition.id}"
            ),
            metadata={
                "exhibition_id": exhibition.id,
                "name": exhibition.name,
                "is_open": exhibition.is_open,
                "item_count": exhibition.item_count,
                "view_count": exhibition.view_count,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("gallery_items")],
        help="List items in an exhibition gallery",
        examples=["kg atelier gallery items exhibit-abc123"],
    )
    async def gallery_items(
        self,
        observer: "Umwelt[Any, Any]",
        exhibition_id: str,
        **kwargs: Any,
    ) -> Renderable:
        """List gallery items."""
        if self._persistence is None:
            return self._not_configured()

        items = await self._persistence.list_gallery_items(exhibition_id)

        if not items:
            return BasicRendering(
                summary="No Gallery Items",
                content=f"Exhibition '{exhibition_id}' has no items yet.",
                metadata={"status": "empty", "count": 0},
            )

        lines = ["[GALLERY]", "=" * 50]
        for item in items:
            preview = item.artifact_content[:60].replace("\n", " ")
            lines.append(f"\n#{item.display_order} {item.title or 'Untitled'}")
            lines.append(f"  Type: {item.artifact_type}")
            lines.append(f"  Preview: {preview}...")

        return BasicRendering(
            summary=f"Gallery: {len(items)} items",
            content="\n".join(lines),
            metadata={
                "count": len(items),
                "items": [
                    {
                        "id": i.id,
                        "title": i.title,
                        "artifact_type": i.artifact_type,
                        "display_order": i.display_order,
                    }
                    for i in items
                ],
            },
        )

    # =========================================================================
    # Aspect Routing
    # =========================================================================

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle atelier-specific aspects."""
        match aspect:
            # Workshop
            case "workshop_create":
                return await self.workshop_create(observer, **kwargs)
            case "workshop_join":
                return await self.workshop_join(observer, **kwargs)
            case "workshop_list":
                return await self.workshop_list(observer, **kwargs)
            case "workshop_end":
                return await self.workshop_end(observer, **kwargs)
            # Contributions
            case "contribute":
                return await self.contribute(observer, **kwargs)
            case "contributions":
                return await self.contributions(observer, **kwargs)
            # Exhibitions
            case "exhibition_create":
                return await self.exhibition_create(observer, **kwargs)
            case "exhibition_open":
                return await self.exhibition_open(observer, **kwargs)
            # Gallery
            case "gallery_add":
                return await self.gallery_add(observer, **kwargs)
            case "gallery_view":
                return await self.gallery_view(observer, **kwargs)
            case "gallery_items":
                return await self.gallery_items(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # =========================================================================
    # Helpers
    # =========================================================================

    def _not_configured(self) -> BasicRendering:
        """Return not configured message."""
        return BasicRendering(
            summary="Atelier: Not Configured",
            content=(
                "Atelier persistence not configured.\n"
                "Configure with AtelierPersistence in services/atelier/"
            ),
            metadata={"status": "not_configured"},
        )

    def _format_status(self, status: "AtelierStatus") -> BasicRendering:
        """Format status for rendering."""
        lines = [
            "[ATELIER] Creative Workshop Status",
            "=" * 50,
            f"  Total Workshops:      {status.total_workshops}",
            f"  Active Workshops:     {status.active_workshops}",
            f"  Total Artisans:       {status.total_artisans}",
            f"  Total Contributions:  {status.total_contributions}",
            f"  Total Exhibitions:    {status.total_exhibitions}",
            f"  Open Exhibitions:     {status.open_exhibitions}",
            f"  Storage Backend:      {status.storage_backend}",
            "=" * 50,
        ]

        return BasicRendering(
            summary=f"Atelier: {status.total_workshops} workshops, {status.total_contributions} contributions",
            content="\n".join(lines),
            metadata={
                "total_workshops": status.total_workshops,
                "active_workshops": status.active_workshops,
                "total_artisans": status.total_artisans,
                "total_contributions": status.total_contributions,
                "total_exhibitions": status.total_exhibitions,
                "open_exhibitions": status.open_exhibitions,
            },
        )


# =============================================================================
# Factory Functions
# =============================================================================

# Global singleton for AtelierNode
_atelier_node: AtelierNode | None = None


def get_atelier_node() -> AtelierNode:
    """Get the global AtelierNode singleton."""
    global _atelier_node
    if _atelier_node is None:
        _atelier_node = AtelierNode()
    return _atelier_node


def set_atelier_node(node: AtelierNode) -> None:
    """Set the global AtelierNode singleton (for testing)."""
    global _atelier_node
    _atelier_node = node


def create_atelier_node(
    persistence: "AtelierPersistence | None" = None,
) -> AtelierNode:
    """
    Create an AtelierNode with optional persistence injection.

    Args:
        persistence: Pre-configured AtelierPersistence

    Returns:
        Configured AtelierNode
    """
    return AtelierNode(_persistence=persistence)


__all__ = [
    # Constants
    "ATELIER_AFFORDANCES",
    # Node
    "AtelierNode",
    # Factory
    "get_atelier_node",
    "set_atelier_node",
    "create_atelier_node",
]
