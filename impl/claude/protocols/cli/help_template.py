"""
Unified Help Template System for kgents CLI.

This module provides a standardized way to render command help across the CLI,
ensuring consistency breeds confidence and every help screen feels like the
same product.

Design Principles:
- Consistency breeds confidence
- Progressive disclosure: simple usage first, details below
- Every help screen should feel like the same product

Standard Sections (in order):
1. Philosophy quote (optional, for Crown Jewels)
2. Description (1-2 sentences)
3. Usage syntax
4. Subcommands table (if any)
5. Flags table (if any)
6. Examples (2-3)
7. AGENTESE paths (for context commands)
8. Related commands

Usage:
    from protocols.cli.help_template import HelpSpec, render_command_help

    # Simple: just call the render function
    render_command_help(
        name="brain",
        description="Holographic memory operations",
        usage="kg brain [subcommand] [options]",
        subcommands=[
            ("capture", "Capture content to memory"),
            ("search", "Semantic search for similar memories"),
        ],
        examples=[
            'kg brain capture "Category theory is beautiful"',
            'kg brain search "programming language"',
        ],
    )

    # Or define a HelpSpec for reuse
    BRAIN_HELP = HelpSpec(
        name="brain",
        description="Holographic memory operations",
        philosophy="Every memory is a seed waiting to bloom.",
        usage="kg brain [subcommand] [options]",
        ...
    )
    render_help(BRAIN_HELP)

Migration Guide:
    # Before (inconsistent _print_help):
    def _print_help() -> None:
        print('''
        kg brain - Holographic Brain (Crown Jewel Memory)
        ...
        ''')

    # After (unified template):
    from protocols.cli.help_template import HelpSpec, render_help

    BRAIN_HELP = HelpSpec(...)

    def _print_help() -> None:
        render_help(BRAIN_HELP)

See: cli-renaissance.md
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from io import StringIO
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

F = TypeVar("F", bound=Callable[..., Any])


# =============================================================================
# Help Specification Dataclass
# =============================================================================


class OutputMode(Enum):
    """Output mode for help rendering."""

    RICH = "rich"
    PLAIN = "plain"
    JSON = "json"


@dataclass(frozen=True)
class HelpSpec:
    """
    Specification for command help content.

    This dataclass defines all the content that can appear in a help screen.
    Use this for commands with complex help that you want to define statically.

    Attributes:
        name: Command name (e.g., "brain", "witness")
        description: 1-2 sentence description of what the command does
        usage: Usage syntax (e.g., "kg brain [subcommand] [options]")
        philosophy: Optional opening quote/philosophy for Crown Jewels
        subcommands: List of (name, description) tuples
        flags: List of (flag, type_hint, description) tuples
        examples: List of example command strings
        agentese_paths: List of AGENTESE paths this command maps to
        related: List of related command names
        footer: Optional footer text (tips, philosophy)
    """

    name: str
    description: str
    usage: str
    philosophy: str | None = None
    subcommands: tuple[tuple[str, str], ...] = ()
    flags: tuple[tuple[str, str, str], ...] = ()
    examples: tuple[str, ...] = ()
    agentese_paths: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    footer: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "name": self.name,
            "description": self.description,
            "usage": self.usage,
            "philosophy": self.philosophy,
            "subcommands": [{"name": n, "description": d} for n, d in self.subcommands],
            "flags": [{"flag": f, "type": t, "description": d} for f, t, d in self.flags],
            "examples": list(self.examples),
            "agentese_paths": list(self.agentese_paths),
            "related": list(self.related),
            "footer": self.footer,
        }


# =============================================================================
# Output Mode Detection
# =============================================================================


def _can_use_rich() -> bool:
    """Check if Rich rendering is available and appropriate."""
    if not sys.stdout.isatty():
        return False

    try:
        import rich  # noqa: F401

        return True
    except ImportError:
        return False


def _detect_output_mode(force_mode: OutputMode | None = None) -> OutputMode:
    """Detect the appropriate output mode."""
    if force_mode is not None:
        return force_mode

    if _can_use_rich():
        return OutputMode.RICH

    return OutputMode.PLAIN


# =============================================================================
# Rich Renderer
# =============================================================================


def _render_rich(spec: HelpSpec) -> str:
    """Render help with Rich formatting."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    # Philosophy quote (if present)
    if spec.philosophy:
        console.print()
        console.print(f'[dim italic]"{spec.philosophy}"[/dim italic]')
        console.print()

    # Header with name and description
    header_text = Text()
    header_text.append(f"kg {spec.name}", style="bold cyan")
    header_text.append(" - ", style="dim")
    header_text.append(spec.description)
    console.print(header_text)
    console.print()

    # Usage
    console.print("[bold]USAGE[/bold]")
    console.print(f"  [cyan]{spec.usage}[/cyan]")
    console.print()

    # Subcommands table
    if spec.subcommands:
        console.print("[bold]COMMANDS[/bold]")
        for cmd_name, cmd_desc in spec.subcommands:
            console.print(f"  [cyan]{cmd_name:24}[/cyan] {cmd_desc}")
        console.print()

    # Flags table
    if spec.flags:
        console.print("[bold]OPTIONS[/bold]")
        for flag, type_hint, flag_desc in spec.flags:
            if type_hint:
                console.print(f"  [cyan]{flag:24}[/cyan] [dim]<{type_hint}>[/dim]  {flag_desc}")
            else:
                console.print(f"  [cyan]{flag:24}[/cyan] {flag_desc}")
        console.print()

    # Examples
    if spec.examples:
        console.print("[bold]EXAMPLES[/bold]")
        for example in spec.examples:
            console.print(f"  [dim]$[/dim] {example}")
        console.print()

    # AGENTESE paths
    if spec.agentese_paths:
        console.print("[bold]AGENTESE PATHS[/bold]")
        for path in spec.agentese_paths:
            console.print(f"  [magenta]{path}[/magenta]")
        console.print()

    # Related commands
    if spec.related:
        related_str = ", ".join(f"[cyan]kg {r}[/cyan]" for r in spec.related)
        console.print(f"[bold]SEE ALSO[/bold]  {related_str}")
        console.print()

    # Footer
    if spec.footer:
        console.print(f"[dim]{spec.footer}[/dim]")
        console.print()

    return buffer.getvalue()


# =============================================================================
# Plain Text Renderer
# =============================================================================


def _render_plain(spec: HelpSpec) -> str:
    """Render help as plain text."""
    lines: list[str] = []

    # Philosophy quote (if present)
    if spec.philosophy:
        lines.append("")
        lines.append(f'"{spec.philosophy}"')
        lines.append("")

    # Header with name and description
    lines.append(f"kg {spec.name} - {spec.description}")
    lines.append("")

    # Usage
    lines.append("USAGE")
    lines.append(f"  {spec.usage}")
    lines.append("")

    # Subcommands table
    if spec.subcommands:
        lines.append("COMMANDS")
        for cmd_name, cmd_desc in spec.subcommands:
            lines.append(f"  {cmd_name:24} {cmd_desc}")
        lines.append("")

    # Flags table
    if spec.flags:
        lines.append("OPTIONS")
        for flag, type_hint, flag_desc in spec.flags:
            if type_hint:
                lines.append(f"  {flag:24} <{type_hint}>  {flag_desc}")
            else:
                lines.append(f"  {flag:24} {flag_desc}")
        lines.append("")

    # Examples
    if spec.examples:
        lines.append("EXAMPLES")
        for example in spec.examples:
            lines.append(f"  $ {example}")
        lines.append("")

    # AGENTESE paths
    if spec.agentese_paths:
        lines.append("AGENTESE PATHS")
        for path in spec.agentese_paths:
            lines.append(f"  {path}")
        lines.append("")

    # Related commands
    if spec.related:
        related_str = ", ".join(f"kg {r}" for r in spec.related)
        lines.append(f"SEE ALSO  {related_str}")
        lines.append("")

    # Footer
    if spec.footer:
        lines.append(spec.footer)
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# JSON Renderer
# =============================================================================


def _render_json(spec: HelpSpec) -> str:
    """Render help as JSON for machine consumption."""
    return json.dumps(spec.to_dict(), indent=2)


# =============================================================================
# Main Render Functions
# =============================================================================


def render_help(
    spec: HelpSpec,
    *,
    mode: OutputMode | None = None,
) -> str:
    """
    Render help from a HelpSpec.

    Args:
        spec: The HelpSpec defining the help content
        mode: Force a specific output mode (auto-detect if None)

    Returns:
        Formatted help string
    """
    output_mode = _detect_output_mode(mode)

    if output_mode == OutputMode.JSON:
        return _render_json(spec)
    elif output_mode == OutputMode.RICH:
        try:
            return _render_rich(spec)
        except ImportError:
            return _render_plain(spec)
    else:
        return _render_plain(spec)


def render_command_help(
    name: str,
    description: str,
    usage: str,
    subcommands: list[tuple[str, str]] | None = None,
    flags: list[tuple[str, str, str]] | None = None,
    examples: list[str] | None = None,
    agentese_paths: list[str] | None = None,
    philosophy: str | None = None,
    related: list[str] | None = None,
    footer: str | None = None,
    *,
    mode: OutputMode | None = None,
) -> None:
    """
    Unified help renderer for all commands.

    This is the primary API for rendering help. It creates a HelpSpec internally
    and renders it, printing the result to stdout.

    Args:
        name: Command name (e.g., "brain", "witness")
        description: 1-2 sentence description
        usage: Usage syntax
        subcommands: List of (name, description) tuples
        flags: List of (flag, type_hint, description) tuples
        examples: List of example command strings
        agentese_paths: List of AGENTESE paths
        philosophy: Optional opening quote (for Crown Jewels)
        related: List of related command names
        footer: Optional footer text
        mode: Force output mode (auto-detect if None)

    Example:
        render_command_help(
            name="brain",
            description="Holographic memory operations",
            usage="kg brain [subcommand] [options]",
            subcommands=[
                ("capture", "Capture content to memory"),
                ("search", "Semantic search for similar memories"),
            ],
            flags=[
                ("--help, -h", "", "Show this help message"),
                ("--json", "", "Output as JSON"),
            ],
            examples=[
                'kg brain capture "Category theory is beautiful"',
                'kg brain search "programming language"',
            ],
            agentese_paths=[
                "self.memory.manifest",
                "self.memory.capture",
            ],
        )
    """
    spec = HelpSpec(
        name=name,
        description=description,
        usage=usage,
        philosophy=philosophy,
        subcommands=tuple(subcommands or []),
        flags=tuple(flags or []),
        examples=tuple(examples or []),
        agentese_paths=tuple(agentese_paths or []),
        related=tuple(related or []),
        footer=footer,
    )

    print(render_help(spec, mode=mode))


# =============================================================================
# Help Decorator
# =============================================================================


def help_spec(spec: HelpSpec) -> Callable[[F], F]:
    """
    Decorator to attach a HelpSpec to a handler function.

    This decorator attaches the help specification to the function,
    allowing automatic help rendering when --help is passed.

    Usage:
        BRAIN_HELP = HelpSpec(
            name="brain",
            description="Holographic memory operations",
            ...
        )

        @help_spec(BRAIN_HELP)
        def cmd_brain(args: list[str], ctx=None) -> int:
            if "--help" in args or "-h" in args:
                # Help rendering is handled by the decorator
                return show_help_for(cmd_brain)
            ...

    Args:
        spec: The HelpSpec to attach

    Returns:
        Decorated function with _help_spec attribute
    """

    def decorator(fn: F) -> F:
        setattr(fn, "_help_spec", spec)
        return fn

    return decorator


def show_help_for(fn: Callable[..., Any], mode: OutputMode | None = None) -> int:
    """
    Show help for a function that has a _help_spec attribute.

    Args:
        fn: Function with _help_spec attribute
        mode: Force output mode

    Returns:
        Exit code (always 0)
    """
    spec = getattr(fn, "_help_spec", None)
    if spec is None:
        print(f"No help available for {fn.__name__}")
        return 1

    print(render_help(spec, mode=mode))
    return 0


def with_help(spec: HelpSpec) -> Callable[[F], F]:
    """
    Decorator that automatically handles --help/-h flags.

    This is a convenience decorator that combines @help_spec with automatic
    help flag handling. Use this when you want the simplest possible integration.

    Usage:
        BRAIN_HELP = HelpSpec(...)

        @with_help(BRAIN_HELP)
        def cmd_brain(args: list[str], ctx=None) -> int:
            # No need to check for --help, it's handled automatically
            ...

    Args:
        spec: The HelpSpec to use

    Returns:
        Decorated function that handles --help automatically
    """

    def decorator(fn: F) -> F:
        setattr(fn, "_help_spec", spec)

        @wraps(fn)
        def wrapper(args: list[str], ctx: "InvocationContext | None" = None) -> int:
            # Check for help flags
            if "--help" in args or "-h" in args:
                # Check for JSON mode
                mode = OutputMode.JSON if "--json" in args else None
                print(render_help(spec, mode=mode))
                return 0
            result = fn(args, ctx)
            return int(result) if result is not None else 0

        return wrapper  # type: ignore[return-value]

    return decorator


# =============================================================================
# Pre-built Help Specs for Common Commands
# =============================================================================

# These can be imported and used directly, or as templates for customization

COMMON_FLAGS: tuple[tuple[str, str, str], ...] = (
    ("--help, -h", "", "Show this help message"),
    ("--json", "", "Output as JSON"),
    ("--trace", "", "Show AGENTESE path being invoked"),
)


def make_common_spec(
    name: str,
    description: str,
    usage: str,
    subcommands: list[tuple[str, str]] | None = None,
    extra_flags: list[tuple[str, str, str]] | None = None,
    examples: list[str] | None = None,
    agentese_paths: list[str] | None = None,
    philosophy: str | None = None,
    related: list[str] | None = None,
) -> HelpSpec:
    """
    Create a HelpSpec with common flags pre-included.

    This is a convenience function for creating HelpSpecs that include
    the standard --help, --json, and --trace flags.

    Args:
        name: Command name
        description: 1-2 sentence description
        usage: Usage syntax
        subcommands: List of (name, description) tuples
        extra_flags: Additional flags beyond the common ones
        examples: List of example strings
        agentese_paths: AGENTESE paths
        philosophy: Optional philosophy quote
        related: Related commands

    Returns:
        HelpSpec with common flags included
    """
    all_flags = list(COMMON_FLAGS)
    if extra_flags:
        all_flags.extend(extra_flags)

    return HelpSpec(
        name=name,
        description=description,
        usage=usage,
        philosophy=philosophy,
        subcommands=tuple(subcommands or []),
        flags=tuple(all_flags),
        examples=tuple(examples or []),
        agentese_paths=tuple(agentese_paths or []),
        related=tuple(related or []),
    )


# =============================================================================
# Example Help Specs (for reference and testing)
# =============================================================================

# Example Crown Jewel help spec (brain)
BRAIN_HELP_EXAMPLE = HelpSpec(
    name="brain",
    description="Holographic memory operations - capture, search, and recall",
    usage="kg brain [subcommand] [options]",
    philosophy="Every memory is a seed waiting to bloom.",
    subcommands=(
        ("capture", "Capture content to memory"),
        ("search", "Semantic search for similar memories"),
        ("ghost", "Surface memories from context"),
        ("surface", "Serendipity: random memory from the void"),
        ("chat", "Interactive chat with holographic memory"),
        ("list", "List recent memories"),
        ("status", "Show brain status"),
        ("extinct", "Extinction protocol commands"),
    ),
    flags=(
        ("--help, -h", "", "Show this help message"),
        ("--json", "", "Output as JSON"),
        ("--trace", "", "Show AGENTESE path being invoked"),
        ("--limit", "int", "Limit number of results"),
    ),
    examples=(
        'kg brain capture "Python is great for data science"',
        'kg brain search "programming language"',
        "kg brain chat",
        "kg brain extinct wisdom services.town",
    ),
    agentese_paths=(
        "self.memory.manifest",
        "self.memory.capture",
        "self.memory.recall",
        "void.extinct.list",
        "void.extinct.wisdom",
    ),
    related=("witness", "docs"),
    footer="The Brain remembers so you don't have to.",
)

# Example simple command help spec (docs)
DOCS_HELP_EXAMPLE = HelpSpec(
    name="docs",
    description="Living documentation generator - extract and query teaching moments",
    usage="kg docs [subcommand] [options]",
    subcommands=(
        ("generate", "Generate reference documentation"),
        ("teaching", "Query teaching moments (gotchas)"),
        ("verify", "Verify evidence links exist"),
        ("lint", "Lint for missing docstrings"),
        ("hydrate", "Generate context for a task"),
        ("relevant", "Show gotchas relevant to a file"),
        ("crystallize", "Persist teaching moments to Brain"),
    ),
    flags=(
        ("--help, -h", "", "Show this help message"),
        ("--json", "", "Output as JSON"),
        ("--output", "dir", "Output directory"),
        ("--overwrite", "", "Overwrite existing files"),
        ("--severity", "level", "Filter by severity (critical, warning, info)"),
        ("--strict", "", "Exit 1 if issues found"),
    ),
    examples=(
        "kg docs generate --output docs/reference/",
        "kg docs teaching --severity critical",
        'kg docs hydrate "implement wasm projector"',
    ),
    agentese_paths=(
        "concept.docs.manifest",
        "concept.docs.generate",
        "concept.docs.teaching",
    ),
    related=("brain", "witness"),
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "HelpSpec",
    "OutputMode",
    # Render functions
    "render_help",
    "render_command_help",
    # Decorators
    "help_spec",
    "show_help_for",
    "with_help",
    # Utilities
    "make_common_spec",
    "COMMON_FLAGS",
    # Examples (for reference)
    "BRAIN_HELP_EXAMPLE",
    "DOCS_HELP_EXAMPLE",
]
