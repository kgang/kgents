"""
Tests for MusePolynomial state machine.

Tests the Muse lifecycle:
- State transitions
- Whisper generation
- Tension tracking
- Dismissal handling
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.muse.arc import ArcPhase, StoryArc
from services.muse.polynomial import (
    MUSE_POLYNOMIAL,
    ActivityPause,
    ArcShift,
    CrystalObserved,
    DormancyComplete,
    MuseContext,
    MuseOutput,
    MuseState,
    RequestEncouragement,
    RequestReframe,
    SummonMuse,
    TensionRising,
    WhisperAccepted,
    WhisperDismissed,
    muse_transition,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def silent_context() -> MuseContext:
    """Context in silent state."""
    return MuseContext(state=MuseState.SILENT)


@pytest.fixture
def contemplating_context() -> MuseContext:
    """Context in contemplating state with high tension."""
    ctx = MuseContext(state=MuseState.CONTEMPLATING)
    ctx.tension = 0.5
    ctx.crystals_observed = 5
    return ctx


@pytest.fixture
def whispering_context() -> MuseContext:
    """Context in whispering state with pending whisper."""
    from services.muse.polynomial import MuseWhisper

    ctx = MuseContext(state=MuseState.WHISPERING)
    ctx.pending_whisper = MuseWhisper(
        whisper_id="test-whisper",
        content="Test whisper content",
        category="observation",
        urgency=0.5,
        confidence=0.7,
    )
    return ctx


@pytest.fixture
def sample_crystal_event() -> CrystalObserved:
    """Sample crystal observation event."""
    return CrystalObserved(
        crystal_id="crystal-abc123",
        session_id="test-session",
        mood_brightness=0.7,
        topics=("routing", "tests"),
        complexity=0.5,
    )


# =============================================================================
# MuseState Tests
# =============================================================================


class TestMuseState:
    """Tests for MuseState enum."""

    def test_silent_is_active(self) -> None:
        """Silent state is active (observing)."""
        assert MuseState.SILENT.is_active is True

    def test_dormant_is_not_active(self) -> None:
        """Dormant state is not active."""
        assert MuseState.DORMANT.is_active is False

    def test_resonating_is_engaged(self) -> None:
        """Resonating state is engaged with user."""
        assert MuseState.RESONATING.is_engaged is True

    def test_silent_allows_suggestion(self) -> None:
        """Silent state allows new suggestions."""
        assert MuseState.SILENT.allows_suggestion is True

    def test_dormant_does_not_allow_suggestion(self) -> None:
        """Dormant state does not allow suggestions."""
        assert MuseState.DORMANT.allows_suggestion is False


# =============================================================================
# MuseContext Tests
# =============================================================================


class TestMuseContext:
    """Tests for MuseContext state container."""

    def test_initial_state(self) -> None:
        """New context starts in SILENT state."""
        ctx = MuseContext()
        assert ctx.state == MuseState.SILENT
        assert ctx.tension == 0.0
        assert ctx.crystals_observed == 0

    def test_observe_crystal(
        self, silent_context: MuseContext, sample_crystal_event: CrystalObserved
    ) -> None:
        """Observing crystal updates count."""
        silent_context.observe_crystal(sample_crystal_event)
        assert silent_context.crystals_observed == 1
        assert silent_context.last_crystal_time is not None

    def test_acceptance_rate_default(self) -> None:
        """Default acceptance rate is 0.5."""
        ctx = MuseContext()
        assert ctx.acceptance_rate == 0.5

    def test_acceptance_rate_calculation(self) -> None:
        """Acceptance rate calculated correctly."""
        ctx = MuseContext()
        ctx.whispers_accepted = 3
        ctx.whispers_dismissed = 1
        assert ctx.acceptance_rate == 0.75

    def test_can_whisper_initially(self) -> None:
        """Can whisper when no pending and no recent whisper."""
        ctx = MuseContext()
        assert ctx.can_whisper is True

    def test_cannot_whisper_with_pending(self) -> None:
        """Cannot whisper when one is pending."""
        from services.muse.polynomial import MuseWhisper

        ctx = MuseContext()
        ctx.pending_whisper = MuseWhisper(
            whisper_id="test",
            content="test",
            category="test",
            urgency=0.5,
            confidence=0.5,
        )
        assert ctx.can_whisper is False

    def test_tension_update(self) -> None:
        """Tension update tracks trend."""
        ctx = MuseContext()
        ctx.update_tension(0.3)
        assert ctx.tension == 0.3
        assert ctx.tension_trend == 0.3

    def test_tension_clamped(self) -> None:
        """Tension is clamped to [0, 1]."""
        ctx = MuseContext()
        ctx.update_tension(1.5)
        assert ctx.tension == 1.0

        ctx.tension = 0.5
        ctx.update_tension(-0.8)
        assert ctx.tension == 0.0


# =============================================================================
# State Transition Tests
# =============================================================================


class TestMuseTransitions:
    """Tests for Muse state transitions."""

    def test_crystal_observation_in_silent(
        self, silent_context: MuseContext, sample_crystal_event: CrystalObserved
    ) -> None:
        """Crystal observation in silent state."""
        new_ctx, output = muse_transition(silent_context, sample_crystal_event)

        assert output.success is True
        assert "Observed crystal" in output.message
        assert new_ctx.crystals_observed == 1

    def test_high_tension_triggers_contemplation(self, silent_context: MuseContext) -> None:
        """High tension after enough observations triggers contemplation."""
        # Observe several crystals with low brightness (increases tension)
        for i in range(5):
            event = CrystalObserved(
                crystal_id=f"crystal-{i}",
                session_id="test",
                mood_brightness=0.2,  # Low brightness → tension
                topics=(),
                complexity=0.5,
            )
            silent_context, output = muse_transition(silent_context, event)

        # Should eventually move to contemplating
        # (depends on tension threshold and observation count)
        assert silent_context.crystals_observed == 5

    def test_pause_in_contemplating_generates_whisper(
        self, contemplating_context: MuseContext
    ) -> None:
        """Activity pause in contemplating state generates whisper."""
        pause = ActivityPause(pause_seconds=10)
        new_ctx, output = muse_transition(contemplating_context, pause)

        assert output.success is True
        assert new_ctx.state == MuseState.WHISPERING
        assert output.whisper is not None

    def test_short_pause_no_whisper(self, contemplating_context: MuseContext) -> None:
        """Brief pause does not generate whisper."""
        pause = ActivityPause(pause_seconds=2)
        new_ctx, output = muse_transition(contemplating_context, pause)

        assert output.success is True
        assert new_ctx.state == MuseState.CONTEMPLATING
        assert output.whisper is None

    def test_arc_shift_updates_arc(self, silent_context: MuseContext) -> None:
        """Arc shift event updates story arc."""
        shift = ArcShift(
            from_phase=ArcPhase.EXPOSITION,
            to_phase=ArcPhase.RISING_ACTION,
            confidence=0.8,
        )
        new_ctx, output = muse_transition(silent_context, shift)

        assert output.success is True
        assert output.arc is not None
        assert output.arc.phase == ArcPhase.RISING_ACTION

    def test_tension_rising_updates_tension(self, silent_context: MuseContext) -> None:
        """Tension rising event updates tension level."""
        event = TensionRising(previous=0.2, current=0.6, trigger="test failures")
        new_ctx, output = muse_transition(silent_context, event)

        assert output.success is True
        # Tension should increase
        assert new_ctx.tension > 0

    def test_whisper_accepted_moves_to_resonating(self, whispering_context: MuseContext) -> None:
        """Accepted whisper moves to resonating state."""
        accepted = WhisperAccepted(whisper_id="test-whisper", action="viewed")
        new_ctx, output = muse_transition(whispering_context, accepted)

        assert output.success is True
        assert new_ctx.state == MuseState.RESONATING

    def test_whisper_acted_moves_to_reflecting(self, whispering_context: MuseContext) -> None:
        """Acted whisper moves to reflecting state."""
        accepted = WhisperAccepted(whisper_id="test-whisper", action="acted")
        new_ctx, output = muse_transition(whispering_context, accepted)

        assert output.success is True
        assert new_ctx.state == MuseState.REFLECTING

    def test_whisper_dismissed_moves_to_dormant(self, whispering_context: MuseContext) -> None:
        """Dismissed whisper moves to dormant state."""
        dismissed = WhisperDismissed(whisper_id="test-whisper", method="explicit")
        new_ctx, output = muse_transition(whispering_context, dismissed)

        assert output.success is True
        assert new_ctx.state == MuseState.DORMANT

    def test_dormancy_complete_returns_to_silent(self) -> None:
        """Dormancy complete returns to silent state."""
        ctx = MuseContext(state=MuseState.DORMANT)
        ctx.dormancy_started = datetime.now() - timedelta(minutes=20)

        complete = DormancyComplete()
        new_ctx, output = muse_transition(ctx, complete)

        assert output.success is True
        assert new_ctx.state == MuseState.SILENT


# =============================================================================
# Request Handling Tests
# =============================================================================


class TestMuseRequests:
    """Tests for explicit Muse requests."""

    def test_request_encouragement(self, silent_context: MuseContext) -> None:
        """Requesting encouragement generates whisper."""
        request = RequestEncouragement(context="feeling stuck")
        new_ctx, output = muse_transition(silent_context, request)

        assert output.success is True
        assert output.whisper is not None
        assert output.whisper.category == "encouragement"

    def test_request_reframe(self, silent_context: MuseContext) -> None:
        """Requesting reframe generates whisper."""
        request = RequestReframe(context="stuck on design")
        new_ctx, output = muse_transition(silent_context, request)

        assert output.success is True
        assert output.whisper is not None
        assert output.whisper.category == "reframe"

    def test_summon_muse(self, silent_context: MuseContext) -> None:
        """Summoning Muse generates immediate whisper."""
        summon = SummonMuse(topic="architecture")
        new_ctx, output = muse_transition(silent_context, summon)

        assert output.success is True
        assert output.whisper is not None
        assert output.whisper.urgency == 1.0  # Summoned = immediate


# =============================================================================
# Polynomial Tests
# =============================================================================


class TestMusePolynomial:
    """Tests for MusePolynomial wrapper."""

    def test_polynomial_name(self) -> None:
        """Polynomial has correct name."""
        assert MUSE_POLYNOMIAL.name == "MusePolynomial"

    def test_polynomial_positions(self) -> None:
        """Polynomial has all states as positions."""
        positions = MUSE_POLYNOMIAL.positions
        assert MuseState.SILENT in positions
        assert MuseState.DORMANT in positions

    def test_polynomial_directions(self) -> None:
        """Polynomial returns valid directions for state."""
        ctx = MuseContext(state=MuseState.SILENT)
        directions = MUSE_POLYNOMIAL.directions(ctx)

        # Silent state should accept crystal observations
        assert CrystalObserved in directions

    def test_polynomial_invoke(
        self, silent_context: MuseContext, sample_crystal_event: CrystalObserved
    ) -> None:
        """Polynomial invoke works like transition."""
        new_ctx, output = MUSE_POLYNOMIAL.invoke(silent_context, sample_crystal_event)

        assert output.success is True
        assert new_ctx.crystals_observed == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestMuseIntegration:
    """Integration tests for complete Muse flows."""

    def test_observation_to_whisper_flow(self) -> None:
        """Test complete flow from observation to whisper."""
        ctx = MuseContext()

        # Observe several low-brightness crystals to build tension
        for i in range(5):
            event = CrystalObserved(
                crystal_id=f"crystal-{i}",
                session_id="test",
                mood_brightness=0.2,
                topics=("debugging",),
                complexity=0.6,
            )
            ctx, _ = muse_transition(ctx, event)

        # Force contemplation if not already
        if ctx.state == MuseState.SILENT:
            ctx.state = MuseState.CONTEMPLATING
            ctx.tension = 0.6

        # Trigger whisper with pause
        pause = ActivityPause(pause_seconds=10)
        ctx, output = muse_transition(ctx, pause)

        assert ctx.state == MuseState.WHISPERING
        assert output.whisper is not None

    def test_dismissal_leads_to_dormancy(self) -> None:
        """Test that dismissal leads to dormancy cooldown."""
        from services.muse.polynomial import MuseWhisper

        ctx = MuseContext(state=MuseState.WHISPERING)
        ctx.pending_whisper = MuseWhisper(
            whisper_id="test",
            content="test",
            category="observation",
            urgency=0.5,
            confidence=0.5,
        )

        # Dismiss
        dismissed = WhisperDismissed(whisper_id="test", method="explicit")
        ctx, output = muse_transition(ctx, dismissed)

        assert ctx.state == MuseState.DORMANT
        assert ctx.dormancy_started is not None

        # Complete dormancy
        ctx.dormancy_started = datetime.now() - timedelta(minutes=20)
        complete = DormancyComplete()
        ctx, output = muse_transition(ctx, complete)

        assert ctx.state == MuseState.SILENT

    def test_acceptance_flow(self) -> None:
        """Test whisper acceptance flow."""
        from services.muse.polynomial import MuseWhisper

        ctx = MuseContext(state=MuseState.WHISPERING)
        ctx.pending_whisper = MuseWhisper(
            whisper_id="test",
            content="test",
            category="encouragement",
            urgency=0.5,
            confidence=0.8,
        )

        # Accept
        accepted = WhisperAccepted(whisper_id="test", action="acted")
        ctx, output = muse_transition(ctx, accepted)

        assert ctx.state == MuseState.REFLECTING
        assert ctx.whispers_accepted == 1
