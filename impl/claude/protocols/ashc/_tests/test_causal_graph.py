"""
Tests for ASHC Causal Graph Learning

Tests the causal edge, graph, learner, similarity functions,
and law verification.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from ..causal_graph import (
    CausalEdge,
    CausalGraph,
    CausalLearner,
    build_graph_from_edges,
    create_edge,
    is_similar_nudge,
    nudge_similarity,
    text_similarity,
)
from ..evidence import Nudge, Run
from ..verify import LintReport, TestReport, TypeReport

# =============================================================================
# Fixtures
# =============================================================================


def make_nudge(
    location: str = "spec.principles",
    before: str = "composable",
    after: str = "very composable",
    reason: str = "emphasis",
) -> Nudge:
    """Create a test nudge."""
    return Nudge(location=location, before=before, after=after, reason=reason)


def make_edge(
    outcome_delta: float = 0.1,
    confidence: float = 0.5,
    runs_observed: int = 1,
    **nudge_kwargs,
) -> CausalEdge:
    """Create a test edge."""
    nudge = make_nudge(**nudge_kwargs)
    return CausalEdge(
        nudge=nudge,
        outcome_delta=outcome_delta,
        confidence=confidence,
        runs_observed=runs_observed,
    )


def make_run(
    passed: int = 10,
    failed: int = 0,
    nudges: tuple[Nudge, ...] = (),
) -> Run:
    """Create a test run."""
    return Run(
        run_id="test_run",
        spec_hash="abc123",
        prompt_used="test prompt",
        implementation="def foo(): pass",
        test_results=TestReport(passed=passed, failed=failed, skipped=0),
        type_results=TypeReport(passed=True, error_count=0),
        lint_results=LintReport(passed=True, violation_count=0),
        nudges=nudges,
    )


# =============================================================================
# Test Similarity Functions
# =============================================================================


class TestTextSimilarity:
    """Tests for text_similarity function."""

    def test_identical_strings(self) -> None:
        """Identical strings have similarity 1.0."""
        assert text_similarity("hello", "hello") == 1.0

    def test_empty_strings(self) -> None:
        """Two empty strings are similar."""
        assert text_similarity("", "") == 1.0

    def test_one_empty(self) -> None:
        """One empty string = no similarity."""
        assert text_similarity("hello", "") == 0.0
        assert text_similarity("", "hello") == 0.0

    def test_case_insensitive(self) -> None:
        """Similarity is case-insensitive."""
        assert text_similarity("Hello", "hello") == 1.0
        assert text_similarity("WORLD", "world") == 1.0

    def test_partial_match(self) -> None:
        """Partial matches have intermediate similarity."""
        sim = text_similarity("hello world", "hello there")
        assert 0.3 < sim < 0.8

    def test_completely_different(self) -> None:
        """Completely different strings have low similarity."""
        sim = text_similarity("abcdef", "xyz123")
        assert sim < 0.3


class TestNudgeSimilarity:
    """Tests for nudge_similarity function."""

    def test_identical_nudges(self) -> None:
        """Identical nudges have similarity 1.0."""
        n1 = make_nudge()
        n2 = make_nudge()
        assert nudge_similarity(n1, n2) == 1.0

    def test_same_location_different_content(self) -> None:
        """Same location but different content = partial similarity."""
        n1 = make_nudge(before="foo", after="bar")
        n2 = make_nudge(before="baz", after="qux")
        sim = nudge_similarity(n1, n2)
        # Location matches (0.3), reason matches (0.2), content differs
        assert 0.4 <= sim <= 0.6

    def test_different_location_same_content(self) -> None:
        """Different location but same content = high similarity."""
        n1 = make_nudge(location="spec.a")
        n2 = make_nudge(location="spec.b")
        sim = nudge_similarity(n1, n2)
        # Content matches (~0.7), location nearly matches (spec.a vs spec.b is ~0.85)
        assert sim > 0.9

    def test_completely_different(self) -> None:
        """Completely different nudges have low similarity."""
        n1 = Nudge(location="a", before="x", after="y", reason="z")
        n2 = Nudge(location="1", before="2", after="3", reason="4")
        sim = nudge_similarity(n1, n2)
        assert sim < 0.2


class TestIsSimilarNudge:
    """Tests for is_similar_nudge predicate."""

    def test_identical_is_similar(self) -> None:
        """Identical nudges are similar."""
        n = make_nudge()
        assert is_similar_nudge(n, n)

    def test_threshold_boundary(self) -> None:
        """Test behavior at threshold boundary."""
        n1 = make_nudge()
        # Slightly different but still similar
        n2 = Nudge(
            location=n1.location,
            before=n1.before,
            after=n1.after + " extra",
            reason=n1.reason,
        )
        # Should still be similar with default threshold
        assert is_similar_nudge(n1, n2, threshold=0.5)

    def test_custom_threshold(self) -> None:
        """Custom threshold affects result."""
        n1 = make_nudge()
        n2 = make_nudge(before="different")

        # With high threshold, not similar
        assert not is_similar_nudge(n1, n2, threshold=0.95)
        # With low threshold, similar
        assert is_similar_nudge(n1, n2, threshold=0.3)


# =============================================================================
# Test CausalEdge
# =============================================================================


class TestCausalEdge:
    """Tests for CausalEdge type."""

    def test_create_edge(self) -> None:
        """Create a basic edge."""
        edge = make_edge(outcome_delta=0.15, confidence=0.7)

        assert edge.outcome_delta == 0.15
        assert edge.confidence == 0.7
        assert edge.runs_observed == 1

    def test_is_beneficial(self) -> None:
        """Edge is beneficial if delta > 0."""
        assert make_edge(outcome_delta=0.1).is_beneficial
        assert not make_edge(outcome_delta=-0.1).is_beneficial
        assert not make_edge(outcome_delta=0.0).is_beneficial

    def test_is_harmful(self) -> None:
        """Edge is harmful if delta < 0."""
        assert make_edge(outcome_delta=-0.1).is_harmful
        assert not make_edge(outcome_delta=0.1).is_harmful
        assert not make_edge(outcome_delta=0.0).is_harmful

    def test_is_neutral(self) -> None:
        """Edge is neutral if |delta| < 0.05."""
        assert make_edge(outcome_delta=0.02).is_neutral
        assert make_edge(outcome_delta=-0.02).is_neutral
        assert not make_edge(outcome_delta=0.1).is_neutral

    def test_effect_size(self) -> None:
        """Effect size categorization."""
        assert make_edge(outcome_delta=0.01).effect_size == "negligible"
        assert make_edge(outcome_delta=0.10).effect_size == "small"
        assert make_edge(outcome_delta=0.20).effect_size == "medium"
        assert make_edge(outcome_delta=0.50).effect_size == "large"

    def test_with_observation_updates_delta(self) -> None:
        """Adding observation updates outcome delta."""
        edge = make_edge(outcome_delta=0.10, runs_observed=1)
        updated = edge.with_observation(0.20)

        # New delta should be between old and new
        assert 0.10 < updated.outcome_delta < 0.20

    def test_with_observation_increases_confidence(self) -> None:
        """Adding observation increases confidence (or preserves if already high)."""
        # Start with low confidence so count-based increase is visible
        edge = make_edge(confidence=0.2, runs_observed=1)
        updated = edge.with_observation(0.10)

        # With 2 runs, count_confidence = 1 - 1/(1 + 2*0.2) ≈ 0.286
        assert updated.confidence >= edge.confidence
        assert updated.runs_observed == 2

        # After more observations, confidence increases further
        edge2 = updated.with_observation(0.10)
        edge3 = edge2.with_observation(0.10)
        edge4 = edge3.with_observation(0.10)

        assert edge4.confidence > updated.confidence
        assert edge4.runs_observed == 5

    def test_with_observation_updates_timestamp(self) -> None:
        """Adding observation updates last_updated."""
        edge = make_edge()
        updated = edge.with_observation(0.10)

        assert updated.last_updated >= edge.last_updated


# =============================================================================
# Test CausalGraph
# =============================================================================


class TestCausalGraph:
    """Tests for CausalGraph type."""

    def test_empty_graph(self) -> None:
        """Empty graph has no edges."""
        graph = CausalGraph()

        assert graph.edge_count == 0
        assert graph.total_observations == 0

    def test_with_edge(self) -> None:
        """Add edge to graph."""
        graph = CausalGraph()
        edge = make_edge()

        new_graph = graph.with_edge(edge)

        assert new_graph.edge_count == 1
        assert graph.edge_count == 0  # Immutable

    def test_with_edge_updates_similar(self) -> None:
        """Adding similar edge updates existing."""
        edge1 = make_edge(outcome_delta=0.10)
        graph = CausalGraph(edges=(edge1,))

        # Add very similar edge
        edge2 = make_edge(outcome_delta=0.20)
        new_graph = graph.with_edge(edge2)

        # Should still be 1 edge, but updated
        assert new_graph.edge_count == 1
        assert new_graph.edges[0].runs_observed == 2

    def test_with_edge_adds_different(self) -> None:
        """Adding different edge creates new entry."""
        edge1 = make_edge(location="principles.composability", before="A", after="B")
        graph = CausalGraph(edges=(edge1,))

        # Add truly different edge (different location AND content)
        edge2 = make_edge(
            location="requirements.security", before="X", after="Y", reason="security concern"
        )
        new_graph = graph.with_edge(edge2)

        assert new_graph.edge_count == 2

    def test_predict_outcome_no_data(self) -> None:
        """Prediction with no data returns 0."""
        graph = CausalGraph()
        nudge = make_nudge()

        assert graph.predict_outcome(nudge) == 0.0

    def test_predict_outcome_exact_match(self) -> None:
        """Prediction with exact match uses that edge."""
        edge = make_edge(outcome_delta=0.15, confidence=0.8)
        graph = CausalGraph(edges=(edge,))

        prediction = graph.predict_outcome(edge.nudge)

        assert prediction == pytest.approx(0.15, abs=0.01)

    def test_predict_outcome_similar_match(self) -> None:
        """Prediction with similar nudge interpolates."""
        edge = make_edge(outcome_delta=0.20, confidence=0.8, before="composable")
        graph = CausalGraph(edges=(edge,))

        # Similar but not identical nudge
        similar = make_nudge(before="composable agents")
        prediction = graph.predict_outcome(similar)

        # Should be positive (similar to beneficial nudge)
        assert prediction > 0

    def test_predict_with_confidence(self) -> None:
        """Prediction with confidence interval."""
        edge = make_edge(outcome_delta=0.15, confidence=0.8)
        graph = CausalGraph(edges=(edge,))

        delta, confidence = graph.predict_with_confidence(edge.nudge)

        assert delta == pytest.approx(0.15, abs=0.01)
        assert 0 < confidence <= 1.0

    def test_predict_with_confidence_no_data(self) -> None:
        """No data = zero confidence."""
        graph = CausalGraph()
        nudge = make_nudge()

        delta, confidence = graph.predict_with_confidence(nudge)

        assert delta == 0.0
        assert confidence == 0.0

    def test_stability_score_stable(self) -> None:
        """Graph with consistent small nudge effects is stable."""
        edges = [
            create_edge("a", "x", "y", "r", 0.02, confidence=0.5),
            create_edge("b", "x", "y", "r", 0.03, confidence=0.5),
            create_edge("c", "x", "y", "r", 0.01, confidence=0.5),
        ]
        graph = build_graph_from_edges(edges)

        # Low variance = high stability
        assert graph.stability_score > 0.9

    def test_stability_score_unstable(self) -> None:
        """Graph with inconsistent effects is less stable."""
        edges = [
            create_edge("a", "x", "y", "r", 0.50, confidence=0.5),
            create_edge("b", "x", "y", "r", -0.50, confidence=0.5),
            create_edge("c", "x", "y", "r", 0.30, confidence=0.5),
        ]
        graph = build_graph_from_edges(edges)

        # High variance = lower stability (but still above 0.5 with formula 1/(1+var))
        # Variance of [0.5, -0.5, 0.3] ≈ 0.28, so stability ≈ 0.78
        assert graph.stability_score < 0.85

    def test_beneficial_edges(self) -> None:
        """Get edges with positive outcomes."""
        edges = [
            make_edge(outcome_delta=0.10, location="a"),
            make_edge(outcome_delta=-0.10, location="b"),
            make_edge(outcome_delta=0.20, location="c"),
        ]
        graph = CausalGraph(edges=tuple(edges))

        beneficial = graph.beneficial_edges

        assert len(beneficial) == 2
        assert all(e.is_beneficial for e in beneficial)

    def test_harmful_edges(self) -> None:
        """Get edges with negative outcomes."""
        edges = [
            make_edge(outcome_delta=0.10, location="a"),
            make_edge(outcome_delta=-0.10, location="b"),
            make_edge(outcome_delta=-0.20, location="c"),
        ]
        graph = CausalGraph(edges=tuple(edges))

        harmful = graph.harmful_edges

        assert len(harmful) == 2
        assert all(e.is_harmful for e in harmful)

    def test_merge_graphs(self) -> None:
        """Merge two graphs."""
        g1 = CausalGraph(edges=(make_edge(location="a"),))
        g2 = CausalGraph(edges=(make_edge(location="b"),))

        merged = g1.merge(g2)

        assert merged.edge_count == 2


# =============================================================================
# Test Causal Laws
# =============================================================================


class TestCausalLaws:
    """Tests for causal law verification."""

    def test_causal_monotonicity_satisfied(self) -> None:
        """Similar nudges with similar outcomes satisfy monotonicity."""
        # Two very similar nudges with similar outcomes
        n1 = make_nudge(before="composable", after="very composable")
        n2 = make_nudge(before="composable", after="highly composable")

        e1 = CausalEdge(nudge=n1, outcome_delta=0.10, confidence=0.8, runs_observed=5)
        e2 = CausalEdge(nudge=n2, outcome_delta=0.12, confidence=0.8, runs_observed=5)

        graph = CausalGraph(edges=(e1, e2))

        assert graph.verify_causal_monotonicity()

    def test_causal_monotonicity_violated(self) -> None:
        """Similar nudges with very different outcomes violate monotonicity."""
        # Two very similar nudges with very different outcomes
        n1 = make_nudge(before="composable", after="very composable")
        n2 = make_nudge(before="composable", after="highly composable")

        e1 = CausalEdge(nudge=n1, outcome_delta=0.50, confidence=0.8, runs_observed=5)
        e2 = CausalEdge(nudge=n2, outcome_delta=-0.30, confidence=0.8, runs_observed=5)

        graph = CausalGraph(edges=(e1, e2))

        assert not graph.verify_causal_monotonicity()

    def test_find_violations(self) -> None:
        """Find specific monotonicity violations."""
        n1 = make_nudge(before="a", after="a+")
        n2 = make_nudge(before="a", after="a++")

        e1 = CausalEdge(nudge=n1, outcome_delta=0.50, confidence=0.8, runs_observed=5)
        e2 = CausalEdge(nudge=n2, outcome_delta=-0.30, confidence=0.8, runs_observed=5)

        graph = CausalGraph(edges=(e1, e2))
        violations = graph.causal_monotonicity_violations()

        assert len(violations) == 1
        assert violations[0][2] == pytest.approx(0.80, abs=0.01)


# =============================================================================
# Test CausalLearner
# =============================================================================


class TestCausalLearner:
    """Tests for CausalLearner."""

    def test_observe_run_with_nudges(self) -> None:
        """Learn from run with nudges."""
        learner = CausalLearner(baseline_pass_rate=0.5)
        nudge = make_nudge()
        run = make_run(passed=8, failed=2, nudges=(nudge,))

        learner.observe_run(run)

        assert learner.graph.edge_count == 1
        # Pass rate 0.8, baseline 0.5 → delta 0.3
        edge = learner.graph.edges[0]
        assert edge.outcome_delta == pytest.approx(0.3, abs=0.01)

    def test_observe_run_without_nudges(self) -> None:
        """Run without nudges doesn't add edges."""
        learner = CausalLearner()
        run = make_run(passed=10, failed=0, nudges=())

        learner.observe_run(run)

        assert learner.graph.edge_count == 0

    def test_observe_multiple_nudges(self) -> None:
        """Run with multiple nudges creates multiple edges."""
        learner = CausalLearner(baseline_pass_rate=0.5)
        n1 = make_nudge(location="a")
        n2 = make_nudge(location="b")
        run = make_run(passed=7, failed=3, nudges=(n1, n2))

        learner.observe_run(run)

        assert learner.graph.edge_count == 2

    def test_compare_with_without(self) -> None:
        """Compare runs with and without nudge."""
        learner = CausalLearner()
        nudge = make_nudge()

        runs_with = [
            make_run(passed=9, failed=1),
            make_run(passed=8, failed=2),
        ]
        runs_without = [
            make_run(passed=5, failed=5),
            make_run(passed=6, failed=4),
        ]

        edge = learner.compare_with_without(runs_with, runs_without, nudge)

        # With: avg 0.85, Without: avg 0.55 → delta 0.30
        assert edge.outcome_delta == pytest.approx(0.30, abs=0.01)
        assert edge.runs_observed == 4

    def test_compare_empty_raises(self) -> None:
        """Compare with empty runs raises error."""
        learner = CausalLearner()
        nudge = make_nudge()

        with pytest.raises(ValueError):
            learner.compare_with_without([], [make_run()], nudge)

        with pytest.raises(ValueError):
            learner.compare_with_without([make_run()], [], nudge)

    def test_suggest_nudge_improve(self) -> None:
        """Suggest most beneficial nudge."""
        # Build graph with beneficial and harmful edges
        beneficial = make_edge(outcome_delta=0.30, confidence=0.8, location="good")
        harmful = make_edge(outcome_delta=-0.20, confidence=0.8, location="bad")

        learner = CausalLearner()
        learner.graph = CausalGraph(edges=(beneficial, harmful))

        suggestion = learner.suggest_nudge(goal="improve")

        assert suggestion is not None
        assert suggestion.location == "good"

    def test_suggest_nudge_no_data(self) -> None:
        """No suggestions when graph is empty."""
        learner = CausalLearner()

        assert learner.suggest_nudge() is None


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests for helper functions."""

    def test_create_edge(self) -> None:
        """Create edge with convenience function."""
        edge = create_edge(
            location="spec.principles",
            before="old",
            after="new",
            reason="improvement",
            outcome_delta=0.15,
        )

        assert edge.nudge.location == "spec.principles"
        assert edge.outcome_delta == 0.15

    def test_build_graph_from_edges(self) -> None:
        """Build graph from edge list."""
        edges = [
            create_edge("a", "x", "y", "r1", 0.1),
            create_edge("b", "x", "y", "r2", 0.2),
        ]

        graph = build_graph_from_edges(edges)

        assert graph.edge_count == 2
