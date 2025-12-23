"""
WitnessSource: Adapts Witness marks to HyperEdge.

Witness marks contain tags that encode edges:
- spec:{path} — Mark relates to a spec (evidence edge)
- file:{path} — Mark relates to a file (evidence edge)
- evidence:{type} — Mark is evidence of type (impl|test|usage)
- gotcha, eureka, taste, friction — Session tags (edge kind)

Design Principle:
    "Every mark is evidence. Tags encode the graph structure."

Tag Taxonomy (from spec/protocols/living-spec-evidence.md):
    spec:{path}        → EVIDENCE edge to spec
    file:{path}        → EVIDENCE edge to file
    evidence:impl      → IMPLEMENTS edge
    evidence:test      → EVIDENCE edge (test coverage)
    evidence:usage     → EVIDENCE edge (usage proof)
    gotcha             → GOTCHA edge kind
    eureka             → EUREKA edge kind
    taste              → TASTE edge kind
    friction           → FRICTION edge kind
    decision           → DECISION edge kind
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from ..composition import ComposableMixin
from ..types import EdgeKind, HyperEdge

if TYPE_CHECKING:
    from ...witness.persistence import WitnessPersistence


class WitnessSource(ComposableMixin):
    """
    Edge source from Witness marks.

    Parses mark tags to extract edges:
    - Tags starting with "spec:" create edges to specs
    - Tags starting with "file:" create edges to files
    - Session tags (gotcha, eureka, etc.) determine edge kind

    Example:
        >>> persistence = WitnessPersistence(session, dgent)
        >>> source = WitnessSource(persistence)
        >>> async for edge in source.edges_to("spec/agents/d-gent.md"):
        ...     print(f"Evidence from: {edge.source_path}")
    """

    def __init__(self, persistence: "WitnessPersistence") -> None:
        """
        Create a WitnessSource from WitnessPersistence.

        Args:
            persistence: The WitnessPersistence instance
        """
        self._persistence = persistence

    @property
    def origin(self) -> str:
        """Source identifier."""
        return "witness"

    def _parse_tags(self, tags: list[str]) -> tuple[EdgeKind, list[str]]:
        """
        Parse tags to determine edge kind and target paths.

        Returns:
            Tuple of (EdgeKind, list of target paths)
        """
        kind = EdgeKind.EVIDENCE  # Default
        targets: list[str] = []

        for tag in tags:
            tag_lower = tag.lower()

            # Extract targets from spec: and file: tags
            if tag.startswith("spec:"):
                targets.append(tag[5:])  # Remove "spec:" prefix
            elif tag.startswith("file:"):
                targets.append(tag[5:])  # Remove "file:" prefix

            # Determine edge kind from session tags
            detected_kind = EdgeKind.from_witness_tag(tag_lower)
            if detected_kind:
                kind = detected_kind

        return kind, targets

    async def edges_from(self, path: str) -> AsyncIterator[HyperEdge]:
        """
        Get edges originating from a path.

        For witness, this finds marks whose action or reasoning mentions
        the path, then extracts edges from their tags.

        Args:
            path: Source path to query

        Yields:
            HyperEdge instances from marks mentioning path
        """
        # Get marks that might relate to this path
        # (This is a heuristic - marks don't have explicit source paths)
        marks = await self._persistence.get_marks(limit=1000)

        for mark in marks:
            # Check if mark action/reasoning mentions the path
            if path not in (mark.action or "") and path not in (mark.reasoning or ""):
                continue

            kind, targets = self._parse_tags(mark.tags)

            for target in targets:
                yield HyperEdge(
                    kind=kind,
                    source_path=path,
                    target_path=target,
                    origin=self.origin,
                    context=mark.action,
                    timestamp=mark.timestamp,
                    mark_id=mark.mark_id,
                )

    async def edges_to(self, path: str) -> AsyncIterator[HyperEdge]:
        """
        Get edges pointing to a path.

        Finds marks with tags like spec:{path} or file:{path}.

        Args:
            path: Target path to find edges to

        Yields:
            HyperEdge instances with this path as target
        """
        # Look for marks with tags pointing to this path
        # Try both spec: and file: prefixes
        for prefix in ["spec:", "file:"]:
            tag_to_search = f"{prefix}{path}"
            marks = await self._persistence.get_marks(
                limit=1000,
                tags=[tag_to_search],
            )

            for mark in marks:
                kind, _ = self._parse_tags(mark.tags)

                yield HyperEdge(
                    kind=kind,
                    source_path=mark.action or "unknown",
                    target_path=path,
                    origin=self.origin,
                    context=mark.reasoning,
                    timestamp=mark.timestamp,
                    mark_id=mark.mark_id,
                )

        # Also try tag prefix search
        marks = await self._persistence.get_marks(
            limit=1000,
            tag_prefix=f"spec:{path}",
        )

        for mark in marks:
            kind, targets = self._parse_tags(mark.tags)
            for target in targets:
                if target == path or path in target or target in path:
                    yield HyperEdge(
                        kind=kind,
                        source_path=mark.action or "unknown",
                        target_path=target,
                        origin=self.origin,
                        context=mark.reasoning,
                        timestamp=mark.timestamp,
                        mark_id=mark.mark_id,
                    )

    async def all_edges(self) -> AsyncIterator[HyperEdge]:
        """
        Get all edges from all marks.

        Yields:
            All HyperEdge instances from marks with spec/file tags
        """
        marks = await self._persistence.get_marks(limit=10000)

        for mark in marks:
            kind, targets = self._parse_tags(mark.tags)

            for target in targets:
                yield HyperEdge(
                    kind=kind,
                    source_path=mark.action or "unknown",
                    target_path=target,
                    origin=self.origin,
                    context=mark.reasoning,
                    timestamp=mark.timestamp,
                    mark_id=mark.mark_id,
                )

    async def search(self, query: str) -> AsyncIterator[HyperEdge]:
        """
        Search edges by query.

        Searches mark action, reasoning, and tags.

        Args:
            query: Search string (case-insensitive)

        Yields:
            Matching HyperEdge instances
        """
        query_lower = query.lower()
        marks = await self._persistence.get_marks(limit=10000)

        for mark in marks:
            # Check if query matches action, reasoning, or tags
            action_match = query_lower in (mark.action or "").lower()
            reasoning_match = query_lower in (mark.reasoning or "").lower()
            tag_match = any(query_lower in t.lower() for t in mark.tags)

            if action_match or reasoning_match or tag_match:
                kind, targets = self._parse_tags(mark.tags)

                # If no explicit targets, create an edge from action
                if not targets:
                    yield HyperEdge(
                        kind=kind,
                        source_path=mark.action or "unknown",
                        target_path="unknown",
                        origin=self.origin,
                        context=mark.reasoning,
                        timestamp=mark.timestamp,
                        mark_id=mark.mark_id,
                    )
                else:
                    for target in targets:
                        yield HyperEdge(
                            kind=kind,
                            source_path=mark.action or "unknown",
                            target_path=target,
                            origin=self.origin,
                            context=mark.reasoning,
                            timestamp=mark.timestamp,
                            mark_id=mark.mark_id,
                        )


__all__ = ["WitnessSource"]
