"""
Tests for Town CLI Handler.

Verifies:
- TownSession dataclass
- whisper, inhabit, intervene commands
- User mode state management
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from agents.town.environment import create_mpp_environment
from agents.town.flux import TownFlux
from protocols.cli.handlers.town import (
    TownSession,
    _inhabit_citizen,
    _intervene_event,
    _simulation_state,
    _whisper_citizen,
    cmd_town,
)


class TestTownSession:
    """Test TownSession dataclass."""

    def test_default_mode(self) -> None:
        """Default mode is observe."""
        session = TownSession()
        assert session.mode == "observe"
        assert session.target_citizen is None

    def test_whisper_mode(self) -> None:
        """Can set whisper mode."""
        session = TownSession(mode="whisper", target_citizen="Alice")
        assert session.mode == "whisper"
        assert session.target_citizen == "Alice"

    def test_history_tracking(self) -> None:
        """Tracks whisper and intervention history."""
        session = TownSession()
        session.whisper_history.append({"citizen": "Alice", "message": "hello"})
        session.intervention_history.append("storm")

        assert len(session.whisper_history) == 1
        assert len(session.intervention_history) == 1


class TestTownCommands:
    """Test town CLI commands."""

    @pytest.fixture(autouse=True)
    def setup_simulation(self) -> Generator[None, None, None]:
        """Set up simulation state for each test."""
        # Clear state
        _simulation_state.clear()

        # Create environment and flux
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        _simulation_state["environment"] = env
        _simulation_state["flux"] = flux
        _simulation_state["session"] = TownSession()

        yield

        # Clean up
        _simulation_state.clear()

    def test_whisper_success(self) -> None:
        """Whisper command succeeds for available citizen."""
        result = _whisper_citizen("Alice", "Hello friend!", None)
        assert result == 0

        # Session should be updated
        session = _simulation_state["session"]
        assert session.mode == "whisper"
        assert session.target_citizen == "Alice"
        assert len(session.whisper_history) == 1

    def test_whisper_unknown_citizen(self) -> None:
        """Whisper fails for unknown citizen."""
        result = _whisper_citizen("Unknown", "Hello!", None)
        assert result == 1

    def test_whisper_resting_citizen(self) -> None:
        """Whisper fails for resting citizen."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")
        alice.rest()  # Put Alice to rest

        result = _whisper_citizen("Alice", "Hello!", None)
        assert result == 1

    def test_whisper_affects_eigenvectors(self) -> None:
        """Whisper with positive words affects warmth."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")
        initial_warmth = alice.eigenvectors.warmth

        _whisper_citizen("Alice", "You are so kind and good!", None)

        assert alice.eigenvectors.warmth > initial_warmth

    def test_whisper_question_affects_curiosity(self) -> None:
        """Whisper with question affects curiosity."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")
        initial_curiosity = alice.eigenvectors.curiosity

        _whisper_citizen("Alice", "What do you think about life?", None)

        assert alice.eigenvectors.curiosity > initial_curiosity

    def test_inhabit_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Inhabit command succeeds."""
        # Mock input to immediately quit inhabit mode
        monkeypatch.setattr("builtins.input", lambda _: "q")
        result = _inhabit_citizen("Alice", None)
        assert result == 0

        session = _simulation_state["session"]
        assert session.mode == "inhabit"
        assert session.target_citizen == "Alice"

    def test_inhabit_unknown_citizen(self) -> None:
        """Inhabit fails for unknown citizen."""
        result = _inhabit_citizen("Unknown", None)
        assert result == 1

    def test_intervene_success(self) -> None:
        """Intervene command succeeds."""
        result = _intervene_event("A sudden storm!", None)
        assert result == 0

        session = _simulation_state["session"]
        assert session.mode == "intervene"
        assert "A sudden storm!" in session.intervention_history

    def test_intervene_storm_moves_citizens(self) -> None:
        """Storm intervention moves citizens to shelter."""
        env = _simulation_state["environment"]

        # First put a citizen outside
        bob = env.get_citizen_by_name("Bob")
        bob.move_to("square")

        _intervene_event("A terrible storm!", None)

        # Bob should have moved to inn
        assert bob.region == "inn"

    def test_intervene_festival_increases_warmth(self) -> None:
        """Festival intervention increases warmth."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")
        initial_warmth = alice.eigenvectors.warmth

        _intervene_event("A grand festival!", None)

        assert alice.eigenvectors.warmth > initial_warmth

    def test_intervene_gift_increases_surplus(self) -> None:
        """Gift intervention increases surplus."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")
        initial_surplus = alice.accursed_surplus

        _intervene_event("A surprise gift!", None)

        assert alice.accursed_surplus > initial_surplus


class TestTownCommandDispatch:
    """Test command dispatch."""

    @pytest.fixture(autouse=True)
    def setup_simulation(self) -> Generator[None, None, None]:
        """Set up simulation state."""
        _simulation_state.clear()
        yield
        _simulation_state.clear()

    def test_cmd_town_help(self) -> None:
        """Help command works."""
        result = cmd_town(["help"], None)
        assert result == 0

    def test_cmd_town_start(self) -> None:
        """Start command works."""
        result = cmd_town(["start"], None)
        assert result == 0
        assert "environment" in _simulation_state
        assert "session" in _simulation_state

    def test_cmd_town_start2(self) -> None:
        """Start2 command works."""
        result = cmd_town(["start2"], None)
        assert result == 0
        assert "environment" in _simulation_state

    def test_cmd_town_whisper_requires_sim(self) -> None:
        """Whisper requires simulation."""
        result = cmd_town(["whisper", "Alice", "hello"], None)
        assert result == 1

    def test_cmd_town_inhabit_requires_sim(self) -> None:
        """Inhabit requires simulation."""
        result = cmd_town(["inhabit", "Alice"], None)
        assert result == 1

    def test_cmd_town_intervene_requires_sim(self) -> None:
        """Intervene requires simulation."""
        result = cmd_town(["intervene", "storm"], None)
        assert result == 1


class TestUserModeIntegration:
    """Integration tests for user modes."""

    @pytest.fixture(autouse=True)
    def setup_simulation(self) -> Generator[None, None, None]:
        """Set up simulation state."""
        _simulation_state.clear()
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        _simulation_state["environment"] = env
        _simulation_state["flux"] = flux
        _simulation_state["session"] = TownSession()
        yield
        _simulation_state.clear()

    def test_mode_transitions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Can transition between modes."""
        _whisper_citizen("Alice", "Hello", None)
        assert _simulation_state["session"].mode == "whisper"

        # Mock input to immediately quit inhabit mode
        monkeypatch.setattr("builtins.input", lambda _: "q")
        _inhabit_citizen("Bob", None)
        assert _simulation_state["session"].mode == "inhabit"

        _intervene_event("storm", None)
        assert _simulation_state["session"].mode == "intervene"

    def test_whisper_stores_memory(self) -> None:
        """Whisper stores in citizen memory."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")

        _whisper_citizen("Alice", "Remember this message", None)

        # Check memory store directly
        store = alice.memory._store
        # At least one whisper memory should be stored
        whisper_memories = [
            v
            for v in store.state.values()
            if isinstance(v, dict) and v.get("type") == "whisper"
        ]
        assert len(whisper_memories) >= 1

    def test_multiple_whispers_accumulate(self) -> None:
        """Multiple whispers accumulate in history."""
        _whisper_citizen("Alice", "First whisper", None)
        _whisper_citizen("Alice", "Second whisper", None)
        _whisper_citizen("Bob", "Third whisper", None)

        session = _simulation_state["session"]
        assert len(session.whisper_history) == 3

    def test_multiple_interventions_accumulate(self) -> None:
        """Multiple interventions accumulate in history."""
        _intervene_event("storm", None)
        _intervene_event("festival", None)
        _intervene_event("gift", None)

        session = _simulation_state["session"]
        assert len(session.intervention_history) == 3

    def test_intervene_peace_causes_rest(self) -> None:
        """Peace intervention causes citizens to rest."""
        env = _simulation_state["environment"]

        _intervene_event("A peaceful quiet descends", None)

        resting = [c for c in env.citizens.values() if c.is_resting]
        assert len(resting) > 0

    def test_intervene_rumor_affects_trust(self) -> None:
        """Rumor intervention affects trust."""
        env = _simulation_state["environment"]
        alice = env.get_citizen_by_name("Alice")
        initial_trust = alice.eigenvectors.trust

        _intervene_event("A bad rumor spreads", None)

        assert alice.eigenvectors.trust != initial_trust

    def test_festival_gathers_citizens(self) -> None:
        """Festival intervention gathers citizens to square."""
        env = _simulation_state["environment"]

        _intervene_event("A grand festival!", None)

        in_square = env.get_citizens_in_region("square")
        assert len(in_square) == len(env.citizens)

    def test_generic_intervention_stores_memory(self) -> None:
        """Generic intervention stores in all citizen memories."""
        env = _simulation_state["environment"]

        _intervene_event("Something mysterious happened", None)

        # Check at least one citizen has the intervention stored
        alice = env.get_citizen_by_name("Alice")
        store = alice.memory._store
        intervention_memories = [
            v
            for v in store.state.values()
            if isinstance(v, dict) and v.get("type") == "intervention"
        ]
        assert len(intervention_memories) >= 1
