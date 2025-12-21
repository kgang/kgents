"""
Tests for Morning Coffee polynomial state machine.

Verifies:
- State transitions follow the ritual flow
- Exit is honored from any state (Law 5)
- Skip works from any non-DORMANT state (Law 1)
- Direction functions are correct
- Law compliance
"""

import pytest

from services.liminal.coffee.polynomial import (
    COFFEE_POLYNOMIAL,
    coffee_directions,
    coffee_transition,
)
from services.liminal.coffee.types import (
    CoffeeOutput,
    CoffeeState,
    RitualEvent,
)

# =============================================================================
# Direction Function Tests
# =============================================================================


class TestCoffeeDirections:
    """Tests for coffee_directions function."""

    def test_dormant_directions(self) -> None:
        """DORMANT can wake or force_start."""
        dirs = coffee_directions(CoffeeState.DORMANT)
        assert "wake" in dirs
        assert "force_start" in dirs
        assert "exit" in dirs
        assert "manifest" in dirs

    def test_garden_directions(self) -> None:
        """GARDEN can continue, skip, or exit."""
        dirs = coffee_directions(CoffeeState.GARDEN)
        assert "continue" in dirs
        assert "skip_to_menu" in dirs
        assert "skip" in dirs
        assert "exit" in dirs

    def test_weather_directions(self) -> None:
        """WEATHER can continue, skip, or exit."""
        dirs = coffee_directions(CoffeeState.WEATHER)
        assert "continue" in dirs
        assert "skip_to_menu" in dirs
        assert "exit" in dirs

    def test_menu_directions(self) -> None:
        """MENU can select, go serendipitous, or exit."""
        dirs = coffee_directions(CoffeeState.MENU)
        assert "select" in dirs
        assert "serendipity" in dirs
        assert "exit" in dirs

    def test_capture_directions(self) -> None:
        """CAPTURE can record, skip, or exit."""
        dirs = coffee_directions(CoffeeState.CAPTURE)
        assert "record" in dirs
        assert "skip" in dirs
        assert "exit" in dirs

    def test_transition_directions(self) -> None:
        """TRANSITION can begin work, linger, or exit."""
        dirs = coffee_directions(CoffeeState.TRANSITION)
        assert "begin_work" in dirs
        assert "linger" in dirs
        assert "exit" in dirs

    def test_exit_always_valid(self) -> None:
        """Law 5: exit should be valid in every state."""
        for state in CoffeeState:
            dirs = coffee_directions(state)
            assert "exit" in dirs, f"exit not valid in {state.name}"

    def test_manifest_always_valid(self) -> None:
        """manifest should be valid in every state."""
        for state in CoffeeState:
            dirs = coffee_directions(state)
            assert "manifest" in dirs, f"manifest not valid in {state.name}"


# =============================================================================
# Happy Path Tests
# =============================================================================


class TestHappyPath:
    """Tests for the standard ritual flow."""

    def test_wake_from_dormant(self) -> None:
        """wake transitions DORMANT → GARDEN."""
        state, output = coffee_transition(CoffeeState.DORMANT, "wake")
        assert state == CoffeeState.GARDEN
        assert output.status == "ok"
        assert output.movement is not None
        assert output.movement.name == "Garden View"

    def test_continue_garden_to_weather(self) -> None:
        """continue transitions GARDEN → WEATHER."""
        state, output = coffee_transition(CoffeeState.GARDEN, "continue")
        assert state == CoffeeState.WEATHER
        assert output.status == "ok"
        assert "weather" in output.message.lower() or "shifting" in output.message.lower()

    def test_continue_weather_to_menu(self) -> None:
        """continue transitions WEATHER → MENU."""
        state, output = coffee_transition(CoffeeState.WEATHER, "continue")
        assert state == CoffeeState.MENU
        assert output.status == "ok"

    def test_select_menu_to_capture(self) -> None:
        """select transitions MENU → CAPTURE."""
        state, output = coffee_transition(
            CoffeeState.MENU,
            {"command": "select", "selection": "focused"},
        )
        assert state == CoffeeState.CAPTURE
        assert output.status == "ok"
        assert output.data.get("selection") == "focused"

    def test_serendipity_menu_to_capture(self) -> None:
        """serendipity transitions MENU → CAPTURE."""
        state, output = coffee_transition(CoffeeState.MENU, "serendipity")
        assert state == CoffeeState.CAPTURE
        assert output.status == "ok"
        assert output.data.get("selection") == "serendipitous"

    def test_record_capture_to_transition(self) -> None:
        """record transitions CAPTURE → TRANSITION."""
        voice_data = {
            "command": "record",
            "voice": {
                "captured_date": "2025-12-21",
                "success_criteria": "Ship it",
            },
        }
        state, output = coffee_transition(CoffeeState.CAPTURE, voice_data)
        assert state == CoffeeState.TRANSITION
        assert output.status == "ok"
        assert output.voice is not None
        assert output.voice.success_criteria == "Ship it"

    def test_begin_work_completes_ritual(self) -> None:
        """begin_work transitions TRANSITION → DORMANT (complete)."""
        state, output = coffee_transition(CoffeeState.TRANSITION, "begin_work")
        assert state == CoffeeState.DORMANT
        assert output.status == "ok"
        assert "begin" in output.message.lower()


# =============================================================================
# Exit Tests (Law 5: Exit Honored)
# =============================================================================


class TestExitHonored:
    """Law 5: Exit should be honored from any state."""

    @pytest.mark.parametrize(
        "start_state",
        [
            CoffeeState.DORMANT,
            CoffeeState.GARDEN,
            CoffeeState.WEATHER,
            CoffeeState.MENU,
            CoffeeState.CAPTURE,
            CoffeeState.TRANSITION,
        ],
    )
    def test_exit_from_any_state(self, start_state: CoffeeState) -> None:
        """exit transitions any state → DORMANT."""
        state, output = coffee_transition(start_state, "exit")
        assert state == CoffeeState.DORMANT
        assert output.status == "exited"
        assert "guilt" in output.message.lower() or "nagging" in output.message.lower()


# =============================================================================
# Skip Tests (Law 1: Skippable Movements)
# =============================================================================


class TestSkippableMovements:
    """Law 1: Every movement should be skippable."""

    def test_skip_from_garden(self) -> None:
        """skip in GARDEN → TRANSITION (inspiration struck)."""
        state, output = coffee_transition(CoffeeState.GARDEN, "skip")
        assert state == CoffeeState.TRANSITION
        assert output.status == "skipped"

    def test_skip_to_menu_from_garden(self) -> None:
        """skip_to_menu in GARDEN → MENU."""
        state, output = coffee_transition(CoffeeState.GARDEN, "skip_to_menu")
        assert state == CoffeeState.MENU
        assert output.status == "skipped"

    def test_skip_from_weather(self) -> None:
        """skip in WEATHER → MENU."""
        state, output = coffee_transition(CoffeeState.WEATHER, "skip")
        assert state == CoffeeState.MENU
        assert output.status == "skipped"

    def test_skip_from_menu(self) -> None:
        """skip in MENU → TRANSITION."""
        state, output = coffee_transition(CoffeeState.MENU, "skip")
        assert state == CoffeeState.TRANSITION
        assert output.status == "skipped"

    def test_skip_from_capture(self) -> None:
        """skip in CAPTURE → TRANSITION (no voice recorded)."""
        state, output = coffee_transition(CoffeeState.CAPTURE, "skip")
        assert state == CoffeeState.TRANSITION
        assert output.status == "skipped"
        assert output.voice is None


# =============================================================================
# Manifest Tests
# =============================================================================


class TestManifest:
    """Tests for manifest command (view current state)."""

    @pytest.mark.parametrize(
        "state",
        [
            CoffeeState.DORMANT,
            CoffeeState.GARDEN,
            CoffeeState.WEATHER,
            CoffeeState.MENU,
            CoffeeState.CAPTURE,
            CoffeeState.TRANSITION,
        ],
    )
    def test_manifest_stays_in_same_state(self, state: CoffeeState) -> None:
        """manifest should not change state."""
        new_state, output = coffee_transition(state, "manifest")
        assert new_state == state
        assert output.status == "ok"
        assert state.name in output.message


# =============================================================================
# Input Format Tests
# =============================================================================


class TestInputFormats:
    """Tests for various input formats."""

    def test_string_command(self) -> None:
        """Simple string command should work."""
        state, output = coffee_transition(CoffeeState.DORMANT, "wake")
        assert state == CoffeeState.GARDEN

    def test_dict_command(self) -> None:
        """Dict with command key should work."""
        state, output = coffee_transition(
            CoffeeState.DORMANT,
            {"command": "wake"},
        )
        assert state == CoffeeState.GARDEN

    def test_dict_cmd_key(self) -> None:
        """Dict with cmd key should work."""
        state, output = coffee_transition(
            CoffeeState.DORMANT,
            {"cmd": "wake"},
        )
        assert state == CoffeeState.GARDEN

    def test_ritual_event(self) -> None:
        """RitualEvent should work."""
        event = RitualEvent(command="wake")
        state, output = coffee_transition(CoffeeState.DORMANT, event)
        assert state == CoffeeState.GARDEN

    def test_dict_with_data(self) -> None:
        """Dict with command and data should extract both."""
        state, output = coffee_transition(
            CoffeeState.MENU,
            {"command": "select", "selection": "intense"},
        )
        assert state == CoffeeState.CAPTURE
        assert output.data.get("selection") == "intense"


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error cases."""

    def test_unknown_command_returns_error(self) -> None:
        """Unknown command should return error status."""
        state, output = coffee_transition(CoffeeState.GARDEN, "invalid_command")
        assert state == CoffeeState.GARDEN  # Stay in same state
        assert output.status == "error"
        assert "unknown" in output.message.lower()

    def test_invalid_dormant_command(self) -> None:
        """Invalid command in DORMANT returns error."""
        state, output = coffee_transition(CoffeeState.DORMANT, "continue")
        assert state == CoffeeState.DORMANT
        assert output.status == "error"


# =============================================================================
# Polynomial Agent Tests
# =============================================================================


class TestCoffeePolynomial:
    """Tests for the COFFEE_POLYNOMIAL agent."""

    def test_polynomial_has_name(self) -> None:
        """Polynomial should have a name."""
        assert COFFEE_POLYNOMIAL.name == "CoffeePolynomial"

    def test_polynomial_has_all_positions(self) -> None:
        """Polynomial should have all 6 states as positions."""
        positions = COFFEE_POLYNOMIAL.positions
        assert len(positions) == 6
        for state in CoffeeState:
            assert state in positions

    def test_polynomial_transition(self) -> None:
        """Polynomial transition should work."""
        state, output = COFFEE_POLYNOMIAL.transition(CoffeeState.DORMANT, "wake")
        assert state == CoffeeState.GARDEN
        assert isinstance(output, CoffeeOutput)

    def test_polynomial_invoke(self) -> None:
        """Polynomial invoke (sync) should work."""
        state, output = COFFEE_POLYNOMIAL.invoke(CoffeeState.DORMANT, "wake")
        assert state == CoffeeState.GARDEN


# =============================================================================
# Full Ritual Flow Test
# =============================================================================


class TestFullRitualFlow:
    """Integration test for complete ritual flow."""

    def test_complete_ritual(self) -> None:
        """Test the complete happy path through the ritual."""
        state = CoffeeState.DORMANT

        # Wake up
        state, output = coffee_transition(state, "wake")
        assert state == CoffeeState.GARDEN
        assert output.movement is not None

        # View garden, continue
        state, output = coffee_transition(state, "continue")
        assert state == CoffeeState.WEATHER

        # View weather, continue
        state, output = coffee_transition(state, "continue")
        assert state == CoffeeState.MENU

        # Select challenge
        state, output = coffee_transition(
            state,
            {"command": "select", "selection": "focused"},
        )
        assert state == CoffeeState.CAPTURE

        # Record voice
        state, output = coffee_transition(
            state,
            {
                "command": "record",
                "voice": {
                    "captured_date": "2025-12-21",
                    "success_criteria": "Ship one feature",
                },
            },
        )
        assert state == CoffeeState.TRANSITION
        assert output.voice is not None

        # Begin work
        state, output = coffee_transition(state, "begin_work")
        assert state == CoffeeState.DORMANT
        assert "begin" in output.message.lower()

    def test_short_circuit_with_skip(self) -> None:
        """Test skipping directly to work from garden."""
        state = CoffeeState.DORMANT

        # Wake up
        state, _ = coffee_transition(state, "wake")
        assert state == CoffeeState.GARDEN

        # Skip everything
        state, output = coffee_transition(state, "skip")
        assert state == CoffeeState.TRANSITION
        assert output.status == "skipped"

        # Begin work
        state, _ = coffee_transition(state, "begin_work")
        assert state == CoffeeState.DORMANT

    def test_linger_in_transition(self) -> None:
        """Test lingering before beginning work."""
        state = CoffeeState.TRANSITION

        # Linger
        state, output = coffee_transition(state, "linger")
        assert state == CoffeeState.TRANSITION
        assert output.status == "ok"
        assert "moment" in output.message.lower()

        # Can still begin work
        state, _ = coffee_transition(state, "begin_work")
        assert state == CoffeeState.DORMANT
