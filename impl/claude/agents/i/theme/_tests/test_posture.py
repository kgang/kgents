"""Tests for Posture system."""

from __future__ import annotations

import pytest

from ..posture import (
    POSTURE_ANIMATION_FRAMES,
    POSTURE_COLORS,
    POSTURE_DESCRIPTIONS,
    POSTURE_SYMBOLS,
    Posture,
    PostureMapper,
    PostureMode,
    get_posture_for_mode,
    render_posture_with_tooltip,
)


class TestPostureMode:
    """Tests for PostureMode enum."""

    def test_all_modes_exist(self) -> None:
        """Test all expected modes exist."""
        modes = list(PostureMode)
        assert PostureMode.GROUNDING in modes
        assert PostureMode.DELIBERATING in modes
        assert PostureMode.JUDGING in modes
        assert PostureMode.COMPLETE in modes
        assert PostureMode.EXHAUSTED in modes
        assert PostureMode.CONFUSED in modes
        assert PostureMode.YIELDING in modes
        assert PostureMode.IDLE in modes


class TestPostureSymbols:
    """Tests for posture symbol mappings."""

    def test_all_modes_have_symbols(self) -> None:
        """Test all modes have symbols."""
        for mode in PostureMode:
            assert mode in POSTURE_SYMBOLS
            assert len(POSTURE_SYMBOLS[mode]) >= 1

    def test_all_modes_have_colors(self) -> None:
        """Test all modes have colors."""
        for mode in PostureMode:
            assert mode in POSTURE_COLORS
            assert POSTURE_COLORS[mode].startswith("#")

    def test_all_modes_have_descriptions(self) -> None:
        """Test all modes have descriptions."""
        for mode in PostureMode:
            assert mode in POSTURE_DESCRIPTIONS
            assert len(POSTURE_DESCRIPTIONS[mode]) > 0

    def test_all_modes_have_animation_frames(self) -> None:
        """Test all modes have animation frames."""
        for mode in PostureMode:
            assert mode in POSTURE_ANIMATION_FRAMES
            assert len(POSTURE_ANIMATION_FRAMES[mode]) >= 2


class TestPosture:
    """Tests for Posture dataclass."""

    def test_from_mode_enum(self) -> None:
        """Test creating posture from enum mode."""
        posture = Posture.from_mode(PostureMode.DELIBERATING)
        assert posture.mode == PostureMode.DELIBERATING
        assert posture.symbol == POSTURE_SYMBOLS[PostureMode.DELIBERATING]
        assert posture.color == POSTURE_COLORS[PostureMode.DELIBERATING]

    def test_from_mode_string(self) -> None:
        """Test creating posture from string mode."""
        posture = Posture.from_mode("JUDGING")
        assert posture.mode == PostureMode.JUDGING

    def test_from_mode_invalid_string(self) -> None:
        """Test invalid string defaults to IDLE."""
        posture = Posture.from_mode("INVALID_MODE")
        assert posture.mode == PostureMode.IDLE

    def test_confidence(self) -> None:
        """Test posture with confidence."""
        posture = Posture.from_mode(PostureMode.GROUNDING, confidence=0.8)
        assert posture.confidence == 0.8
        assert posture.animation_speed > 0

    def test_get_frame(self) -> None:
        """Test getting animation frame."""
        posture = Posture.from_mode(PostureMode.DELIBERATING, animated=True)
        frame0 = posture.get_frame(0)
        frame1 = posture.get_frame(1)

        assert isinstance(frame0, str)
        assert isinstance(frame1, str)
        # Frames should cycle
        frames = posture.animation_frames
        assert frames is not None
        assert posture.get_frame(100) == posture.get_frame(100 % len(frames))

    def test_get_frame_not_animated(self) -> None:
        """Test getting frame when not animated."""
        posture = Posture.from_mode(PostureMode.COMPLETE, animated=False)
        frame = posture.get_frame(0)
        assert frame == posture.symbol

    def test_with_confidence(self) -> None:
        """Test creating copy with updated confidence."""
        posture = Posture.from_mode(PostureMode.GROUNDING, confidence=0.5)
        updated = posture.with_confidence(0.9)

        assert updated.confidence == 0.9
        assert updated.mode == posture.mode
        assert posture.confidence == 0.5  # Original unchanged


class TestPostureMapper:
    """Tests for PostureMapper."""

    def test_create(self) -> None:
        """Test mapper creation."""
        mapper = PostureMapper()
        assert mapper.confidence_threshold == 0.3

    def test_from_polynomial_state_grounding(self) -> None:
        """Test mapping GROUNDING mode."""
        mapper = PostureMapper()
        posture = mapper.from_polynomial_state("GROUNDING", confidence=0.8)
        assert posture.mode == PostureMode.GROUNDING

    def test_from_polynomial_state_deliberating(self) -> None:
        """Test mapping DELIBERATING mode."""
        mapper = PostureMapper()
        posture = mapper.from_polynomial_state("DELIBERATING", confidence=0.8)
        assert posture.mode == PostureMode.DELIBERATING

    def test_from_polynomial_state_exhausted(self) -> None:
        """Test low confidence results in EXHAUSTED."""
        mapper = PostureMapper()
        posture = mapper.from_polynomial_state("GROUNDING", confidence=0.1)
        assert posture.mode == PostureMode.EXHAUSTED

    def test_from_polynomial_state_yielding(self) -> None:
        """Test APPROVE in inputs results in YIELDING."""
        mapper = PostureMapper()
        posture = mapper.from_polynomial_state(
            "GROUNDING", confidence=0.8, valid_inputs=["APPROVE", "REJECT"]
        )
        assert posture.mode == PostureMode.YIELDING

    def test_from_phase_dormant(self) -> None:
        """Test mapping DORMANT phase."""
        mapper = PostureMapper()
        posture = mapper.from_phase("DORMANT", activity=0.1)
        assert posture.mode == PostureMode.IDLE

    def test_from_phase_active(self) -> None:
        """Test mapping ACTIVE phase."""
        mapper = PostureMapper()
        posture = mapper.from_phase("ACTIVE", activity=0.8)
        assert posture.mode == PostureMode.DELIBERATING

    def test_from_phase_void(self) -> None:
        """Test mapping VOID phase."""
        mapper = PostureMapper()
        posture = mapper.from_phase("VOID", activity=0.5)
        assert posture.mode == PostureMode.CONFUSED


class TestGetPostureForMode:
    """Tests for get_posture_for_mode helper."""

    def test_polynomial_mode(self) -> None:
        """Test with polynomial mode."""
        posture = get_posture_for_mode("JUDGING")
        assert posture.mode == PostureMode.JUDGING

    def test_phase_mode(self) -> None:
        """Test with phase mode."""
        posture = get_posture_for_mode("WAKING")
        assert posture.mode == PostureMode.GROUNDING

    def test_unknown_mode(self) -> None:
        """Test unknown mode defaults to IDLE."""
        posture = get_posture_for_mode("UNKNOWN_XYZ")
        assert posture.mode == PostureMode.IDLE

    def test_with_confidence(self) -> None:
        """Test with confidence parameter."""
        posture = get_posture_for_mode("DELIBERATING", confidence=0.7)
        assert posture.confidence == 0.7


class TestRenderPostureWithTooltip:
    """Tests for render_posture_with_tooltip helper."""

    def test_without_tooltip(self) -> None:
        """Test rendering without tooltip."""
        posture = Posture.from_mode(PostureMode.COMPLETE)
        rendered = render_posture_with_tooltip(posture, show_tooltip=False)

        assert posture.symbol in rendered
        assert "[" in rendered  # Has color formatting
        assert posture.description not in rendered

    def test_with_tooltip(self) -> None:
        """Test rendering with tooltip."""
        posture = Posture.from_mode(PostureMode.DELIBERATING)
        rendered = render_posture_with_tooltip(posture, show_tooltip=True)

        assert posture.symbol in rendered
        assert posture.description in rendered
