"""
Teaching Moments Query API

A lightweight API for querying and verifying teaching moments (gotchas)
across the codebase. Builds on the existing extractor infrastructure.

AGENTESE: concept.docs.teaching

Usage:
    from services.living_docs import query_teaching, verify_evidence

    # Query all critical gotchas
    results = query_teaching(severity="critical")

    # Query by module pattern
    results = query_teaching(module_pattern="services.brain")

    # Verify all evidence links exist
    missing = verify_evidence()

Teaching:
    gotcha: Evidence paths are relative to impl/claude.
            (Evidence: test_teaching.py::test_evidence_path_resolution)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Literal

from .extractor import DocstringExtractor
from .generator import CATEGORIES, SPEC_CATEGORIES, CategoryConfig
from .spec_extractor import SpecExtractor
from .types import DocNode, TeachingMoment


@dataclass(frozen=True)
class TeachingResult:
    """
    A teaching moment with its source context.

    Includes the symbol and module where the moment was found,
    making it easy to navigate to the source.
    """

    moment: TeachingMoment
    symbol: str
    module: str
    source_path: str | None = None  # Path to source file if known


@dataclass
class TeachingQuery:
    """
    Query parameters for filtering teaching moments.

    All parameters are optional—omit to include all.
    """

    severity: Literal["critical", "warning", "info"] | None = None
    module_pattern: str | None = None  # Substring match on module path
    symbol_pattern: str | None = None  # Substring match on symbol name
    with_evidence: bool | None = None  # True = only with evidence, False = only without


@dataclass
class VerificationResult:
    """
    Result of evidence verification for a teaching moment.

    Tracks whether the evidence path (test file) exists.
    """

    result: TeachingResult
    evidence_exists: bool
    resolved_path: Path | None = None


@dataclass
class TeachingStats:
    """
    Statistics about teaching moments in the codebase.
    """

    total: int = 0
    by_severity: dict[str, int] = field(default_factory=dict)
    with_evidence: int = 0
    without_evidence: int = 0
    verified_evidence: int = 0  # Evidence files that exist


class TeachingCollector:
    """
    Collect and query teaching moments from the codebase.

    This is the workhorse class. For most uses, prefer the
    convenience functions: query_teaching(), verify_evidence().
    """

    def __init__(
        self,
        base_path: Path | None = None,
        extractor: DocstringExtractor | None = None,
        spec_extractor: SpecExtractor | None = None,
        include_specs: bool = True,
    ):
        self._base_path = base_path or Path(__file__).parent.parent.parent
        self._spec_base_path = self._base_path.parent.parent  # kgents root
        self._extractor = extractor or DocstringExtractor()
        self._spec_extractor = spec_extractor or SpecExtractor()
        self._include_specs = include_specs

    def collect_all(self) -> Iterator[TeachingResult]:
        """
        Collect all teaching moments from the codebase.

        Yields TeachingResult for each moment found.
        """
        # Collect from implementation categories
        for category in CATEGORIES:
            yield from self._collect_from_category(category)

        # Collect from spec categories if enabled
        if self._include_specs:
            yield from self._collect_from_specs()

    def _collect_from_category(self, category: CategoryConfig) -> Iterator[TeachingResult]:
        """Collect teaching moments from a single category."""
        for path_str in category.paths:
            path = self._base_path / path_str
            if not path.exists():
                continue

            for py_file in path.glob("**/*.py"):
                if not self._extractor.should_extract(py_file):
                    continue

                try:
                    # Module docstring
                    mod_node = self._extractor.extract_module_docstring(py_file)
                    if mod_node:
                        yield from self._node_to_results(mod_node, str(py_file))

                    # Symbol docstrings
                    nodes = self._extractor.extract_file(py_file)
                    for node in nodes:
                        yield from self._node_to_results(node, str(py_file))
                except Exception:
                    continue

    def _collect_from_specs(self) -> Iterator[TeachingResult]:
        """Collect teaching moments from spec markdown files."""
        for category in SPEC_CATEGORIES:
            for path_str in category.paths:
                path = self._spec_base_path / path_str
                if not path.exists():
                    continue

                if path.is_file() and path.suffix == ".md":
                    yield from self._collect_from_spec_file(path)
                else:
                    for md_file in path.glob("**/*.md"):
                        if self._spec_extractor.should_extract(md_file):
                            yield from self._collect_from_spec_file(md_file)

    def _collect_from_spec_file(self, path: Path) -> Iterator[TeachingResult]:
        """Collect teaching moments from a single spec file."""
        try:
            nodes = self._spec_extractor.extract_file(path)
            for node in nodes:
                yield from self._node_to_results(node, str(path))
        except Exception:
            pass

    def _node_to_results(self, node: DocNode, source_path: str) -> Iterator[TeachingResult]:
        """Convert a DocNode's teaching moments to TeachingResults."""
        for moment in node.teaching:
            yield TeachingResult(
                moment=moment,
                symbol=node.symbol,
                module=node.module,
                source_path=source_path,
            )

    def query(self, query: TeachingQuery) -> list[TeachingResult]:
        """
        Query teaching moments with filters.

        Args:
            query: Filter parameters

        Returns:
            List of matching TeachingResults
        """
        results: list[TeachingResult] = []

        for result in self.collect_all():
            # Apply filters
            if query.severity and result.moment.severity != query.severity:
                continue
            if query.module_pattern and query.module_pattern not in result.module:
                continue
            if query.symbol_pattern and query.symbol_pattern not in result.symbol:
                continue
            if query.with_evidence is True and not result.moment.evidence:
                continue
            if query.with_evidence is False and result.moment.evidence:
                continue

            results.append(result)

        return results

    def verify_evidence(self) -> list[VerificationResult]:
        """
        Verify that all evidence paths exist.

        Returns list of VerificationResults for moments WITH evidence.
        Moments without evidence are excluded.
        """
        results: list[VerificationResult] = []

        for teaching_result in self.collect_all():
            if not teaching_result.moment.evidence:
                continue

            # Parse evidence path: test_file.py::test_name
            evidence = teaching_result.moment.evidence
            test_file = evidence.split("::")[0] if "::" in evidence else evidence

            # Try to resolve the path
            resolved = self._resolve_evidence_path(test_file)
            exists = resolved is not None and resolved.exists()

            results.append(
                VerificationResult(
                    result=teaching_result,
                    evidence_exists=exists,
                    resolved_path=resolved if exists else None,
                )
            )

        return results

    def _resolve_evidence_path(self, test_file: str) -> Path | None:
        """
        Resolve a test file name to a path.

        Searches common test locations:
        - _tests/ subdirectory of module
        - tests/ at impl/claude level
        """
        # Search patterns
        search_patterns = [
            f"**/_tests/{test_file}",
            f"**/{test_file}",
            f"**/tests/{test_file}",
        ]

        for pattern in search_patterns:
            matches = list(self._base_path.glob(pattern))
            if matches:
                return matches[0]

        return None

    def get_stats(self) -> TeachingStats:
        """
        Get statistics about teaching moments.
        """
        stats = TeachingStats()
        stats.by_severity = {"critical": 0, "warning": 0, "info": 0}

        verification_results = self.verify_evidence()
        verified_set = {r.result.moment.insight for r in verification_results if r.evidence_exists}

        for result in self.collect_all():
            stats.total += 1
            stats.by_severity[result.moment.severity] = (
                stats.by_severity.get(result.moment.severity, 0) + 1
            )
            if result.moment.evidence:
                stats.with_evidence += 1
                if result.moment.insight in verified_set:
                    stats.verified_evidence += 1
            else:
                stats.without_evidence += 1

        return stats


# ============================================================================
# Convenience Functions (Preferred API)
# ============================================================================


def query_teaching(
    severity: Literal["critical", "warning", "info"] | None = None,
    module_pattern: str | None = None,
    symbol_pattern: str | None = None,
    with_evidence: bool | None = None,
) -> list[TeachingResult]:
    """
    Query teaching moments with optional filters.

    Args:
        severity: Filter by severity level
        module_pattern: Substring match on module path
        symbol_pattern: Substring match on symbol name
        with_evidence: True = only with evidence, False = only without

    Returns:
        List of matching teaching moments with context

    Usage:
        # All critical gotchas
        critical = query_teaching(severity="critical")

        # Brain service gotchas
        brain_gotchas = query_teaching(module_pattern="services.brain")

        # Gotchas missing evidence
        undocumented = query_teaching(with_evidence=False)
    """
    collector = TeachingCollector()
    query = TeachingQuery(
        severity=severity,
        module_pattern=module_pattern,
        symbol_pattern=symbol_pattern,
        with_evidence=with_evidence,
    )
    return collector.query(query)


def verify_evidence() -> list[VerificationResult]:
    """
    Verify that all evidence paths exist.

    Returns list of VerificationResults for moments WITH evidence.

    Usage:
        missing = [v for v in verify_evidence() if not v.evidence_exists]
        if missing:
            print(f"⚠️ {len(missing)} teaching moments have broken evidence links")
    """
    collector = TeachingCollector()
    return collector.verify_evidence()


def get_teaching_stats() -> TeachingStats:
    """
    Get statistics about teaching moments in the codebase.

    Returns:
        TeachingStats with counts by severity and evidence status
    """
    collector = TeachingCollector()
    return collector.get_stats()
