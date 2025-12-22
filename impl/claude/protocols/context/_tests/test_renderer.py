"""
Tests for Multi-Surface Outline Renderer.

Verifies that outlines render correctly to different surfaces
with appropriate fidelity levels.

Spec: spec/protocols/context-perception.md §9
"""

from __future__ import annotations

import json
import pytest

from protocols.context.outline import (
    Outline,
    OutlineNode,
    TextSnippet,
    PortalToken,
    SnippetType,
    create_outline,
)
from protocols.context.renderer import (
    Surface,
    RenderConfig,
    OutlineRenderer,
    render_outline,
    render_for_llm,
    SURFACE_CONFIG,
)


# === Test Fixtures ===


@pytest.fixture
def simple_outline() -> Outline:
    """Create a simple outline for testing."""
    outline = create_outline(root_text="# Investigation")
    return outline


@pytest.fixture
def outline_with_portal() -> Outline:
    """Create an outline with a portal."""
    outline = create_outline(root_text="# Investigation")

    # Add a portal
    portal = PortalToken(
        source_path="world.auth",
        edge_type="tests",
        destinations=["test_auth.py", "test_core.py", "test_edge.py"],
        expanded=False,
    )
    portal_node = OutlineNode(portal=portal)
    outline.root.add_child(portal_node)

    return outline


@pytest.fixture
def outline_with_expanded_portal() -> Outline:
    """Create an outline with an expanded portal and children."""
    outline = create_outline(root_text="# Investigation")

    # Add an expanded portal
    portal = PortalToken(
        source_path="world.auth",
        edge_type="tests",
        destinations=["test_auth.py"],
        expanded=True,
    )
    portal_node = OutlineNode(portal=portal)
    outline.root.add_child(portal_node)

    # Add child content
    child_snippet = TextSnippet(
        visible_text="def test_auth():\n    assert True",
        snippet_type=SnippetType.CODE,
    )
    child_node = OutlineNode(snippet=child_snippet)
    portal_node.add_child(child_node)

    return outline


# === Surface Configuration Tests ===


class TestSurfaceConfig:
    """Tests for surface configuration."""

    def test_all_surfaces_have_config(self) -> None:
        """Every surface has a configuration."""
        for surface in Surface:
            assert surface in SURFACE_CONFIG

    def test_cli_has_low_fidelity(self) -> None:
        """CLI has low fidelity (0.2)."""
        config = SURFACE_CONFIG[Surface.CLI]
        assert config["fidelity"] == 0.2
        assert config["use_color"] is False

    def test_web_has_high_fidelity(self) -> None:
        """Web has high fidelity (0.8)."""
        config = SURFACE_CONFIG[Surface.WEB]
        assert config["fidelity"] == 0.8
        assert config["use_color"] is True

    def test_llm_has_medium_fidelity(self) -> None:
        """LLM has medium fidelity (0.6) with depth limits."""
        config = SURFACE_CONFIG[Surface.LLM]
        assert config["fidelity"] == 0.6
        assert config["max_depth"] == 4

    def test_json_has_full_fidelity(self) -> None:
        """JSON has full fidelity (1.0)."""
        config = SURFACE_CONFIG[Surface.JSON]
        assert config["fidelity"] == 1.0


# === CLI Rendering Tests ===


class TestCLIRendering:
    """Tests for CLI surface rendering."""

    def test_cli_renders_text(self, simple_outline: Outline) -> None:
        """CLI renders basic text."""
        output = render_outline(simple_outline, Surface.CLI)
        assert "Investigation" in output

    def test_cli_renders_portal_collapsed(self, outline_with_portal: Outline) -> None:
        """CLI renders collapsed portal with ASCII marker."""
        output = render_outline(outline_with_portal, Surface.CLI)
        # Should use > for collapsed
        assert ">" in output
        assert "[tests]" in output

    def test_cli_has_no_ansi_codes(self, outline_with_portal: Outline) -> None:
        """CLI output has no ANSI escape codes."""
        output = render_outline(outline_with_portal, Surface.CLI)
        assert "\033[" not in output

    def test_cli_shows_trail_count(self, simple_outline: Outline) -> None:
        """CLI shows trail count when steps exist."""
        simple_outline.record_step("navigate", "world.foo")
        output = render_outline(simple_outline, Surface.CLI)
        assert "Trail:" in output
        assert "1 step" in output

    def test_cli_shows_budget_warning(self, simple_outline: Outline) -> None:
        """CLI shows budget warning when low."""
        simple_outline.steps_taken = 90  # 90% used
        output = render_outline(simple_outline, Surface.CLI)
        assert "Budget:" in output


# === TUI Rendering Tests ===


class TestTUIRendering:
    """Tests for TUI surface rendering."""

    def test_tui_has_unicode_markers(self, outline_with_portal: Outline) -> None:
        """TUI uses unicode markers."""
        output = render_outline(outline_with_portal, Surface.TUI)
        assert "▶" in output or "▼" in output

    def test_tui_has_colors(self, outline_with_portal: Outline) -> None:
        """TUI output has ANSI color codes."""
        output = render_outline(outline_with_portal, Surface.TUI)
        # Should contain ANSI codes
        assert "\033[" in output


# === Web Rendering Tests ===


class TestWebRendering:
    """Tests for Web surface rendering."""

    def test_web_renders_html(self, simple_outline: Outline) -> None:
        """Web renders as HTML."""
        output = render_outline(simple_outline, Surface.WEB)
        assert "<div" in output
        assert "</div>" in output

    def test_web_portal_uses_details(self, outline_with_portal: Outline) -> None:
        """Web renders portals as <details> elements."""
        output = render_outline(outline_with_portal, Surface.WEB)
        assert "<details" in output
        assert "<summary>" in output

    def test_web_expanded_portal_has_open(self, outline_with_expanded_portal: Outline) -> None:
        """Expanded portals have 'open' attribute."""
        output = render_outline(outline_with_expanded_portal, Surface.WEB)
        assert "open" in output

    def test_web_escapes_content(self) -> None:
        """Web escapes HTML in content."""
        outline = create_outline(root_text="<script>alert('xss')</script>")
        output = render_outline(outline, Surface.WEB)
        # Should escape the script tag
        assert "<script>" not in output
        assert "&lt;script&gt;" in output


# === LLM Rendering Tests ===


class TestLLMRendering:
    """Tests for LLM context surface rendering."""

    def test_llm_has_xml_structure(self, simple_outline: Outline) -> None:
        """LLM output has XML tags."""
        output = render_outline(simple_outline, Surface.LLM)
        assert "<!-- OUTLINE:" in output
        assert "<!-- END OUTLINE -->" in output
        assert "<node" in output
        assert "</node>" in output

    def test_llm_portal_has_metadata(self, outline_with_portal: Outline) -> None:
        """LLM portal includes edge type and state."""
        output = render_outline(outline_with_portal, Surface.LLM)
        assert 'edge="tests"' in output
        assert 'state="collapsed"' in output

    def test_llm_includes_trail_metadata(self, simple_outline: Outline) -> None:
        """LLM includes trail length in comments."""
        simple_outline.record_step("focus", "world.foo")
        output = render_outline(simple_outline, Surface.LLM)
        assert "trail_length:" in output

    def test_llm_respects_depth_limit(self) -> None:
        """LLM respects depth limit for context windows."""
        # Create deep outline
        outline = create_outline(root_text="Root")
        current = outline.root
        for i in range(10):
            child = OutlineNode(
                snippet=TextSnippet(visible_text=f"Level {i}")
            )
            current.add_child(child)
            current = child

        # Render with depth limit
        output = render_for_llm(outline, max_depth=3)
        assert "DEPTH LIMIT" in output

    def test_render_for_llm_convenience(self, simple_outline: Outline) -> None:
        """render_for_llm convenience function works."""
        output = render_for_llm(simple_outline)
        assert "<!-- OUTLINE:" in output


# === JSON Rendering Tests ===


class TestJSONRendering:
    """Tests for JSON surface rendering."""

    def test_json_is_valid(self, simple_outline: Outline) -> None:
        """JSON output is valid JSON."""
        output = render_outline(simple_outline, Surface.JSON)
        data = json.loads(output)
        assert "id" in data
        assert "root" in data

    def test_json_includes_all_fields(self, outline_with_portal: Outline) -> None:
        """JSON includes all outline fields."""
        output = render_outline(outline_with_portal, Surface.JSON)
        data = json.loads(output)

        assert "observer_id" in data
        assert "trail_steps" in data
        assert "budget_remaining" in data
        assert "created_at" in data

    def test_json_portal_has_destinations(self, outline_with_portal: Outline) -> None:
        """JSON portal includes destinations."""
        output = render_outline(outline_with_portal, Surface.JSON)
        data = json.loads(output)

        # Find the portal in children
        root = data["root"]
        portal_child = root["children"][0]
        assert portal_child["type"] == "portal"
        assert "destinations" in portal_child
        assert len(portal_child["destinations"]) == 3


# === Render Config Tests ===


class TestRenderConfig:
    """Tests for render configuration."""

    def test_config_overrides_max_depth(self) -> None:
        """Config can override max depth."""
        config = RenderConfig(surface=Surface.CLI, max_depth=1)
        assert config.config["max_depth"] == 1

    def test_config_preserves_surface_defaults(self) -> None:
        """Config preserves surface defaults when not overridden."""
        config = RenderConfig(surface=Surface.WEB)
        assert config.config["use_color"] is True
        assert config.config["fidelity"] == 0.8


# === Renderer Class Tests ===


class TestOutlineRenderer:
    """Tests for OutlineRenderer class."""

    def test_renderer_can_be_instantiated(self) -> None:
        """Renderer can be created."""
        renderer = OutlineRenderer()
        assert renderer is not None

    def test_renderer_handles_all_surfaces(self, simple_outline: Outline) -> None:
        """Renderer handles all surface types."""
        renderer = OutlineRenderer()
        for surface in Surface:
            output = renderer.render(simple_outline, surface)
            assert output is not None
            assert len(output) > 0
