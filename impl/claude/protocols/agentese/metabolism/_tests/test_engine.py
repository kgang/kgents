"""
Tests for MetabolicEngine.

Tests cover:
- Pressure accumulation from activity
- Natural decay
- Fever trigger at threshold
- Fever recovery at 50% of threshold
- Tithe (voluntary discharge)
- Temperature calculation
"""

from __future__ import annotations

import pytest
from protocols.agentese.metabolism import MetabolicEngine, create_metabolic_engine


class TestPressureAccumulation:
    """Test pressure accumulation from activity."""

    def test_pressure_accumulates_from_activity(self) -> None:
        """Activity increases pressure."""
        engine = MetabolicEngine()
        assert engine.pressure == 0.0

        engine.tick(100, 100)
        assert engine.pressure > 0

    def test_pressure_scales_with_activity(self) -> None:
        """More activity = more pressure."""
        engine1 = MetabolicEngine()
        engine2 = MetabolicEngine()

        engine1.tick(100, 100)
        engine2.tick(1000, 1000)

        assert engine2.pressure > engine1.pressure

    def test_pressure_accumulates_over_multiple_ticks(self) -> None:
        """Pressure accumulates across multiple ticks."""
        engine = MetabolicEngine()

        for _ in range(10):
            engine.tick(100, 100)

        # With decay, won't be exactly 10x, but should be significant
        assert engine.pressure > 0.5


class TestPressureDecay:
    """Test natural pressure decay."""

    def test_pressure_decays(self) -> None:
        """Natural decay reduces pressure over time."""
        engine = MetabolicEngine(pressure=1.0)

        # Tick with no activity
        engine.tick(0, 0)

        assert engine.pressure < 1.0

    def test_decay_rate_is_configurable(self) -> None:
        """Custom decay rate works."""
        engine_slow = MetabolicEngine(pressure=1.0, decay_rate=0.01)
        engine_fast = MetabolicEngine(pressure=1.0, decay_rate=0.1)

        engine_slow.tick(0, 0)
        engine_fast.tick(0, 0)

        assert engine_fast.pressure < engine_slow.pressure

    def test_pressure_stays_non_negative(self) -> None:
        """Pressure cannot go below zero."""
        engine = MetabolicEngine(pressure=0.001, decay_rate=0.5)

        # Even with high decay, pressure stays >= 0
        for _ in range(100):
            engine.tick(0, 0)

        assert engine.pressure >= 0.0


class TestFeverTrigger:
    """Test fever trigger at threshold."""

    def test_fever_triggers_at_threshold(self) -> None:
        """Pressure exceeding threshold triggers fever."""
        engine = MetabolicEngine(critical_threshold=0.5)

        # Pump up pressure
        event = None
        for _ in range(100):
            event = engine.tick(1000, 1000)
            if event is not None:
                break

        assert engine.in_fever
        assert event is not None
        assert event.trigger == "pressure_overflow"

    def test_fever_event_has_intensity(self) -> None:
        """FeverEvent contains intensity (pressure - threshold)."""
        engine = MetabolicEngine(critical_threshold=0.5)

        event = None
        for _ in range(100):
            event = engine.tick(1000, 1000)
            if event is not None:
                break

        assert event is not None
        assert event.intensity > 0

    def test_fever_event_has_oblique_strategy(self) -> None:
        """FeverEvent contains an oblique strategy."""
        engine = MetabolicEngine(critical_threshold=0.5)

        event = None
        for _ in range(100):
            event = engine.tick(1000, 1000)
            if event is not None:
                break

        assert event is not None
        assert event.oblique_strategy != ""

    def test_fever_discharges_pressure(self) -> None:
        """Fever trigger reduces pressure by 50%."""
        # Set pressure just below threshold, then one tick to trigger
        engine = MetabolicEngine(critical_threshold=0.5, pressure=0.6)

        # Trigger fever with a tick
        event = engine.tick(100, 100)

        assert event is not None
        assert engine.in_fever
        # Pressure was halved from ~0.8 (0.6 + 0.2 activity) to ~0.4
        # Then decay applied, so should be around 0.4
        assert engine.pressure < 0.5  # Below the threshold after halving

    def test_no_double_fever(self) -> None:
        """Can't trigger fever when already in fever."""
        engine = MetabolicEngine(critical_threshold=0.5)

        # Trigger first fever
        for _ in range(100):
            engine.tick(1000, 1000)
            if engine.in_fever:
                break

        assert engine.in_fever

        # Continue ticking - should not trigger second fever
        second_event = None
        for _ in range(10):
            second_event = engine.tick(1000, 1000)
            if second_event is not None:
                break

        # No second fever event while in fever
        assert second_event is None


class TestFeverRecovery:
    """Test fever recovery at 50% of threshold."""

    def test_fever_ends_at_recovery(self) -> None:
        """Fever ends when pressure drops below 50% of threshold."""
        engine = MetabolicEngine(
            critical_threshold=1.0,
            in_fever=True,
            pressure=0.4,  # Below 50% of threshold (0.5)
        )

        engine.tick(0, 0)  # Trigger recovery check

        assert not engine.in_fever

    def test_fever_continues_above_recovery(self) -> None:
        """Fever continues when pressure is above 50% of threshold."""
        engine = MetabolicEngine(
            critical_threshold=1.0,
            in_fever=True,
            pressure=0.6,  # Above 50% of threshold
        )

        engine.tick(0, 0)

        assert engine.in_fever


class TestTithe:
    """Test voluntary pressure discharge."""

    def test_tithe_discharges_pressure(self) -> None:
        """Voluntary tithe reduces pressure."""
        engine = MetabolicEngine(pressure=0.5)

        result = engine.tithe(0.2)

        assert engine.pressure == pytest.approx(0.3, abs=0.01)
        assert result["discharged"] == 0.2

    def test_tithe_returns_gratitude(self) -> None:
        """Tithe returns gratitude message."""
        engine = MetabolicEngine(pressure=0.5)

        result = engine.tithe(0.1)

        assert "gratitude" in result
        assert result["gratitude"] == "The river flows."

    def test_tithe_clamps_to_available(self) -> None:
        """Tithe can't discharge more than available."""
        engine = MetabolicEngine(pressure=0.1)

        result = engine.tithe(1.0)

        assert engine.pressure == 0.0
        assert result["discharged"] == 0.1  # Only discharged what was available

    def test_tithe_keeps_pressure_non_negative(self) -> None:
        """Pressure stays non-negative after tithe."""
        engine = MetabolicEngine(pressure=0.1)

        engine.tithe(0.5)

        assert engine.pressure >= 0.0


class TestTemperature:
    """Test token-based temperature."""

    def test_temperature_starts_at_zero(self) -> None:
        """Temperature is 0 when no output tokens."""
        engine = MetabolicEngine()

        assert engine.temperature == 0.0

    def test_temperature_reflects_ratio(self) -> None:
        """Temperature is input:output ratio."""
        engine = MetabolicEngine()

        engine.tick(1000, 500)

        assert engine.temperature == pytest.approx(2.0)  # 1000/500 = 2.0

    def test_temperature_capped_at_2(self) -> None:
        """Temperature capped at 2.0."""
        engine = MetabolicEngine()

        engine.tick(10000, 100)  # Would be 100, but capped

        assert engine.temperature == 2.0


class TestManualFever:
    """Test manual fever trigger."""

    def test_manual_fever_trigger(self) -> None:
        """Can manually trigger fever."""
        engine = MetabolicEngine()

        event = engine.trigger_manual_fever()

        assert event is not None
        assert event.trigger == "manual"
        assert engine.in_fever

    def test_manual_fever_fails_when_in_fever(self) -> None:
        """Can't manually trigger fever when already in fever."""
        engine = MetabolicEngine(in_fever=True)

        event = engine.trigger_manual_fever()

        assert event is None


class TestStatus:
    """Test status reporting."""

    def test_status_contains_all_fields(self) -> None:
        """Status dict contains all expected fields."""
        engine = MetabolicEngine(pressure=0.5, in_fever=True)

        status = engine.status()

        assert "pressure" in status
        assert "critical_threshold" in status
        assert "in_fever" in status
        assert "fever_start" in status
        assert "temperature" in status
        assert "input_tokens" in status
        assert "output_tokens" in status


class TestFactoryFunction:
    """Test create_metabolic_engine factory."""

    def test_factory_creates_configured_engine(self) -> None:
        """Factory creates engine with custom config."""
        engine = create_metabolic_engine(
            critical_threshold=2.0,
            decay_rate=0.05,
        )

        assert engine.critical_threshold == 2.0
        assert engine.decay_rate == 0.05
