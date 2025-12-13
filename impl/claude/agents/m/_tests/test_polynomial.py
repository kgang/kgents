"""
Tests for Memory as Polynomial Agent.

The polynomial functor P(y) = Σₛ y^{D(s)} captures state-dependent behavior.
"""

from __future__ import annotations

import pytest
from agents.m.crystal import MemoryCrystal
from agents.m.games import LanguageGame, create_dialectical_game, create_recall_game
from agents.m.polynomial import (
    MemoryDirection,
    MemoryMode,
    MemoryOutput,
    MemoryPolynomial,
    MemoryState,
    create_memory_polynomial,
    game_to_polynomial,
)

# ========== Fixtures ==========


@pytest.fixture
def crystal() -> MemoryCrystal[str]:
    """Create a test crystal with some concepts."""
    c: MemoryCrystal[str] = MemoryCrystal(dimension=64)
    c.store("python", "Python programming tips", [0.9] * 64)
    c.store("rust", "Rust memory safety", [0.8] * 64)
    c.store("javascript", "JavaScript async patterns", [0.6] * 64)
    return c


@pytest.fixture
def games() -> dict[str, LanguageGame[str]]:
    """Create test games."""
    return {
        "recall": create_recall_game(),
        "dialectical": create_dialectical_game(),
    }


@pytest.fixture
def polynomial(
    crystal: MemoryCrystal[str], games: dict[str, LanguageGame[str]]
) -> MemoryPolynomial[str]:
    """Create a test polynomial."""
    return MemoryPolynomial(crystal=crystal, games=games)


# ========== MemoryState Tests ==========


class TestMemoryState:
    """Tests for MemoryState."""

    def test_state_creation(self) -> None:
        """Test basic state creation."""
        state = MemoryState()
        assert state.mode == MemoryMode.IDLE
        assert state.focus is None
        assert state.game == "recall"

    def test_state_hashable(self) -> None:
        """Test that states are hashable."""
        state1 = MemoryState(mode=MemoryMode.IDLE)
        state2 = MemoryState(mode=MemoryMode.IDLE)

        # Should be equal
        assert state1 == state2

        # Should be hashable (can use in sets)
        states = {state1, state2}
        assert len(states) == 1

    def test_state_equality(self) -> None:
        """Test state equality based on key fields."""
        state1 = MemoryState(mode=MemoryMode.FOCUSED, focus="python")
        state2 = MemoryState(mode=MemoryMode.FOCUSED, focus="python")
        state3 = MemoryState(mode=MemoryMode.FOCUSED, focus="rust")

        assert state1 == state2
        assert state1 != state3


# ========== MemoryDirection Tests ==========


class TestMemoryDirection:
    """Tests for MemoryDirection."""

    def test_direction_creation(self) -> None:
        """Test basic direction creation."""
        d = MemoryDirection("focus", "python")
        assert d.action == "focus"
        assert d.target == "python"

    def test_direction_without_target(self) -> None:
        """Test direction without target."""
        d = MemoryDirection("unfocus")
        assert d.action == "unfocus"
        assert d.target is None

    def test_direction_hashable(self) -> None:
        """Test directions are hashable."""
        d1 = MemoryDirection("focus", "python")
        d2 = MemoryDirection("focus", "python")

        assert d1 == d2
        dirs = {d1, d2}
        assert len(dirs) == 1


# ========== MemoryPolynomial Tests ==========


class TestMemoryPolynomial:
    """Tests for MemoryPolynomial."""

    def test_polynomial_creation(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test polynomial creation."""
        assert polynomial.name == "MemoryPolynomial"
        assert polynomial.crystal is not None
        assert len(polynomial.games) == 2

    def test_positions(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test positions returns valid states."""
        positions = polynomial.positions

        # Should have at least idle and focused states
        assert len(positions) > 0

        # Should have idle state
        idle_states = [p for p in positions if p.mode == MemoryMode.IDLE]
        assert len(idle_states) >= 1

    def test_directions_idle(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test directions from idle state."""
        state = MemoryState(mode=MemoryMode.IDLE)
        directions = polynomial.directions(state)

        # Should be able to focus on concepts
        focus_dirs = [d for d in directions if d.action == "focus"]
        assert len(focus_dirs) == 3  # python, rust, javascript

        # Should be able to explore
        assert MemoryDirection("explore") in directions

        # Should be able to switch games
        switch_dirs = [d for d in directions if d.action == "switch_game"]
        assert len(switch_dirs) == 2

    def test_directions_focused(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test directions from focused state."""
        state = MemoryState(
            mode=MemoryMode.FOCUSED,
            focus="python",
            game="recall",
            position="python",
        )
        directions = polynomial.directions(state)

        # Should be able to unfocus
        assert MemoryDirection("unfocus") in directions

        # Should have game moves
        game = polynomial.games["recall"]
        game_dirs = game.directions("python")
        for d in game_dirs:
            assert MemoryDirection(d) in directions

    def test_transition_focus(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test focus transition."""
        state = MemoryState(mode=MemoryMode.IDLE)
        direction = MemoryDirection("focus", "python")

        new_state, output = polynomial.transition(state, direction)

        assert new_state.mode == MemoryMode.FOCUSED
        assert new_state.focus == "python"
        assert new_state.position == "python"
        assert output.grammatical
        assert output.content is not None
        assert "Python" in output.content

    def test_transition_unfocus(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test unfocus transition."""
        state = MemoryState(
            mode=MemoryMode.FOCUSED,
            focus="python",
            position="python",
        )
        direction = MemoryDirection("unfocus")

        new_state, output = polynomial.transition(state, direction)

        assert new_state.mode == MemoryMode.IDLE
        assert new_state.focus is None
        assert output.grammatical

    def test_transition_switch_game(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test game switching."""
        state = MemoryState(
            mode=MemoryMode.FOCUSED,
            focus="python",
            game="recall",
            position="python",
        )
        direction = MemoryDirection("switch_game", "dialectical")

        new_state, output = polynomial.transition(state, direction)

        assert new_state.game == "dialectical"
        assert new_state.focus == "python"
        assert output.grammatical

    def test_transition_game_move(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test game move transition."""
        state = MemoryState(
            mode=MemoryMode.FOCUSED,
            focus="python",
            game="recall",
            position="python",
        )
        # Get a valid direction from the game
        game = polynomial.games["recall"]
        directions = game.directions("python")
        if directions:
            move_action = next(iter(directions))
            direction = MemoryDirection(move_action)

            new_state, output = polynomial.transition(state, direction)

            assert output.grammatical
            assert new_state.position != state.position or move_action in ["compress"]

    def test_transition_explore(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test explore transition."""
        state = MemoryState(mode=MemoryMode.IDLE)
        direction = MemoryDirection("explore")

        new_state, output = polynomial.transition(state, direction)

        assert new_state.mode == MemoryMode.EXPLORING
        assert output.grammatical

    def test_transition_invalid_focus(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test invalid focus transition."""
        state = MemoryState(mode=MemoryMode.IDLE)
        direction = MemoryDirection("focus", "nonexistent")

        new_state, output = polynomial.transition(state, direction)

        # Should return unmodified state with grammatical=False
        assert new_state.mode == MemoryMode.IDLE
        assert not output.grammatical

    def test_invoke_validates(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test invoke validates directions."""
        state = MemoryState(mode=MemoryMode.IDLE)

        # Invalid direction for idle state
        invalid_dir = MemoryDirection("unfocus")  # Can't unfocus when not focused

        with pytest.raises(ValueError):
            polynomial.invoke(state, invalid_dir)

    def test_run_sequence(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test running a sequence of transitions."""
        initial = MemoryState(mode=MemoryMode.IDLE)
        sequence = [
            MemoryDirection("focus", "python"),
            MemoryDirection("unfocus"),
            MemoryDirection("focus", "rust"),
        ]

        final_state, outputs = polynomial.run(initial, sequence)

        assert len(outputs) == 3
        assert final_state.mode == MemoryMode.FOCUSED
        assert final_state.focus == "rust"

    def test_history_tracking(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test that history is tracked."""
        initial = MemoryState(mode=MemoryMode.IDLE)
        sequence = [
            MemoryDirection("focus", "python"),
            MemoryDirection("unfocus"),
        ]

        final_state, _ = polynomial.run(initial, sequence)

        assert len(final_state.history) == 2
        assert "focus:python" in final_state.history[0]

    def test_initial_state(self, polynomial: MemoryPolynomial[str]) -> None:
        """Test initial state getter."""
        initial = polynomial.initial_state()
        assert initial.mode == MemoryMode.IDLE


# ========== Factory Function Tests ==========


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_memory_polynomial(self, crystal: MemoryCrystal[str]) -> None:
        """Test creating polynomial with defaults."""
        poly = create_memory_polynomial(crystal, include_default_games=True)

        assert poly.crystal is crystal
        assert len(poly.games) > 0
        assert "recall" in poly.games

    def test_create_memory_polynomial_no_games(
        self, crystal: MemoryCrystal[str]
    ) -> None:
        """Test creating polynomial without default games."""
        poly = create_memory_polynomial(crystal, include_default_games=False)

        assert poly.crystal is crystal
        assert len(poly.games) == 0


class TestGameToPolynomial:
    """Tests for game_to_polynomial."""

    def test_recall_game_polynomial(self) -> None:
        """Test extracting polynomial from recall game."""
        game = create_recall_game()
        sig = game_to_polynomial(game, ["start", "a", "b"])

        assert "positions" in sig
        assert "signature" in sig
        assert "total_directions" in sig

        # All positions should have directions
        for count in sig["signature"].values():
            assert count > 0

    def test_dialectical_game_polynomial(self) -> None:
        """Test extracting polynomial from dialectical game."""
        game = create_dialectical_game()
        sig = game_to_polynomial(game, ["thesis"])

        assert len(sig["positions"]) > 0
        assert sig["total_directions"] > 0


# ========== Integration Tests ==========


class TestPolynomialIntegration:
    """Integration tests for polynomial with other pillars."""

    def test_polynomial_with_inference(
        self, crystal: MemoryCrystal[str], games: dict[str, LanguageGame[str]]
    ) -> None:
        """Test polynomial with inference agent."""
        from agents.m.inference import ActiveInferenceAgent, Belief

        belief = Belief(distribution={"python": 0.5, "rust": 0.3, "javascript": 0.2})
        inference: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        poly = MemoryPolynomial(crystal=crystal, games=games, inference=inference)

        # Should have evaluate direction when focused
        state = MemoryState(
            mode=MemoryMode.FOCUSED,
            focus="python",
            game="recall",
            position="python",
        )
        directions = poly.directions(state)

        assert MemoryDirection("evaluate") in directions

    def test_full_workflow(
        self, crystal: MemoryCrystal[str], games: dict[str, LanguageGame[str]]
    ) -> None:
        """Test complete workflow through polynomial."""
        poly = MemoryPolynomial(crystal=crystal, games=games)

        # Start idle
        state = poly.initial_state()
        assert state.mode == MemoryMode.IDLE

        # Focus on python
        state, out = poly.transition(state, MemoryDirection("focus", "python"))
        assert state.mode == MemoryMode.FOCUSED
        assert state.focus == "python"
        assert out.content is not None

        # Switch to dialectical game
        state, out = poly.transition(
            state, MemoryDirection("switch_game", "dialectical")
        )
        assert state.game == "dialectical"

        # Play a game move
        dirs = poly.directions(state)
        game_moves = [
            d for d in dirs if d.action not in ["unfocus", "switch_game", "evaluate"]
        ]
        if game_moves:
            state, out = poly.transition(state, game_moves[0])
            assert out.grammatical

        # Return to idle
        state, out = poly.transition(state, MemoryDirection("unfocus"))
        assert state.mode == MemoryMode.IDLE
