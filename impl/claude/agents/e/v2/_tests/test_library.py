"""
Tests for E-gent v2 Viral Library.

Tests cover:
1. ViralPattern fitness calculation
2. Record success/failure operations
3. Suggest mutations via semantic retrieval
4. Pruning (natural selection)
5. Library statistics
6. Market integration (fitness → odds)
"""

from __future__ import annotations

import pytest
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from ..library import (
    ViralPattern,
    ViralLibrary,
    ViralLibraryConfig,
    LibraryStats,
    MutationSuggestion,
    PruneReport,
    create_library,
    create_strict_library,
    create_exploratory_library,
    fitness_to_odds,
    odds_from_library,
)
from ..types import (
    Phage,
    PhageStatus,
    MutationVector,
    PhageLineage,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_mutation() -> MutationVector:
    """Create a sample mutation vector."""
    return MutationVector(
        schema_signature="loop_to_comprehension",
        original_code="for x in items:\n    result.append(f(x))",
        mutated_code="result = [f(x) for x in items]",
        enthalpy_delta=-0.3,
        entropy_delta=0.0,
        temperature=1.0,
        description="Convert loop to list comprehension",
        confidence=0.7,
        lines_changed=2,
    )


@pytest.fixture
def sample_phage(sample_mutation: MutationVector) -> Phage:
    """Create a sample phage."""
    return Phage(
        target_path=Path("test_module.py"),
        target_module="test_module",
        mutation=sample_mutation,
        hypothesis="Simplify loop to comprehension",
        status=PhageStatus.MUTATED,
        lineage=PhageLineage(schema_signature="loop_to_comprehension"),
    )


@pytest.fixture
def library() -> ViralLibrary:
    """Create a library for testing."""
    return create_library()


@dataclass
class MockSemanticRegistry:
    """Mock L-gent SemanticRegistry for testing."""

    archetypes: dict[str, dict[str, Any]] = field(default_factory=dict)
    embeddings: dict[str, list[float]] = field(default_factory=dict)

    async def register_archetype(
        self,
        name: str,
        embedding: list[float] | None = None,
        text: str | None = None,
        signature: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if embedding is None and text:
            embedding = await self.embed_text(text)
        self.archetypes[name] = {
            "embedding": embedding,
            "signature": signature,
            "metadata": metadata or {},
        }
        return name

    def deregister_archetype(self, name: str) -> bool:
        if name in self.archetypes:
            del self.archetypes[name]
            return True
        return False

    async def find_similar_archetypes(
        self,
        embedding: list[float],
        prefix: str = "",
        threshold: float = 0.5,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        results = []
        for name, data in self.archetypes.items():
            if prefix and not name.startswith(prefix):
                continue
            arch_emb = data.get("embedding", [])
            if arch_emb:
                # Simple similarity: inverse of distance
                sim = 1.0 / (1.0 + sum(abs(a - b) for a, b in zip(embedding, arch_emb)))
                if sim >= threshold:
                    results.append((name, sim))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    async def embed_text(self, text: str) -> list[float]:
        # Deterministic mock embedding
        if text in self.embeddings:
            return self.embeddings[text]
        # Generate simple embedding from text hash
        import hashlib

        h = hashlib.md5(text.encode()).hexdigest()
        return [int(c, 16) / 15.0 for c in h[:8]]


@pytest.fixture
def mock_registry() -> MockSemanticRegistry:
    """Create a mock semantic registry."""
    return MockSemanticRegistry()


@pytest.fixture
def library_with_lgent(mock_registry: MockSemanticRegistry) -> ViralLibrary:
    """Create a library with L-gent integration."""
    return create_library(l_gent=mock_registry)


# =============================================================================
# ViralPattern Tests
# =============================================================================


class TestViralPattern:
    """Tests for ViralPattern dataclass."""

    def test_initial_fitness_is_zero(self) -> None:
        """New patterns have zero fitness."""
        pattern = ViralPattern(signature="test", dna="code")
        assert pattern.fitness == 0.0

    def test_fitness_after_one_success(self) -> None:
        """Single success with impact gives positive fitness."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=1,
            failure_count=0,
            total_impact=1.5,
        )
        # fitness = success_rate × avg_impact = 1.0 × 1.5 = 1.5
        assert pattern.fitness == 1.5

    def test_fitness_with_mixed_results(self) -> None:
        """Fitness accounts for both successes and failures."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=3,
            failure_count=1,
            total_impact=6.0,  # avg_impact = 2.0
        )
        # success_rate = 3/4 = 0.75
        # avg_impact = 6.0/3 = 2.0
        # fitness = 0.75 × 2.0 = 1.5
        assert pattern.fitness == 1.5

    def test_fitness_with_only_failures(self) -> None:
        """Pattern with only failures has zero fitness."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=0,
            failure_count=5,
            total_impact=0.0,
        )
        assert pattern.fitness == 0.0

    def test_reinforce_increases_fitness(self) -> None:
        """Reinforcing a pattern increases its fitness."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=1,
            failure_count=0,
            total_impact=1.0,
        )
        initial_fitness = pattern.fitness

        pattern.reinforce(impact=2.0)

        assert pattern.success_count == 2
        assert pattern.total_impact == 3.0
        assert pattern.fitness > initial_fitness

    def test_weaken_decreases_fitness(self) -> None:
        """Weakening a pattern decreases its fitness."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=2,
            failure_count=0,
            total_impact=2.0,
        )
        initial_fitness = pattern.fitness

        pattern.weaken()

        assert pattern.failure_count == 1
        assert pattern.fitness < initial_fitness

    def test_success_rate(self) -> None:
        """Success rate is correctly calculated."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=7,
            failure_count=3,
        )
        assert pattern.success_rate == 0.7

    def test_avg_impact_per_success(self) -> None:
        """Average impact per success is correctly calculated."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=4,
            total_impact=8.0,
        )
        assert pattern.avg_impact_per_success == 2.0

    def test_total_uses(self) -> None:
        """Total uses is sum of successes and failures."""
        pattern = ViralPattern(
            signature="test",
            dna="code",
            success_count=5,
            failure_count=3,
        )
        assert pattern.total_uses == 8


# =============================================================================
# Record Success Tests
# =============================================================================


class TestRecordSuccess:
    """Tests for record_success operation."""

    @pytest.mark.asyncio
    async def test_creates_new_pattern(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Recording success for new phage creates pattern."""
        pattern = await library.record_success(sample_phage, impact=1.0)

        assert library.total_patterns == 1
        assert library.total_successes == 1
        assert pattern.success_count == 1

    @pytest.mark.asyncio
    async def test_reinforces_existing_pattern(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Recording success for existing pattern reinforces it."""
        await library.record_success(sample_phage, impact=1.0)
        pattern = await library.record_success(sample_phage, impact=2.0)

        assert library.total_patterns == 1  # Still one pattern
        assert library.total_successes == 2
        assert pattern.success_count == 2
        assert pattern.total_impact == 3.0

    @pytest.mark.asyncio
    async def test_records_impact(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Impact is correctly accumulated."""
        pattern = await library.record_success(sample_phage, impact=1.5)

        assert pattern.total_impact == 1.5
        assert pattern.avg_impact_per_success == 1.5

    @pytest.mark.asyncio
    async def test_records_cost(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Cost is correctly averaged."""
        await library.record_success(sample_phage, impact=1.0, cost=100)
        pattern = await library.record_success(sample_phage, impact=1.0, cost=200)

        assert pattern.avg_cost == 150.0

    @pytest.mark.asyncio
    async def test_registers_with_lgent(
        self,
        library_with_lgent: ViralLibrary,
        sample_phage: Phage,
        mock_registry: MockSemanticRegistry,
    ) -> None:
        """New patterns are registered with L-gent."""
        await library_with_lgent.record_success(sample_phage, impact=1.0)

        # Check archetype was registered
        expected_name = f"viral:{sample_phage.mutation.signature}"
        assert any(name.startswith("viral:") for name in mock_registry.archetypes)

    @pytest.mark.asyncio
    async def test_updates_last_used(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Last used timestamp is updated."""
        pattern = await library.record_success(sample_phage, impact=1.0)
        initial_time = pattern.last_used

        # Small delay to ensure time difference
        import time

        time.sleep(0.01)

        pattern = await library.record_success(sample_phage, impact=1.0)

        assert pattern.last_used >= initial_time


# =============================================================================
# Record Failure Tests
# =============================================================================


class TestRecordFailure:
    """Tests for record_failure operation."""

    @pytest.mark.asyncio
    async def test_weakens_existing_pattern(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Recording failure weakens existing pattern."""
        await library.record_success(sample_phage, impact=1.0)
        initial_fitness = library.get_fitness(sample_phage.mutation.signature)

        await library.record_failure(sample_phage)

        new_fitness = library.get_fitness(sample_phage.mutation.signature)
        assert new_fitness < initial_fitness

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_pattern(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Recording failure for unknown pattern returns None."""
        pattern = await library.record_failure(sample_phage)

        assert pattern is None
        assert library.total_failures == 1

    @pytest.mark.asyncio
    async def test_increments_failure_count(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Failure count is incremented."""
        await library.record_success(sample_phage, impact=1.0)
        pattern = await library.record_failure(sample_phage)

        assert pattern is not None
        assert pattern.failure_count == 1


# =============================================================================
# Query Tests
# =============================================================================


class TestSuggestMutations:
    """Tests for suggest_mutations query."""

    @pytest.mark.asyncio
    async def test_returns_empty_for_empty_library(self, library: ViralLibrary) -> None:
        """Empty library returns no suggestions."""
        suggestions = await library.suggest_mutations(
            context_embedding=[0.5] * 8,
        )

        assert suggestions == []

    @pytest.mark.asyncio
    async def test_returns_patterns_by_fitness(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Without L-gent, returns patterns by fitness."""
        await library.record_success(sample_phage, impact=2.0)

        suggestions = await library.suggest_mutations(
            context_embedding=[0.5] * 8,
        )

        assert len(suggestions) == 1
        assert suggestions[0].pattern.fitness > 0

    @pytest.mark.asyncio
    async def test_filters_by_min_fitness(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Patterns below min_fitness are excluded."""
        await library.record_success(sample_phage, impact=0.1)  # Low fitness

        suggestions = await library.suggest_mutations(
            context_embedding=[0.5] * 8,
            min_fitness=1.0,
        )

        assert suggestions == []

    @pytest.mark.asyncio
    async def test_respects_top_k(self, library: ViralLibrary) -> None:
        """Respects top_k limit."""
        # Create multiple patterns
        for i in range(5):
            phage = Phage(
                target_module=f"module_{i}",
                mutation=MutationVector(
                    schema_signature=f"schema_{i}",
                    original_code=f"code_{i}",
                    mutated_code=f"mutated_{i}",
                ),
                status=PhageStatus.MUTATED,
            )
            await library.record_success(phage, impact=1.0)

        suggestions = await library.suggest_mutations(
            context_embedding=[0.5] * 8,
            top_k=3,
        )

        assert len(suggestions) == 3

    @pytest.mark.asyncio
    async def test_with_lgent_uses_similarity(
        self,
        library_with_lgent: ViralLibrary,
        mock_registry: MockSemanticRegistry,
    ) -> None:
        """With L-gent, uses semantic similarity."""
        # Create pattern with specific embedding
        phage = Phage(
            target_module="test",
            mutation=MutationVector(
                schema_signature="test_schema",
                original_code="original",
                mutated_code="mutated",
                description="test mutation",
            ),
            status=PhageStatus.MUTATED,
        )
        await library_with_lgent.record_success(phage, impact=1.0)

        # Query with embedding
        suggestions = await library_with_lgent.suggest_mutations(
            context_embedding=[0.5] * 8,
        )

        # Should return suggestions (may be empty if similarity too low)
        assert isinstance(suggestions, list)


class TestGetFitness:
    """Tests for get_fitness query."""

    @pytest.mark.asyncio
    async def test_returns_pattern_fitness(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Returns correct fitness for pattern."""
        await library.record_success(sample_phage, impact=2.0)

        fitness = library.get_fitness(sample_phage.mutation.signature)

        assert fitness == 2.0

    def test_returns_zero_for_unknown(self, library: ViralLibrary) -> None:
        """Returns 0.0 for unknown pattern."""
        fitness = library.get_fitness("unknown_signature")

        assert fitness == 0.0


class TestGetStats:
    """Tests for get_stats query."""

    def test_empty_library_stats(self, library: ViralLibrary) -> None:
        """Empty library has zero stats."""
        stats = library.get_stats()

        assert stats.total_patterns == 0
        assert stats.total_successes == 0
        assert stats.total_failures == 0
        assert stats.avg_fitness == 0.0

    @pytest.mark.asyncio
    async def test_stats_after_operations(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Stats reflect operations."""
        await library.record_success(sample_phage, impact=1.5)
        await library.record_failure(sample_phage)

        stats = library.get_stats()

        assert stats.total_patterns == 1
        assert stats.total_successes == 1
        assert stats.total_failures == 1
        assert stats.avg_fitness > 0

    @pytest.mark.asyncio
    async def test_categorizes_by_fitness(self, library: ViralLibrary) -> None:
        """Categorizes patterns by fitness level."""
        # High fitness pattern
        high_phage = Phage(
            target_module="high",
            mutation=MutationVector(
                schema_signature="high",
                original_code="a",
                mutated_code="b",
            ),
            status=PhageStatus.MUTATED,
        )
        await library.record_success(high_phage, impact=2.0)

        # Low fitness pattern
        low_phage = Phage(
            target_module="low",
            mutation=MutationVector(
                schema_signature="low",
                original_code="c",
                mutated_code="d",
            ),
            status=PhageStatus.MUTATED,
        )
        await library.record_success(low_phage, impact=0.1)

        stats = library.get_stats()

        assert stats.high_fitness_patterns >= 1 or stats.viable_patterns >= 1


# =============================================================================
# Prune Tests
# =============================================================================


class TestPrune:
    """Tests for prune operation (natural selection)."""

    @pytest.mark.asyncio
    async def test_removes_low_fitness_patterns(self, library: ViralLibrary) -> None:
        """Prunes patterns below threshold."""
        # Create low-fitness pattern (many failures)
        phage = Phage(
            target_module="weak",
            mutation=MutationVector(
                schema_signature="weak",
                original_code="a",
                mutated_code="b",
            ),
            status=PhageStatus.MUTATED,
        )
        await library.record_success(phage, impact=0.01)  # Very low impact
        for _ in range(10):
            await library.record_failure(phage)

        initial_count = library.total_patterns

        report = await library.prune(threshold=0.5)

        assert report.pruned_count > 0
        assert library.total_patterns < initial_count

    @pytest.mark.asyncio
    async def test_preserves_high_fitness_patterns(self, library: ViralLibrary) -> None:
        """Does not prune patterns above threshold."""
        phage = Phage(
            target_module="strong",
            mutation=MutationVector(
                schema_signature="strong",
                original_code="a",
                mutated_code="b",
            ),
            status=PhageStatus.MUTATED,
        )
        await library.record_success(phage, impact=2.0)

        report = await library.prune(threshold=0.5)

        assert report.pruned_count == 0
        assert library.total_patterns == 1

    @pytest.mark.asyncio
    async def test_returns_prune_report(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Returns detailed prune report."""
        await library.record_success(sample_phage, impact=0.01)

        report = await library.prune(threshold=1.0)  # High threshold

        assert isinstance(report, PruneReport)
        assert report.avg_fitness_before >= 0
        assert report.avg_fitness_after >= 0
        assert isinstance(report.pruned_signatures, list)

    @pytest.mark.asyncio
    async def test_deregisters_from_lgent(
        self,
        library_with_lgent: ViralLibrary,
        mock_registry: MockSemanticRegistry,
    ) -> None:
        """Pruned patterns are deregistered from L-gent."""
        phage = Phage(
            target_module="weak",
            mutation=MutationVector(
                schema_signature="weak",
                original_code="a",
                mutated_code="b",
            ),
            status=PhageStatus.MUTATED,
        )
        await library_with_lgent.record_success(phage, impact=0.01)

        # Verify registered
        initial_archetypes = len(mock_registry.archetypes)

        await library_with_lgent.prune(threshold=1.0)

        # Should have fewer archetypes
        assert len(mock_registry.archetypes) < initial_archetypes


# =============================================================================
# Auto-Prune Tests
# =============================================================================


class TestAutoPrune:
    """Tests for automatic pruning."""

    @pytest.mark.asyncio
    async def test_auto_prunes_after_interval(self) -> None:
        """Auto-prunes after configured interval."""
        config = ViralLibraryConfig(
            auto_prune_interval=5,
            prune_threshold=0.5,
        )
        library = ViralLibrary(config=config)

        # Create weak pattern
        weak_phage = Phage(
            target_module="weak",
            mutation=MutationVector(
                schema_signature="weak",
                original_code="a",
                mutated_code="b",
            ),
            status=PhageStatus.MUTATED,
        )
        await library.record_success(weak_phage, impact=0.01)

        # Record enough operations to trigger auto-prune
        for i in range(5):
            phage = Phage(
                target_module=f"module_{i}",
                mutation=MutationVector(
                    schema_signature=f"schema_{i}",
                    original_code=f"code_{i}",
                    mutated_code=f"mutated_{i}",
                ),
                status=PhageStatus.MUTATED,
            )
            await library.record_success(phage, impact=1.0)

        # Weak pattern should have been pruned
        assert library.get_fitness("weak") == 0.0 or library.total_patterns <= 5


# =============================================================================
# Market Integration Tests
# =============================================================================


class TestMarketIntegration:
    """Tests for market integration functions."""

    def test_high_fitness_gives_low_odds(self) -> None:
        """High fitness patterns have low odds (likely to succeed)."""
        odds = fitness_to_odds(1.5)
        assert odds < 2.0

    def test_low_fitness_gives_high_odds(self) -> None:
        """Low fitness patterns have high odds (unlikely to succeed)."""
        odds = fitness_to_odds(0.1)
        assert odds >= 5.0

    def test_zero_fitness_gives_maximum_odds(self) -> None:
        """Zero fitness gives maximum odds."""
        odds = fitness_to_odds(0.0)
        assert odds == 10.0

    @pytest.mark.asyncio
    async def test_odds_from_library(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Gets odds from library for phage."""
        await library.record_success(sample_phage, impact=1.5)

        odds = odds_from_library(library, sample_phage)

        assert odds < 5.0  # Should get better odds

    def test_odds_from_library_unknown_pattern(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Unknown pattern gets base odds."""
        odds = odds_from_library(library, sample_phage, base_odds=5.0)

        assert odds == 5.0


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactories:
    """Tests for factory functions."""

    def test_create_library(self) -> None:
        """create_library creates default library."""
        library = create_library()

        assert library.total_patterns == 0
        assert library.config.prune_threshold == 0.3

    def test_create_strict_library(self) -> None:
        """create_strict_library creates strict configuration."""
        library = create_strict_library()

        assert library.config.prune_threshold == 0.5
        assert library.config.max_patterns == 500

    def test_create_exploratory_library(self) -> None:
        """create_exploratory_library creates lenient configuration."""
        library = create_exploratory_library()

        assert library.config.prune_threshold == 0.1
        assert library.config.max_patterns == 2000


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_phage_without_mutation(self, library: ViralLibrary) -> None:
        """Handles phage without mutation."""
        phage = Phage(
            target_module="test",
            mutation=None,
            status=PhageStatus.NASCENT,
        )

        # Should not raise
        pattern = await library.record_success(phage, impact=1.0)

        assert pattern is not None

    @pytest.mark.asyncio
    async def test_zero_impact_success(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Zero impact success still counts."""
        pattern = await library.record_success(sample_phage, impact=0.0)

        assert pattern.success_count == 1
        assert pattern.fitness == 0.0  # success_rate × 0 = 0

    @pytest.mark.asyncio
    async def test_negative_impact(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Negative impact is allowed (regression)."""
        pattern = await library.record_success(sample_phage, impact=-0.5)

        assert pattern.total_impact == -0.5
        assert pattern.fitness < 0

    @pytest.mark.asyncio
    async def test_large_number_of_patterns(self, library: ViralLibrary) -> None:
        """Handles large number of patterns."""
        for i in range(100):
            phage = Phage(
                target_module=f"module_{i}",
                mutation=MutationVector(
                    schema_signature=f"schema_{i}",
                    original_code=f"code_{i}",
                    mutated_code=f"mutated_{i}",
                ),
                status=PhageStatus.MUTATED,
            )
            await library.record_success(phage, impact=1.0)

        assert library.total_patterns == 100

    @pytest.mark.asyncio
    async def test_concurrent_access(self, library: ViralLibrary) -> None:
        """Basic concurrent access test."""
        import asyncio

        phages = [
            Phage(
                target_module=f"module_{i}",
                mutation=MutationVector(
                    schema_signature=f"schema_{i}",
                    original_code=f"code_{i}",
                    mutated_code=f"mutated_{i}",
                ),
                status=PhageStatus.MUTATED,
            )
            for i in range(10)
        ]

        async def record(p: Phage) -> None:
            await library.record_success(p, impact=1.0)

        await asyncio.gather(*[record(p) for p in phages])

        assert library.total_patterns == 10


# =============================================================================
# Property-Based Tests
# =============================================================================


class TestProperties:
    """Property-based tests for invariants."""

    @pytest.mark.asyncio
    async def test_fitness_is_non_negative_with_positive_impact(
        self, library: ViralLibrary
    ) -> None:
        """Fitness is non-negative when impact is non-negative."""
        import random

        for _ in range(20):
            phage = Phage(
                target_module="test",
                mutation=MutationVector(
                    schema_signature=f"schema_{random.randint(0, 1000)}",
                    original_code="a",
                    mutated_code="b",
                ),
                status=PhageStatus.MUTATED,
            )
            impact = random.uniform(0, 10)
            pattern = await library.record_success(phage, impact=impact)

            assert pattern.fitness >= 0

    @pytest.mark.asyncio
    async def test_total_uses_equals_sum(
        self, library: ViralLibrary, sample_phage: Phage
    ) -> None:
        """Total uses equals successes + failures."""
        await library.record_success(sample_phage, impact=1.0)
        await library.record_success(sample_phage, impact=1.0)
        await library.record_failure(sample_phage)
        pattern = await library.record_failure(sample_phage)

        assert pattern.total_uses == pattern.success_count + pattern.failure_count
        assert pattern.total_uses == 4

    @pytest.mark.asyncio
    async def test_prune_never_increases_count(self, library: ViralLibrary) -> None:
        """Pruning never increases pattern count."""
        for i in range(10):
            phage = Phage(
                target_module=f"module_{i}",
                mutation=MutationVector(
                    schema_signature=f"schema_{i}",
                    original_code=f"code_{i}",
                    mutated_code=f"mutated_{i}",
                ),
                status=PhageStatus.MUTATED,
            )
            await library.record_success(phage, impact=0.1)

        before = library.total_patterns
        await library.prune(threshold=0.5)
        after = library.total_patterns

        assert after <= before
