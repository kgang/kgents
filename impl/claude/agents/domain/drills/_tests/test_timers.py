"""
Tests for Compliance Timers: Regulatory Deadline Management.

Verifies:
1. Timer configuration (GDPR 72h, SEC 4-day, HIPAA 60-day)
2. Timer state lifecycle (start, tick, stop, pause/resume)
3. Status transitions (ACTIVE → WARNING → CRITICAL → EXPIRED)
4. Display utilities (countdown formatting, colors)
"""

from datetime import datetime, timedelta

import pytest
from agents.domain.drills.timers import (
    GDPR_72H_CONFIG,
    HIPAA_60DAY_CONFIG,
    SEC_4DAY_CONFIG,
    TIMER_CONFIGS,
    TimerConfig,
    TimerState,
    TimerStatus,
    TimerType,
    create_gdpr_timer,
    create_hipaa_timer,
    create_sec_timer,
    create_timer,
    format_countdown,
    get_status_color,
)


class TestTimerTypes:
    """Tests for TimerType enum."""

    def test_has_five_types(self) -> None:
        """All timer types exist."""
        assert len(TimerType) == 5
        assert TimerType.GDPR_72H is not None
        assert TimerType.SEC_4DAY is not None
        assert TimerType.HIPAA_60DAY is not None
        assert TimerType.INTERNAL_SLA is not None
        assert TimerType.CUSTOM is not None


class TestTimerStatus:
    """Tests for TimerStatus enum."""

    def test_has_seven_statuses(self) -> None:
        """All timer statuses exist."""
        assert len(TimerStatus) == 7
        assert TimerStatus.PENDING is not None
        assert TimerStatus.ACTIVE is not None
        assert TimerStatus.WARNING is not None
        assert TimerStatus.CRITICAL is not None
        assert TimerStatus.EXPIRED is not None
        assert TimerStatus.COMPLETED is not None
        assert TimerStatus.PAUSED is not None


class TestTimerConfig:
    """Tests for timer configurations."""

    def test_gdpr_config(self) -> None:
        """GDPR timer config is correct."""
        config = GDPR_72H_CONFIG
        assert config.timer_type == TimerType.GDPR_72H
        assert config.name == "GDPR 72-Hour Notification"
        assert config.duration == timedelta(hours=72)
        assert config.can_pause is False
        assert config.extensions_allowed == 0
        assert config.warning_threshold == 0.75  # 54 hours
        assert config.critical_threshold == 0.90  # ~65 hours

    def test_sec_config(self) -> None:
        """SEC timer config is correct."""
        config = SEC_4DAY_CONFIG
        assert config.timer_type == TimerType.SEC_4DAY
        assert config.name == "SEC 8-K Disclosure"
        assert config.duration == timedelta(days=4)
        assert config.can_pause is False

    def test_hipaa_config(self) -> None:
        """HIPAA timer config is correct."""
        config = HIPAA_60DAY_CONFIG
        assert config.timer_type == TimerType.HIPAA_60DAY
        assert config.name == "HIPAA Breach Notification"
        assert config.duration == timedelta(days=60)
        assert config.can_pause is False

    def test_all_types_in_registry(self) -> None:
        """All standard types have configs in registry."""
        assert TimerType.GDPR_72H in TIMER_CONFIGS
        assert TimerType.SEC_4DAY in TIMER_CONFIGS
        assert TimerType.HIPAA_60DAY in TIMER_CONFIGS


class TestTimerState:
    """Tests for TimerState lifecycle."""

    def test_initial_state_is_pending(self) -> None:
        """Timer starts in PENDING status."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        assert timer.status == TimerStatus.PENDING
        assert timer.started_at is None

    def test_start_transitions_to_active(self) -> None:
        """Starting timer transitions to ACTIVE."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        timer.start()

        assert timer.status == TimerStatus.ACTIVE
        assert timer.started_at is not None

    def test_cannot_start_twice(self) -> None:
        """Cannot start an already-started timer."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        timer.start()

        with pytest.raises(ValueError, match="Cannot start timer"):
            timer.start()

    def test_elapsed_is_zero_before_start(self) -> None:
        """Elapsed time is zero before starting."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        assert timer.elapsed == timedelta()

    def test_elapsed_increases_after_start(self) -> None:
        """Elapsed time increases after starting."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        timer.start()
        # Immediately elapsed should be very small but non-negative
        assert timer.elapsed.total_seconds() >= 0

    def test_remaining_decreases(self) -> None:
        """Remaining time decreases as elapsed increases."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        assert timer.remaining == timedelta(hours=72)

        timer.start()
        # Remaining should now be slightly less than full duration
        assert timer.remaining < timedelta(hours=72)

    def test_progress_starts_at_zero(self) -> None:
        """Progress is 0 before starting."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        assert timer.progress == 0.0

    def test_stop_sets_completed(self) -> None:
        """Stopping timer sets COMPLETED status."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        timer.start()
        timer.stop(success=True)

        assert timer.status == TimerStatus.COMPLETED
        assert timer.stopped_at is not None

    def test_stop_failure_sets_expired(self) -> None:
        """Stopping with failure sets EXPIRED status."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        timer.start()
        timer.stop(success=False)

        assert timer.status == TimerStatus.EXPIRED


class TestTimerStatusTransitions:
    """Tests for automatic status transitions based on progress."""

    def test_tick_updates_status(self) -> None:
        """Tick method updates timer status."""
        timer = TimerState(config=GDPR_72H_CONFIG)
        timer.start()

        status = timer.tick()
        assert status == TimerStatus.ACTIVE

    def test_status_to_warning_at_threshold(self) -> None:
        """Status changes to WARNING at warning threshold."""
        # Create a short-duration timer for testing
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Test Timer",
            description="For testing",
            duration=timedelta(seconds=10),
            warning_threshold=0.5,
            critical_threshold=0.9,
        )
        timer = TimerState(config=config)
        timer.start()

        # Manually set started_at to simulate elapsed time
        timer.started_at = datetime.now() - timedelta(seconds=6)  # 60% elapsed

        timer.tick()
        assert timer.status == TimerStatus.WARNING

    def test_status_to_critical_at_threshold(self) -> None:
        """Status changes to CRITICAL at critical threshold."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Test Timer",
            description="For testing",
            duration=timedelta(seconds=10),
            warning_threshold=0.5,
            critical_threshold=0.9,
        )
        timer = TimerState(config=config)
        timer.start()

        # 95% elapsed
        timer.started_at = datetime.now() - timedelta(seconds=9.5)

        timer.tick()
        assert timer.status == TimerStatus.CRITICAL

    def test_status_to_expired_when_exceeded(self) -> None:
        """Status changes to EXPIRED when duration exceeded."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Test Timer",
            description="For testing",
            duration=timedelta(seconds=1),
            warning_threshold=0.5,
            critical_threshold=0.9,
        )
        timer = TimerState(config=config)
        timer.start()

        # 200% elapsed (well past duration)
        timer.started_at = datetime.now() - timedelta(seconds=2)

        timer.tick()
        assert timer.status == TimerStatus.EXPIRED


class TestTimerPause:
    """Tests for timer pause/resume (when allowed)."""

    def test_compliance_timers_cannot_pause(self) -> None:
        """Compliance timers cannot be paused."""
        timer = create_gdpr_timer()
        timer.start()

        with pytest.raises(ValueError, match="cannot be paused"):
            timer.pause()

    def test_custom_timer_can_pause(self) -> None:
        """Custom timers with can_pause=True can pause."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Pausable Timer",
            description="Can pause",
            duration=timedelta(hours=1),
            can_pause=True,
        )
        timer = TimerState(config=config)
        timer.start()

        timer.pause()
        assert timer.status == TimerStatus.PAUSED

    def test_resume_after_pause(self) -> None:
        """Can resume a paused timer."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Pausable Timer",
            description="Can pause",
            duration=timedelta(hours=1),
            can_pause=True,
        )
        timer = TimerState(config=config)
        timer.start()
        timer.pause()
        timer.resume()

        assert timer.status == TimerStatus.ACTIVE


class TestTimerManifest:
    """Tests for timer manifest/display."""

    def test_manifest_contains_required_fields(self) -> None:
        """Manifest includes all required display fields."""
        timer = create_gdpr_timer()
        timer.start()

        manifest = timer.manifest()

        assert "name" in manifest
        assert "type" in manifest
        assert "status" in manifest
        assert "remaining" in manifest
        assert "remaining_seconds" in manifest
        assert "progress" in manifest
        assert "started_at" in manifest

    def test_remaining_formatted_correctly(self) -> None:
        """Remaining time is formatted as HH:MM:SS."""
        timer = create_gdpr_timer()
        manifest = timer.manifest()

        # Should be "72:00:00" format
        remaining = manifest["remaining"]
        assert ":" in remaining
        parts = remaining.split(":")
        assert len(parts) == 3


class TestTimerFactories:
    """Tests for timer factory functions."""

    def test_create_gdpr_timer(self) -> None:
        """create_gdpr_timer creates GDPR timer."""
        timer = create_gdpr_timer()
        assert timer.config.timer_type == TimerType.GDPR_72H
        assert timer.status == TimerStatus.PENDING

    def test_create_sec_timer(self) -> None:
        """create_sec_timer creates SEC timer."""
        timer = create_sec_timer()
        assert timer.config.timer_type == TimerType.SEC_4DAY

    def test_create_hipaa_timer(self) -> None:
        """create_hipaa_timer creates HIPAA timer."""
        timer = create_hipaa_timer()
        assert timer.config.timer_type == TimerType.HIPAA_60DAY

    def test_create_custom_timer(self) -> None:
        """create_timer with CUSTOM type requires duration."""
        timer = create_timer(
            TimerType.CUSTOM,
            custom_duration=timedelta(hours=24),
            custom_name="Custom Deadline",
        )
        assert timer.config.duration == timedelta(hours=24)
        assert timer.config.name == "Custom Deadline"

    def test_create_custom_timer_requires_duration(self) -> None:
        """Custom timer without duration raises error."""
        with pytest.raises(ValueError, match="requires duration"):
            create_timer(TimerType.CUSTOM)


class TestDisplayUtilities:
    """Tests for display utility functions."""

    def test_format_countdown_active(self) -> None:
        """Active timer shows clock emoji."""
        timer = create_gdpr_timer()
        timer.start()

        countdown = format_countdown(timer)
        assert "⏱️" in countdown

    def test_format_countdown_warning(self) -> None:
        """Warning timer shows warning emoji."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Test",
            description="Test",
            duration=timedelta(seconds=10),
            warning_threshold=0.5,
            critical_threshold=0.9,
        )
        timer = TimerState(config=config)
        timer.start()
        timer.started_at = datetime.now() - timedelta(seconds=6)
        timer.tick()

        countdown = format_countdown(timer)
        assert "⚠️" in countdown

    def test_format_countdown_critical(self) -> None:
        """Critical timer shows alarm emoji."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Test",
            description="Test",
            duration=timedelta(seconds=10),
            warning_threshold=0.5,
            critical_threshold=0.9,
        )
        timer = TimerState(config=config)
        timer.start()
        timer.started_at = datetime.now() - timedelta(seconds=9.5)
        timer.tick()

        countdown = format_countdown(timer)
        assert "🚨" in countdown

    def test_format_countdown_expired(self) -> None:
        """Expired timer shows EXPIRED text."""
        config = TimerConfig(
            timer_type=TimerType.CUSTOM,
            name="Test",
            description="Test",
            duration=timedelta(seconds=1),
        )
        timer = TimerState(config=config)
        timer.start()
        timer.started_at = datetime.now() - timedelta(seconds=2)
        timer.tick()

        countdown = format_countdown(timer)
        assert "EXPIRED" in countdown

    def test_get_status_color(self) -> None:
        """Status colors are correct."""
        timer = TimerState(config=GDPR_72H_CONFIG)

        timer.status = TimerStatus.ACTIVE
        assert get_status_color(timer) == "green"

        timer.status = TimerStatus.WARNING
        assert get_status_color(timer) == "yellow"

        timer.status = TimerStatus.CRITICAL
        assert get_status_color(timer) == "red"

        timer.status = TimerStatus.EXPIRED
        assert get_status_color(timer) == "darkred"
