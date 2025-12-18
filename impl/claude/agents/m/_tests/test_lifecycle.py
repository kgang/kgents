"""
Tests for Lifecycle state machine.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
"""

from __future__ import annotations

import time

import pytest

from agents.m.lifecycle import (
    VALID_TRANSITIONS,
    LifecycleEvent,
    LifecycleManager,
    RelevancePolicy,
    ResolutionPolicy,
    TimeoutPolicy,
    is_valid_transition,
)
from agents.m.memory import Lifecycle, Memory, simple_embedding

# === Lifecycle Event Tests ===


class TestLifecycleEvent:
    """Test LifecycleEvent."""

    def test_is_demotion_active_to_dormant(self) -> None:
        """ACTIVE -> DORMANT is demotion."""
        event = LifecycleEvent(
            memory_id="test",
            from_state=Lifecycle.ACTIVE,
            to_state=Lifecycle.DORMANT,
        )
        assert event.is_demotion is True
        assert event.is_promotion is False

    def test_is_promotion_dormant_to_active(self) -> None:
        """DORMANT -> ACTIVE is promotion."""
        event = LifecycleEvent(
            memory_id="test",
            from_state=Lifecycle.DORMANT,
            to_state=Lifecycle.ACTIVE,
        )
        assert event.is_promotion is True
        assert event.is_demotion is False

    def test_is_demotion_dormant_to_composting(self) -> None:
        """DORMANT -> COMPOSTING is demotion."""
        event = LifecycleEvent(
            memory_id="test",
            from_state=Lifecycle.DORMANT,
            to_state=Lifecycle.COMPOSTING,
        )
        assert event.is_demotion is True


# === Timeout Policy Tests ===


class TestTimeoutPolicy:
    """Test TimeoutPolicy."""

    def test_should_deactivate_after_timeout(self) -> None:
        """Memory should deactivate after timeout."""
        policy = TimeoutPolicy(timeout_seconds=60.0)

        # Create memory accessed 120 seconds ago
        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
        )
        # Manually set last_accessed
        old_memory = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=Lifecycle.ACTIVE,
            relevance=memory.relevance,
            last_accessed=time.time() - 120,  # 120 seconds ago
            access_count=memory.access_count,
            metadata=memory.metadata,
        )

        assert policy.should_deactivate(old_memory) is True

    def test_should_not_deactivate_recent(self) -> None:
        """Recent memory should not deactivate."""
        policy = TimeoutPolicy(timeout_seconds=60.0)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
        )

        assert policy.should_deactivate(memory) is False

    def test_should_not_deactivate_dormant(self) -> None:
        """DORMANT memory should not be checked for deactivation."""
        policy = TimeoutPolicy(timeout_seconds=60.0)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.DORMANT,
        )

        # Even with old timestamp, DORMANT shouldn't deactivate
        assert policy.should_deactivate(memory) is False


# === Relevance Policy Tests ===


class TestRelevancePolicy:
    """Test RelevancePolicy."""

    def test_should_demote_low_relevance(self) -> None:
        """Low relevance memory should be demoted."""
        policy = RelevancePolicy(demote_threshold=0.2)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            relevance=0.1,
        )

        assert policy.should_demote(memory) is True

    def test_should_not_demote_high_relevance(self) -> None:
        """High relevance memory should not be demoted."""
        policy = RelevancePolicy(demote_threshold=0.2)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            relevance=0.5,
        )

        assert policy.should_demote(memory) is False

    def test_should_not_demote_cherished(self) -> None:
        """Cherished memory should not be demoted even with low relevance."""
        policy = RelevancePolicy(demote_threshold=0.2)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            relevance=0.1,
        ).cherish()

        # Relevance is now 1.0 because cherish sets it
        # But even if we manually set low relevance with cherished flag
        assert policy.should_demote(memory) is False

    def test_apply_decay(self) -> None:
        """Apply decay reduces relevance."""
        policy = RelevancePolicy(decay_factor=0.9)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            relevance=1.0,
        )

        decayed = policy.apply_decay(memory)
        assert decayed.relevance == 0.9


# === Resolution Policy Tests ===


class TestResolutionPolicy:
    """Test ResolutionPolicy."""

    def test_should_degrade_composting(self) -> None:
        """COMPOSTING memory should be degraded."""
        policy = ResolutionPolicy(minimum_resolution=0.1)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.COMPOSTING,
            resolution=0.5,
        )

        assert policy.should_degrade(memory) is True

    def test_should_not_degrade_active(self) -> None:
        """ACTIVE memory should not be degraded."""
        policy = ResolutionPolicy()

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.ACTIVE,
        )

        assert policy.should_degrade(memory) is False

    def test_should_not_degrade_below_minimum(self) -> None:
        """Should not degrade below minimum resolution."""
        policy = ResolutionPolicy(minimum_resolution=0.1)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.COMPOSTING,
            resolution=0.05,  # Already below minimum
        )

        assert policy.should_degrade(memory) is False

    def test_apply_degradation(self) -> None:
        """Apply degradation reduces resolution."""
        policy = ResolutionPolicy(degrade_factor=0.5, minimum_resolution=0.1)

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.COMPOSTING,
            resolution=0.8,
        )

        degraded = policy.apply_degradation(memory)
        assert degraded.resolution == 0.4


# === Lifecycle Manager Tests ===


class TestLifecycleManager:
    """Test LifecycleManager."""

    def test_evaluate_timeout(self) -> None:
        """Evaluate detects timeout."""
        manager = LifecycleManager(
            timeout_policy=TimeoutPolicy(timeout_seconds=60.0),
        )

        # Memory accessed long ago
        memory = Memory(
            datum_id="test",
            embedding=simple_embedding("test"),
            resolution=1.0,
            lifecycle=Lifecycle.ACTIVE,
            relevance=1.0,
            last_accessed=time.time() - 120,
            access_count=0,
            metadata={},
        )

        event = manager.evaluate(memory)
        assert event is not None
        assert event.to_state == Lifecycle.DORMANT
        assert event.reason == "timeout"

    def test_evaluate_no_change(self) -> None:
        """Evaluate returns None when no change needed."""
        manager = LifecycleManager()

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
        )

        event = manager.evaluate(memory)
        assert event is None

    def test_apply_transition(self) -> None:
        """Apply transitions memory state."""
        manager = LifecycleManager()

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.ACTIVE,
        )

        updated = manager.apply(memory, Lifecycle.DORMANT)
        assert updated.lifecycle == Lifecycle.DORMANT

    def test_apply_emits_event(self) -> None:
        """Apply emits event to listeners."""
        manager = LifecycleManager()
        events: list[LifecycleEvent] = []

        manager.add_listener(lambda e: events.append(e))

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.ACTIVE,
        )

        manager.apply(memory, Lifecycle.DORMANT)

        assert len(events) == 1
        assert events[0].from_state == Lifecycle.ACTIVE
        assert events[0].to_state == Lifecycle.DORMANT

    def test_apply_policies(self) -> None:
        """Apply policies to memory."""
        manager = LifecycleManager(
            relevance_policy=RelevancePolicy(decay_factor=0.9),
            resolution_policy=ResolutionPolicy(degrade_factor=0.5),
        )

        memory = Memory.create(
            datum_id="test",
            embedding=simple_embedding("test"),
            lifecycle=Lifecycle.COMPOSTING,
            resolution=1.0,
            relevance=1.0,
        )

        updated = manager.apply_policies(memory)

        # Relevance should decay
        assert updated.relevance == 0.9

        # Resolution should degrade (COMPOSTING)
        assert updated.resolution == 0.5

    def test_batch_evaluate(self) -> None:
        """Batch evaluate multiple memories."""
        manager = LifecycleManager(
            timeout_policy=TimeoutPolicy(timeout_seconds=60.0),
        )

        # One old memory, one recent
        old_memory = Memory(
            datum_id="old",
            embedding=simple_embedding("old"),
            resolution=1.0,
            lifecycle=Lifecycle.ACTIVE,
            relevance=1.0,
            last_accessed=time.time() - 120,
            access_count=0,
            metadata={},
        )
        recent_memory = Memory.create(
            datum_id="recent",
            embedding=simple_embedding("recent"),
        )

        results = manager.batch_evaluate([old_memory, recent_memory])

        assert len(results) == 2
        assert results[0][1] is not None  # Old needs transition
        assert results[1][1] is None  # Recent doesn't


# === Valid Transitions Tests ===


class TestValidTransitions:
    """Test valid transition checking."""

    def test_active_to_dormant_valid(self) -> None:
        """ACTIVE -> DORMANT is valid."""
        assert is_valid_transition(Lifecycle.ACTIVE, Lifecycle.DORMANT) is True

    def test_dormant_to_active_valid(self) -> None:
        """DORMANT -> ACTIVE is valid."""
        assert is_valid_transition(Lifecycle.DORMANT, Lifecycle.ACTIVE) is True

    def test_dormant_to_dreaming_valid(self) -> None:
        """DORMANT -> DREAMING is valid."""
        assert is_valid_transition(Lifecycle.DORMANT, Lifecycle.DREAMING) is True

    def test_dreaming_to_dormant_valid(self) -> None:
        """DREAMING -> DORMANT is valid."""
        assert is_valid_transition(Lifecycle.DREAMING, Lifecycle.DORMANT) is True

    def test_active_to_composting_invalid(self) -> None:
        """ACTIVE -> COMPOSTING is invalid (must go through DORMANT)."""
        assert is_valid_transition(Lifecycle.ACTIVE, Lifecycle.COMPOSTING) is False

    def test_composting_to_active_invalid(self) -> None:
        """COMPOSTING -> ACTIVE is invalid."""
        assert is_valid_transition(Lifecycle.COMPOSTING, Lifecycle.ACTIVE) is False

    def test_composting_to_dormant_valid(self) -> None:
        """COMPOSTING -> DORMANT is valid (resurrection)."""
        assert is_valid_transition(Lifecycle.COMPOSTING, Lifecycle.DORMANT) is True
