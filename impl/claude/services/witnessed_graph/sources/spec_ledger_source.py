"""
SpecLedgerSource: Adapts Living Spec Ledger to HyperEdge.

The Living Spec Ledger provides spec-to-spec relationships:
- Harmony: Specs that align/reinforce each other
- Contradiction: Specs that conflict
- References: Cross-references between specs

Design Principle:
    "Specs are nodes. Relations are edges. The ledger is the graph."

AD-015 (Upload-and-Copy):
    This source NO LONGER auto-computes. It requires pre-computed data.
    If no data exists, it gracefully returns empty results with a warning.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Callable

from ..composition import ComposableMixin
from ..types import EdgeKind, HyperEdge

if TYPE_CHECKING:
    from ...living_spec.analyzer import Contradiction, Harmony, LedgerReport, SpecRecord

logger = logging.getLogger(__name__)


class SpecLedgerSource(ComposableMixin):
    """
    Edge source from Living Spec Ledger.

    Converts Harmony/Contradiction/references to HyperEdge.

    Example:
        >>> from services.living_spec.ledger_node import ensure_scanned
        >>> report = await ensure_scanned()
        >>> source = SpecLedgerSource(report)
        >>> async for edge in source.edges_from("spec/principles.md"):
        ...     print(f"{edge.kind.name}: {edge.target_path}")
    """

    def __init__(
        self,
        report: "LedgerReport | None" = None,
        report_loader: Callable[[], Awaitable["LedgerReport"]] | None = None,
    ) -> None:
        """
        Create a SpecLedgerSource.

        Args:
            report: Pre-loaded LedgerReport (optional)
            report_loader: Async callable to load report on demand
        """
        self._report = report
        self._loader = report_loader

    async def _ensure_report(self) -> "LedgerReport | None":
        """
        Get the pre-computed report.

        AD-015: Does NOT auto-compute. Returns None if no data available.
        """
        if self._report is None:
            if self._loader:
                try:
                    self._report = await self._loader()
                except Exception as e:
                    logger.warning(f"Could not load spec ledger report: {e}")
                    return None
            else:
                # Try to import and use ensure_scanned
                try:
                    from ...living_spec.ledger_node import ensure_scanned

                    self._report = await ensure_scanned()
                except Exception as e:
                    # AD-015: No auto-compute, graceful degradation
                    logger.warning(
                        f"Spec ledger data not available: {e}. "
                        "Run `kg spec analyze` to pre-compute."
                    )
                    return None
        return self._report

    @property
    def origin(self) -> str:
        """Source identifier."""
        return "spec_ledger"

    def _harmony_to_edge(self, harmony: "Harmony") -> HyperEdge:
        """Convert Harmony to HyperEdge."""
        # Map relationship to edge kind
        relationship = harmony.relationship.lower()
        if relationship == "extends":
            kind = EdgeKind.EXTENDS
        elif relationship == "implements":
            kind = EdgeKind.IMPLEMENTS
        else:
            kind = EdgeKind.HARMONY

        return HyperEdge(
            kind=kind,
            source_path=harmony.spec_a,
            target_path=harmony.spec_b,
            origin=self.origin,
            confidence=harmony.strength,
            context=f"Harmony: {harmony.relationship}",
        )

    def _contradiction_to_edge(self, contradiction: "Contradiction") -> HyperEdge:
        """Convert Contradiction to HyperEdge."""
        return HyperEdge(
            kind=EdgeKind.CONTRADICTION,
            source_path=contradiction.spec_a,
            target_path=contradiction.spec_b,
            origin=self.origin,
            confidence=1.0 if contradiction.severity == "hard" else 0.5,
            context=f"{contradiction.severity}: {contradiction.conflict_type}",
        )

    def _reference_to_edge(self, source: str, target: str) -> HyperEdge:
        """Convert a spec reference to HyperEdge."""
        # Determine kind based on target path
        if target.startswith("impl/") or target.startswith("services/"):
            kind = EdgeKind.IMPLEMENTS
        elif "_tests/" in target or "test_" in target:
            kind = EdgeKind.EVIDENCE
        elif target.startswith("spec/"):
            kind = EdgeKind.DEPENDENCY
        else:
            kind = EdgeKind.REFERENCES

        return HyperEdge(
            kind=kind,
            source_path=source,
            target_path=target,
            origin=self.origin,
        )

    async def edges_from(self, path: str) -> AsyncIterator[HyperEdge]:
        """
        Get edges originating from a spec path.

        Returns harmonies, contradictions, and references from this spec.
        AD-015: Returns empty if no pre-computed data available.

        Args:
            path: Source spec path to query

        Yields:
            HyperEdge instances from spec relations
        """
        report = await self._ensure_report()
        if report is None:
            return  # AD-015: Graceful degradation

        # Harmonies where this spec is spec_a
        for harmony in report.harmonies:
            if harmony.spec_a == path:
                yield self._harmony_to_edge(harmony)

        # Contradictions where this spec is spec_a
        for contradiction in report.contradictions:
            if contradiction.spec_a == path:
                yield self._contradiction_to_edge(contradiction)

        # References from this spec
        for spec in report.specs:
            if spec.path == path:
                for ref in spec.references:
                    yield self._reference_to_edge(path, ref)
                for impl in spec.implementations:
                    yield self._reference_to_edge(path, impl)
                for test in spec.tests:
                    yield self._reference_to_edge(path, test)
                break

    async def edges_to(self, path: str) -> AsyncIterator[HyperEdge]:
        """
        Get edges pointing to a spec path.

        Returns harmonies and contradictions targeting this spec.
        AD-015: Returns empty if no pre-computed data available.

        Args:
            path: Target spec path

        Yields:
            HyperEdge instances pointing to path
        """
        report = await self._ensure_report()
        if report is None:
            return  # AD-015: Graceful degradation

        # Harmonies where this spec is spec_b
        for harmony in report.harmonies:
            if harmony.spec_b == path:
                yield self._harmony_to_edge(harmony)

        # Contradictions where this spec is spec_b
        for contradiction in report.contradictions:
            if contradiction.spec_b == path:
                yield self._contradiction_to_edge(contradiction)

        # References pointing to this path
        for spec in report.specs:
            if path in spec.references:
                yield self._reference_to_edge(spec.path, path)
            if path in spec.implementations:
                yield self._reference_to_edge(spec.path, path)
            if path in spec.tests:
                yield self._reference_to_edge(spec.path, path)

    async def all_edges(self) -> AsyncIterator[HyperEdge]:
        """
        Get all edges in the spec ledger.

        AD-015: Returns empty if no pre-computed data available.

        Yields:
            All HyperEdge instances from harmonies, contradictions, references
        """
        report = await self._ensure_report()
        if report is None:
            return  # AD-015: Graceful degradation

        # All harmonies
        for harmony in report.harmonies:
            yield self._harmony_to_edge(harmony)

        # All contradictions
        for contradiction in report.contradictions:
            yield self._contradiction_to_edge(contradiction)

        # All references
        for spec in report.specs:
            for ref in spec.references:
                yield self._reference_to_edge(spec.path, ref)
            for impl in spec.implementations:
                yield self._reference_to_edge(spec.path, impl)
            for test in spec.tests:
                yield self._reference_to_edge(spec.path, test)

    async def search(self, query: str) -> AsyncIterator[HyperEdge]:
        """
        Search edges by query.

        Searches spec paths and relationship contexts.
        AD-015: Returns empty if no pre-computed data available.

        Args:
            query: Search string (case-insensitive)

        Yields:
            Matching HyperEdge instances
        """
        query_lower = query.lower()
        async for edge in self.all_edges():  # AD-015: all_edges handles None
            if (
                query_lower in edge.source_path.lower()
                or query_lower in edge.target_path.lower()
                or (edge.context and query_lower in edge.context.lower())
            ):
                yield edge


__all__ = ["SpecLedgerSource"]
