"""
Tests for HolographicField class.

These tests verify the high-level HDC memory functionality:
- Symbol codebook management
- Structure encoding
- Morphic resonance (cross-agent learning)
- Memory imprinting
"""

from __future__ import annotations

import numpy as np
import pytest

from ..hdc_ops import hdc_similarity, random_hd_vector
from ..holographic import GLOBAL_HOLOGRAM, HolographicField

# Use smaller dimensions for faster tests
TEST_DIMENSIONS = 1000


class TestHolographicFieldBasics:
    """Basic HolographicField tests."""

    def test_initialization(self) -> None:
        """Field initializes with zero superposition."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        assert np.allclose(field.global_superposition, np.zeros(TEST_DIMENSIONS))
        assert field.imprint_count == 0

    def test_dimensions_property(self) -> None:
        """Dimensions property returns correct value."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        assert field.dimensions == TEST_DIMENSIONS

    def test_repr(self) -> None:
        """repr shows useful information."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        repr_str = repr(field)
        assert "HolographicField" in repr_str
        assert str(TEST_DIMENSIONS) in repr_str


class TestSymbolCodebook:
    """Tests for symbol codebook management."""

    def test_get_symbol_creates_vector(self) -> None:
        """get_symbol creates a vector for new symbols."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        vec = field.get_symbol("house")
        assert vec.shape == (TEST_DIMENSIONS,)
        assert abs(np.linalg.norm(vec) - 1.0) < 1e-10

    def test_get_symbol_is_deterministic(self) -> None:
        """Same symbol name returns same vector."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        v1 = field.get_symbol("house")
        v2 = field.get_symbol("house")
        assert np.allclose(v1, v2)

    def test_different_symbols_are_different(self) -> None:
        """Different symbol names return different vectors."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        house = field.get_symbol("house")
        tree = field.get_symbol("tree")
        assert not np.allclose(house, tree)

    def test_different_symbols_near_orthogonal(self) -> None:
        """Different symbols are nearly orthogonal."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        symbols = ["house", "tree", "car", "dog", "cat"]
        vectors = [field.get_symbol(s) for s in symbols]

        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                sim = abs(hdc_similarity(vectors[i], vectors[j]))
                assert sim < 0.2, f"{symbols[i]} and {symbols[j]} too similar: {sim}"

    def test_codebook_persistence(self) -> None:
        """Codebook persists symbols across calls."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        field.get_symbol("a")
        field.get_symbol("b")
        field.get_symbol("c")

        # Query should find symbols in codebook
        vec_a = field.get_symbol("a")
        results = field.query(vec_a, threshold=0.5)
        assert any(name == "a" for name, _ in results)


class TestBindOperation:
    """Tests for bind operation."""

    def test_bind_creates_new_concept(self) -> None:
        """Binding creates a new concept different from inputs."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        house = field.get_symbol("house")
        architect = field.get_symbol("architect")

        bound = field.bind(house, architect)

        # Should be different from both
        assert not np.allclose(bound, house)
        assert not np.allclose(bound, architect)

    def test_different_bindings_are_different(self) -> None:
        """Same concept bound to different roles yields different vectors."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        house = field.get_symbol("house")
        architect = field.get_symbol("architect")
        poet = field.get_symbol("poet")

        house_architect = field.bind(house, architect)
        house_poet = field.bind(house, poet)

        # Should be nearly orthogonal
        sim = abs(hdc_similarity(house_architect, house_poet))
        assert sim < 0.2, f"Different bindings too similar: {sim}"


class TestBundleOperation:
    """Tests for bundle operation."""

    def test_bundle_similar_to_all(self) -> None:
        """Bundled vector is similar to all inputs."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        concepts = ["house", "home", "dwelling", "residence"]
        vectors = [field.get_symbol(c) for c in concepts]

        bundled = field.bundle(vectors)

        for v in vectors:
            sim = hdc_similarity(bundled, v)
            assert sim > 0.3, f"Not similar enough: {sim}"


class TestPermuteOperation:
    """Tests for permute operation."""

    def test_permute_encodes_position(self) -> None:
        """Different positions are distinguishable."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        word = field.get_symbol("word")

        pos0 = field.permute(word, 0)
        pos1 = field.permute(word, 1)
        pos2 = field.permute(word, 2)

        # Different positions should be nearly orthogonal
        assert abs(hdc_similarity(pos0, pos1)) < 0.1
        assert abs(hdc_similarity(pos1, pos2)) < 0.1


class TestStructureEncoding:
    """Tests for encode_structure."""

    def test_encode_empty_structure(self) -> None:
        """Empty structure returns zero vector."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        result = field.encode_structure({})
        assert np.allclose(result, np.zeros(TEST_DIMENSIONS))

    def test_encode_simple_structure(self) -> None:
        """Simple structure encodes correctly."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        structure = {"type": "house", "color": "red"}
        result = field.encode_structure(structure)

        assert result.shape == (TEST_DIMENSIONS,)
        assert abs(np.linalg.norm(result) - 1.0) < 1e-10

    def test_same_structure_same_encoding(self) -> None:
        """Same structure produces same encoding."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        structure = {"type": "house", "color": "red"}

        enc1 = field.encode_structure(structure)
        enc2 = field.encode_structure(structure)

        assert np.allclose(enc1, enc2)

    def test_different_structures_different_encodings(self) -> None:
        """Different structures produce different encodings."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        struct1 = {"type": "house", "color": "red"}
        struct2 = {"type": "car", "color": "blue"}

        enc1 = field.encode_structure(struct1)
        enc2 = field.encode_structure(struct2)

        # Should be different (not highly similar)
        sim = hdc_similarity(enc1, enc2)
        assert sim < 0.8

    def test_encode_without_role_binding(self) -> None:
        """Encoding without role binding just bundles values."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        structure = {"type": "house", "color": "red"}

        with_binding = field.encode_structure(structure, role_binding=True)
        without_binding = field.encode_structure(structure, role_binding=False)

        # Should produce different results
        sim = hdc_similarity(with_binding, without_binding)
        assert sim < 0.9

    def test_similar_structures_somewhat_similar(self) -> None:
        """Structures with shared fields are somewhat similar."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        struct1 = {"type": "house", "color": "red"}
        struct2 = {"type": "house", "color": "blue"}

        enc1 = field.encode_structure(struct1)
        enc2 = field.encode_structure(struct2)

        # Sharing "type: house" should make them somewhat similar
        sim = hdc_similarity(enc1, enc2)
        assert sim > 0.2, f"Similar structures should be somewhat similar: {sim}"


class TestSequenceEncoding:
    """Tests for encode_sequence."""

    def test_sequence_preserves_order(self) -> None:
        """Different orders produce different encodings."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        seq1 = field.encode_sequence(["a", "b", "c"])
        seq2 = field.encode_sequence(["c", "b", "a"])

        sim = hdc_similarity(seq1, seq2)
        assert sim < 0.9, f"Order not preserved: {sim}"

    def test_same_sequence_same_encoding(self) -> None:
        """Same sequence produces same encoding."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        seq1 = field.encode_sequence(["a", "b", "c"])
        seq2 = field.encode_sequence(["a", "b", "c"])

        assert np.allclose(seq1, seq2)


class TestImprinting:
    """Tests for imprint operation."""

    def test_imprint_increases_count(self) -> None:
        """Imprinting increases imprint count."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        assert field.imprint_count == 0

        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)

        assert field.imprint_count == 1

    def test_imprint_changes_superposition(self) -> None:
        """Imprinting changes global superposition."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        initial = field.global_superposition.copy()

        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)

        assert not np.allclose(field.global_superposition, initial)

    def test_imprint_normalizes(self) -> None:
        """Imprinting keeps superposition normalized."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        for _ in range(100):
            pattern = random_hd_vector(TEST_DIMENSIONS)
            field.imprint(pattern)

        norm = np.linalg.norm(field.global_superposition)
        assert abs(norm - 1.0) < 1e-10

    def test_imprint_strength(self) -> None:
        """Higher strength has more effect (before normalization saturation)."""
        field1 = HolographicField(dimensions=TEST_DIMENSIONS)
        field2 = HolographicField(dimensions=TEST_DIMENSIONS)

        pattern = random_hd_vector(TEST_DIMENSIONS)

        # First imprint something else to avoid both being 1.0 after normalization
        other = random_hd_vector(TEST_DIMENSIONS)
        field1.imprint(other, strength=1.0)
        field2.imprint(other, strength=1.0)

        # Now test strength difference
        field1.imprint(pattern, strength=1.0)
        field2.imprint(pattern, strength=0.1)

        # Higher strength should make superposition more similar to pattern
        sim1 = hdc_similarity(field1.global_superposition, pattern)
        sim2 = hdc_similarity(field2.global_superposition, pattern)

        assert sim1 > sim2, f"sim1={sim1}, sim2={sim2}"


class TestResonance:
    """Tests for resonate operation."""

    def test_resonance_empty_field(self) -> None:
        """Resonance with empty field is 0."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        query = random_hd_vector(TEST_DIMENSIONS)

        resonance = field.resonate(query)
        assert resonance == 0.0

    def test_resonance_with_imprinted_pattern(self) -> None:
        """Resonance is high for imprinted patterns."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        pattern = random_hd_vector(TEST_DIMENSIONS)

        field.imprint(pattern)
        resonance = field.resonate(pattern)

        assert resonance > 0.9

    def test_resonance_with_similar_pattern(self) -> None:
        """Resonance is moderate for similar patterns."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint a structure
        struct1 = {"problem": "auth", "solution": "jwt"}
        pattern1 = field.encode_structure(struct1)
        field.imprint(pattern1)

        # Query with similar structure
        struct2 = {"problem": "auth", "solution": "oauth"}
        pattern2 = field.encode_structure(struct2)

        resonance = field.resonate(pattern2)
        # Should have some resonance due to shared "problem: auth"
        assert resonance > 0.2

    def test_resonance_with_unrelated_pattern(self) -> None:
        """Resonance is low for unrelated patterns."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint one pattern
        pattern1 = field.encode_structure({"topic": "cooking", "dish": "pasta"})
        field.imprint(pattern1)

        # Query with unrelated pattern
        pattern2 = field.encode_structure({"topic": "astronomy", "object": "star"})

        resonance = field.resonate(pattern2)
        assert abs(resonance) < 0.3


class TestMorphicResonance:
    """Tests for morphic resonance - the key feature."""

    def test_morphic_resonance_basic(self) -> None:
        """Agent B feels Agent A's learning (the core test)."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Agent A learns something
        pattern_a = field.encode_structure({"problem": "auth", "solution": "jwt"})
        field.imprint(pattern_a)

        # Agent B queries with similar problem (no direct communication!)
        query_b = field.encode_structure({"problem": "auth"})
        resonance = field.resonate(query_b)

        # Agent B should "feel" Agent A's learning
        assert resonance > 0.3, f"Agent B should feel Agent A's learning: {resonance}"

    def test_morphic_resonance_multiple_agents(self) -> None:
        """Multiple agents' learning accumulates."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Multiple agents learn auth-related things
        patterns = [
            field.encode_structure({"problem": "auth", "solution": "jwt"}),
            field.encode_structure({"problem": "auth", "solution": "oauth"}),
            field.encode_structure({"problem": "auth", "solution": "saml"}),
        ]

        for p in patterns:
            field.imprint(p)

        # New agent queries about auth
        query = field.encode_structure({"problem": "auth"})
        resonance = field.resonate(query)

        # Should have strong resonance with accumulated knowledge
        assert resonance > 0.4

    def test_morphic_resonance_different_topics(self) -> None:
        """Resonance distinguishes between topics."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint auth patterns
        auth_pattern = field.encode_structure({"domain": "auth", "method": "jwt"})
        field.imprint(auth_pattern)

        # Query auth vs database
        auth_query = field.encode_structure({"domain": "auth"})
        db_query = field.encode_structure({"domain": "database"})

        auth_resonance = field.resonate(auth_query)
        db_resonance = field.resonate(db_query)

        # Auth query should resonate more than DB query
        assert auth_resonance > db_resonance


class TestQuery:
    """Tests for query operation."""

    def test_query_empty_codebook(self) -> None:
        """Query on empty codebook returns empty list."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        pattern = random_hd_vector(TEST_DIMENSIONS)

        results = field.query(pattern)
        assert results == []

    def test_query_finds_similar_symbols(self) -> None:
        """Query finds symbols above threshold."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Create some symbols
        house = field.get_symbol("house")
        _ = field.get_symbol("tree")
        _ = field.get_symbol("car")

        # Query for house
        results = field.query(house, threshold=0.9)

        # Should find house
        assert any(name == "house" for name, _ in results)

    def test_query_respects_threshold(self) -> None:
        """Query respects similarity threshold."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Create symbols
        for name in ["a", "b", "c", "d", "e"]:
            field.get_symbol(name)

        # Create query that's similar to one symbol
        query = field.get_symbol("a")

        # High threshold should only find exact match
        high_results = field.query(query, threshold=0.99)
        assert len(high_results) == 1

        # Lower threshold might find more
        low_results = field.query(query, threshold=0.1)
        assert len(low_results) >= 1


class TestUnbind:
    """Tests for unbind operation."""

    def test_unbind_recovers_filler(self) -> None:
        """Unbinding recovers the filler approximately."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        role = field.get_symbol("role")
        filler = field.get_symbol("filler")

        bound = field.bind(role, filler)
        recovered = field.unbind(bound, role)

        # Circular correlation recovery is approximate
        sim = hdc_similarity(recovered, filler)
        assert sim > 0.6, f"Unbind recovery too low: {sim}"


class TestClearAndFork:
    """Tests for clear and fork operations."""

    def test_clear_resets_field(self) -> None:
        """Clear resets global superposition."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)
        assert field.imprint_count > 0

        field.clear()

        assert field.imprint_count == 0
        assert np.allclose(field.global_superposition, np.zeros(TEST_DIMENSIONS))

    def test_fork_creates_independent_copy(self) -> None:
        """Fork creates independent copy."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)

        forked = field.fork()

        # Forked should have same state
        assert np.allclose(forked.global_superposition, field.global_superposition)

        # Changes to forked should not affect original
        forked.imprint(random_hd_vector(TEST_DIMENSIONS))
        assert not np.allclose(forked.global_superposition, field.global_superposition)

    def test_fork_shares_codebook(self) -> None:
        """Forked field shares codebook."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        field.get_symbol("test")

        forked = field.fork()

        # Same symbol should return same vector
        assert np.allclose(field.get_symbol("test"), forked.get_symbol("test"))


class TestGlobalHologram:
    """Tests for GLOBAL_HOLOGRAM singleton."""

    def test_global_hologram_exists(self) -> None:
        """GLOBAL_HOLOGRAM is a HolographicField."""
        assert isinstance(GLOBAL_HOLOGRAM, HolographicField)

    def test_global_hologram_has_default_dimensions(self) -> None:
        """GLOBAL_HOLOGRAM has default dimensions."""
        from ..hdc_ops import DIMENSIONS

        assert GLOBAL_HOLOGRAM.dimensions == DIMENSIONS


class TestSimilarity:
    """Tests for similarity method."""

    def test_similarity_identical(self) -> None:
        """Similarity of identical vectors is 1."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        v = random_hd_vector(TEST_DIMENSIONS)
        assert abs(field.similarity(v, v) - 1.0) < 1e-10

    def test_similarity_orthogonal(self) -> None:
        """Similarity of orthogonal vectors is 0."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        v1 = np.zeros(TEST_DIMENSIONS)
        v2 = np.zeros(TEST_DIMENSIONS)
        v1[0] = 1.0
        v2[1] = 1.0

        assert abs(field.similarity(v1, v2)) < 1e-10
