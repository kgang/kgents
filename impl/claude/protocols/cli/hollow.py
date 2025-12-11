"""
The Hollow Shell - Fast CLI entry point with lazy loading.

This module implements the "Hollow Shell" pattern from docs/cli-integration-plan.md:
- Zero heavy imports at module level
- Command registry maps commands to module paths (not imports)
- Lazy resolution only when command is invoked
- Target: `kgents --help` < 50ms

The Hollow Shell is the membrane between intent and action.
It must be fast enough to feel like no interface at all.

Auto-bootstrap: On startup, the cortex is automatically initialized via
LifecycleManager, enabling DB persistence and telemetry from the first command.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable, Sequence

# Global lifecycle manager (lazy-initialized)
_lifecycle_manager = None
_lifecycle_state = None

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
  membrane  Membrane Protocol - topological perception
  flow      Flowfile engine for composition

WORKSPACE:
  init      Initialize .kgents workspace
  wipe      Remove local/global/all databases (with confirmation)

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
    "membrane": "protocols.cli.handlers.membrane:cmd_membrane",
    # Flow Engine (Phase 3)
    "flow": "protocols.cli.flow.commands:cmd_flow",
    # Bootstrap (Phase 2)
    "init": "protocols.cli.handlers.init:cmd_init",
    "wipe": "protocols.cli.handlers.wipe:cmd_wipe",
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
    # DevEx V4 Phase 1 - Foundation
    "status": "protocols.cli.handlers.status:cmd_status",
    "dream": "protocols.cli.handlers.dream:cmd_dream",
    "map": "protocols.cli.handlers.map:cmd_map",
    "signal": "protocols.cli.handlers.signal:cmd_signal",
    # DevEx V4 Phase 2 - Sensorium
    "ghost": "protocols.cli.handlers.ghost:cmd_ghost",
    # K-Terrarium (Infrastructure)
    "infra": "protocols.cli.handlers.infra:cmd_infra",
    "exec": "protocols.cli.handlers.exec:cmd_exec",  # Q-gent execution
    "dev": "protocols.cli.handlers.dev:cmd_dev",  # Live reload dev mode
    # MCP (Phase 4)
    "mcp": "protocols.cli.mcp.server:cmd_mcp",
    # TUI Dashboard (Phase 7)
    "dash": "protocols.cli.tui.dashboard:cmd_dash",
}


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

    # Try to use sympathetic errors if available
    try:
        from protocols.cli.errors import command_not_found

        err = command_not_found(command, suggestions)
        print(err.render())
    except ImportError:
        # Fallback to simple output
        print(f"Unknown command: {command}")
        print()

        if suggestions:
            print("Did you mean?")
            for s in suggestions:
                print(f"  kgents {s}")
            print()

        print("Run 'kgents --help' for available commands.")


# =============================================================================
# Lifecycle Management (Auto-Bootstrap)
# =============================================================================


async def _bootstrap_cortex(project_path: Path | None = None):
    """
    Bootstrap the cortex asynchronously.

    This initializes the LifecycleManager and storage providers,
    enabling database persistence for all subsequent commands.

    Called automatically by main() unless --no-bootstrap is specified.
    """
    global _lifecycle_manager, _lifecycle_state

    if _lifecycle_manager is not None:
        return _lifecycle_state

    try:
        from protocols.cli.instance_db.lifecycle import LifecycleManager

        _lifecycle_manager = LifecycleManager()
        _lifecycle_state = await _lifecycle_manager.bootstrap(project_path)

        return _lifecycle_state
    except Exception as e:
        # Bootstrap failure shouldn't crash the CLI
        # Commands should work in degraded (DB-less) mode
        print(f"\033[33m[kgents]\033[0m Bootstrap warning: {e}", file=sys.stderr)
        return None


async def _shutdown_cortex():
    """Gracefully shutdown the cortex."""
    global _lifecycle_manager, _lifecycle_state

    if _lifecycle_manager is not None:
        await _lifecycle_manager.shutdown()
        _lifecycle_manager = None
        _lifecycle_state = None


def get_lifecycle_state():
    """
    Get the current lifecycle state.

    Returns None if bootstrap hasn't been called or failed.
    Handlers can use this to access storage providers.
    """
    return _lifecycle_state


def get_storage_provider():
    """
    Get the storage provider from the lifecycle state.

    Returns None if not bootstrapped or in DB-less mode.
    """
    if _lifecycle_state is None:
        return None
    return _lifecycle_state.storage_provider


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
        import yaml  # type: ignore

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
        "no_bootstrap": False,
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
        elif arg == "--no-bootstrap":
            flags["no_bootstrap"] = True
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

# Commands that don't need bootstrap (fast path)
NO_BOOTSTRAP_COMMANDS = {
    "help",
    "--help",
    "-h",
    "--version",
}


def _sync_bootstrap(project_path: Path | None = None, verbose: bool = False):
    """
    Bootstrap the cortex synchronously.

    Uses asyncio.run() to run the async bootstrap in a fresh event loop.
    This must be called BEFORE any handler that might create its own event loop.

    Principle: Infrastructure work should always communicate what's happening.
    Users should never wonder "what is this doing?" during startup.
    """
    import asyncio

    try:
        state = asyncio.run(_bootstrap_cortex(project_path))

        # User-facing messaging: tell the user what happened
        if state is not None:
            if verbose:
                # Verbose mode: full details
                mode_desc = {
                    "db_less": "in-memory (no persistence)",
                    "local": "project-local DB",
                    "global": "global DB (~/.local/share/kgents/)",
                    "full": "global + project DB",
                }
                mode_str = mode_desc.get(state.mode.value, state.mode.value)
                print(
                    f"\033[90m[cortex]\033[0m Initialized: {mode_str} "
                    f"| instance={state.instance_id[:8] if state.instance_id else 'none'}",
                    file=sys.stderr,
                )
            elif state.mode.value == "db_less":
                # Always warn about DB-less mode (already handled in lifecycle.py)
                pass
            # Normal mode: silent success (no noise)

        return state
    except Exception as e:
        print(f"\033[33m[kgents]\033[0m Bootstrap warning: {e}", file=sys.stderr)
        return None


def _sync_shutdown(verbose: bool = False):
    """
    Shutdown the cortex synchronously.

    Uses asyncio.run() to run the async shutdown.

    Principle: Infrastructure work should always communicate what's happening.
    """
    import asyncio

    try:
        if verbose and _lifecycle_state and _lifecycle_state.instance_id:
            print(
                f"\033[90m[cortex]\033[0m Shutdown: instance={_lifecycle_state.instance_id[:8]}",
                file=sys.stderr,
            )
        asyncio.run(_shutdown_cortex())
    except Exception:
        pass  # Best effort


def main(argv: Sequence[str] | None = None) -> int:
    """
    The Hollow Shell entry point.

    Fast path:
    - --help: print help and exit (no imports, no bootstrap)
    - --version: print version and exit (no imports, no bootstrap)

    Normal path:
    - Auto-bootstrap cortex (enables DB persistence)
    - Parse command from first arg
    - Resolve to handler (lazy import)
    - Execute handler with remaining args
    - Graceful shutdown
    """
    if argv is None:
        argv = sys.argv[1:]

    args = list(argv)

    # Parse global flags (fast, no imports)
    flags, remaining = parse_global_flags(args)

    # Fast path: --help (no bootstrap)
    if flags["help"] and not remaining:
        print(HELP_TEXT)
        return 0

    # Fast path: --version (no bootstrap)
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

    # Check for command-level help (no bootstrap needed)
    if flags["help"] or "--help" in command_args or "-h" in command_args:
        handler = resolve_command(command)
        if handler:
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

    # Check for verbose mode
    verbose = "--verbose" in command_args or "-v" in command_args

    # Auto-bootstrap cortex (unless --no-bootstrap flag is set)
    # This initializes DB persistence and telemetry
    # Runs synchronously BEFORE handler to avoid nested event loop issues
    if not flags.get("no_bootstrap"):
        project_root = find_kgents_root()
        _sync_bootstrap(project_root, verbose=verbose)

    # Execute handler
    try:
        return handler(command_args)
    except KeyboardInterrupt:
        print("\n[...] Interrupted. No worries—nothing was left in a bad state.")
        return 130
    except Exception as e:
        # Sympathetic error handling
        try:
            from protocols.cli.errors import handle_exception

            print(handle_exception(e, verbose=verbose))
        except ImportError:
            print(f"Error: {e}")
        return 1
    finally:
        # Graceful shutdown
        _sync_shutdown(verbose=verbose)


if __name__ == "__main__":
    sys.exit(main())
