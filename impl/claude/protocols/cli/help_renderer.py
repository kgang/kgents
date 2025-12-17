"""
Help Renderer - Format CommandHelp for Terminal Output.

This module renders CommandHelp structures to terminal output.
Supports both Rich (colorful) and plain text rendering.

Usage:
    from protocols.cli.help_projector import HelpProjector, create_help_projector
    from protocols.cli.help_renderer import render_help

    projector = create_help_projector()
    help = projector.project("self.memory")
    print(render_help(help))

The renderer adapts to terminal capabilities:
- Rich formatting when rich is available and terminal supports it
- Plain text fallback for pipes, CI, or missing dependencies
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .help_projector import CommandHelp


# === Rich Rendering ===


def _render_rich(help: "CommandHelp") -> str:
    """
    Render help with Rich formatting.

    Produces colorful, well-formatted output for interactive terminals.
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    # Create console that writes to string buffer
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    # Title line
    console.print()
    console.print(f"[bold cyan]{help.title}[/] [dim]({help.path})[/]")
    console.print()

    # Description
    if help.description:
        console.print(f"  {help.description}")
        console.print()

    # Commands section
    if help.usage:
        console.print("[bold]Commands:[/]")
        for line in help.usage:
            console.print(f"  {line}")
        console.print()

    # Flags section
    if help.flags:
        console.print("[bold]Flags:[/]")
        for flag, desc in help.flags:
            console.print(f"  [green]{flag:25}[/] {desc}")
        console.print()

    # Examples section
    if help.examples:
        console.print("[bold]Examples:[/]")
        for ex in help.examples:
            console.print(f"  [dim]$[/] {ex}")
        console.print()

    # AGENTESE paths section (for direct invocation)
    if help.agentese_paths:
        console.print("[bold]AGENTESE Paths:[/]")
        for path in help.agentese_paths[:5]:  # Limit to 5
            console.print(f"  [yellow]{path}[/]")
        console.print()

    # Dimension hints (warnings, capabilities)
    if help.dimension_hints:
        for hint in help.dimension_hints:
            console.print(f"  {hint}")
        console.print()

    # Budget hint
    if help.budget_hint:
        console.print(f"  {help.budget_hint}")
        console.print()

    # See also
    if help.see_also:
        see_also_str = ", ".join(f"kg {cmd}" for cmd in help.see_also)
        console.print(f"[dim]See also:[/] {see_also_str}")
        console.print()

    return buffer.getvalue()


# === Plain Text Rendering ===


def _render_plain(help: "CommandHelp") -> str:
    """
    Render help as plain text.

    Produces simple, pipe-friendly output.
    """
    lines: list[str] = []

    # Title
    lines.append("")
    lines.append(f"{help.title} ({help.path})")
    lines.append("")

    # Description
    if help.description:
        lines.append(f"  {help.description}")
        lines.append("")

    # Commands
    if help.usage:
        lines.append("Commands:")
        for line in help.usage:
            lines.append(f"  {line}")
        lines.append("")

    # Flags
    if help.flags:
        lines.append("Flags:")
        for flag, desc in help.flags:
            lines.append(f"  {flag:25} {desc}")
        lines.append("")

    # Examples
    if help.examples:
        lines.append("Examples:")
        for ex in help.examples:
            lines.append(f"  $ {ex}")
        lines.append("")

    # AGENTESE paths
    if help.agentese_paths:
        lines.append("AGENTESE Paths:")
        for path in help.agentese_paths[:5]:
            lines.append(f"  {path}")
        lines.append("")

    # Dimension hints
    if help.dimension_hints:
        for hint in help.dimension_hints:
            lines.append(f"  {hint}")
        lines.append("")

    # Budget hint
    if help.budget_hint:
        lines.append(f"  {help.budget_hint}")
        lines.append("")

    # See also
    if help.see_also:
        see_also_str = ", ".join(f"kg {cmd}" for cmd in help.see_also)
        lines.append(f"See also: {see_also_str}")
        lines.append("")

    return "\n".join(lines)


# === JSON Rendering ===


def _render_json(help: "CommandHelp") -> str:
    """Render help as JSON."""
    import json

    return json.dumps(
        {
            "path": help.path,
            "title": help.title,
            "description": help.description,
            "usage": help.usage,
            "flags": [{"flag": f, "description": d} for f, d in help.flags],
            "examples": help.examples,
            "see_also": help.see_also,
            "budget_hint": help.budget_hint,
            "dimension_hints": help.dimension_hints,
            "agentese_paths": help.agentese_paths,
        },
        indent=2,
    )


# === Main Render Function ===


def render_help(
    help: "CommandHelp",
    *,
    use_rich: bool | None = None,
    json_output: bool = False,
) -> str:
    """
    Render CommandHelp to a string.

    Automatically selects Rich or plain text based on terminal
    capabilities unless explicitly specified.

    Args:
        help: The CommandHelp structure to render
        use_rich: Force Rich (True) or plain (False). None = auto-detect.
        json_output: Output as JSON instead of text

    Returns:
        Formatted help string

    Example:
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help = projector.project("self.memory")

        # Auto-detect terminal
        print(render_help(help))

        # Force plain text (for pipes)
        print(render_help(help, use_rich=False))

        # JSON for programmatic use
        print(render_help(help, json_output=True))
    """
    # JSON output
    if json_output:
        return _render_json(help)

    # Auto-detect Rich capability
    if use_rich is None:
        use_rich = _can_use_rich()

    # Render
    if use_rich:
        try:
            return _render_rich(help)
        except ImportError:
            return _render_plain(help)
    else:
        return _render_plain(help)


def _can_use_rich() -> bool:
    """Check if Rich rendering is available and appropriate."""
    import sys

    # Not a TTY - use plain
    if not sys.stdout.isatty():
        return False

    # Check Rich is available
    try:
        import rich  # noqa: F401
        return True
    except ImportError:
        return False


# === Compact Format (for command lists) ===


def render_command_list(
    commands: list[tuple[str, str, str]],
    *,
    use_rich: bool | None = None,
) -> str:
    """
    Render a list of commands in compact format.

    Args:
        commands: List of (command, path, description) tuples
        use_rich: Force Rich (True) or plain (False). None = auto-detect.

    Returns:
        Formatted command list

    Example:
        commands = [
            ("brain", "self.memory", "Holographic memory operations"),
            ("soul", "self.soul", "Digital consciousness dialogue"),
        ]
        print(render_command_list(commands))
    """
    if use_rich is None:
        use_rich = _can_use_rich()

    if use_rich:
        try:
            return _render_command_list_rich(commands)
        except ImportError:
            pass

    return _render_command_list_plain(commands)


def _render_command_list_rich(commands: list[tuple[str, str, str]]) -> str:
    """Render command list with Rich."""
    from rich.console import Console

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    for cmd, path, desc in commands:
        console.print(f"  [cyan]kg {cmd:15}[/] [dim]{path:25}[/] {desc}")

    return buffer.getvalue()


def _render_command_list_plain(commands: list[tuple[str, str, str]]) -> str:
    """Render command list as plain text."""
    lines = []
    for cmd, path, desc in commands:
        lines.append(f"  kg {cmd:15} {path:25} {desc}")
    return "\n".join(lines)


__all__ = [
    "render_help",
    "render_command_list",
]
