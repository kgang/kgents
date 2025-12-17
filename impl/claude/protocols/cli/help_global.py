"""
Global Help - Overview of All Command Families.

This module generates the global help output shown when running
`kg --help` or `kgents --help`.

It organizes commands into families based on the kgents architecture:
- Crown Jewels (primary experiences)
- Forest Protocol (project health)
- Joy Commands (serendipity)
- Developer Tools (debugging, tracing)

The help is derived from registered affordances when possible,
ensuring accuracy without maintaining duplicate documentation.
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.agentese.logos import Logos

# === Command Families ===

# Organized by user-facing family, not implementation structure
COMMAND_FAMILIES = [
    (
        "Crown Jewels",
        "Primary experiences - where the magic happens",
        [
            ("brain", "self.memory", "Holographic memory operations"),
            ("soul", "self.soul", "Digital consciousness dialogue"),
            ("town", "world.town", "Agent simulation and coalitions"),
            ("park", "world.park", "Punchdrunk-style experiences"),
            ("atelier", "world.atelier", "Collaborative creative workshops"),
            ("gardener", "self.forest.gardener", "Development session management"),
        ],
    ),
    (
        "Forest Protocol",
        "Project health and cultivation",
        [
            ("forest", "self.forest", "Project health and plan status"),
            ("garden", "self.forest.garden", "Hypnagogia and dream states"),
            ("tend", "self.forest.tend", "Garden tending operations"),
        ],
    ),
    (
        "Joy Commands",
        "Serendipity and creative disruption",
        [
            ("joy", "void.joy", "Oblique strategies gateway"),
            ("oblique", "void.joy.oblique", "Draw an oblique strategy card"),
            ("surprise-me", "void.joy.surprise", "Unexpected creative prompt"),
            ("challenge", "void.joy.challenge", "Creative challenge generator"),
        ],
    ),
    (
        "Direct AGENTESE",
        "Advanced path invocation",
        [
            ("query <pattern>", "q", "Query paths (e.g., kg q self.*)"),
            ("-i", "repl", "Interactive AGENTESE REPL"),
            ("path.to.aspect", "invoke", "Direct aspect invocation"),
        ],
    ),
]


# === Global Help Renderer ===


def render_global_help(
    *,
    use_rich: bool | None = None,
    show_paths: bool = False,
) -> str:
    """
    Render the global help message.

    Args:
        use_rich: Force Rich (True) or plain (False). None = auto-detect.
        show_paths: Show AGENTESE paths in output

    Returns:
        Formatted global help string
    """
    if use_rich is None:
        use_rich = _can_use_rich()

    if use_rich:
        try:
            return _render_global_rich(show_paths=show_paths)
        except ImportError:
            pass

    return _render_global_plain(show_paths=show_paths)


def _render_global_rich(show_paths: bool = False) -> str:
    """Render global help with Rich formatting."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    # Header
    console.print()
    console.print(
        Panel(
            "[bold cyan]kgents[/] - Tasteful, curated, ethical agents",
            subtitle="[dim]The verb is the noun in motion[/]",
            width=60,
        )
    )

    # Command families
    for family_name, family_desc, commands in COMMAND_FAMILIES:
        console.print()
        console.print(f"[bold magenta]{family_name}[/] [dim]- {family_desc}[/]")

        for cmd, path, desc in commands:
            if show_paths:
                console.print(f"  [cyan]kg {cmd:18}[/] [dim]{path:30}[/] {desc}")
            else:
                console.print(f"  [cyan]kg {cmd:18}[/] {desc}")

    # Footer
    console.print()
    console.print("[dim]Usage:[/]")
    console.print("  [cyan]kg <command>[/]          Run a command")
    console.print("  [cyan]kg <command> --help[/]   Get command help")
    console.print("  [cyan]kg -i[/]                 Interactive REPL")
    console.print("  [cyan]kg q <pattern>[/]        Query paths (e.g., kg q 'self.*')")
    console.print()
    console.print("[dim]Examples:[/]")
    console.print('  [dim]$[/] kg brain capture "Category theory is beautiful"')
    console.print("  [dim]$[/] kg soul reflect")
    console.print("  [dim]$[/] kg town inhabit alice")
    console.print("  [dim]$[/] kg q 'self.*'")
    console.print()
    console.print("[dim]Learn more:[/] https://github.com/kgents/kgents")
    console.print()

    return buffer.getvalue()


def _render_global_plain(show_paths: bool = False) -> str:
    """Render global help as plain text."""
    lines: list[str] = []

    # Header
    lines.append("")
    lines.append("kgents - Tasteful, curated, ethical agents")
    lines.append("")

    # Command families
    for family_name, family_desc, commands in COMMAND_FAMILIES:
        lines.append(f"{family_name} - {family_desc}")

        for cmd, path, desc in commands:
            if show_paths:
                lines.append(f"  kg {cmd:18} {path:30} {desc}")
            else:
                lines.append(f"  kg {cmd:18} {desc}")

        lines.append("")

    # Footer
    lines.append("Usage:")
    lines.append("  kg <command>          Run a command")
    lines.append("  kg <command> --help   Get command help")
    lines.append("  kg -i                 Interactive REPL")
    lines.append("  kg q <pattern>        Query paths (e.g., kg q 'self.*')")
    lines.append("")
    lines.append("Examples:")
    lines.append('  $ kg brain capture "Category theory is beautiful"')
    lines.append("  $ kg soul reflect")
    lines.append("  $ kg town inhabit alice")
    lines.append("  $ kg q 'self.*'")
    lines.append("")
    lines.append("Learn more: https://github.com/kgents/kgents")
    lines.append("")

    return "\n".join(lines)


def _can_use_rich() -> bool:
    """Check if Rich rendering is available and appropriate."""
    import sys

    if not sys.stdout.isatty():
        return False

    try:
        import rich  # noqa: F401
        return True
    except ImportError:
        return False


# === Entry Point for CLI ===


def show_global_help(show_paths: bool = False) -> int:
    """
    Display global help and return exit code.

    This is called by hollow.py when `kg --help` is invoked.

    Args:
        show_paths: Whether to show AGENTESE paths

    Returns:
        Exit code (always 0)
    """
    print(render_global_help(show_paths=show_paths))
    return 0


__all__ = [
    "COMMAND_FAMILIES",
    "render_global_help",
    "show_global_help",
]
