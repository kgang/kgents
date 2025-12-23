"""
WitnessedGraph Protocol: Common interface for edge sources.

This module defines the EdgeSourceProtocol that all edge sources must implement:
- edges_from: Get edges originating from a path
- edges_to: Get edges pointing to a path
- all_edges: Get all edges in the source
- search: Search edges by query

Design Principle:
    "The protocol is the contract. Composition is possible because
    all sources speak the same language."

Category Theory Perspective:
    EdgeSourceProtocol is a functor from Paths to AsyncIterators of HyperEdges.
    Composition (>>) creates product functors.

Teaching:
    gotcha: All methods are async generators. Use `async for` to iterate.
            Don't forget to handle empty results gracefully.

    gotcha: The `origin` property is a discriminator. It must be unique
            per source type to enable filtering by origin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .types import HyperEdge


# =============================================================================
# EdgeSourceProtocol
# =============================================================================


@runtime_checkable
class EdgeSourceProtocol(Protocol):
    """
    Common interface for all edge providers.

    Every edge source (Sovereign, Witness, SpecLedger) implements this protocol.
    This enables composition via the >> operator.

    Properties:
        origin: Unique identifier for this source type

    Methods:
        edges_from: Get edges originating from a path
        edges_to: Get edges pointing to a path
        all_edges: Get all edges in this source
        search: Search edges by query string

    Example:
        >>> async for edge in source.edges_from("spec/agents/d-gent.md"):
        ...     print(edge)
    """

    @property
    def origin(self) -> str:
        """
        Unique identifier for this source.

        Used for:
        - Filtering edges by origin
        - Debugging/tracing edge provenance
        - Composing source names (e.g., "sovereign+witness")
        """
        ...

    def edges_from(self, path: str) -> AsyncIterator["HyperEdge"]:
        """
        Get edges originating from a path.

        Args:
            path: The source path to query (e.g., "impl/claude/services/brain/persistence.py")

        Yields:
            HyperEdge instances where source_path matches or contains path

        Example:
            >>> async for edge in source.edges_from("spec/agents/flux.md"):
            ...     print(f"{edge.kind.name}: {edge.target_path}")
        """
        ...

    def edges_to(self, path: str) -> AsyncIterator["HyperEdge"]:
        """
        Get edges pointing to a path.

        Args:
            path: The target path to query

        Yields:
            HyperEdge instances where target_path matches or contains path

        Example:
            >>> # Find all evidence for a spec
            >>> async for edge in source.edges_to("spec/protocols/k-block.md"):
            ...     if edge.kind == EdgeKind.EVIDENCE:
            ...         print(f"Evidence from: {edge.source_path}")
        """
        ...

    def all_edges(self) -> AsyncIterator["HyperEdge"]:
        """
        Get all edges in this source.

        Use sparingly - can be expensive for large sources.

        Yields:
            All HyperEdge instances in this source
        """
        ...

    def search(self, query: str) -> AsyncIterator["HyperEdge"]:
        """
        Search edges by query string.

        Searches across:
        - source_path
        - target_path
        - context (if available)

        Args:
            query: Search string (case-insensitive substring match)

        Yields:
            HyperEdge instances matching the query
        """
        ...


# =============================================================================
# Type Helpers
# =============================================================================


def is_edge_source(obj: object) -> bool:
    """Check if object implements EdgeSourceProtocol."""
    return isinstance(obj, EdgeSourceProtocol)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "EdgeSourceProtocol",
    "is_edge_source",
]
