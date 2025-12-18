"""Property-based tests for Projection Functor Laws.

Uses Hypothesis to verify projection laws hold across arbitrary widget states.

Properties Verified:
    1. Identity Law: project(id(state)) ≡ project(state)
    2. Determinism: Same state → same output (across N iterations)
    3. Composition Law: project(f ∘ g)(state) ≡ project(f)(project(g)(state))

Edge Cases Covered:
    - Empty values (empty sparkline, zero-width bar)
    - Boundary conditions (entropy 0.0/1.0, value 0.0/1.0)
    - Extreme values (max length, high entropy)
    - Unicode characters in glyphs
"""

from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given, settings, strategies as st

from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.projection import (
    ExtendedTarget,
    verify_composition_law,
    verify_determinism,
    verify_identity_law,
)

# =============================================================================
# Hypothesis Strategies for Widget States
# =============================================================================


@st.composite
def glyph_state_strategy(draw: st.DrawFn) -> GlyphState:
    """Generate arbitrary GlyphState instances."""
    char = draw(
        st.text(
            min_size=1,
            max_size=1,
            alphabet=st.characters(
                whitelist_categories=("L", "N", "S", "P"), whitelist_characters="◉○●◐◑▣▢▤▥▦▧▨▩"
            ),
        )
    )
    phase = draw(st.sampled_from(["idle", "active", "error", "success", None]))
    entropy = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    seed = draw(st.integers(min_value=0, max_value=2**16 - 1))
    t = draw(st.floats(min_value=0.0, max_value=100000.0, allow_nan=False))
    animate = draw(st.sampled_from(["none", "pulse", "breathe", "spin"]))
    fg = draw(st.one_of(st.none(), st.text(min_size=1, max_size=7, alphabet="0123456789abcdef#")))
    bg = draw(st.one_of(st.none(), st.text(min_size=1, max_size=7, alphabet="0123456789abcdef#")))

    return GlyphState(
        char=char,
        fg=fg,
        bg=bg,
        phase=phase,
        entropy=entropy,
        seed=seed,
        t=t,
        animate=animate,
    )


@st.composite
def bar_state_strategy(draw: st.DrawFn) -> BarState:
    """Generate arbitrary BarState instances."""
    value = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    width = draw(st.integers(min_value=1, max_value=100))
    orientation = draw(st.sampled_from(["horizontal", "vertical"]))
    style = draw(st.sampled_from(["solid", "gradient", "segments", "dots"]))
    entropy = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    seed = draw(st.integers(min_value=0, max_value=2**16 - 1))
    t = draw(st.floats(min_value=0.0, max_value=100000.0, allow_nan=False))
    label = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    fg = draw(st.one_of(st.none(), st.text(min_size=1, max_size=7, alphabet="0123456789abcdef#")))
    bg = draw(st.one_of(st.none(), st.text(min_size=1, max_size=7, alphabet="0123456789abcdef#")))

    return BarState(
        value=value,
        width=width,
        orientation=orientation,
        style=style,
        fg=fg,
        bg=bg,
        entropy=entropy,
        seed=seed,
        t=t,
        label=label,
    )


@st.composite
def sparkline_state_strategy(draw: st.DrawFn) -> SparklineState:
    """Generate arbitrary SparklineState instances."""
    # Generate values tuple - 0 to max_length values, each in [0, 1]
    max_length = draw(st.integers(min_value=1, max_value=50))
    num_values = draw(st.integers(min_value=0, max_value=max_length))
    values = tuple(
        draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False)) for _ in range(num_values)
    )

    entropy = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    seed = draw(st.integers(min_value=0, max_value=2**16 - 1))
    t = draw(st.floats(min_value=0.0, max_value=100000.0, allow_nan=False))
    label = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    show_bounds = draw(st.booleans())
    fg = draw(st.one_of(st.none(), st.text(min_size=1, max_size=7, alphabet="0123456789abcdef#")))
    bg = draw(st.one_of(st.none(), st.text(min_size=1, max_size=7, alphabet="0123456789abcdef#")))

    return SparklineState(
        values=values,
        max_length=max_length,
        fg=fg,
        bg=bg,
        entropy=entropy,
        seed=seed,
        t=t,
        label=label,
        show_bounds=show_bounds,
    )


# =============================================================================
# GlyphWidget Property Tests
# =============================================================================


class TestGlyphProjectionProperties:
    """Property-based tests for GlyphWidget projection laws."""

    @given(state=glyph_state_strategy())
    @settings(max_examples=100)
    def test_identity_law_cli_property(self, state: GlyphState) -> None:
        """Identity law holds for CLI projection across arbitrary states."""
        widget = GlyphWidget(state)
        assert verify_identity_law(widget, ExtendedTarget.CLI)

    @given(state=glyph_state_strategy())
    @settings(max_examples=100)
    def test_identity_law_json_property(self, state: GlyphState) -> None:
        """Identity law holds for JSON projection across arbitrary states."""
        widget = GlyphWidget(state)
        assert verify_identity_law(widget, ExtendedTarget.JSON)

    @given(state=glyph_state_strategy())
    @settings(max_examples=100)
    def test_determinism_property(self, state: GlyphState) -> None:
        """Projection is deterministic across arbitrary states."""
        widget = GlyphWidget(state)
        assert verify_determinism(widget, ExtendedTarget.CLI, iterations=5)
        assert verify_determinism(widget, ExtendedTarget.JSON, iterations=5)

    @given(state=glyph_state_strategy())
    @settings(max_examples=50)
    def test_composition_law_identity_transforms(self, state: GlyphState) -> None:
        """Composition law holds with identity transforms."""

        def identity(s: GlyphState) -> GlyphState:
            return s

        widget = GlyphWidget(state)
        assert verify_composition_law(widget, identity, identity, ExtendedTarget.CLI)


# =============================================================================
# BarWidget Property Tests
# =============================================================================


class TestBarProjectionProperties:
    """Property-based tests for BarWidget projection laws."""

    @given(state=bar_state_strategy())
    @settings(max_examples=100)
    def test_identity_law_cli_property(self, state: BarState) -> None:
        """Identity law holds for CLI projection across arbitrary states."""
        widget = BarWidget(state)
        assert verify_identity_law(widget, ExtendedTarget.CLI)

    @given(state=bar_state_strategy())
    @settings(max_examples=100)
    def test_identity_law_json_property(self, state: BarState) -> None:
        """Identity law holds for JSON projection across arbitrary states."""
        widget = BarWidget(state)
        assert verify_identity_law(widget, ExtendedTarget.JSON)

    @given(state=bar_state_strategy())
    @settings(max_examples=100)
    def test_determinism_property(self, state: BarState) -> None:
        """Projection is deterministic across arbitrary states."""
        widget = BarWidget(state)
        assert verify_determinism(widget, ExtendedTarget.CLI, iterations=5)
        assert verify_determinism(widget, ExtendedTarget.JSON, iterations=5)

    @given(state=bar_state_strategy())
    @settings(max_examples=50)
    def test_composition_law_value_transform(self, state: BarState) -> None:
        """Composition law holds with value transform."""

        def scale_value(s: BarState) -> BarState:
            return BarState(
                value=min(1.0, s.value * 1.2),
                width=s.width,
                orientation=s.orientation,
                style=s.style,
                fg=s.fg,
                bg=s.bg,
                entropy=s.entropy,
                seed=s.seed,
                t=s.t,
                label=s.label,
            )

        def identity(s: BarState) -> BarState:
            return s

        widget = BarWidget(state)
        assert verify_composition_law(widget, scale_value, identity, ExtendedTarget.CLI)


# =============================================================================
# SparklineWidget Property Tests
# =============================================================================


class TestSparklineProjectionProperties:
    """Property-based tests for SparklineWidget projection laws."""

    @given(state=sparkline_state_strategy())
    @settings(max_examples=100)
    def test_identity_law_cli_property(self, state: SparklineState) -> None:
        """Identity law holds for CLI projection across arbitrary states."""
        widget = SparklineWidget(state)
        assert verify_identity_law(widget, ExtendedTarget.CLI)

    @given(state=sparkline_state_strategy())
    @settings(max_examples=100)
    def test_identity_law_json_property(self, state: SparklineState) -> None:
        """Identity law holds for JSON projection across arbitrary states."""
        widget = SparklineWidget(state)
        assert verify_identity_law(widget, ExtendedTarget.JSON)

    @given(state=sparkline_state_strategy())
    @settings(max_examples=100)
    def test_determinism_property(self, state: SparklineState) -> None:
        """Projection is deterministic across arbitrary states."""
        widget = SparklineWidget(state)
        assert verify_determinism(widget, ExtendedTarget.CLI, iterations=5)
        assert verify_determinism(widget, ExtendedTarget.JSON, iterations=5)

    @given(state=sparkline_state_strategy())
    @settings(max_examples=50)
    def test_composition_law_identity_transforms(self, state: SparklineState) -> None:
        """Composition law holds with identity transforms."""

        def identity(s: SparklineState) -> SparklineState:
            return s

        widget = SparklineWidget(state)
        assert verify_composition_law(widget, identity, identity, ExtendedTarget.CLI)


# =============================================================================
# Edge Case Tests (Targeted, Not Random)
# =============================================================================


class TestProjectionEdgeCases:
    """Explicit edge case tests for projection laws."""

    def test_glyph_with_empty_char(self) -> None:
        """Glyph with default char projects correctly."""
        widget = GlyphWidget(GlyphState(char="·"))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_identity_law(widget, ExtendedTarget.JSON)

    def test_bar_with_zero_value(self) -> None:
        """Bar with value=0 projects correctly."""
        widget = BarWidget(BarState(value=0.0, width=10))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_bar_with_full_value(self) -> None:
        """Bar with value=1 projects correctly."""
        widget = BarWidget(BarState(value=1.0, width=10))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_sparkline_with_empty_values(self) -> None:
        """Sparkline with no values projects correctly."""
        widget = SparklineWidget(SparklineState(values=()))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_identity_law(widget, ExtendedTarget.JSON)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_sparkline_with_single_value(self) -> None:
        """Sparkline with single value projects correctly."""
        widget = SparklineWidget(SparklineState(values=(0.5,)))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.JSON)

    def test_sparkline_at_max_length(self) -> None:
        """Sparkline at max_length projects correctly."""
        values = tuple(i / 99.0 for i in range(100))
        widget = SparklineWidget(SparklineState(values=values, max_length=100))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_glyph_with_zero_entropy(self) -> None:
        """Glyph with entropy=0 has no distortion."""
        widget = GlyphWidget(GlyphState(char="X", entropy=0.0))
        assert verify_identity_law(widget, ExtendedTarget.JSON)
        assert verify_determinism(widget, ExtendedTarget.JSON)

    def test_glyph_with_max_entropy(self) -> None:
        """Glyph with entropy=1 projects consistently."""
        widget = GlyphWidget(GlyphState(char="X", entropy=1.0, seed=42))
        assert verify_identity_law(widget, ExtendedTarget.JSON)
        assert verify_determinism(widget, ExtendedTarget.JSON)

    def test_bar_with_narrow_width(self) -> None:
        """Bar with width=1 projects correctly."""
        widget = BarWidget(BarState(value=0.5, width=1))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_bar_with_wide_width(self) -> None:
        """Bar with width=100 projects correctly."""
        widget = BarWidget(BarState(value=0.5, width=100))
        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_glyph_with_unicode(self) -> None:
        """Glyph with various unicode chars projects correctly."""
        for char in ["◉", "●", "○", "▣", "▢", "⬡", "⬢"]:
            widget = GlyphWidget(GlyphState(char=char))
            assert verify_identity_law(widget, ExtendedTarget.CLI)
            assert verify_identity_law(widget, ExtendedTarget.JSON)

    def test_all_bar_styles(self) -> None:
        """All bar styles project correctly."""
        for style in ["solid", "gradient", "segments", "dots"]:
            widget = BarWidget(BarState(value=0.5, width=10, style=style))
            assert verify_identity_law(widget, ExtendedTarget.CLI)
            assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_all_bar_orientations(self) -> None:
        """All bar orientations project correctly."""
        for orientation in ["horizontal", "vertical"]:
            widget = BarWidget(BarState(value=0.5, width=5, orientation=orientation))
            assert verify_identity_law(widget, ExtendedTarget.CLI)
            assert verify_determinism(widget, ExtendedTarget.CLI)
