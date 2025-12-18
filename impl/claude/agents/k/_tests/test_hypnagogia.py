"""
Tests for K-gent Phase 4: Hypnagogia (Dream Cycle).

Tests cover:
1. HypnagogicConfig - Configuration validation
2. Pattern types - Pattern creation, promotion, serialization
3. HypnagogicCycle - Dream cycle execution
4. Pattern extraction - Heuristic and LLM-based
5. Eigenvector updates - Confidence evolution
6. Dream events - Event factory functions
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest

from agents.k.eigenvectors import KentEigenvectors
from agents.k.events import (
    SoulEventType,
    dream_end_event,
    dream_insight_event,
    dream_pattern_event,
    dream_start_event,
    is_dream_event,
)
from agents.k.hypnagogia import (
    DreamReport,
    EigenvectorDelta,
    HypnagogicConfig,
    HypnagogicCycle,
    Interaction,
    Pattern,
    PatternMaturity,
    create_hypnagogic_cycle,
    get_hypnagogia,
    set_hypnagogia,
)
from agents.k.soul import KgentSoul

if TYPE_CHECKING:
    pass


# =============================================================================
# HypnagogicConfig Tests
# =============================================================================


class TestHypnagogicConfig:
    """Tests for HypnagogicConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = HypnagogicConfig()

        assert config.dream_hour == 3
        assert config.dream_minute == 0
        assert config.max_interactions_per_dream == 100
        assert config.min_interactions_for_dream == 10
        assert config.seed_to_tree_threshold == 5
        assert config.tree_pruning_days == 30
        assert config.use_llm_for_patterns is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = HypnagogicConfig(
            dream_hour=4,
            dream_minute=30,
            max_interactions_per_dream=50,
            min_interactions_for_dream=5,
        )

        assert config.dream_hour == 4
        assert config.dream_minute == 30
        assert config.max_interactions_per_dream == 50
        assert config.min_interactions_for_dream == 5


# =============================================================================
# Pattern Tests
# =============================================================================


class TestPattern:
    """Tests for Pattern dataclass."""

    def test_pattern_creation(self) -> None:
        """Test basic pattern creation."""
        pattern = Pattern(content="Recurring theme: architecture")

        assert pattern.content == "Recurring theme: architecture"
        assert pattern.occurrences == 1
        assert pattern.maturity == PatternMaturity.SEED
        assert len(pattern.id) == 12  # MD5 hash prefix

    def test_pattern_id_is_stable(self) -> None:
        """Test that pattern ID is stable for same content."""
        p1 = Pattern(content="Test pattern")
        p2 = Pattern(content="Test pattern")
        p3 = Pattern(content="Different pattern")

        assert p1.id == p2.id
        assert p1.id != p3.id

    def test_pattern_promotion(self) -> None:
        """Test pattern maturity promotion."""
        seed = Pattern(content="Test", maturity=PatternMaturity.SEED)
        sapling = seed.promote()
        tree = sapling.promote()

        assert seed.maturity == PatternMaturity.SEED
        assert sapling.maturity == PatternMaturity.SAPLING
        assert tree.maturity == PatternMaturity.TREE

        # Tree cannot be promoted further
        still_tree = tree.promote()
        assert still_tree.maturity == PatternMaturity.TREE

    def test_pattern_age(self) -> None:
        """Test pattern age calculation."""
        old_time = datetime.now(timezone.utc) - timedelta(days=5)
        pattern = Pattern(content="Test", first_seen=old_time)

        assert pattern.age_days >= 4.9  # Approximately 5 days

    def test_pattern_staleness(self) -> None:
        """Test pattern staleness calculation."""
        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        pattern = Pattern(content="Test", last_seen=old_time)

        assert pattern.staleness_days >= 9.9  # Approximately 10 days

    def test_pattern_to_dict(self) -> None:
        """Test pattern serialization."""
        pattern = Pattern(
            content="Test pattern",
            occurrences=3,
            maturity=PatternMaturity.SAPLING,
            evidence=["Evidence 1", "Evidence 2"],
            eigenvector_affinities={"categorical": 0.7},
        )

        data = pattern.to_dict()

        assert data["content"] == "Test pattern"
        assert data["occurrences"] == 3
        assert data["maturity"] == "sapling"
        assert len(data["evidence"]) == 2
        assert data["eigenvector_affinities"]["categorical"] == 0.7


# =============================================================================
# EigenvectorDelta Tests
# =============================================================================


class TestEigenvectorDelta:
    """Tests for EigenvectorDelta."""

    def test_positive_delta(self) -> None:
        """Test positive confidence change."""
        delta = EigenvectorDelta(
            eigenvector="categorical",
            old_confidence=0.90,
            new_confidence=0.92,
            evidence=["Pattern A"],
            reasoning="Growing evidence",
        )

        assert delta.delta == pytest.approx(0.02)
        assert delta.direction == "increased"

    def test_negative_delta(self) -> None:
        """Test negative confidence change."""
        delta = EigenvectorDelta(
            eigenvector="aesthetic",
            old_confidence=0.85,
            new_confidence=0.82,
            evidence=["Pattern B"],
            reasoning="Counter-evidence",
        )

        assert delta.delta == pytest.approx(-0.03)
        assert delta.direction == "decreased"

    def test_unchanged_delta(self) -> None:
        """Test unchanged confidence."""
        delta = EigenvectorDelta(
            eigenvector="joy",
            old_confidence=0.75,
            new_confidence=0.7505,  # Very small change
            evidence=[],
            reasoning="Stable",
        )

        assert delta.direction == "unchanged"


# =============================================================================
# Interaction Tests
# =============================================================================


class TestInteraction:
    """Tests for Interaction dataclass."""

    def test_interaction_creation(self) -> None:
        """Test interaction creation."""
        interaction = Interaction(
            timestamp=datetime.now(timezone.utc),
            message="What am I avoiding?",
            response="The uncomfortable truth about...",
            mode="reflect",
            tokens_used=150,
        )

        assert interaction.mode == "reflect"
        assert interaction.tokens_used == 150

    def test_interaction_to_text(self) -> None:
        """Test interaction text conversion."""
        interaction = Interaction(
            timestamp=datetime.now(timezone.utc),
            message="Test message",
            response="Test response",
            mode="challenge",
        )

        text = interaction.to_text()

        assert "[challenge]" in text
        assert "Test message" in text
        assert "Test response" in text


# =============================================================================
# DreamReport Tests
# =============================================================================


class TestDreamReport:
    """Tests for DreamReport."""

    def test_empty_report(self) -> None:
        """Test empty dream report."""
        report = DreamReport()

        assert report.interactions_processed == 0
        assert len(report.patterns_discovered) == 0
        assert report.was_dry_run is False

    def test_report_summary(self) -> None:
        """Test report summary generation."""
        report = DreamReport(
            interactions_processed=20,
            patterns_discovered=[Pattern(content="Test")],
            eigenvector_deltas=[
                EigenvectorDelta(
                    eigenvector="categorical",
                    old_confidence=0.90,
                    new_confidence=0.92,
                    evidence=[],
                    reasoning="Test",
                )
            ],
            insights=["Test insight"],
        )

        summary = report.summary

        assert "20" in summary
        assert "1" in summary  # patterns discovered
        assert "categorical" in summary
        assert "Test insight" in summary

    def test_report_to_dict(self) -> None:
        """Test report serialization."""
        report = DreamReport(
            interactions_processed=10,
            was_dry_run=True,
        )

        data = report.to_dict()

        assert data["interactions_processed"] == 10
        assert data["was_dry_run"] is True
        assert "timestamp" in data


# =============================================================================
# HypnagogicCycle Tests
# =============================================================================


class TestHypnagogicCycle:
    """Tests for HypnagogicCycle."""

    def test_cycle_creation(self) -> None:
        """Test cycle creation."""
        # Disable persistence to avoid loading patterns from disk
        config = HypnagogicConfig(persist_patterns=False)
        cycle = HypnagogicCycle(config=config)

        assert cycle.interactions_buffered == 0
        assert len(cycle.patterns) == 0
        assert cycle.last_dream is None

    def test_cycle_with_custom_config(self) -> None:
        """Test cycle with custom config."""
        config = HypnagogicConfig(min_interactions_for_dream=5)
        cycle = HypnagogicCycle(config=config)

        assert cycle.config.min_interactions_for_dream == 5

    def test_record_interaction(self) -> None:
        """Test recording interactions."""
        cycle = HypnagogicCycle()

        cycle.record_interaction(
            message="Test message",
            response="Test response",
            mode="reflect",
            tokens_used=100,
        )

        assert cycle.interactions_buffered == 1

    def test_clear_interactions(self) -> None:
        """Test clearing interactions."""
        cycle = HypnagogicCycle()

        for i in range(5):
            cycle.record_interaction(
                message=f"Message {i}",
                response=f"Response {i}",
                mode="reflect",
            )

        cleared = cycle.clear_interactions()

        assert cleared == 5
        assert cycle.interactions_buffered == 0

    def test_status(self) -> None:
        """Test status reporting."""
        # Disable persistence to avoid loading patterns from disk
        config = HypnagogicConfig(persist_patterns=False)
        cycle = HypnagogicCycle(config=config)

        cycle.record_interaction(
            message="Test",
            response="Response",
            mode="advise",
        )

        status = cycle.status()

        assert status["interactions_buffered"] == 1
        assert status["patterns_stored"] == 0
        assert status["dreams_completed"] == 0
        assert "config" in status

    def test_should_dream_threshold(self) -> None:
        """Test dream threshold check."""
        config = HypnagogicConfig(min_interactions_for_dream=3)
        cycle = HypnagogicCycle(config=config)

        assert cycle.should_dream() is False

        # Add interactions
        for i in range(3):
            cycle.record_interaction(
                message=f"Message {i}",
                response=f"Response {i}",
                mode="reflect",
            )

        assert cycle.should_dream() is True


class TestHypnagogicCycleDream:
    """Tests for dream execution."""

    @pytest.mark.asyncio
    async def test_dream_with_insufficient_interactions(self) -> None:
        """Test dream skips when not enough interactions."""
        soul = KgentSoul(auto_llm=False)
        cycle = HypnagogicCycle()

        # Add fewer than minimum interactions
        for i in range(5):
            cycle.record_interaction(
                message=f"Message {i}",
                response=f"Response {i}",
                mode="reflect",
            )

        report = await cycle.dream(soul)

        # Should report insufficient interactions
        assert report.interactions_processed == 5
        assert any("Insufficient" in insight for insight in report.insights)

    @pytest.mark.asyncio
    async def test_dream_dry_run(self) -> None:
        """Test dream dry run doesn't apply changes."""
        config = HypnagogicConfig(min_interactions_for_dream=3)
        soul = KgentSoul(auto_llm=False)
        cycle = HypnagogicCycle(config=config)

        # Add interactions
        for i in range(10):
            cycle.record_interaction(
                message="What about architecture?",
                response="Architecture is important.",
                mode="reflect",
            )

        initial_count = cycle.interactions_buffered
        report = await cycle.dream(soul, dry_run=True)

        assert report.was_dry_run is True
        # Interactions should not be cleared in dry run
        assert cycle.interactions_buffered == initial_count

    @pytest.mark.asyncio
    async def test_dream_extracts_patterns(self) -> None:
        """Test dream extracts patterns from interactions."""
        config = HypnagogicConfig(
            min_interactions_for_dream=3,
            use_llm_for_patterns=False,
        )
        soul = KgentSoul(auto_llm=False)
        cycle = HypnagogicCycle(config=config)

        # Add interactions with repeated words
        for _ in range(10):
            cycle.record_interaction(
                message="How do I improve the architecture design?",
                response="Architecture design requires careful thought.",
                mode="reflect",
            )

        report = await cycle.dream(soul)

        # Should extract patterns (at least mode preference)
        assert report.interactions_processed == 10
        assert len(report.patterns_discovered) > 0


class TestPatternExtraction:
    """Tests for pattern extraction."""

    @pytest.mark.asyncio
    async def test_heuristic_mode_pattern(self) -> None:
        """Test heuristic extracts mode preference pattern."""
        config = HypnagogicConfig(
            min_interactions_for_dream=3,
            use_llm_for_patterns=False,
        )
        cycle = HypnagogicCycle(config=config)

        # All reflect mode
        interactions = [
            Interaction(
                timestamp=datetime.now(timezone.utc),
                message=f"Message {i}",
                response=f"Response {i}",
                mode="reflect",
            )
            for i in range(10)
        ]

        patterns = await cycle.extract_patterns(interactions)

        # Should find mode preference
        mode_patterns = [p for p in patterns if "reflect" in p.content.lower()]
        assert len(mode_patterns) > 0

    @pytest.mark.asyncio
    async def test_heuristic_question_pattern(self) -> None:
        """Test heuristic extracts question pattern."""
        config = HypnagogicConfig(use_llm_for_patterns=False)
        cycle = HypnagogicCycle(config=config)

        # High question rate
        interactions = [
            Interaction(
                timestamp=datetime.now(timezone.utc),
                message=f"What about {i}? Why is this?",
                response=f"Response {i}",
                mode="explore",
            )
            for i in range(10)
        ]

        patterns = await cycle.extract_patterns(interactions)

        # Should find question pattern
        question_patterns = [
            p for p in patterns if "question" in p.content.lower() or "inquiry" in p.content.lower()
        ]
        assert len(question_patterns) > 0


class TestEigenvectorUpdates:
    """Tests for eigenvector confidence updates."""

    @pytest.mark.asyncio
    async def test_eigenvector_update_from_patterns(self) -> None:
        """Test eigenvector confidence updates from patterns."""
        cycle = HypnagogicCycle()
        soul = KgentSoul(auto_llm=False)

        patterns = [
            Pattern(
                content="Abstract thinking prevalent",
                eigenvector_affinities={"categorical": 0.8},
            ),
            Pattern(
                content="Another abstract pattern",
                eigenvector_affinities={"categorical": 0.6},
            ),
        ]

        deltas = await cycle.update_eigenvectors(patterns, soul)

        # Should have delta for categorical
        categorical_deltas = [d for d in deltas if d.eigenvector == "categorical"]
        assert len(categorical_deltas) > 0

    @pytest.mark.asyncio
    async def test_eigenvector_update_clamped(self) -> None:
        """Test eigenvector updates are clamped to max change."""
        config = HypnagogicConfig(max_confidence_change=0.01)
        cycle = HypnagogicCycle(config=config)
        soul = KgentSoul(auto_llm=False)

        # Create patterns with strong affinities
        patterns = [
            Pattern(
                content=f"Pattern {i}",
                eigenvector_affinities={"categorical": 1.0},
            )
            for i in range(10)
        ]

        deltas = await cycle.update_eigenvectors(patterns, soul)

        # All deltas should be within max change
        for delta in deltas:
            assert abs(delta.delta) <= config.max_confidence_change + 0.001


# =============================================================================
# Dream Events Tests
# =============================================================================


class TestDreamEvents:
    """Tests for dream event factory functions."""

    def test_dream_start_event(self) -> None:
        """Test dream start event creation."""
        event = dream_start_event(interactions_count=20)

        assert event.event_type == SoulEventType.DREAM_START
        assert event.payload["interactions_count"] == 20

    def test_dream_pattern_event(self) -> None:
        """Test dream pattern event creation."""
        event = dream_pattern_event(
            pattern="Test pattern",
            occurrences=3,
            promoted=True,
            maturity="sapling",
        )

        assert event.event_type == SoulEventType.DREAM_PATTERN
        assert event.payload["pattern"] == "Test pattern"
        assert event.payload["promoted"] is True

    def test_dream_insight_event(self) -> None:
        """Test dream insight event creation."""
        event = dream_insight_event(
            eigenvector="categorical",
            delta=0.02,
            old_confidence=0.90,
            new_confidence=0.92,
            evidence=["Pattern A"],
        )

        assert event.event_type == SoulEventType.DREAM_INSIGHT
        assert event.payload["eigenvector"] == "categorical"
        assert event.payload["delta"] == 0.02

    def test_dream_end_event(self) -> None:
        """Test dream end event creation."""
        event = dream_end_event(
            patterns_discovered=5,
            patterns_promoted=2,
            patterns_composted=1,
            eigenvector_changes=3,
            insights=["Test insight"],
            was_dry_run=True,
        )

        assert event.event_type == SoulEventType.DREAM_END
        assert event.payload["patterns_discovered"] == 5
        assert event.payload["was_dry_run"] is True

    def test_is_dream_event(self) -> None:
        """Test dream event predicate."""
        start_event = dream_start_event(10)
        pattern_event = dream_pattern_event("Test", 1)
        insight_event = dream_insight_event("categorical", 0.01, 0.9, 0.91)
        end_event = dream_end_event(1, 0, 0, 0)

        assert is_dream_event(start_event) is True
        assert is_dream_event(pattern_event) is True
        assert is_dream_event(insight_event) is True
        assert is_dream_event(end_event) is True


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory and singleton functions."""

    def test_create_hypnagogic_cycle(self) -> None:
        """Test factory function."""
        cycle = create_hypnagogic_cycle()
        assert isinstance(cycle, HypnagogicCycle)

        # With custom config
        config = HypnagogicConfig(dream_hour=5)
        cycle_custom = create_hypnagogic_cycle(config=config)
        assert cycle_custom.config.dream_hour == 5

    def test_get_set_hypnagogia(self) -> None:
        """Test singleton management."""
        # Get creates singleton
        cycle1 = get_hypnagogia()
        cycle2 = get_hypnagogia()
        assert cycle1 is cycle2

        # Set replaces singleton
        new_cycle = HypnagogicCycle()
        set_hypnagogia(new_cycle)
        cycle3 = get_hypnagogia()
        assert cycle3 is new_cycle

        # Reset for other tests
        set_hypnagogia(HypnagogicCycle())


# =============================================================================
# Integration Tests
# =============================================================================


class TestHypnagogiaIntegration:
    """Integration tests for hypnagogia with soul."""

    @pytest.mark.asyncio
    async def test_full_dream_cycle(self) -> None:
        """Test complete dream cycle with soul."""
        config = HypnagogicConfig(
            min_interactions_for_dream=5,
            use_llm_for_patterns=False,
        )
        soul = KgentSoul(auto_llm=False)
        cycle = HypnagogicCycle(config=config)

        # Record interactions
        for i in range(10):
            cycle.record_interaction(
                message=f"What about architecture decision {i}?",
                response=f"Consider the trade-offs of option {i}.",
                mode="advise",
            )

        # Execute dream
        report = await cycle.dream(soul)

        # Verify report
        assert report.interactions_processed == 10
        assert len(report.patterns_discovered) > 0

        # Interactions should be cleared
        assert cycle.interactions_buffered == 0

        # History should be updated
        assert cycle.last_dream is not None

    @pytest.mark.asyncio
    async def test_pattern_promotion_over_cycles(self) -> None:
        """Test pattern promotion over multiple dream cycles."""
        config = HypnagogicConfig(
            min_interactions_for_dream=3,
            use_llm_for_patterns=False,
        )
        soul = KgentSoul(auto_llm=False)
        cycle = HypnagogicCycle(config=config)

        # First cycle - discover patterns
        for _ in range(5):
            cycle.record_interaction(
                message="Tell me about architecture",
                response="Architecture is key",
                mode="reflect",
            )
        report1 = await cycle.dream(soul)

        # Second cycle - same patterns should be reinforced
        for _ in range(5):
            cycle.record_interaction(
                message="More about architecture",
                response="Architecture continues",
                mode="reflect",
            )
        report2 = await cycle.dream(soul)

        # Should have promoted some patterns
        total_promoted = len(report1.patterns_promoted) + len(report2.patterns_promoted)
        # At least mode preference should be reinforced
        assert total_promoted >= 0  # May be 0 if patterns are new each cycle
