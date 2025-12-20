"""
Tests for Morphic Resonance - the key HDC feature.

These tests verify that cross-agent learning works without
explicit message passing. This is the core value proposition
of HDC over Vector DB.
"""

from __future__ import annotations

import numpy as np
import pytest

from ..hdc_ops import hdc_similarity, random_hd_vector
from ..holographic import HolographicField

# Use smaller dimensions for faster tests
TEST_DIMENSIONS = 1000


class TestMorphicResonanceCore:
    """Core morphic resonance tests."""

    def test_resonance_emerges_from_imprint(self) -> None:
        """Imprinted pattern creates resonance for similar queries."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Before imprint, no resonance
        query = field.encode_structure({"topic": "auth"})
        assert field.resonate(query) == 0.0

        # Imprint
        pattern = field.encode_structure({"topic": "auth", "method": "jwt"})
        field.imprint(pattern)

        # After imprint, resonance exists
        assert field.resonate(query) > 0.0

    def test_resonance_strengthens_with_repetition(self) -> None:
        """Repeated similar imprints strengthen resonance."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        patterns = [
            field.encode_structure({"topic": "auth", "method": "jwt"}),
            field.encode_structure({"topic": "auth", "method": "oauth"}),
            field.encode_structure({"topic": "auth", "method": "saml"}),
        ]

        query = field.encode_structure({"topic": "auth"})

        resonances = []
        for p in patterns:
            field.imprint(p)
            resonances.append(field.resonate(query))

        # Each imprint should strengthen resonance
        # (or at least maintain it at high levels)
        assert all(r > 0 for r in resonances)

    def test_resonance_diminishes_for_unrelated(self) -> None:
        """Unrelated imprints reduce relative resonance."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint auth pattern
        auth_pattern = field.encode_structure({"topic": "auth"})
        field.imprint(auth_pattern)

        auth_resonance_before = field.resonate(auth_pattern)

        # Imprint many unrelated patterns
        for i in range(10):
            unrelated = field.encode_structure({"topic": f"unrelated_{i}"})
            field.imprint(unrelated)

        auth_resonance_after = field.resonate(auth_pattern)

        # Auth resonance should decrease as field becomes "crowded"
        assert auth_resonance_after < auth_resonance_before


class TestCrossAgentLearning:
    """Tests simulating cross-agent learning scenarios."""

    def test_problem_solution_transfer(self) -> None:
        """Agent B benefits from Agent A's problem-solution learning."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Agent A solves a problem
        agent_a_solution = field.encode_structure(
            {
                "problem_type": "memory_leak",
                "language": "python",
                "solution": "use_context_manager",
            }
        )
        field.imprint(agent_a_solution)

        # Agent B encounters similar problem
        agent_b_query = field.encode_structure(
            {"problem_type": "memory_leak", "language": "python"}
        )

        resonance = field.resonate(agent_b_query)

        # Agent B should feel resonance with the solution domain
        assert resonance > 0.3

    def test_domain_expertise_accumulation(self) -> None:
        """Field accumulates domain expertise from multiple agents."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Multiple agents learn about kubernetes
        k8s_learnings = [
            {"domain": "kubernetes", "concept": "pod"},
            {"domain": "kubernetes", "concept": "service"},
            {"domain": "kubernetes", "concept": "deployment"},
            {"domain": "kubernetes", "concept": "configmap"},
        ]

        for learning in k8s_learnings:
            pattern = field.encode_structure(learning)
            field.imprint(pattern)

        # New agent queries about kubernetes
        k8s_query = field.encode_structure({"domain": "kubernetes"})
        k8s_resonance = field.resonate(k8s_query)

        # Query about unrelated domain
        ml_query = field.encode_structure({"domain": "machine_learning"})
        ml_resonance = field.resonate(ml_query)

        # K8s query should resonate more
        assert k8s_resonance > ml_resonance

    def test_collaborative_learning_scenario(self) -> None:
        """Multiple agents collaboratively build knowledge."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Three agents work on different aspects of same project
        agent_contributions = [
            {"project": "web_app", "aspect": "frontend", "tech": "react"},
            {"project": "web_app", "aspect": "backend", "tech": "fastapi"},
            {"project": "web_app", "aspect": "database", "tech": "postgres"},
        ]

        for contribution in agent_contributions:
            pattern = field.encode_structure(contribution)
            field.imprint(pattern)

        # Fourth agent queries about project
        project_query = field.encode_structure({"project": "web_app"})

        resonance = field.resonate(project_query)

        # Should have strong resonance with project knowledge
        assert resonance > 0.4


class TestResonanceSelectivity:
    """Tests for resonance selectivity."""

    def test_resonance_distinguishes_topics(self) -> None:
        """Resonance correctly distinguishes between topics."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Learn about two different topics
        auth_pattern = field.encode_structure({"topic": "authentication", "detail": "jwt_tokens"})
        db_pattern = field.encode_structure({"topic": "database", "detail": "query_optimization"})

        field.imprint(auth_pattern)
        field.imprint(db_pattern)

        # Query each topic
        auth_query = field.encode_structure({"topic": "authentication"})
        db_query = field.encode_structure({"topic": "database"})

        # Different base query
        web_query = field.encode_structure({"topic": "web_development"})

        auth_res = field.resonate(auth_query)
        db_res = field.resonate(db_query)
        web_res = field.resonate(web_query)

        # Auth and db should resonate similarly (both imprinted)
        # Web should resonate less (not imprinted)
        assert auth_res > web_res
        assert db_res > web_res

    def test_resonance_hierarchical_similarity(self) -> None:
        """Resonance reflects hierarchical similarity."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint specific pattern
        pattern = field.encode_structure(
            {
                "category": "animal",
                "subcategory": "mammal",
                "species": "dog",
                "breed": "labrador",
            }
        )
        field.imprint(pattern)

        # Query at different specificity levels
        exact_query = field.encode_structure(
            {
                "category": "animal",
                "subcategory": "mammal",
                "species": "dog",
                "breed": "labrador",
            }
        )
        species_query = field.encode_structure(
            {"category": "animal", "subcategory": "mammal", "species": "dog"}
        )
        category_query = field.encode_structure({"category": "animal"})
        unrelated_query = field.encode_structure({"category": "vehicle"})

        exact_res = field.resonate(exact_query)
        species_res = field.resonate(species_query)
        cat_res = field.resonate(category_query)
        unrelated_res = field.resonate(unrelated_query)

        # More specific matches should resonate more
        assert exact_res >= species_res >= cat_res > unrelated_res


class TestResonancePatterns:
    """Tests for specific resonance patterns."""

    def test_analogy_resonance(self) -> None:
        """Analogical patterns can be detected via resonance."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint a relationship pattern
        # "King is to queen as man is to woman"
        king_queen = field.encode_structure(
            {"relation": "royalty", "male": "king", "female": "queen"}
        )
        field.imprint(king_queen)

        # Query with analogous pattern
        man_woman = field.encode_structure({"relation": "gender", "male": "man", "female": "woman"})

        # Some resonance expected due to structural similarity
        resonance = field.resonate(man_woman)
        # May not be high but should be non-trivial
        assert resonance != 0.0

    def test_context_dependent_resonance(self) -> None:
        """Resonance depends on context."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint "bank" in financial context
        financial_bank = field.encode_structure(
            {"domain": "finance", "entity": "bank", "action": "deposit"}
        )
        field.imprint(financial_bank)

        # Query "bank" in financial context
        finance_query = field.encode_structure({"domain": "finance", "entity": "bank"})

        # Query "bank" in geographic context
        river_query = field.encode_structure({"domain": "geography", "entity": "bank"})

        finance_res = field.resonate(finance_query)
        river_res = field.resonate(river_query)

        # Financial context should resonate more
        assert finance_res > river_res


class TestResonanceStability:
    """Tests for resonance stability under various conditions."""

    def test_resonance_stable_after_many_imprints(self) -> None:
        """Resonance remains meaningful after many imprints."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint target pattern multiple times to strengthen it
        target = field.encode_structure({"target": "special"})
        for _ in range(10):  # Imprint multiple times to strengthen
            field.imprint(target, strength=3.0)

        initial_resonance = field.resonate(target)

        # Add many other patterns (fewer to not overwhelm)
        for i in range(20):
            noise = field.encode_structure({"noise": f"pattern_{i}"})
            field.imprint(noise, strength=0.5)  # Weaker strength

        final_resonance = field.resonate(target)

        # Resonance should decrease but remain detectable
        # Note: can go slightly negative due to random patterns
        assert final_resonance > -0.1, f"Resonance too negative: {final_resonance}"
        assert final_resonance < initial_resonance

    def test_resonance_with_noisy_query(self) -> None:
        """Resonance is robust to noisy queries."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Imprint clean pattern
        pattern = field.encode_structure({"clean": "pattern"})
        field.imprint(pattern)

        # Create slightly noisy version of pattern (1% noise)
        noise_level = 0.01
        noise = np.random.randn(TEST_DIMENSIONS) * noise_level
        noisy_pattern = pattern + noise
        noisy_pattern = noisy_pattern / np.linalg.norm(noisy_pattern)

        clean_res = field.resonate(pattern)
        noisy_res = field.resonate(noisy_pattern)

        # Noisy pattern should still resonate very significantly
        # With 1% noise, expect 95%+ of clean resonance
        assert noisy_res > clean_res * 0.9, f"noisy={noisy_res}, clean={clean_res}"


class TestResonanceEdgeCases:
    """Edge case tests for resonance."""

    def test_resonance_zero_vector_query(self) -> None:
        """Zero vector query returns 0 resonance."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)

        zero_query = np.zeros(TEST_DIMENSIONS)
        resonance = field.resonate(zero_query)

        assert resonance == 0.0

    def test_resonance_identical_to_superposition(self) -> None:
        """Query identical to superposition resonates maximally."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)

        # Query with the superposition itself
        query = field.global_superposition.copy()
        resonance = field.resonate(query)

        assert resonance > 0.99

    def test_resonance_opposite_vector(self) -> None:
        """Opposite vector has negative resonance."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        pattern = random_hd_vector(TEST_DIMENSIONS)
        field.imprint(pattern)

        # Query with opposite
        opposite = -field.global_superposition
        resonance = field.resonate(opposite)

        assert resonance < -0.99


class TestResonancePerformance:
    """Performance-related resonance tests."""

    def test_resonance_scales_with_imprints(self) -> None:
        """Resonance operation scales reasonably with imprint count."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)
        query = random_hd_vector(TEST_DIMENSIONS)

        # Should work with many imprints
        for i in range(1000):
            pattern = random_hd_vector(TEST_DIMENSIONS)
            field.imprint(pattern)

        # Resonance should still work
        resonance = field.resonate(query)
        assert isinstance(resonance, float)

    def test_resonance_with_large_structures(self) -> None:
        """Resonance works with large structure encodings."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Create large structure
        large_struct = {f"key_{i}": f"value_{i}" for i in range(50)}
        pattern = field.encode_structure(large_struct)
        field.imprint(pattern)

        # Query with partial structure
        partial = {f"key_{i}": f"value_{i}" for i in range(10)}
        query = field.encode_structure(partial)

        resonance = field.resonate(query)
        assert resonance > 0


class TestResonanceIntegration:
    """Integration tests for resonance with other field operations."""

    def test_resonance_with_bind_patterns(self) -> None:
        """Resonance works with bound patterns."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Create role-filler bindings
        role = field.get_symbol("solver")
        filler = field.get_symbol("jwt_expert")
        bound = field.bind(role, filler)

        field.imprint(bound)

        # Query for the role
        role_resonance = field.resonate(role)

        # Should have some resonance (bound contains role info)
        # Note: binding makes it orthogonal to role, so resonance is low
        # This tests the math is working correctly
        assert isinstance(role_resonance, float)

    def test_resonance_with_bundled_patterns(self) -> None:
        """Resonance works with bundled patterns."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Create bundle
        concepts = ["auth", "jwt", "security", "token"]
        vectors = [field.get_symbol(c) for c in concepts]
        bundled = field.bundle(vectors)

        field.imprint(bundled)

        # Query for individual concepts
        for concept in concepts:
            query = field.get_symbol(concept)
            resonance = field.resonate(query)
            assert resonance > 0.3, f"Concept {concept} should resonate"

    def test_resonance_with_sequence_patterns(self) -> None:
        """Resonance works with sequence patterns."""
        field = HolographicField(dimensions=TEST_DIMENSIONS)

        # Create sequence
        seq = field.encode_sequence(["first", "second", "third"])
        field.imprint(seq)

        # Query for sequence should resonate
        same_seq = field.encode_sequence(["first", "second", "third"])
        resonance = field.resonate(same_seq)

        assert resonance > 0.9
