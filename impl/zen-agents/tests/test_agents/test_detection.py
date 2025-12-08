"""Tests for StateDetector (Fix pattern).

StateDetector uses the Fix pattern for polling session state.
Confidence accumulates across iterations until stable.
"""

import pytest
from unittest.mock import AsyncMock

from zen_agents.models.session import Session, SessionState, SessionType
from zen_agents.agents.detection import (
    DetectionState,
    StateDetector,
    detect_state,
)


class TestDetectionState:
    """Test DetectionState dataclass."""

    def test_initial_state(self):
        """Initial state has zero confidence."""
        state = DetectionState.initial()
        assert state.session_state == SessionState.RUNNING
        assert state.confidence == 0.0
        assert not state.is_stable()

    def test_is_stable_threshold(self):
        """State is stable when confidence >= 0.8."""
        state = DetectionState(
            session_state=SessionState.RUNNING,
            confidence=0.79,
        )
        assert not state.is_stable()

        state = DetectionState(
            session_state=SessionState.RUNNING,
            confidence=0.8,
        )
        assert state.is_stable()

        state = DetectionState(
            session_state=SessionState.RUNNING,
            confidence=1.0,
        )
        assert state.is_stable()

    def test_completed_state(self):
        """Completed state with exit code."""
        state = DetectionState(
            session_state=SessionState.COMPLETED,
            confidence=1.0,
            exit_code=0,
        )
        assert state.is_stable()
        assert state.exit_code == 0

    def test_failed_state(self):
        """Failed state with error message."""
        state = DetectionState(
            session_state=SessionState.FAILED,
            confidence=1.0,
            exit_code=1,
            error_message="Process exited with code 1",
        )
        assert state.is_stable()
        assert state.error_message is not None


class TestStateDetector:
    """Test StateDetector agent."""

    @pytest.mark.asyncio
    async def test_running_session_accumulates_confidence(self, mock_session, mock_tmux):
        """Running session accumulates confidence across polls."""
        detector = StateDetector()
        initial = DetectionState.initial()

        # First poll: 0.0 + 0.2 = 0.2
        result = await detector.invoke((mock_session, mock_tmux, initial))
        assert result.session_state == SessionState.RUNNING
        assert result.confidence == 0.2

        # Second poll: 0.2 + 0.2 = 0.4
        result = await detector.invoke((mock_session, mock_tmux, result))
        assert result.confidence == 0.4

        # Third poll: 0.4 + 0.2 = 0.6
        result = await detector.invoke((mock_session, mock_tmux, result))
        assert abs(result.confidence - 0.6) < 0.001  # Float comparison

        # Fourth poll: 0.6 + 0.2 = 0.8 (stable!)
        result = await detector.invoke((mock_session, mock_tmux, result))
        assert result.confidence == 0.8
        assert result.is_stable()

    @pytest.mark.asyncio
    async def test_dead_session_completed(self, mock_session, mock_tmux_dead):
        """Dead session with exit code 0 is completed."""
        mock_tmux_dead.get_exit_code.return_value = 0
        detector = StateDetector()
        initial = DetectionState.initial()

        result = await detector.invoke((mock_session, mock_tmux_dead, initial))
        assert result.session_state == SessionState.COMPLETED
        assert result.confidence == 1.0
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_dead_session_failed(self, mock_session, mock_tmux_dead):
        """Dead session with non-zero exit code is failed."""
        detector = StateDetector()
        initial = DetectionState.initial()

        result = await detector.invoke((mock_session, mock_tmux_dead, initial))
        assert result.session_state == SessionState.FAILED
        assert result.confidence == 1.0
        assert result.exit_code == 1
        assert "exited with code 1" in result.error_message

    @pytest.mark.asyncio
    async def test_state_change_resets_confidence(self, mock_session, mock_tmux):
        """Confidence resets when state changes."""
        detector = StateDetector()

        # Start with high confidence in COMPLETED state
        previous = DetectionState(
            session_state=SessionState.COMPLETED,
            confidence=0.8,
        )

        # Session is now running (state changed)
        result = await detector.invoke((mock_session, mock_tmux, previous))
        # Confidence resets to 0.2 (not accumulated)
        assert result.session_state == SessionState.RUNNING
        assert result.confidence == 0.2

    def test_detector_name(self):
        """Detector has correct name."""
        detector = StateDetector()
        assert detector.name == "StateDetector"


class TestDetectStateFunction:
    """Test detect_state convenience function."""

    @pytest.mark.asyncio
    async def test_converges_on_running(self, mock_session, mock_tmux):
        """detect_state converges for running session."""
        result = await detect_state(
            session=mock_session,
            tmux=mock_tmux,
            max_iterations=10,
        )
        assert result.converged
        assert result.value.session_state == SessionState.RUNNING
        assert result.value.confidence >= 0.8

    @pytest.mark.asyncio
    async def test_converges_immediately_on_dead(self, mock_session, mock_tmux_dead):
        """detect_state converges quickly for dead session."""
        result = await detect_state(
            session=mock_session,
            tmux=mock_tmux_dead,
            max_iterations=10,
        )
        assert result.converged
        assert result.value.session_state == SessionState.FAILED
        assert result.iterations <= 2  # Should converge quickly

    @pytest.mark.asyncio
    async def test_max_iterations_limit(self, mock_session, mock_tmux):
        """detect_state respects max_iterations."""
        # Use very low max_iterations
        result = await detect_state(
            session=mock_session,
            tmux=mock_tmux,
            max_iterations=2,
        )
        # Won't converge in 2 iterations (need 4 to reach 0.8)
        assert result.iterations <= 2
