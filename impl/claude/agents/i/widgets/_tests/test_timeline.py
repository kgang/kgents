"""
Tests for Timeline widget.

Verifies temporal visualization with activity bars and cursor navigation.
"""

from datetime import datetime, timedelta

import pytest

from agents.i.widgets.timeline import Timeline


class TestTimelineRendering:
    """Test Timeline widget rendering."""

    def test_empty_timeline(self) -> None:
        """Empty timeline shows message."""
        timeline = Timeline()

        output = timeline.render()
        assert output == "No timeline data"

    def test_single_day(self) -> None:
        """Single day renders with activity bar."""
        now = datetime.now()
        events = [(now, 0.5), (now, 0.6), (now, 0.7)]

        timeline = Timeline(events=events)
        output = str(timeline.render())

        # Should contain day label
        day_label = now.strftime("%b %d")
        assert day_label in output

        # Should contain cursor
        assert "▲" in output

    def test_multiple_days(self) -> None:
        """Multiple days render with separate bars."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)

        events = [
            (two_days_ago, 0.3),
            (yesterday, 0.5),
            (now, 0.8),
        ]

        timeline = Timeline(events=events)
        output = str(timeline.render())

        # Should contain multiple day labels
        assert now.strftime("%b %d") in output
        assert yesterday.strftime("%b %d") in output

    def test_activity_bars_vary_by_intensity(self) -> None:
        """Activity bars show different heights."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        # Low activity yesterday, high activity today
        events = [
            (yesterday, 0.1),
            (now, 0.9),
        ]

        timeline = Timeline(events=events, num_days=2)
        output = str(timeline.render())

        # Should contain block characters for bars
        # Low intensity: ▁
        # High intensity: █
        assert "▁" in output or "█" in output

    def test_cursor_positioning(self) -> None:
        """Cursor appears at correct position."""
        now = datetime.now()
        events = [(now, 0.5)]

        timeline = Timeline(events=events, cursor_index=0)
        output = str(timeline.render())

        # Should have cursor symbol
        assert "▲" in output

    def test_num_days_limits_display(self) -> None:
        """Only shows specified number of days."""
        now = datetime.now()
        events = []

        # Create 10 days of events
        for i in range(10):
            day = now - timedelta(days=i)
            events.append((day, 0.5))

        # Only show 5 days
        timeline = Timeline(events=events, num_days=5)
        output = str(timeline.render())

        # Each line has 4 separators between 5 days
        # Output has 3 lines: header, bars, cursor
        lines = output.split("\n")
        assert len(lines) == 3
        # First line (header) should have 4 separators between 5 days
        assert lines[0].count(" │ ") == 4


class TestTimelineNavigation:
    """Test cursor navigation."""

    def test_move_cursor_left(self) -> None:
        """Can move cursor to earlier day."""
        now = datetime.now()
        events = [
            (now - timedelta(days=2), 0.5),
            (now - timedelta(days=1), 0.5),
            (now, 0.5),
        ]

        timeline = Timeline(events=events, cursor_index=2, num_days=3)

        timeline.move_cursor_left()
        assert timeline.cursor_index == 1

        timeline.move_cursor_left()
        assert timeline.cursor_index == 0

    def test_move_cursor_left_at_boundary(self) -> None:
        """Can't move cursor left past start."""
        now = datetime.now()
        events = [(now, 0.5)]

        timeline = Timeline(events=events, cursor_index=0)

        timeline.move_cursor_left()
        # Should stay at 0
        assert timeline.cursor_index == 0

    def test_move_cursor_right(self) -> None:
        """Can move cursor to later day."""
        now = datetime.now()
        events = [
            (now - timedelta(days=1), 0.5),
            (now, 0.5),
        ]

        timeline = Timeline(events=events, cursor_index=0, num_days=2)

        timeline.move_cursor_right()
        assert timeline.cursor_index == 1

    def test_move_cursor_right_at_boundary(self) -> None:
        """Can't move cursor right past end."""
        now = datetime.now()
        events = [(now, 0.5)]

        timeline = Timeline(events=events, cursor_index=0)

        timeline.move_cursor_right()
        # Should stay at 0 (no more days)
        assert timeline.cursor_index == 0

    def test_add_event(self) -> None:
        """Can add events to timeline."""
        timeline = Timeline()

        now = datetime.now()
        timeline.add_event(now, 0.5)

        assert len(timeline.events) == 1
        assert timeline.events[0] == (now, 0.5)


class TestTimelineDayBar:
    """Test day bar generation."""

    def test_day_bar_empty(self) -> None:
        """Empty day shows baseline."""
        timeline = Timeline()
        bar = timeline._day_bar([])

        assert bar == "▁" * 8

    def test_day_bar_low_activity(self) -> None:
        """Low activity shows low bar."""
        timeline = Timeline()
        bar = timeline._day_bar([0.1, 0.1, 0.1])

        # Should use low block characters
        assert "▁" in bar or "▂" in bar

    def test_day_bar_high_activity(self) -> None:
        """High activity shows high bar."""
        timeline = Timeline()
        bar = timeline._day_bar([0.9, 0.9, 0.9])

        # Should use high block characters
        assert "█" in bar or "▇" in bar

    def test_day_bar_length(self) -> None:
        """Day bar is always 8 characters."""
        timeline = Timeline()

        bar_empty = timeline._day_bar([])
        bar_low = timeline._day_bar([0.1])
        bar_high = timeline._day_bar([0.9])

        assert len(bar_empty) == 8
        assert len(bar_low) == 8
        assert len(bar_high) == 8

    def test_day_bar_averages_values(self) -> None:
        """Multiple values are averaged."""
        timeline = Timeline()

        # Mix of high and low should average to medium
        bar = timeline._day_bar([0.0, 1.0])

        # Should use medium block character
        assert bar not in ["▁" * 8, "█" * 8]


class TestTimelineGrouping:
    """Test event grouping by day."""

    def test_group_by_day_single_day(self) -> None:
        """Events on same day are grouped."""
        now = datetime.now()
        events = [
            (now, 0.3),
            (now, 0.5),
            (now, 0.7),
        ]

        timeline = Timeline(events=events)
        by_day = timeline._group_by_day()

        day_key = now.strftime("%b %d")
        assert day_key in by_day
        assert len(by_day[day_key]) == 3

    def test_group_by_day_multiple_days(self) -> None:
        """Events on different days are separated."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        events = [
            (yesterday, 0.3),
            (now, 0.5),
        ]

        timeline = Timeline(events=events)
        by_day = timeline._group_by_day()

        assert len(by_day) == 2
        assert now.strftime("%b %d") in by_day
        assert yesterday.strftime("%b %d") in by_day
