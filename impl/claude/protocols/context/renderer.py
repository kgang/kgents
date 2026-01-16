"""
Multi-Surface Outline Renderer.

Renders Outline to different surfaces with appropriate fidelity:
- CLI (0.2): ASCII portals, no color, simple tree
- TUI (0.5): Full tree, keyboard nav, basic color
- Web (0.8): Interactive, animated, presence indicators
- LLM (0.6): XML-tagged, depth-limited for context windows
- JSON (1.0): Raw state, no rendering

Spec: spec/protocols/context-perception.md §9

Teaching:
    gotcha: Surface fidelity is a trade-off. CLI needs to work in any terminal,
            while Web can assume rich rendering. Don't over-engineer low-fidelity
            surfaces—simplicity IS the feature.
            (Evidence: test_renderer.py::test_cli_simplicity)

    gotcha: LLM surface has special requirements: XML tags for parsing, depth
            limits for context windows, metadata in comments. It's not just
            "another text format."
            (Evidence: test_renderer.py::test_llm_context_limits)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .outline import Outline, OutlineNode, PortalToken, TextSnippet


class Surface(Enum):
    """Rendering surfaces with different fidelity levels."""

    CLI = auto()  # 0.2 fidelity: ASCII, no color
    TUI = auto()  # 0.5 fidelity: Full tree, basic color
    WEB = auto()  # 0.8 fidelity: Interactive, animated
    LLM = auto()  # 0.6 fidelity: XML-tagged, depth-limited
    JSON = auto()  # 1.0 fidelity: Raw state


# Surface-specific configuration
SURFACE_CONFIG = {
    Surface.CLI: {
        "fidelity": 0.2,
        "max_depth": 3,
        "use_color": False,
        "expand_marker": ">",
        "collapse_marker": "v",
        "indent": "  ",
    },
    Surface.TUI: {
        "fidelity": 0.5,
        "max_depth": 5,
        "use_color": True,
        "expand_marker": "▶",
        "collapse_marker": "▼",
        "indent": "  ",
    },
    Surface.WEB: {
        "fidelity": 0.8,
        "max_depth": 10,
        "use_color": True,
        "expand_marker": "▶",
        "collapse_marker": "▼",
        "indent": "  ",
    },
    Surface.LLM: {
        "fidelity": 0.6,
        "max_depth": 4,
        "use_color": False,
        "expand_marker": "[+]",
        "collapse_marker": "[-]",
        "indent": "  ",
    },
    Surface.JSON: {
        "fidelity": 1.0,
        "max_depth": 100,
        "use_color": False,
        "expand_marker": "",
        "collapse_marker": "",
        "indent": "",
    },
}


@dataclass
class RenderConfig:
    """Configuration for a specific render operation."""

    surface: Surface
    max_depth: int | None = None  # Override surface default
    max_lines: int | None = None  # Limit output length
    show_metadata: bool = False  # Include metadata in output
    compact: bool = False  # Use compact layout

    @property
    def config(self) -> dict[str, Any]:
        """Get merged configuration for this render."""
        base = SURFACE_CONFIG.get(self.surface, SURFACE_CONFIG[Surface.CLI]).copy()
        if self.max_depth is not None:
            base["max_depth"] = self.max_depth
        return base


class OutlineRenderer:
    """
    Renders Outline to multiple surfaces.

    Each surface has its own rendering logic optimized for that context:
    - CLI: Plain text, works in any terminal
    - TUI: Rich text with ANSI colors
    - Web: HTML with interactive elements
    - LLM: XML-tagged for LLM context windows
    - JSON: Serialized state for programmatic access

    Usage:
        renderer = OutlineRenderer()
        cli_output = renderer.render(outline, Surface.CLI)
        web_output = renderer.render(outline, Surface.WEB)
    """

    def render(
        self,
        outline: "Outline",
        surface: Surface,
        config: RenderConfig | None = None,
    ) -> str:
        """
        Render outline to the specified surface.

        Args:
            outline: The outline to render
            surface: Target surface
            config: Optional render configuration

        Returns:
            Rendered string appropriate for the surface
        """
        if config is None:
            config = RenderConfig(surface=surface)

        match surface:
            case Surface.CLI:
                return self._render_cli(outline, config)
            case Surface.TUI:
                return self._render_tui(outline, config)
            case Surface.WEB:
                return self._render_web(outline, config)
            case Surface.LLM:
                return self._render_llm(outline, config)
            case Surface.JSON:
                return self._render_json(outline, config)

    def _render_cli(self, outline: "Outline", config: RenderConfig) -> str:
        """
        Render for CLI (0.2 fidelity).

        Simple ASCII tree, no color, works everywhere.
        """
        cfg = config.config
        lines: list[str] = []

        def render_node(node: "OutlineNode", depth: int = 0) -> None:
            if depth > cfg["max_depth"]:
                return

            indent = cfg["indent"] * depth

            if node.snippet is not None:
                # Text snippet
                text = node.snippet.visible_text
                # Truncate long lines for CLI
                if len(text) > 80:
                    text = text[:77] + "..."
                lines.append(f"{indent}{text}")

            elif node.portal is not None:
                # Portal token
                portal = node.portal
                marker = cfg["collapse_marker"] if portal.expanded else cfg["expand_marker"]
                lines.append(f"{indent}{marker} [{portal.edge_type}] {portal.summary}")

            # Render children if expanded
            if node.is_expanded:
                for child in node.children:
                    render_node(child, depth + 1)

        render_node(outline.root)

        # Add trail info if present
        if outline.trail_steps:
            lines.append("")
            lines.append(f"[Trail: {len(outline.trail_steps)} steps]")

        # Add budget warning
        if outline.is_budget_low:
            lines.append(f"[Budget: {outline.budget_remaining:.0%}]")

        return "\n".join(lines)

    def _render_tui(self, outline: "Outline", config: RenderConfig) -> str:
        """
        Render for TUI (0.5 fidelity).

        Full tree with ANSI colors.
        """
        cfg = config.config

        # ANSI color codes
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        lines: list[str] = []

        def render_node(node: "OutlineNode", depth: int = 0) -> None:
            if depth > cfg["max_depth"]:
                return

            indent = cfg["indent"] * depth

            if node.snippet is not None:
                text = node.snippet.visible_text
                # Highlight based on snippet type
                from .outline import SnippetType

                match node.snippet.snippet_type:
                    case SnippetType.PROSE:
                        lines.append(f"{indent}{text}")
                    case SnippetType.CODE:
                        lines.append(f"{indent}{CYAN}{text}{RESET}")
                    case SnippetType.EVIDENCE:
                        lines.append(f"{indent}{GREEN}{text}{RESET}")
                    case SnippetType.ANNOTATION:
                        lines.append(f"{indent}{DIM}{text}{RESET}")
                    case _:
                        lines.append(f"{indent}{text}")

            elif node.portal is not None:
                portal = node.portal
                marker = cfg["collapse_marker"] if portal.expanded else cfg["expand_marker"]
                edge = f"{YELLOW}[{portal.edge_type}]{RESET}"
                lines.append(f"{indent}{marker} {edge} {portal.summary}")

            if node.is_expanded:
                for child in node.children:
                    render_node(child, depth + 1)

        render_node(outline.root)

        # Trail breadcrumb
        if outline.trail_steps:
            steps = outline.trail_steps[-5:]  # Last 5 steps
            breadcrumb = " > ".join(s.get("node_path", "?").split(".")[-1] for s in steps)
            lines.append("")
            lines.append(f"{DIM}Trail: {breadcrumb}{RESET}")

        # Budget meter
        budget = outline.budget_remaining
        if budget < 0.2:
            lines.append(f"{YELLOW}Budget: {budget:.0%}{RESET}")

        return "\n".join(lines)

    def _render_web(self, outline: "Outline", config: RenderConfig) -> str:
        """
        Render for Web (0.8 fidelity).

        HTML with interactive <details> elements.
        """
        import html

        cfg = config.config
        parts: list[str] = ['<div class="outline">']

        def render_node(node: "OutlineNode", depth: int = 0) -> None:
            if depth > cfg["max_depth"]:
                return

            if node.snippet is not None:
                text = html.escape(node.snippet.visible_text)
                snippet_type = node.snippet.snippet_type.name.lower()
                parts.append(f'<div class="snippet snippet-{snippet_type}">{text}</div>')

            elif node.portal is not None:
                portal = node.portal
                open_attr = " open" if portal.expanded else ""
                edge = html.escape(portal.edge_type)
                summary_text = html.escape(portal.summary)

                parts.append(
                    f'<details class="portal" data-edge-type="{edge}" '
                    f'data-depth="{depth}"{open_attr}>'
                )
                parts.append(f"<summary>[{edge}] {summary_text}</summary>")
                parts.append('<div class="portal-content">')

                if node.is_expanded:
                    for child in node.children:
                        render_node(child, depth + 1)

                parts.append("</div></details>")
                return

            if node.is_expanded:
                for child in node.children:
                    render_node(child, depth + 1)

        render_node(outline.root)

        # Trail and budget in footer
        parts.append('<div class="outline-footer">')
        if outline.trail_steps:
            parts.append(
                f'<span class="trail-count">Trail: {len(outline.trail_steps)} steps</span>'
            )
        if outline.is_budget_low:
            parts.append(
                f'<span class="budget-warning">Budget: {outline.budget_remaining:.0%}</span>'
            )
        parts.append("</div>")

        parts.append("</div>")
        return "\n".join(parts)

    def _render_llm(self, outline: "Outline", config: RenderConfig) -> str:
        """
        Render for LLM context (0.6 fidelity).

        XML-tagged for reliable parsing, depth-limited for context windows.

        Format:
            <!-- OUTLINE: name -->
            <node path="root" type="snippet">
              Content here
            </node>
            <portal edge="tests" path="root.0" state="expanded">
              <node ...>
              </node>
            </portal>
            <!-- END OUTLINE -->
        """
        cfg = config.config
        lines: list[str] = [f"<!-- OUTLINE: {outline.id} -->"]

        def render_node(node: "OutlineNode", depth: int = 0) -> None:
            if depth > cfg["max_depth"]:
                lines.append(f"<!-- DEPTH LIMIT: skipping children at depth {depth} -->")
                return

            indent = cfg["indent"] * depth

            if node.snippet is not None:
                snippet_type = node.snippet.snippet_type.name.lower()
                lines.append(f'{indent}<node path="{node.path}" type="{snippet_type}">')
                # Escape content for XML
                content = node.snippet.visible_text.replace("&", "&amp;").replace("<", "&lt;")
                for line in content.split("\n"):
                    lines.append(f"{indent}  {line}")
                lines.append(f"{indent}</node>")

            elif node.portal is not None:
                portal = node.portal
                state = "expanded" if portal.expanded else "collapsed"
                lines.append(
                    f'{indent}<portal edge="{portal.edge_type}" '
                    f'path="{node.path}" state="{state}" count="{portal.destination_count}">'
                )

                if node.is_expanded and node.children:
                    for child in node.children:
                        render_node(child, depth + 1)
                else:
                    lines.append(f"{indent}  <!-- {portal.summary} -->")

                lines.append(f"{indent}</portal>")
                return

            if node.is_expanded:
                for child in node.children:
                    render_node(child, depth + 1)

        render_node(outline.root)

        # Metadata in comments
        lines.append(f"<!-- trail_length: {len(outline.trail_steps)} -->")
        lines.append(f"<!-- budget_remaining: {outline.budget_remaining:.2f} -->")
        lines.append("<!-- END OUTLINE -->")

        return "\n".join(lines)

    def _render_json(self, outline: "Outline", config: RenderConfig) -> str:
        """
        Render as JSON (1.0 fidelity).

        Full state serialization for programmatic access.
        """
        import json

        def node_to_dict(node: "OutlineNode") -> dict[str, Any]:
            result: dict[str, Any] = {
                "path": node.path,
                "depth": node.depth,
                "is_expanded": node.is_expanded,
            }

            if node.snippet is not None:
                result["type"] = "snippet"
                result["snippet_type"] = node.snippet.snippet_type.name
                result["visible_text"] = node.snippet.visible_text
                result["source_path"] = node.snippet.source_path
                result["links"] = node.snippet.links

            elif node.portal is not None:
                result["type"] = "portal"
                result["edge_type"] = node.portal.edge_type
                result["destinations"] = node.portal.destinations
                result["expanded"] = node.portal.expanded
                result["summary"] = node.portal.summary

            if node.children:
                result["children"] = [node_to_dict(c) for c in node.children]

            return result

        data = {
            "id": outline.id,
            "observer_id": outline.observer_id,
            "root": node_to_dict(outline.root),
            "trail_steps": outline.trail_steps,
            "steps_taken": outline.steps_taken,
            "max_steps": outline.max_steps,
            "budget_remaining": outline.budget_remaining,
            "created_at": outline.created_at.isoformat(),
        }

        return json.dumps(data, indent=2)


# === Convenience Functions ===


def render_outline(
    outline: "Outline",
    surface: Surface = Surface.CLI,
    **kwargs: Any,
) -> str:
    """
    Render an outline to the specified surface.

    Convenience function for quick rendering.

    Args:
        outline: The outline to render
        surface: Target surface (default: CLI)
        **kwargs: Additional config options

    Returns:
        Rendered string
    """
    renderer = OutlineRenderer()
    config = RenderConfig(surface=surface, **kwargs)
    return renderer.render(outline, surface, config)


def render_for_llm(
    outline: "Outline",
    max_depth: int = 4,
) -> str:
    """
    Render outline optimized for LLM context.

    Includes XML tags and depth limiting.

    Args:
        outline: The outline to render
        max_depth: Maximum depth to include

    Returns:
        XML-tagged outline string
    """
    renderer = OutlineRenderer()
    config = RenderConfig(surface=Surface.LLM, max_depth=max_depth)
    return renderer.render(outline, Surface.LLM, config)


__all__ = [
    "Surface",
    "RenderConfig",
    "OutlineRenderer",
    "render_outline",
    "render_for_llm",
    "SURFACE_CONFIG",
]
