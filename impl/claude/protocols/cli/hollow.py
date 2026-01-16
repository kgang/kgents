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

# Help text is now generated dynamically by help_global.py
# This fallback is only used if the help module fails to load
HELP_TEXT_FALLBACK = """\
kgents - Tasteful, curated, ethical agents

USAGE:
  kg <command> [args...]       Run a command
  kg <command> --help          Get command help
  kg -i                        Interactive REPL
  kg ?<pattern>                Query paths (e.g., ?self.*)

CROWN JEWELS:
  brain       Holographic memory operations
  soul        Digital consciousness dialogue
  town        Agent simulation and interactions
  gardener    Development session management

FOREST PROTOCOL:
  forest      Project health and plan status
  garden      Hypnagogia and dream states
  tend        Garden tending operations

JOY COMMANDS:
  joy         Oblique strategies gateway
  oblique     Draw an oblique strategy card
  surprise-me Unexpected creative prompt

EXAMPLES:
  $ kg brain capture "Category theory is beautiful"
  $ kg soul reflect
  $ kg town inhabit alice
  $ kg oblique

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
    # Getting Started (New User Entry Points)
    # ==========================================================================
    "start": "protocols.cli.handlers.start:cmd_start",
    # ==========================================================================
    # Bootstrap Commands
    # ==========================================================================
    "init": "protocols.cli.handlers.init:cmd_init",
    "wipe": "protocols.cli.handlers.wipe:cmd_wipe",
    "reset": "protocols.cli.handlers.reset:cmd_reset",
    "doctor": "protocols.cli.handlers.doctor:cmd_doctor",
    "migrate": "protocols.cli.handlers.migrate:cmd_migrate",
    # ==========================================================================
    # Note: Town, Park, Atelier CLI removed 2025-12-21 (Post-Extinction cleanup)
    # ==========================================================================
    # Holographic Brain (Crown Jewel - Memory)
    # Uses thin routing shim - all logic in services/brain/
    # ==========================================================================
    "brain": "protocols.cli.handlers.brain_thin:cmd_brain",
    # ==========================================================================
    # Witness (8th Crown Jewel - The Witnessing Ghost)
    # Modular CLI package - see protocols/cli/handlers/witness/
    # ==========================================================================
    "witness": "protocols.cli.handlers.witness:cmd_witness",
    # ==========================================================================
    # WitnessedGraph (9th Crown Jewel - Unified Edge Composition)
    # Uses thin routing shim - delegates to concept.graph.* paths
    # ==========================================================================
    "graph": "protocols.cli.handlers.graph_thin:cmd_graph",
    # ==========================================================================
    # Fusion: Symmetric Supersession (Dialectical Decision Witnessing)
    # Captures reasoning traces for decisions as they happen
    # ==========================================================================
    "decide": "services.fusion.cli:main",
    # ==========================================================================
    # Shortcuts (ergonomic aliases for common operations)
    # ==========================================================================
    "play": "protocols.cli.handlers.play:cmd_play",
    # ==========================================================================
    # Wave 4: Joy-Inducing Commands (CLI Quick Wins)
    # Restored 2026-01-16 (CLI Renaissance Phase 1)
    # "Surprise and serendipity; discovery should feel rewarding."
    # ==========================================================================
    "oblique": "protocols.cli.handlers.joy:cmd_oblique",
    "surprise": "protocols.cli.handlers.joy:cmd_surprise",
    "yes-and": "protocols.cli.handlers.joy:cmd_yes_and",
    "challenge": "protocols.cli.handlers.joy:cmd_challenge",
    "constrain": "protocols.cli.handlers.joy:cmd_constrain",
    # ==========================================================================
    # Inquiry Commands
    # ==========================================================================
    "why": "protocols.cli.handlers.why:cmd_why",
    # ==========================================================================
    # v3: Shortcut Management
    # ARCHIVED 2026-01-16 (CLI Renaissance Phase 2): Low usage, unclear purpose
    # ==========================================================================
    # "shortcut": "protocols.cli.shortcuts:cmd_shortcut",
    # ==========================================================================
    # v3: Query and Subscribe Commands
    # ==========================================================================
    "query": "protocols.cli.handlers.query:cmd_query",
    # ARCHIVED 2026-01-16 (CLI Renaissance Phase 2): Daemon-only, not user-facing
    # "subscribe": "protocols.cli.handlers.subscribe:cmd_subscribe",
    # ==========================================================================
    # Coffee: Morning Coffee Liminal Transition Protocol (time.coffee.*)
    # ==========================================================================
    "coffee": "protocols.cli.handlers.coffee:cmd_coffee",
    # ==========================================================================
    # Dawn: Dawn Cockpit Daily Operating Surface (time.dawn.*)
    # Quarter-screen TUI where copy-paste is the killer feature
    # ==========================================================================
    "dawn": "protocols.cli.handlers.dawn:cmd_dawn",
    # ==========================================================================
    # Completions: Shell completions generator (Wave 3)
    # ==========================================================================
    "completions": "protocols.cli.completions:cmd_completions",
    # ARCHIVED: 'q' alias removed - ambiguous (could mean "quit"), use 'query' instead
    # ==========================================================================
    # Living Docs: Documentation Generator (Phase 4-5)
    # Uses thin routing shim - all logic in services/living_docs/
    # ==========================================================================
    "docs": "protocols.cli.handlers.docs:cmd_docs",
    # ==========================================================================
    # ARCHAEOLOGY: Git History Mining for Priors and Teachings
    # Uses thin routing shim - all logic in services/archaeology/
    # ==========================================================================
    "archaeology": "protocols.cli.handlers.archaeology:cmd_archaeology",
    # ==========================================================================
    # EVIDENCE: Evidence Mining & ROI Tracking
    # Uses thin routing shim - all logic in services/evidence/
    # ==========================================================================
    "evidence": "protocols.cli.handlers.evidence:cmd_evidence",
    # ==========================================================================
    # AUDIT: Spec validation against principles and implementation (Phase 1)
    # Validates specs against 7 constitutional principles and detects drift
    # ==========================================================================
    "audit": "protocols.cli.commands.audit:cmd_audit",
    # ==========================================================================
    # PROBE: Fast categorical law checks and health probes (Phase 4)
    # Quick identity/associativity law verification and Crown Jewel health checks
    # ==========================================================================
    "probe": "protocols.cli.handlers.probe_thin:cmd_probe",
    # ==========================================================================
    # FILE_OPERAD: Navigate Operads as Documents (Session 2)
    # Portal tokens enable inline expansion of cross-operad links
    # ARCHIVED 2026-01-16 (CLI Renaissance Phase 2): Opaque name, low discoverability
    # ==========================================================================
    # "op": "protocols.file_operad.cli:cmd_op",
    # ==========================================================================
    # TYPED-HYPERGRAPH: Navigate context as typed-hypergraph (self.context.*)
    # Lazy navigation, observer-dependent edges, replayable trails
    # ==========================================================================
    "context": "protocols.cli.handlers.context:cmd_context",
    # ==========================================================================
    # PORTAL: Navigate source files through hyperedge expansion (Phase 4)
    # Portal tokens for real source files, not just .op files
    # ==========================================================================
    "portal": "protocols.cli.handlers.portal:cmd_portal",
    # ==========================================================================
    # EXPLORATION HARNESS: Bounded exploration with evidence (self.explore.*)
    # Budget, loop detection, evidence collection, commitment protocol
    # ==========================================================================
    "explore": "protocols.cli.handlers.explore:cmd_explore",
    # ==========================================================================
    # DERIVATION FRAMEWORK: Agent justification chains (concept.derivation.*)
    # Bootstrap axioms → derived agents, confidence propagation, principle draws
    # ==========================================================================
    "derivation": "protocols.cli.handlers.derivation:cmd_derivation",
    # ARCHIVED: 'derive' alias removed - duplicate of 'derivation', use 'derivation' instead
    # ==========================================================================
    # SOVEREIGN: Inbound Sovereignty - possess, don't reference (concept.sovereign.*)
    # Bootstrap, ingest, sync, diff - all data enters witnessed
    # ==========================================================================
    "sovereign": "protocols.cli.handlers.sovereign_thin:cmd_sovereign",
    # ==========================================================================
    # ANNOTATE: Spec ↔ Impl mapping (concept.annotate.*)
    # Principles, impl links, gotchas, taste - bidirectional tracing
    # ==========================================================================
    "annotate": "protocols.cli.handlers.annotate:cmd_annotate",
    # ==========================================================================
    # COMPOSE: Chain kg operations with unified witnessing (Phase 5)
    # Sequential execution, dependency resolution, trace linking
    # ==========================================================================
    "compose": "protocols.cli.commands.compose:cmd_compose",
    # ==========================================================================
    # EXPERIMENT: Bayesian evidence gathering experiments (Phase 3)
    # VoidHarness execution, Bayesian stopping, parse experiments
    # ==========================================================================
    "experiment": "protocols.cli.commands.experiment:main",
    # ==========================================================================
    # ANALYZE: Four-mode spec analysis (categorical, epistemic, dialectical, generative)
    # Analysis Operad operations - law verification, grounding, tensions, regenerability
    # ==========================================================================
    "analyze": "protocols.cli.handlers.analyze:cmd_analyze",
    # ==========================================================================
    # DEV: Unified development server (frontend + backend)
    # Runs uvicorn (port 8000) and Vite (port 3000) with hot reload
    # ==========================================================================
    "dev": "protocols.cli.handlers.dev:cmd_dev",
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

        # Wire Crown Jewel services for AGENTESE nodes
        # This enables real LLM calls via ChatNode → Morpheus
        try:
            from services.providers import setup_providers

            await setup_providers()
        except Exception as provider_err:
            # Graceful degradation - chat will use stub mode
            import logging

            logging.getLogger(__name__).debug(f"setup_providers skipped: {provider_err}")

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


def _print_windows_error() -> None:
    """Print a helpful error message for Windows users."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console(stderr=True)
        content = (
            "[bold red]kgents requires Unix (macOS/Linux)[/bold red]\n\n"
            "[dim]Windows users can use:[/dim]\n"
            "  • [cyan]WSL2:[/cyan] wsl --install\n"
            "  • [cyan]Docker:[/cyan] docker run -it kgents/kgents\n\n"
            "[dim]See:[/dim] https://kgents.dev/docs/windows"
        )
        console.print(Panel(content, border_style="red", padding=(1, 2)))
    except ImportError:
        # Fallback without rich
        print("", file=sys.stderr)
        print("╭─────────────────────────────────────────────────────╮", file=sys.stderr)
        print("│  kgents requires Unix (macOS/Linux)                 │", file=sys.stderr)
        print("│                                                     │", file=sys.stderr)
        print("│  Windows users can use:                             │", file=sys.stderr)
        print("│    • WSL2: wsl --install                            │", file=sys.stderr)
        print("│    • Docker: docker run -it kgents/kgents           │", file=sys.stderr)
        print("│                                                     │", file=sys.stderr)
        print("│  See: https://kgents.dev/docs/windows               │", file=sys.stderr)
        print("╰─────────────────────────────────────────────────────╯", file=sys.stderr)
        print("", file=sys.stderr)


def _print_daemon_required_error() -> None:
    """Print a helpful error message when the daemon is not running."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console(stderr=True)
        content = (
            "[bold red]kgentsd daemon is not running[/bold red]\n\n"
            "[dim]Start the daemon:[/dim]\n"
            "  [cyan]kgentsd summon[/cyan]\n\n"
            "[dim]The daemon provides:[/dim]\n"
            "  • Persistent context across commands\n"
            "  • Trust-gated execution\n"
            "  • Audit logging\n\n"
            "[dim]Fallback mode (no daemon):[/dim]\n"
            "  [cyan]KGENTS_NO_DAEMON=1 kg <command>[/cyan]"
        )
        console.print(Panel(content, border_style="red", padding=(1, 2)))
    except ImportError:
        # Fallback without rich
        print("", file=sys.stderr)
        print("╭─────────────────────────────────────────────────────╮", file=sys.stderr)
        print("│  kgentsd daemon is not running                      │", file=sys.stderr)
        print("│                                                     │", file=sys.stderr)
        print("│  Start the daemon:                                  │", file=sys.stderr)
        print("│    kgentsd summon                                   │", file=sys.stderr)
        print("│                                                     │", file=sys.stderr)
        print("│  Or run without daemon (fallback):                  │", file=sys.stderr)
        print("│    KGENTS_NO_DAEMON=1 kg <command>                  │", file=sys.stderr)
        print("╰─────────────────────────────────────────────────────╯", file=sys.stderr)
        print("", file=sys.stderr)


def _show_global_help() -> int:
    """
    Show global help using the new help system.

    Falls back to static help text if the help module fails to load.
    """
    try:
        from protocols.cli.help_global import show_global_help

        return show_global_help()
    except ImportError:
        # Fallback to static help text
        print(HELP_TEXT_FALLBACK)
        return 0


def _show_command_help(command: str) -> int:
    """
    Show help for a specific command using the new help system.

    Falls back to handler-provided help if projection fails.
    """
    try:
        # Get the AGENTESE path for this command
        from protocols.cli.help_projector import PATH_TO_COMMAND, create_help_projector
        from protocols.cli.help_renderer import render_help

        # Reverse lookup: command -> path
        path = None
        for p, cmd in PATH_TO_COMMAND.items():
            if cmd == command:
                path = p
                break

        if path:
            projector = create_help_projector()
            help_obj = projector.project(path)
            print(render_help(help_obj))
            return 0
    except Exception:
        pass

    # Fallback: return 1 to indicate handler should show its own help
    return -1  # Special return code: use handler's help


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

    # Platform check: kgents requires Unix (PTY support)
    if sys.platform == "win32":
        _print_windows_error()
        return 1

    args = list(argv)

    # Parse global flags (fast, no imports)
    flags, remaining = parse_global_flags(args)

    # Fast path: --help (no bootstrap)
    if flags["help"] and not remaining:
        return _show_global_help()

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
        return _show_global_help()

    # Extract command
    command = remaining[0]
    command_args = remaining[1:]

    # =========================================================================
    # Command-Level Help (Fast Path - No Bootstrap/Daemon)
    # =========================================================================
    # Handle help BEFORE daemon routing. The --help flag is consumed by
    # parse_global_flags and stored in flags["help"], so we need to check
    # it here and handle help locally (no daemon round-trip needed).
    # =========================================================================
    if flags["help"] or "--help" in command_args or "-h" in command_args:
        # Try projected help first
        result = _show_command_help(command)
        if result >= 0:
            return result
        # Fallback to handler's built-in help
        handler = resolve_command(command)
        if handler:
            import asyncio
            import inspect

            filtered_args = [a for a in command_args if a not in ("--help", "-h")]
            result = handler(["--help"] + filtered_args)
            # Handle async handlers
            if inspect.iscoroutine(result):
                return int(asyncio.run(result))
            return int(result)
        else:
            print_suggestions(command)
            return 1

    # =========================================================================
    # TUI Commands (Bypass Daemon + Async)
    # =========================================================================
    # TUI applications (Textual) require:
    # 1. Main thread (for signal handlers)
    # 2. Direct terminal access
    # 3. Their own event loop (can't nest asyncio.run())
    #
    # These commands bypass daemon AND run synchronously (no asyncio.run()).
    # =========================================================================
    TUI_COMMANDS = {"dawn", "coffee", "dev"}
    TUI_SUBCOMMANDS = {
        "witness": {"dashboard", "dash"},
    }

    is_tui_command = command in TUI_COMMANDS
    is_tui_subcommand = (
        command in TUI_SUBCOMMANDS and command_args and command_args[0] in TUI_SUBCOMMANDS[command]
    )

    if is_tui_command or is_tui_subcommand:
        # TUI commands run locally, synchronously, in main thread
        # Skip both daemon routing AND asyncio.run() wrapping
        try:
            if is_tui_subcommand:
                # For subcommands like "witness dashboard", call the subcommand directly
                # This avoids going through the async parent handler
                if command == "witness" and command_args[0] in {"dashboard", "dash"}:
                    from protocols.cli.handlers.witness import cmd_dashboard

                    return cmd_dashboard(command_args[1:])
                # Add other TUI subcommands here as needed

            # For top-level TUI commands (dawn, coffee)
            handler = resolve_command(command)
            if handler:
                result = handler(command_args)
                import inspect

                if inspect.iscoroutine(result):
                    print("Error: TUI commands must use synchronous handlers")
                    result.close()
                    return 1
                return int(result) if result is not None else 0
            else:
                print_suggestions(command)
                return 1
        except KeyboardInterrupt:
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1

    # =========================================================================
    # Daemon Routing (All Commands)
    # =========================================================================
    # ALL commands route through the kgentsd daemon. This provides:
    # - Centralized execution with daemon context
    # - Trust-gated operations via ActionGate
    # - Audit logging for all CLI activity
    #
    # If daemon is not running:
    # - Set KGENTS_NO_DAEMON=1 for fallback to local execution (with warning)
    # - Otherwise fail with a helpful error message
    #
    # KGENTS_INSIDE_DAEMON: Set by daemon when spawning subprocess.
    # Prevents recursive routing (daemon -> subprocess -> daemon -> ...).
    # =========================================================================
    allow_no_daemon = os.environ.get("KGENTS_NO_DAEMON") == "1"

    # Skip daemon routing if:
    # - Command is a TUI command (needs direct terminal)
    # - KGENTS_NO_DAEMON=1 (explicit bypass)
    # - KGENTS_INSIDE_DAEMON is set (already in daemon)
    skip_daemon = (
        command in TUI_COMMANDS or allow_no_daemon or os.environ.get("KGENTS_INSIDE_DAEMON")
    )

    if not skip_daemon:
        try:
            from services.kgentsd.socket_client import (
                DaemonConnectionError,
                DaemonNotRunningError,
                DaemonProtocolError,
                DaemonTimeoutError,
                is_daemon_available,
                route_command,
            )

            if is_daemon_available():
                # Route through daemon
                try:
                    response = route_command(command, command_args, flags)
                    if response.stdout:
                        print(response.stdout, end="")
                    if response.stderr:
                        print(response.stderr, end="", file=sys.stderr)
                    return response.exit_code
                except DaemonConnectionError as e:
                    print(f"Error: Cannot connect to kgentsd: {e}", file=sys.stderr)
                    return 1
                except DaemonTimeoutError as e:
                    print(f"Error: kgentsd not responding: {e}", file=sys.stderr)
                    return 1
                except DaemonProtocolError as e:
                    print(f"Error: Invalid response from kgentsd: {e}", file=sys.stderr)
                    return 1
            else:
                # Daemon not running - show helpful message
                _print_daemon_required_error()
                return 1

        except ImportError:
            # Socket client module not available - fall through to local execution
            # This allows development without the daemon infrastructure
            pass

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
    # Phase 3.3 CLI Renaissance: Detect >> composition syntax
    # See protocols/cli/compose_paths.py for composition semantics
    # Categorical law: (f >> g) >> h = f >> (g >> h)
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

    # Note: Command-level help is handled BEFORE daemon routing (see above)

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
        import asyncio
        import inspect

        result = handler(command_args)
        # Handle async handlers
        if inspect.iscoroutine(result):
            exit_code = int(asyncio.run(result))
        else:
            exit_code = int(result)
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
