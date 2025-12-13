"""
Tests for DashboardTheme.

Validates:
- Color consistency
- Animation timing constants
- Semantic color helpers
- CSS generation
"""

from __future__ import annotations

import pytest

from ..dashboard import THEME, DashboardTheme


class TestDashboardTheme:
    """Test suite for DashboardTheme."""

    def test_theme_singleton(self) -> None:
        """THEME is a singleton instance."""
        assert isinstance(THEME, DashboardTheme)
        assert THEME.background == "#1a1a1a"

    def test_color_consistency(self) -> None:
        """All colors are valid hex codes."""
        theme = DashboardTheme()

        # Check all color attributes
        colors = [
            theme.background,
            theme.surface,
            theme.border,
            theme.text_primary,
            theme.accent,
            theme.success,
            theme.warning,
            theme.error,
            theme.info,
            theme.agent_dormant,
            theme.agent_active,
            theme.connection_high,
        ]

        for color in colors:
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB
            # Validate hex
            int(color[1:], 16)

    def test_animation_timing(self) -> None:
        """Animation timings are reasonable."""
        theme = DashboardTheme()

        # All timings should be positive
        assert theme.zoom_duration > 0
        assert theme.screen_fade_in > 0
        assert theme.materialize_duration > 0
        assert theme.heartbeat_period > 0

        # Zoom should feel snappy (< 200ms)
        assert theme.zoom_duration < 200

        # Heartbeat should be slow enough to see (> 1s)
        assert theme.heartbeat_period >= 1000

    def test_spacing_values(self) -> None:
        """Spacing values are consistent."""
        theme = DashboardTheme()

        assert theme.padding_small < theme.padding_medium < theme.padding_large
        assert theme.padding_small >= 1
        assert theme.padding_large <= 5

    def test_get_status_color(self) -> None:
        """Semantic status colors work."""
        assert DashboardTheme.get_status_color("success") == "#6bcf7f"
        assert DashboardTheme.get_status_color("error") == "#ff6b6b"
        assert DashboardTheme.get_status_color("warning") == "#ffd93d"
        assert DashboardTheme.get_status_color("pending") == "#ffd93d"

        # Unknown status returns default
        unknown = DashboardTheme.get_status_color("unknown")
        assert unknown.startswith("#")

    def test_get_activity_color(self) -> None:
        """Activity level maps to correct colors."""
        # Dormant (low activity)
        assert DashboardTheme.get_activity_color(0.0) == "#4a4a5c"
        assert DashboardTheme.get_activity_color(0.1) == "#4a4a5c"

        # Waking (medium-low)
        assert DashboardTheme.get_activity_color(0.3) == "#c97b84"

        # Active (medium-high)
        assert DashboardTheme.get_activity_color(0.6) == "#e6a352"

        # Intense (high)
        assert DashboardTheme.get_activity_color(0.9) == "#f5d08a"
        assert DashboardTheme.get_activity_color(1.0) == "#f5d08a"

    def test_get_phase_color(self) -> None:
        """Phase names map to correct colors."""
        assert DashboardTheme.get_phase_color("dormant") == "#4a4a5c"
        assert DashboardTheme.get_phase_color("waking") == "#c97b84"
        assert DashboardTheme.get_phase_color("active") == "#e6a352"
        assert DashboardTheme.get_phase_color("intense") == "#f5d08a"
        assert DashboardTheme.get_phase_color("void") == "#6b4b8a"

        # Case insensitive
        assert DashboardTheme.get_phase_color("ACTIVE") == "#e6a352"
        assert DashboardTheme.get_phase_color("Waking") == "#c97b84"

        # Unknown phase returns default
        unknown = DashboardTheme.get_phase_color("unknown")
        assert unknown == "#4a4a5c"

    def test_generate_css(self) -> None:
        """CSS generation produces valid output."""
        css = DashboardTheme.generate_css()

        # Check for key selectors
        assert "Screen {" in css
        assert ".text-primary" in css
        assert ".status-success" in css
        assert ".agent-dormant" in css
        assert "#header" in css
        assert "#footer" in css

        # Check colors are interpolated
        theme = DashboardTheme()
        assert theme.background in css
        assert theme.accent in css
        assert theme.success in css

    def test_theme_immutability(self) -> None:
        """Theme is frozen (immutable)."""
        theme = DashboardTheme()

        with pytest.raises(Exception):  # FrozenInstanceError or similar
            theme.background = "#000000"  # type: ignore[misc]

    def test_border_styles(self) -> None:
        """Border style constants are defined."""
        theme = DashboardTheme()

        assert theme.border_round == "round"
        assert theme.border_solid == "solid"
        assert theme.border_double == "double"

    def test_yield_state_colors(self) -> None:
        """Yield states have distinct colors."""
        theme = DashboardTheme()

        # Should be different
        assert theme.yield_pending != theme.yield_approved
        assert theme.yield_approved != theme.yield_rejected
        assert theme.yield_pending != theme.yield_rejected

        # Should match status colors
        assert theme.yield_pending == theme.warning
        assert theme.yield_approved == theme.success
        assert theme.yield_rejected == theme.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
