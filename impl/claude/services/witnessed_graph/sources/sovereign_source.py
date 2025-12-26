"""
SovereignSource: Adapts Sovereign edges to HyperEdge.

Sovereign provides code structure edges from ingested files:
- IMPORTS: File imports another
- REFERENCES: Links to other files/specs
- IMPLEMENTS: Code implements spec
- EXTENDS: Spec extends another

Design Principle:
    "Every ingested file has structure. Sovereign discovers it."
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from ..composition import ComposableMixin
from ..types import EdgeKind, HyperEdge

if TYPE_CHECKING:
    from ...sovereign import SovereignStore


class SovereignSource(ComposableMixin):
    """
    Edge source from Sovereign code structure analysis.

    Wraps SovereignStore and converts DiscoveredEdge to HyperEdge.

    Example:
        >>> store = SovereignStore(base_dir)
        >>> source = SovereignSource(store)
        >>> async for edge in source.edges_from("impl/claude/services/brain/persistence.py"):
        ...     print(f"{edge.kind.name}: {edge.target_path}")
    """

    def __init__(self, store: "SovereignStore") -> None:
        """
        Create a SovereignSource from a SovereignStore.

        Args:
            store: The SovereignStore instance
        """
        self._store = store

    @property
    def origin(self) -> str:
        """Source identifier."""
        return "sovereign"

    async def edges_from(self, path: str) -> AsyncIterator[HyperEdge]:
        """
        Get edges originating from a path.

        Looks up the entity in the store and converts its edges.
        Also reads overlay edges created via store.add_edge().

        Args:
            path: Source path to query

        Yields:
            HyperEdge instances from Sovereign analysis and overlay
        """
        seen_edge_ids: set[str] = set()

        # 1. Get edges from entity (discovered code structure)
        entity = await self._store.get_current(path)
        if entity is not None:
            for edge_dict in entity.edges:
                edge_type = edge_dict.get("edge_type", "references")
                target = edge_dict.get("target", "")
                line_number = edge_dict.get("line_number")
                context = edge_dict.get("context", "")

                if not target:
                    continue

                edge_id = edge_dict.get("id", f"{path}->{target}")
                seen_edge_ids.add(edge_id)

                yield HyperEdge(
                    kind=EdgeKind.from_sovereign_type(edge_type),
                    source_path=path,
                    target_path=target,
                    origin=self.origin,
                    context=context if context else None,
                    line_number=line_number,
                )

        # 2. Get edges from overlay (manually added via store.add_edge())
        overlay = await self._store.get_overlay(path, "edges")
        if overlay is not None:
            overlay_edges = overlay.get("edges", [])
            for edge_dict in overlay_edges:
                # Only outgoing edges from this path
                if edge_dict.get("direction") != "outgoing":
                    continue

                edge_id = edge_dict.get("id", "")
                if edge_id in seen_edge_ids:
                    continue
                seen_edge_ids.add(edge_id)

                edge_type = edge_dict.get("type", "references")
                target = edge_dict.get("target", "")
                context = edge_dict.get("context", "")
                mark_id = edge_dict.get("mark_id")

                if not target:
                    continue

                yield HyperEdge(
                    kind=EdgeKind.from_sovereign_type(edge_type),
                    source_path=path,
                    target_path=target,
                    origin=self.origin,
                    context=context if context else None,
                    mark_id=mark_id,
                )

    async def edges_to(self, path: str) -> AsyncIterator[HyperEdge]:
        """
        Get edges pointing to a path.

        Scans all entities looking for edges targeting this path.
        Also reads incoming overlay edges.

        Args:
            path: Target path to find edges to

        Yields:
            HyperEdge instances pointing to path
        """
        seen_edge_ids: set[str] = set()

        # 1. Get incoming edges from overlay (direct lookup - fast)
        overlay = await self._store.get_overlay(path, "edges")
        if overlay is not None:
            overlay_edges = overlay.get("edges", [])
            for edge_dict in overlay_edges:
                # Only incoming edges to this path
                if edge_dict.get("direction") != "incoming":
                    continue

                edge_id = edge_dict.get("id", "")
                if edge_id in seen_edge_ids:
                    continue
                seen_edge_ids.add(edge_id)

                edge_type = edge_dict.get("type", "references")
                source = edge_dict.get("source", "")
                context = edge_dict.get("context", "")
                mark_id = edge_dict.get("mark_id")

                if not source:
                    continue

                yield HyperEdge(
                    kind=EdgeKind.from_sovereign_type(edge_type),
                    source_path=source,
                    target_path=path,
                    origin=self.origin,
                    context=context if context else None,
                    mark_id=mark_id,
                )

        # 2. List all entities and check their edges (discovered code structure)
        all_paths = await self._store.list_all()
        for entity_path in all_paths:
            entity = await self._store.get_current(entity_path)
            if entity is None:
                continue

            for edge_dict in entity.edges:
                target = edge_dict.get("target", "")
                # Check if target matches (exact or prefix match)
                if target == path or target.endswith(f"/{path}") or path.endswith(target):
                    edge_id = edge_dict.get("id", f"{entity_path}->{target}")
                    if edge_id in seen_edge_ids:
                        continue
                    seen_edge_ids.add(edge_id)

                    edge_type = edge_dict.get("edge_type", "references")
                    line_number = edge_dict.get("line_number")
                    context = edge_dict.get("context", "")

                    yield HyperEdge(
                        kind=EdgeKind.from_sovereign_type(edge_type),
                        source_path=entity_path,
                        target_path=target,
                        origin=self.origin,
                        context=context if context else None,
                        line_number=line_number,
                    )

    async def all_edges(self) -> AsyncIterator[HyperEdge]:
        """
        Get all edges in Sovereign.

        Iterates all entities and yields all their edges.

        Yields:
            All HyperEdge instances from Sovereign
        """
        all_paths = await self._store.list_all()
        for path in all_paths:
            async for edge in self.edges_from(path):
                yield edge

    async def search(self, query: str) -> AsyncIterator[HyperEdge]:
        """
        Search edges by query.

        Searches path and context fields.

        Args:
            query: Search string (case-insensitive)

        Yields:
            Matching HyperEdge instances
        """
        query_lower = query.lower()
        async for edge in self.all_edges():
            # Search in paths and context
            if (
                query_lower in edge.source_path.lower()
                or query_lower in edge.target_path.lower()
                or (edge.context and query_lower in edge.context.lower())
            ):
                yield edge


__all__ = ["SovereignSource"]
