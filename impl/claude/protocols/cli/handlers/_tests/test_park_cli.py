"""
Tests for Park CLI handler.

Wave 3 integration tests for crisis practice scenarios,
dialogue masks, and timer mechanics.
"""

from __future__ import annotations

import pytest

from protocols.cli.handlers.park import (
    DEFAULT_EIGENVECTORS,
    _ensure_scenario,
    _park_state,
    _render_bar,
    _render_mask_panel,
    _render_phase_inline,
    _timer_emoji,
    cmd_park,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clear_state():
    """Clear park state before and after each test."""
    _park_state.clear()
    yield
    _park_state.clear()


# =============================================================================
# Test: Command Routing
# =============================================================================


class TestCommandRouting:
    """Test subcommand routing."""

    def test_help_flag(self, capsys):
        """Test --help shows usage."""
        result = cmd_park(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "park" in captured.out.lower()
        assert "start" in captured.out.lower()

    def test_help_subcommand(self, capsys):
        """Test help subcommand."""
        result = cmd_park(["help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "park" in captured.out.lower()

    def test_unknown_subcommand(self, capsys):
        """Test unknown subcommand returns error."""
        result = cmd_park(["foobar"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out

    def test_no_args_shows_status(self, capsys):
        """Test no args shows status/help."""
        result = cmd_park([])
        assert result == 0
        captured = capsys.readouterr()
        # Should show help when no scenario running
        assert "No scenario running" in captured.out


# =============================================================================
# Test: Start Scenario
# =============================================================================


class TestStartScenario:
    """Test scenario start command."""

    def test_start_default(self, capsys):
        """Test starting default scenario."""
        result = cmd_park(["start"])
        assert result == 0
        captured = capsys.readouterr()
        assert "PARK:" in captured.out

        # Scenario should be running
        scenario = _ensure_scenario()
        assert scenario is not None

    def test_start_with_gdpr_timer(self, capsys):
        """Test starting with GDPR timer."""
        result = cmd_park(["start", "--timer=gdpr"])
        assert result == 0
        captured = capsys.readouterr()
        assert "GDPR" in captured.out or "72" in captured.out

    def test_start_with_template(self, capsys):
        """Test starting with template."""
        result = cmd_park(["start", "--template=data-breach"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Data Breach" in captured.out

    def test_start_already_running(self, capsys):
        """Test error when scenario already running."""
        cmd_park(["start"])
        result = cmd_park(["start"])
        assert result == 1
        captured = capsys.readouterr()
        assert "already running" in captured.out.lower()

    def test_start_unknown_timer(self, capsys):
        """Test error for unknown timer."""
        result = cmd_park(["start", "--timer=unknown"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown timer" in captured.out

    def test_start_with_mask(self, capsys):
        """Test starting with mask pre-selected."""
        result = cmd_park(["start", "--mask=trickster"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Trickster" in captured.out

        # Mask should be applied
        assert _park_state.get("masked_state") is not None


# =============================================================================
# Test: Status
# =============================================================================


class TestStatus:
    """Test status command."""

    def test_status_no_scenario(self, capsys):
        """Test status when no scenario running."""
        result = cmd_park(["status"])
        assert result == 0
        captured = capsys.readouterr()
        assert "No scenario running" in captured.out

    def test_status_with_scenario(self, capsys):
        """Test status with running scenario."""
        cmd_park(["start"])
        result = cmd_park(["status"])
        assert result == 0
        captured = capsys.readouterr()
        assert "PARK:" in captured.out
        assert "[TIMERS]" in captured.out
        assert "[PHASE]" in captured.out
        assert "[CONSENT]" in captured.out


# =============================================================================
# Test: Tick
# =============================================================================


class TestTick:
    """Test tick command."""

    def test_tick_no_scenario(self, capsys):
        """Test tick when no scenario running."""
        result = cmd_park(["tick"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No scenario running" in captured.out

    def test_tick_default(self, capsys):
        """Test single tick."""
        cmd_park(["start"])
        result = cmd_park(["tick"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Ticking" in captured.out

    def test_tick_multiple(self, capsys):
        """Test multiple ticks."""
        cmd_park(["start"])
        result = cmd_park(["tick", "--count=5"])
        assert result == 0
        captured = capsys.readouterr()
        assert "5" in captured.out


# =============================================================================
# Test: Phase Transitions
# =============================================================================


class TestPhaseTransitions:
    """Test phase transition command."""

    def test_phase_no_scenario(self, capsys):
        """Test phase when no scenario running."""
        result = cmd_park(["phase", "incident"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No scenario running" in captured.out

    def test_phase_no_args(self, capsys):
        """Test phase with no args shows current."""
        cmd_park(["start"])
        result = cmd_park(["phase"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Usage" in captured.out

    def test_phase_valid_transition(self, capsys):
        """Test valid phase transition."""
        cmd_park(["start"])
        # NORMAL -> INCIDENT should work
        result = cmd_park(["phase", "incident"])
        assert result == 0
        captured = capsys.readouterr()
        assert "INCIDENT" in captured.out

    def test_phase_invalid_transition(self, capsys):
        """Test invalid phase transition."""
        cmd_park(["start"])
        # NORMAL -> RECOVERY should fail (must go through INCIDENT -> RESPONSE first)
        result = cmd_park(["phase", "recovery"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Invalid transition" in captured.out


# =============================================================================
# Test: Mask Commands
# =============================================================================


class TestMaskCommands:
    """Test mask subcommands."""

    def test_mask_list(self, capsys):
        """Test listing masks."""
        result = cmd_park(["mask", "list"])
        assert result == 0
        captured = capsys.readouterr()
        assert "DIALOGUE MASKS" in captured.out
        assert "Trickster" in captured.out
        assert "Skeptic" in captured.out

    def test_mask_show(self, capsys):
        """Test showing mask details."""
        result = cmd_park(["mask", "show", "trickster"])
        assert result == 0
        captured = capsys.readouterr()
        assert "TRICKSTER" in captured.out
        assert "creativity" in captured.out.lower()

    def test_mask_show_unknown(self, capsys):
        """Test showing unknown mask."""
        result = cmd_park(["mask", "show", "unknown"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown mask" in captured.out

    def test_mask_don(self, capsys):
        """Test donning a mask."""
        cmd_park(["start"])
        result = cmd_park(["mask", "don", "skeptic"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Skeptic" in captured.out
        assert _park_state.get("masked_state") is not None

    def test_mask_don_already_wearing(self, capsys):
        """Test donning when already wearing."""
        cmd_park(["start"])
        cmd_park(["mask", "don", "trickster"])
        result = cmd_park(["mask", "don", "skeptic"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Already wearing" in captured.out

    def test_mask_doff(self, capsys):
        """Test removing mask."""
        cmd_park(["start"])
        cmd_park(["mask", "don", "trickster"])
        result = cmd_park(["mask", "doff"])
        assert result == 0
        captured = capsys.readouterr()
        assert "remove" in captured.out.lower()
        assert _park_state.get("masked_state") is None

    def test_mask_transform(self, capsys):
        """Test showing transform comparison."""
        cmd_park(["start"])
        cmd_park(["mask", "don", "warrior"])
        result = cmd_park(["mask", "transform"])
        assert result == 0
        captured = capsys.readouterr()
        assert "TRANSFORM" in captured.out
        assert "Base" in captured.out


# =============================================================================
# Test: Force
# =============================================================================


class TestForce:
    """Test force command."""

    def test_force_no_scenario(self, capsys):
        """Test force when no scenario running."""
        result = cmd_park(["force"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No scenario running" in captured.out

    def test_force_success(self, capsys):
        """Test successful force use."""
        cmd_park(["start"])
        result = cmd_park(["force"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Force used" in captured.out
        assert "Consent debt" in captured.out

    def test_force_limit(self, capsys):
        """Test force limit (3 per scenario)."""
        cmd_park(["start"])
        cmd_park(["force"])
        cmd_park(["force"])
        cmd_park(["force"])
        result = cmd_park(["force"])
        assert result == 1
        captured = capsys.readouterr()
        assert "limit reached" in captured.out.lower()


# =============================================================================
# Test: Complete
# =============================================================================


class TestComplete:
    """Test complete command."""

    def test_complete_no_scenario(self, capsys):
        """Test complete when no scenario running."""
        result = cmd_park(["complete"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No scenario running" in captured.out

    def test_complete_success(self, capsys):
        """Test successful completion."""
        cmd_park(["start"])
        result = cmd_park(["complete", "success"])
        assert result == 0
        captured = capsys.readouterr()
        assert "COMPLETE" in captured.out
        assert "SUCCESS" in captured.out

        # State should be cleared
        assert _ensure_scenario() is None

    def test_complete_failure(self, capsys):
        """Test failure completion."""
        cmd_park(["start"])
        result = cmd_park(["complete", "failure"])
        assert result == 0
        captured = capsys.readouterr()
        assert "FAILURE" in captured.out

    def test_complete_unknown_outcome(self, capsys):
        """Test unknown outcome."""
        cmd_park(["start"])
        result = cmd_park(["complete", "unknown"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown outcome" in captured.out


# =============================================================================
# Test: Display Functions
# =============================================================================


class TestDisplayFunctions:
    """Test display helper functions."""

    def test_render_bar(self):
        """Test progress bar rendering."""
        assert _render_bar(0.0, 1.0, 10) == ".........."
        assert _render_bar(0.5, 1.0, 10) == "#####....."
        assert _render_bar(1.0, 1.0, 10) == "##########"
        assert _render_bar(0.25, 1.0, 4) == "#..."

    def test_timer_emoji(self):
        """Test timer emoji mapping."""
        from agents.domain.drills import TimerStatus

        assert _timer_emoji(TimerStatus.ACTIVE) == "[>]"
        assert _timer_emoji(TimerStatus.WARNING) == "[!]"
        assert _timer_emoji(TimerStatus.CRITICAL) == "[X]"
        assert _timer_emoji(TimerStatus.EXPIRED) == "[x]"

    def test_render_phase_inline(self):
        """Test inline phase rendering."""
        from agents.domain.drills import CrisisPhase

        result = _render_phase_inline(CrisisPhase.INCIDENT)
        assert "[INCIDENT]" in result
        assert "NORMAL" in result
        assert "RESPONSE" in result

    def test_render_mask_panel(self):
        """Test mask panel rendering."""
        from agents.park import TRICKSTER_MASK

        result = _render_mask_panel(TRICKSTER_MASK)
        assert "TRICKSTER" in result
        assert "creativity" in result.lower()
        assert "ABILITIES" in result


# =============================================================================
# Test: Default Eigenvectors
# =============================================================================


class TestDefaults:
    """Test default values."""

    def test_default_eigenvectors(self):
        """Test default eigenvectors are neutral."""
        for key, value in DEFAULT_EIGENVECTORS.items():
            assert value == 0.5, f"{key} should be 0.5"

    def test_all_eigenvector_keys(self):
        """Test all expected eigenvector keys present."""
        expected = {
            "creativity",
            "trust",
            "empathy",
            "authority",
            "playfulness",
            "wisdom",
            "directness",
            "warmth",
        }
        assert set(DEFAULT_EIGENVECTORS.keys()) == expected
