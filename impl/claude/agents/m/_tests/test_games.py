"""
Tests for Wittgensteinian language games.

Verifies that memory access can be modeled as playing games,
with grammatical rules determining valid moves.
"""

from __future__ import annotations

import pytest
from agents.m.games import (
    ComposedGame,
    Direction,
    LanguageGame,
    Move,
    PolynomialPosition,
    create_associative_game,
    create_dialectical_game,
    create_episodic_game,
    create_navigation_game,
    create_recall_game,
    game_to_polynomial,
    polynomial_signature,
)


class TestMove:
    """Tests for Move dataclass."""

    def test_move_creation(self) -> None:
        """Move is created with correct fields."""
        move: Move[str] = Move(
            from_position="start",
            direction="elaborate",
            to_position="start:detailed",
            is_grammatical=True,
        )

        assert move.from_position == "start"
        assert move.direction == "elaborate"
        assert move.to_position == "start:detailed"
        assert move.is_grammatical is True

    def test_move_with_metadata(self) -> None:
        """Move can carry metadata."""
        move: Move[str] = Move(
            from_position="start",
            direction="elaborate",
            to_position="start:detailed",
            is_grammatical=True,
            metadata={"confidence": 0.9},
        )

        assert move.metadata["confidence"] == 0.9


class TestLanguageGame:
    """Tests for LanguageGame base class."""

    def test_empty_game_creation(self) -> None:
        """Can create empty game."""
        game: LanguageGame[str] = LanguageGame(name="test")

        assert game.name == "test"
        assert game.positions == set()

    def test_add_position(self) -> None:
        """Can add positions to game."""
        game: LanguageGame[str] = LanguageGame(name="test")

        game.add_position("position_a")
        game.add_position("position_b")

        assert "position_a" in game.positions
        assert "position_b" in game.positions

    def test_custom_directions(self) -> None:
        """Custom directions function works."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"up", "down", "left", "right"},
        )

        dirs = game.directions("any_position")

        assert dirs == {"up", "down", "left", "right"}

    def test_is_grammatical_default(self) -> None:
        """Default rules check direction membership."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"valid_move"},
        )

        assert game.is_grammatical("pos", "valid_move") is True
        assert game.is_grammatical("pos", "invalid_move") is False

    def test_is_grammatical_custom_rules(self) -> None:
        """Custom rules can restrict moves."""
        # Only allow "go" direction at positions starting with "a"
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"go"},
            rules=lambda s, d: s.startswith("a"),
        )

        assert game.is_grammatical("abc", "go") is True
        assert game.is_grammatical("xyz", "go") is False

    def test_apply_grammatical_move(self) -> None:
        """Apply executes grammatical moves."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"transform"},
            transitions=lambda s, d: f"{s}:transformed",
        )

        result = game.apply("start", "transform")

        assert result == "start:transformed"

    def test_apply_ungrammatical_raises(self) -> None:
        """Apply raises on ungrammatical moves."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: set(),  # No directions allowed
        )

        with pytest.raises(ValueError, match="Ungrammatical"):
            game.apply("start", "anything")

    def test_play_grammatical(self) -> None:
        """Play returns Move for grammatical moves."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"go"},
            transitions=lambda s, d: f"{s}:went",
        )

        move = game.play("start", "go")

        assert move.is_grammatical is True
        assert move.from_position == "start"
        assert move.to_position == "start:went"

    def test_play_ungrammatical(self) -> None:
        """Play returns Move with is_grammatical=False."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: set(),
        )

        move = game.play("start", "invalid")

        assert move.is_grammatical is False
        assert move.from_position == "start"
        assert move.to_position == "start"  # No change

    def test_trace_records_moves(self) -> None:
        """Trace records sequence of moves."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"a", "b"},
            transitions=lambda s, d: f"{s}:{d}",
        )

        moves = game.trace("start", ["a", "b", "a"])

        assert len(moves) == 3
        assert all(m.is_grammatical for m in moves)
        assert moves[-1].to_position == "start:a:b:a"

    def test_trace_stops_on_ungrammatical(self) -> None:
        """Trace continues but marks ungrammatical moves."""
        game: LanguageGame[str] = LanguageGame(
            name="test",
            directions=lambda s: {"valid"},
            transitions=lambda s, d: f"{s}:{d}",
        )

        moves = game.trace("start", ["valid", "invalid", "valid"])

        assert len(moves) == 3
        assert moves[0].is_grammatical is True
        assert moves[1].is_grammatical is False
        assert moves[2].is_grammatical is True  # Can continue after failure


class TestRecallGame:
    """Tests for the recall game."""

    def test_recall_game_directions(self) -> None:
        """Recall game has expected directions."""
        game = create_recall_game()

        dirs = game.directions("any_concept")

        assert "elaborate" in dirs
        assert "compress" in dirs
        assert "associate" in dirs
        assert "forget" in dirs
        assert "witness" in dirs

    def test_elaborate_transition(self) -> None:
        """Elaborate adds :detailed suffix."""
        game = create_recall_game()

        result = game.apply("memory", "elaborate")

        assert result == "memory:detailed"

    def test_compress_transition(self) -> None:
        """Compress adds :summary suffix."""
        game = create_recall_game()

        result = game.apply("memory", "compress")

        assert result == "memory:summary"

    def test_associate_transition(self) -> None:
        """Associate adds :linked suffix."""
        game = create_recall_game()

        result = game.apply("memory", "associate")

        assert result == "memory:linked"

    def test_forget_transition(self) -> None:
        """Forget adds :fading suffix."""
        game = create_recall_game()

        result = game.apply("memory", "forget")

        assert result == "memory:fading"


class TestNavigationGame:
    """Tests for the navigation game."""

    def test_navigation_game_directions(self) -> None:
        """Navigation game has cardinal and zoom directions."""
        game = create_navigation_game()

        dirs = game.directions(("concept", "context"))

        assert "north" in dirs
        assert "south" in dirs
        assert "zoom_in" in dirs
        assert "zoom_out" in dirs

    def test_zoom_in_transition(self) -> None:
        """Zoom in focuses on concept detail."""
        game = create_navigation_game()

        result = game.apply(("concept", "context"), "zoom_in")

        assert result == ("concept:detail", "context")

    def test_zoom_out_transition(self) -> None:
        """Zoom out broadens context."""
        game = create_navigation_game()

        result = game.apply(("concept", "context"), "zoom_out")

        assert result == ("concept:context", "context")

    def test_cardinal_transition(self) -> None:
        """Cardinal directions change context."""
        game = create_navigation_game()

        result = game.apply(("concept", "context"), "north")

        assert result == ("concept", "context:north")


class TestDialecticalGame:
    """Tests for the dialectical game."""

    def test_dialectical_directions_initial(self) -> None:
        """Initial state can challenge, defend, abandon."""
        game = create_dialectical_game()

        dirs = game.directions("thesis")

        assert "challenge" in dirs
        assert "defend" in dirs
        assert "abandon" in dirs
        assert "synthesize" not in dirs  # Not yet available

    def test_dialectical_directions_after_challenge(self) -> None:
        """After challenge, synthesize becomes available."""
        game = create_dialectical_game()

        result = game.apply("thesis", "challenge")
        dirs = game.directions(result)

        assert "synthesize" in dirs

    def test_synthesize_removes_tension(self) -> None:
        """Synthesize removes tension markers."""
        game = create_dialectical_game()

        challenged = game.apply("thesis", "challenge")
        synthesized = game.apply(challenged, "synthesize")

        assert ":challenged" not in synthesized
        assert ":synthesized" in synthesized

    def test_cant_abandon_after_synthesis(self) -> None:
        """Cannot abandon after synthesis."""
        game = create_dialectical_game()

        challenged = game.apply("thesis", "challenge")
        synthesized = game.apply(challenged, "synthesize")

        assert game.is_grammatical(synthesized, "abandon") is False


class TestAssociativeGame:
    """Tests for the associative game."""

    def test_associative_directions(self) -> None:
        """Associative game has activation directions."""
        game = create_associative_game()

        dirs = game.directions("concept")

        assert "activate" in dirs
        assert "inhibit" in dirs
        assert "prime" in dirs
        assert "decay" in dirs

    def test_activate_transition(self) -> None:
        """Activate adds :active marker."""
        game = create_associative_game()

        result = game.apply("concept", "activate")

        assert result == "concept:active"

    def test_inhibit_transition(self) -> None:
        """Inhibit adds :inhibited marker."""
        game = create_associative_game()

        result = game.apply("concept", "inhibit")

        assert result == "concept:inhibited"


class TestEpisodicGame:
    """Tests for the episodic game."""

    def test_episodic_directions(self) -> None:
        """Episodic game has reconstruction directions."""
        game = create_episodic_game()

        dirs = game.directions(("event", "place", "time"))

        assert "contextualize" in dirs
        assert "temporalize" in dirs
        assert "spatialize" in dirs
        assert "personalize" in dirs

    def test_contextualize_transition(self) -> None:
        """Contextualize enriches event."""
        game = create_episodic_game()

        result = game.apply(("event", "place", "time"), "contextualize")

        assert result == ("event:contextual", "place", "time")

    def test_temporalize_transition(self) -> None:
        """Temporalize navigates in time."""
        game = create_episodic_game()

        result = game.apply(("event", "place", "time"), "temporalize")

        assert result == ("event", "place", "time:navigated")

    def test_spatialize_transition(self) -> None:
        """Spatialize navigates in space."""
        game = create_episodic_game()

        result = game.apply(("event", "place", "time"), "spatialize")

        assert result == ("event", "place:navigated", "time")


class TestComposedGame:
    """Tests for ComposedGame."""

    def test_composed_game_creation(self) -> None:
        """Can create composed game from multiple games."""
        recall = create_recall_game()
        assoc = create_associative_game()

        composed: ComposedGame[str] = ComposedGame([recall, assoc])

        assert composed._games["recall"] is recall
        assert composed._games["associative"] is assoc

    def test_directions_from_all_games(self) -> None:
        """Can get directions from all games."""
        recall = create_recall_game()
        assoc = create_associative_game()

        composed = ComposedGame([recall, assoc])
        all_dirs = composed.directions("concept")

        assert "recall" in all_dirs
        assert "associative" in all_dirs
        assert "elaborate" in all_dirs["recall"]
        assert "activate" in all_dirs["associative"]

    def test_play_in_specific_game(self) -> None:
        """Can play in specific game."""
        recall = create_recall_game()
        assoc = create_associative_game()

        composed = ComposedGame([recall, assoc])

        move = composed.play_in("recall", "concept", "elaborate")

        assert move is not None
        assert move.is_grammatical is True
        assert move.to_position == "concept:detailed"

    def test_play_in_unknown_game(self) -> None:
        """Playing in unknown game returns None."""
        recall = create_recall_game()

        composed = ComposedGame([recall])

        move = composed.play_in("unknown", "concept", "anything")

        assert move is None


class TestPolynomialFunctor:
    """Tests for polynomial functor interpretation."""

    def test_polynomial_position(self) -> None:
        """PolynomialPosition captures state and directions."""
        pp: PolynomialPosition[str] = PolynomialPosition(
            position="state",
            directions={"a", "b", "c"},
        )

        term = pp.as_polynomial_term()

        assert term == ("state", 3)

    def test_game_to_polynomial(self) -> None:
        """Can convert game to polynomial representation."""
        game = create_recall_game()
        positions = ["concept_a", "concept_b"]

        poly = game_to_polynomial(game, positions)

        assert len(poly) == 2
        # Recall game has 5 directions from any state
        assert poly[0].directions == {
            "elaborate",
            "compress",
            "associate",
            "forget",
            "witness",
        }

    def test_polynomial_signature(self) -> None:
        """Polynomial signature shows direction distribution."""
        game = create_recall_game()
        positions = ["a", "b", "c"]

        sig = polynomial_signature(game, positions)

        # All positions have same number of directions (5)
        assert sig == {5: 3}

    def test_polynomial_signature_varied(self) -> None:
        """Signature captures varied direction counts."""

        # Create game where different positions have different direction counts
        def varying_directions(s: str) -> set[str]:
            if s == "narrow":
                return {"a"}
            elif s == "medium":
                return {"a", "b", "c"}
            else:
                return {"a", "b", "c", "d", "e"}

        game: LanguageGame[str] = LanguageGame(
            name="varied",
            directions=varying_directions,
        )

        sig = polynomial_signature(game, ["narrow", "medium", "wide"])

        assert sig == {1: 1, 3: 1, 5: 1}


class TestDirectionEnum:
    """Tests for standard Direction enum."""

    def test_direction_enum_values(self) -> None:
        """Direction enum has expected values."""
        assert Direction.ELABORATE is not None
        assert Direction.COMPRESS is not None
        assert Direction.ASSOCIATE is not None
        assert Direction.FORGET is not None
        assert Direction.WITNESS is not None
        assert Direction.REFINE is not None
        assert Direction.MANIFEST is not None
        assert Direction.NAVIGATE is not None


class TestGrammarChecking:
    """Tests for grammar (rule) checking."""

    def test_grammar_with_state_dependent_rules(self) -> None:
        """Rules can depend on current state."""

        # Can only "unlock" from locked state
        def rules(state: str, direction: str) -> bool:
            if direction == "unlock" and state != "locked":
                return False
            return True

        game: LanguageGame[str] = LanguageGame(
            name="lock",
            directions=lambda s: {"unlock", "lock"},
            rules=rules,
        )

        assert game.is_grammatical("locked", "unlock") is True
        assert game.is_grammatical("unlocked", "unlock") is False
        assert game.is_grammatical("unlocked", "lock") is True

    def test_grammar_with_history_encoding(self) -> None:
        """State can encode history for grammar checking."""

        # Can't go "back" without first going "forward"
        def rules(state: str, direction: str) -> bool:
            if direction == "back" and ":forward" not in state:
                return False
            return True

        game: LanguageGame[str] = LanguageGame(
            name="history",
            directions=lambda s: {"forward", "back"},
            rules=rules,
            transitions=lambda s, d: f"{s}:{d}",
        )

        assert game.is_grammatical("start", "back") is False
        assert game.is_grammatical("start", "forward") is True

        moved = game.apply("start", "forward")
        assert game.is_grammatical(moved, "back") is True


class TestMeaningAsUse:
    """Tests demonstrating the Wittgensteinian principle: meaning is use."""

    def test_same_concept_different_games(self) -> None:
        """Same concept has different affordances in different games."""
        recall = create_recall_game()
        dialectical = create_dialectical_game()

        concept = "thesis"

        # In recall game: can elaborate, compress, etc.
        recall_dirs = recall.directions(concept)
        assert "elaborate" in recall_dirs

        # In dialectical game: can challenge, defend, etc.
        dialectical_dirs = dialectical.directions(concept)
        assert "challenge" in dialectical_dirs

        # The "meaning" (affordances) of the same concept differs by game

    def test_state_transformation_creates_meaning(self) -> None:
        """Transitions create meaning through state transformation."""
        game = create_recall_game()

        # Start with raw concept
        concept = "memory"

        # Each move creates a new meaning
        elaborated = game.apply(concept, "elaborate")
        compressed = game.apply(concept, "compress")

        assert elaborated != compressed
        # The meaning is the transformation, not the label
