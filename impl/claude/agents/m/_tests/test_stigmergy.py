"""
Tests for stigmergic memory via pheromone fields.

Verifies the key stigmergic properties:
- Traces decay naturally (Ebbinghaus integration)
- Agents can follow gradients
- Consensus emerges from accumulated traces
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from agents.m.stigmergy import (
    EnhancedStigmergicAgent,
    PheromoneField,
    SenseResult,
    SimpleConceptSpace,
    StigmergicAgent,
    Trace,
)


class TestTrace:
    """Tests for Trace dataclass."""

    def test_trace_creation(self) -> None:
        """Trace is created with correct fields."""
        trace = Trace(
            concept="python",
            intensity=1.0,
            depositor="agent_a",
        )

        assert trace.concept == "python"
        assert trace.intensity == 1.0
        assert trace.depositor == "agent_a"
        assert trace.metadata == {}

    def test_trace_age(self) -> None:
        """Trace age is calculated correctly."""
        trace = Trace(
            concept="python",
            intensity=1.0,
        )

        # Age should be very small (just created)
        assert trace.age.total_seconds() < 1.0

    def test_trace_with_metadata(self) -> None:
        """Trace can carry metadata."""
        trace = Trace(
            concept="python",
            intensity=1.0,
            metadata={"source": "exploration", "confidence": 0.8},
        )

        assert trace.metadata["source"] == "exploration"
        assert trace.metadata["confidence"] == 0.8


class TestPheromoneField:
    """Tests for PheromoneField."""

    @pytest.mark.asyncio
    async def test_deposit_creates_trace(self) -> None:
        """Depositing creates a trace."""
        field = PheromoneField()

        trace = await field.deposit("python", intensity=1.0)

        assert trace.concept == "python"
        assert trace.intensity == 1.0
        assert "python" in field.concepts

    @pytest.mark.asyncio
    async def test_deposit_multiple_traces(self) -> None:
        """Multiple deposits at same concept accumulate."""
        field = PheromoneField()

        await field.deposit("python", intensity=1.0)
        await field.deposit("python", intensity=0.5)

        gradient = await field.gradient_toward("python")
        # Total should be sum (minus any decay)
        assert gradient > 1.0

    @pytest.mark.asyncio
    async def test_sense_returns_gradients(self) -> None:
        """Sensing returns sorted gradients."""
        field = PheromoneField()

        await field.deposit("python", intensity=2.0)
        await field.deposit("javascript", intensity=1.0)
        await field.deposit("rust", intensity=3.0)

        results = await field.sense()

        assert len(results) == 3
        # Should be sorted by intensity (descending)
        concepts = [r.concept for r in results]
        assert concepts[0] == "rust"  # Highest intensity

    @pytest.mark.asyncio
    async def test_sense_returns_empty_for_empty_field(self) -> None:
        """Empty field returns no gradients."""
        field = PheromoneField()

        results = await field.sense()

        assert results == []

    @pytest.mark.asyncio
    async def test_gradient_toward_existing(self) -> None:
        """Gradient toward existing concept returns intensity."""
        field = PheromoneField()

        await field.deposit("python", intensity=2.5)

        gradient = await field.gradient_toward("python")

        # Should be close to deposited (some decay may occur)
        assert gradient > 2.0

    @pytest.mark.asyncio
    async def test_gradient_toward_nonexistent(self) -> None:
        """Gradient toward nonexistent concept returns 0."""
        field = PheromoneField()

        gradient = await field.gradient_toward("nonexistent")

        assert gradient == 0.0


class TestPheromoneDecay:
    """Tests for pheromone decay."""

    @pytest.mark.asyncio
    async def test_decay_reduces_intensity(self) -> None:
        """Decay reduces trace intensity."""
        field = PheromoneField(decay_rate=0.5)  # 50% per hour

        await field.deposit("python", intensity=1.0)

        # Apply 1 hour of decay
        await field.decay(elapsed=timedelta(hours=1))

        gradient = await field.gradient_toward("python")
        # Should be approximately 0.5 (1.0 * 0.5^1)
        assert 0.4 <= gradient <= 0.6

    @pytest.mark.asyncio
    async def test_decay_evaporates_weak_traces(self) -> None:
        """Weak traces evaporate completely."""
        field = PheromoneField(decay_rate=0.5, evaporation_threshold=0.1)

        await field.deposit("python", intensity=0.2)

        # Apply multiple hours of decay
        await field.decay(elapsed=timedelta(hours=3))

        # Trace should have evaporated
        assert "python" not in field.concepts

    @pytest.mark.asyncio
    async def test_natural_decay_on_sense(self) -> None:
        """Decay is applied when sensing."""
        field = PheromoneField(decay_rate=0.1)

        trace = Trace(
            concept="python",
            intensity=1.0,
        )
        # Artificially age the trace
        trace.deposited_at = datetime.now() - timedelta(hours=10)
        field._traces["python"] = [trace]

        # Sensing should apply decay
        results = await field.sense()

        # Intensity should be reduced
        if results:
            assert results[0].total_intensity < 1.0

    @pytest.mark.asyncio
    async def test_reinforce_increases_intensity(self) -> None:
        """Reinforcement increases trace intensity."""
        field = PheromoneField()

        await field.deposit("python", intensity=1.0)

        count = await field.reinforce("python", factor=2.0)

        assert count == 1
        gradient = await field.gradient_toward("python")
        assert gradient > 1.5  # Should be close to 2.0

    @pytest.mark.asyncio
    async def test_clear_concept_removes_traces(self) -> None:
        """Clear removes all traces at a concept."""
        field = PheromoneField()

        await field.deposit("python", intensity=1.0)
        await field.deposit("python", intensity=0.5)

        count = await field.clear_concept("python")

        assert count == 2
        assert "python" not in field.concepts


class TestPheromoneFieldStats:
    """Tests for field statistics."""

    @pytest.mark.asyncio
    async def test_stats_empty(self) -> None:
        """Stats for empty field."""
        field = PheromoneField()

        stats = field.stats()

        assert stats["concept_count"] == 0
        assert stats["trace_count"] == 0
        assert stats["deposit_count"] == 0

    @pytest.mark.asyncio
    async def test_stats_with_deposits(self) -> None:
        """Stats after deposits."""
        field = PheromoneField()

        await field.deposit("python", intensity=1.0)
        await field.deposit("javascript", intensity=0.5)

        stats = field.stats()

        assert stats["concept_count"] == 2
        assert stats["trace_count"] == 2
        assert stats["deposit_count"] == 2
        assert stats["avg_intensity"] == pytest.approx(0.75)


class TestStigmergicAgent:
    """Tests for basic StigmergicAgent."""

    @pytest.mark.asyncio
    async def test_agent_starts_nowhere(self) -> None:
        """Agent starts with no position."""
        field = PheromoneField()
        agent = StigmergicAgent(field)

        assert agent.current_position is None
        assert agent.path_history == []

    @pytest.mark.asyncio
    async def test_move_to_updates_position(self) -> None:
        """Moving updates position and history."""
        field = PheromoneField()
        agent = StigmergicAgent(field)

        await agent.move_to("python")

        assert agent.current_position == "python"
        assert agent.path_history == ["python"]

    @pytest.mark.asyncio
    async def test_deposit_at_position(self) -> None:
        """Agent deposits at current position."""
        field = PheromoneField()
        agent = StigmergicAgent(field, deposit_intensity=2.0)

        await agent.move_to("python")
        trace = await agent.deposit()

        assert trace is not None
        assert trace.concept == "python"
        assert trace.intensity == 2.0

    @pytest.mark.asyncio
    async def test_deposit_without_position_returns_none(self) -> None:
        """Deposit without position returns None."""
        field = PheromoneField()
        agent = StigmergicAgent(field)

        trace = await agent.deposit()

        assert trace is None

    @pytest.mark.asyncio
    async def test_follow_gradient_with_traces(self) -> None:
        """Agent follows existing gradients."""
        field = PheromoneField()
        agent = StigmergicAgent(field, exploration_rate=0.0)  # No exploration

        # Create strong gradient toward python
        await field.deposit("python", intensity=10.0)

        result = await agent.follow_gradient()

        # Should follow the gradient (with high probability)
        assert result == "python"
        assert agent.current_position == "python"

    @pytest.mark.asyncio
    async def test_follow_gradient_explores_when_empty(self) -> None:
        """Agent explores when field is empty."""
        field = PheromoneField()
        agent = StigmergicAgent(field, exploration_rate=0.0)

        result = await agent.follow_gradient()

        # Basic agent returns None for exploration
        assert result is None


class TestEnhancedStigmergicAgent:
    """Tests for EnhancedStigmergicAgent with concept space."""

    @pytest.mark.asyncio
    async def test_explore_samples_from_vocabulary(self) -> None:
        """Enhanced agent explores by sampling."""
        field = PheromoneField()
        concept_space = SimpleConceptSpace(vocabulary=["python", "javascript", "rust"])
        agent = EnhancedStigmergicAgent(
            field=field,
            concept_space=concept_space,
            exploration_rate=1.0,  # Always explore
        )

        result = await agent.follow_gradient()

        assert result in ["python", "javascript", "rust"]
        assert agent.current_position in ["python", "javascript", "rust"]

    @pytest.mark.asyncio
    async def test_follow_neighbors(self) -> None:
        """Agent can follow neighbors of current position."""
        field = PheromoneField()
        concept_space = SimpleConceptSpace(
            vocabulary=["python", "programming", "coding"],
            neighbors_map={
                "python": ["programming", "coding"],
                "programming": ["python", "coding"],
                "coding": ["python", "programming"],
            },
        )
        agent = EnhancedStigmergicAgent(
            field=field,
            concept_space=concept_space,
            exploration_rate=0.0,
        )

        # Start at python
        await agent.move_to("python")

        # Add gradient to programming
        await field.deposit("programming", intensity=10.0)

        result = await agent.follow_neighbors()

        # Should prefer programming (stronger gradient)
        assert result in ["programming", "coding"]

    @pytest.mark.asyncio
    async def test_follow_neighbors_random_when_no_gradient(self) -> None:
        """Picks random neighbor when no gradients."""
        field = PheromoneField()
        concept_space = SimpleConceptSpace(
            vocabulary=["python", "programming", "coding"],
            neighbors_map={
                "python": ["programming", "coding"],
            },
        )
        agent = EnhancedStigmergicAgent(
            field=field,
            concept_space=concept_space,
        )

        await agent.move_to("python")

        result = await agent.follow_neighbors()

        assert result in ["programming", "coding"]


class TestSimpleConceptSpace:
    """Tests for SimpleConceptSpace."""

    @pytest.mark.asyncio
    async def test_sample_returns_from_vocabulary(self) -> None:
        """Sample returns concept from vocabulary."""
        space = SimpleConceptSpace(vocabulary=["a", "b", "c"])

        for _ in range(10):
            concept = await space.sample()
            assert concept in ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_sample_empty_raises(self) -> None:
        """Sample from empty vocabulary raises."""
        space = SimpleConceptSpace(vocabulary=[])

        with pytest.raises(ValueError):
            await space.sample()

    @pytest.mark.asyncio
    async def test_neighbors_returns_map(self) -> None:
        """Neighbors returns from map."""
        space = SimpleConceptSpace(
            vocabulary=["a", "b", "c"],
            neighbors_map={"a": ["b", "c"]},
        )

        neighbors = await space.neighbors("a")

        assert neighbors == ["b", "c"]

    @pytest.mark.asyncio
    async def test_neighbors_returns_empty_for_unknown(self) -> None:
        """Unknown concept has no neighbors."""
        space = SimpleConceptSpace(vocabulary=["a", "b", "c"])

        neighbors = await space.neighbors("unknown")

        assert neighbors == []


class TestStigmergicConsensus:
    """Tests verifying consensus emergence from stigmergy."""

    @pytest.mark.asyncio
    async def test_multiple_deposits_increase_gradient(self) -> None:
        """Multiple deposits at same concept increase gradient."""
        field = PheromoneField()

        # Multiple agents deposit at same concept
        for i in range(5):
            await field.deposit("python", intensity=1.0, depositor=f"agent_{i}")

        gradient = await field.gradient_toward("python")

        # Should be significantly higher than single deposit
        assert gradient > 4.0

    @pytest.mark.asyncio
    async def test_dominant_concept_emerges(self) -> None:
        """Most deposited concept becomes dominant."""
        field = PheromoneField()

        # Python gets more deposits
        for _ in range(10):
            await field.deposit("python", intensity=1.0)

        # Others get fewer
        for _ in range(3):
            await field.deposit("javascript", intensity=1.0)

        for _ in range(1):
            await field.deposit("rust", intensity=1.0)

        results = await field.sense()

        # Python should be dominant (first)
        assert results[0].concept == "python"

    @pytest.mark.asyncio
    async def test_trace_count_tracked(self) -> None:
        """SenseResult includes trace count."""
        field = PheromoneField()

        for _ in range(5):
            await field.deposit("python", intensity=1.0)

        results = await field.sense()

        assert results[0].trace_count == 5

    @pytest.mark.asyncio
    async def test_dominant_depositor_tracked(self) -> None:
        """SenseResult includes dominant depositor."""
        field = PheromoneField()

        # Agent A deposits more
        for _ in range(5):
            await field.deposit("python", intensity=1.0, depositor="agent_a")

        for _ in range(2):
            await field.deposit("python", intensity=1.0, depositor="agent_b")

        results = await field.sense()

        assert results[0].dominant_depositor == "agent_a"


class TestEbbinghausIntegration:
    """Tests for Ebbinghaus forgetting curve integration."""

    @pytest.mark.asyncio
    async def test_exponential_decay(self) -> None:
        """Decay follows exponential curve."""
        field = PheromoneField(decay_rate=0.1)  # 10% per hour

        await field.deposit("python", intensity=1.0)

        # After 1 hour: 1.0 * 0.9^1 = 0.9
        await field.decay(elapsed=timedelta(hours=1))
        g1 = await field.gradient_toward("python")
        assert 0.85 <= g1 <= 0.95

        # After another hour: 0.9 * 0.9^1 ≈ 0.81
        await field.decay(elapsed=timedelta(hours=1))
        g2 = await field.gradient_toward("python")
        assert 0.75 <= g2 <= 0.85

    @pytest.mark.asyncio
    async def test_recent_traces_stronger(self) -> None:
        """Recent traces are stronger than old ones."""
        field = PheromoneField(decay_rate=0.1)

        # Old trace
        old_trace = Trace(concept="old", intensity=1.0)
        old_trace.deposited_at = datetime.now() - timedelta(hours=10)
        field._traces["old"] = [old_trace]

        # New trace
        await field.deposit("new", intensity=1.0)

        old_gradient = await field.gradient_toward("old")
        new_gradient = await field.gradient_toward("new")

        assert new_gradient > old_gradient
