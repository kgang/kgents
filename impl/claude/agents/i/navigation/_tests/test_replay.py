"""Tests for ReplayController."""

from __future__ import annotations

from datetime import datetime

import pytest

from ..replay import (
    PlaybackState,
    ReplayController,
    ReplayStats,
    Turn,
    TurnHighlightEvent,
    create_demo_turns,
)


class TestTurn:
    """Tests for Turn dataclass."""

    def test_turn_creation(self) -> None:
        """Test basic turn creation."""
        turn = Turn(
            id="turn-001",
            turn_type="ACTION",
            content="Hello world",
            timestamp=datetime.now(),
            duration=0.5,
            agent_id="agent-1",
        )
        assert turn.id == "turn-001"
        assert turn.turn_type == "ACTION"
        assert turn.content == "Hello world"

    def test_turn_with_children(self) -> None:
        """Test turn with children."""
        turn = Turn(
            id="turn-001",
            turn_type="ACTION",
            content="Parent",
            timestamp=datetime.now(),
            duration=0.1,
            children_ids=["turn-002", "turn-003"],
        )
        assert len(turn.children_ids) == 2

    def test_turn_is_ghost(self) -> None:
        """Test ghost turn."""
        turn = Turn(
            id="turn-001",
            turn_type="THOUGHT",
            content="Rejected thought",
            timestamp=datetime.now(),
            duration=0.1,
            is_ghost=True,
        )
        assert turn.is_ghost is True


class TestReplayStats:
    """Tests for ReplayStats."""

    def test_from_controller(self) -> None:
        """Test stats creation from controller."""
        turns = create_demo_turns(10)
        controller = ReplayController(turns=turns)

        stats = controller.get_stats()

        assert stats.total_turns == 10
        assert stats.current_position == 0
        assert stats.speed == 1.0
        assert stats.state == PlaybackState.STOPPED


class TestReplayController:
    """Tests for ReplayController."""

    def test_create_empty(self) -> None:
        """Test creating with empty turns."""
        controller = ReplayController(turns=[])
        assert len(controller.turns) == 0
        assert controller.stopped is True

    def test_create_with_turns(self) -> None:
        """Test creating with turns."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)
        assert len(controller.turns) == 5

    def test_initial_state(self) -> None:
        """Test initial state is stopped."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        assert controller.stopped is True
        assert controller.playing is False
        assert controller.paused is False
        assert controller.playhead == 0

    def test_get_current_turn(self) -> None:
        """Test getting current turn."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        turn = controller.get_current_turn()
        assert turn is not None
        assert turn == turns[0]

    def test_get_current_turn_empty(self) -> None:
        """Test getting current turn when empty."""
        controller = ReplayController(turns=[])
        assert controller.get_current_turn() is None

    def test_step_forward(self) -> None:
        """Test stepping forward."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        assert controller.playhead == 0
        controller.step_forward()
        assert controller.playhead == 1

    def test_step_forward_at_end(self) -> None:
        """Test stepping forward at end."""
        turns = create_demo_turns(3)
        controller = ReplayController(turns=turns)

        controller.step_forward()  # 0 -> 1
        controller.step_forward()  # 1 -> 2
        controller.step_forward()  # should stay at 2
        assert controller.playhead == 2

    def test_step_backward(self) -> None:
        """Test stepping backward."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        controller.step_forward()  # 0 -> 1
        controller.step_backward()  # 1 -> 0
        assert controller.playhead == 0

    def test_step_backward_at_start(self) -> None:
        """Test stepping backward at start."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        controller.step_backward()  # should stay at 0
        assert controller.playhead == 0

    def test_seek(self) -> None:
        """Test seeking to position."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        controller.seek(3)
        assert controller.playhead == 3

    def test_seek_relative(self) -> None:
        """Test relative seeking."""
        turns = create_demo_turns(10)
        controller = ReplayController(turns=turns)

        controller.seek(5)
        controller.seek_relative(-2)
        assert controller.playhead == 3

        controller.seek_relative(4)
        assert controller.playhead == 7

    def test_pause_resume(self) -> None:
        """Test pause and resume."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        # Can't pause from stopped
        controller.pause()
        assert controller.stopped is True

        # Simulate playing state to test pause
        controller._state = PlaybackState.PLAYING
        controller.pause()
        assert controller.paused is True

        controller.resume()
        assert controller.playing is True

    def test_stop(self) -> None:
        """Test stopping playback."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        controller._state = PlaybackState.PLAYING
        controller.stop()
        assert controller.stopped is True
        assert controller.playhead == 0

    def test_cycle_speed(self) -> None:
        """Test cycling playback speed."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        assert controller.speed == 1.0

        new_speed = controller.cycle_speed()
        assert new_speed == 2.0
        assert controller.speed == 2.0

        controller.cycle_speed()
        controller.cycle_speed()
        assert controller.speed == 0.25

        controller.cycle_speed()
        assert controller.speed == 0.5

    def test_set_speed(self) -> None:
        """Test setting speed directly."""
        turns = create_demo_turns(5)
        controller = ReplayController(turns=turns)

        controller.set_speed(0.5)
        assert controller.speed == 0.5


class TestCreateDemoTurns:
    """Tests for create_demo_turns helper."""

    def test_creates_requested_count(self) -> None:
        """Test it creates the requested number of turns."""
        turns = create_demo_turns(10)
        assert len(turns) == 10

    def test_turns_have_unique_ids(self) -> None:
        """Test all turns have unique IDs."""
        turns = create_demo_turns(20)
        ids = [t.id for t in turns]
        assert len(ids) == len(set(ids))

    def test_turns_have_increasing_timestamps(self) -> None:
        """Test turns have increasing timestamps."""
        turns = create_demo_turns(5)
        for i in range(1, len(turns)):
            assert turns[i].timestamp >= turns[i - 1].timestamp
