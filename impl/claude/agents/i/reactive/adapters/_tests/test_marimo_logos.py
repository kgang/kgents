"""
Tests for LogosCell: AGENTESE REPL for marimo notebooks.

Tests verify:
1. LogosCellResult formatting (HTML, JSON, CLI)
2. LogosCell invocation patterns
3. LogosCellPath composition
4. Error handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from agents.i.reactive.adapters.marimo_logos import (
    LogosCell,
    LogosCellPath,
    LogosCellResult,
    create_logos_cell,
)
from agents.i.reactive.widget import RenderTarget

# =============================================================================
# LogosCellResult Tests
# =============================================================================


class TestLogosCellResult:
    """Test LogosCellResult formatting."""

    def test_result_repr_html_success(self) -> None:
        """Successful result renders as HTML."""
        result = LogosCellResult(
            raw={"value": 42},
            path="test.path",
            html="<div>42</div>",
            json={"value": 42},
            cli="42",
        )

        html = result._repr_html_()

        assert html == "<div>42</div>"

    def test_result_repr_html_error(self) -> None:
        """Error result renders with error styling."""
        result = LogosCellResult(
            raw=None,
            path="test.path",
            error="Path not found",
        )

        html = result._repr_html_()

        assert "logos-error" in html
        assert "Path not found" in html
        assert "color: red" in html

    def test_result_str_success(self) -> None:
        """Successful result __str__ returns CLI output."""
        result = LogosCellResult(
            raw={"value": 42},
            path="test.path",
            cli="Value: 42",
        )

        assert str(result) == "Value: 42"

    def test_result_str_error(self) -> None:
        """Error result __str__ returns error message."""
        result = LogosCellResult(
            raw=None,
            path="test.path",
            error="Something went wrong",
        )

        assert str(result) == "Error: Something went wrong"

    def test_result_str_fallback_to_raw(self) -> None:
        """Result __str__ falls back to raw if CLI empty."""
        result = LogosCellResult(
            raw={"value": 42},
            path="test.path",
        )

        assert str(result) == "{'value': 42}"


# =============================================================================
# LogosCell Tests
# =============================================================================


class TestLogosCell:
    """Test LogosCell creation and configuration."""

    def test_create_logos_cell_default(self) -> None:
        """create_logos_cell creates cell with default Logos."""
        cell = create_logos_cell()

        assert isinstance(cell, LogosCell)
        assert cell.default_target == RenderTarget.MARIMO
        assert cell.auto_project is True

    def test_create_logos_cell_custom_target(self) -> None:
        """create_logos_cell respects custom target."""
        cell = create_logos_cell(default_target=RenderTarget.CLI)

        assert cell.default_target == RenderTarget.CLI

    def test_logos_cell_path_creation(self) -> None:
        """LogosCell.path() creates LogosCellPath."""
        cell = create_logos_cell()

        path = cell.path("world.agent.manifest")

        assert isinstance(path, LogosCellPath)
        assert path.path == "world.agent.manifest"
        assert path.cell is cell

    def test_logos_cell_rshift_creates_path(self) -> None:
        """cell >> 'path' creates LogosCellPath."""
        cell = create_logos_cell()

        path = cell >> "world.agent.manifest"

        assert isinstance(path, LogosCellPath)
        assert path.path == "world.agent.manifest"


# =============================================================================
# LogosCellPath Tests
# =============================================================================


class TestLogosCellPath:
    """Test LogosCellPath composition."""

    def test_path_rshift_composition(self) -> None:
        """path >> 'other' composes paths."""
        cell = create_logos_cell()
        path1 = cell.path("world.agent")

        path2 = path1 >> "manifest"

        assert isinstance(path2, LogosCellPath)
        assert path2.path == "world.agent >> manifest"


# =============================================================================
# Projection Tests
# =============================================================================


class TestLogosCellProjection:
    """Test LogosCell projection helpers."""

    def test_project_to_html_kgents_widget(self) -> None:
        """_project_to_html handles KgentsWidget."""
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        cell = create_logos_cell()
        widget = GlyphWidget(GlyphState(char="X"))

        html = cell._project_to_html(widget, RenderTarget.MARIMO)

        # Should get marimo projection (HTML string)
        assert isinstance(html, str)

    def test_project_to_html_dict(self) -> None:
        """_project_to_html wraps dict in pre tag."""
        cell = create_logos_cell()

        html = cell._project_to_html({"key": "value"}, RenderTarget.MARIMO)

        assert "<pre>" in html
        assert "key" in html

    def test_project_to_json_kgents_widget(self) -> None:
        """_project_to_json handles KgentsWidget."""
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        cell = create_logos_cell()
        widget = GlyphWidget(GlyphState(char="X", phase="active"))

        json_dict = cell._project_to_json(widget)

        assert isinstance(json_dict, dict)
        assert json_dict.get("type") == "glyph"

    def test_project_to_json_dict(self) -> None:
        """_project_to_json returns dict unchanged."""
        cell = create_logos_cell()

        json_dict = cell._project_to_json({"key": "value"})

        assert json_dict == {"key": "value"}

    def test_project_to_cli_kgents_widget(self) -> None:
        """_project_to_cli handles KgentsWidget."""
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        cell = create_logos_cell()
        widget = GlyphWidget(GlyphState(char="X"))

        cli = cell._project_to_cli(widget)

        assert isinstance(cli, str)
        assert "X" in cli

    def test_escape_html(self) -> None:
        """_escape_html escapes special characters."""
        cell = create_logos_cell()

        escaped = cell._escape_html('<script>alert("xss")</script>')

        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&quot;" in escaped
        assert "<script>" not in escaped


# =============================================================================
# Integration Pattern Tests
# =============================================================================


class TestLogosCellIntegration:
    """Test LogosCell integration patterns for marimo."""

    def test_result_usable_with_mo_html(self) -> None:
        """LogosCellResult can be used with mo.Html pattern."""
        result = LogosCellResult(
            raw={"value": 42},
            path="test.path",
            html="<div>42</div>",
        )

        # Simulates: mo.Html(result._repr_html_())
        html = result._repr_html_()

        assert isinstance(html, str)
        assert "<div>" in html

    def test_composed_widget_projection(self) -> None:
        """LogosCell can project composed widgets."""
        from agents.i.reactive.composable import HStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        cell = create_logos_cell()
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        composed = a >> b

        html = cell._project_to_html(composed, RenderTarget.MARIMO)

        assert "kgents-hstack" in html
        assert "A" in html
        assert "B" in html
