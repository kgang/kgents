"""
AGENTESE Path Display Utilities.

Makes the categorical magic VISIBLE by showing AGENTESE paths on every CLI invocation.

Wave 0 Foundation 1: Path Visibility
- Users see `self.memory.capture` when they run `kg brain capture`
- Users learn AGENTESE naturally through usage
- Users can invoke paths directly once they learn them

The goal: AGENTESE becomes as natural as shell commands.

Usage:
    from protocols.cli.path_display import display_path_header, PathInfo

    # In a CLI handler:
    display_path_header(
        path="self.memory.capture",
        aspect="define",
        effects=["CRYSTAL_FORMED", "LINKS_CREATED"],
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

# Optional rich import for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

if TYPE_CHECKING:
    from typing import Literal

# Default console for CLI output
_console: "Console | None" = None


def _get_console() -> "Console":
    """Get or create the rich console."""
    global _console
    if _console is None and RICH_AVAILABLE:
        _console = Console()
    return _console  # type: ignore


# =============================================================================
# Data Types
# =============================================================================


@dataclass
class PathInfo:
    """Information about an AGENTESE path invocation."""

    path: str
    """The AGENTESE path (e.g., 'self.memory.capture')"""

    aspect: str = "manifest"
    """The aspect being invoked (manifest, witness, define, refine, sip, tithe, lens)"""

    observer: str = "default"
    """The observer context for this invocation"""

    effects: list[str] = field(default_factory=list)
    """Effects that may result from this invocation (e.g., CRYSTAL_FORMED)"""

    context: str | None = None
    """The context root (self, world, concept, void, time)"""

    def __post_init__(self) -> None:
        # Auto-detect context from path
        if self.context is None and "." in self.path:
            self.context = self.path.split(".")[0]


# =============================================================================
# Display Configuration
# =============================================================================


@dataclass
class PathDisplayConfig:
    """Configuration for path display behavior."""

    enabled: bool = True
    """Whether to show path headers at all"""

    verbose: bool = False
    """Whether to show extended info (effects, available aspects)"""

    show_tip: bool = True
    """Whether to show the 'invoke directly' tip"""

    use_color: bool = True
    """Whether to use colored output"""

    compact: bool = False
    """Use compact single-line format"""


# Global config (can be modified by CLI flags)
_config = PathDisplayConfig()


def set_path_display_config(
    enabled: bool | None = None,
    verbose: bool | None = None,
    show_tip: bool | None = None,
    use_color: bool | None = None,
    compact: bool | None = None,
) -> None:
    """Update the global path display configuration.

    Args:
        enabled: Enable/disable path headers
        verbose: Show extended information
        show_tip: Show the direct invocation tip
        use_color: Use colored output
        compact: Use compact single-line format
    """
    global _config
    if enabled is not None:
        _config.enabled = enabled
    if verbose is not None:
        _config.verbose = verbose
    if show_tip is not None:
        _config.show_tip = show_tip
    if use_color is not None:
        _config.use_color = use_color
    if compact is not None:
        _config.compact = compact


def get_path_display_config() -> PathDisplayConfig:
    """Get the current path display configuration."""
    return _config


# =============================================================================
# Context Styling
# =============================================================================

# Colors for each AGENTESE context
CONTEXT_COLORS = {
    "self": "cyan",
    "world": "green",
    "concept": "magenta",
    "void": "yellow",
    "time": "blue",
}

# Emoji for each context (for non-rich fallback)
CONTEXT_EMOJI = {
    "self": "",
    "world": "",
    "concept": "",
    "void": "",
    "time": "",
}

# Aspect descriptions
ASPECT_DESCRIPTIONS = {
    "manifest": "Collapse to observer's view",
    "witness": "Show history",
    "define": "Create/autopoiesis",
    "refine": "Dialectical challenge",
    "sip": "Draw from entropy",
    "tithe": "Pay for order",
    "lens": "Get composable agent",
}


# =============================================================================
# Display Functions
# =============================================================================


def display_path_header(
    path: str,
    aspect: str = "manifest",
    observer: str = "default",
    effects: list[str] | None = None,
    verbose: bool | None = None,
) -> None:
    """Display an AGENTESE path header before command output.

    This is the main entry point for making AGENTESE visible to users.

    Args:
        path: The AGENTESE path (e.g., 'self.memory.capture')
        aspect: The aspect being invoked
        observer: The observer context
        effects: List of potential effects (e.g., ['CRYSTAL_FORMED'])
        verbose: Override global verbose setting

    Example:
        >>> display_path_header(
        ...     path="self.memory.capture",
        ...     aspect="define",
        ...     effects=["CRYSTAL_FORMED", "LINKS_CREATED"],
        ... )

        self.memory.capture
        Aspect: define | Effects: CRYSTAL_FORMED, LINKS_CREATED

        Tip: Invoke directly: kg self.memory.capture --content "..."
    """
    if not _config.enabled:
        return

    info = PathInfo(
        path=path,
        aspect=aspect,
        observer=observer,
        effects=effects or [],
    )

    use_verbose = verbose if verbose is not None else _config.verbose

    if _config.compact:
        _display_compact(info)
    elif RICH_AVAILABLE and _config.use_color:
        _display_rich(info, use_verbose)
    else:
        _display_plain(info, use_verbose)


def _display_rich(info: PathInfo, verbose: bool) -> None:
    """Display path header with rich formatting."""
    from rich.markup import escape

    console = _get_console()

    # Get context color
    color = CONTEXT_COLORS.get(info.context or "", "white")

    # Build header text - escape special characters to prevent markup errors
    escaped_path = escape(info.path)
    header = Text()
    header.append(escaped_path, style=f"bold {color}")

    # Build body
    body_parts = [f"Aspect: {info.aspect}"]
    if info.observer != "default":
        body_parts.append(f"Observer: {info.observer}")
    if verbose and info.effects:
        body_parts.append(f"Effects: {', '.join(info.effects)}")

    body = Text(" | ".join(body_parts), style="dim")

    # Create panel - use Text object for title to avoid markup parsing
    panel = Panel(
        body,
        title=header,  # Pass Text object directly
        title_align="left",
        border_style=color,
        padding=(0, 1),
    )
    console.print(panel)

    # Show tip
    if _config.show_tip:
        tip = Text()
        tip.append("Tip: ", style="dim")
        tip.append(f"kg {escaped_path}", style=f"bold {color}")
        tip.append(" --help", style="dim")
        console.print(tip)
        console.print()


def _display_plain(info: PathInfo, verbose: bool) -> None:
    """Display path header without rich formatting."""
    emoji = CONTEXT_EMOJI.get(info.context or "", "")

    # Header line
    print(f"\n{emoji} {info.path}")
    print("-" * (len(info.path) + len(emoji) + 1))

    # Details
    parts = [f"Aspect: {info.aspect}"]
    if info.observer != "default":
        parts.append(f"Observer: {info.observer}")
    if verbose and info.effects:
        parts.append(f"Effects: {', '.join(info.effects)}")

    print(" | ".join(parts))

    # Tip
    if _config.show_tip:
        print(f"\nTip: kg {info.path} --help")
    print()


def _display_compact(info: PathInfo) -> None:
    """Display path header in compact single-line format."""
    CONTEXT_EMOJI.get(info.context or "", "")
    effects_str = f" [{', '.join(info.effects)}]" if info.effects else ""
    print(f"[{info.path}] {info.aspect}{effects_str}")


# =============================================================================
# CLI Flag Utilities
# =============================================================================


def parse_path_flags(args: list[str]) -> tuple[list[str], bool, bool]:
    """Parse path-related CLI flags from arguments.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (remaining_args, show_paths, trace_mode)

    Example:
        >>> parse_path_flags(["capture", "--show-paths", "content"])
        (['capture', 'content'], True, False)
    """
    show_paths = True  # Default on
    trace_mode = False
    remaining = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--show-paths":
            show_paths = True
            i += 1
        elif arg == "--no-paths":
            show_paths = False
            i += 1
        elif arg == "--trace":
            trace_mode = True
            i += 1
        else:
            remaining.append(arg)
            i += 1

    return remaining, show_paths, trace_mode


def apply_path_flags(show_paths: bool, trace_mode: bool) -> None:
    """Apply path-related flags to the global config.

    Args:
        show_paths: Whether to show path headers
        trace_mode: Whether to enable verbose/trace mode
    """
    set_path_display_config(enabled=show_paths, verbose=trace_mode)


# =============================================================================
# Path Mapping Utilities
# =============================================================================

# Mapping of CLI commands to AGENTESE paths
CLI_TO_PATH_MAP = {
    # Brain commands
    "brain": "self.memory",
    "brain capture": "self.memory.capture",
    "brain ghost": "self.memory.ghost.surface",
    "brain map": "self.memory.cartography.manifest",
    "brain status": "self.memory.manifest",
    "brain import": "self.memory.import",
    # Gestalt commands
    "world codebase": "world.codebase.manifest",
    "world codebase health": "world.codebase.health.manifest",
    "world codebase drift": "world.codebase.drift.witness",
    "world codebase module": "world.codebase.module.manifest",
    "world codebase scan": "world.codebase.manifest",
    # Gardener commands
    "gardener": "concept.gardener.manifest",
    "gardener session": "concept.gardener.session.manifest",
    # Void commands
    "tithe": "void.entropy.tithe",
    "sip": "void.entropy.sip",
}


def get_path_for_command(command: str, subcommand: str | None = None) -> str | None:
    """Get the AGENTESE path for a CLI command.

    Args:
        command: The main command (e.g., 'brain')
        subcommand: Optional subcommand (e.g., 'capture')

    Returns:
        The AGENTESE path or None if not mapped
    """
    if subcommand:
        key = f"{command} {subcommand}"
        if key in CLI_TO_PATH_MAP:
            return CLI_TO_PATH_MAP[key]

    return CLI_TO_PATH_MAP.get(command)


def get_aspect_for_subcommand(subcommand: str) -> str:
    """Infer the AGENTESE aspect from a subcommand.

    Args:
        subcommand: The CLI subcommand

    Returns:
        The inferred aspect
    """
    aspect_map = {
        # manifest aspects
        "status": "manifest",
        "show": "manifest",
        "list": "manifest",
        "get": "manifest",
        "map": "manifest",
        "health": "manifest",
        # witness aspects
        "ghost": "witness",
        "history": "witness",
        "drift": "witness",
        "log": "witness",
        # define aspects
        "capture": "define",
        "create": "define",
        "add": "define",
        "import": "define",
        "new": "define",
        # refine aspects
        "refine": "refine",
        "challenge": "refine",
        "update": "refine",
        # entropy aspects
        "tithe": "tithe",
        "sip": "sip",
    }
    return aspect_map.get(subcommand, "manifest")


# =============================================================================
# Test Utilities
# =============================================================================


def _reset_config() -> None:
    """Reset config to defaults (for testing)."""
    global _config
    _config = PathDisplayConfig()
