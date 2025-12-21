"""
Tests for Teaching Moments Query API

Tests the teaching module's query and verification capabilities.

Note: Tests that scan the entire codebase are marked @pytest.mark.slow.
Run fast tests only: pytest -m "not slow"
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ..teaching import (
    TeachingCollector,
    TeachingQuery,
    TeachingResult,
    TeachingStats,
    VerificationResult,
    get_teaching_stats,
    query_teaching,
    verify_evidence,
)
from ..types import TeachingMoment


class TestTeachingResult:
    """Tests for TeachingResult dataclass."""

    def test_creation(self) -> None:
        """TeachingResult can be created with all fields."""
        moment = TeachingMoment(
            insight="Test insight",
            severity="warning",
            evidence="test_file.py::test_name",
        )
        result = TeachingResult(
            moment=moment,
            symbol="test_func",
            module="services.test",
            source_path="/path/to/file.py",
        )

        assert result.moment.insight == "Test insight"
        assert result.symbol == "test_func"
        assert result.module == "services.test"
        assert result.source_path == "/path/to/file.py"

    def test_optional_source_path(self) -> None:
        """source_path is optional."""
        moment = TeachingMoment(insight="Test", severity="info")
        result = TeachingResult(moment=moment, symbol="test", module="test")

        assert result.source_path is None


class TestTeachingQuery:
    """Tests for TeachingQuery dataclass."""

    def test_default_query(self) -> None:
        """Default query has all None filters."""
        query = TeachingQuery()

        assert query.severity is None
        assert query.module_pattern is None
        assert query.symbol_pattern is None
        assert query.with_evidence is None

    def test_specific_query(self) -> None:
        """Query can specify filters."""
        query = TeachingQuery(
            severity="critical",
            module_pattern="brain",
            with_evidence=True,
        )

        assert query.severity == "critical"
        assert query.module_pattern == "brain"
        assert query.with_evidence is True


@pytest.mark.slow
class TestTeachingCollector:
    """Tests for TeachingCollector class (scans entire codebase)."""

    @pytest.fixture
    def collector(self) -> TeachingCollector:
        """Provide a collector instance."""
        return TeachingCollector()

    def test_collect_all_returns_iterator(self, collector: TeachingCollector) -> None:
        """collect_all returns an iterator."""
        results = collector.collect_all()
        # Should be iterable
        assert hasattr(results, "__iter__")

    def test_collect_all_yields_teaching_results(self, collector: TeachingCollector) -> None:
        """collect_all yields TeachingResult instances."""
        # Collect first few results
        results = list(collector.collect_all())

        # Should have at least some teaching moments (from living_docs itself)
        # The living_docs module has several gotcha: annotations
        assert len(results) > 0

        # All should be TeachingResult
        for result in results[:5]:
            assert isinstance(result, TeachingResult)
            assert isinstance(result.moment, TeachingMoment)
            assert isinstance(result.symbol, str)
            assert isinstance(result.module, str)

    def test_query_by_severity(self, collector: TeachingCollector) -> None:
        """Query can filter by severity."""
        query = TeachingQuery(severity="critical")
        results = collector.query(query)

        # All results should be critical severity
        for result in results:
            assert result.moment.severity == "critical"

    def test_query_by_module_pattern(self, collector: TeachingCollector) -> None:
        """Query can filter by module pattern."""
        query = TeachingQuery(module_pattern="living_docs")
        results = collector.query(query)

        # Should find at least the living_docs module's own gotchas
        assert len(results) > 0

        # All should match the pattern
        for result in results:
            assert "living_docs" in result.module

    def test_query_with_evidence_filter(self, collector: TeachingCollector) -> None:
        """Query can filter by evidence presence."""
        # Only with evidence
        with_evidence = collector.query(TeachingQuery(with_evidence=True))
        for result in with_evidence:
            assert result.moment.evidence is not None

        # Only without evidence
        without_evidence = collector.query(TeachingQuery(with_evidence=False))
        for result in without_evidence:
            assert result.moment.evidence is None

    def test_verify_evidence_returns_list(self, collector: TeachingCollector) -> None:
        """verify_evidence returns a list of VerificationResults."""
        results = collector.verify_evidence()

        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, VerificationResult)
            assert isinstance(result.result, TeachingResult)
            assert isinstance(result.evidence_exists, bool)

    def test_verify_evidence_only_checks_moments_with_evidence(
        self, collector: TeachingCollector
    ) -> None:
        """verify_evidence only includes moments WITH evidence."""
        results = collector.verify_evidence()

        for result in results:
            assert result.result.moment.evidence is not None

    def test_get_stats_returns_stats(self, collector: TeachingCollector) -> None:
        """get_stats returns TeachingStats."""
        stats = collector.get_stats()

        assert isinstance(stats, TeachingStats)
        assert stats.total > 0
        assert "critical" in stats.by_severity
        assert "warning" in stats.by_severity
        assert "info" in stats.by_severity


@pytest.mark.slow
class TestEvidenceResolution:
    """Tests for evidence path resolution (scans entire codebase)."""

    def test_evidence_path_resolution(self) -> None:
        """
        Evidence paths are resolved relative to impl/claude.

        Teaching:
            gotcha: Evidence paths are relative to impl/claude.
                    (Evidence: test_teaching.py::test_evidence_path_resolution)
        """
        collector = TeachingCollector()

        # The living_docs module has evidence links we can verify
        results = collector.verify_evidence()

        # Find a result for living_docs module
        living_docs_results = [r for r in results if "living_docs" in r.result.module]

        # Should have at least one verified evidence link
        verified = [r for r in living_docs_results if r.evidence_exists]
        assert len(verified) > 0, "At least one living_docs evidence link should exist"

    def test_resolved_path_is_path_object(self) -> None:
        """resolved_path is a Path object when evidence exists."""
        collector = TeachingCollector()
        results = collector.verify_evidence()

        # Find one where evidence exists
        existing = [r for r in results if r.evidence_exists]
        if existing:
            assert isinstance(existing[0].resolved_path, Path)


@pytest.mark.slow
class TestConvenienceFunctions:
    """Tests for convenience functions (scan entire codebase)."""

    def test_query_teaching_all(self) -> None:
        """query_teaching() with no args returns all moments."""
        results = query_teaching()

        assert len(results) > 0
        for result in results:
            assert isinstance(result, TeachingResult)

    def test_query_teaching_by_severity(self) -> None:
        """query_teaching(severity=...) filters correctly."""
        results = query_teaching(severity="warning")

        for result in results:
            assert result.moment.severity == "warning"

    def test_query_teaching_by_module(self) -> None:
        """query_teaching(module_pattern=...) filters correctly."""
        results = query_teaching(module_pattern="living_docs")

        assert len(results) > 0
        for result in results:
            assert "living_docs" in result.module

    def test_verify_evidence_function(self) -> None:
        """verify_evidence() convenience function works."""
        results = verify_evidence()

        assert isinstance(results, list)
        # Should have results (living_docs has evidence links)
        assert len(results) > 0

    def test_get_teaching_stats_function(self) -> None:
        """get_teaching_stats() convenience function works."""
        stats = get_teaching_stats()

        assert isinstance(stats, TeachingStats)
        assert stats.total > 0
        assert stats.with_evidence + stats.without_evidence == stats.total


class TestTeachingStats:
    """Tests for TeachingStats dataclass."""

    def test_default_stats(self) -> None:
        """Default stats are zeroes."""
        stats = TeachingStats()

        assert stats.total == 0
        assert stats.by_severity == {}
        assert stats.with_evidence == 0
        assert stats.without_evidence == 0
        assert stats.verified_evidence == 0

    @pytest.mark.slow
    def test_stats_from_codebase(self) -> None:
        """Stats from actual codebase are sensible (scans entire codebase)."""
        stats = get_teaching_stats()

        # Total should equal sum of severities
        severity_sum = sum(stats.by_severity.values())
        assert stats.total == severity_sum

        # with + without should equal total
        assert stats.with_evidence + stats.without_evidence == stats.total

        # verified should be <= with_evidence
        assert stats.verified_evidence <= stats.with_evidence


@pytest.mark.slow
@pytest.mark.integration
class TestIntegration:
    """Integration tests for teaching module (scan entire codebase)."""

    def test_find_missing_evidence(self) -> None:
        """Can identify teaching moments with broken evidence links."""
        results = verify_evidence()
        missing = [r for r in results if not r.evidence_exists]

        # We don't assert on count, but we verify the query works
        # If there are missing links, they should have evidence strings
        for result in missing:
            assert result.result.moment.evidence is not None
            assert result.evidence_exists is False
            assert result.resolved_path is None

    def test_combined_filters(self) -> None:
        """Multiple filters combine correctly."""
        results = query_teaching(
            severity="warning",
            module_pattern="services",
        )

        for result in results:
            assert result.moment.severity == "warning"
            assert "services" in result.module
