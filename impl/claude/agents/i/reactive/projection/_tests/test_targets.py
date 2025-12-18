"""
Tests for ExtendedTarget and target capabilities.

Test Categories:
    1. Enum - ExtendedTarget enum values and conversion
    2. Capabilities - Target capability queries
    3. Fidelity - Fidelity levels and selection
    4. Backward Compatibility - RenderTarget conversion
"""

from __future__ import annotations

import pytest

from agents.i.reactive.projection import (
    ExtendedTarget,
    FidelityLevel,
    TargetCapability,
    target_capabilities,
    target_fidelity,
)
from agents.i.reactive.projection.targets import targets_by_fidelity

# =============================================================================
# ExtendedTarget Enum Tests
# =============================================================================


class TestExtendedTarget:
    """Tests for ExtendedTarget enum."""

    def test_core_targets_exist(self) -> None:
        """Core targets are defined."""
        assert ExtendedTarget.CLI
        assert ExtendedTarget.TUI
        assert ExtendedTarget.MARIMO
        assert ExtendedTarget.JSON

    def test_extended_targets_exist(self) -> None:
        """Extended targets are defined."""
        assert ExtendedTarget.SSE
        assert ExtendedTarget.WEBGL
        assert ExtendedTarget.WEBXR
        assert ExtendedTarget.AUDIO

    def test_from_render_target_cli(self) -> None:
        """Can convert RenderTarget.CLI to ExtendedTarget."""
        from agents.i.reactive.widget import RenderTarget

        result = ExtendedTarget.from_render_target(RenderTarget.CLI)
        assert result == ExtendedTarget.CLI

    def test_from_render_target_all_core(self) -> None:
        """All core RenderTargets convert correctly."""
        from agents.i.reactive.widget import RenderTarget

        mappings = [
            (RenderTarget.CLI, ExtendedTarget.CLI),
            (RenderTarget.TUI, ExtendedTarget.TUI),
            (RenderTarget.MARIMO, ExtendedTarget.MARIMO),
            (RenderTarget.JSON, ExtendedTarget.JSON),
        ]

        for render, extended in mappings:
            assert ExtendedTarget.from_render_target(render) == extended

    def test_is_streaming(self) -> None:
        """is_streaming property works correctly."""
        assert ExtendedTarget.SSE.is_streaming
        assert not ExtendedTarget.CLI.is_streaming
        assert not ExtendedTarget.JSON.is_streaming

    def test_is_interactive(self) -> None:
        """is_interactive property works correctly."""
        assert ExtendedTarget.TUI.is_interactive
        assert ExtendedTarget.MARIMO.is_interactive
        assert ExtendedTarget.WEBGL.is_interactive
        assert not ExtendedTarget.CLI.is_interactive
        assert not ExtendedTarget.JSON.is_interactive

    def test_is_placeholder(self) -> None:
        """is_placeholder property works correctly."""
        assert ExtendedTarget.WEBGL.is_placeholder
        assert ExtendedTarget.WEBXR.is_placeholder
        assert ExtendedTarget.AUDIO.is_placeholder
        assert not ExtendedTarget.CLI.is_placeholder
        assert not ExtendedTarget.SSE.is_placeholder


# =============================================================================
# Target Capability Tests
# =============================================================================


class TestTargetCapabilities:
    """Tests for target capability queries."""

    def test_cli_capabilities(self) -> None:
        """CLI has expected capabilities."""
        caps = target_capabilities(ExtendedTarget.CLI)
        assert caps.fidelity < 0.5  # Low fidelity
        assert not caps.interactive
        assert not caps.streaming
        assert not caps.async_
        assert caps.implemented

    def test_json_capabilities(self) -> None:
        """JSON has expected capabilities."""
        caps = target_capabilities(ExtendedTarget.JSON)
        assert caps.fidelity == 1.0  # Lossless
        assert not caps.interactive
        assert caps.implemented

    def test_marimo_capabilities(self) -> None:
        """MARIMO has expected capabilities."""
        caps = target_capabilities(ExtendedTarget.MARIMO)
        assert caps.fidelity > 0.5  # High fidelity
        assert caps.interactive
        assert caps.implemented

    def test_sse_capabilities(self) -> None:
        """SSE has expected capabilities."""
        caps = target_capabilities(ExtendedTarget.SSE)
        assert caps.streaming
        assert caps.async_
        assert caps.implemented

    def test_placeholder_not_implemented(self) -> None:
        """Placeholder targets are marked as not implemented."""
        for target in [
            ExtendedTarget.WEBGL,
            ExtendedTarget.WEBXR,
            ExtendedTarget.AUDIO,
        ]:
            caps = target_capabilities(target)
            assert not caps.implemented


# =============================================================================
# Fidelity Tests
# =============================================================================


class TestFidelity:
    """Tests for fidelity levels and selection."""

    def test_target_fidelity_returns_float(self) -> None:
        """target_fidelity() returns a float."""
        fidelity = target_fidelity(ExtendedTarget.CLI)
        assert isinstance(fidelity, float)
        assert 0.0 <= fidelity <= 1.0

    def test_json_highest_fidelity(self) -> None:
        """JSON has highest fidelity (lossless)."""
        assert target_fidelity(ExtendedTarget.JSON) == 1.0

    def test_cli_lowest_fidelity(self) -> None:
        """CLI has lower fidelity than marimo."""
        cli_fidelity = target_fidelity(ExtendedTarget.CLI)
        marimo_fidelity = target_fidelity(ExtendedTarget.MARIMO)
        assert cli_fidelity < marimo_fidelity

    def test_targets_by_fidelity_lossless(self) -> None:
        """targets_by_fidelity() returns JSON for LOSSLESS."""
        targets = targets_by_fidelity(FidelityLevel.LOSSLESS)
        names = [t.name for t in targets]
        assert "JSON" in names

    def test_targets_by_fidelity_low(self) -> None:
        """targets_by_fidelity() returns CLI for LOW."""
        targets = targets_by_fidelity(FidelityLevel.LOW)
        names = [t.name for t in targets]
        assert "CLI" in names

    def test_targets_by_fidelity_excludes_unimplemented(self) -> None:
        """targets_by_fidelity() excludes unimplemented targets."""
        # WEBGL has high fidelity but is unimplemented
        targets = targets_by_fidelity(FidelityLevel.HIGH)
        names = [t.name for t in targets]
        # Should include marimo but not webgl
        assert "MARIMO" in names
        assert "WEBGL" not in names

    def test_targets_sorted_by_fidelity_descending(self) -> None:
        """targets_by_fidelity() returns targets sorted by fidelity (highest first)."""
        targets = targets_by_fidelity(FidelityLevel.MEDIUM)
        fidelities = [target_fidelity(t) for t in targets]
        assert fidelities == sorted(fidelities, reverse=True)


# =============================================================================
# FidelityLevel Enum Tests
# =============================================================================


class TestFidelityLevel:
    """Tests for FidelityLevel enum."""

    def test_all_levels_defined(self) -> None:
        """All fidelity levels are defined."""
        assert FidelityLevel.MAXIMUM
        assert FidelityLevel.HIGH
        assert FidelityLevel.MEDIUM
        assert FidelityLevel.LOW
        assert FidelityLevel.LOSSLESS

    def test_level_values(self) -> None:
        """FidelityLevel values are strings."""
        assert FidelityLevel.MAXIMUM.value == "maximum"
        assert FidelityLevel.HIGH.value == "high"
        assert FidelityLevel.MEDIUM.value == "medium"
        assert FidelityLevel.LOW.value == "low"
        assert FidelityLevel.LOSSLESS.value == "lossless"


# =============================================================================
# TargetCapability Dataclass Tests
# =============================================================================


class TestTargetCapabilityDataclass:
    """Tests for TargetCapability dataclass."""

    def test_is_frozen(self) -> None:
        """TargetCapability is immutable."""
        caps = TargetCapability(
            fidelity=0.5,
            interactive=True,
            streaming=False,
            async_=False,
            implemented=True,
        )
        with pytest.raises(AttributeError):
            caps.fidelity = 0.9  # type: ignore[misc]

    def test_all_fields_accessible(self) -> None:
        """All TargetCapability fields are accessible."""
        caps = TargetCapability(
            fidelity=0.8,
            interactive=True,
            streaming=True,
            async_=True,
            implemented=False,
        )
        assert caps.fidelity == 0.8
        assert caps.interactive is True
        assert caps.streaming is True
        assert caps.async_ is True
        assert caps.implemented is False
