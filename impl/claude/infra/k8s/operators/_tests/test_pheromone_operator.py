"""Tests for Pheromone Operator decay logic.

These tests verify the pheromone decay system works correctly
without requiring a real K8s cluster.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from infra.k8s.operators.pheromone_operator import (
    DEFAULT_DECAY_RATE,
    DREAM_DECAY_MULTIPLIER,
    MockPheromone,
    MockPheromoneField,
    calculate_decay,
    get_mock_field,
    reset_mock_field,
    should_delete,
)


class TestCalculateDecay:
    """Test the decay calculation function."""

    def test_basic_decay(self) -> None:
        """Basic decay reduces intensity."""
        result = calculate_decay(
            current_intensity=1.0,
            decay_rate=0.1,
            pheromone_type="WARNING",
            elapsed_minutes=1.0,
        )
        assert result == pytest.approx(0.9)

    def test_decay_over_time(self) -> None:
        """Decay accumulates over multiple minutes."""
        result = calculate_decay(
            current_intensity=1.0,
            decay_rate=0.1,
            pheromone_type="WARNING",
            elapsed_minutes=5.0,
        )
        assert result == pytest.approx(0.5)

    def test_decay_clamps_to_zero(self) -> None:
        """Decay cannot go below zero."""
        result = calculate_decay(
            current_intensity=0.1,
            decay_rate=0.5,
            pheromone_type="WARNING",
            elapsed_minutes=1.0,
        )
        assert result == 0.0

    def test_dream_decay_slower(self) -> None:
        """DREAM pheromones decay at half rate (accursed share)."""
        warning_decay = calculate_decay(
            current_intensity=1.0,
            decay_rate=0.2,
            pheromone_type="WARNING",
            elapsed_minutes=1.0,
        )
        dream_decay = calculate_decay(
            current_intensity=1.0,
            decay_rate=0.2,
            pheromone_type="DREAM",
            elapsed_minutes=1.0,
        )

        assert warning_decay == pytest.approx(0.8)
        assert dream_decay == pytest.approx(0.9)  # Half decay rate
        assert dream_decay > warning_decay  # DREAM preserved longer

    def test_zero_decay_rate(self) -> None:
        """Zero decay rate means no decay."""
        result = calculate_decay(
            current_intensity=1.0,
            decay_rate=0.0,
            pheromone_type="STATE",
            elapsed_minutes=100.0,
        )
        assert result == 1.0


class TestShouldDelete:
    """Test the deletion decision function."""

    def test_delete_at_zero_intensity(self) -> None:
        """Delete when intensity reaches zero."""
        assert should_delete(intensity=0.0, created_at=None, ttl_seconds=None) is True

    def test_dont_delete_with_intensity(self) -> None:
        """Don't delete when intensity remains."""
        assert should_delete(intensity=0.5, created_at=None, ttl_seconds=None) is False

    def test_delete_on_ttl_expired(self) -> None:
        """Delete when TTL has expired."""
        created = datetime.now(timezone.utc) - timedelta(seconds=120)
        assert should_delete(intensity=1.0, created_at=created, ttl_seconds=60) is True

    def test_dont_delete_before_ttl(self) -> None:
        """Don't delete before TTL expires."""
        created = datetime.now(timezone.utc) - timedelta(seconds=30)
        assert should_delete(intensity=1.0, created_at=created, ttl_seconds=60) is False

    def test_no_ttl_only_checks_intensity(self) -> None:
        """Without TTL, only intensity matters."""
        created = datetime.now(timezone.utc) - timedelta(days=100)
        assert (
            should_delete(intensity=0.5, created_at=created, ttl_seconds=None) is False
        )


class TestMockPheromone:
    """Test the mock pheromone implementation."""

    def test_create_pheromone(self) -> None:
        """Can create a mock pheromone."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="WARNING",
            intensity=0.8,
            source="B-gent",
            payload="Budget exceeded",
        )
        assert ph.name == "test-ph"
        assert ph.type == "WARNING"
        assert ph.intensity == 0.8
        assert ph.source == "B-gent"
        assert ph.payload == "Budget exceeded"
        assert ph.sensed_by == []

    def test_decay_reduces_intensity(self) -> None:
        """Decay reduces pheromone intensity."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="WARNING",
            intensity=1.0,
            source="B-gent",
            decay_rate=0.2,
        )
        deleted = ph.decay(elapsed_minutes=1.0)
        assert deleted is False
        assert ph.intensity == pytest.approx(0.8)

    def test_decay_returns_true_when_depleted(self) -> None:
        """Decay returns True when intensity reaches zero."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="WARNING",
            intensity=0.1,
            source="B-gent",
            decay_rate=0.5,
        )
        deleted = ph.decay(elapsed_minutes=1.0)
        assert deleted is True
        assert ph.intensity == 0.0

    def test_sense_records_agent(self) -> None:
        """Sensing records which agents sensed the pheromone."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="MEMORY",
            intensity=0.5,
            source="M-gent",
        )
        ph.sense("O-gent")
        ph.sense("N-gent")
        ph.sense("O-gent")  # Duplicate

        assert "O-gent" in ph.sensed_by
        assert "N-gent" in ph.sensed_by
        assert len(ph.sensed_by) == 2  # No duplicates


class TestMockPheromoneField:
    """Test the mock pheromone field."""

    def test_emit_and_list(self) -> None:
        """Can emit and list pheromones."""
        field = MockPheromoneField()
        field.emit("ph-1", "WARNING", 0.8, "F-gent")
        field.emit("ph-2", "MEMORY", 0.5, "M-gent")

        pheromones = field.list()
        assert len(pheromones) == 2
        assert {ph.name for ph in pheromones} == {"ph-1", "ph-2"}

    def test_sense_filters_by_type(self) -> None:
        """Sensing can filter by pheromone type."""
        field = MockPheromoneField()
        field.emit("warn-1", "WARNING", 0.8, "F-gent")
        field.emit("mem-1", "MEMORY", 0.5, "M-gent")
        field.emit("warn-2", "WARNING", 0.6, "J-gent")

        warnings = field.sense("O-gent", pheromone_type="WARNING")
        assert len(warnings) == 2
        assert all(ph.type == "WARNING" for ph in warnings)
        # Sorted by intensity descending
        assert warnings[0].intensity > warnings[1].intensity

    def test_sense_records_sensor(self) -> None:
        """Sensing records the sensing agent."""
        field = MockPheromoneField()
        field.emit("ph-1", "WARNING", 0.8, "F-gent")

        field.sense("O-gent", "WARNING")
        ph = field.list()[0]
        assert "O-gent" in ph.sensed_by

    def test_tick_applies_decay(self) -> None:
        """Tick applies decay to all pheromones."""
        field = MockPheromoneField()
        field.emit("ph-1", "WARNING", 0.5, "F-gent", decay_rate=0.1)
        field.emit("ph-2", "MEMORY", 0.3, "M-gent", decay_rate=0.2)

        field.tick(elapsed_minutes=1.0)

        pheromones = {ph.name: ph.intensity for ph in field.list()}
        assert pheromones["ph-1"] == pytest.approx(0.4)
        assert pheromones["ph-2"] == pytest.approx(0.1)

    def test_tick_deletes_depleted(self) -> None:
        """Tick deletes pheromones that decay to zero."""
        field = MockPheromoneField()
        field.emit("will-survive", "WARNING", 1.0, "F-gent", decay_rate=0.1)
        field.emit("will-die", "MEMORY", 0.1, "M-gent", decay_rate=0.5)

        deleted = field.tick(elapsed_minutes=1.0)

        assert deleted == 1
        names = [ph.name for ph in field.list()]
        assert "will-survive" in names
        assert "will-die" not in names


class TestGlobalMockField:
    """Test the global mock field singleton."""

    def setup_method(self) -> None:
        """Reset the global field before each test."""
        reset_mock_field()

    def test_get_creates_singleton(self) -> None:
        """get_mock_field creates a singleton."""
        field1 = get_mock_field()
        field2 = get_mock_field()
        assert field1 is field2

    def test_reset_clears_field(self) -> None:
        """reset_mock_field clears the singleton."""
        field1 = get_mock_field()
        field1.emit("ph-1", "WARNING", 0.8, "F-gent")

        reset_mock_field()
        field2 = get_mock_field()

        assert field1 is not field2
        assert len(field2.list()) == 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_stigmergic_coordination(self) -> None:
        """Test agents coordinating via pheromones without direct communication."""
        field = MockPheromoneField()

        # F-gent detects test failure, emits WARNING
        field.emit(
            name="test-failure-graph-py",
            pheromone_type="WARNING",
            intensity=0.9,
            source="F-gent",
            payload='{"file": "graph.py", "line": 142, "occurrences": 3}',
        )

        # O-gent monitors field, senses all warnings
        warnings = field.sense("O-gent", pheromone_type="WARNING")
        assert len(warnings) == 1
        assert warnings[0].intensity == 0.9

        # Time passes, decay occurs
        field.tick(elapsed_minutes=2.0)

        # Intensity reduced but still present
        warnings = field.sense("O-gent", pheromone_type="WARNING")
        assert warnings[0].intensity < 0.9

        # F-gent fixes the issue - doesn't emit more warnings
        # Over time, the WARNING decays away naturally
        for _ in range(10):
            field.tick(elapsed_minutes=1.0)

        # Eventually deleted
        assert len(field.list()) == 0

    def test_dream_pheromone_preserved(self) -> None:
        """DREAM pheromones decay slower (accursed share principle)."""
        field = MockPheromoneField()

        # Dreamer emits creative tangent
        field.emit(
            name="dream-haiku-auth",
            pheromone_type="DREAM",
            intensity=0.8,
            source="Dreamer",
            payload="What if auth.py was a haiku?",
            decay_rate=0.2,  # Same rate, but DREAM applies multiplier
        )

        # Standard warning for comparison
        field.emit(
            name="warning-auth",
            pheromone_type="WARNING",
            intensity=0.8,
            source="F-gent",
            decay_rate=0.2,
        )

        # After 2 minutes of decay
        field.tick(elapsed_minutes=2.0)

        pheromones = {ph.name: ph.intensity for ph in field.list()}

        # DREAM decays at 0.2 * 0.5 = 0.1 per minute
        # WARNING decays at 0.2 per minute
        assert pheromones["dream-haiku-auth"] == pytest.approx(0.6)  # 0.8 - 0.1*2
        assert pheromones["warning-auth"] == pytest.approx(0.4)  # 0.8 - 0.2*2

        # DREAM preserved longer - joy cannot be optimized
        assert pheromones["dream-haiku-auth"] > pheromones["warning-auth"]
