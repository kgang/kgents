"""
Tests for the Projection Component Gallery.

Tests cover:
1. Pilot registration and retrieval
2. Override system (env, CLI, merge)
3. Rendering across all targets
4. Category filtering
5. Benchmark execution
6. Error handling
"""

from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest

from agents.i.reactive.widget import RenderTarget
from protocols.projection.gallery.overrides import (
    DEFAULT_OVERRIDES,
    GalleryOverrides,
    get_overrides_from_env,
    merge_overrides,
)
from protocols.projection.gallery.pilots import (
    PILOT_REGISTRY,
    Pilot,
    PilotCategory,
    get_pilots_by_category,
    get_pilots_by_tag,
    list_all_pilots,
)
from protocols.projection.gallery.runner import Gallery, RenderResult, run_gallery

# =============================================================================
# Override Tests
# =============================================================================


class TestGalleryOverrides:
    """Test the override configuration system."""

    def test_default_overrides_are_none(self) -> None:
        """Default overrides should not modify anything."""
        overrides = DEFAULT_OVERRIDES
        assert overrides.target is None
        assert overrides.entropy is None
        assert overrides.seed is None
        assert overrides.time_ms is None
        assert overrides.verbose is False

    def test_with_entropy_clamps_value(self) -> None:
        """Entropy should be clamped to [0.0, 1.0]."""
        overrides = GalleryOverrides()

        # Normal value
        o1 = overrides.with_entropy(0.5)
        assert o1.entropy == 0.5

        # Below 0
        o2 = overrides.with_entropy(-0.5)
        assert o2.entropy == 0.0

        # Above 1
        o3 = overrides.with_entropy(1.5)
        assert o3.entropy == 1.0

    def test_with_seed_sets_value(self) -> None:
        """Seed override should set the value."""
        overrides = GalleryOverrides().with_seed(42)
        assert overrides.seed == 42

    def test_with_widget_override_merges(self) -> None:
        """Widget-specific overrides should merge with existing."""
        overrides = GalleryOverrides().with_widget_override("glyph_active", {"phase": "error"})
        overrides = overrides.with_widget_override("glyph_active", {"entropy": 0.5})

        widget_overrides = overrides.get_widget_override("glyph_active")
        assert widget_overrides["phase"] == "error"
        assert widget_overrides["entropy"] == 0.5

    def test_get_overrides_from_env(self) -> None:
        """Environment variables should populate overrides."""
        with patch.dict(
            os.environ,
            {
                "KGENTS_GALLERY_ENTROPY": "0.7",
                "KGENTS_GALLERY_SEED": "123",
                "KGENTS_GALLERY_VERBOSE": "1",
                "KGENTS_GALLERY_PHASE": "error",
            },
        ):
            overrides = get_overrides_from_env()
            assert overrides.entropy == 0.7
            assert overrides.seed == 123
            assert overrides.verbose is True
            assert overrides.phase == "error"

    def test_get_overrides_from_env_handles_invalid(self) -> None:
        """Invalid env values should be ignored."""
        with patch.dict(
            os.environ,
            {
                "KGENTS_GALLERY_ENTROPY": "not-a-number",
                "KGENTS_GALLERY_SEED": "also-not-a-number",
            },
        ):
            overrides = get_overrides_from_env()
            assert overrides.entropy is None
            assert overrides.seed is None

    def test_merge_overrides_cli_wins(self) -> None:
        """CLI overrides should take precedence over env."""
        base = GalleryOverrides(entropy=0.3, seed=42, verbose=False)
        cli = GalleryOverrides(entropy=0.8, seed=None)

        merged = merge_overrides(base, cli)
        assert merged.entropy == 0.8  # CLI wins
        assert merged.seed == 42  # Base (CLI was None)
        assert merged.verbose is False  # Base


# =============================================================================
# Pilot Registry Tests
# =============================================================================


class TestPilotRegistry:
    """Test pilot registration and retrieval."""

    def test_registry_not_empty(self) -> None:
        """Registry should have pilots registered."""
        assert len(PILOT_REGISTRY) > 0

    def test_all_pilots_have_required_fields(self) -> None:
        """Every pilot should have name, category, description."""
        for name, pilot in PILOT_REGISTRY.items():
            assert pilot.name == name
            assert isinstance(pilot.category, PilotCategory)
            assert len(pilot.description) > 0
            assert callable(pilot.widget_factory)

    def test_get_pilots_by_category(self) -> None:
        """Category filtering should return correct pilots."""
        primitives = get_pilots_by_category(PilotCategory.PRIMITIVES)
        assert len(primitives) > 0
        for pilot in primitives:
            assert pilot.category == PilotCategory.PRIMITIVES

    def test_get_pilots_by_tag(self) -> None:
        """Tag filtering should return matching pilots."""
        glyph_pilots = get_pilots_by_tag("glyph")
        assert len(glyph_pilots) > 0
        for pilot in glyph_pilots:
            assert "glyph" in pilot.tags

    def test_list_all_pilots(self) -> None:
        """List all should return all pilot names."""
        names = list_all_pilots()
        assert len(names) == len(PILOT_REGISTRY)
        assert all(name in PILOT_REGISTRY for name in names)


# =============================================================================
# Pilot Rendering Tests
# =============================================================================


class TestPilotRendering:
    """Test that all pilots render successfully."""

    @pytest.mark.parametrize("pilot_name", list(PILOT_REGISTRY.keys()))
    def test_pilot_renders_to_cli(self, pilot_name: str) -> None:
        """Every pilot should render to CLI without error."""
        pilot = PILOT_REGISTRY[pilot_name]
        result = pilot.render(RenderTarget.CLI)
        assert result is not None

    @pytest.mark.parametrize("pilot_name", list(PILOT_REGISTRY.keys()))
    def test_pilot_renders_to_json(self, pilot_name: str) -> None:
        """Every pilot should render to JSON without error."""
        pilot = PILOT_REGISTRY[pilot_name]
        result = pilot.render(RenderTarget.JSON)
        assert result is not None

    def test_pilot_with_overrides(self) -> None:
        """Pilots should accept overrides."""
        pilot = PILOT_REGISTRY.get("glyph_entropy_sweep")
        if pilot:
            result_low = pilot.render(RenderTarget.CLI, {"entropy": 0.1})
            result_high = pilot.render(RenderTarget.CLI, {"entropy": 0.9})
            # Both should succeed
            assert result_low is not None
            assert result_high is not None


# =============================================================================
# Gallery Runner Tests
# =============================================================================


class TestGalleryRunner:
    """Test the Gallery executor."""

    def test_gallery_creation(self) -> None:
        """Gallery should initialize with overrides."""
        gallery = Gallery(GalleryOverrides(entropy=0.5))
        assert gallery.overrides.entropy == 0.5

    def test_render_returns_result(self) -> None:
        """Render should return RenderResult."""
        gallery = Gallery()
        result = gallery.render("glyph_idle")
        assert isinstance(result, RenderResult)
        assert result.success is True
        assert result.render_time_ms >= 0

    def test_render_unknown_pilot_fails(self) -> None:
        """Unknown pilot should return failure result."""
        gallery = Gallery()
        result = gallery.render("nonexistent_pilot")
        assert result.success is False
        assert "Unknown pilot" in result.error

    def test_show_returns_string(self) -> None:
        """Show should return formatted string."""
        gallery = Gallery()
        output = gallery.show("glyph_idle")
        assert isinstance(output, str)
        assert len(output) > 0

    def test_show_all_includes_all_categories(self) -> None:
        """Show all should include section headers for categories."""
        gallery = Gallery()
        output = gallery.show_all(RenderTarget.CLI)
        assert "PRIMITIVES" in output
        assert "CARDS" in output

    def test_show_category_filters_correctly(self) -> None:
        """Category view should only include that category."""
        gallery = Gallery()
        output = gallery.show_category(PilotCategory.PRIMITIVES)
        assert "PRIMITIVES" in output

    def test_compare_targets_shows_all_targets(self) -> None:
        """Target comparison should show CLI, TUI, MARIMO, JSON."""
        gallery = Gallery()
        output = gallery.compare_targets("glyph_idle")
        assert "CLI" in output
        assert "TUI" in output
        assert "MARIMO" in output
        assert "JSON" in output

    def test_benchmark_returns_results(self) -> None:
        """Benchmark should return timing data."""
        gallery = Gallery()
        results = gallery.benchmark(["glyph_idle"], iterations=10)
        assert len(results) == 1
        assert results[0].pilot_name == "glyph_idle"
        assert "CLI" in results[0].renders_per_second

    def test_iter_renders_yields_all_pilots(self) -> None:
        """Iteration should yield all registered pilots."""
        gallery = Gallery()
        rendered = list(gallery.iter_renders(RenderTarget.CLI))
        assert len(rendered) == len(PILOT_REGISTRY)


# =============================================================================
# Integration Tests
# =============================================================================


class TestRunGallery:
    """Test the high-level run_gallery function."""

    def test_run_gallery_list_mode(self) -> None:
        """List mode should show all pilots."""
        output = run_gallery(list_only=True)
        assert "Available Pilots" in output
        assert "glyph_idle" in output

    def test_run_gallery_single_pilot(self) -> None:
        """Single pilot mode should show just one widget."""
        output = run_gallery(pilot_name="glyph_idle")
        assert output is not None
        assert len(output) > 0

    def test_run_gallery_with_overrides(self) -> None:
        """Overrides should affect rendering."""
        overrides = GalleryOverrides(verbose=True)
        output = run_gallery(pilot_name="glyph_idle", overrides=overrides)
        # Verbose mode adds extra info
        assert "Tags:" in output or "Description:" in output


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_entropy_extreme_values(self) -> None:
        """Extreme entropy values should render without error."""
        gallery = Gallery(GalleryOverrides(entropy=0.0))
        result_low = gallery.render("glyph_active")
        assert result_low.success

        gallery_high = Gallery(GalleryOverrides(entropy=1.0))
        result_high = gallery_high.render("glyph_active")
        assert result_high.success

    def test_empty_category_returns_message(self) -> None:
        """Empty category should return appropriate message."""
        gallery = Gallery()
        # ADAPTERS category might be empty in our pilot set
        output = gallery.show_category(PilotCategory.ADAPTERS)
        # Should not crash, should return something
        assert isinstance(output, str)

    def test_benchmark_with_empty_list(self) -> None:
        """Benchmark with no pilots should return empty list."""
        gallery = Gallery()
        results = gallery.benchmark([])
        assert results == []

    def test_variation_rendering(self) -> None:
        """Pilots with variations should handle variation overrides."""
        pilot = PILOT_REGISTRY.get("glyph_entropy_sweep")
        if pilot and pilot.variations:
            for variation in pilot.variations:
                result = pilot.render(RenderTarget.CLI, variation)
                assert result is not None
