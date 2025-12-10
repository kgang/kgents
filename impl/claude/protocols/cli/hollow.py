"""
The Hollow Shell - Fast CLI entry point with lazy loading.

This module implements the "Hollow Shell" pattern from docs/cli-integration-plan.md:
- Zero heavy imports at module level
- Command registry maps commands to module paths (not imports)
- Lazy resolution only when command is invoked
- Target: `kgents --help` < 50ms

The Hollow Shell is the membrane between intent and action.
It must be fast enough to feel like no interface at all.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable, Sequence

# =============================================================================
# Version & Constants
# =============================================================================

__version__ = "0.2.0"

# Help text (no imports required)
HELP_TEXT = """\
kgents - Kent's Agents CLI

USAGE:
  kgents <command> [args...]
  kgents <command> --help

INTENT LAYER (learn these 10 verbs):
  new       Create something (agent, flow, tongue)
  run       Execute an intent
  check     Verify target against principles/laws
  think     Generate hypotheses about a topic
  watch     Observe without judgment
  find      Search the catalog
  fix       Repair malformed input
  speak     Create a domain language (Tongue)
  judge     Evaluate against the 7 principles
  do        Natural language intent router

PROTOCOLS:
  mirror    Mirror Protocol - dialectical introspection
  membrane  Membrane Protocol - topological perception
  flow      Flowfile engine for composition

COMPANIONS (0 tokens):
  pulse     1-line project health
  ground    Parse & reflect statement structure
  breathe   Contemplative pause
  entropy   Show session chaos budget

SCIENTIFIC (0 tokens):
  falsify   Find counterexamples to hypothesis
  conjecture Generate hypotheses from patterns
  rival     Steel-man opposing views
  sublate   Synthesize contradictions
  shadow    Surface suppressed concerns

WORKSPACE:
  init      Initialize .kgents workspace

BOOTSTRAP:
  laws      Display/verify category laws
  principles Display/check 7 design principles

VISUALIZATION:
  garden    I-gent stigmergic field (TUI)
  dash      TUI dashboard

OPTIONS:
  --version     Show version
  --help, -h    Show this help

For more: https://github.com/kgents/kgents
"""

# =============================================================================
# Command Registry (module paths, not imports)
# =============================================================================

# Format: 'command': 'module.path:function_name'
# Only the invoked command's module will be imported

COMMAND_REGISTRY: dict[str, str] = {
    # Intent Layer (Phase 6)
    "new": "protocols.cli.intent.commands:cmd_new",
    "run": "protocols.cli.intent.commands:cmd_run",
    "check": "protocols.cli.intent.commands:cmd_check",
    "think": "protocols.cli.intent.commands:cmd_think",
    "watch": "protocols.cli.intent.commands:cmd_watch",
    "find": "protocols.cli.intent.commands:cmd_find",
    "fix": "protocols.cli.intent.commands:cmd_fix",
    "speak": "protocols.cli.intent.commands:cmd_speak",
    "judge": "protocols.cli.intent.commands:cmd_judge",
    "do": "protocols.cli.intent.router:cmd_do",
    # Protocols (existing)
    "mirror": "protocols.cli.handlers.mirror:cmd_mirror",
    "membrane": "protocols.cli.handlers.membrane:cmd_membrane",
    # Flow Engine (Phase 3)
    "flow": "protocols.cli.flow.commands:cmd_flow",
    # Companions (existing - Tier 1)
    "pulse": "protocols.cli.handlers.companions:cmd_pulse",
    "ground": "protocols.cli.handlers.companions:cmd_ground",
    "breathe": "protocols.cli.handlers.companions:cmd_breathe",
    "entropy": "protocols.cli.handlers.companions:cmd_entropy",
    # Scientific (existing - Tier 2)
    "falsify": "protocols.cli.handlers.scientific:cmd_falsify",
    "conjecture": "protocols.cli.handlers.scientific:cmd_conjecture",
    "rival": "protocols.cli.handlers.scientific:cmd_rival",
    "sublate": "protocols.cli.handlers.scientific:cmd_sublate",
    "shadow": "protocols.cli.handlers.scientific:cmd_shadow",
    # Bootstrap (Phase 2)
    "init": "protocols.cli.handlers.init:cmd_init",
    "laws": "protocols.cli.bootstrap.laws:cmd_laws",
    "principles": "protocols.cli.bootstrap.principles:cmd_principles",
    # Genus Layer (Power User)
    "grammar": "protocols.cli.genus.g_gent:cmd_grammar",
    "jit": "protocols.cli.genus.j_gent:cmd_jit",
    "parse": "protocols.cli.genus.p_gent:cmd_parse",
    "library": "protocols.cli.genus.l_gent:cmd_library",
    "witness": "protocols.cli.genus.w_gent:cmd_witness",
    # Aliases (top-level shortcuts)
    "observe": "protocols.cli.handlers.membrane:cmd_observe",
    "sense": "protocols.cli.handlers.membrane:cmd_sense",
    "trace": "protocols.cli.handlers.membrane:cmd_trace",
    "touch": "protocols.cli.handlers.membrane:cmd_touch",
    "name": "protocols.cli.handlers.membrane:cmd_name",
    # I-gent
    "garden": "protocols.cli.handlers.igent:cmd_garden",
    "whisper": "protocols.cli.handlers.igent:cmd_whisper",
    # Debug
    "debug": "protocols.cli.handlers.debug:cmd_debug",
    # MCP (Phase 4)
    "mcp": "protocols.cli.mcp.server:cmd_mcp",
    # TUI Dashboard (Phase 7)
    "dash": "protocols.cli.tui.dashboard:cmd_dash",
}

# Commands that still need legacy fallback (deprecated - migrate these)
LEGACY_COMMANDS: set[str] = set()  # All migrated to hollow shell handlers


# =============================================================================
# Lazy Loading
# =============================================================================


def resolve_command(name: str) -> Callable | None:
    """
    Resolve command name to callable, importing only when needed.

    This is the heart of the Hollow Shell pattern:
    - We don't import any command modules at startup
    - We only import the specific module for the invoked command
    - This keeps startup time minimal
    """
    if name not in COMMAND_REGISTRY:
        return None

    module_path, func_name = COMMAND_REGISTRY[name].rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
        return getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        # Command registered but handler not found
        print(f"Error loading command '{name}': {e}")
        return None


# =============================================================================
# Fuzzy Matching (for typo suggestions)
# =============================================================================


def suggest_similar(command: str, max_suggestions: int = 3) -> list[str]:
    """
    Find commands similar to the mistyped command.
    Uses simple edit distance heuristic.
    """
    from difflib import get_close_matches

    all_commands = list(COMMAND_REGISTRY.keys())
    return get_close_matches(command, all_commands, n=max_suggestions, cutoff=0.5)


def print_suggestions(command: str) -> None:
    """Print helpful suggestions for unknown command."""
    suggestions = suggest_similar(command)

    print(f"Unknown command: {command}")
    print()

    if suggestions:
        print("Did you mean?")
        for s in suggestions:
            print(f"  kgents {s}")
        print()

    print("Run 'kgents --help' for available commands.")


# =============================================================================
# Context System (.kgents directory)
# =============================================================================


def find_kgents_root() -> Path | None:
    """
    Find the nearest .kgents directory (like git finding .git).

    Walks up from cwd looking for .kgents/.
    Returns the directory containing .kgents, or None if not found.
    """
    current = Path.cwd()

    while current != current.parent:
        if (current / ".kgents").is_dir():
            return current
        current = current.parent

    # Check root
    if (current / ".kgents").is_dir():
        return current

    return None


def load_context() -> dict:
    """
    Load context from .kgents/config.yaml if it exists.

    Returns empty dict if no context file found.
    This is intentionally lightweight - full parsing happens lazily.
    """
    root = find_kgents_root()
    if root is None:
        return {}

    config_path = root / ".kgents" / "config.yaml"
    if not config_path.exists():
        return {}

    # Lazy import yaml only if config exists
    try:
        import yaml

        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # PyYAML not installed, return empty
        return {}
    except Exception:
        # Config exists but failed to parse
        return {}


# =============================================================================
# Argument Parsing (Lightweight)
# =============================================================================


def parse_global_flags(args: list[str]) -> tuple[dict, list[str]]:
    """
    Parse global flags without importing argparse.

    Returns (flags, remaining_args).
    This is fast path for --help, --version.
    """
    flags = {
        "help": False,
        "version": False,
        "format": "rich",
        "budget": "medium",
        "persona": "minimal",
        "explain": False,
        "no_metrics": False,
    }
    remaining = []
    skip_next = False

    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue

        if arg in ("--help", "-h"):
            flags["help"] = True
        elif arg == "--version":
            flags["version"] = True
        elif arg == "--explain":
            flags["explain"] = True
        elif arg == "--no-metrics":
            flags["no_metrics"] = True
        elif arg.startswith("--format="):
            flags["format"] = arg.split("=", 1)[1]
        elif arg == "--format" and i + 1 < len(args):
            flags["format"] = args[i + 1]
            skip_next = True
        elif arg.startswith("--budget="):
            flags["budget"] = arg.split("=", 1)[1]
        elif arg == "--budget" and i + 1 < len(args):
            flags["budget"] = args[i + 1]
            skip_next = True
        elif arg.startswith("--persona="):
            flags["persona"] = arg.split("=", 1)[1]
        elif arg == "--persona" and i + 1 < len(args):
            flags["persona"] = args[i + 1]
            skip_next = True
        else:
            remaining.append(arg)

    return flags, remaining


# =============================================================================
# Main Entry Point
# =============================================================================


def main(argv: Sequence[str] | None = None) -> int:
    """
    The Hollow Shell entry point.

    Fast path:
    - --help: print help and exit (no imports)
    - --version: print version and exit (no imports)

    Normal path:
    - Parse command from first arg
    - Resolve to handler (lazy import)
    - Execute handler with remaining args
    """
    if argv is None:
        argv = sys.argv[1:]

    args = list(argv)

    # Parse global flags (fast, no imports)
    flags, remaining = parse_global_flags(args)

    # Fast path: --help
    if flags["help"] and not remaining:
        print(HELP_TEXT)
        return 0

    # Fast path: --version
    if flags["version"]:
        print(f"kgents {__version__}")
        return 0

    # No command given
    if not remaining:
        print(HELP_TEXT)
        return 0

    # Extract command
    command = remaining[0]
    command_args = remaining[1:]

    # Check for command-level help
    if flags["help"] or "--help" in command_args or "-h" in command_args:
        # Delegate to command handler for its own help
        handler = resolve_command(command)
        if handler:
            # Filter out help flags, let handler show its help
            filtered_args = [a for a in command_args if a not in ("--help", "-h")]
            return handler(["--help"] + filtered_args)
        else:
            print_suggestions(command)
            return 1

    # Resolve command
    handler = resolve_command(command)

    if handler is None:
        print_suggestions(command)
        return 1

    # Build context from .kgents/ and flags
    # This is passed to handler via environment or args
    # (Implementation detail for handlers)

    # Execute handler
    try:
        return handler(command_args)
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 130
    except Exception as e:
        # Sympathetic error handling (Phase 8)
        # For now, just print the error
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
