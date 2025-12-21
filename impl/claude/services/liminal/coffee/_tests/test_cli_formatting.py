"""
Tests for Morning Coffee CLI formatting.

Tests the rich terminal output formatters.
"""

from __future__ import annotations

import pytest

from services.liminal.coffee.cli_formatting import (
    DEFAULT_WIDTH,
    format_captured_voice,
    format_garden_view,
    format_history,
    format_manifest,
    format_menu,
    format_transition,
    format_weather,
)


class TestBoxDrawing:
    """Test box drawing utilities."""

    def test_garden_view_has_box(self) -> None:
        """Garden view should be wrapped in a box."""
        data = {"harvest": [], "growing": [], "sprouting": [], "seeds": []}
        result = format_garden_view(data)

        assert "┌" in result
        assert "└" in result
        assert "│" in result

    def test_weather_has_box(self) -> None:
        """Weather should be wrapped in a box."""
        data = {"refactoring": [], "emerging": [], "scaffolding": [], "tension": []}
        result = format_weather(data)

        assert "┌" in result
        assert "└" in result

    def test_menu_has_box(self) -> None:
        """Menu should be wrapped in a box."""
        data = {"gentle": [], "focused": [], "intense": [], "serendipitous_prompt": "?"}
        result = format_menu(data)

        assert "┌" in result
        assert "└" in result


class TestGardenViewFormatter:
    """Test garden view formatting."""

    def test_shows_title(self) -> None:
        """Garden view should have a title."""
        data = {"harvest": [], "growing": [], "sprouting": [], "seeds": []}
        result = format_garden_view(data)

        assert "Yesterday's Garden" in result

    def test_shows_harvest_items(self) -> None:
        """Harvest items should be displayed."""
        data = {
            "harvest": [{"description": "Brain persistence hardening"}],
            "growing": [],
            "sprouting": [],
            "seeds": [],
        }
        result = format_garden_view(data)

        assert "HARVEST" in result
        assert "Brain persistence" in result

    def test_shows_growing_items(self) -> None:
        """Growing items should be displayed."""
        data = {
            "harvest": [],
            "growing": [{"description": "Gestalt crystalline rendering"}],
            "sprouting": [],
            "seeds": [],
        }
        result = format_garden_view(data)

        assert "GROWING" in result
        assert "Gestalt" in result

    def test_empty_shows_fallback(self) -> None:
        """Empty garden should show fallback message."""
        data = {"harvest": [], "growing": [], "sprouting": [], "seeds": []}
        result = format_garden_view(data)

        assert "garden rests" in result or "planting day" in result

    def test_truncates_long_descriptions(self) -> None:
        """Long descriptions should be truncated."""
        data = {
            "harvest": [{"description": "A" * 100}],
            "growing": [],
            "sprouting": [],
            "seeds": [],
        }
        result = format_garden_view(data)

        assert "..." in result

    def test_limits_items_per_category(self) -> None:
        """Should limit items shown per category."""
        data = {
            "harvest": [{"description": f"Item {i}"} for i in range(10)],
            "growing": [],
            "sprouting": [],
            "seeds": [],
        }
        result = format_garden_view(data)

        # Should only show first 5
        assert "Item 4" in result
        assert "Item 9" not in result


class TestWeatherFormatter:
    """Test weather formatting."""

    def test_shows_title(self) -> None:
        """Weather should have a title."""
        data = {"refactoring": [], "emerging": [], "scaffolding": [], "tension": []}
        result = format_weather(data)

        assert "Conceptual Weather" in result

    def test_shows_refactoring_patterns(self) -> None:
        """Refactoring patterns should be displayed."""
        data = {
            "refactoring": [{"label": "S-gents → D-gents consolidation"}],
            "emerging": [],
            "scaffolding": [],
            "tension": [],
        }
        result = format_weather(data)

        assert "REFACTORING" in result
        assert "S-gents" in result

    def test_shows_emerging_patterns(self) -> None:
        """Emerging patterns should be displayed."""
        data = {
            "refactoring": [],
            "emerging": [{"label": "Failure-as-Evidence principle"}],
            "scaffolding": [],
            "tension": [],
        }
        result = format_weather(data)

        assert "EMERGING" in result
        assert "Failure" in result

    def test_empty_shows_clear_skies(self) -> None:
        """Empty weather should show clear skies message."""
        data = {"refactoring": [], "emerging": [], "scaffolding": [], "tension": []}
        result = format_weather(data)

        assert "Clear skies" in result


class TestMenuFormatter:
    """Test menu formatting."""

    def test_shows_title(self) -> None:
        """Menu should have a title."""
        data = {"gentle": [], "focused": [], "intense": [], "serendipitous_prompt": "?"}
        result = format_menu(data)

        assert "Today's Menu" in result

    def test_shows_gentle_items(self) -> None:
        """Gentle items should be displayed with numbers."""
        data = {
            "gentle": [{"label": "Write a test"}],
            "focused": [],
            "intense": [],
            "serendipitous_prompt": "?",
        }
        result = format_menu(data)

        assert "GENTLE" in result
        assert "1." in result
        assert "Write a test" in result

    def test_shows_focused_items(self) -> None:
        """Focused items should be displayed."""
        data = {
            "gentle": [],
            "focused": [{"label": "Wire ASHC L0 kernel"}],
            "intense": [],
            "serendipitous_prompt": "?",
        }
        result = format_menu(data)

        assert "FOCUSED" in result
        assert "ASHC" in result

    def test_shows_intense_items(self) -> None:
        """Intense items should be displayed."""
        data = {
            "gentle": [],
            "focused": [],
            "intense": [{"label": "Bootstrap regeneration"}],
            "serendipitous_prompt": "?",
        }
        result = format_menu(data)

        assert "INTENSE" in result
        assert "Bootstrap" in result

    def test_always_shows_serendipitous(self) -> None:
        """Serendipitous option should always be shown."""
        data = {
            "gentle": [],
            "focused": [],
            "intense": [],
            "serendipitous_prompt": "What caught your eye?",
        }
        result = format_menu(data)

        assert "SERENDIPITOUS" in result
        assert "caught your eye" in result

    def test_numbers_are_sequential(self) -> None:
        """Item numbers should be sequential across categories."""
        data = {
            "gentle": [{"label": "Item A"}],
            "focused": [{"label": "Item B"}],
            "intense": [{"label": "Item C"}],
            "serendipitous_prompt": "?",
        }
        result = format_menu(data)

        assert "1." in result
        assert "2." in result
        assert "3." in result


class TestManifestFormatter:
    """Test manifest formatting."""

    def test_shows_ready_when_not_started(self) -> None:
        """Should show ready state when no ritual started."""
        data = {
            "state": "DORMANT",
            "is_active": False,
            "current_movement": None,
            "today_voice": None,
            "last_ritual": None,
        }
        result = format_manifest(data)

        assert "ready" in result.lower()
        assert "--quick" in result

    def test_shows_complete_when_voice_captured(self) -> None:
        """Should show complete when today's voice exists."""
        data = {
            "state": "DORMANT",
            "is_active": False,
            "current_movement": None,
            "today_voice": {"success_criteria": "Ship the feature"},
            "last_ritual": "2025-12-21",
        }
        result = format_manifest(data)

        assert "complete" in result.lower()
        assert "Ship the feature" in result

    def test_shows_in_progress_when_active(self) -> None:
        """Should show in progress when ritual is active."""
        data = {
            "state": "GARDEN",
            "is_active": True,
            "current_movement": "garden",
            "today_voice": None,
            "last_ritual": None,
        }
        result = format_manifest(data)

        assert "in progress" in result.lower()


class TestTransitionFormatter:
    """Test transition formatting."""

    def test_shows_transition_message(self) -> None:
        """Should show transition message."""
        result = format_transition(None)

        assert "Transitioning" in result
        assert "morning is yours" in result.lower()

    def test_shows_selected_item(self) -> None:
        """Should show selected item if provided."""
        result = format_transition({"label": "ASHC L0 Kernel", "source": "menu"})

        assert "ASHC L0 Kernel" in result
        assert "Selected" in result

    def test_shows_source_if_not_todo(self) -> None:
        """Should show source if not from todo."""
        result = format_transition({"label": "Something", "source": "plan"})

        assert "plan" in result.lower()


class TestHistoryFormatter:
    """Test history formatting."""

    def test_shows_title(self) -> None:
        """History should have a title."""
        data = {"voices": [], "patterns": None}
        result = format_history(data)

        # Either empty message or box title
        assert "history" in result.lower() or "captures" in result.lower()

    def test_shows_empty_message(self) -> None:
        """Empty history should show guidance."""
        data = {"voices": [], "patterns": None}
        result = format_history(data)

        assert "capture" in result.lower()

    def test_shows_voices(self) -> None:
        """Should show voice entries."""
        data = {
            "voices": [
                {
                    "captured_date": "2025-12-21",
                    "success_criteria": "Ship it",
                    "is_substantive": True,
                }
            ],
            "patterns": None,
        }
        result = format_history(data)

        assert "2025-12-21" in result
        assert "Ship it" in result

    def test_shows_patterns(self) -> None:
        """Should show patterns when available."""
        data = {
            "voices": [
                {"captured_date": "2025-12-21", "is_substantive": True},
                {"captured_date": "2025-12-20", "is_substantive": True},
                {"captured_date": "2025-12-19", "is_substantive": True},
            ],
            "patterns": {"common_themes": ["ship", "understand", "fun"]},
        }
        result = format_history(data)

        assert "themes" in result.lower()


class TestCapturedVoiceFormatter:
    """Test captured voice confirmation formatting."""

    def test_shows_confirmation(self) -> None:
        """Should show capture confirmation."""
        data = {
            "voice": {"success_criteria": "Understand the problem"},
            "saved_path": "/path/to/voice.json",
        }
        result = format_captured_voice(data)

        assert "captured" in result.lower()
        assert "Understand the problem" in result

    def test_shows_saved_path(self) -> None:
        """Should show saved path."""
        data = {
            "voice": {},
            "saved_path": "/path/to/voice.json",
        }
        result = format_captured_voice(data)

        assert "/path/to/voice.json" in result

    def test_shows_voice_anchor_note(self) -> None:
        """Should mention voice anchor."""
        data = {"voice": {"success_criteria": "Test"}, "saved_path": "/tmp/test.json"}
        result = format_captured_voice(data)

        assert "anchor" in result.lower()
