"""
Tests for gardener CLI handler.

Session: F-gent Crown Jewels Integration (Phase 3)

Tests cover:
- Basic gardener commands
- Chat mode (Phase 3: Gardener + ChatFlow)
- Gesture parsing
"""

from __future__ import annotations

import os
from typing import Generator

import pytest
from protocols.cli.handlers.gardener import (
    GESTURE_PATTERNS,
    _parse_gesture,
    cmd_gardener,
)


@pytest.fixture(autouse=True)
def isolate_gardener(tmp_path: str) -> Generator[None, None, None]:
    """Isolate gardener tests with temp directory."""
    from pathlib import Path

    # Use temp directory for gardener storage
    gardener_dir = Path(tmp_path) / "kgents" / "gardener"
    gardener_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variable for data storage location
    old_data_dir = os.environ.get("KGENTS_DATA_DIR")
    os.environ["KGENTS_DATA_DIR"] = str(Path(tmp_path))

    yield

    # Restore original env
    if old_data_dir is not None:
        os.environ["KGENTS_DATA_DIR"] = old_data_dir
    elif "KGENTS_DATA_DIR" in os.environ:
        del os.environ["KGENTS_DATA_DIR"]


# =============================================================================
# Basic Command Tests
# =============================================================================


class TestGardenerHelp:
    """Tests for gardener --help."""

    def test_help_returns_zero(self) -> None:
        """--help should return 0."""
        result = cmd_gardener(["--help"])
        assert result == 0

    def test_help_short_returns_zero(self) -> None:
        """-h should return 0."""
        result = cmd_gardener(["-h"])
        assert result == 0


class TestGardenerStatus:
    """Tests for gardener status command."""

    def test_status_default(self) -> None:
        """Default command (no args) shows status."""
        result = cmd_gardener([])
        assert result == 0

    def test_status_explicit(self) -> None:
        """Explicit status command works."""
        result = cmd_gardener(["status"])
        assert result == 0


# =============================================================================
# Gesture Parsing Tests (Phase 3)
# =============================================================================


class TestGesturePatterns:
    """Tests for gesture pattern definitions."""

    def test_all_gestures_have_keywords(self) -> None:
        """All six gestures should have keywords defined."""
        expected = {"observe", "prune", "graft", "water", "rotate", "wait"}
        assert set(GESTURE_PATTERNS.keys()) == expected

    def test_all_keywords_are_lowercase(self) -> None:
        """All keywords should be lowercase."""
        for gesture, keywords in GESTURE_PATTERNS.items():
            for keyword in keywords:
                assert keyword == keyword.lower(), f"{gesture}:{keyword} not lowercase"


class TestGestureParsing:
    """Tests for _parse_gesture function."""

    def test_observe_keyword(self) -> None:
        """'observe' keyword maps to OBSERVE gesture."""
        gesture, target = _parse_gesture("observe the forest")
        assert gesture == "OBSERVE"
        assert "forest" in target

    def test_look_keyword(self) -> None:
        """'look' keyword maps to OBSERVE gesture."""
        gesture, target = _parse_gesture("look at plans")
        assert gesture == "OBSERVE"
        assert "plans" in target

    def test_prune_keyword(self) -> None:
        """'prune' keyword maps to PRUNE gesture."""
        gesture, target = _parse_gesture("prune stale tasks")
        assert gesture == "PRUNE"
        assert "stale tasks" in target

    def test_water_keyword(self) -> None:
        """'water' keyword maps to WATER gesture."""
        gesture, target = _parse_gesture("water the blocked plots")
        assert gesture == "WATER"
        assert "blocked plots" in target

    def test_graft_keyword(self) -> None:
        """'graft' keyword maps to GRAFT gesture."""
        gesture, target = _parse_gesture("graft these two modules")
        assert gesture == "GRAFT"

    def test_rotate_keyword(self) -> None:
        """'rotate' keyword maps to ROTATE gesture."""
        gesture, target = _parse_gesture("rotate priorities")
        assert gesture == "ROTATE"
        assert "priorities" in target

    def test_wait_keyword(self) -> None:
        """'wait' keyword maps to WAIT gesture."""
        gesture, target = _parse_gesture("wait for CI")
        assert gesture == "WAIT"
        assert "ci" in target.lower()

    def test_default_to_observe(self) -> None:
        """Unknown text defaults to OBSERVE gesture."""
        gesture, target = _parse_gesture("what is the current status")
        assert gesture == "OBSERVE"
        assert "what is the current status" in target

    def test_empty_input(self) -> None:
        """Empty input returns OBSERVE with garden target."""
        gesture, target = _parse_gesture("")
        assert gesture == "OBSERVE"
        assert target == "garden"

    def test_keyword_only(self) -> None:
        """Keyword with no target uses 'garden' as default."""
        gesture, target = _parse_gesture("observe")
        assert gesture == "OBSERVE"
        assert target == "garden"

    def test_case_insensitive(self) -> None:
        """Gesture parsing should be case insensitive."""
        gesture, _ = _parse_gesture("PRUNE the weeds")
        assert gesture == "PRUNE"

        gesture2, _ = _parse_gesture("PrUnE the weeds")
        assert gesture2 == "PRUNE"


# =============================================================================
# Chat Command Tests (Phase 3)
# =============================================================================


class TestGardenerChat:
    """Tests for gardener chat command (Phase 3 F-gent integration)."""

    def test_chat_single_intent(self) -> None:
        """Chat with intent argument does single gesture mode."""
        result = cmd_gardener(["chat", "observe the forest"])
        assert result == 0

    def test_chat_prune_intent(self) -> None:
        """Chat with prune intent works."""
        result = cmd_gardener(["chat", "prune stale tasks"])
        assert result == 0

    def test_chat_water_intent(self) -> None:
        """Chat with water intent works."""
        result = cmd_gardener(["chat", "water blocked plots"])
        assert result == 0

    def test_chat_empty_intent_shows_error(self) -> None:
        """Chat with empty intent shows error."""
        result = cmd_gardener(["chat", "   "])
        assert result == 1

    def test_chat_multiple_args_joins(self) -> None:
        """Chat with multiple args joins them into intent."""
        result = cmd_gardener(["chat", "observe", "the", "current", "forest"])
        assert result == 0

    def test_unknown_command(self) -> None:
        """Unknown subcommand returns error."""
        result = cmd_gardener(["unknown_cmd"])
        assert result == 1


# =============================================================================
# Garden Command Tests (Idea Lifecycle)
# =============================================================================


class TestGardenerGarden:
    """Tests for garden status command."""

    def test_garden_status_returns_zero(self) -> None:
        """Garden status command should succeed."""
        result = cmd_gardener(["garden"])
        assert result == 0


class TestGardenerPlant:
    """Tests for plant command."""

    def test_plant_with_idea(self) -> None:
        """Planting an idea should succeed."""
        result = cmd_gardener(["plant", "Test idea about composability"])
        assert result == 0

    def test_plant_multiple_words(self) -> None:
        """Planting idea with multiple words works."""
        result = cmd_gardener(["plant", "This", "is", "a", "test", "idea"])
        assert result == 0

    def test_plant_empty_fails(self) -> None:
        """Planting empty idea should fail."""
        result = cmd_gardener(["plant"])
        assert result == 1

    def test_plant_whitespace_fails(self) -> None:
        """Planting whitespace-only idea should fail."""
        result = cmd_gardener(["plant", "   "])
        assert result == 1


class TestGardenerHarvest:
    """Tests for harvest command."""

    def test_harvest_returns_zero(self) -> None:
        """Harvest command should succeed (even with no flowers)."""
        result = cmd_gardener(["harvest"])
        assert result == 0


class TestGardenerSurprise:
    """Tests for surprise/serendipity command."""

    def test_surprise_returns_zero(self) -> None:
        """Surprise command should succeed (even with empty garden)."""
        result = cmd_gardener(["surprise"])
        assert result == 0

    def test_serendipity_alias(self) -> None:
        """Serendipity is alias for surprise."""
        result = cmd_gardener(["serendipity"])
        assert result == 0

    def test_void_alias(self) -> None:
        """Void is alias for surprise."""
        result = cmd_gardener(["void"])
        assert result == 0

    def test_surprise_with_planted_ideas(self) -> None:
        """Surprise should work with planted ideas."""
        # Plant some ideas first
        cmd_gardener(["plant", "First test idea"])
        cmd_gardener(["plant", "Second test idea"])
        cmd_gardener(["plant", "Third test idea"])

        result = cmd_gardener(["surprise"])
        assert result == 0
