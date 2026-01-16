"""
Shared Help Utilities for CLI Handlers.

This module provides utilities for handlers to show help in a consistent manner.
It bridges the legacy projected help system with the new unified template system.

THREE WAYS TO ADD HELP TO A HANDLER:

1. SIMPLEST: Use @with_help decorator (automatic --help handling)
   ```python
   from protocols.cli.help_template import HelpSpec, with_help

   MY_HELP = HelpSpec(
       name="mycommand",
       description="Does something useful",
       usage="kg mycommand [options]",
       ...
   )

   @handler("mycommand", ...)
   @with_help(MY_HELP)
   def cmd_mycommand(args: list[str], ctx=None) -> int:
       # No need to check for --help, handled automatically
       ...
   ```

2. EXPLICIT: Use render_command_help in _print_help()
   ```python
   from protocols.cli.help_template import render_command_help

   def _print_help() -> None:
       render_command_help(
           name="mycommand",
           description="Does something useful",
           usage="kg mycommand [options]",
           subcommands=[...],
           examples=[...],
       )

   @handler("mycommand", ...)
   def cmd_mycommand(args: list[str], ctx=None) -> int:
       if "--help" in args or "-h" in args:
           _print_help()
           return 0
       ...
   ```

3. LEGACY: Use show_projected_help (for AGENTESE-derived help)
   ```python
   from protocols.cli.handlers._help import show_projected_help

   def _print_help() -> None:
       show_projected_help("self.memory", _print_help_fallback)
   ```

MIGRATION GUIDE:

Before (inconsistent):
    def _print_help() -> None:
        print('''
        kg brain - Holographic Brain (Crown Jewel Memory)

        Commands:
          kg brain capture "content"    Capture content...
        ''')

After (unified):
    from protocols.cli.help_template import HelpSpec, render_help

    BRAIN_HELP = HelpSpec(
        name="brain",
        description="Holographic memory operations",
        usage="kg brain [subcommand] [options]",
        subcommands=[
            ("capture", "Capture content to memory"),
            ("search", "Semantic search for similar memories"),
        ],
        examples=[
            'kg brain capture "Category theory is beautiful"',
        ],
    )

    def _print_help() -> None:
        render_help(BRAIN_HELP)

See: protocols/cli/help_template.py for full API documentation
"""

from __future__ import annotations

from typing import Callable

# Re-export template system for convenience
from protocols.cli.help_template import (
    COMMON_FLAGS,
    HelpSpec,
    OutputMode,
    help_spec,
    make_common_spec,
    render_command_help,
    render_help,
    show_help_for,
    with_help,
)


def show_projected_help(
    path: str,
    fallback: Callable[[], None] | None = None,
) -> None:
    """
    Show projected help for an AGENTESE path.

    Attempts to use the HelpProjector to derive help from affordances.
    Falls back to the provided fallback function if projection fails.

    This is the LEGACY approach. For new handlers, prefer:
    - @with_help decorator for automatic handling
    - render_command_help() for explicit help rendering

    Args:
        path: AGENTESE path (e.g., "self.soul", "world.town")
        fallback: Optional fallback function to call if projection fails
    """
    try:
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help as render_projected_help

        projector = create_help_projector()
        help_obj = projector.project(path)
        print(render_projected_help(help_obj))
    except Exception:
        if fallback:
            fallback()
        else:
            # Generic fallback
            print(f"Help for: {path}")
            print()
            print(f"  Use 'kg {path.replace('.', ' ')}' to invoke")
            print(f"  Use 'kg ?{path}.*' to discover subcommands")


def make_help_function(
    path: str,
    fallback_text: str,
) -> Callable[[], None]:
    """
    Create a _print_help function for a handler.

    This is a factory for creating standardized help functions that first
    try projected help, then fall back to static text.

    This is the LEGACY approach. For new handlers, prefer defining a HelpSpec
    and using render_help() or the @with_help decorator.

    Args:
        path: AGENTESE path
        fallback_text: Static help text to use if projection fails

    Returns:
        A function that prints help

    Example:
        _print_help = make_help_function(
            "self.soul",
            '''
            kg soul - Digital Consciousness

            Commands:
              kg soul reflect    K-gent reflection
              kg soul chat       Dialogue with K-gent
            '''
        )
    """

    def _print_help() -> None:
        def _fallback() -> None:
            print(fallback_text.strip())

        show_projected_help(path, _fallback)

    return _print_help


def make_help_from_spec(spec: HelpSpec) -> Callable[[], None]:
    """
    Create a _print_help function from a HelpSpec.

    This is the PREFERRED approach for new handlers.

    Args:
        spec: The HelpSpec defining the help content

    Returns:
        A function that prints help

    Example:
        BRAIN_HELP = HelpSpec(
            name="brain",
            description="Holographic memory operations",
            ...
        )

        _print_help = make_help_from_spec(BRAIN_HELP)
    """

    def _print_help() -> None:
        print(render_help(spec))

    return _print_help


def make_help_with_projection_fallback(
    spec: HelpSpec,
    agentese_path: str,
) -> Callable[[], None]:
    """
    Create a _print_help function that tries projection first, then uses HelpSpec.

    This combines the best of both worlds:
    - Dynamic help from AGENTESE affordances when available
    - Static HelpSpec as reliable fallback

    Args:
        spec: The HelpSpec to use as fallback
        agentese_path: AGENTESE path to try projecting first

    Returns:
        A function that prints help

    Example:
        BRAIN_HELP = HelpSpec(...)

        _print_help = make_help_with_projection_fallback(
            BRAIN_HELP,
            "self.memory",
        )
    """

    def _print_help() -> None:
        def _fallback() -> None:
            print(render_help(spec))

        show_projected_help(agentese_path, _fallback)

    return _print_help


# =============================================================================
# Pre-built Help Specs for Core Commands
# =============================================================================

# These specs can be imported by handlers for consistent help rendering.
# They serve as both working implementations and templates for new commands.

WITNESS_HELP = HelpSpec(
    name="witness",
    description="Everyday mark-making and memory crystallization",
    usage="kg witness [subcommand] [options]",
    philosophy="Every action leaves a mark. The mark IS the witness.",
    subcommands=(
        ("mark", "Create a mark"),
        ("show", "Show recent marks"),
        ("session", "Show this session's marks"),
        ("tree", "Show causal tree of marks"),
        ("crystallize", "Crystallize marks into insight"),
        ("crystals", "List recent crystals"),
        ("crystal", "Show crystal details"),
        ("expand", "Show crystal sources"),
        ("context", "Budget-aware crystal context"),
        ("dashboard", "Crystal visualization TUI"),
    ),
    flags=(
        ("--help, -h", "", "Show this help message"),
        ("--json", "", "Output as JSON"),
        ("-w, --why", "text", "Add reasoning to mark"),
        ("-p, --principles", "a,b", "Add principles to mark"),
        ("-t, --tag", "tag", "Add tag to mark"),
        ("--parent", "mark-id", "Link as child of parent"),
        ("--today", "", "Filter to today only"),
        ("--grep", "pattern", "Filter by content"),
        ("--budget", "int", "Token budget for context"),
    ),
    examples=(
        'kg witness mark "Refactored DI container"',
        'kg witness mark "Chose PostgreSQL" -w "Scaling needs"',
        "kg witness crystallize",
        "kg witness context --budget 1500",
        'km "Quick mark"',
    ),
    agentese_paths=(
        "time.witness.mark",
        "time.witness.show",
        "time.witness.crystallize",
    ),
    related=("brain", "docs", "coffee"),
    footer="Marks are observations. Crystals are insights. An action with a mark is agency.",
)

COFFEE_HELP = HelpSpec(
    name="coffee",
    description="Morning Coffee - Liminal transition protocol from rest to work",
    usage="kg coffee [subcommand] [options]",
    philosophy="The musician doesn't start with the hardest passage. She tunes, breathes, plays a scale.",
    subcommands=(
        ("garden", "Movement 1: What grew while I slept?"),
        ("weather", "Movement 2: What's shifting in the atmosphere?"),
        ("menu", "Movement 3: What suits my taste this morning?"),
        ("capture", "Movement 4: Fresh voice capture"),
        ("begin", "Complete ritual, transition to work"),
        ("history", "View past voice captures"),
    ),
    flags=(
        ("--help, -h", "", "Show this help message"),
        ("--json", "", "Output as JSON"),
        ("--quick", "", "Garden + Menu only (skip Weather/Capture)"),
        ("--full", "", "Interactive guided ritual (all 4 movements)"),
        ("--trace", "", "Show AGENTESE path being invoked"),
    ),
    examples=(
        "kg coffee",
        "kg coffee --quick",
        "kg coffee garden",
        "kg coffee capture",
        'kg coffee begin "ASHC L0"',
    ),
    agentese_paths=(
        "time.coffee.manifest",
        "time.coffee.garden",
        "time.coffee.weather",
        "time.coffee.menu",
        "time.coffee.capture",
        "time.coffee.begin",
    ),
    related=("witness", "forest", "brain"),
    footer="The ritual serves the human, not vice versa. Exit anytime.",
)

BRAIN_HELP = HelpSpec(
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
        ("import", "Batch import content"),
        ("extinct", "Extinction protocol commands"),
    ),
    flags=(
        ("--help, -h", "", "Show this help message"),
        ("--json", "", "Output as JSON"),
        ("--trace", "", "Show AGENTESE path being invoked"),
        ("--limit", "int", "Limit number of results"),
    ),
    examples=(
        'kg brain capture "Category theory is beautiful"',
        'kg brain search "programming language"',
        "kg brain chat",
        "kg brain extinct wisdom services.town",
    ),
    agentese_paths=(
        "self.memory.manifest",
        "self.memory.capture",
        "self.memory.recall",
        "self.memory.ghost.surface",
        "void.extinct.list",
        "void.extinct.wisdom",
    ),
    related=("witness", "docs"),
    footer="The Brain remembers so you don't have to.",
)

DOCS_HELP = HelpSpec(
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
        ("--module", "pattern", "Filter by module pattern"),
        ("--strict", "", "Exit 1 if issues found"),
        ("--changed", "", "Lint only git-changed files"),
        ("--dry-run", "", "Preview without persisting"),
        ("--no-ghosts", "", "Skip ancestral wisdom"),
    ),
    examples=(
        "kg docs generate --output docs/reference/",
        "kg docs teaching --severity critical",
        'kg docs hydrate "implement wasm projector"',
        "kg docs relevant services/brain/persistence.py",
        "kg docs crystallize --dry-run",
    ),
    agentese_paths=(
        "concept.docs.manifest",
        "concept.docs.generate",
        "concept.docs.teaching",
        "concept.docs.lint",
        "concept.docs.hydrate",
    ),
    related=("brain", "witness"),
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Legacy API (still works, but prefer new approach)
    "show_projected_help",
    "make_help_function",
    # New unified API (preferred)
    "HelpSpec",
    "OutputMode",
    "render_help",
    "render_command_help",
    "help_spec",
    "show_help_for",
    "with_help",
    "make_common_spec",
    "COMMON_FLAGS",
    # Helpers
    "make_help_from_spec",
    "make_help_with_projection_fallback",
    # Pre-built specs
    "WITNESS_HELP",
    "COFFEE_HELP",
    "BRAIN_HELP",
    "DOCS_HELP",
]
