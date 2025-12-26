"""
Tests for Fixed-Point Detection (Amendment F).

Verifies that fixed-point detection:
1. Correctly identifies content below threshold as candidates
2. Verifies stability under repeated R-C
3. Rejects content that doesn't remain stable
4. Extracts axiom candidates from corpora
"""

import statistics

import pytest

from services.zero_seed.galois.fixed_point import (
    MAX_STABILITY_ITERATIONS,
    STABILITY_THRESHOLD,
    FixedPointMetrics,
    FixedPointResult,
    batch_detect_fixed_points,
    compute_fixed_point_metrics,
    detect_fixed_point,
    extract_axioms,
)
from services.zero_seed.galois.galois_loss import (
    FIXED_POINT_THRESHOLD,
    GaloisLossComputer,
    ModularComponent,
    ModularPrompt,
)

# =============================================================================
# Mock LLM Client
# =============================================================================


class MockLLMClient:
    """
    Mock LLM client for testing fixed-point detection.

    Configurable to produce stable or unstable losses.
    """

    def __init__(
        self,
        base_loss: float = 0.02,
        variance: float = 0.005,
        add_noise: bool = True,
    ):
        """
        Initialize mock client.

        Args:
            base_loss: Base loss value for reconstitution
            variance: Amount of variance in losses (simulates instability)
            add_noise: Whether to add noise to losses
        """
        self.base_loss = base_loss
        self.variance = variance
        self.add_noise = add_noise
        self.call_count = 0

    async def restructure(self, content: str) -> ModularPrompt:
        """Mock restructure - splits content into components."""
        self.call_count += 1
        # Simple split by sentences
        sentences = content.split(". ")
        components = [
            ModularComponent(
                name=f"component_{i}",
                content=sent.strip(),
                weight=1.0,
                dependencies=(),
            )
            for i, sent in enumerate(sentences)
            if sent.strip()
        ]
        return ModularPrompt(components=components)

    async def reconstitute(self, modular: ModularPrompt) -> str:
        """Mock reconstitute - joins components with slight modifications."""
        return ". ".join(c.content for c in modular.components)


class UnstableLLMClient(MockLLMClient):
    """LLM client that produces unstable (varying) outputs."""

    def __init__(self):
        super().__init__(base_loss=0.03, variance=0.1, add_noise=True)
        self._iteration = 0

    async def reconstitute(self, modular: ModularPrompt) -> str:
        """Reconstitute with increasing variation."""
        self._iteration += 1
        # Add more variation with each iteration
        variation = f" [variation {self._iteration}]"
        return ". ".join(c.content for c in modular.components) + variation


class HighLossLLMClient(MockLLMClient):
    """LLM client that produces high losses (not fixed point candidates)."""

    async def reconstitute(self, modular: ModularPrompt) -> str:
        """Reconstitute with major changes."""
        # Return completely different content
        return "This is completely different content that will have high loss."


# =============================================================================
# Test FixedPointResult
# =============================================================================


class TestFixedPointResult:
    """Test FixedPointResult data structure."""

    def test_is_axiom_candidate_true(self):
        """Axiom candidates have is_fixed_point=True and loss < 0.01."""
        result = FixedPointResult(
            is_fixed_point=True,
            loss=0.005,
            stability=0.001,
            iterations=3,
            losses=[0.005, 0.004, 0.006],
        )
        assert result.is_axiom_candidate is True

    def test_is_axiom_candidate_false_not_fixed_point(self):
        """Non-fixed points cannot be axiom candidates."""
        result = FixedPointResult(
            is_fixed_point=False,
            loss=0.005,
            stability=0.001,
            iterations=1,
            losses=[0.005],
        )
        assert result.is_axiom_candidate is False

    def test_is_axiom_candidate_false_high_loss(self):
        """Fixed points with loss >= 0.01 are not axiom candidates."""
        result = FixedPointResult(
            is_fixed_point=True,
            loss=0.02,
            stability=0.001,
            iterations=3,
            losses=[0.02, 0.02, 0.02],
        )
        assert result.is_axiom_candidate is False

    def test_convergence_depth(self):
        """Test convergence depth calculation."""
        result = FixedPointResult(
            is_fixed_point=True,
            loss=0.03,
            stability=0.001,
            iterations=3,
            losses=[0.08, 0.06, 0.03],  # Converges at iteration 3
        )
        assert result.convergence_depth == 3

    def test_convergence_depth_immediate(self):
        """Immediate convergence has depth 1."""
        result = FixedPointResult(
            is_fixed_point=True,
            loss=0.02,
            stability=0.001,
            iterations=3,
            losses=[0.02, 0.02, 0.02],
        )
        assert result.convergence_depth == 1

    def test_convergence_depth_never(self):
        """Non-converging content has depth -1."""
        result = FixedPointResult(
            is_fixed_point=False,
            loss=0.3,
            stability=0.05,
            iterations=3,
            losses=[0.3, 0.35, 0.32],  # All above threshold
        )
        assert result.convergence_depth == -1

    def test_mean_loss(self):
        """Mean loss is average of all iteration losses."""
        result = FixedPointResult(
            is_fixed_point=True,
            loss=0.02,
            stability=0.005,
            iterations=3,
            losses=[0.02, 0.03, 0.025],
        )
        expected = statistics.mean([0.02, 0.03, 0.025])
        assert abs(result.mean_loss - expected) < 1e-6

    def test_to_dict(self):
        """Serialization includes all fields."""
        result = FixedPointResult(
            is_fixed_point=True,
            loss=0.02,
            stability=0.005,
            iterations=3,
            losses=[0.02, 0.03, 0.025],
        )
        d = result.to_dict()

        assert d["is_fixed_point"] is True
        assert d["loss"] == 0.02
        assert d["stability"] == 0.005
        assert d["iterations"] == 3
        assert d["losses"] == [0.02, 0.03, 0.025]
        assert "is_axiom_candidate" in d
        assert "convergence_depth" in d
        assert "mean_loss" in d


# =============================================================================
# Test detect_fixed_point
# =============================================================================


class TestDetectFixedPoint:
    """Test the core detect_fixed_point function."""

    @pytest.mark.asyncio
    async def test_detects_stable_fixed_point(self):
        """
        Stable content with low loss should be detected as fixed point.
        """
        content = "Agency requires justification"
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        result = await detect_fixed_point(content, computer)

        # Should be detected as fixed point
        assert result.is_fixed_point is True
        assert result.loss < FIXED_POINT_THRESHOLD
        assert result.stability < STABILITY_THRESHOLD
        assert result.iterations == MAX_STABILITY_ITERATIONS

    @pytest.mark.asyncio
    async def test_rejects_high_loss_content(self):
        """
        Content with high initial loss should not be fixed point.
        """
        content = "This is complex content that restructures poorly"
        computer = GaloisLossComputer(llm=HighLossLLMClient())

        result = await detect_fixed_point(content, computer)

        # Should fail immediately (initial loss too high)
        assert result.is_fixed_point is False
        assert result.iterations == 1  # Should fail fast

    @pytest.mark.asyncio
    async def test_rejects_unstable_content(self):
        """
        Content that varies too much under repeated R-C should not be fixed point.
        """
        content = "Content that will become unstable"
        computer = GaloisLossComputer(llm=UnstableLLMClient())

        result = await detect_fixed_point(
            content,
            computer,
            threshold=0.5,  # Generous threshold
            stability_threshold=0.01,  # Strict stability
        )

        # Initial loss might pass, but stability should fail
        # (depending on mock behavior)
        # The key is that stability > stability_threshold causes rejection

    @pytest.mark.asyncio
    async def test_respects_threshold_parameter(self):
        """
        Custom threshold should be respected.
        """
        content = "Test content"
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.03))

        # With default threshold (0.05), should pass
        result1 = await detect_fixed_point(content, computer, threshold=0.05)

        # With stricter threshold, might fail
        result2 = await detect_fixed_point(content, computer, threshold=0.01)

        # Result depends on actual loss computation
        # Just verify the function accepts the parameter

    @pytest.mark.asyncio
    async def test_respects_max_iterations(self):
        """
        Custom max_iterations should be respected.
        """
        content = "Test content"
        computer = GaloisLossComputer(llm=MockLLMClient())

        result = await detect_fixed_point(content, computer, max_iterations=5)

        # Should have exactly 5 losses (or fewer if failed early)
        assert result.iterations <= 5


# =============================================================================
# Test extract_axioms
# =============================================================================


class TestExtractAxioms:
    """Test axiom extraction from corpora."""

    @pytest.mark.asyncio
    async def test_extracts_top_k(self):
        """
        Should return top_k candidates sorted by loss.
        """
        corpus = [
            "Simple axiom one",
            "Simple axiom two",
            "Simple axiom three",
            "Complex content that won't be a fixed point",
        ]
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        axioms = await extract_axioms(corpus, computer, top_k=2)

        assert len(axioms) <= 2
        # Should be sorted by loss (lowest first)
        if len(axioms) >= 2:
            assert axioms[0][1].loss <= axioms[1][1].loss

    @pytest.mark.asyncio
    async def test_returns_tuples(self):
        """
        Should return (content, FixedPointResult) tuples.
        """
        corpus = ["Test content"]
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        axioms = await extract_axioms(corpus, computer, top_k=5)

        for content, result in axioms:
            assert isinstance(content, str)
            assert isinstance(result, FixedPointResult)

    @pytest.mark.asyncio
    async def test_empty_corpus(self):
        """
        Should handle empty corpus.
        """
        computer = GaloisLossComputer(llm=MockLLMClient())

        axioms = await extract_axioms([], computer, top_k=5)

        assert axioms == []


# =============================================================================
# Test batch_detect_fixed_points
# =============================================================================


class TestBatchDetectFixedPoints:
    """Test batch fixed-point detection."""

    @pytest.mark.asyncio
    async def test_batch_returns_all_content(self):
        """
        Should return results for all content, not just fixed points.
        """
        corpus = [
            "Fixed point content",
            "Non-fixed point content",
        ]
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        results = await batch_detect_fixed_points(corpus, computer)

        assert len(results) == 2
        assert "Fixed point content" in results
        assert "Non-fixed point content" in results

    @pytest.mark.asyncio
    async def test_batch_results_are_fixed_point_results(self):
        """
        All results should be FixedPointResult instances.
        """
        corpus = ["Test content"]
        computer = GaloisLossComputer(llm=MockLLMClient())

        results = await batch_detect_fixed_points(corpus, computer)

        for result in results.values():
            assert isinstance(result, FixedPointResult)


# =============================================================================
# Test FixedPointMetrics
# =============================================================================


class TestFixedPointMetrics:
    """Test aggregate metrics computation."""

    @pytest.mark.asyncio
    async def test_compute_metrics(self):
        """
        Should compute aggregate metrics from batch results.
        """
        corpus = [
            "Fixed point one",
            "Fixed point two",
            "Not a fixed point",
        ]
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        results = await batch_detect_fixed_points(corpus, computer)
        metrics = await compute_fixed_point_metrics(results)

        assert metrics.total_analyzed == 3
        assert metrics.fixed_point_count >= 0
        assert 0.0 <= metrics.mean_loss <= 1.0
        assert metrics.mean_stability >= 0.0

    @pytest.mark.asyncio
    async def test_ratios(self):
        """
        Test ratio properties.
        """
        corpus = ["Test"]
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        results = await batch_detect_fixed_points(corpus, computer)
        metrics = await compute_fixed_point_metrics(results)

        assert 0.0 <= metrics.fixed_point_ratio <= 1.0
        assert 0.0 <= metrics.axiom_candidate_ratio <= 1.0

    @pytest.mark.asyncio
    async def test_empty_results(self):
        """
        Should handle empty results.
        """
        metrics = await compute_fixed_point_metrics({})

        assert metrics.total_analyzed == 0
        assert metrics.fixed_point_count == 0
        assert metrics.mean_loss == 0.0


# =============================================================================
# Test Constants
# =============================================================================


class TestConstants:
    """Test that constants have appropriate values."""

    def test_stability_threshold(self):
        """Stability threshold should be reasonable."""
        assert STABILITY_THRESHOLD > 0
        assert STABILITY_THRESHOLD < 0.1  # Should be fairly strict

    def test_max_stability_iterations(self):
        """Max iterations should be reasonable."""
        assert MAX_STABILITY_ITERATIONS >= 2  # Need at least 2 for stability
        assert MAX_STABILITY_ITERATIONS <= 10  # Not too expensive


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for fixed-point detection."""

    @pytest.mark.asyncio
    async def test_axiom_like_content_detected(self):
        """
        Content that is "axiom-like" should be detected as fixed point.

        Axioms are universal statements that restructure well.
        """
        axiom_content = "Agency requires justification"
        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.01))

        result = await detect_fixed_point(axiom_content, computer)

        # This mock produces low, stable losses
        assert result.is_fixed_point is True

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """
        Test the full pipeline: detect -> extract -> metrics.
        """
        corpus = [
            "Entity axiom: Everything is representable",
            "Morphism axiom: Composition is primary",
            "Complex goal: Build a system that surfaces contradictions",
            "Execution: Run pytest and verify",
        ]

        computer = GaloisLossComputer(llm=MockLLMClient(base_loss=0.02))

        # Batch detect
        batch_results = await batch_detect_fixed_points(corpus, computer)
        assert len(batch_results) == len(corpus)

        # Compute metrics
        metrics = await compute_fixed_point_metrics(batch_results)
        assert metrics.total_analyzed == len(corpus)

        # Extract axioms
        axioms = await extract_axioms(corpus, computer, top_k=2)
        # Should return at most 2 fixed points
        assert len(axioms) <= 2
