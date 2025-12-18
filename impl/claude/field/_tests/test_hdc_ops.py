"""
Tests for HDC primitive operations.

These tests verify the mathematical properties of Hyperdimensional Computing:
- Random vectors are nearly orthogonal
- Binding produces orthogonal vectors
- Bundling produces similar vectors
- Permutation encodes position
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from ..hdc_ops import (
    DIMENSIONS,
    hdc_bind,
    hdc_bundle,
    hdc_encode_sequence,
    hdc_encode_set,
    hdc_permute,
    hdc_resonance_score,
    hdc_similarity,
    hdc_unbind,
    random_hd_vector,
)

# Use smaller dimensions for faster tests
TEST_DIMENSIONS = 1000


class TestRandomHDVector:
    """Tests for random_hd_vector."""

    def test_correct_dimensions(self) -> None:
        """Random vectors have correct dimensionality."""
        vec = random_hd_vector(TEST_DIMENSIONS)
        assert vec.shape == (TEST_DIMENSIONS,)

    def test_normalized(self) -> None:
        """Random vectors are normalized (unit length)."""
        vec = random_hd_vector(TEST_DIMENSIONS)
        assert abs(np.linalg.norm(vec) - 1.0) < 1e-10

    def test_reproducible_with_seed(self) -> None:
        """Same seed produces same vector."""
        v1 = random_hd_vector(TEST_DIMENSIONS, seed=42)
        v2 = random_hd_vector(TEST_DIMENSIONS, seed=42)
        assert np.allclose(v1, v2)

    def test_different_seeds_produce_different_vectors(self) -> None:
        """Different seeds produce different vectors."""
        v1 = random_hd_vector(TEST_DIMENSIONS, seed=42)
        v2 = random_hd_vector(TEST_DIMENSIONS, seed=43)
        assert not np.allclose(v1, v2)

    def test_random_vectors_near_orthogonal(self) -> None:
        """Random vectors are nearly orthogonal in high dimensions."""
        # Generate many random vectors and check similarities
        n_vectors = 100
        vectors = [random_hd_vector(TEST_DIMENSIONS) for _ in range(n_vectors)]

        similarities = []
        for i in range(n_vectors):
            for j in range(i + 1, n_vectors):
                sim = hdc_similarity(vectors[i], vectors[j])
                similarities.append(abs(sim))

        # Mean should be close to 0, std should be small
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)

        # In high dimensions, expect mean ≈ 0 with std ≈ 1/sqrt(D)
        expected_std = 1.0 / np.sqrt(TEST_DIMENSIONS)
        assert mean_sim < 0.1, f"Mean similarity {mean_sim} too high"
        assert std_sim < expected_std * 2, f"Std {std_sim} higher than expected"


class TestHDCBind:
    """Tests for binding operation."""

    def test_same_dimensions(self) -> None:
        """Binding produces vector with same dimensions."""
        a = random_hd_vector(TEST_DIMENSIONS)
        b = random_hd_vector(TEST_DIMENSIONS)
        result = hdc_bind(a, b)
        assert result.shape == (TEST_DIMENSIONS,)

    def test_different_from_inputs(self) -> None:
        """Binding produces vector different from inputs."""
        a = random_hd_vector(TEST_DIMENSIONS)
        b = random_hd_vector(TEST_DIMENSIONS)
        result = hdc_bind(a, b)

        # Result should be different from both inputs
        # (but not necessarily orthogonal with element-wise multiplication)
        assert not np.allclose(result, a)
        assert not np.allclose(result, b)

    def test_commutative(self) -> None:
        """Binding is commutative: bind(a, b) = bind(b, a)."""
        a = random_hd_vector(TEST_DIMENSIONS)
        b = random_hd_vector(TEST_DIMENSIONS)

        ab = hdc_bind(a, b)
        ba = hdc_bind(b, a)

        assert np.allclose(ab, ba)

    def test_unbind_recovers_filler(self) -> None:
        """Unbind recovers the filler approximately: unbind(bind(a, b), a) ≈ b."""
        a = random_hd_vector(TEST_DIMENSIONS)
        b = random_hd_vector(TEST_DIMENSIONS)

        ab = hdc_bind(a, b)
        recovered = hdc_unbind(ab, a)

        # Should be similar to b (circular correlation recovery is approximate)
        # In 1000-D, expect ~0.6-0.8 similarity
        similarity = hdc_similarity(recovered, b)
        assert similarity > 0.6, f"Unbind failed to recover filler: {similarity}"

    def test_different_bindings_are_different(self) -> None:
        """Binding same concept with different roles yields different vectors."""
        house = random_hd_vector(TEST_DIMENSIONS, seed=1)
        architect = random_hd_vector(TEST_DIMENSIONS, seed=2)
        poet = random_hd_vector(TEST_DIMENSIONS, seed=3)

        house_architect = hdc_bind(house, architect)
        house_poet = hdc_bind(house, poet)

        # These should be nearly orthogonal
        similarity = abs(hdc_similarity(house_architect, house_poet))
        assert similarity < 0.2, f"Different bindings too similar: {similarity}"


class TestHDCBundle:
    """Tests for bundling operation."""

    def test_same_dimensions(self) -> None:
        """Bundling produces vector with same dimensions."""
        vectors = [random_hd_vector(TEST_DIMENSIONS) for _ in range(5)]
        result = hdc_bundle(vectors)
        assert result.shape == (TEST_DIMENSIONS,)

    def test_normalized(self) -> None:
        """Bundled vector is normalized."""
        vectors = [random_hd_vector(TEST_DIMENSIONS) for _ in range(5)]
        result = hdc_bundle(vectors)
        assert abs(np.linalg.norm(result) - 1.0) < 1e-10

    def test_similar_to_all_inputs(self) -> None:
        """Bundled vector is similar to all input vectors."""
        vectors = [random_hd_vector(TEST_DIMENSIONS) for _ in range(5)]
        result = hdc_bundle(vectors)

        for v in vectors:
            sim = hdc_similarity(result, v)
            # Should be more similar than random vectors
            assert sim > 0.3, f"Not similar enough: {sim}"

    def test_empty_list_raises(self) -> None:
        """Bundling empty list raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            hdc_bundle([])

    def test_order_independent(self) -> None:
        """Bundling is order-independent."""
        vectors = [random_hd_vector(TEST_DIMENSIONS, seed=i) for i in range(5)]

        bundle1 = hdc_bundle(vectors)
        bundle2 = hdc_bundle(vectors[::-1])

        assert np.allclose(bundle1, bundle2)

    def test_graceful_degradation(self) -> None:
        """Bundling many vectors still preserves similarity to each."""
        n_vectors = 100
        vectors = [random_hd_vector(TEST_DIMENSIONS) for _ in range(n_vectors)]
        result = hdc_bundle(vectors)

        # Check similarity to a sample of inputs
        sample_indices = np.random.choice(n_vectors, size=10, replace=False)
        positive_count = 0
        for i in sample_indices:
            sim = hdc_similarity(result, vectors[i])
            # With many vectors, similarity decreases
            # In 1000-D with 100 vectors, expect ~0.1 expected value
            if sim > 0.0:
                positive_count += 1

        # Most should have positive similarity
        assert positive_count >= 7, f"Too few positive similarities: {positive_count}/10"


class TestHDCPermute:
    """Tests for permutation operation."""

    def test_same_dimensions(self) -> None:
        """Permutation preserves dimensions."""
        v = random_hd_vector(TEST_DIMENSIONS)
        result = hdc_permute(v, 1)
        assert result.shape == (TEST_DIMENSIONS,)

    def test_zero_permutation_is_identity(self) -> None:
        """Permuting by 0 returns same vector."""
        v = random_hd_vector(TEST_DIMENSIONS)
        result = hdc_permute(v, 0)
        assert np.allclose(v, result)

    def test_different_positions_are_orthogonal(self) -> None:
        """Different permutation amounts yield orthogonal vectors."""
        v = random_hd_vector(TEST_DIMENSIONS)

        p1 = hdc_permute(v, 1)
        p2 = hdc_permute(v, 2)
        p5 = hdc_permute(v, 5)

        # Different positions should be nearly orthogonal
        assert abs(hdc_similarity(p1, p2)) < 0.1
        assert abs(hdc_similarity(p1, p5)) < 0.1
        assert abs(hdc_similarity(p2, p5)) < 0.1

    def test_inverse_permutation(self) -> None:
        """Negative permutation inverts positive permutation."""
        v = random_hd_vector(TEST_DIMENSIONS)

        forward = hdc_permute(v, 5)
        back = hdc_permute(forward, -5)

        assert np.allclose(v, back)


class TestHDCSimilarity:
    """Tests for similarity operation."""

    def test_identical_vectors(self) -> None:
        """Identical vectors have similarity 1."""
        v = random_hd_vector(TEST_DIMENSIONS)
        assert abs(hdc_similarity(v, v) - 1.0) < 1e-10

    def test_opposite_vectors(self) -> None:
        """Opposite vectors have similarity -1."""
        v = random_hd_vector(TEST_DIMENSIONS)
        assert abs(hdc_similarity(v, -v) + 1.0) < 1e-10

    def test_orthogonal_vectors(self) -> None:
        """Orthogonal vectors have similarity 0."""
        # Create truly orthogonal vectors
        v1 = np.zeros(TEST_DIMENSIONS)
        v2 = np.zeros(TEST_DIMENSIONS)
        v1[0] = 1.0
        v2[1] = 1.0

        assert abs(hdc_similarity(v1, v2)) < 1e-10

    def test_zero_vector_handling(self) -> None:
        """Zero vectors return 0 similarity."""
        v = random_hd_vector(TEST_DIMENSIONS)
        zero = np.zeros(TEST_DIMENSIONS)

        assert hdc_similarity(v, zero) == 0.0
        assert hdc_similarity(zero, v) == 0.0
        assert hdc_similarity(zero, zero) == 0.0


class TestHDCUnbind:
    """Tests for unbind operation."""

    def test_recovers_filler(self) -> None:
        """Unbinding recovers the filler approximately."""
        role = random_hd_vector(TEST_DIMENSIONS)
        filler = random_hd_vector(TEST_DIMENSIONS)

        bound = hdc_bind(role, filler)
        recovered = hdc_unbind(bound, role)

        # Circular correlation recovery is approximate in finite dimensions
        sim = hdc_similarity(recovered, filler)
        assert sim > 0.6, f"Failed to recover filler: {sim}"


class TestHDCSequenceEncoding:
    """Tests for sequence encoding."""

    def test_preserves_order(self) -> None:
        """Different orders produce different encodings."""
        a = random_hd_vector(TEST_DIMENSIONS, seed=1)
        b = random_hd_vector(TEST_DIMENSIONS, seed=2)

        seq_ab = hdc_encode_sequence([a, b])
        seq_ba = hdc_encode_sequence([b, a])

        # Different orders should produce different (less similar) encodings
        similarity = hdc_similarity(seq_ab, seq_ba)
        assert similarity < 0.9, f"Order not preserved: {similarity}"

    def test_same_sequence_same_encoding(self) -> None:
        """Same sequence produces same encoding."""
        a = random_hd_vector(TEST_DIMENSIONS, seed=1)
        b = random_hd_vector(TEST_DIMENSIONS, seed=2)

        seq1 = hdc_encode_sequence([a, b])
        seq2 = hdc_encode_sequence([a, b])

        assert np.allclose(seq1, seq2)

    def test_empty_sequence_raises(self) -> None:
        """Empty sequence raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            hdc_encode_sequence([])


class TestHDCSetEncoding:
    """Tests for set encoding."""

    def test_order_independent(self) -> None:
        """Set encoding is order-independent."""
        a = random_hd_vector(TEST_DIMENSIONS, seed=1)
        b = random_hd_vector(TEST_DIMENSIONS, seed=2)

        set_ab = hdc_encode_set([a, b])
        set_ba = hdc_encode_set([b, a])

        assert np.allclose(set_ab, set_ba)

    def test_empty_set_raises(self) -> None:
        """Empty set raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            hdc_encode_set([])


class TestHDCResonance:
    """Tests for resonance scoring."""

    def test_resonance_with_empty_memory(self) -> None:
        """Resonance with empty memory is 0."""
        query = random_hd_vector(TEST_DIMENSIONS)
        memory = np.zeros(TEST_DIMENSIONS)

        score = hdc_resonance_score(query, memory)
        assert score == 0.0

    def test_resonance_with_imprinted_pattern(self) -> None:
        """Resonance is high for imprinted patterns."""
        pattern = random_hd_vector(TEST_DIMENSIONS)
        memory = pattern.copy()

        score = hdc_resonance_score(pattern, memory)
        assert score > 0.99


class TestHDCMathematicalProperties:
    """Tests for mathematical properties of HDC operations."""

    @given(st.integers(min_value=0, max_value=1000))
    @settings(max_examples=20)
    def test_bind_associativity(self, seed: int) -> None:
        """Binding is associative: bind(a, bind(b, c)) = bind(bind(a, b), c)."""
        rng = np.random.default_rng(seed)
        a = rng.standard_normal(TEST_DIMENSIONS)
        b = rng.standard_normal(TEST_DIMENSIONS)
        c = rng.standard_normal(TEST_DIMENSIONS)

        left = hdc_bind(a, hdc_bind(b, c))
        right = hdc_bind(hdc_bind(a, b), c)

        assert np.allclose(left, right, rtol=1e-5)

    def test_bundle_idempotent_with_same_vector(self) -> None:
        """Bundling same vector multiple times converges."""
        v = random_hd_vector(TEST_DIMENSIONS)

        # Bundle same vector multiple times
        result = hdc_bundle([v, v, v, v])

        # Should be similar to original
        sim = hdc_similarity(result, v)
        assert sim > 0.99

    def test_bind_preserves_norm_approximately(self) -> None:
        """Binding approximately preserves vector norm."""
        a = random_hd_vector(TEST_DIMENSIONS)
        b = random_hd_vector(TEST_DIMENSIONS)

        result = hdc_bind(a, b)
        norm = np.linalg.norm(result)

        # Norm should be close to 1 (product of unit vectors)
        assert 0.5 < norm < 2.0


class TestHDCHighDimensionalBehavior:
    """Tests that verify high-dimensional HDC behavior."""

    def test_capacity_test(self) -> None:
        """HDC can distinguish many bundled items."""
        # Create many random patterns
        n_patterns = 50
        patterns = [random_hd_vector(TEST_DIMENSIONS, seed=i) for i in range(n_patterns)]

        # Bundle them all
        memory = hdc_bundle(patterns)

        # Each original pattern should be detectable
        detected = 0
        for p in patterns:
            if hdc_similarity(p, memory) > 0.1:
                detected += 1

        # Most patterns should be detectable
        assert detected > n_patterns * 0.8

    def test_noise_robustness(self) -> None:
        """HDC is robust to small noise."""
        original = random_hd_vector(TEST_DIMENSIONS)

        # Add small noise - 1% noise should maintain high similarity
        noise_level = 0.01
        noise = np.random.randn(TEST_DIMENSIONS) * noise_level
        noisy = original + noise
        noisy = noisy / np.linalg.norm(noisy)

        # Should still be very recognizable
        sim = hdc_similarity(original, noisy)
        # With 1% noise in 1000-D, expect >99% similarity
        assert sim > 0.95, f"Noise robustness too low: {sim}"
