"""
AGENTESE Brain Terrace Context: Curated Knowledge Layer.

Knowledge-related nodes for brain.terrace.* paths:
- TerraceNode: Versioned knowledge management

This node provides AGENTESE access to the Terrace primitive for
curated, versioned knowledge that evolves across sessions.

AGENTESE Paths:
    brain.terrace.manifest  - Show all current knowledge
    brain.terrace.create    - Create new knowledge entry
    brain.terrace.evolve    - Evolve existing knowledge
    brain.terrace.search    - Search knowledge by topic/content
    brain.terrace.history   - Get evolution history of a topic

See: services/witness/terrace.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# =============================================================================
# Global Store Instance
# =============================================================================

# Module-level store for persistence across invocations
_terrace_store: Any = None


def _get_store() -> Any:
    """Get or create the global TerraceStore."""
    global _terrace_store
    if _terrace_store is None:
        from services.witness.terrace import TerraceStore

        _terrace_store = TerraceStore()
    return _terrace_store


# =============================================================================
# TerraceNode: AGENTESE Interface to Terrace
# =============================================================================


# Terrace affordances
TERRACE_AFFORDANCES: tuple[str, ...] = ("manifest", "create", "evolve", "search", "history")


@node(
    "brain.terrace",
    description="Curated knowledge layer with versioning",
)
@dataclass
class TerraceNode(BaseLogosNode):
    """
    brain.terrace - Curated knowledge layer with versioning.

    A Terrace is a piece of crystallized knowledge that evolves over time.
    Like geological terraces, each version builds on the last while
    preserving history.

    Laws (from terrace.py):
    - Law 1 (Immutability): Terraces are frozen after creation
    - Law 2 (Supersession): New versions explicitly supersede old
    - Law 3 (History Preserved): All versions are kept for reference
    - Law 4 (Topic Uniqueness): One current version per topic

    AGENTESE: brain.terrace.*
    """

    _handle: str = "brain.terrace"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Terrace affordances available to all archetypes."""
        return TERRACE_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show all current knowledge entries.

        Returns:
            List of all CURRENT Terraces with topics and summaries
        """
        store = _get_store()
        current_terraces = store.all_current()

        # Build manifest
        entries = []
        for terrace in sorted(current_terraces, key=lambda t: t.topic):
            entries.append(
                {
                    "id": str(terrace.id),
                    "topic": terrace.topic,
                    "version": terrace.version,
                    "confidence": terrace.confidence,
                    "tags": list(terrace.tags),
                    "age_days": round(terrace.age_days, 1),
                    "content_preview": terrace.content[:100] + "..."
                    if len(terrace.content) > 100
                    else terrace.content,
                }
            )

        manifest_data = {
            "path": self.handle,
            "description": "Curated knowledge layer with versioning",
            "total_entries": len(entries),
            "topics": store.all_topics(),
            "entries": entries,
            "laws": [
                "Law 1: Terraces are immutable after creation",
                "Law 2: New versions explicitly supersede old",
                "Law 3: All versions are kept for reference",
                "Law 4: One current version per topic",
            ],
        }

        return BasicRendering(
            summary="Brain Terrace (Knowledge Layer)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Terrace-specific aspects."""
        match aspect:
            case "create":
                return self._create_entry(**kwargs)
            case "evolve":
                return self._evolve_entry(**kwargs)
            case "search":
                return self._search_entries(**kwargs)
            case "history":
                return self._get_history(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations (Internal)
    # ==========================================================================

    def _create_entry(
        self,
        topic: str = "",
        content: str = "",
        tags: list[str] | None = None,
        source: str = "",
        confidence: float = 1.0,
    ) -> dict[str, Any]:
        """Create a new knowledge entry (internal)."""
        from services.witness.terrace import Terrace

        store = _get_store()

        # Check if topic exists
        existing = store.current(topic)
        if existing:
            return {
                "error": "topic_exists",
                "message": f"Topic '{topic}' already exists. Use evolve to update.",
                "existing_id": str(existing.id),
                "existing_version": existing.version,
            }

        # Create new terrace
        terrace = Terrace.create(
            topic=topic,
            content=content,
            tags=tuple(tags) if tags else (),
            source=source,
            confidence=confidence,
        )

        # Add to store
        store.add(terrace)

        return {
            "created": True,
            "terrace": terrace.to_dict(),
        }

    def _evolve_entry(
        self,
        topic: str = "",
        content: str = "",
        reason: str = "",
        tags: list[str] | None = None,
        confidence: float | None = None,
    ) -> dict[str, Any]:
        """Evolve existing knowledge to new version (internal)."""
        store = _get_store()

        # Get current version
        current = store.current(topic)
        if not current:
            return {
                "error": "topic_not_found",
                "message": f"Topic '{topic}' not found. Use create for new topics.",
            }

        # Evolve to new version
        new_terrace = current.evolve(
            content=content,
            reason=reason,
            tags=tuple(tags) if tags is not None else None,
            confidence=confidence,
        )

        # Add to store (marks old as superseded)
        store.add(new_terrace)

        return {
            "evolved": True,
            "old_version": current.version,
            "new_version": new_terrace.version,
            "terrace": new_terrace.to_dict(),
        }

    def _search_entries(self, query: str = "") -> dict[str, Any]:
        """Search knowledge by topic or content (internal)."""
        store = _get_store()
        results = store.search(query)

        entries = []
        for terrace in results:
            entries.append(
                {
                    "id": str(terrace.id),
                    "topic": terrace.topic,
                    "version": terrace.version,
                    "confidence": terrace.confidence,
                    "content_preview": terrace.content[:150] + "..."
                    if len(terrace.content) > 150
                    else terrace.content,
                }
            )

        return {
            "query": query,
            "count": len(entries),
            "results": entries,
        }

    def _get_history(self, topic: str = "") -> dict[str, Any]:
        """Get evolution history of a topic (internal)."""
        store = _get_store()
        versions = store.history(topic)

        if not versions:
            return {
                "topic": topic,
                "count": 0,
                "versions": [],
            }

        entries = []
        for terrace in versions:
            entries.append(
                {
                    "version": terrace.version,
                    "status": terrace.status.name,
                    "created_at": terrace.created_at.isoformat(),
                    "evolution_reason": terrace.evolution_reason,
                    "content_preview": terrace.content[:100] + "..."
                    if len(terrace.content) > 100
                    else terrace.content,
                }
            )

        return {
            "topic": topic,
            "count": len(entries),
            "versions": entries,
        }

    # ==========================================================================
    # Public Interface (for direct calls / testing)
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Create new knowledge entry",
    )
    def create(
        self,
        topic: str,
        content: str,
        tags: list[str] | None = None,
        source: str = "",
        confidence: float = 1.0,
    ) -> BasicRendering:
        """
        Create a new knowledge entry (public API).

        Args:
            topic: The topic of this knowledge
            content: The knowledge content
            tags: Tags for categorization
            source: Where this knowledge came from
            confidence: Confidence level (0.0-1.0)

        Returns:
            BasicRendering with the result
        """
        data = self._create_entry(
            topic=topic,
            content=content,
            tags=tags,
            source=source,
            confidence=confidence,
        )

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=f"Topic '{topic}' already exists. Use evolve to update.",
                metadata=data,
            )

        return BasicRendering(
            summary=f"Created knowledge entry: '{topic}' (v1)",
            content=f"Created '{topic}' with {len(content)} chars",
            metadata=data,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        help="Evolve existing knowledge to new version",
    )
    def evolve(
        self,
        topic: str,
        content: str,
        reason: str = "",
        tags: list[str] | None = None,
        confidence: float | None = None,
    ) -> BasicRendering:
        """
        Evolve existing knowledge to a new version (public API).

        Args:
            topic: The topic to evolve
            content: Updated content
            reason: Why this evolution occurred
            tags: New tags (or inherit)
            confidence: New confidence (or inherit)

        Returns:
            BasicRendering with the result
        """
        data = self._evolve_entry(
            topic=topic,
            content=content,
            reason=reason,
            tags=tags,
            confidence=confidence,
        )

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=f"Topic '{topic}' not found. Use create for new topics.",
                metadata=data,
            )

        return BasicRendering(
            summary=f"Evolved '{topic}': v{data['old_version']} → v{data['new_version']}",
            content=self._format_evolve_cli(data),
            metadata=data,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Search knowledge by topic or content",
    )
    def search(self, query: str) -> BasicRendering:
        """
        Search knowledge by topic or content (public API).

        Args:
            query: Search query (case-insensitive substring match)

        Returns:
            BasicRendering with matching results
        """
        data = self._search_entries(query=query)

        return BasicRendering(
            summary=f"Search: '{query}' - {data['count']} results",
            content=self._format_search_cli(data),
            metadata=data,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get evolution history of a topic",
    )
    def history(self, topic: str) -> BasicRendering:
        """
        Get evolution history of a topic (public API).

        Args:
            topic: The topic to get history for

        Returns:
            BasicRendering with version history
        """
        data = self._get_history(topic=topic)

        return BasicRendering(
            summary=f"History: '{topic}' - {data['count']} versions",
            content=self._format_history_cli(data),
            metadata=data,
        )

    def _format_evolve_cli(self, data: dict[str, Any]) -> str:
        """Format evolve result for CLI output."""
        return f"Evolved to version {data['new_version']}"

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Brain Terrace (Knowledge Layer)",
            "=" * 40,
            "",
            f"Total entries: {data['total_entries']}",
            f"Topics: {len(data['topics'])}",
            "",
        ]

        if data["entries"]:
            lines.append("Current Knowledge:")
            for entry in data["entries"]:
                conf_str = f" [{entry['confidence']:.0%}]" if entry["confidence"] < 1.0 else ""
                lines.append(f"  • {entry['topic']} (v{entry['version']}){conf_str}")
                if entry["tags"]:
                    lines.append(f"    Tags: {', '.join(entry['tags'])}")
        else:
            lines.append("No knowledge entries yet. Use create to add some.")

        return "\n".join(lines)

    def _format_search_cli(self, data: dict[str, Any]) -> str:
        """Format search results for CLI output."""
        lines = [
            f"Search: '{data['query']}'",
            f"Found: {data['count']} results",
            "",
        ]

        for result in data["results"]:
            lines.append(f"• {result['topic']} (v{result['version']})")
            lines.append(f"  {result['content_preview']}")
            lines.append("")

        return "\n".join(lines)

    def _format_history_cli(self, data: dict[str, Any]) -> str:
        """Format history for CLI output."""
        lines = [
            f"History: '{data['topic']}'",
            f"Versions: {data['count']}",
            "",
        ]

        for version in data["versions"]:
            status_icon = "✓" if version["status"] == "CURRENT" else "○"
            lines.append(f"{status_icon} v{version['version']} [{version['status']}]")
            if version["evolution_reason"]:
                lines.append(f"  Reason: {version['evolution_reason']}")
            lines.append(f"  Created: {version['created_at'][:19]}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "TerraceNode",
]
