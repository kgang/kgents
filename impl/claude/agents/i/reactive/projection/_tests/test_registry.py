"""
Tests for ProjectionRegistry.

Test Categories:
    1. Registration - Decorator-based target registration
    2. Lookup - Target lookup with graceful degradation
    3. Built-ins - Core targets (CLI, TUI, MARIMO, JSON, SSE)
    4. Custom - Custom target registration and use
    5. Fidelity - Fidelity-based target selection
    6. Isolation - Registry reset for test isolation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest
from agents.i.reactive.projection import (
    ExtendedTarget,
    FidelityLevel,
    ProjectionRegistry,
    Projector,
)

if TYPE_CHECKING:
    from collections.abc import Generator
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass(frozen=True)
class SimpleState:
    """Simple state for testing."""

    value: int = 42
    label: str = "test"


class SimpleWidget(KgentsWidget[SimpleState]):
    """Simple widget for testing projections."""

    def __init__(self, state: SimpleState | None = None) -> None:
        self.state = Signal.of(state or SimpleState())

    def project(self, target: RenderTarget) -> Any:
        s = self.state.value
        match target:
            case RenderTarget.CLI:
                return f"[{s.label}] {s.value}"
            case RenderTarget.TUI:
                return f"TUI: {s.label} = {s.value}"
            case RenderTarget.MARIMO:
                return f"<span>{s.label}: {s.value}</span>"
            case RenderTarget.JSON:
                return {"label": s.label, "value": s.value}


@pytest.fixture(autouse=True)
def reset_registry() -> "Generator[None, None, None]":
    """Reset registry before and after each test for isolation."""
    ProjectionRegistry.reset()
    yield
    ProjectionRegistry.reset()


# =============================================================================
# Registration Tests
# =============================================================================


class TestRegistration:
    """Tests for decorator-based target registration."""

    def test_register_custom_target(self) -> None:
        """Custom targets can be registered via decorator."""

        @ProjectionRegistry.register("custom_test")
        def custom_projector(widget: KgentsWidget[Any]) -> str:
            return "custom output"

        assert ProjectionRegistry.supports("custom_test")
        assert "custom_test" in ProjectionRegistry.all_targets()

    def test_register_with_fidelity(self) -> None:
        """Fidelity can be specified during registration."""

        @ProjectionRegistry.register("high_fi", fidelity=0.95)
        def high_fi_projector(widget: KgentsWidget[Any]) -> str:
            return "high fidelity"

        projector = ProjectionRegistry.get("high_fi")
        assert projector is not None
        assert projector.fidelity == 0.95

    def test_register_with_description(self) -> None:
        """Description can be specified during registration."""

        @ProjectionRegistry.register(
            "described",
            description="A well-documented projector",
        )
        def described_projector(widget: KgentsWidget[Any]) -> str:
            return "described"

        projector = ProjectionRegistry.get("described")
        assert projector is not None
        assert "well-documented" in projector.description

    def test_register_overwrites_existing(self) -> None:
        """Registering same name overwrites previous registration."""

        @ProjectionRegistry.register("overwrite_test")
        def v1(widget: KgentsWidget[Any]) -> str:
            return "v1"

        @ProjectionRegistry.register("overwrite_test")
        def v2(widget: KgentsWidget[Any]) -> str:
            return "v2"

        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "overwrite_test")
        assert result == "v2"


# =============================================================================
# Lookup Tests
# =============================================================================


class TestLookup:
    """Tests for target lookup and graceful degradation."""

    def test_get_existing_target(self) -> None:
        """Can retrieve registered projector by name."""
        projector = ProjectionRegistry.get("cli")
        assert projector is not None
        assert projector.name == "cli"

    def test_get_nonexistent_returns_none(self) -> None:
        """Getting nonexistent target returns None."""
        projector = ProjectionRegistry.get("nonexistent")
        assert projector is None

    def test_supports_existing(self) -> None:
        """supports() returns True for registered targets."""
        assert ProjectionRegistry.supports("cli")
        assert ProjectionRegistry.supports("json")

    def test_supports_nonexistent(self) -> None:
        """supports() returns False for unregistered targets."""
        assert not ProjectionRegistry.supports("nonexistent")

    def test_all_targets_includes_builtins(self) -> None:
        """all_targets() includes all built-in targets."""
        targets = ProjectionRegistry.all_targets()
        assert "cli" in targets
        assert "tui" in targets
        assert "marimo" in targets
        assert "json" in targets
        assert "sse" in targets

    def test_graceful_degradation_to_json(self) -> None:
        """Unknown targets fall back to JSON projection."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "unknown_target")
        # Should fall back to JSON
        assert isinstance(result, dict)
        assert "label" in result

    def test_explicit_fallback(self) -> None:
        """Can specify explicit fallback target."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "unknown", fallback="cli")
        assert "[test]" in result

    def test_fallback_not_found_raises(self) -> None:
        """Raises if both target and fallback not found."""
        widget = SimpleWidget()
        with pytest.raises(ValueError, match="Unknown projection target"):
            ProjectionRegistry.project(widget, "bad", fallback="also_bad")


# =============================================================================
# Built-in Target Tests
# =============================================================================


class TestBuiltinTargets:
    """Tests for built-in target projections."""

    def test_cli_projection(self) -> None:
        """CLI projection returns string."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "cli")
        assert result == "[test] 42"

    def test_tui_projection(self) -> None:
        """TUI projection returns string/Text."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "tui")
        assert "test" in str(result)

    def test_marimo_projection(self) -> None:
        """MARIMO projection returns HTML string."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "marimo")
        assert "<span>" in result

    def test_json_projection(self) -> None:
        """JSON projection returns dict."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "json")
        assert result == {"label": "test", "value": 42}

    def test_sse_projection_with_to_sse(self) -> None:
        """SSE projection delegates to to_sse() if available."""

        class SSEWidget(SimpleWidget):
            def to_sse(self) -> str:
                return "data: custom-sse\n\n"

        widget = SSEWidget()
        result = ProjectionRegistry.project(widget, "sse")
        assert result == "data: custom-sse\n\n"

    def test_sse_projection_fallback(self) -> None:
        """SSE projection falls back to JSON wrapper if no to_sse()."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, "sse")
        assert result.startswith("data: ")
        assert "label" in result

    def test_extended_target_enum_input(self) -> None:
        """Can use ExtendedTarget enum as input."""
        widget = SimpleWidget()
        result = ProjectionRegistry.project(widget, ExtendedTarget.CLI)
        assert result == "[test] 42"


# =============================================================================
# Fidelity Tests
# =============================================================================


class TestFidelity:
    """Tests for fidelity-based target selection."""

    def test_by_fidelity_lossless(self) -> None:
        """Can get lossless (JSON) projectors."""
        projectors = ProjectionRegistry.by_fidelity(FidelityLevel.LOSSLESS)
        names = [p.name for p in projectors]
        assert "json" in names

    def test_by_fidelity_high(self) -> None:
        """Can get high fidelity projectors."""
        projectors = ProjectionRegistry.by_fidelity(FidelityLevel.HIGH)
        names = [p.name for p in projectors]
        assert "marimo" in names

    def test_by_fidelity_low(self) -> None:
        """Can get low fidelity projectors."""
        projectors = ProjectionRegistry.by_fidelity(FidelityLevel.LOW)
        names = [p.name for p in projectors]
        assert "cli" in names

    def test_custom_fidelity_in_selection(self) -> None:
        """Custom targets appear in fidelity selection."""

        @ProjectionRegistry.register("ultra_hd", fidelity=0.99)
        def ultra_projector(widget: KgentsWidget[Any]) -> str:
            return "ultra"

        projectors = ProjectionRegistry.by_fidelity(FidelityLevel.MAXIMUM)
        names = [p.name for p in projectors]
        assert "ultra_hd" in names


# =============================================================================
# Isolation Tests
# =============================================================================


class TestIsolation:
    """Tests for registry reset and test isolation."""

    def test_reset_removes_custom(self) -> None:
        """reset() removes custom registrations."""

        @ProjectionRegistry.register("temporary")
        def temp(widget: KgentsWidget[Any]) -> str:
            return "temp"

        assert ProjectionRegistry.supports("temporary")

        ProjectionRegistry.reset()

        assert not ProjectionRegistry.supports("temporary")

    def test_reset_preserves_builtins(self) -> None:
        """reset() preserves built-in targets."""
        ProjectionRegistry.reset()

        assert ProjectionRegistry.supports("cli")
        assert ProjectionRegistry.supports("json")
        assert ProjectionRegistry.supports("sse")


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the projection system."""

    def test_custom_target_full_workflow(self) -> None:
        """Complete workflow: register, project, verify."""

        @ProjectionRegistry.register(
            "markdown",
            fidelity=0.4,
            description="Markdown projection",
        )
        def markdown_projector(widget: KgentsWidget[Any]) -> str:
            data = widget.to_json()
            return f"**{data.get('label', 'unknown')}**: {data.get('value', 'N/A')}"

        # Verify registration
        assert ProjectionRegistry.supports("markdown")
        projector = ProjectionRegistry.get("markdown")
        assert projector is not None
        assert projector.fidelity == 0.4

        # Use the projection
        widget = SimpleWidget(SimpleState(value=100, label="count"))
        result = ProjectionRegistry.project(widget, "markdown")
        assert result == "**count**: 100"

    def test_multiple_widgets_same_target(self) -> None:
        """Multiple widgets project to same target correctly."""

        @ProjectionRegistry.register("csv")
        def csv_projector(widget: KgentsWidget[Any]) -> str:
            data = widget.to_json()
            return f"{data.get('label', '')},{data.get('value', '')}"

        w1 = SimpleWidget(SimpleState(value=1, label="a"))
        w2 = SimpleWidget(SimpleState(value=2, label="b"))

        assert ProjectionRegistry.project(w1, "csv") == "a,1"
        assert ProjectionRegistry.project(w2, "csv") == "b,2"
