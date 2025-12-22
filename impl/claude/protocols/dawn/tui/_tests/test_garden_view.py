"""
Tests for Dawn Cockpit Garden View.

Tests the event stream and status bar behavior.
"""

from __future__ import annotations

import pytest

from protocols.dawn.tui.garden_view import MAX_EVENTS, GardenView


class TestGardenViewConstruction:
    """Tests for GardenView construction."""

    def test_create_garden_view(self) -> None:
        """Test creating garden view."""
        view = GardenView()

        assert view._event_history is not None
        assert len(view._event_history) == 0

    def test_initial_events_empty(self) -> None:
        """Test events are initially empty."""
        view = GardenView()

        assert view.events == ()


class TestGardenViewEvents:
    """Tests for event management."""

    def test_add_event(self) -> None:
        """Test adding an event."""
        view = GardenView()

        view.add_event("Test event")

        assert len(view._event_history) == 1
        assert view.events == ("Test event",)

    def test_add_multiple_events(self) -> None:
        """Test adding multiple events."""
        view = GardenView()

        view.add_event("Event 1")
        view.add_event("Event 2")
        view.add_event("Event 3")

        assert len(view._event_history) == 3
        assert len(view.events) == 3

    def test_events_limited_to_max(self) -> None:
        """Test that displayed events are limited to MAX_EVENTS."""
        view = GardenView()

        # Add more than MAX_EVENTS
        for i in range(MAX_EVENTS + 5):
            view.add_event(f"Event {i}")

        # History should have all events
        assert len(view._event_history) == MAX_EVENTS + 5

        # Displayed events should be limited
        assert len(view.events) == MAX_EVENTS

    def test_events_are_most_recent(self) -> None:
        """Test that displayed events are the most recent."""
        view = GardenView()

        # Add more than MAX_EVENTS
        for i in range(MAX_EVENTS + 5):
            view.add_event(f"Event {i}")

        # Should show the last MAX_EVENTS
        expected_last = f"Event {MAX_EVENTS + 4}"
        assert expected_last in view.events

    def test_clear_events(self) -> None:
        """Test clearing events."""
        view = GardenView()

        view.add_event("Event 1")
        view.add_event("Event 2")

        view.clear()

        assert len(view._event_history) == 0
        assert view.events == ()


class TestGardenViewHistory:
    """Tests for event history."""

    def test_history_has_max_length(self) -> None:
        """Test history has a maximum length."""
        view = GardenView()

        # Add many events
        for i in range(100):
            view.add_event(f"Event {i}")

        # History should be capped at 50 (deque maxlen)
        assert len(view._event_history) == 50

    def test_events_have_timestamps(self) -> None:
        """Test that events in history have timestamps."""
        view = GardenView()

        view.add_event("Test event")

        # History contains (timestamp, event) tuples
        timestamp, event = view._event_history[0]

        from datetime import datetime

        assert isinstance(timestamp, datetime)
        assert event == "Test event"


class TestGardenViewConstants:
    """Tests for garden view constants."""

    def test_max_events_defined(self) -> None:
        """Test MAX_EVENTS is defined and reasonable."""
        assert MAX_EVENTS >= 1
        assert MAX_EVENTS <= 10  # Should be a small number
