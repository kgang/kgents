"""
AGENTESE REPL: Interactive navigation through the five contexts.

The REPL embodies the verb-first ontology: commands are invocations,
not queries. Navigation feels like grasping handles in a living world.

Wave 2 Enhancements:
    - Async execution via Logos (proper AGENTESE resolution)
    - Pipeline execution (>> composition actually runs)
    - Observer/Umwelt context switching (/observer command)
    - Rich output rendering (tables, panels, colors)
    - Error sympathy (errors suggest next actions)

Usage:
    kgents -i              # Enter interactive mode
    kgents --interactive   # Same as above

Design Principles Applied:
    - Liturgical: Commands read like invocations
    - Joy-Inducing: Personality and warmth in responses
    - Transparent Infrastructure: Always shows what's happening
    - Graceful Degradation: Works even when subsystems are offline
    - Composable: Supports >> operator for path composition

Navigation:
    self, world, concept, void, time  # Enter context
    agents, daemon, infra             # Navigate to holon
    ..                                # Go up one level
    .                                 # Show current path
    /                                 # Go to root

Commands:
    <path>                 # Invoke manifest aspect
    <path>.<aspect>        # Invoke specific aspect
    <path> >> <path>       # Compose paths (now executes!)
    ?                      # Show affordances
    ??                     # Detailed help
    /observer <archetype>  # Switch observer context
    help                   # Show help
    exit, quit, q          # Leave REPL
"""

from __future__ import annotations

import asyncio
import readline  # noqa: F401 - imported for side effects (history, editing)
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Rich imports for beautiful output (graceful degradation if unavailable)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore[misc, assignment]
    Panel = None  # type: ignore[misc, assignment]
    Table = None  # type: ignore[misc, assignment]
    Text = None  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Constants
# =============================================================================

CONTEXTS = frozenset({"self", "world", "concept", "void", "time"})

# Context -> Holons mapping (lazily populated)
CONTEXT_HOLONS: dict[str, list[str]] = {
    "self": ["status", "memory", "dream", "soul", "capabilities", "dashboard"],
    "world": ["agents", "daemon", "infra", "fixture", "exec", "dev", "town"],
    "concept": ["laws", "dialectic", "principle", "operad"],
    "void": ["entropy", "shadow", "serendipity", "gratitude", "archetype"],
    "time": ["trace", "past", "future", "schedule", "turn"],
}

WELCOME_BANNER = """\
\033[36m╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│   \033[1;37mkgents\033[0;36m  ·  \033[3mThe verb-first ontology\033[0;36m                          │
│                                                                 │
│   \033[33m"The noun is a lie. There is only the rate of change."\033[36m        │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯\033[0m

\033[90mContexts:\033[0m  self · world · concept · void · time
\033[90mCommands:\033[0m  ? (affordances) · ?? (help) · .. (up) · exit
\033[90mPipeline:\033[0m  path >> path  (compose and execute)
\033[90mSwitch:\033[0m    /observer <archetype>  (explorer, developer, architect)

"""

# Observer archetypes with their descriptions
OBSERVER_ARCHETYPES = {
    "explorer": "Curious newcomer, sees pedagogical affordances",
    "developer": "Skilled builder, sees technical affordances",
    "architect": "System designer, sees structural + define affordances",
    "admin": "Full access, sees all affordances including dangerous",
}

HELP_TEXT = """\
\033[1mAGENTESE REPL\033[0m - Navigate the five contexts

\033[1mNavigation:\033[0m
  self, world, concept, void, time   Enter a context
  <holon>                            Navigate to holon
  ..                                 Go up one level
  .                                  Show current path
  /                                  Return to root

\033[1mInvocation:\033[0m
  <path>                   Invoke with manifest aspect
  <path>.<aspect>          Invoke specific aspect (e.g., soul.reflect)
  <path> >> <path>         Compose paths into pipeline (executes!)

\033[1mIntrospection:\033[0m
  ?                        Show affordances for current node
  ??                       Detailed help for current node
  help                     Show this help

\033[1mObserver Control:\033[0m
  /observer                Show current observer archetype
  /observer <archetype>    Switch observer (explorer, developer, architect, admin)
  /observers               List all available archetypes

\033[1mExamples:\033[0m
  \033[33mself\033[0m                       Enter self context
  \033[33msoul reflect\033[0m               Invoke self.soul.reflect
  \033[33mworld agents list\033[0m          List agents
  \033[33mvoid entropy sip\033[0m           Draw from Accursed Share
  \033[33mworld.agents >> count\033[0m      Pipeline: list then count
  \033[33m/observer developer\033[0m        Switch to developer observer
  \033[33m..\033[0m                         Go back up

\033[1mMeta:\033[0m
  exit, quit, q            Leave the REPL
  clear                    Clear screen
  history                  Show command history
"""


# =============================================================================
# Rich Console Singleton
# =============================================================================

# Global console for rich output (created once)
_console: Any = None


def get_console() -> Any:
    """Get or create the rich console (lazy initialization)."""
    global _console
    if _console is None and RICH_AVAILABLE:
        _console = Console()
    return _console


# =============================================================================
# Umwelt Wrapper (for cache tracking)
# =============================================================================


class _UmweltWrapper:
    """
    Wrapper around a frozen Umwelt to track observer type for cache invalidation.

    Since LightweightUmwelt is frozen, we can't add fields to it.
    This wrapper provides a mutable container.
    """

    def __init__(self, umwelt: Any, observer_type: str):
        self._umwelt = umwelt
        self._observer_type = observer_type

    @property
    def dna(self) -> Any:
        """Forward DNA access to wrapped umwelt."""
        return self._umwelt.dna

    async def get(self) -> Any:
        """Forward get to wrapped umwelt."""
        return await self._umwelt.get()

    async def set(self, value: Any) -> None:
        """Forward set to wrapped umwelt."""
        await self._umwelt.set(value)

    def is_grounded(self, output: Any) -> bool:
        """Forward is_grounded to wrapped umwelt."""
        result = self._umwelt.is_grounded(output)
        return bool(result)


# =============================================================================
# REPL State
# =============================================================================


@dataclass
class ReplState:
    """
    The REPL's current state.

    Principle: Transparent Infrastructure - state is always visible.

    Wave 2 Enhancements:
    - Observer archetype for affordance filtering
    - Logos integration for proper AGENTESE resolution
    - Rich console for beautiful output
    """

    # Current path (e.g., ["self", "soul"])
    path: list[str] = field(default_factory=list)

    # Command history for this session
    history: list[str] = field(default_factory=list)

    # Observer archetype (affects affordances)
    observer: str = "explorer"

    # Is REPL running?
    running: bool = True

    # Last result (for reference in subsequent commands)
    last_result: Any = None

    # Verbosity level
    verbose: bool = False

    # Logos resolver (lazy-loaded)
    _logos: Any = field(default=None, repr=False)

    # Umwelt for observer (lazy-loaded)
    _umwelt: Any = field(default=None, repr=False)

    @property
    def current_path(self) -> str:
        """Get the current path as a dotted string."""
        return ".".join(self.path) if self.path else ""

    @property
    def prompt(self) -> str:
        """Generate the prompt string with observer indicator."""
        # Observer indicator (abbreviated)
        obs_abbrev = {
            "explorer": "E",
            "developer": "D",
            "architect": "A",
            "admin": "*",
        }
        obs = obs_abbrev.get(self.observer, "?")

        if not self.path:
            return f"\033[90m({obs})\033[0m \033[36m[root]\033[0m \033[33m»\033[0m "

        # Color the context differently
        context = self.path[0]
        rest = ".".join(self.path[1:])

        context_colors = {
            "self": "\033[32m",  # green
            "world": "\033[34m",  # blue
            "concept": "\033[35m",  # magenta
            "void": "\033[90m",  # gray
            "time": "\033[33m",  # yellow
        }

        color = context_colors.get(context, "\033[36m")

        if rest:
            return f"\033[90m({obs})\033[0m {color}[{context}\033[0m.{rest}{color}]\033[0m \033[33m»\033[0m "
        else:
            return f"\033[90m({obs})\033[0m {color}[{context}]\033[0m \033[33m»\033[0m "

    def get_logos(self) -> Any:
        """Get or create the Logos resolver (lazy initialization)."""
        if self._logos is None:
            try:
                from protocols.agentese.logos import create_logos

                self._logos = create_logos()
            except ImportError:
                pass  # Logos not available, will use CLI fallback
        return self._logos

    def get_umwelt(self) -> Any:
        """Get or create Umwelt for current observer (lazy initialization)."""
        if (
            self._umwelt is None
            or getattr(self._umwelt, "_observer_type", None) != self.observer
        ):
            try:
                from agents.d.volatile import VolatileAgent
                from bootstrap.umwelt import LightweightUmwelt

                # Create a simple DNA-like object for the observer
                @dataclass
                class ObserverDNA:
                    name: str = "repl_user"
                    archetype: str = "explorer"
                    capabilities: tuple[str, ...] = ()

                dna = ObserverDNA(
                    name="repl_user",
                    archetype=self.observer,
                    capabilities=("manifest", "witness", "affordances")
                    if self.observer == "explorer"
                    else ("manifest", "witness", "affordances", "define")
                    if self.observer in ("developer", "architect", "admin")
                    else (),
                )

                # Create lightweight umwelt with volatile storage
                storage: Any = VolatileAgent(_state={})
                umwelt = LightweightUmwelt(
                    storage=storage,
                    dna=dna,
                    gravity=(),
                )
                # Wrap in a non-frozen container for cache tracking
                self._umwelt = _UmweltWrapper(umwelt, self.observer)
            except ImportError:
                pass  # Umwelt not available
        return self._umwelt


# =============================================================================
# Command Handlers
# =============================================================================


def handle_navigation(state: ReplState, parts: list[str]) -> str | None:
    """
    Handle navigation commands.

    Returns a message to display, or None for no output.

    IMPORTANT: Only handles single-word navigation. Multi-word inputs
    (e.g., "self status") should be treated as invocations, not navigation.
    """
    if not parts:
        return None

    # Multi-word input = not navigation (it's an invocation)
    if len(parts) > 1:
        return None

    cmd = parts[0].lower()

    # Root navigation
    if cmd == "/":
        state.path = []
        return "\033[90m→ root\033[0m"

    # Go up
    if cmd == "..":
        if state.path:
            removed = state.path.pop()
            return f"\033[90m← {removed}\033[0m"
        return "\033[90m(already at root)\033[0m"

    # Show current path
    if cmd == ".":
        if state.path:
            return f"\033[36m{state.current_path}\033[0m"
        return "\033[36m(root)\033[0m"

    # Context navigation (single word - can switch from anywhere)
    if cmd in CONTEXTS:
        if not state.path or state.path[0] != cmd:
            state.path = [cmd]
            return f"\033[90m→ {cmd}\033[0m"
        # Already in this context - no-op
        return f"\033[90m(already in {cmd})\033[0m"

    # Holon navigation (when in a context, single word only)
    if len(state.path) == 1:
        context = state.path[0]
        holons = CONTEXT_HOLONS.get(context, [])
        if cmd in holons:
            state.path.append(cmd)
            return f"\033[90m→ {cmd}\033[0m"

    return None  # Not a navigation command


def handle_introspection(state: ReplState, cmd: str) -> str | None:
    """Handle ? and ?? commands."""
    if cmd == "?":
        return _show_affordances(state)
    elif cmd == "??":
        return _show_detailed_help(state)
    return None


def _show_affordances(state: ReplState) -> str:
    """Show affordances for current location."""
    lines = ["\033[1mAffordances:\033[0m"]

    if not state.path:
        # At root - show contexts
        lines.append("")
        for ctx in sorted(CONTEXTS):
            desc = {
                "self": "Internal state, memory, soul",
                "world": "Agents, infrastructure, resources",
                "concept": "Laws, principles, dialectics",
                "void": "Entropy, shadow, Accursed Share",
                "time": "Traces, forecasts, schedules",
            }.get(ctx, "")
            lines.append(f"  \033[36m{ctx:<10}\033[0m  {desc}")

    elif len(state.path) == 1:
        # In a context - show holons
        context = state.path[0]
        holons = CONTEXT_HOLONS.get(context, [])
        lines.append("")
        for holon in holons:
            lines.append(f"  \033[33m{holon}\033[0m")
        lines.append("")
        lines.append(
            "\033[90mUse '<holon>' to navigate or '<holon> <aspect>' to invoke\033[0m"
        )

    else:
        # In a holon - show aspects
        lines.append("")
        aspects = ["manifest", "witness", "affordances", "refine"]
        for aspect in aspects:
            lines.append(f"  \033[33m{aspect}\033[0m")
        lines.append("")
        lines.append("\033[90mUse '<aspect>' to invoke\033[0m")

    return "\n".join(lines)


def _show_detailed_help(state: ReplState) -> str:
    """Show detailed help for current location."""
    if not state.path:
        return HELP_TEXT

    context = state.path[0]

    context_help = {
        "self": """\
\033[1mself.*\033[0m - The Internal

The self context handles all internal agent operations:
  status       System health at a glance
  memory       Four Pillars memory health
  dream        LucidDreamer morning briefing
  soul         K-gent soul dialogue
  dashboard    Real-time TUI dashboard
  capabilities What can I do? (affordances)

\033[90mPrinciple: Ethical (boundaries of agency)\033[0m
""",
        "world": """\
\033[1mworld.*\033[0m - The External

The world context handles all external operations:
  agents       Agent operations (list, run, inspect)
  daemon       Cortex daemon lifecycle
  infra        K8s infrastructure operations
  fixture      HotData fixtures
  exec         Q-gent execution
  dev          Live reload development mode
  town         Agent Town civilizational simulation

\033[90mPrinciple: Heterarchical (resources in flux)\033[0m
""",
        "concept": """\
\033[1mconcept.*\033[0m - The Abstract

The concept context handles abstract operations:
  laws         Category laws (identity, associativity)
  dialectic    Challenge and refine concepts
  principle    Design principles
  operad       Composition grammar

\033[90mPrinciple: Generative (compressed wisdom)\033[0m
""",
        "void": """\
\033[1mvoid.*\033[0m - The Accursed Share

The void context handles entropy operations:
  entropy      Draw/return randomness
  shadow       Jungian shadow analysis
  serendipity  Request tangents
  gratitude    Express thanks (tithe)
  archetype    Archetypal patterns

\033[90mMeta-Principle: Everything is slop or comes from slop\033[0m
""",
        "time": """\
\033[1mtime.*\033[0m - The Temporal

The time context handles temporal operations:
  trace        View temporal traces
  past         View past state
  future       Forecast (probabilistic)
  schedule     Schedule future actions
  turn         Turn management

\033[90mPrinciple: Heterarchical (temporal composition)\033[0m
""",
    }

    return context_help.get(context, f"No detailed help for {context}")


def handle_invocation(state: ReplState, parts: list[str]) -> str:
    """
    Handle path invocation.

    Wave 2: Tries async Logos first, falls back to CLI routing.
    """
    # Build full path
    if parts[0] in CONTEXTS:
        full_path = parts
    else:
        full_path = state.path + parts

    if not full_path:
        return _error_with_sympathy(
            "No path specified",
            suggestion="Navigate to a context first: self, world, concept, void, time",
        )

    # Convert to dotted path for Logos
    path_str = ".".join(full_path)

    # First, try Logos (Wave 2: async execution)
    logos = state.get_logos()
    umwelt = state.get_umwelt()

    if logos is not None and umwelt is not None:
        # Check if path has an aspect (3+ parts) or needs .manifest
        if len(full_path) >= 3:
            # Has explicit aspect
            try:
                result = asyncio.run(logos.invoke(path_str, umwelt))
                state.last_result = result
                return _render_result(result, state)
            except Exception:
                # Fall back to CLI on any Logos error
                pass
        elif len(full_path) == 2:
            # Holon without aspect - try .manifest
            try:
                result = asyncio.run(logos.invoke(f"{path_str}.manifest", umwelt))
                state.last_result = result
                return _render_result(result, state)
            except Exception:
                # Fall back to CLI
                pass

    # Fall back to CLI routing
    try:
        result = _invoke_path(full_path)
        state.last_result = result
        return result
    except Exception as e:
        return _error_with_sympathy(
            str(e),
            suggestion=_suggest_for_path(full_path),
        )


def _suggest_for_path(path: list[str]) -> str | None:
    """Generate a helpful suggestion for a failed path."""
    if not path:
        return "Try: self, world, concept, void, time"

    context = path[0]
    if context not in CONTEXTS:
        return (
            f"'{context}' is not a valid context. Try: self, world, concept, void, time"
        )

    if len(path) == 1:
        holons = CONTEXT_HOLONS.get(context, [])
        if holons:
            return f"Available in {context}: {', '.join(holons[:5])}"

    if len(path) >= 2:
        return f"Use ? to see affordances at {'.'.join(path[:2])}"

    return None


# =============================================================================
# Error Sympathy & Rich Rendering (Wave 2)
# =============================================================================


def _error_with_sympathy(message: str, suggestion: str | None = None) -> str:
    """
    Format an error message with sympathy (helpful suggestions).

    Principle: Errors should guide, not just fail.
    """
    lines = [f"\033[31mError:\033[0m {message}"]
    if suggestion:
        lines.append(f"\033[33mTry:\033[0m {suggestion}")
    return "\n".join(lines)


def _render_result(result: Any, state: ReplState) -> str:
    """
    Render a result with rich formatting if available.

    Adapts rendering to the type of result:
    - BasicRendering -> Panel with summary/content
    - dict -> Table
    - list -> Numbered list or table
    - str -> Direct output
    - Other -> repr
    """
    console = get_console()

    # Handle BasicRendering from Logos
    if hasattr(result, "summary") and hasattr(result, "content"):
        if RICH_AVAILABLE and console:
            panel = Panel(
                result.content or "(no content)",
                title=result.summary,
                border_style="cyan",
            )
            # Capture to string
            import io as string_io

            from rich.console import Console as RichConsole

            buffer = string_io.StringIO()
            str_console = RichConsole(file=buffer, force_terminal=True)
            str_console.print(panel)
            return buffer.getvalue().rstrip()
        else:
            return f"\033[1m{result.summary}\033[0m\n{result.content or '(no content)'}"

    # Handle dicts
    if isinstance(result, dict):
        if RICH_AVAILABLE and console:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Key", style="yellow")
            table.add_column("Value")
            for k, v in result.items():
                table.add_row(str(k), str(v))
            import io as string_io

            from rich.console import Console as RichConsole

            buffer = string_io.StringIO()
            str_console = RichConsole(file=buffer, force_terminal=True)
            str_console.print(table)
            return buffer.getvalue().rstrip()
        else:
            lines = []
            for k, v in result.items():
                lines.append(f"  \033[33m{k}:\033[0m {v}")
            return "\n".join(lines)

    # Handle lists
    if isinstance(result, list):
        if len(result) == 0:
            return "\033[90m(empty list)\033[0m"

        if RICH_AVAILABLE and console and len(result) <= 20:
            # For short lists, use a table
            if result and isinstance(result[0], dict):
                # List of dicts -> table with columns
                keys = list(result[0].keys())
                table = Table(show_header=True, header_style="bold cyan")
                for key in keys[:5]:  # Limit columns
                    table.add_column(str(key))
                for item in result[:20]:  # Limit rows
                    table.add_row(*[str(item.get(k, "")) for k in keys[:5]])
                import io as string_io

                from rich.console import Console as RichConsole

                buffer = string_io.StringIO()
                str_console = RichConsole(file=buffer, force_terminal=True)
                str_console.print(table)
                return buffer.getvalue().rstrip()

        # Fall back to numbered list
        lines = []
        for i, item in enumerate(result[:20], 1):
            lines.append(f"  {i:3}. {item}")
        if len(result) > 20:
            lines.append(f"  ... and {len(result) - 20} more")
        return "\n".join(lines)

    # Handle strings
    if isinstance(result, str):
        return result

    # Handle None
    if result is None:
        return "\033[90m(ok)\033[0m"

    # Fallback: repr
    return repr(result)


def _invoke_path(path: list[str]) -> str:
    """
    Invoke an AGENTESE path through the CLI routing.

    Maps paths to actual CLI commands.
    """
    if not path:
        return "\033[90m(no path)\033[0m"

    context = path[0]
    rest = path[1:]

    # Route through existing CLI infrastructure
    try:
        if context == "self":
            # Capture output
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.self_ import cmd_self

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_self(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "world":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.world import cmd_world

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_world(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "concept":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.concept import cmd_concept

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_concept(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "void":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.void import cmd_void

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_void(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        elif context == "time":
            import io
            from contextlib import redirect_stdout

            from protocols.cli.contexts.time_ import cmd_time

            f = io.StringIO()
            with redirect_stdout(f):
                cmd_time(rest)
            return f.getvalue().rstrip() or "\033[90m(ok)\033[0m"

        else:
            return f"\033[31mUnknown context: {context}\033[0m"

    except ImportError as e:
        return f"\033[33mContext not implemented:\033[0m {e}"
    except Exception as e:
        return f"\033[31mInvocation error:\033[0m {e}"


def handle_composition(state: ReplState, line: str) -> str:
    """
    Handle >> composition operator.

    Wave 2: Actually executes the pipeline through Logos!

    Example: world.agents.list >> concept.count
    """
    parts = [p.strip() for p in line.split(">>")]

    if len(parts) < 2:
        return _error_with_sympathy(
            "Composition requires at least two paths",
            suggestion="Try: self.status >> time.trace",
        )

    # Build full paths by prepending current context if needed
    full_paths = []
    for part in parts:
        if part.split(".")[0] in CONTEXTS or part.split()[0] in CONTEXTS:
            full_paths.append(part)
        else:
            # Prepend current path
            if state.path:
                full_paths.append(f"{state.current_path}.{part}")
            else:
                full_paths.append(part)

    # Try to execute through Logos
    logos = state.get_logos()
    umwelt = state.get_umwelt()

    if logos is not None and umwelt is not None:
        try:
            # Execute pipeline
            composed = logos.compose(*full_paths)
            result = asyncio.run(composed.invoke(umwelt))

            # Render result
            return _render_result(result, state)
        except Exception as e:
            # Fall back to CLI execution with sympathy
            return _execute_pipeline_cli(state, full_paths, e)
    else:
        # No Logos available, use CLI fallback
        return _execute_pipeline_cli(state, full_paths, None)


def _execute_pipeline_cli(
    state: ReplState, paths: list[str], logos_error: Exception | None
) -> str:
    """Execute pipeline via CLI routing (fallback when Logos unavailable)."""
    lines = []

    if logos_error:
        lines.append(f"\033[33mLogos unavailable:\033[0m {logos_error}")
        lines.append("\033[90mFalling back to CLI routing...\033[0m")
        lines.append("")

    # Execute each path sequentially
    current_input = None
    for i, path in enumerate(paths):
        lines.append(f"\033[90m[{i + 1}/{len(paths)}]\033[0m \033[36m{path}\033[0m")

        # Parse and execute through CLI
        parts = path.replace(".", " ").split()
        result = _invoke_path(parts)
        lines.append(result)

        if i < len(paths) - 1:
            lines.append("")  # Separator between steps
            # Pass result forward (for future use when CLI supports it)
            current_input = result

    state.last_result = current_input
    return "\n".join(lines)


def handle_observer_command(state: ReplState, line: str) -> str:
    """
    Handle /observer commands for switching observer context.

    Commands:
        /observer            - Show current observer
        /observer <arch>     - Switch to archetype
        /observers           - List all archetypes
    """
    parts = line.strip().split()
    cmd = parts[0].lower()

    if cmd == "/observers":
        # List all archetypes
        lines = ["\033[1mObserver Archetypes:\033[0m", ""]
        for arch, desc in OBSERVER_ARCHETYPES.items():
            marker = " \033[32m←\033[0m" if arch == state.observer else ""
            lines.append(f"  \033[33m{arch:<12}\033[0m {desc}{marker}")
        return "\n".join(lines)

    if cmd == "/observer":
        if len(parts) == 1:
            # Show current
            desc = OBSERVER_ARCHETYPES.get(state.observer, "Unknown")
            return f"\033[1mCurrent observer:\033[0m \033[33m{state.observer}\033[0m\n{desc}"

        # Switch to new archetype
        new_arch = parts[1].lower()
        if new_arch not in OBSERVER_ARCHETYPES:
            return _error_with_sympathy(
                f"Unknown archetype: {new_arch}",
                suggestion=f"Available: {', '.join(OBSERVER_ARCHETYPES.keys())}",
            )

        old_arch = state.observer
        state.observer = new_arch
        # Invalidate umwelt cache so it gets recreated with new archetype
        state._umwelt = None

        # Show what changed
        return (
            f"\033[90mObserver changed:\033[0m {old_arch} → \033[33m{new_arch}\033[0m\n"
            f"\033[90m{OBSERVER_ARCHETYPES[new_arch]}\033[0m"
        )

    return _error_with_sympathy(
        f"Unknown command: {cmd}",
        suggestion="Try: /observer, /observer developer, /observers",
    )


# =============================================================================
# Tab Completion
# =============================================================================


class Completer:
    """Tab completion for AGENTESE paths."""

    def __init__(self, state: ReplState):
        self.state = state
        self.matches: list[str] = []

    def complete(self, text: str, state_idx: int) -> str | None:
        """Return the state_idx'th completion for text."""
        if state_idx == 0:
            self.matches = self._get_matches(text)

        if state_idx < len(self.matches):
            return self.matches[state_idx]
        return None

    def _get_matches(self, text: str) -> list[str]:
        """Get all completions matching text."""
        matches = []

        # At root, complete contexts
        if not self.state.path:
            matches = [c for c in CONTEXTS if c.startswith(text)]

        # In context, complete holons
        elif len(self.state.path) == 1:
            context = self.state.path[0]
            holons = CONTEXT_HOLONS.get(context, [])
            matches = [h for h in holons if h.startswith(text)]

        # In holon, complete aspects
        else:
            aspects = [
                "manifest",
                "witness",
                "affordances",
                "refine",
                "lens",
                "define",
                "sip",
                "tithe",
            ]
            matches = [a for a in aspects if a.startswith(text)]

        # Add special commands
        special = [
            "..",
            ".",
            "/",
            "?",
            "??",
            "help",
            "exit",
            "quit",
            "clear",
            "/observer",
            "/observers",
        ]
        matches.extend([s for s in special if s.startswith(text)])

        # Complete archetype names after /observer
        if text.startswith("/observer "):
            prefix = text[len("/observer ") :]
            matches = [
                f"/observer {a}" for a in OBSERVER_ARCHETYPES if a.startswith(prefix)
            ]

        return sorted(set(matches))


# =============================================================================
# Main REPL Loop
# =============================================================================


def run_repl(
    ctx: "InvocationContext | None" = None,
    verbose: bool = False,
) -> int:
    """
    Run the AGENTESE REPL.

    This is a synchronous function that blocks until the user exits.

    Principle: Joy-Inducing - the REPL should feel warm and responsive.
    """
    state = ReplState(verbose=verbose)

    # Set up tab completion
    completer = Completer(state)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")

    # Set up history file
    history_file = Path.home() / ".kgents_repl_history"
    try:
        readline.read_history_file(history_file)
    except (FileNotFoundError, PermissionError, OSError):
        pass  # History unavailable, continue without

    # Print welcome banner
    print(WELCOME_BANNER)

    # Main loop
    while state.running:
        try:
            line = input(state.prompt).strip()

            if not line:
                continue

            # Add to history
            state.history.append(line)

            # Handle special commands
            if line.lower() in ("exit", "quit", "q"):
                print("\033[90mFarewell. The river flows.\033[0m")
                break

            if line.lower() == "help":
                print(HELP_TEXT)
                continue

            if line.lower() == "clear":
                print("\033[2J\033[H", end="")
                continue

            if line.lower() == "history":
                for i, cmd in enumerate(state.history[-20:], 1):
                    print(f"  {i:3}  {cmd}")
                continue

            # Check for /observer commands (Wave 2)
            if line.startswith("/observer") or line == "/observers":
                observer_result = handle_observer_command(state, line)
                print(observer_result)
                continue

            # Check for introspection
            intro_result = handle_introspection(state, line)
            if intro_result is not None:
                print(intro_result)
                continue

            # Check for composition
            if ">>" in line:
                comp_result = handle_composition(state, line)
                print(comp_result)
                continue

            # Parse command
            parts = line.split()

            # Check for navigation
            nav_result = handle_navigation(state, parts)
            if nav_result is not None:
                print(nav_result)
                continue

            # Otherwise, treat as invocation
            result = handle_invocation(state, parts)
            if result:
                print(result)

        except KeyboardInterrupt:
            print("\n\033[90m(use 'exit' to leave)\033[0m")
            continue

        except EOFError:
            print("\n\033[90mFarewell. The river flows.\033[0m")
            break

        except Exception as e:
            print(f"\033[31mError:\033[0m {e}")
            if verbose:
                import traceback

                traceback.print_exc()

    # Save history
    try:
        readline.write_history_file(history_file)
    except Exception:
        pass

    return 0


# =============================================================================
# Entry Point
# =============================================================================


def cmd_interactive(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Enter the AGENTESE REPL.

    The REPL provides interactive navigation through the five contexts,
    with tab completion, history, and path composition.
    """
    verbose = "--verbose" in args or "-v" in args

    return run_repl(ctx=ctx, verbose=verbose)


if __name__ == "__main__":
    sys.exit(cmd_interactive(sys.argv[1:]))
