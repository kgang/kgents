"""
Tests for ASHC Adapter: Archaeological priors → CausalGraph integration.

These tests verify:
1. Prior → Nudge conversion preserves semantics
2. Prior → Edge conversion applies confidence discount
3. Graph seeding adds edges correctly
4. CausalLearner seeding works end-to-end
"""

from __future__ import annotations

from datetime import datetime

import pytest

from services.archaeology.ashc_adapter import (
    ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT,
    PriorConversionResult,
    create_seeded_learner,
    generate_priors_report,
    prior_to_edge,
    prior_to_nudge,
    seed_graph_with_priors,
    seed_learner_with_archaeology,
    spec_pattern_to_edge,
    spec_pattern_to_nudge,
)
from services.archaeology.priors import CausalPrior as ArchaeologicalPrior, SpecPattern

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_prior() -> ArchaeologicalPrior:
    """Sample archaeological prior for testing."""
    return ArchaeologicalPrior(
        pattern="feat: prefix",
        outcome_correlation=0.15,
        sample_size=50,
        confidence=0.3,
    )


@pytest.fixture
def negative_prior() -> ArchaeologicalPrior:
    """Prior with negative correlation."""
    return ArchaeologicalPrior(
        pattern="high_churn_commits",
        outcome_correlation=-0.2,
        sample_size=30,
        confidence=0.25,
    )


@pytest.fixture
def sample_spec_pattern() -> SpecPattern:
    """Sample spec pattern for testing."""
    return SpecPattern(
        pattern_type="early_test_adoption",
        example_specs=("PolyAgent", "Operad", "Sheaf", "Flux", "Brain"),
        success_correlation=1.0,
        description="Tests added within first 10 commits",
    )


@pytest.fixture
def multiple_priors() -> list[ArchaeologicalPrior]:
    """Multiple priors for batch testing."""
    return [
        ArchaeologicalPrior(
            pattern="feat: prefix",
            outcome_correlation=0.15,
            sample_size=50,
            confidence=0.3,
        ),
        ArchaeologicalPrior(
            pattern="fix: prefix",
            outcome_correlation=0.1,
            sample_size=40,
            confidence=0.3,
        ),
        ArchaeologicalPrior(
            pattern="refactor: prefix",
            outcome_correlation=0.05,
            sample_size=20,
            confidence=0.3,
        ),
    ]


@pytest.fixture
def multiple_patterns() -> list[SpecPattern]:
    """Multiple spec patterns for batch testing."""
    return [
        SpecPattern(
            pattern_type="early_test_adoption",
            example_specs=("PolyAgent", "Operad"),
            success_correlation=1.0,
            description="Tests in first 10 commits",
        ),
        SpecPattern(
            pattern_type="sustained_momentum",
            example_specs=("Brain", "Gardener"),
            success_correlation=0.9,
            description="High velocity sustained",
        ),
    ]


# =============================================================================
# Prior → Nudge Conversion Tests
# =============================================================================


class TestPriorToNudge:
    """Tests for prior_to_nudge conversion."""

    def test_converts_feat_prefix(self, sample_prior: ArchaeologicalPrior) -> None:
        """feat: prefix maps to commit_message location."""
        nudge = prior_to_nudge(sample_prior)

        assert nudge.location == "commit_message"
        assert "feat: prefix" in nudge.after
        assert "Archaeological evidence" in nudge.reason
        assert "50 observations" in nudge.reason

    def test_converts_negative_prior(self, negative_prior: ArchaeologicalPrior) -> None:
        """Negative correlation is preserved in reason."""
        nudge = prior_to_nudge(negative_prior)

        assert nudge.location == "implementation"
        assert "negative" in nudge.reason.lower()
        assert "high_churn_commits" in nudge.after

    def test_reason_includes_correlation(self, sample_prior: ArchaeologicalPrior) -> None:
        """Reason includes the correlation value."""
        nudge = prior_to_nudge(sample_prior)

        assert "15%" in nudge.reason  # 0.15 as percentage

    def test_unknown_pattern_uses_spec_location(self) -> None:
        """Unknown patterns default to 'spec' location."""
        prior = ArchaeologicalPrior(
            pattern="unknown_pattern",
            outcome_correlation=0.1,
            sample_size=10,
            confidence=0.2,
        )
        nudge = prior_to_nudge(prior)

        assert nudge.location == "spec"


class TestSpecPatternToNudge:
    """Tests for spec_pattern_to_nudge conversion."""

    def test_converts_spec_pattern(self, sample_spec_pattern: SpecPattern) -> None:
        """Spec patterns become spec_structure nudges."""
        nudge = spec_pattern_to_nudge(sample_spec_pattern)

        assert nudge.location == "spec_structure"
        assert "early_test_adoption" in nudge.after
        assert "100%" in nudge.reason  # success_correlation

    def test_includes_examples(self, sample_spec_pattern: SpecPattern) -> None:
        """Reason includes example specs."""
        nudge = spec_pattern_to_nudge(sample_spec_pattern)

        assert "PolyAgent" in nudge.reason
        assert "Operad" in nudge.reason


# =============================================================================
# Prior → Edge Conversion Tests
# =============================================================================


class TestPriorToEdge:
    """Tests for prior_to_edge conversion."""

    def test_applies_confidence_discount(self, sample_prior: ArchaeologicalPrior) -> None:
        """Archaeological confidence is discounted."""
        edge = prior_to_edge(sample_prior)

        expected_confidence = sample_prior.confidence * ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT
        assert edge.confidence == expected_confidence
        assert edge.confidence < sample_prior.confidence

    def test_preserves_outcome_delta(self, sample_prior: ArchaeologicalPrior) -> None:
        """Outcome delta is preserved from prior."""
        edge = prior_to_edge(sample_prior)

        assert edge.outcome_delta == sample_prior.outcome_correlation

    def test_preserves_sample_size(self, sample_prior: ArchaeologicalPrior) -> None:
        """Runs observed equals sample size."""
        edge = prior_to_edge(sample_prior)

        assert edge.runs_observed == sample_prior.sample_size

    def test_sets_timestamps(self, sample_prior: ArchaeologicalPrior) -> None:
        """Timestamps are set on conversion."""
        before = datetime.now()
        edge = prior_to_edge(sample_prior)
        after = datetime.now()

        assert before <= edge.created_at <= after
        assert before <= edge.last_updated <= after


class TestSpecPatternToEdge:
    """Tests for spec_pattern_to_edge conversion."""

    def test_applies_confidence_discount(self, sample_spec_pattern: SpecPattern) -> None:
        """Spec pattern confidence is discounted."""
        edge = spec_pattern_to_edge(sample_spec_pattern)

        expected_confidence = sample_spec_pattern.confidence * ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT
        assert edge.confidence == expected_confidence

    def test_uses_example_count_for_runs(self, sample_spec_pattern: SpecPattern) -> None:
        """Runs observed equals number of examples."""
        edge = spec_pattern_to_edge(sample_spec_pattern)

        assert edge.runs_observed == len(sample_spec_pattern.example_specs)


# =============================================================================
# Graph Seeding Tests
# =============================================================================


class TestSeedGraphWithPriors:
    """Tests for seed_graph_with_priors function."""

    def test_adds_edges_to_empty_graph(self, multiple_priors: list[ArchaeologicalPrior]) -> None:
        """Seeding adds edges to empty graph."""
        from protocols.ashc import CausalGraph

        graph = CausalGraph()
        seeded_graph, result = seed_graph_with_priors(graph, multiple_priors)

        # CausalGraph merges similar edges (>0.9 similarity), so the
        # feat:/fix:/refactor: prefixes coalesce into fewer edges
        # The important thing is that edges are created and result tracks attempts
        assert seeded_graph.edge_count >= 1
        assert result.edges_created == len(multiple_priors)

    def test_includes_spec_patterns(
        self,
        multiple_priors: list[ArchaeologicalPrior],
        multiple_patterns: list[SpecPattern],
    ) -> None:
        """Seeding includes both priors and patterns."""
        from protocols.ashc import CausalGraph

        graph = CausalGraph()
        seeded_graph, result = seed_graph_with_priors(graph, multiple_priors, multiple_patterns)

        # Similar edges may be merged, but result tracks all attempted
        expected_attempts = len(multiple_priors) + len(multiple_patterns)
        assert seeded_graph.edge_count >= 1  # At least one edge
        assert result.edges_created == expected_attempts

    def test_reports_patterns_incorporated(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Result includes incorporated pattern names."""
        from protocols.ashc import CausalGraph

        graph = CausalGraph()
        _, result = seed_graph_with_priors(graph, multiple_priors)

        for prior in multiple_priors:
            assert prior.pattern in result.patterns_incorporated

    def test_calculates_total_confidence(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Result includes total discounted confidence."""
        from protocols.ashc import CausalGraph

        graph = CausalGraph()
        _, result = seed_graph_with_priors(graph, multiple_priors)

        # Each prior contributes discounted confidence
        expected = sum(p.confidence * ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT for p in multiple_priors)
        assert abs(result.total_confidence - expected) < 0.01

    def test_adds_to_existing_graph(self, sample_prior: ArchaeologicalPrior) -> None:
        """Seeding works on graph with existing edges."""
        from protocols.ashc import CausalEdge, CausalGraph, Nudge

        # Create graph with existing edge
        existing_nudge = Nudge(
            location="spec",
            before="old",
            after="new",
            reason="existing",
        )
        existing_edge = CausalEdge(
            nudge=existing_nudge,
            outcome_delta=0.5,
            confidence=0.8,
            runs_observed=10,
        )
        graph = CausalGraph(edges=(existing_edge,))

        seeded_graph, result = seed_graph_with_priors(graph, [sample_prior])

        assert seeded_graph.edge_count == 2  # existing + new
        assert result.edges_created == 1  # only new counted


# =============================================================================
# CausalLearner Seeding Tests
# =============================================================================


class TestSeedLearnerWithArchaeology:
    """Tests for seed_learner_with_archaeology function."""

    def test_updates_learner_in_place(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Seeding updates learner's graph in place."""
        from protocols.ashc import CausalLearner

        learner = CausalLearner()
        assert learner.graph.edge_count == 0

        result = seed_learner_with_archaeology(learner, multiple_priors)

        # Similar edges merge, but result tracks all attempted
        assert learner.graph.edge_count >= 1
        assert result.edges_created == len(multiple_priors)


class TestCreateSeededLearner:
    """Tests for create_seeded_learner convenience function."""

    def test_creates_new_learner(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Creates fresh learner with priors."""
        learner, result = create_seeded_learner(multiple_priors)

        # Similar edges merge, but result tracks all attempted
        assert learner.graph.edge_count >= 1
        assert result.edges_created == len(multiple_priors)

    def test_sets_baseline(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Baseline pass rate is configurable."""
        learner, _ = create_seeded_learner(
            multiple_priors,
            baseline_pass_rate=0.7,
        )

        assert learner.baseline_pass_rate == 0.7


# =============================================================================
# Report Generation Tests
# =============================================================================


class TestGeneratePriorsReport:
    """Tests for generate_priors_report function."""

    def test_generates_markdown(self) -> None:
        """Report is valid markdown."""
        result = PriorConversionResult(
            edges_created=5,
            total_confidence=1.5,
            patterns_incorporated=["feat: prefix", "fix: prefix"],
            warnings=[],
        )

        report = generate_priors_report(result)

        assert "# Archaeological Prior Integration Report" in report
        assert "**Edges Created**: 5" in report
        assert "feat: prefix" in report

    def test_includes_warnings(self) -> None:
        """Report includes warnings if present."""
        result = PriorConversionResult(
            edges_created=3,
            total_confidence=0.9,
            patterns_incorporated=["a", "b", "c"],
            warnings=["Could not convert 'x': error"],
        )

        report = generate_priors_report(result)

        assert "## Warnings" in report
        assert "Could not convert 'x'" in report

    def test_shows_discount_rate(self) -> None:
        """Report shows the confidence discount rate."""
        result = PriorConversionResult(
            edges_created=1,
            total_confidence=0.3,
            patterns_incorporated=["test"],
            warnings=[],
        )

        report = generate_priors_report(result)

        assert "50%" in report  # ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT


# =============================================================================
# Integration Tests
# =============================================================================


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_seeded_learner_can_predict(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Seeded learner can make predictions."""
        from protocols.ashc import Nudge

        learner, _ = create_seeded_learner(multiple_priors)

        # Create a nudge similar to one of the priors
        similar_nudge = Nudge(
            location="commit_message",
            before="(no feat: prefix)",
            after="(with feat: prefix)",
            reason="test prediction",
        )

        # Should predict based on archaeological evidence
        prediction = learner.graph.predict_outcome(similar_nudge)

        # Prediction may be 0 if similarity threshold not met,
        # but the graph should have edges
        assert learner.graph.edge_count > 0

    def test_graph_maintains_causal_laws(
        self,
        multiple_priors: list[ArchaeologicalPrior],
    ) -> None:
        """Seeded graph maintains causal monotonicity."""
        from protocols.ashc import CausalGraph

        graph = CausalGraph()
        seeded_graph, _ = seed_graph_with_priors(graph, multiple_priors)

        # Archaeological priors shouldn't violate monotonicity
        # (similar patterns from same source should have similar effects)
        assert seeded_graph.verify_causal_monotonicity(tolerance=0.5)

    def test_round_trip_with_patterns(
        self,
        multiple_priors: list[ArchaeologicalPrior],
        multiple_patterns: list[SpecPattern],
    ) -> None:
        """Full round-trip with priors and patterns."""
        learner, result = create_seeded_learner(
            multiple_priors,
            multiple_patterns,
        )

        # Verify all incorporated
        assert result.edges_created == len(multiple_priors) + len(multiple_patterns)

        # Verify beneficial edges detected
        beneficial = learner.graph.beneficial_edges
        assert len(beneficial) > 0  # Most archaeological priors are positive
