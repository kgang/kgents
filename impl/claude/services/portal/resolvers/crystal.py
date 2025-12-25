"""
CrystalResolver: Resolver for crystal: resources.

Resolves Memory Crystals (compressed conversation memories).

Philosophy:
    "The crystal is compressed wisdom. The memories are distilled decisions."

See: spec/protocols/portal-resource-system.md §5.6
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..uri import PortalURI
from ..resolver import ResolvedResource

if TYPE_CHECKING:
    from services.chat.crystallizer import MemoryCrystal


class CrystalResolver:
    """
    Resolver for crystal: resources.

    Handles:
    - crystal:crystal-abc123    → MemoryCrystal with content

    Dependencies:
        crystal_store: Storage for MemoryCrystal instances
    """

    resource_type = "crystal"

    def __init__(self, crystal_store: Any = None) -> None:
        """
        Initialize CrystalResolver.

        Args:
            crystal_store: Storage provider for memory crystals
        """
        self.crystal_store = crystal_store

    def can_resolve(self, uri: PortalURI) -> bool:
        """Check if this resolver can handle the URI."""
        return uri.resource_type == self.resource_type

    async def resolve(self, uri: PortalURI, observer: Any = None) -> ResolvedResource:
        """
        Resolve MemoryCrystal.

        Args:
            uri: Parsed portal URI
            observer: Optional observer for access control

        Returns:
            ResolvedResource with crystal data
        """
        crystal_id = uri.resource_path

        # Fetch crystal
        crystal = await self._get_crystal(crystal_id)
        if crystal is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Crystal Not Found",
                preview=f"Crystal not found: {crystal_id}",
                content=None,
                actions=[],
                metadata={"error": "crystal_not_found"},
            )

        return self._resolve_crystal(uri, crystal)

    def _resolve_crystal(self, uri: PortalURI, crystal: MemoryCrystal) -> ResolvedResource:
        """Resolve MemoryCrystal to resource."""
        # Get crystal content
        crystal_id = getattr(crystal, "crystal_id", str(uri.resource_path))
        title = getattr(crystal, "title", None) or crystal_id
        summary = getattr(crystal, "summary", "")
        topics = getattr(crystal, "topics", [])
        decisions = getattr(crystal, "decisions", [])
        created_at = getattr(crystal, "created_at", None)
        source_session = getattr(crystal, "source_session_id", None)

        # Build preview
        preview = summary[:100] + "..." if len(summary) > 100 else summary

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title=title,
            preview=preview,
            content={
                "crystal_id": crystal_id,
                "title": title,
                "summary": summary,
                "topics": topics,
                "decisions": decisions,
                "source_session_id": source_session,
                "created_at": created_at.isoformat() if created_at else None,
            },
            actions=["expand", "hydrate", "cite"],
            metadata={
                "crystal_id": crystal_id,
                "topics": topics,
                "decision_count": len(decisions),
                "source_session_id": source_session,
            },
        )

    async def _get_crystal(self, crystal_id: str) -> MemoryCrystal | None:
        """Fetch crystal from storage."""
        if self.crystal_store is None:
            return None

        if hasattr(self.crystal_store, "get"):
            return await self.crystal_store.get(crystal_id)
        elif hasattr(self.crystal_store, "load"):
            return await self.crystal_store.load(crystal_id)
        else:
            return None


__all__ = ["CrystalResolver"]
