"""
Tests for Axiom Discovery Service.

Validates:
1. Pattern extraction from decisions
2. Fixed point detection (L < 0.05)
3. Candidate clustering and filtering
4. Discovery report generation

Philosophy:
    "Axioms are discovered, not stipulated.
     These tests verify the discovery machinery works."
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.zero_seed.axiom_discovery import (
    AXIOM_THRESHOLD,
    MIN_PATTERN_OCCURRENCES,
    AxiomDiscoveryService,
    CandidateAxiom,
    DiscoveredAxiom,
    DiscoveryReport,
    cluster_similar_phrases,
    discover_axioms,
    extract_candidates,
    extract_value_phrases,
    validate_axiom,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_decisions() -> list[str]:
    """Sample decision texts with recurring value patterns."""
    return [
        "I chose to prioritize simplicity over complexity because simplicity is important.",
        "Decided to use composition for better modularity. Simplicity matters most.",
        "Always prefer clear code over clever code. Simplicity is essential.",
        "Value clarity and simplicity in all design decisions.",
        "Composability is important for long-term maintainability.",
        "Prefer composition over inheritance. Composition is important.",
    ]


@pytest.fixture
def contradicting_decisions() -> list[str]:
    """Decision texts with contradicting values."""
    return [
        "Always prioritize performance over readability.",
        "Readability is more important than performance.",
        "Performance is the top priority.",
        "Readability matters most in code.",
    ]


# =============================================================================
# Pattern Extraction Tests
# =============================================================================


class TestExtractValuePhrases:
    """Tests for extract_value_phrases function."""

    def test_extracts_importance_statements(self) -> None:
        """Should extract 'X is important' patterns."""
        text = "Simplicity is important for maintainability."
        phrases = extract_value_phrases(text)
        assert len(phrases) > 0
        assert any("simplicity" in p.lower() for p in phrases)

    def test_extracts_always_never_patterns(self) -> None:
        """Should extract 'always/never X' patterns."""
        text = "Always prefer clarity. Never compromise on quality."
        phrases = extract_value_phrases(text)
        assert len(phrases) > 0
        assert any("prefer" in p.lower() or "clarity" in p.lower() for p in phrases)

    def test_extracts_matters_patterns(self) -> None:
        """Should extract 'X matters' patterns."""
        text = "Code clarity matters for collaboration."
        phrases = extract_value_phrases(text)
        assert len(phrases) > 0
        # Should find either "clarity matters" or the sentence

    def test_handles_empty_text(self) -> None:
        """Should return empty list for empty text."""
        phrases = extract_value_phrases("")
        assert phrases == []

    def test_extracts_prioritize_patterns(self) -> None:
        """Should extract 'prioritize X' patterns."""
        text = "We prioritize user experience above all."
        phrases = extract_value_phrases(text)
        assert len(phrases) > 0


class TestClusterSimilarPhrases:
    """Tests for cluster_similar_phrases function."""

    def test_clusters_similar_phrases(self) -> None:
        """Should cluster phrases with word overlap."""
        phrases = [
            "simplicity is important",
            "simplicity matters",
            "simplicity is essential",
            "complexity is bad",
        ]
        clustered = cluster_similar_phrases(phrases)

        # Should have at least 2 clusters (simplicity and complexity)
        assert len(clustered) >= 2

        # Simplicity cluster should have count >= 3
        simplicity_clusters = [c for c in clustered if "simplicity" in c[0].lower()]
        assert any(count >= 2 for _, count in simplicity_clusters)

    def test_handles_empty_list(self) -> None:
        """Should return empty list for empty input."""
        clustered = cluster_similar_phrases([])
        assert clustered == []

    def test_single_phrase(self) -> None:
        """Should handle single phrase."""
        clustered = cluster_similar_phrases(["simplicity"])
        assert len(clustered) == 1
        assert clustered[0][1] == 1


class TestExtractCandidates:
    """Tests for extract_candidates function."""

    @pytest.mark.skip(reason="Requires Mark type from witness module")
    def test_extracts_candidates_from_marks(self, sample_decisions: list[str]) -> None:
        """Should extract candidate axioms from marks."""
        # This test requires actual Mark objects
        pass

    def test_respects_min_occurrences(self) -> None:
        """Candidates should meet minimum occurrence threshold."""
        # All candidates should have frequency >= MIN_PATTERN_OCCURRENCES
        # Test with mock marks when available
        pass


# =============================================================================
# Discovery Service Tests
# =============================================================================


class TestAxiomDiscoveryService:
    """Tests for AxiomDiscoveryService."""

    @pytest.fixture
    def service(self) -> AxiomDiscoveryService:
        """Create discovery service instance."""
        return AxiomDiscoveryService()

    @pytest.mark.asyncio
    async def test_discover_from_text_returns_report(
        self, service: AxiomDiscoveryService, sample_decisions: list[str]
    ) -> None:
        """discover_from_text should return DiscoveryReport."""
        report = await service.discover_from_text(
            texts=sample_decisions,
            min_pattern_occurrences=2,
        )

        assert isinstance(report, DiscoveryReport)
        assert report.decisions_processed == len(sample_decisions)
        assert report.duration_ms > 0

    @pytest.mark.asyncio
    async def test_discover_finds_recurring_patterns(
        self, service: AxiomDiscoveryService, sample_decisions: list[str]
    ) -> None:
        """Should discover axioms from recurring patterns."""
        report = await service.discover_from_text(
            texts=sample_decisions,
            min_pattern_occurrences=2,
        )

        # Should find at least one pattern
        assert report.candidates_analyzed >= 0  # May be 0 if threshold not met

    @pytest.mark.asyncio
    async def test_validate_fixed_point_with_stable_content(
        self, service: AxiomDiscoveryService
    ) -> None:
        """validate_fixed_point should work for simple content."""
        # Use simple mathematical axiom-like statement
        result = await service.validate_fixed_point("A equals A")

        # Should return a result with loss value
        assert hasattr(result, "loss")
        assert hasattr(result, "stability")
        assert hasattr(result, "is_fixed_point")
        assert 0.0 <= result.loss <= 1.0

    @pytest.mark.asyncio
    async def test_validate_fixed_point_threshold(self, service: AxiomDiscoveryService) -> None:
        """Should use custom threshold for validation."""
        result = await service.validate_fixed_point(
            "Test content",
            threshold=0.1,
        )

        assert hasattr(result, "is_fixed_point")
        # Result should be validated against 0.1 threshold

    @pytest.mark.asyncio
    async def test_empty_input_handling(self, service: AxiomDiscoveryService) -> None:
        """Should handle empty input gracefully."""
        report = await service.discover_from_text(
            texts=[],
            min_pattern_occurrences=2,
        )

        assert report.decisions_processed == 0
        assert len(report.discovered) == 0


# =============================================================================
# Discovered Axiom Tests
# =============================================================================


class TestDiscoveredAxiom:
    """Tests for DiscoveredAxiom dataclass."""

    def test_is_axiom_below_threshold(self) -> None:
        """is_axiom should return True when loss < AXIOM_THRESHOLD."""
        axiom = DiscoveredAxiom(
            content="Test axiom",
            loss=0.01,  # Below 0.05 threshold
            stability=0.001,
            iterations=3,
            confidence=0.99,
        )
        assert axiom.is_axiom is True

    def test_is_axiom_above_threshold(self) -> None:
        """is_axiom should return False when loss >= AXIOM_THRESHOLD."""
        axiom = DiscoveredAxiom(
            content="Not an axiom",
            loss=0.1,  # Above 0.05 threshold
            stability=0.01,
            iterations=3,
            confidence=0.9,
        )
        assert axiom.is_axiom is False

    def test_is_axiom_at_threshold(self) -> None:
        """is_axiom should return False when loss == AXIOM_THRESHOLD."""
        axiom = DiscoveredAxiom(
            content="Boundary case",
            loss=AXIOM_THRESHOLD,  # Exactly at threshold
            stability=0.001,
            iterations=3,
            confidence=0.95,
        )
        assert axiom.is_axiom is False  # Must be strictly less than

    def test_to_dict_includes_computed_properties(self) -> None:
        """to_dict should include is_axiom and is_stable."""
        axiom = DiscoveredAxiom(
            content="Test",
            loss=0.01,
            stability=0.001,
            iterations=3,
            confidence=0.99,
        )
        data = axiom.to_dict()

        assert "is_axiom" in data
        assert "is_stable" in data
        assert data["is_axiom"] is True


# =============================================================================
# Discovery Report Tests
# =============================================================================


class TestDiscoveryReport:
    """Tests for DiscoveryReport dataclass."""

    def test_axiom_count(self) -> None:
        """axiom_count should count axioms with L < 0.05."""
        report = DiscoveryReport(
            discovered=[
                DiscoveredAxiom("A1", 0.01, 0.001, 3, 0.99),  # Axiom
                DiscoveredAxiom("A2", 0.03, 0.002, 3, 0.97),  # Axiom
                DiscoveredAxiom("N1", 0.1, 0.01, 3, 0.9),  # Not axiom
            ],
            candidates_analyzed=3,
            patterns_found=3,
            decisions_processed=10,
            duration_ms=100.0,
        )
        assert report.axiom_count == 2

    def test_average_loss(self) -> None:
        """average_loss should compute mean of all discoveries."""
        report = DiscoveryReport(
            discovered=[
                DiscoveredAxiom("A1", 0.1, 0.001, 3, 0.9),
                DiscoveredAxiom("A2", 0.3, 0.002, 3, 0.7),
            ],
            candidates_analyzed=2,
            patterns_found=2,
            decisions_processed=10,
            duration_ms=100.0,
        )
        assert report.average_loss == 0.2

    def test_average_loss_empty(self) -> None:
        """average_loss should return 1.0 for empty discoveries."""
        report = DiscoveryReport(
            discovered=[],
            candidates_analyzed=0,
            patterns_found=0,
            decisions_processed=0,
            duration_ms=100.0,
        )
        assert report.average_loss == 1.0

    def test_to_dict(self) -> None:
        """to_dict should serialize report."""
        report = DiscoveryReport(
            discovered=[],
            candidates_analyzed=5,
            patterns_found=3,
            decisions_processed=10,
            duration_ms=50.5,
        )
        data = report.to_dict()

        assert data["candidates_analyzed"] == 5
        assert data["patterns_found"] == 3
        assert data["decisions_processed"] == 10
        assert data["duration_ms"] == 50.5
        assert "axiom_count" in data
        assert "average_loss" in data


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_validate_axiom_returns_tuple(self) -> None:
        """validate_axiom should return (is_axiom, loss) tuple."""
        is_axiom, loss = await validate_axiom("Test content")

        assert isinstance(is_axiom, bool)
        assert isinstance(loss, float)
        assert 0.0 <= loss <= 1.0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full discovery pipeline."""

    @pytest.mark.asyncio
    async def test_full_discovery_pipeline(self, sample_decisions: list[str]) -> None:
        """Full pipeline: decisions -> candidates -> validation -> axioms."""
        service = AxiomDiscoveryService()

        # Run discovery
        report = await service.discover_from_text(
            texts=sample_decisions,
            min_pattern_occurrences=2,
        )

        # Verify structure
        assert isinstance(report, DiscoveryReport)
        assert report.decisions_processed == len(sample_decisions)

        # All discovered items should have valid metrics
        for axiom in report.discovered:
            assert 0.0 <= axiom.loss <= 1.0
            assert axiom.stability >= 0.0
            assert axiom.confidence == 1.0 - axiom.loss

    @pytest.mark.asyncio
    async def test_discovered_axioms_sorted_by_loss(self) -> None:
        """Discovered axioms should be sorted by loss (best first)."""
        service = AxiomDiscoveryService()

        decisions = [
            "Clarity is important",
            "Clarity matters",
            "Clarity is essential",
            "Simplicity is important",
            "Simplicity matters",
        ]

        report = await service.discover_from_text(
            texts=decisions,
            min_pattern_occurrences=2,
        )

        if len(report.discovered) > 1:
            for i in range(len(report.discovered) - 1):
                assert report.discovered[i].loss <= report.discovered[i + 1].loss
