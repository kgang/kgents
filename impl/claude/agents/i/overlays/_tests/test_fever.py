"""
Tests for FeverOverlay and related components.
"""

from __future__ import annotations

import pytest

from agents.i.overlays.fever import (
    EntropyGauge,
    EntropyState,
    FeverOverlay,
    ObliqueDisplay,
    create_fever_overlay,
    should_show_fever_overlay,
)
from protocols.agentese.metabolism.fever import FeverEvent


class TestEntropyState:
    """Tests for EntropyState dataclass."""

    def test_calm_state(self) -> None:
        """Low entropy is calm."""
        state = EntropyState(entropy=0.1)
        assert state.state_name == "calm"
        assert state.state_color == "green"

    def test_warming_state(self) -> None:
        """Medium-low entropy is warming."""
        state = EntropyState(entropy=0.4)
        assert state.state_name == "warming"
        assert state.state_color == "yellow"

    def test_hot_state(self) -> None:
        """Medium-high entropy is hot."""
        state = EntropyState(entropy=0.7)
        assert state.state_name == "hot"
        assert state.state_color == "orange"

    def test_fever_state(self) -> None:
        """High entropy is fever."""
        state = EntropyState(entropy=0.9)
        assert state.state_name == "fever"
        assert state.state_color == "red"

    def test_fever_stream_default(self) -> None:
        """FeverStream is created by default."""
        state = EntropyState(entropy=0.5)
        oblique = state.fever_stream.oblique()
        assert isinstance(oblique, str)
        assert len(oblique) > 0


class TestEntropyGauge:
    """Tests for EntropyGauge widget."""

    def test_render_low_entropy(self) -> None:
        """Low entropy shows calm bar."""
        gauge = EntropyGauge()
        gauge.entropy = 0.1
        rendered = gauge.render()

        assert "10%" in rendered
        assert "calm" in rendered

    def test_render_high_entropy(self) -> None:
        """High entropy shows fever bar."""
        gauge = EntropyGauge()
        gauge.entropy = 0.9
        rendered = gauge.render()

        assert "90%" in rendered
        assert "fever" in rendered

    def test_bar_characters_change(self) -> None:
        """Bar fill character changes with entropy."""
        gauge = EntropyGauge()

        gauge.entropy = 0.2
        low_render = gauge.render()
        assert "█" in low_render

        gauge.entropy = 0.9
        high_render = gauge.render()
        assert "░" in high_render


class TestObliqueDisplay:
    """Tests for ObliqueDisplay widget."""

    def test_render_with_quotes(self) -> None:
        """Strategy is rendered with quotes."""
        display = ObliqueDisplay()
        display.strategy = "Honor thy error as a hidden intention."
        rendered = display.render()

        assert rendered.startswith('"')
        assert rendered.endswith('"')
        assert "Honor thy error" in rendered


class TestFeverOverlay:
    """Tests for FeverOverlay modal."""

    def test_init_with_entropy(self) -> None:
        """Overlay initializes with entropy."""
        overlay = FeverOverlay(entropy=0.8)

        assert overlay.state.entropy == 0.8
        assert overlay.state.state_name == "hot"

    def test_init_with_fever_event(self) -> None:
        """Overlay uses oblique from fever event."""
        event = FeverEvent(
            intensity=0.3,
            timestamp=1000.0,
            trigger="test",
            seed=0.5,
            oblique_strategy="Test strategy",
        )
        overlay = FeverOverlay(entropy=0.9, fever_event=event)

        assert overlay._oblique.strategy == "Test strategy"

    def test_action_draw_oblique(self) -> None:
        """Drawing oblique updates display and history."""
        overlay = FeverOverlay(entropy=0.5)
        initial = overlay._oblique.strategy

        overlay.action_draw_oblique()

        # Strategy may or may not change (random), but history should update
        assert len(overlay.state.history) == 1

    def test_update_entropy(self) -> None:
        """Updating entropy changes state."""
        overlay = FeverOverlay(entropy=0.2)
        assert overlay.state.state_name == "calm"

        overlay.update_entropy(0.9)

        assert overlay.state.entropy == 0.9
        assert overlay.state.state_name == "fever"
        assert overlay._gauge.entropy == 0.9

    def test_title_changes_with_state(self) -> None:
        """Title reflects entropy state."""
        overlay = FeverOverlay(entropy=0.1)
        assert overlay._get_title() == "Entropy Pool"

        overlay.update_entropy(0.9)
        assert overlay._get_title() == "FEVER STATE"


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_fever_overlay(self) -> None:
        """Factory creates overlay with correct entropy."""
        overlay = create_fever_overlay(entropy=0.75)

        assert isinstance(overlay, FeverOverlay)
        assert overlay.state.entropy == 0.75

    def test_should_show_fever_overlay_below_threshold(self) -> None:
        """Below threshold returns False."""
        assert not should_show_fever_overlay(0.5)
        assert not should_show_fever_overlay(0.7)  # Exactly at threshold

    def test_should_show_fever_overlay_above_threshold(self) -> None:
        """Above threshold returns True."""
        assert should_show_fever_overlay(0.71)
        assert should_show_fever_overlay(0.9)
        assert should_show_fever_overlay(1.0)

    def test_should_show_fever_overlay_custom_threshold(self) -> None:
        """Custom threshold is respected."""
        assert should_show_fever_overlay(0.5, threshold=0.4)
        assert not should_show_fever_overlay(0.5, threshold=0.6)
