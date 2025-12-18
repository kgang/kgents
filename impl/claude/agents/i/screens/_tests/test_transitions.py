"""Tests for the Gentle Eye transition system.

Philosophy verification:
    - Transitions encode semantic meaning
    - No jarring or violent screen changes
    - Anchor points and stagger delays work correctly
    - LOD changes map to appropriate transitions
"""

import pytest

from agents.i.screens.transitions import (
    GentleNavigator,
    ScreenTransition,
    TransitionStyle,
)


class TestTransitionStyle:
    """Test TransitionStyle enum values."""

    def test_all_styles_defined(self) -> None:
        """All expected transition styles should be defined."""
        assert TransitionStyle.CROSSFADE.value == "crossfade"
        assert TransitionStyle.SLIDE_LEFT.value == "slide_left"
        assert TransitionStyle.SLIDE_RIGHT.value == "slide_right"
        assert TransitionStyle.MORPH.value == "morph"

    def test_enum_membership(self) -> None:
        """All styles should be accessible via enum."""
        styles = {style.value for style in TransitionStyle}
        assert styles == {"crossfade", "slide_left", "slide_right", "morph"}


class TestScreenTransition:
    """Test ScreenTransition dataclass."""

    def test_default_transition(self) -> None:
        """Default transition should be crossfade with 200ms duration."""
        transition = ScreenTransition()
        assert transition.style == TransitionStyle.CROSSFADE
        assert transition.duration_ms == 200
        assert transition.anchor_element is None
        assert transition.stagger_ms == 50

    def test_duration_seconds_conversion(self) -> None:
        """Should correctly convert milliseconds to seconds."""
        transition = ScreenTransition(duration_ms=250)
        assert transition.duration_seconds == 0.25

        transition = ScreenTransition(duration_ms=1000)
        assert transition.duration_seconds == 1.0

    def test_custom_transition(self) -> None:
        """Should support custom transition parameters."""
        transition = ScreenTransition(
            style=TransitionStyle.SLIDE_LEFT,
            duration_ms=300,
            anchor_element="header",
            stagger_ms=100,
        )
        assert transition.style == TransitionStyle.SLIDE_LEFT
        assert transition.duration_ms == 300
        assert transition.anchor_element == "header"
        assert transition.stagger_ms == 100

    def test_with_anchor(self) -> None:
        """Should create new transition with anchor element."""
        original = ScreenTransition(style=TransitionStyle.MORPH, duration_ms=250)
        with_anchor = original.with_anchor("spotlight")

        assert with_anchor.anchor_element == "spotlight"
        assert with_anchor.style == TransitionStyle.MORPH
        assert with_anchor.duration_ms == 250
        assert original.anchor_element is None  # Original unchanged

    def test_with_duration(self) -> None:
        """Should create new transition with different duration."""
        original = ScreenTransition(
            style=TransitionStyle.SLIDE_RIGHT,
            anchor_element="footer",
        )
        faster = original.with_duration(100)

        assert faster.duration_ms == 100
        assert faster.style == TransitionStyle.SLIDE_RIGHT
        assert faster.anchor_element == "footer"
        assert original.duration_ms == 200  # Original unchanged

    def test_negative_duration_raises(self) -> None:
        """Negative duration should raise ValueError."""
        with pytest.raises(ValueError, match="Duration must be non-negative"):
            ScreenTransition(duration_ms=-100)

    def test_negative_stagger_raises(self) -> None:
        """Negative stagger should raise ValueError."""
        with pytest.raises(ValueError, match="Stagger must be non-negative"):
            ScreenTransition(stagger_ms=-50)

    def test_immutability(self) -> None:
        """ScreenTransition should be frozen/immutable."""
        transition = ScreenTransition()
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            transition.duration_ms = 500  # type: ignore


class TestGentleNavigator:
    """Test GentleNavigator for semantic transitions."""

    def test_class_constants(self) -> None:
        """Class should define expected transition constants."""
        assert GentleNavigator.LOD_DOWN_TRANSITION.style == TransitionStyle.SLIDE_LEFT
        assert GentleNavigator.LOD_UP_TRANSITION.style == TransitionStyle.SLIDE_RIGHT
        assert GentleNavigator.PEER_TRANSITION.style == TransitionStyle.CROSSFADE
        assert GentleNavigator.MORPH_TRANSITION.style == TransitionStyle.MORPH

    def test_lod_down_transition(self) -> None:
        """Drilling down should use slide left."""
        nav = GentleNavigator()
        transition = nav.get_transition_for_lod_change(old_lod=0, new_lod=1)
        assert transition.style == TransitionStyle.SLIDE_LEFT

        transition = nav.get_transition_for_lod_change(old_lod=1, new_lod=2)
        assert transition.style == TransitionStyle.SLIDE_LEFT

    def test_lod_up_transition(self) -> None:
        """Zooming out should use slide right."""
        nav = GentleNavigator()
        transition = nav.get_transition_for_lod_change(old_lod=2, new_lod=1)
        assert transition.style == TransitionStyle.SLIDE_RIGHT

        transition = nav.get_transition_for_lod_change(old_lod=1, new_lod=0)
        assert transition.style == TransitionStyle.SLIDE_RIGHT

    def test_peer_transition(self) -> None:
        """Same LOD should use crossfade."""
        nav = GentleNavigator()
        transition = nav.get_transition_for_lod_change(old_lod=0, new_lod=0)
        assert transition.style == TransitionStyle.CROSSFADE

        transition = nav.get_transition_for_lod_change(old_lod=1, new_lod=1)
        assert transition.style == TransitionStyle.CROSSFADE

    def test_get_transition_for_screens_strategy_to_tactical(self) -> None:
        """Strategy to tactical should slide left."""
        nav = GentleNavigator()
        transition = nav.get_transition_for_screens("cockpit", "flux")
        assert transition.style == TransitionStyle.SLIDE_LEFT

        transition = nav.get_transition_for_screens("observatory", "mri")
        assert transition.style == TransitionStyle.SLIDE_LEFT

    def test_get_transition_for_screens_tactical_to_forensic(self) -> None:
        """Tactical to forensic should slide left."""
        nav = GentleNavigator()
        transition = nav.get_transition_for_screens("flux", "debugger")
        assert transition.style == TransitionStyle.SLIDE_LEFT

    def test_get_transition_for_screens_forensic_to_tactical(self) -> None:
        """Forensic to tactical should slide right."""
        nav = GentleNavigator()
        transition = nav.get_transition_for_screens("debugger", "flux")
        assert transition.style == TransitionStyle.SLIDE_RIGHT

    def test_get_transition_for_screens_peer_navigation(self) -> None:
        """Peer navigation should crossfade."""
        nav = GentleNavigator()
        # Both tactical level
        transition = nav.get_transition_for_screens("flux", "mri")
        assert transition.style == TransitionStyle.CROSSFADE

        # Both strategy level
        transition = nav.get_transition_for_screens("cockpit", "observatory")
        assert transition.style == TransitionStyle.CROSSFADE

    def test_get_transition_for_screens_unknown_defaults_to_tactical(self) -> None:
        """Unknown screens should default to tactical (LOD 1)."""
        nav = GentleNavigator()
        # Both unknown -> same LOD -> crossfade
        transition = nav.get_transition_for_screens("unknown_a", "unknown_b")
        assert transition.style == TransitionStyle.CROSSFADE

    def test_get_instant_transition(self) -> None:
        """Instant transition should have 0ms duration."""
        nav = GentleNavigator()
        instant = nav.get_instant_transition()
        assert instant.duration_ms == 0
        assert instant.style == TransitionStyle.CROSSFADE
        assert instant.duration_seconds == 0.0
