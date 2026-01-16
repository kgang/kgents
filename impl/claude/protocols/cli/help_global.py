"""
Global Help - Overview of All Command Families.

This module generates the global help output shown when running
`kg --help` or `kgents --help`.

It organizes commands into families telling a story:
  start here → work → explore → delight

Families (in order):
- Getting Started (new users begin here)
- Memory & Witness (capture and remember)
- Development (project health)
- AGENTESE Contexts (direct invocation)
- Utilities (tools and initialization)
- Joy (serendipity and delight)

Design: "Simplistic, brutalistic, dense, intelligent design"
Goal: New users should find `play` in < 30 seconds.
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.agentese.logos import Logos

# === Command Families ===

# Type: list of (family_name, family_desc, [(cmd, path, desc), ...])
CommandEntry = tuple[str, str | None, str]  # (command, agentese_path, description)
CommandFamily = tuple[str, str, list[CommandEntry]]

# Organized to tell a story: start here → work → explore → delight
# New users should find `play` in < 30 seconds
COMMAND_FAMILIES: list[CommandFamily] = [
    # === START HERE ===
    (
        "Getting Started",
        "New to kgents? Start here",
        [
            ("start", None, "Your starting point (new users begin here)"),
            ("play", None, "Interactive tutorials"),
            ("coffee", "time.coffee", "Morning ritual"),
        ],
    ),
    # === WORK ===
    (
        "Memory & Witness",
        "Capture, remember, decide",
        [
            ("brain", "self.memory", "Holographic memory operations"),
            ("witness", None, "Everyday mark-making"),
            ("decide", None, "Dialectical decision capture"),
        ],
    ),
    (
        "Crown Jewels",
        "Primary experiences - where the magic happens",
        [
            ("town", "world.town", "Agent simulation and interactions"),
            ("atelier", "world.atelier", "Collaborative creative workshops"),
        ],
    ),
    (
        "Development",
        "Project health and session management",
        [
            ("forest", "self.forest", "Project health and plan status"),
            ("session", "self.forest.session", "Session lifecycle management"),
            ("gardener", "concept.gardener", "Development session operations"),
            ("audit", None, "Validate specs against principles"),
        ],
    ),
    # === EXPLORE ===
    (
        "AGENTESE Contexts",
        "Direct path invocation",
        [
            ("query <pattern>", "q", "Query paths (e.g., kg q self.*)"),
            ("-i", "repl", "Interactive AGENTESE REPL"),
            ("path.to.aspect", "invoke", "Direct aspect invocation"),
        ],
    ),
    (
        "Utilities",
        "Tools and initialization",
        [
            ("docs", "concept.docs", "Living documentation generator"),
            ("init", None, "Initialize a kgents workspace"),
            ("garden", "self.forest.garden", "Hypnagogia and dream states"),
        ],
    ),
    # === DELIGHT ===
    (
        "Joy",
        "Delight and serendipity",
        [
            ("oblique", "void.oblique", "Draw an Oblique Strategy card"),
            ("surprise", "void.surprise", "Discover something unexpected"),
            ("challenge", "void.challenge", "Daily coding challenge"),
            ("yes-and", "void.yes-and", "Improv-style affirmation"),
            ("constrain", "void.constrain", "Random creative constraint"),
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

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    # Header - welcoming, mentions kg start
    console.print()
    console.print(
        Panel(
            "[bold cyan]kgents[/] - Tasteful, curated, ethical agents\n"
            "[dim]New here? Run [cyan]kg start[/cyan] or [cyan]kg play[/cyan] to begin.[/]",
            subtitle="[dim]The verb is the noun in motion[/]",
            width=60,
        )
    )

    # Command families - tell a story
    for family_name, family_desc, commands in COMMAND_FAMILIES:
        console.print()
        console.print(f"[bold magenta]{family_name}[/] [dim]- {family_desc}[/]")

        for cmd, path, desc in commands:
            # Handle None paths gracefully
            path_str = path if path else ""
            if show_paths and path_str:
                console.print(f"  [cyan]kg {cmd:18}[/] [dim]{path_str:30}[/] {desc}")
            else:
                console.print(f"  [cyan]kg {cmd:18}[/] {desc}")

    # Footer - simplified, focuses on getting started
    console.print()
    console.print("[dim]Quick Start:[/]")
    console.print("  [cyan]kg start[/]              Begin your journey")
    console.print("  [cyan]kg play[/]               Interactive tutorials")
    console.print("  [cyan]kg <command> --help[/]   Get command help")
    console.print()
    console.print("[dim]Examples:[/]")
    console.print("  [dim]$[/] kg start")
    console.print('  [dim]$[/] kg brain capture "Category theory is beautiful"')
    console.print("  [dim]$[/] kg oblique")
    console.print("  [dim]$[/] kg q 'self.*'")
    console.print()
    console.print("[dim]Learn more:[/] https://github.com/kgents/kgents")
    console.print()

    return buffer.getvalue()


def _render_global_plain(show_paths: bool = False) -> str:
    """Render global help as plain text."""
    lines: list[str] = []

    # Header - welcoming, mentions kg start
    lines.append("")
    lines.append("kgents - Tasteful, curated, ethical agents")
    lines.append("New here? Run `kg start` or `kg play` to begin.")
    lines.append("")

    # Command families - tell a story
    for family_name, family_desc, commands in COMMAND_FAMILIES:
        lines.append(f"{family_name} - {family_desc}")

        for cmd, path, desc in commands:
            # Handle None paths gracefully
            path_str = path if path else ""
            if show_paths and path_str:
                lines.append(f"  kg {cmd:18} {path_str:30} {desc}")
            else:
                lines.append(f"  kg {cmd:18} {desc}")

        lines.append("")

    # Footer - simplified, focuses on getting started
    lines.append("Quick Start:")
    lines.append("  kg start              Begin your journey")
    lines.append("  kg play               Interactive tutorials")
    lines.append("  kg <command> --help   Get command help")
    lines.append("")
    lines.append("Examples:")
    lines.append("  $ kg start")
    lines.append('  $ kg brain capture "Category theory is beautiful"')
    lines.append("  $ kg oblique")
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
