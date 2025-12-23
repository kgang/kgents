"""
WitnessedGraph Composition: The >> operator for edge sources.

This module provides composition primitives:
- IdentitySource: The identity element (returns no edges)
- ComposedSource: Multiple sources acting as one
- compose(): Functional composition helper

Category Laws (verified by tests):
    Identity:      Id >> f == f == f >> Id
    Associativity: (a >> b) >> c == a >> (b >> c)

Design Principle:
    "Sources are morphisms. Composition is the operation.
    The graph is the category."

Usage:
    >>> sovereign = SovereignSource(store)
    >>> witness = WitnessSource(persistence)
    >>> spec = SpecLedgerSource(ledger)
    >>>
    >>> # Compose all sources
    >>> graph = sovereign >> witness >> spec
    >>>
    >>> # Query the unified graph
    >>> async for edge in graph.edges_from("spec/agents/d-gent.md"):
    ...     print(edge)

Teaching:
    gotcha: ComposedSource preserves order. First source's edges come first.
            This matters when you want predictable iteration order.

    gotcha: The >> operator creates a NEW ComposedSource. Sources are immutable.
            Original sources are not modified.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from .protocol import EdgeSourceProtocol

if TYPE_CHECKING:
    from .types import HyperEdge


# =============================================================================
# IdentitySource: The Category Identity Element
# =============================================================================


class IdentitySource:
    """
    Identity element for edge source composition.

    Properties:
        Id >> f == f (left identity)
        f >> Id == f (right identity)

    Returns no edges for any query. Useful for:
    - Default/fallback source
    - Testing composition laws
    - Building up sources incrementally
    """

    @property
    def origin(self) -> str:
        """Identity has no origin."""
        return "identity"

    async def edges_from(self, path: str) -> AsyncIterator["HyperEdge"]:
        """Returns empty iterator."""
        return
        yield  # Makes this an async generator

    async def edges_to(self, path: str) -> AsyncIterator["HyperEdge"]:
        """Returns empty iterator."""
        return
        yield

    async def all_edges(self) -> AsyncIterator["HyperEdge"]:
        """Returns empty iterator."""
        return
        yield

    async def search(self, query: str) -> AsyncIterator["HyperEdge"]:
        """Returns empty iterator."""
        return
        yield

    def __rshift__(self, other: EdgeSourceProtocol) -> "ComposedSource":
        """Id >> f returns f (wrapped in ComposedSource for consistency)."""
        if isinstance(other, IdentitySource):
            return ComposedSource([])
        if isinstance(other, ComposedSource):
            return other
        return ComposedSource([other])


# =============================================================================
# ComposedSource: The Product of Edge Sources
# =============================================================================


class ComposedSource:
    """
    Multiple edge sources acting as one.

    Composition creates a product: all sources' edges are yielded in order.
    This is the heart of the WitnessedGraph composition system.

    Properties:
        - Sources are stored in order
        - Queries are fan-out: each source is queried, results concatenated
        - Origin is joined: "sovereign+witness+spec_ledger"

    Category Laws:
        - Associativity: (a >> b) >> c produces same edges as a >> (b >> c)
        - Identity: Id >> a == a == a >> Id

    Example:
        >>> composed = sovereign >> witness
        >>> composed.origin  # "sovereign+witness"
        >>> async for edge in composed.edges_from("foo.py"):
        ...     # Yields sovereign edges first, then witness edges
    """

    def __init__(self, sources: list[EdgeSourceProtocol]) -> None:
        """
        Create a composed source from a list of sources.

        Args:
            sources: List of edge sources (order preserved)
        """
        # Flatten nested ComposedSources for associativity
        self._sources: list[EdgeSourceProtocol] = []
        for source in sources:
            if isinstance(source, ComposedSource):
                self._sources.extend(source._sources)
            elif not isinstance(source, IdentitySource):
                self._sources.append(source)

    @property
    def sources(self) -> list[EdgeSourceProtocol]:
        """The list of sources in this composition."""
        return list(self._sources)

    @property
    def origin(self) -> str:
        """Combined origin of all sources."""
        if not self._sources:
            return "empty"
        return "+".join(s.origin for s in self._sources)

    async def edges_from(self, path: str) -> AsyncIterator["HyperEdge"]:
        """
        Get edges from all sources, in order.

        Args:
            path: Source path to query

        Yields:
            HyperEdges from each source in order
        """
        for source in self._sources:
            async for edge in source.edges_from(path):
                yield edge

    async def edges_to(self, path: str) -> AsyncIterator["HyperEdge"]:
        """
        Get edges to a target from all sources, in order.

        Args:
            path: Target path to query

        Yields:
            HyperEdges from each source in order
        """
        for source in self._sources:
            async for edge in source.edges_to(path):
                yield edge

    async def all_edges(self) -> AsyncIterator["HyperEdge"]:
        """
        Get all edges from all sources.

        Use sparingly - can be very expensive.

        Yields:
            All HyperEdges from all sources
        """
        for source in self._sources:
            async for edge in source.all_edges():
                yield edge

    async def search(self, query: str) -> AsyncIterator["HyperEdge"]:
        """
        Search all sources for edges matching query.

        Args:
            query: Search string

        Yields:
            Matching HyperEdges from all sources
        """
        for source in self._sources:
            async for edge in source.search(query):
                yield edge

    def __rshift__(self, other: EdgeSourceProtocol) -> "ComposedSource":
        """
        Compose this source with another: self >> other.

        Category Law: Associativity holds.
            (a >> b) >> c produces same results as a >> (b >> c)

        Args:
            other: Another edge source to compose

        Returns:
            New ComposedSource containing all sources
        """
        if isinstance(other, IdentitySource):
            return self
        if isinstance(other, ComposedSource):
            return ComposedSource(self._sources + other._sources)
        return ComposedSource(self._sources + [other])

    def __len__(self) -> int:
        """Number of sources in this composition."""
        return len(self._sources)

    def __repr__(self) -> str:
        """Debug representation."""
        origins = [s.origin for s in self._sources]
        return f"ComposedSource([{', '.join(origins)}])"


# =============================================================================
# Composition Helpers
# =============================================================================


def compose(*sources: EdgeSourceProtocol) -> ComposedSource:
    """
    Compose multiple edge sources into one.

    Functional alternative to >> operator.

    Args:
        *sources: Edge sources to compose

    Returns:
        ComposedSource containing all sources

    Example:
        >>> graph = compose(sovereign, witness, spec_ledger)
        >>> # Equivalent to: sovereign >> witness >> spec_ledger
    """
    return ComposedSource(list(sources))


def identity() -> IdentitySource:
    """
    Create an identity source.

    Returns:
        IdentitySource instance
    """
    return IdentitySource()


# =============================================================================
# Mixin for EdgeSourceProtocol Implementations
# =============================================================================


class ComposableMixin:
    """
    Mixin that adds >> operator to any EdgeSourceProtocol implementation.

    Usage:
        class MySource(ComposableMixin):
            @property
            def origin(self) -> str:
                return "my_source"

            async def edges_from(self, path: str) -> AsyncIterator[HyperEdge]:
                ...
    """

    def __rshift__(self, other: EdgeSourceProtocol) -> ComposedSource:
        """Compose: self >> other."""
        self_source: EdgeSourceProtocol = self  # type: ignore[assignment]
        if isinstance(other, IdentitySource):
            return ComposedSource([self_source])
        if isinstance(other, ComposedSource):
            return ComposedSource([self_source] + other._sources)
        return ComposedSource([self_source, other])


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "IdentitySource",
    "ComposedSource",
    "ComposableMixin",
    "compose",
    "identity",
]
