"""
Tests for Projection Functor Law Verification.

Test Categories:
    1. Identity Law - project(id(state)) ≡ project(state)
    2. Composition Law - Composed transformations project correctly
    3. Determinism - Same state → same output
    4. Comprehensive - verify_all_laws() function
    5. Error Handling - ProjectionLawError behavior
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from agents.i.reactive.projection import (
    ExtendedTarget,
    ProjectionLawError,
    verify_all_laws,
    verify_composition_law,
    verify_determinism,
    verify_identity_law,
)
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass(frozen=True)
class CounterState:
    """Counter state for law testing."""

    count: int = 0
    label: str = "counter"


class CounterWidget(KgentsWidget[CounterState]):
    """Counter widget that follows projection laws."""

    def __init__(self, initial: CounterState | None = None) -> None:
        self.state = Signal.of(initial or CounterState())

    def project(self, target: RenderTarget) -> Any:
        s = self.state.value
        match target:
            case RenderTarget.CLI:
                return f"{s.label}: {s.count}"
            case RenderTarget.JSON:
                return {"label": s.label, "count": s.count}
            case _:
                return f"{s.label}={s.count}"


@dataclass(frozen=True)
class NonDeterministicState:
    """State that includes randomness for testing violations."""

    value: int = 0


class NonDeterministicWidget(KgentsWidget[NonDeterministicState]):
    """Widget that violates determinism law (for testing detection)."""

    def __init__(self) -> None:
        self.state = Signal.of(NonDeterministicState())
        self._call_count = 0

    def project(self, target: RenderTarget) -> Any:
        self._call_count += 1
        # Bug: output depends on call count, not just state
        return f"output-{self._call_count}"


# =============================================================================
# Identity Law Tests
# =============================================================================


class TestIdentityLaw:
    """Tests for the identity functor law."""

    def test_counter_identity_cli(self) -> None:
        """CounterWidget satisfies identity law for CLI."""
        widget = CounterWidget(CounterState(count=5))
        assert verify_identity_law(widget, ExtendedTarget.CLI)

    def test_counter_identity_json(self) -> None:
        """CounterWidget satisfies identity law for JSON."""
        widget = CounterWidget(CounterState(count=10))
        assert verify_identity_law(widget, ExtendedTarget.JSON)

    def test_counter_identity_string_target(self) -> None:
        """Can use string target names."""
        widget = CounterWidget()
        assert verify_identity_law(widget, "cli")

    def test_identity_law_different_states(self) -> None:
        """Identity holds for various states."""
        for count in [0, 1, -1, 100, 999999]:
            widget = CounterWidget(CounterState(count=count))
            assert verify_identity_law(widget, ExtendedTarget.CLI)

    def test_identity_law_violation_detected(self) -> None:
        """Violations of identity law are detected."""
        widget = NonDeterministicWidget()
        assert not verify_identity_law(widget, ExtendedTarget.CLI)

    def test_identity_law_raises_on_failure(self) -> None:
        """raise_on_failure=True raises ProjectionLawError."""
        widget = NonDeterministicWidget()
        with pytest.raises(ProjectionLawError) as exc_info:
            verify_identity_law(widget, ExtendedTarget.CLI, raise_on_failure=True)

        assert exc_info.value.law == "identity"
        assert "NonDeterministicWidget" in exc_info.value.widget_type


# =============================================================================
# Composition Law Tests
# =============================================================================


class TestCompositionLaw:
    """Tests for the composition functor law."""

    def test_composition_with_identity_transforms(self) -> None:
        """Composition holds with identity transformations."""

        def identity(s: CounterState) -> CounterState:
            return s

        widget = CounterWidget(CounterState(count=5))
        assert verify_composition_law(widget, identity, identity, ExtendedTarget.CLI)

    def test_composition_with_increment(self) -> None:
        """Composition holds with increment transformation."""

        def increment(s: CounterState) -> CounterState:
            return CounterState(count=s.count + 1, label=s.label)

        def identity(s: CounterState) -> CounterState:
            return s

        widget = CounterWidget(CounterState(count=0))
        assert verify_composition_law(widget, increment, identity, ExtendedTarget.CLI)

    def test_composition_with_chained_transforms(self) -> None:
        """Composition holds with multiple transformations."""

        def double(s: CounterState) -> CounterState:
            return CounterState(count=s.count * 2, label=s.label)

        def add_ten(s: CounterState) -> CounterState:
            return CounterState(count=s.count + 10, label=s.label)

        widget = CounterWidget(CounterState(count=5))
        # double(add_ten(5)) = double(15) = 30
        assert verify_composition_law(widget, double, add_ten, ExtendedTarget.CLI)

    def test_composition_restores_original_state(self) -> None:
        """Widget state is restored after composition test."""
        original = CounterState(count=42, label="original")
        widget = CounterWidget(original)

        def increment(s: CounterState) -> CounterState:
            return CounterState(count=s.count + 1, label=s.label)

        verify_composition_law(widget, increment, increment, ExtendedTarget.CLI)

        # State should be restored
        assert widget.state.value == original


# =============================================================================
# Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests for projection determinism."""

    def test_determinism_with_good_widget(self) -> None:
        """Deterministic widget passes determinism check."""
        widget = CounterWidget(CounterState(count=100))
        assert verify_determinism(widget, ExtendedTarget.CLI, iterations=20)

    def test_determinism_detects_violation(self) -> None:
        """Non-deterministic widget fails determinism check."""
        widget = NonDeterministicWidget()
        assert not verify_determinism(widget, ExtendedTarget.CLI, iterations=5)

    def test_determinism_raises_on_failure(self) -> None:
        """raise_on_failure=True raises ProjectionLawError for determinism."""
        widget = NonDeterministicWidget()
        with pytest.raises(ProjectionLawError) as exc_info:
            verify_determinism(widget, ExtendedTarget.CLI, raise_on_failure=True)

        assert exc_info.value.law == "determinism"

    def test_determinism_single_iteration_always_passes(self) -> None:
        """Single iteration can't detect non-determinism (edge case)."""
        widget = NonDeterministicWidget()
        # With only 1 iteration, no comparison is made
        assert verify_determinism(widget, ExtendedTarget.CLI, iterations=1)


# =============================================================================
# Comprehensive Law Verification Tests
# =============================================================================


class TestVerifyAllLaws:
    """Tests for verify_all_laws() comprehensive check."""

    def test_all_laws_pass_for_good_widget(self) -> None:
        """Good widget passes all laws."""

        def increment(s: CounterState) -> CounterState:
            return CounterState(count=s.count + 1, label=s.label)

        widget = CounterWidget(CounterState(count=0))
        result = verify_all_laws(
            widget,
            ExtendedTarget.CLI,
            state_transforms=[increment, increment],
        )

        assert result.all_passed
        assert result.identity
        assert result.composition
        assert result.determinism
        assert len(result.errors) == 0

    def test_all_laws_without_transforms(self) -> None:
        """verify_all_laws() works without state transforms."""
        widget = CounterWidget()
        result = verify_all_laws(widget, ExtendedTarget.CLI)

        assert result.identity
        assert result.determinism
        assert result.composition is None  # Not tested
        assert result.all_passed  # None composition doesn't fail

    def test_all_laws_captures_identity_failure(self) -> None:
        """verify_all_laws() captures identity law failures."""
        widget = NonDeterministicWidget()
        result = verify_all_laws(widget, ExtendedTarget.CLI)

        assert not result.identity
        assert not result.all_passed
        assert any("Identity" in e for e in result.errors)

    def test_all_laws_captures_determinism_failure(self) -> None:
        """verify_all_laws() captures determinism failures."""
        widget = NonDeterministicWidget()
        result = verify_all_laws(widget, ExtendedTarget.CLI)

        assert not result.determinism
        assert any("Determinism" in e for e in result.errors)


# =============================================================================
# Error Message Tests
# =============================================================================


class TestProjectionLawError:
    """Tests for ProjectionLawError formatting."""

    def test_error_message_format(self) -> None:
        """Error message includes all relevant information."""
        error = ProjectionLawError(
            law="identity",
            expected="foo",
            actual="bar",
            target=ExtendedTarget.CLI,
            widget_type="TestWidget",
        )

        msg = str(error)
        assert "identity" in msg
        assert "CLI" in msg or "ExtendedTarget.CLI" in msg
        assert "TestWidget" in msg
        assert "foo" in msg
        assert "bar" in msg

    def test_error_attributes(self) -> None:
        """Error has expected attributes."""
        error = ProjectionLawError(
            law="composition",
            expected={"a": 1},
            actual={"a": 2},
            target="json",
            widget_type="ComplexWidget",
        )

        assert error.law == "composition"
        assert error.expected == {"a": 1}
        assert error.actual == {"a": 2}
        assert error.target == "json"
        assert error.widget_type == "ComplexWidget"


# =============================================================================
# Integration with Real Widgets
# =============================================================================


class TestRealWidgetLaws:
    """Tests using real kgents widgets to verify law compliance."""

    def test_glyph_widget_laws(self) -> None:
        """GlyphWidget satisfies projection laws."""
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        widget = GlyphWidget(GlyphState(char="X", phase="active"))

        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_identity_law(widget, ExtendedTarget.JSON)
        assert verify_determinism(widget, ExtendedTarget.CLI)

    def test_glyph_composition_law(self) -> None:
        """GlyphWidget satisfies composition law."""
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        def set_error(s: GlyphState) -> GlyphState:
            return GlyphState(
                char=s.char,
                fg=s.fg,
                bg=s.bg,
                phase="error",
                entropy=s.entropy,
                seed=s.seed,
                t=s.t,
                animate=s.animate,
            )

        def identity(s: GlyphState) -> GlyphState:
            return s

        widget = GlyphWidget(GlyphState(char="O", phase="idle"))
        assert verify_composition_law(widget, set_error, identity, ExtendedTarget.CLI)

    def test_bar_widget_laws(self) -> None:
        """BarWidget satisfies projection laws."""
        from agents.i.reactive.primitives.bar import BarState, BarWidget

        widget = BarWidget(BarState(value=0.5, width=10))

        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.JSON)

    def test_sparkline_widget_laws(self) -> None:
        """SparklineWidget satisfies projection laws."""
        from agents.i.reactive.primitives.sparkline import (
            SparklineState,
            SparklineWidget,
        )

        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9, 0.3)))

        assert verify_identity_law(widget, ExtendedTarget.CLI)
        assert verify_determinism(widget, ExtendedTarget.CLI)
