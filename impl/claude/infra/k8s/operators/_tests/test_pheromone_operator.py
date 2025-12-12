"""Tests for Pheromone Operator - Passive Stigmergy (v2.0).

These tests verify the pheromone decay system works correctly
without requiring a real K8s cluster.

v2.0 Changes:
- calculate_intensity() replaces calculate_decay()
- Intensity calculated on read, not stored
- MockPheromone.intensity is a property, not a field
- should_evaporate() replaces should_delete()
"""
# mypy: disable-error-code="union-attr"

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from infra.k8s.operators.pheromone_operator import (
    DEFAULT_HALF_LIFE_MINUTES,
    DREAM_HALF_LIFE_MULTIPLIER,
    EVAPORATION_THRESHOLD,
    MockPheromone,
    MockPheromoneField,
    calculate_intensity,
    get_mock_field,
    reset_mock_field,
    should_evaporate,
)


class TestCalculateIntensity:
    """Test the intensity calculation function (Passive Stigmergy)."""

    def test_fresh_pheromone_full_intensity(self) -> None:
        """Fresh pheromone has full intensity."""
        spec = {
            "emittedAt": datetime.now(timezone.utc).isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "WARNING",
        }
        result = calculate_intensity(spec)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_half_life_decay(self) -> None:
        """After one half-life, intensity is ~0.5."""
        old_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        spec = {
            "emittedAt": old_time.isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "WARNING",
        }
        result = calculate_intensity(spec)
        assert result == pytest.approx(0.5, abs=0.05)

    def test_double_half_life_quarter_intensity(self) -> None:
        """After two half-lives, intensity is ~0.25."""
        old_time = datetime.now(timezone.utc) - timedelta(minutes=20)
        spec = {
            "emittedAt": old_time.isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "WARNING",
        }
        result = calculate_intensity(spec)
        assert result == pytest.approx(0.25, abs=0.05)

    def test_dream_decays_slower(self) -> None:
        """DREAM pheromones decay at half rate (2x half-life)."""
        old_time = datetime.now(timezone.utc) - timedelta(minutes=10)

        warning_spec = {
            "emittedAt": old_time.isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "WARNING",
        }
        dream_spec = {
            "emittedAt": old_time.isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "DREAM",  # Gets 2x multiplier
        }

        warning_intensity = calculate_intensity(warning_spec)
        dream_intensity = calculate_intensity(dream_spec)

        assert warning_intensity == pytest.approx(0.5, abs=0.05)
        # DREAM with 2x multiplier: effective half-life is 20min
        # After 10min: 0.5^(10/20) = 0.5^0.5 ≈ 0.707
        assert dream_intensity == pytest.approx(0.707, abs=0.05)
        assert dream_intensity > warning_intensity

    def test_legacy_intensity_field(self) -> None:
        """Legacy specs with 'intensity' field still work."""
        spec = {
            "intensity": 0.8,  # Legacy field
            "type": "STATE",
        }
        result = calculate_intensity(spec)
        assert result == 0.8

    def test_custom_initial_intensity(self) -> None:
        """Custom initial intensity is respected."""
        spec = {
            "emittedAt": datetime.now(timezone.utc).isoformat(),
            "initialIntensity": 0.5,
            "halfLifeMinutes": 10,
            "type": "STATE",
        }
        result = calculate_intensity(spec)
        assert result == pytest.approx(0.5, abs=0.01)


class TestShouldEvaporate:
    """Test the evaporation decision function."""

    def test_evaporate_below_threshold(self) -> None:
        """Evaporate when intensity below threshold."""
        # Very old pheromone should be below threshold
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        spec = {
            "emittedAt": old_time.isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "STATE",
        }
        meta = {"creationTimestamp": old_time.isoformat()}
        assert should_evaporate(spec, meta) is True

    def test_dont_evaporate_fresh(self) -> None:
        """Don't evaporate fresh pheromones."""
        spec = {
            "emittedAt": datetime.now(timezone.utc).isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 10,
            "type": "STATE",
        }
        meta = {"creationTimestamp": datetime.now(timezone.utc).isoformat()}
        assert should_evaporate(spec, meta) is False

    def test_evaporate_on_ttl_expired(self) -> None:
        """Evaporate when TTL has expired."""
        spec = {
            "emittedAt": datetime.now(timezone.utc).isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 60,  # Long half-life
            "type": "STATE",
            "ttl_seconds": 60,
        }
        old_time = datetime.now(timezone.utc) - timedelta(seconds=120)
        meta = {"creationTimestamp": old_time.isoformat()}
        assert should_evaporate(spec, meta) is True

    def test_dont_evaporate_before_ttl(self) -> None:
        """Don't evaporate before TTL expires."""
        spec = {
            "emittedAt": datetime.now(timezone.utc).isoformat(),
            "initialIntensity": 1.0,
            "halfLifeMinutes": 60,
            "type": "STATE",
            "ttl_seconds": 120,
        }
        recent = datetime.now(timezone.utc) - timedelta(seconds=30)
        meta = {"creationTimestamp": recent.isoformat()}
        assert should_evaporate(spec, meta) is False


class TestMockPheromone:
    """Test the mock pheromone implementation (Passive Stigmergy)."""

    def test_create_pheromone(self) -> None:
        """Can create a mock pheromone."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="WARNING",
            initial_intensity=0.8,
            source="B-gent",
            payload="Budget exceeded",
        )
        assert ph.name == "test-ph"
        assert ph.type == "WARNING"
        assert ph.initial_intensity == 0.8
        assert ph.source == "B-gent"
        assert ph.payload == "Budget exceeded"
        assert ph.sensed_by == []

    def test_intensity_is_property(self) -> None:
        """Intensity is calculated on access (Passive Stigmergy)."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="WARNING",
            initial_intensity=1.0,
            source="B-gent",
            half_life_minutes=10,
        )
        # Fresh pheromone should be ~1.0
        assert ph.intensity == pytest.approx(1.0, abs=0.01)

    def test_should_evaporate_threshold(self) -> None:
        """should_evaporate() returns True below threshold."""
        # Create a pheromone with very short half-life in the past
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="WARNING",
            initial_intensity=1.0,
            source="B-gent",
            half_life_minutes=0.1,  # Very short
        )
        # Manually set emitted_at to the past
        ph.emitted_at = datetime.now(timezone.utc) - timedelta(hours=1)
        assert ph.should_evaporate() is True

    def test_sense_records_agent(self) -> None:
        """Sensing records which agents sensed the pheromone."""
        ph = MockPheromone(
            name="test-ph",
            pheromone_type="MEMORY",
            initial_intensity=0.5,
            source="M-gent",
        )
        ph.sense("O-gent")
        ph.sense("N-gent")
        ph.sense("O-gent")  # Duplicate

        assert "O-gent" in ph.sensed_by
        assert "N-gent" in ph.sensed_by
        assert len(ph.sensed_by) == 2  # No duplicates


class TestMockPheromoneField:
    """Test the mock pheromone field (Passive Stigmergy)."""

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
        field.emit("warn-1", "WARNING", initial_intensity=0.8, source="F-gent")
        field.emit("mem-1", "MEMORY", initial_intensity=0.5, source="M-gent")
        field.emit("warn-2", "WARNING", initial_intensity=0.6, source="J-gent")

        warnings = field.sense("O-gent", pheromone_type="WARNING")
        assert len(warnings) == 2
        assert all(ph.type == "WARNING" for ph in warnings)
        # Sorted by intensity descending
        assert warnings[0].intensity >= warnings[1].intensity

    def test_sense_filters_by_target(self) -> None:
        """Sensing can filter by target agent."""
        field = MockPheromoneField()
        field.emit("broadcast", "WARNING", 0.8, "F-gent", target=None)
        field.emit("targeted", "WARNING", 0.8, "F-gent", target="O-gent")
        field.emit("other", "WARNING", 0.8, "F-gent", target="N-gent")

        # O-gent should see broadcast and targeted at them
        sensed = field.sense("O-gent", target="O-gent")
        assert len(sensed) == 2  # broadcast + targeted
        names = {ph.name for ph in sensed}
        assert "broadcast" in names
        assert "targeted" in names
        assert "other" not in names

    def test_sense_records_sensor(self) -> None:
        """Sensing records the sensing agent."""
        field = MockPheromoneField()
        field.emit("ph-1", "WARNING", 0.8, "F-gent")

        field.sense("O-gent", "WARNING")
        ph = field.list()[0]
        assert "O-gent" in ph.sensed_by

    def test_tick_garbage_collects(self) -> None:
        """Tick garbage collects evaporated pheromones."""
        field = MockPheromoneField()
        # Create one with very short half-life
        field.emit(
            "will-die",
            "MEMORY",
            initial_intensity=0.02,
            source="M-gent",
            half_life_minutes=0.1,
        )
        # Manually age it
        field.get("will-die").emitted_at = datetime.now(timezone.utc) - timedelta(
            hours=1
        )

        # Create one that will survive
        field.emit(
            "will-survive",
            "WARNING",
            initial_intensity=1.0,
            source="F-gent",
            half_life_minutes=60,
        )

        deleted = field.tick()

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
            initial_intensity=0.9,
            source="F-gent",
            payload='{"file": "graph.py", "line": 142, "occurrences": 3}',
        )

        # O-gent monitors field, senses all warnings
        warnings = field.sense("O-gent", pheromone_type="WARNING")
        assert len(warnings) == 1
        # Fresh pheromone should be close to initial
        assert warnings[0].intensity == pytest.approx(0.9, abs=0.05)

        # Sense records the agent
        assert "O-gent" in warnings[0].sensed_by

    def test_dream_pheromone_preserved(self) -> None:
        """DREAM pheromones decay slower (accursed share principle)."""
        field = MockPheromoneField()

        # Dreamer emits creative tangent
        field.emit(
            name="dream-haiku-auth",
            pheromone_type="DREAM",
            initial_intensity=0.8,
            source="Dreamer",
            payload="What if auth.py was a haiku?",
            half_life_minutes=10,
        )

        # Standard warning for comparison
        field.emit(
            name="warning-auth",
            pheromone_type="WARNING",
            initial_intensity=0.8,
            source="F-gent",
            half_life_minutes=10,
        )

        # Get the pheromones
        dream_ph = field.get("dream-haiku-auth")
        warning_ph = field.get("warning-auth")

        # Manually age them by 10 minutes
        aged_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        dream_ph.emitted_at = aged_time
        warning_ph.emitted_at = aged_time

        # DREAM with 2x half-life multiplier decays slower
        # WARNING: 0.8 * 0.5^(10/10) = 0.4
        # DREAM: 0.8 * 0.5^(10/20) ≈ 0.566
        assert warning_ph.intensity == pytest.approx(0.4, abs=0.05)
        assert dream_ph.intensity == pytest.approx(0.566, abs=0.05)

        # DREAM preserved longer - joy cannot be optimized
        assert dream_ph.intensity > warning_ph.intensity

    def test_passive_stigmergy_no_updates(self) -> None:
        """Verify that intensity is calculated, not stored."""
        field = MockPheromoneField()

        field.emit(
            name="test-ph",
            pheromone_type="STATE",
            initial_intensity=1.0,
            source="test",
            half_life_minutes=10,
        )

        ph = field.get("test-ph")

        # Store initial_intensity (the stored value)
        stored_value = ph.initial_intensity

        # Access intensity multiple times (calculated on read)
        i1 = ph.intensity
        i2 = ph.intensity

        # Stored value unchanged
        assert ph.initial_intensity == stored_value

        # Calculated values should be very close (calculated at ~same time)
        assert i1 == pytest.approx(i2, abs=0.001)
