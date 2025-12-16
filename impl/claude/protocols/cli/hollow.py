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
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence, cast

# Global lifecycle manager (lazy-initialized)
_lifecycle_manager = None
_lifecycle_state = None

# Global reflector (lazy-initialized)
_reflector: Any = None

# =============================================================================
# Version & Constants
# =============================================================================

__version__ = "0.2.0"

# Help text (no imports required)
HELP_TEXT = """\
kgents - K-gents Agent Framework

USAGE:
  kgents <context> [subcommand] [args...]
  kgents <context> --help
  kgents -i                    # Interactive REPL mode

COMMANDS (AGENTESE Contexts):
  self      Internal state, memory, soul
  world     Agents, infrastructure, resources
  concept   Laws, principles, dialectics
  void      Entropy, shadow, archetypes
  time      Traces, turns, telemetry
  do        Natural language intent
  flow      Pipeline composition

Run 'kgents <context>' for subcommands.

OPTIONS:
  -i, --interactive   Enter AGENTESE REPL (interactive mode)
  --version           Show version
  --help, -h          Show this help
  --explain           Show AGENTESE path for command

EXAMPLES:
  kgents -i                    # Interactive REPL
  kgents self status           # System health
  kgents self soul reflect     # K-gent reflection
  kgents world agents list     # List registered agents
  kgents concept laws          # Category laws
  kgents void shadow           # Jungian shadow analysis
  kgents time trace            # Call graph tracing
  kgents do "test the API"     # Natural language intent

For more: https://github.com/kgents/kgents
"""

# =============================================================================
# Command Registry (module paths, not imports)
# =============================================================================

# Format: 'command': 'module.path:function_name'
# Only the invoked command's module will be imported

COMMAND_REGISTRY: dict[str, str] = {
    # ==========================================================================
    # AGENTESE Context Commands (Primary Interface)
    # ==========================================================================
    # These are the ONLY top-level commands. All functionality is accessible
    # through context routing: kgents <context> <subcommand>
    "self": "protocols.cli.contexts.self_:cmd_self",
    "world": "protocols.cli.contexts.world:cmd_world",
    "concept": "protocols.cli.contexts.concept:cmd_concept",
    "void": "protocols.cli.contexts.void:cmd_void",
    "time": "protocols.cli.contexts.time_:cmd_time",
    # ==========================================================================
    # Intent Layer (Natural Language)
    # ==========================================================================
    "do": "protocols.cli.intent.router:cmd_do",
    # ==========================================================================
    # Pipeline Composition
    # ==========================================================================
    "flow": "protocols.cli.flow.commands:cmd_flow",
    # ==========================================================================
    # Bootstrap Commands
    # ==========================================================================
    "init": "protocols.cli.handlers.init:cmd_init",
    "wipe": "protocols.cli.handlers.wipe:cmd_wipe",
    "migrate": "protocols.cli.handlers.migrate:cmd_migrate",
    # ==========================================================================
    # Agent Town (Crown Jewel)
    # ==========================================================================
    "town": "protocols.cli.handlers.town:cmd_town",
    # ==========================================================================
    # Tiny Atelier (Demo Workshop)
    # ==========================================================================
    "atelier": "protocols.cli.handlers.atelier:cmd_atelier",
    # ==========================================================================
    # Shortcuts (ergonomic aliases for common operations)
    # ==========================================================================
    "play": "protocols.cli.handlers.play:cmd_play",
    # ==========================================================================
    # Wave 4: Joy-Inducing Commands (CLI Quick Wins)
    # ==========================================================================
    "challenge": "protocols.cli.handlers.challenge:cmd_challenge",
    "oblique": "protocols.cli.handlers.oblique:cmd_oblique",
    "constrain": "protocols.cli.handlers.constrain:cmd_constrain",
    "yes-and": "protocols.cli.handlers.yes_and:cmd_yes_and",
    "surprise-me": "protocols.cli.handlers.surprise_me:cmd_surprise_me",
    "project": "protocols.cli.handlers.project:cmd_project",
    "why": "protocols.cli.handlers.why:cmd_why",
    "tension": "protocols.cli.handlers.tension:cmd_tension",
    # ==========================================================================
    # v3: Shortcut and Legacy Management
    # ==========================================================================
    "shortcut": "protocols.cli.shortcuts:cmd_shortcut",
    "legacy": "protocols.cli.legacy:cmd_legacy",
    # ==========================================================================
    # v3: Query and Subscribe Commands
    # ==========================================================================
    "query": "protocols.cli.handlers.query:cmd_query",
    "subscribe": "protocols.cli.handlers.subscribe:cmd_subscribe",
    # ==========================================================================
    # Forest: AGENTESE-native forest health (self.forest.*)
    # ==========================================================================
    "forest": "protocols.cli.handlers.forest:cmd_forest",
    # ==========================================================================
    # Grow: Autopoietic Holon Generator (self.grow.*)
    # ==========================================================================
    "grow": "protocols.cli.handlers.grow:cmd_grow",
    # ==========================================================================
    # Prompt: Evergreen Prompt System (concept.prompt.*)
    # ==========================================================================
    "prompt": "protocols.cli.handlers.prompt:cmd_prompt",
    # ==========================================================================
    # Gardener: Development Session Management (concept.gardener.*)
    # Wave 1: Hero Path Polish
    # ==========================================================================
    "gardener": "protocols.cli.handlers.gardener:cmd_gardener",
}


# =============================================================================
# Lazy Loading
# =============================================================================


def resolve_command(name: str) -> Callable[..., Any] | None:
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
        return cast("Callable[..., int] | None", getattr(module, func_name))
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


async def _bootstrap_cortex(project_path: Path | None = None) -> Any:
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


async def _shutdown_cortex() -> None:
    """Gracefully shutdown the cortex."""
    global _lifecycle_manager, _lifecycle_state

    if _lifecycle_manager is not None:
        await _lifecycle_manager.shutdown()
        _lifecycle_manager = None
        _lifecycle_state = None


def get_lifecycle_state() -> Any:
    """
    Get the current lifecycle state.

    Returns None if bootstrap hasn't been called or failed.
    Handlers can use this to access storage providers.
    """
    return _lifecycle_state


def get_storage_provider() -> Any:
    """
    Get the storage provider from the lifecycle state.

    Returns None if not bootstrapped or in DB-less mode.
    """
    if _lifecycle_state is None:
        return None
    return _lifecycle_state.storage_provider


# =============================================================================
# Reflector Management
# =============================================================================


def _create_reflector(verbose: bool = False) -> Any:
    """
    Create a TerminalReflector for the current command.

    The Reflector mediates output between the runtime and user:
    - Human-readable text goes to stdout
    - Semantic data goes to FD3 (if KGENTS_FD3 env var is set)

    This enables agent-to-agent communication via structured JSON
    while keeping human output pretty.
    """
    global _reflector

    try:
        from protocols.cli.reflector import TerminalReflector

        # Check for FD3 path in environment
        fd3_path = os.environ.get("KGENTS_FD3")

        _reflector = TerminalReflector(verbose=verbose, fd3_path=fd3_path)
        return _reflector
    except ImportError:
        # Reflector module not available - return None
        return None


def _get_reflector() -> Any:
    """Get the current reflector (if any)."""
    return _reflector


def _close_reflector() -> None:
    """Close the reflector and release resources."""
    global _reflector

    if _reflector is not None:
        try:
            _reflector.close()
        except Exception:
            pass
        _reflector = None


def get_invocation_context(
    command: str,
    args: list[str] | None = None,
) -> Any:
    """
    Get an InvocationContext for the current command.

    This is the public API for handlers to access the reflector.
    Handlers can call ctx.output(human=..., semantic=...) for dual-channel output.

    Returns None if reflector is not available.
    """
    if _reflector is None:
        return None

    try:
        from protocols.cli.reflector import create_invocation_context

        return create_invocation_context(
            command=command,
            args=args or [],
            reflector=_reflector,
            fd3_path=os.environ.get("KGENTS_FD3"),
        )
    except ImportError:
        return None


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


def load_context() -> dict[str, Any]:
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


def parse_global_flags(args: list[str]) -> tuple[dict[str, Any], list[str]]:
    """
    Parse global flags without importing argparse.

    Returns (flags, remaining_args).
    This is fast path for --help, --version, -i.
    """
    flags = {
        "help": False,
        "version": False,
        "interactive": False,
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
        elif arg in ("-i", "--interactive"):
            flags["interactive"] = True
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


def _sync_bootstrap(project_path: Path | None = None, verbose: bool = False) -> None:
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

        return  # Intentionally return None - state is only for internal use
    except Exception as e:
        print(f"\033[33m[kgents]\033[0m Bootstrap warning: {e}", file=sys.stderr)
        return


def _sync_shutdown(verbose: bool = False) -> None:
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


def _handle_agentese(args: list[str], flags: dict[str, Any]) -> int:
    """
    Handle AGENTESE direct paths, shortcuts, queries, and compositions.

    v3 CLI Integration: Routes through Logos instead of command registry.

    Args:
        args: Command-line arguments (e.g., ["self.forest.manifest", "--json"])
        flags: Global flags from parse_global_flags

    Returns:
        Exit code
    """
    import asyncio

    try:
        from protocols.cli.agentese_router import AgentesRouter, RouterConfig

        # Build config from flags
        config = RouterConfig(
            json_output="--json" in args,
            trace_output="--trace" in args,
            dry_run="--dry-run" in args,
        )

        # Remove flags from args
        clean_args = [a for a in args if a not in ("--json", "--trace", "--dry-run")]

        # Bootstrap cortex if needed
        if not flags.get("no_bootstrap"):
            project_root = find_kgents_root()
            verbose = "--verbose" in args or "-v" in args
            _sync_bootstrap(project_root, verbose=verbose)

        # Create router and execute
        router = AgentesRouter(config=config)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(router.route(clean_args, None))

        if not result.success:
            print(f"Error: {result.error}")
            return 1

        # Output result
        if config.json_output:
            import json

            print(json.dumps(result.result, indent=2, default=str))
        elif result.result is not None:
            try:
                from rich.console import Console

                if hasattr(result.result, "__rich__"):
                    console = Console()
                    console.print(result.result)
                else:
                    print(result.result)
            except ImportError:
                print(result.result)

        if config.trace_output and result.trace_id:
            print(f"\nTrace ID: {result.trace_id}")

        return 0

    except ImportError as e:
        # Fallback if router not available
        print(f"Error: AGENTESE router not available: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Graceful shutdown
        verbose = "--verbose" in args or "-v" in args
        _sync_shutdown(verbose=verbose)


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

    # Interactive mode: -i / --interactive
    if flags["interactive"]:
        from protocols.cli.repl import cmd_interactive

        return cmd_interactive(remaining)

    # No command given
    if not remaining:
        print(HELP_TEXT)
        return 0

    # Extract command
    command = remaining[0]
    command_args = remaining[1:]

    # v3: Check for AGENTESE direct paths, shortcuts, queries, and legacy commands
    # These bypass the command registry and route through Logos
    is_agentese_path = "." in command and command.split(".")[0] in {
        "world",
        "self",
        "concept",
        "void",
        "time",
    }
    is_shortcut = command.startswith("/")
    is_query = command.startswith("?")
    is_composition = ">>" in " ".join(remaining)

    # Check for legacy commands (before command registry check)
    is_legacy = False
    if not (is_agentese_path or is_shortcut or is_query or is_composition):
        try:
            from protocols.cli.legacy import is_legacy_command

            is_legacy = is_legacy_command(remaining)
        except ImportError:
            pass

    if is_agentese_path or is_shortcut or is_query or is_composition or is_legacy:
        # Route through AGENTESE router
        return _handle_agentese(remaining, flags)

    # Check for command-level help (no bootstrap needed)
    if flags["help"] or "--help" in command_args or "-h" in command_args:
        handler = resolve_command(command)
        if handler:
            filtered_args = [a for a in command_args if a not in ("--help", "-h")]
            return int(handler(["--help"] + filtered_args))
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

    # Create reflector for this command invocation
    # This enables dual-channel output (human + semantic)
    reflector = _create_reflector(verbose=verbose)
    start_time = time.time()

    # Emit command start event (if reflector available)
    if reflector is not None:
        try:
            from protocols.cli.reflector import command_start

            reflector.on_event(command_start(command, command_args))
        except ImportError:
            pass

    # Execute handler
    exit_code = 0
    try:
        exit_code = int(handler(command_args))
        return exit_code
    except KeyboardInterrupt:
        print("\n[...] Interrupted. No worries—nothing was left in a bad state.")
        exit_code = 130
        return exit_code
    except Exception as e:
        # Sympathetic error handling
        try:
            from protocols.cli.errors import handle_exception

            print(handle_exception(e, verbose=verbose))
        except ImportError:
            print(f"Error: {e}")
        exit_code = 1
        return exit_code
    finally:
        # Emit command end event (if reflector available)
        if reflector is not None:
            try:
                from protocols.cli.reflector import command_end

                duration_ms = int((time.time() - start_time) * 1000)
                reflector.on_event(
                    command_end(command, exit_code=exit_code, duration_ms=duration_ms)
                )
            except ImportError:
                pass

        # Close reflector
        _close_reflector()

        # Graceful shutdown
        _sync_shutdown(verbose=verbose)


if __name__ == "__main__":
    sys.exit(main())
