"""
AGENTESE Self Lesson Context: Curated Knowledge Layer.

Knowledge-related nodes for self.lesson.* paths:
- LessonNode: Versioned knowledge management

This node provides AGENTESE access to the Lesson primitive for
curated, versioned knowledge that evolves across sessions.

AGENTESE Paths:
    self.lesson.manifest    - Show all current knowledge
    self.lesson.create      - Create new knowledge entry
    self.lesson.evolve      - Evolve existing knowledge
    self.lesson.search      - Search knowledge by topic/content
    self.lesson.history     - Get evolution history of a topic
    self.lesson.curate      - Human curation: elevate trust to L3
    self.lesson.crystallize - Bridge: crystallize Brain memory to Lesson

See: services/witness/lesson.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass
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
_lesson_store: Any = None


def _get_store() -> Any:
    """Get or create the global LessonStore."""
    global _lesson_store
    if _lesson_store is None:
        from services.witness.lesson import LessonStore

        _lesson_store = LessonStore()
    return _lesson_store


# =============================================================================
# LessonNode: AGENTESE Interface to Lesson
# =============================================================================


# Lesson affordances
LESSON_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "create",
    "evolve",
    "search",
    "history",
    "curate",
    "crystallize",
)


@node(
    "self.lesson",
    description="Curated knowledge layer with versioning",
)
@dataclass
class LessonNode(BaseLogosNode):
    """
    self.lesson - Curated knowledge layer with versioning.

    A Lesson is a piece of crystallized knowledge that evolves over time.
    Like geological terraces, each version builds on the last while
    preserving history.

    Laws (from lesson.py):
    - Law 1 (Immutability): Lessons are frozen after creation
    - Law 2 (Supersession): New versions explicitly supersede old
    - Law 3 (History Preserved): All versions are kept for reference
    - Law 4 (Topic Uniqueness): One current version per topic

    AGENTESE: self.lesson.*
    """

    _handle: str = "self.lesson"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Lesson affordances available to all archetypes."""
        return LESSON_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Show all current knowledge entries.

        Returns:
            List of all CURRENT Lessons with topics and summaries
        """
        store = _get_store()
        current_lessons = store.all_current()

        # Build manifest
        entries = []
        for lesson in sorted(current_lessons, key=lambda t: t.topic):
            entries.append(
                {
                    "id": str(lesson.id),
                    "topic": lesson.topic,
                    "version": lesson.version,
                    "confidence": lesson.confidence,
                    "tags": list(lesson.tags),
                    "age_days": round(lesson.age_days, 1),
                    "content_preview": lesson.content[:100] + "..."
                    if len(lesson.content) > 100
                    else lesson.content,
                }
            )

        manifest_data = {
            "path": self.handle,
            "description": "Curated knowledge layer with versioning",
            "total_entries": len(entries),
            "topics": store.all_topics(),
            "entries": entries,
            "laws": [
                "Law 1: Lessons are immutable after creation",
                "Law 2: New versions explicitly supersede old",
                "Law 3: All versions are kept for reference",
                "Law 4: One current version per topic",
            ],
        }

        return BasicRendering(
            summary="Lessons (Knowledge Layer)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Lesson-specific aspects."""
        match aspect:
            case "create":
                return self._create_entry(**kwargs)
            case "evolve":
                return self._evolve_entry(**kwargs)
            case "search":
                return self._search_entries(**kwargs)
            case "history":
                return self._get_history(**kwargs)
            case "curate":
                return self._curate_entry(**kwargs)
            case "crystallize":
                return await self._crystallize_from_brain(**kwargs)
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
        voice_check: bool = True,
    ) -> dict[str, Any]:
        """
        Create a new knowledge entry (internal).

        Args:
            topic: Topic name for the entry
            content: Knowledge content
            tags: Optional tags for categorization
            source: Where this knowledge came from
            confidence: Trust level (0.0-1.0)
            voice_check: If True, run VoiceGate check on content

        Returns:
            Result dict with created lesson or error
        """
        from services.witness.lesson import Lesson

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

        # Optional VoiceGate check (Anti-Sausage Protocol)
        voice_result = None
        if voice_check:
            from services.witness.voice_gate import VoiceGate

            gate = VoiceGate()
            check = gate.check(content)
            voice_result = {
                "passed": check.passed,
                "warnings": check.warning_count,
                "anchors": list(check.anchors_referenced),
            }
            # Note: We don't block on voice check failure in permissive mode
            # This allows creating content but flags it for review

        # Create new lesson
        lesson = Lesson.create(
            topic=topic,
            content=content,
            tags=tuple(tags) if tags else (),
            source=source,
            confidence=confidence,
        )

        # Add to store
        store.add(lesson)

        result: dict[str, Any] = {
            "created": True,
            "lesson": lesson.to_dict(),
        }
        if voice_result:
            result["voice_check"] = voice_result

        return result

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
        new_lesson = current.evolve(
            content=content,
            reason=reason,
            tags=tuple(tags) if tags is not None else None,
            confidence=confidence,
        )

        # Add to store (marks old as superseded)
        store.add(new_lesson)

        return {
            "evolved": True,
            "old_version": current.version,
            "new_version": new_lesson.version,
            "lesson": new_lesson.to_dict(),
        }

    def _search_entries(self, query: str = "") -> dict[str, Any]:
        """Search knowledge by topic or content (internal)."""
        store = _get_store()
        results = store.search(query)

        entries = []
        for lesson in results:
            entries.append(
                {
                    "id": str(lesson.id),
                    "topic": lesson.topic,
                    "version": lesson.version,
                    "confidence": lesson.confidence,
                    "content_preview": lesson.content[:150] + "..."
                    if len(lesson.content) > 150
                    else lesson.content,
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
        for lesson in versions:
            entries.append(
                {
                    "version": lesson.version,
                    "status": lesson.status.name,
                    "created_at": lesson.created_at.isoformat(),
                    "evolution_reason": lesson.evolution_reason,
                    "content_preview": lesson.content[:100] + "..."
                    if len(lesson.content) > 100
                    else lesson.content,
                }
            )

        return {
            "topic": topic,
            "count": len(entries),
            "versions": entries,
        }

    def _curate_entry(
        self,
        topic: str = "",
        curator: str = "human",
        notes: str = "",
    ) -> dict[str, Any]:
        """
        Curate a knowledge entry, elevating it to trust L3 (internal).

        Human curation is a stamp of approval. When a human curates
        a Lesson entry, it becomes authoritative knowledge.

        Law: Human override = trust L3 on that crystal.

        Args:
            topic: The topic to curate
            curator: Who is curating (default: "human")
            notes: Optional curation notes

        Returns:
            Result with curated lesson and trust elevation
        """
        store = _get_store()

        # Get current version
        current = store.current(topic)
        if not current:
            return {
                "error": "topic_not_found",
                "message": f"Topic '{topic}' not found.",
            }

        # Evolve with curation metadata (creates new version)
        curated = current.evolve(
            content=current.content,  # Content unchanged
            reason=f"Curated by {curator}" + (f": {notes}" if notes else ""),
            confidence=1.0,  # L3 trust = full confidence
        )

        # Add curation metadata
        from services.witness.lesson import Lesson

        curated_with_meta = Lesson(
            id=curated.id,
            topic=curated.topic,
            content=curated.content,
            version=curated.version,
            supersedes=curated.supersedes,
            status=curated.status,
            created_at=curated.created_at,
            evolution_reason=curated.evolution_reason,
            tags=(*curated.tags, "curated"),
            source=curated.source,
            confidence=1.0,
            metadata={
                **curated.metadata,
                "curated": True,
                "curator": curator,
                "curation_notes": notes,
                "trust_level": "L3",  # WARP trust level 3 = human-approved
            },
        )

        # Add to store (marks old as superseded)
        store.add(curated_with_meta)

        return {
            "curated": True,
            "topic": topic,
            "old_version": current.version,
            "new_version": curated_with_meta.version,
            "trust_level": "L3",
            "curator": curator,
            "lesson": curated_with_meta.to_dict(),
        }

    async def _crystallize_from_brain(
        self,
        crystal_id: str = "",
        topic: str = "",
        source: str = "brain",
    ) -> dict[str, Any]:
        """
        Crystallize a Brain memory into a Lesson entry (internal).

        This is the bridge between Brain (ephemeral memory) and Lesson
        (curated knowledge). When an insight from Brain is worth preserving,
        crystallize it to Lesson.

        Philosophy: "Knowledge crystallizes over time."

        Args:
            crystal_id: The Brain crystal ID to crystallize
            topic: Topic name for the Lesson entry (required)
            source: Source attribution (default: "brain")

        Returns:
            Result with created lesson
        """
        if not crystal_id:
            return {
                "error": "missing_crystal_id",
                "message": "crystal_id is required to crystallize from Brain.",
            }

        if not topic:
            return {
                "error": "missing_topic",
                "message": "topic is required for Lesson entry.",
            }

        # Try to get the Brain crystal via AGENTESE gateway
        try:
            from protocols.agentese.gateway import create_gateway
            from protocols.agentese.node import Observer

            gateway = create_gateway(prefix="/agentese")
            observer = Observer.test()

            # Invoke Brain's get aspect via gateway
            result = await gateway._invoke_path(
                "self.memory",
                "get",
                observer,
                crystal_id=crystal_id,
            )

            # Check for error response
            if isinstance(result, dict) and "error" in result:
                return {
                    "error": "crystal_not_found",
                    "message": f"Brain crystal '{crystal_id}' not found.",
                }

            # Extract content from result
            content = result.get("content", "") if isinstance(result, dict) else ""
            if not content:
                return {
                    "error": "crystal_empty",
                    "message": f"Brain crystal '{crystal_id}' has no content.",
                }

            # Create Lesson entry from Brain crystal
            create_result = self._create_entry(
                topic=topic,
                content=content,
                tags=["crystallized"],
                source=f"{source}:{crystal_id}",
                confidence=0.8,  # L2 trust: machine-sourced, needs curation for L3
                voice_check=True,
            )

            if "error" in create_result:
                return create_result

            return {
                "crystallized": True,
                "source_crystal": crystal_id,
                "topic": topic,
                "trust_level": "L2",  # Machine-sourced = L2
                "message": "Use 'curate' to elevate to L3",
                "lesson": create_result.get("lesson"),
            }

        except Exception as e:
            # Graceful degradation
            return {
                "error": "crystallization_failed",
                "message": f"Could not crystallize: {e}. Create entry directly with 'create'.",
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
            summary=f"Evolved '{topic}': v{data['old_version']} -> v{data['new_version']}",
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

    @aspect(
        category=AspectCategory.MUTATION,
        help="Curate entry: human approval elevates to trust L3",
    )
    def curate(
        self,
        topic: str,
        curator: str = "human",
        notes: str = "",
    ) -> BasicRendering:
        """
        Curate a knowledge entry (public API).

        Human curation elevates trust to L3 (maximum).
        This is the stamp of approval that transforms
        machine-generated insight into authoritative knowledge.

        Args:
            topic: The topic to curate
            curator: Who is curating (default: "human")
            notes: Optional curation notes

        Returns:
            BasicRendering with curation result
        """
        data = self._curate_entry(topic=topic, curator=curator, notes=notes)

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=f"Could not curate '{topic}'.",
                metadata=data,
            )

        return BasicRendering(
            summary=f"Curated '{topic}': v{data['old_version']} -> v{data['new_version']} (Trust: L3)",
            content=self._format_curate_cli(data),
            metadata=data,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        help="Crystallize Brain memory to Lesson entry",
    )
    async def crystallize(
        self,
        crystal_id: str,
        topic: str,
        source: str = "brain",
    ) -> BasicRendering:
        """
        Crystallize a Brain memory into a Lesson entry (public API).

        This bridges ephemeral Brain memories to curated Lesson knowledge.
        Crystallized entries start at trust L2 (machine-sourced).
        Use 'curate' afterward to elevate to L3.

        Args:
            crystal_id: The Brain crystal ID to crystallize
            topic: Topic name for the Lesson entry
            source: Source attribution (default: "brain")

        Returns:
            BasicRendering with crystallization result
        """
        data = await self._crystallize_from_brain(
            crystal_id=crystal_id,
            topic=topic,
            source=source,
        )

        if "error" in data:
            return BasicRendering(
                summary=f"Error: {data['message']}",
                content=f"Could not crystallize '{crystal_id}' to '{topic}'.",
                metadata=data,
            )

        return BasicRendering(
            summary=f"Crystallized '{crystal_id}' -> '{topic}' (Trust: L2)",
            content=self._format_crystallize_cli(data),
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
            "Lessons (Knowledge Layer)",
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
                lines.append(f"  - {entry['topic']} (v{entry['version']}){conf_str}")
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
            lines.append(f"- {result['topic']} (v{result['version']})")
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
            status_icon = "o" if version["status"] == "CURRENT" else "-"
            lines.append(f"{status_icon} v{version['version']} [{version['status']}]")
            if version["evolution_reason"]:
                lines.append(f"  Reason: {version['evolution_reason']}")
            lines.append(f"  Created: {version['created_at'][:19]}")
            lines.append("")

        return "\n".join(lines)

    def _format_curate_cli(self, data: dict[str, Any]) -> str:
        """Format curate result for CLI output."""
        lines = [
            f"Curated: '{data['topic']}'",
            "=" * 40,
            "",
            f"Version: {data['old_version']} -> {data['new_version']}",
            f"Trust Level: {data['trust_level']}",
            f"Curator: {data['curator']}",
            "",
            "This knowledge is now authoritative.",
        ]
        return "\n".join(lines)

    def _format_crystallize_cli(self, data: dict[str, Any]) -> str:
        """Format crystallize result for CLI output."""
        lines = [
            f"Crystallized: '{data['topic']}'",
            "=" * 40,
            "",
            f"Source Crystal: {data['source_crystal']}",
            f"Trust Level: {data['trust_level']}",
            "",
            data.get("message", ""),
        ]
        return "\n".join(lines)


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================

# Old name -> new name (for gradual migration)
TerraceNode = LessonNode

# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "LessonNode",
    "TerraceNode",  # Backwards compat
]
