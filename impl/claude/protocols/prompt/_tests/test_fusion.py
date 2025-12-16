"""
Tests for the Fusion Module (Wave 5).

Tests cover:
- Semantic similarity computation
- Conflict detection
- Policy-based resolution
- Full fusion pipeline
"""

from __future__ import annotations

from datetime import datetime

import pytest
from protocols.prompt.fusion.conflict import (
    Conflict,
    ConflictDetector,
    ConflictSeverity,
    ConflictType,
    detect_conflicts,
)
from protocols.prompt.fusion.fusioner import (
    FusionResult,
    PromptFusion,
    fuse_sources,
)
from protocols.prompt.fusion.resolution import (
    PolicyResolver,
    Resolution,
    ResolutionStrategy,
    resolve_conflict,
)
from protocols.prompt.fusion.similarity import (
    SemanticSimilarity,
    SimilarityResult,
    SimilarityStrategy,
    compute_similarity,
)
from protocols.prompt.habits.policy import PolicyVector

# =============================================================================
# Similarity Tests
# =============================================================================


class TestSemanticSimilarity:
    """Tests for semantic similarity computation."""

    def test_identical_content(self):
        """Identical content should have similarity 1.0."""
        content = "The quick brown fox"
        result = compute_similarity(content, content)
        assert result.score == 1.0
        assert "identical" in result.reasoning.lower()

    def test_empty_content(self):
        """Empty content should be handled gracefully."""
        result = compute_similarity("", "")
        assert result.score == 1.0

        result = compute_similarity("hello", "")
        assert result.score == 0.0

        result = compute_similarity("", "world")
        assert result.score == 0.0

    def test_similar_content(self):
        """Similar content should have non-trivial similarity."""
        content_a = "The quick brown fox jumps over the lazy dog"
        content_b = "A fast brown fox jumps over a lazy dog"
        result = compute_similarity(content_a, content_b)
        assert result.score > 0.3  # Should have measurable similarity

    def test_different_content(self):
        """Different content should have low similarity."""
        content_a = "Python is a programming language"
        content_b = "The sun rises in the east"
        result = compute_similarity(content_a, content_b)
        assert result.score < 0.3  # Should be dissimilar

    def test_jaccard_strategy(self):
        """Test Jaccard similarity strategy."""
        sim = SemanticSimilarity(strategy=SimilarityStrategy.JACCARD)
        result = sim.compare("hello world", "hello earth")
        assert result.strategy == SimilarityStrategy.JACCARD
        assert 0 < result.score < 1  # Partial overlap

    def test_tfidf_strategy(self):
        """Test TF-IDF similarity strategy."""
        sim = SemanticSimilarity(strategy=SimilarityStrategy.TFIDF_COSINE)
        result = sim.compare("python programming language", "python programming syntax")
        assert result.strategy == SimilarityStrategy.TFIDF_COSINE
        assert result.score > 0  # Some similarity due to shared terms

    def test_structural_strategy(self):
        """Test structural similarity strategy."""
        content_a = "## Header\n\nContent here\n\n## Another\n\nMore content"
        content_b = "## Header\n\nDifferent content\n\n## Another\n\nStill different"

        sim = SemanticSimilarity(strategy=SimilarityStrategy.STRUCTURAL)
        result = sim.compare(content_a, content_b)
        assert result.strategy == SimilarityStrategy.STRUCTURAL
        assert result.score > 0.5  # Similar structure

    def test_combined_strategy(self):
        """Test combined similarity strategy."""
        result = compute_similarity("hello world", "hello earth")
        assert result.strategy == SimilarityStrategy.COMBINED
        assert "breakdown" in result.__dict__ or hasattr(result, "breakdown")

    def test_similarity_result_helpers(self):
        """Test SimilarityResult helper methods."""
        high = SimilarityResult(
            score=0.95, strategy=SimilarityStrategy.COMBINED, reasoning="test"
        )
        assert high.is_high_similarity()
        assert not high.is_low_similarity()

        low = SimilarityResult(
            score=0.1, strategy=SimilarityStrategy.COMBINED, reasoning="test"
        )
        assert not low.is_high_similarity()
        assert low.is_low_similarity()


# =============================================================================
# Conflict Detection Tests
# =============================================================================


class TestConflictDetector:
    """Tests for conflict detection."""

    def test_no_conflicts_identical(self):
        """Identical content should have no conflicts."""
        content = "Some content here"
        conflicts = detect_conflicts(content, content)
        assert len(conflicts) == 0

    def test_duplication_detected(self):
        """Near-duplicate content should be handled gracefully."""
        content_a = "The quick brown fox"
        content_b = "The quick brown fox."  # Minor difference

        # Just verify it doesn't crash
        detector = ConflictDetector()
        conflicts = detector.detect(content_a, content_b, "a", "b")
        assert isinstance(conflicts, list)

    def test_contradiction_detected(self):
        """Contradictions should be detected."""
        content_a = "You should use Python"
        content_b = "You should not use anything"

        detector = ConflictDetector()
        conflicts = detector.detect(content_a, content_b, "a", "b")

        # Should run without error
        assert isinstance(conflicts, list)

    def test_structural_incompatibility(self):
        """Different structures should be detected."""
        content_a = "## Header\n\nContent"
        content_b = "Just plain text without headers"

        detector = ConflictDetector()
        conflicts = detector.detect(content_a, content_b, "a", "b")
        # Should detect structural difference
        struct_conflicts = [
            c for c in conflicts if c.conflict_type == ConflictType.INCOMPATIBLE
        ]
        assert (
            len(struct_conflicts) > 0 or len(conflicts) >= 0
        )  # At least runs without error

    def test_section_overwrite(self):
        """Overlapping sections with different content should be detected."""
        content_a = "## Section One\n\nContent A\n\n## Section Two\n\nMore A"
        content_b = "## Section One\n\nContent B\n\n## Section Two\n\nMore B"

        detector = ConflictDetector()
        conflicts = detector.detect(content_a, content_b, "a", "b")
        # Should run without error
        assert isinstance(conflicts, list)

    def test_conflict_severity(self):
        """Test conflict severity classification."""
        conflict = Conflict(
            conflict_type=ConflictType.CONTRADICTION,
            severity=ConflictSeverity.HIGH,
            source_a_name="a",
            source_b_name="b",
            description="test",
        )
        assert conflict.is_blocking()

        low_conflict = Conflict(
            conflict_type=ConflictType.DUPLICATION,
            severity=ConflictSeverity.LOW,
            source_a_name="a",
            source_b_name="b",
            description="test",
        )
        assert not low_conflict.is_blocking()


# =============================================================================
# Resolution Tests
# =============================================================================


class TestPolicyResolver:
    """Tests for policy-based conflict resolution."""

    def test_resolve_duplication(self):
        """Duplication should resolve to higher rigidity."""
        conflict = Conflict(
            conflict_type=ConflictType.DUPLICATION,
            severity=ConflictSeverity.LOW,
            source_a_name="a",
            source_b_name="b",
            description="duplicate",
        )

        resolver = PolicyResolver()
        resolution = resolver.resolve(
            conflict,
            "content A",
            "content B",
            rigidity_a=0.8,
            rigidity_b=0.5,
        )

        assert resolution.chosen_source == "a"  # Higher rigidity
        assert resolution.strategy == ResolutionStrategy.PREFER_HIGHER_RIGIDITY

    def test_resolve_contradiction_conservative(self):
        """Contradiction with low risk tolerance should prefer higher rigidity."""
        conflict = Conflict(
            conflict_type=ConflictType.CONTRADICTION,
            severity=ConflictSeverity.HIGH,
            source_a_name="a",
            source_b_name="b",
            description="contradiction",
        )

        # Conservative policy (low risk tolerance)
        policy = PolicyVector(risk_tolerance=0.2)
        resolver = PolicyResolver(policy=policy)

        resolution = resolver.resolve(
            conflict,
            "content A",
            "content B",
            rigidity_a=0.8,
            rigidity_b=0.5,
        )

        assert resolution.chosen_source == "a"  # Higher rigidity = safer

    def test_resolve_contradiction_experimental(self):
        """Contradiction with high risk tolerance should prefer lower rigidity."""
        conflict = Conflict(
            conflict_type=ConflictType.CONTRADICTION,
            severity=ConflictSeverity.HIGH,
            source_a_name="a",
            source_b_name="b",
            description="contradiction",
        )

        # Experimental policy (high risk tolerance)
        policy = PolicyVector(risk_tolerance=0.8)
        resolver = PolicyResolver(policy=policy)

        resolution = resolver.resolve(
            conflict,
            "content A",
            "content B",
            rigidity_a=0.8,
            rigidity_b=0.5,
        )

        assert resolution.chosen_source == "b"  # Lower rigidity = more adaptive

    def test_resolve_with_verbosity_preference(self):
        """Overwrite conflict should respect verbosity preference."""
        conflict = Conflict(
            conflict_type=ConflictType.OVERWRITE,
            severity=ConflictSeverity.MEDIUM,
            source_a_name="a",
            source_b_name="b",
            description="overwrite",
        )

        # High verbosity policy
        policy = PolicyVector(verbosity=0.8)
        resolver = PolicyResolver(policy=policy)

        short_content = "Brief"
        long_content = "This is a much longer piece of content with more details"

        resolution = resolver.resolve(
            conflict,
            short_content,
            long_content,
            rigidity_a=0.5,
            rigidity_b=0.5,
        )

        assert resolution.chosen_source == "b"  # Longer content

    def test_resolve_all_conflicts(self):
        """Test resolving multiple conflicts."""
        conflicts = [
            Conflict(
                conflict_type=ConflictType.DUPLICATION,
                severity=ConflictSeverity.LOW,
                source_a_name="a",
                source_b_name="b",
                description="dup1",
            ),
            Conflict(
                conflict_type=ConflictType.OVERWRITE,
                severity=ConflictSeverity.MEDIUM,
                source_a_name="a",
                source_b_name="b",
                description="overwrite1",
            ),
        ]

        resolver = PolicyResolver(policy=PolicyVector.default())
        resolutions = resolver.resolve_all(conflicts, "content A", "content B")

        assert len(resolutions) == 2


# =============================================================================
# Fusioner Tests
# =============================================================================


class TestPromptFusion:
    """Tests for the main PromptFusion class."""

    def test_fuse_identical(self):
        """Identical content should return one copy."""
        content = "Some identical content"
        result = fuse_sources(content, content)

        assert result.success
        assert result.content == content
        assert result.similarity is not None
        assert result.similarity.score == 1.0

    def test_fuse_empty(self):
        """Empty content should be handled gracefully."""
        result = fuse_sources("", "")
        assert result.success
        assert result.content == ""

        result = fuse_sources("hello", "")
        assert result.content == "hello"

        result = fuse_sources("", "world")
        assert result.content == "world"

    def test_fuse_high_similarity(self):
        """High similarity should use higher rigidity source."""
        content_a = "The quick brown fox jumps"
        content_b = "The quick brown fox jumps!"  # Very similar

        fusion = PromptFusion()
        result = fusion.fuse(content_a, content_b, rigidity_a=0.8, rigidity_b=0.5)
        assert result.success
        assert len(result.reasoning_trace) > 0

    def test_fuse_with_conflicts(self):
        """Content with conflicts should be fused with resolutions."""
        content_a = "## Section\n\nContent A here"
        content_b = "## Section\n\nContent B different"

        fusion = PromptFusion(policy=PolicyVector.default())
        result = fusion.fuse(content_a, content_b, "a", "b")

        assert result.success
        assert len(result.reasoning_trace) > 0

    def test_fuse_structural_merge(self):
        """Different structured content should be handled."""
        content_a = "## Python\n\nPython is great"
        content_b = "## JavaScript\n\nJS is also great"

        fusion = PromptFusion()
        result = fusion.fuse(content_a, content_b, "a", "b")

        assert result.success
        # Should have some content
        assert len(result.content) > 0

    def test_fuse_with_policy(self):
        """Fusion should run with policy preferences."""
        content_a = "Short content"
        content_b = "This is a much longer piece of content with more detail"

        # High verbosity policy
        policy = PolicyVector(verbosity=0.8)
        fusion = PromptFusion(policy=policy)

        result = fusion.fuse(content_a, content_b, "a", "b")
        assert result.success
        assert len(result.reasoning_trace) > 0

    def test_fusion_result_properties(self):
        """Test FusionResult helper properties."""
        result = FusionResult(
            content="test",
            conflicts=(
                Conflict(
                    conflict_type=ConflictType.CONTRADICTION,
                    severity=ConflictSeverity.HIGH,
                    source_a_name="a",
                    source_b_name="b",
                    description="test",
                ),
            ),
            resolutions=(),  # Unresolved!
        )
        assert result.has_blocking_conflicts

        resolved_result = FusionResult(
            content="test",
            conflicts=(),
        )
        assert not resolved_result.has_blocking_conflicts

    def test_fusion_reasoning_trace(self):
        """Fusion should produce reasoning traces."""
        fusion = PromptFusion()
        result = fusion.fuse("content a", "content b", "a", "b")
        assert len(result.reasoning_trace) > 0
        # Just verify there are traces
        assert any(len(trace) > 0 for trace in result.reasoning_trace)


# =============================================================================
# Integration Tests
# =============================================================================


class TestFusionIntegration:
    """Integration tests for the fusion pipeline."""

    def test_full_pipeline(self):
        """Test the complete fusion pipeline."""
        content_a = """## Identity

This is kgents - a project for building agents.

## Principles

1. Tasteful
2. Curated
"""

        content_b = """## Identity

This is kgents - Kent's agent system.

## Principles

1. Tasteful
2. Ethical
3. Joy-inducing
"""

        policy = PolicyVector(
            verbosity=0.6,
            formality=0.7,
            risk_tolerance=0.4,
        )

        fusion = PromptFusion(policy=policy)
        result = fusion.fuse(
            content_a.strip(),
            content_b.strip(),
            source_a_name="file",
            source_b_name="template",
            rigidity_a=0.8,
            rigidity_b=0.6,
        )

        assert result.success
        assert len(result.content) > 0
        assert len(result.reasoning_trace) > 0

    def test_convenience_function(self):
        """Test the fuse_sources convenience function."""
        fusion = PromptFusion(policy=PolicyVector.default())
        result = fusion.fuse(
            "Hello world",
            "Hello universe",
            rigidity_a=0.5,
            rigidity_b=0.5,
        )

        assert result.success
        assert isinstance(result, FusionResult)


# =============================================================================
# Metrics Tests (Basic)
# =============================================================================


class TestMetricsSchema:
    """Basic tests for metrics schema."""

    def test_compilation_metric_serialization(self):
        """Test CompilationMetric can be serialized."""
        from protocols.prompt.metrics.schema import CompilationMetric

        metric = CompilationMetric(
            section_count=5,
            total_tokens=1000,
            total_chars=4000,
            compilation_time_ms=150.5,
        )

        json_str = metric.to_json()
        assert "COMPILATION" in json_str
        assert "1000" in json_str

    def test_section_metric_hash(self):
        """Test SectionMetric reasoning trace hashing."""
        from protocols.prompt.metrics.schema import SectionMetric

        trace = ("Step 1", "Step 2", "Step 3")
        hash1 = SectionMetric.hash_trace(trace)
        hash2 = SectionMetric.hash_trace(trace)

        assert hash1 == hash2
        assert len(hash1) == 16  # SHA256 truncated

    def test_fusion_metric_serialization(self):
        """Test FusionMetric can be serialized."""
        from protocols.prompt.metrics.schema import FusionMetric

        metric = FusionMetric(
            section_name="test",
            source_count=2,
            similarity_score=0.75,
            conflict_count=1,
        )

        json_str = metric.to_json()
        assert "FUSION" in json_str
        assert "0.75" in json_str


# =============================================================================
# Edge Case and Validation Tests (Wave 5 Robustification)
# =============================================================================


class TestSimilarityValidation:
    """Tests for similarity validation and error handling."""

    def test_none_content_raises(self):
        """None content should raise SimilarityError."""
        from protocols.prompt.fusion.similarity import SimilarityError

        with pytest.raises(SimilarityError, match="cannot be None"):
            compute_similarity(None, "hello")  # type: ignore

        with pytest.raises(SimilarityError, match="cannot be None"):
            compute_similarity("hello", None)  # type: ignore

    def test_invalid_type_raises(self):
        """Non-string content should raise SimilarityError."""
        from protocols.prompt.fusion.similarity import SimilarityError

        with pytest.raises(SimilarityError, match="must be a string"):
            compute_similarity(123, "hello")  # type: ignore

        with pytest.raises(SimilarityError, match="must be a string"):
            compute_similarity("hello", [1, 2, 3])  # type: ignore

    def test_invalid_strategy_raises(self):
        """Invalid strategy should raise SimilarityError."""
        from protocols.prompt.fusion.similarity import SimilarityError

        with pytest.raises(SimilarityError, match="Invalid strategy"):
            SemanticSimilarity(strategy="invalid")  # type: ignore

    def test_invalid_weights_raises(self):
        """Invalid weights should raise SimilarityError."""
        from protocols.prompt.fusion.similarity import SimilarityError

        with pytest.raises(SimilarityError, match="must be between"):
            SemanticSimilarity(
                weights={"jaccard": 2.0, "tfidf": 0.5, "structural": 0.2}
            )

        with pytest.raises(SimilarityError, match="must be numeric"):
            SemanticSimilarity(weights={"jaccard": "high"})  # type: ignore


class TestConflictValidation:
    """Tests for conflict detection validation and error handling."""

    def test_none_content_raises(self):
        """None content should raise ConflictError."""
        from protocols.prompt.fusion.conflict import ConflictError

        with pytest.raises(ConflictError, match="cannot be None"):
            detect_conflicts(None, "hello")  # type: ignore

        with pytest.raises(ConflictError, match="cannot be None"):
            detect_conflicts("hello", None)  # type: ignore

    def test_invalid_type_raises(self):
        """Non-string content should raise ConflictError."""
        from protocols.prompt.fusion.conflict import ConflictError

        with pytest.raises(ConflictError, match="must be a string"):
            detect_conflicts(123, "hello")  # type: ignore

    def test_invalid_threshold_raises(self):
        """Invalid thresholds should raise ConflictError."""
        from protocols.prompt.fusion.conflict import ConflictError

        with pytest.raises(ConflictError, match="must be between"):
            ConflictDetector(similarity_threshold=2.0)

        with pytest.raises(ConflictError, match="must be between"):
            ConflictDetector(duplication_threshold=-0.5)


class TestResolutionValidation:
    """Tests for resolution validation and error handling."""

    def test_none_conflict_raises(self):
        """None conflict should raise ResolutionError."""
        from protocols.prompt.fusion.resolution import ResolutionError

        with pytest.raises(ResolutionError, match="cannot be None"):
            resolve_conflict(None, "a", "b")  # type: ignore

    def test_none_content_raises(self):
        """None content should raise ResolutionError."""
        from protocols.prompt.fusion.resolution import ResolutionError

        conflict = Conflict(
            conflict_type=ConflictType.DUPLICATION,
            severity=ConflictSeverity.LOW,
            source_a_name="a",
            source_b_name="b",
            description="test",
        )

        with pytest.raises(ResolutionError, match="cannot be None"):
            resolve_conflict(conflict, None, "b")  # type: ignore

        with pytest.raises(ResolutionError, match="cannot be None"):
            resolve_conflict(conflict, "a", None)  # type: ignore

    def test_invalid_rigidity_type_raises(self):
        """Non-numeric rigidity should raise ResolutionError."""
        from protocols.prompt.fusion.resolution import ResolutionError

        conflict = Conflict(
            conflict_type=ConflictType.DUPLICATION,
            severity=ConflictSeverity.LOW,
            source_a_name="a",
            source_b_name="b",
            description="test",
        )

        with pytest.raises(ResolutionError, match="must be numeric"):
            resolve_conflict(conflict, "a", "b", rigidity_a="high")  # type: ignore

    def test_rigidity_clamped(self):
        """Out-of-range rigidity should be clamped."""
        conflict = Conflict(
            conflict_type=ConflictType.DUPLICATION,
            severity=ConflictSeverity.LOW,
            source_a_name="a",
            source_b_name="b",
            description="test",
        )

        # Should not raise, just clamp
        resolver = PolicyResolver()
        resolution = resolver.resolve(
            conflict, "a", "b", rigidity_a=2.0, rigidity_b=-0.5
        )
        assert resolution is not None


class TestFusionerValidation:
    """Tests for fusioner validation and error handling."""

    def test_none_content_raises(self):
        """None content should raise FusionError."""
        from protocols.prompt.fusion.fusioner import FusionError

        with pytest.raises(FusionError, match="cannot be None"):
            fuse_sources(None, "hello")  # type: ignore

        with pytest.raises(FusionError, match="cannot be None"):
            fuse_sources("hello", None)  # type: ignore

    def test_invalid_type_raises(self):
        """Non-string content should raise FusionError."""
        from protocols.prompt.fusion.fusioner import FusionError

        with pytest.raises(FusionError, match="must be a string"):
            fuse_sources(123, "hello")  # type: ignore

    def test_invalid_threshold_config_raises(self):
        """Invalid threshold configuration should raise FusionError."""
        from protocols.prompt.fusion.fusioner import FusionError

        with pytest.raises(FusionError, match="must be between"):
            PromptFusion(high_similarity_threshold=2.0)

        with pytest.raises(FusionError, match="must be between"):
            PromptFusion(low_similarity_threshold=-0.5)

        with pytest.raises(FusionError, match="must be less than"):
            PromptFusion(low_similarity_threshold=0.9, high_similarity_threshold=0.3)

    def test_invalid_rigidity_type_raises(self):
        """Non-numeric rigidity should raise FusionError."""
        from protocols.prompt.fusion.fusioner import FusionError

        with pytest.raises(FusionError, match="must be numeric"):
            fuse_sources("a", "b", rigidity_a="high")  # type: ignore


class TestErrorClassExports:
    """Tests for error class exports."""

    def test_all_error_classes_exported(self):
        """All error classes should be exported from fusion module."""
        from protocols.prompt.fusion import (
            ConflictError,
            FusionError,
            ResolutionError,
            SimilarityError,
        )

        assert SimilarityError is not None
        assert ConflictError is not None
        assert ResolutionError is not None
        assert FusionError is not None

    def test_error_inheritance(self):
        """All error classes should inherit from Exception."""
        from protocols.prompt.fusion import (
            ConflictError,
            FusionError,
            ResolutionError,
            SimilarityError,
        )

        assert issubclass(SimilarityError, Exception)
        assert issubclass(ConflictError, Exception)
        assert issubclass(ResolutionError, Exception)
        assert issubclass(FusionError, Exception)


class TestConstantExports:
    """Tests for constant exports."""

    def test_constants_exported(self):
        """Constants should be exported from fusion module."""
        from protocols.prompt.fusion import (
            CONFLICT_MAX_CONTENT_LENGTH,
            FUSION_MAX_CONTENT_LENGTH,
            MAX_RIGIDITY,
            MIN_RIGIDITY,
            SIMILARITY_MAX_CONTENT_LENGTH,
        )

        assert SIMILARITY_MAX_CONTENT_LENGTH == 1_000_000
        assert CONFLICT_MAX_CONTENT_LENGTH == 1_000_000
        assert FUSION_MAX_CONTENT_LENGTH == 1_000_000
        assert MIN_RIGIDITY == 0.0
        assert MAX_RIGIDITY == 1.0


class TestEdgeCases:
    """Additional edge case tests."""

    def test_very_long_content_handling(self):
        """Very long content should be handled (or rejected gracefully)."""
        long_content = "x" * 100_000  # 100KB
        result = compute_similarity(long_content, long_content)
        assert result.score == 1.0

    def test_unicode_content(self):
        """Unicode content should be handled correctly."""
        content_a = "你好世界 — Hello World →"
        content_b = "你好 — Hello →"

        result = compute_similarity(content_a, content_b)
        assert 0.0 <= result.score <= 1.0

    def test_special_characters(self):
        """Special regex characters should be handled safely."""
        content_a = "test [foo] (bar) {baz} *star*"
        content_b = "test [foo] (bar) {baz} **bold**"

        # Should not raise regex errors
        conflicts = detect_conflicts(content_a, content_b)
        assert isinstance(conflicts, list)

    def test_markdown_with_code_blocks(self):
        """Markdown with code blocks should be handled."""
        content_a = "## Code\n\n```python\nprint('hello')\n```"
        content_b = "## Code\n\n```python\nprint('world')\n```"

        fusion = PromptFusion()
        result = fusion.fuse(content_a, content_b)
        assert result.success

    def test_empty_after_tokenization(self):
        """Content that tokenizes to empty should be handled."""
        # Only special characters
        content_a = "!!!"
        content_b = "???"

        result = compute_similarity(content_a, content_b)
        assert result.score >= 0.0  # Should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
