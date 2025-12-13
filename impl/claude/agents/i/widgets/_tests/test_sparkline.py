"""
Tests for Sparkline widget.

Verifies sparkline generation, reactive updates, and edge cases.
"""

import pytest
from agents.i.widgets.sparkline import Sparkline, generate_sparkline


class TestGenerateSparkline:
    """Test generate_sparkline helper function."""

    def test_empty_values(self) -> None:
        """Empty list returns baseline."""
        spark = generate_sparkline([], width=5)
        assert spark == "▁▁▁▁▁"
        assert len(spark) == 5

    def test_empty_values_custom_width(self) -> None:
        """Empty list respects custom width."""
        spark = generate_sparkline([], width=10)
        assert spark == "▁" * 10
        assert len(spark) == 10

    def test_single_value(self) -> None:
        """Single value renders as baseline (no range)."""
        spark = generate_sparkline([5.0], width=5)
        # Single value has zero range, so renders as baseline
        assert "▁" in spark
        assert len(spark) == 5

    def test_two_values_min_max(self) -> None:
        """Two values create min and max."""
        spark = generate_sparkline([0.0, 100.0], width=5)
        # Should have padding + min + max
        assert len(spark) == 5
        # Last two chars should be min (▁) and max (█)
        assert spark[-2] == "▁"  # Min value
        assert spark[-1] == "█"  # Max value

    def test_ascending_sequence(self) -> None:
        """Ascending sequence shows progression."""
        values = [0.0, 25.0, 50.0, 75.0, 100.0]
        spark = generate_sparkline(values, width=5)

        assert len(spark) == 5
        assert spark[0] == "▁"  # Min
        assert spark[-1] == "█"  # Max
        # Middle values should be between
        assert spark[1] < spark[2] < spark[3]

    def test_descending_sequence(self) -> None:
        """Descending sequence shows decline."""
        values = [100.0, 75.0, 50.0, 25.0, 0.0]
        spark = generate_sparkline(values, width=5)

        assert len(spark) == 5
        assert spark[0] == "█"  # Max
        assert spark[-1] == "▁"  # Min

    def test_constant_values(self) -> None:
        """All same values render as single character."""
        values = [5.0, 5.0, 5.0, 5.0, 5.0]
        spark = generate_sparkline(values, width=5)

        # No range, so all baseline
        assert all(c == "▁" for c in spark)

    def test_values_exceed_width(self) -> None:
        """Values exceed width - takes last N."""
        values = [float(i) for i in range(20)]  # 0-19
        spark = generate_sparkline(values, width=10)

        # Should take last 10: 10-19
        assert len(spark) == 10
        # Should show progression
        assert spark[0] < spark[-1]

    def test_values_less_than_width(self) -> None:
        """Values less than width - pads left."""
        values = [0.0, 50.0, 100.0]
        spark = generate_sparkline(values, width=5)

        assert len(spark) == 5
        # Should have 2 chars of padding
        assert spark[0] == "▁"
        assert spark[1] == "▁"
        # Then the actual values
        assert spark[2] == "▁"  # 0.0
        assert spark[3] in "▃▄▅"  # 50.0 (middle)
        assert spark[4] == "█"  # 100.0

    def test_negative_values(self) -> None:
        """Negative values normalized correctly."""
        values = [-10.0, 0.0, 10.0]
        spark = generate_sparkline(values, width=3)

        assert len(spark) == 3
        assert spark[0] == "▁"  # Min (-10)
        assert spark[1] in "▃▄"  # Middle (0)
        assert spark[2] == "█"  # Max (10)

    def test_fractional_values(self) -> None:
        """Fractional values handled correctly."""
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        spark = generate_sparkline(values, width=5)

        assert len(spark) == 5
        # Should show progression
        for i in range(len(spark) - 1):
            assert spark[i] <= spark[i + 1]

    def test_characters_used(self) -> None:
        """Uses correct sparkline characters."""
        chars = "▁▂▃▄▅▆▇█"
        values = [float(i) for i in range(8)]
        spark = generate_sparkline(values, width=8)

        # All characters should be from the sparkline set
        for c in spark:
            assert c in chars

    def test_width_one(self) -> None:
        """Width of 1 works."""
        values = [5.0, 10.0, 15.0]
        spark = generate_sparkline(values, width=1)

        assert len(spark) == 1
        # Should take last value
        assert spark in "▁▂▃▄▅▆▇█"

    def test_large_range(self) -> None:
        """Large value range normalizes correctly."""
        values = [0.0, 1000000.0]
        spark = generate_sparkline(values, width=5)

        assert len(spark) == 5
        assert spark[-2] == "▁"  # Min
        assert spark[-1] == "█"  # Max


class TestSparklineWidget:
    """Test Sparkline widget."""

    def test_initialization_default(self) -> None:
        """Widget initializes with defaults."""
        sparkline = Sparkline()

        assert sparkline.values == []
        assert sparkline.width == 20

    def test_initialization_with_values(self) -> None:
        """Widget initializes with values."""
        values = [1.0, 2.0, 3.0]
        sparkline = Sparkline(values=values)

        assert sparkline.values == values
        assert sparkline.width == 20

    def test_initialization_with_width(self) -> None:
        """Widget initializes with custom width."""
        sparkline = Sparkline(width=10)

        assert sparkline.values == []
        assert sparkline.width == 10

    def test_initialization_with_both(self) -> None:
        """Widget initializes with values and width."""
        values = [5.0, 10.0, 15.0]
        sparkline = Sparkline(values=values, width=15)

        assert sparkline.values == values
        assert sparkline.width == 15

    def test_add_value(self) -> None:
        """add_value appends to values."""
        sparkline = Sparkline(values=[1.0, 2.0])

        sparkline.add_value(3.0)

        assert sparkline.values == [1.0, 2.0, 3.0]

    def test_add_value_to_empty(self) -> None:
        """add_value works on empty list."""
        sparkline = Sparkline()

        sparkline.add_value(5.0)

        assert sparkline.values == [5.0]

    def test_set_values(self) -> None:
        """set_values replaces all values."""
        sparkline = Sparkline(values=[1.0, 2.0])

        sparkline.set_values([10.0, 20.0, 30.0])

        assert sparkline.values == [10.0, 20.0, 30.0]

    def test_set_values_empty(self) -> None:
        """set_values can clear values."""
        sparkline = Sparkline(values=[1.0, 2.0])

        sparkline.set_values([])

        assert sparkline.values == []

    def test_reactive_values(self) -> None:
        """Values is reactive property."""
        sparkline = Sparkline(values=[1.0])

        # Direct assignment triggers reactivity
        sparkline.values = [2.0, 3.0]

        assert sparkline.values == [2.0, 3.0]

    def test_reactive_width(self) -> None:
        """Width is reactive property."""
        sparkline = Sparkline(width=10)

        sparkline.width = 30

        assert sparkline.width == 30

    def test_render_empty(self) -> None:
        """Render with no values."""
        sparkline = Sparkline(width=8)

        result = sparkline.render()

        assert result == "▁" * 8

    def test_render_with_values(self) -> None:
        """Render with values."""
        sparkline = Sparkline(values=[0.0, 50.0, 100.0], width=5)

        result = str(sparkline.render())

        assert len(result) == 5
        assert "▁" in result  # Min value
        assert "█" in result  # Max value

    def test_css_classes_exist(self) -> None:
        """Widget has expected CSS classes."""
        sparkline = Sparkline()

        # Check DEFAULT_CSS is defined
        assert hasattr(Sparkline, "DEFAULT_CSS")
        assert "Sparkline" in Sparkline.DEFAULT_CSS


class TestSparklineIntegration:
    """Integration tests for sparkline behavior."""

    def test_progressive_addition(self) -> None:
        """Adding values progressively updates sparkline."""
        sparkline = Sparkline(width=5)

        # Add values one by one
        for i in range(10):
            sparkline.add_value(float(i))

        # Should have last 5 values rendered
        result = str(sparkline.render())
        assert len(result) == 5

    def test_time_series_simulation(self) -> None:
        """Simulate time-series data."""
        values = [10.0, 12.0, 15.0, 14.0, 20.0, 25.0, 22.0, 30.0]
        sparkline = Sparkline(values=values, width=8)

        result = str(sparkline.render())

        # Should show general upward trend
        assert len(result) == 8
        assert result[0] == "▁"  # Min (10.0)
        assert result[-1] == "█"  # Max (30.0)

    def test_token_burn_rate_example(self) -> None:
        """Example: token burn rate over time."""
        burn_rates = [5.0, 8.0, 12.0, 15.0, 10.0, 6.0, 3.0]
        sparkline = Sparkline(values=burn_rates, width=7)

        result = str(sparkline.render())

        assert len(result) == 7
        # Should show rise then fall
        assert result[0] < result[3]  # Rising
        assert result[3] > result[-1]  # Falling
