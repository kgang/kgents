"""
CLI Projection Functor - The Bridge from CLI to AGENTESE.

This module implements the Isomorphic CLI architecture from spec/protocols/cli.md Part III.
It provides the projection functor that transforms CLI invocations into AGENTESE paths.

The Core Insight:
    "CLI commands are projections of AGENTESE paths into the terminal substrate."

    CLIProject : (Path, Observer, Dimensions) -> TerminalOutput

Instead of handlers with scattered logic:
    def cmd_brain(args):
        if is_capture: return _handle_capture(args)
        if is_search: return _handle_search(args)
        ...

We have:
    def cmd_brain(args):
        path = route_subcommand_to_path(args)
        return project_command(path, args)

Usage:
    from protocols.cli.projection import project_command

    def cmd_brain(args: list[str], ctx: Any) -> int:
        subcommand = _parse_subcommand(args)
        path = SUBCOMMAND_TO_PATH.get(subcommand, "self.memory.manifest")
        return project_command(path, args, ctx)
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .dimensions import (
    DEFAULT_DIMENSIONS,
    Backend,
    CommandDimensions,
    Execution,
    Interactivity,
    Seriousness,
    derive_dimensions,
)

if TYPE_CHECKING:
    from protocols.agentese.affordances import AspectMetadata
    from protocols.agentese.logos import Logos


# === Terminal Output Types ===


@dataclass
class TerminalOutput:
    """
    Output formatted for terminal rendering.

    This is what the projection functor produces.
    """

    content: str
    """The main content to display."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata (shown in JSON mode or for tracing)."""

    exit_code: int = 0
    """Process exit code."""

    error: str | None = None
    """Error message if any."""

    def to_json(self) -> str:
        """Render as JSON."""
        return json.dumps(
            {
                "content": self.content,
                "metadata": self.metadata,
                "exit_code": self.exit_code,
                "error": self.error,
            },
            indent=2,
            default=str,
        )

    def to_plain(self) -> str:
        """Render as plain text."""
        if self.error:
            return f"Error: {self.error}"
        return self.content


# === Pre-UX Handlers ===


async def _handle_pre_ux_confirmation(
    path: str,
    dimensions: CommandDimensions,
    observer: Any,
) -> bool:
    """
    Handle pre-invocation confirmation for sensitive commands.

    Returns True if execution should proceed, False to abort.
    """
    if not dimensions.needs_confirmation:
        return True

    # In CLI context, prompt for confirmation
    # For now, we'll auto-approve in non-interactive contexts
    # Full implementation would check if stdin is a TTY
    print(f"[CONFIRM] This operation modifies sensitive resources: {path}")
    print("          Proceeding automatically (TTY detection TODO)")
    return True


async def _handle_pre_ux_budget(
    path: str,
    dimensions: CommandDimensions,
    observer: Any,
) -> None:
    """Show budget warning for LLM-backed commands."""
    if dimensions.needs_budget_display:
        # Show budget indicator
        print(f"[BUDGET] LLM call: {path}")


# === Post-UX Handlers ===


def _format_result(
    result: Any,
    dimensions: CommandDimensions,
    json_output: bool = False,
) -> TerminalOutput:
    """
    Format a result based on dimensions.

    The dimensions inform how we format:
    - PLAYFUL: Fun, emoji-rich formatting
    - SENSITIVE: Clear, explicit formatting
    - NEUTRAL: Standard formatting
    """
    # Handle dict results
    if isinstance(result, dict):
        if json_output:
            return TerminalOutput(
                content=json.dumps(result, indent=2, default=str),
                metadata=result,
                exit_code=0,
            )

        # Check for error
        if "error" in result:
            return TerminalOutput(
                content="",
                error=result["error"],
                exit_code=1,
            )

        # Format based on seriousness
        match dimensions.seriousness:
            case Seriousness.PLAYFUL:
                content = _format_playful(result)
            case Seriousness.SENSITIVE:
                content = _format_sensitive(result)
            case _:
                content = _format_neutral(result)

        return TerminalOutput(content=content, metadata=result, exit_code=0)

    # Handle BasicRendering or similar
    if hasattr(result, "content"):
        return TerminalOutput(
            content=str(result.content) if result.content else str(result.summary),
            metadata=getattr(result, "metadata", {}) or {},
            exit_code=0,
        )

    # Handle string results
    if isinstance(result, str):
        return TerminalOutput(content=result, exit_code=0)

    # Fallback: convert to string
    return TerminalOutput(content=str(result), exit_code=0)


def _format_playful(result: dict[str, Any]) -> str:
    """Format result with playful styling (void.* context)."""
    lines = []
    for key, value in result.items():
        if key.startswith("_"):
            continue
        emoji = _get_emoji_for_key(key)
        lines.append(f"{emoji} {key}: {value}")
    return "\n".join(lines)


def _format_sensitive(result: dict[str, Any]) -> str:
    """Format result with clear, explicit styling (protected resources)."""
    lines = []
    for key, value in result.items():
        if key.startswith("_"):
            continue
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def _format_neutral(result: dict[str, Any]) -> str:
    """Format result with standard styling."""
    lines = []
    for key, value in result.items():
        if key.startswith("_"):
            continue
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _get_emoji_for_key(key: str) -> str:
    """Get an emoji for a result key."""
    emoji_map = {
        "status": "✅",
        "error": "❌",
        "count": "#️⃣",
        "total": "📊",
        "query": "🔍",
        "results": "📋",
        "memory": "🧠",
        "captured": "💾",
        "surfaced": "🌀",
    }
    return emoji_map.get(key, "•")


# === CLI Projection Functor ===


@dataclass
class CLIProjection:
    """
    The CLI projection functor.

    Projects AGENTESE paths to terminal output, handling:
    1. Pre-UX: Confirmation, budget warnings
    2. Invocation: Through Logos
    3. Post-UX: Formatting based on dimensions
    """

    logos: "Logos"
    json_output: bool = False
    trace_mode: bool = False

    async def project(
        self,
        path: str,
        observer: Any,
        dimensions: CommandDimensions,
        kwargs: dict[str, Any],
    ) -> TerminalOutput:
        """
        Project an AGENTESE path to terminal output.

        This is the main entry point for the projection functor.

        Args:
            path: The AGENTESE path (e.g., "self.memory.capture")
            observer: The observer (Umwelt or dict)
            dimensions: Command dimensions for behavior
            kwargs: Arguments to pass to the aspect

        Returns:
            TerminalOutput ready for rendering
        """
        # Pre-UX: Confirmation for sensitive operations
        if not await _handle_pre_ux_confirmation(path, dimensions, observer):
            return TerminalOutput(
                content="Operation cancelled",
                exit_code=1,
            )

        # Pre-UX: Budget warning for LLM calls
        await _handle_pre_ux_budget(path, dimensions, observer)

        # Trace mode: Show path being invoked
        if self.trace_mode:
            print(f"[TRACE] Invoking: {path}")
            print(f"[TRACE] Dimensions: {dimensions}")

        try:
            # Invoke through Logos
            result = await self.logos.invoke(path, observer, **kwargs)

            # Post-UX: Format result
            return _format_result(result, dimensions, self.json_output)

        except Exception as e:
            return TerminalOutput(
                content="",
                error=str(e),
                exit_code=1,
            )


# === Main Entry Point ===


def project_command(
    path: str,
    args: list[str],
    ctx: Any = None,
    *,
    json_output: bool = False,
    trace_mode: bool = False,
    kwargs: dict[str, Any] | None = None,
    entity_name: str | None = None,
) -> int:
    """
    Main entry point for CLI -> AGENTESE projection.

    This is what handlers call instead of direct business logic.

    Args:
        path: The AGENTESE path (e.g., "self.memory.capture")
        args: CLI arguments (for extracting kwargs)
        ctx: InvocationContext (optional)
        json_output: Whether to output JSON
        trace_mode: Whether to show trace information
        kwargs: Pre-parsed kwargs (optional, extracted from args if not provided)
        entity_name: Display name for chat entities (optional)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Bootstrap providers FIRST - this imports service nodes and populates registry
    # CRITICAL: Must happen before registry.has() check, otherwise service nodes
    # like GraphNode won't be registered and we fall through to JIT fallback
    from services.providers import setup_providers_sync

    setup_providers_sync()

    # Ensure all context modules are also imported (populates registry with legacy paths)
    from protocols.agentese.gateway import _import_node_modules

    _import_node_modules()

    # Create observer (CLI archetype)
    from protocols.agentese.node import Observer

    observer = Observer.from_archetype("cli")

    # Parse kwargs from args if not provided
    if kwargs is None:
        kwargs = _parse_kwargs_from_args(args, path)

    # Handle json/trace flags from args
    if "--json" in args:
        json_output = True
    if "--trace" in args:
        trace_mode = True

    # Check for --message flag for one-shot chat
    one_shot_message = kwargs.pop("message", None)

    # Parse path into node_path and aspect
    parts = path.split(".")
    if len(parts) < 3:
        print(f"Error: Path must include aspect: '{path}'")
        return 1

    node_path = ".".join(parts[:-1])
    aspect = parts[-1]

    # Try registry first (with DI container) for nodes that need dependencies
    from protocols.agentese.container import get_container
    from protocols.agentese.registry import get_registry

    registry = get_registry()
    container = get_container()

    if registry.has(node_path):
        try:
            result = _run_async(
                _invoke_via_registry(registry, container, node_path, aspect, observer, **kwargs)
            )

            # Render output
            if json_output:
                import json as json_mod

                # Handle BasicRendering and similar types with metadata
                if hasattr(result, "metadata") and result.metadata:
                    json_data = result.metadata
                elif hasattr(result, "__dataclass_fields__"):
                    from dataclasses import asdict

                    json_data = asdict(result)
                elif isinstance(result, dict):
                    json_data = result
                else:
                    json_data = {"result": str(result)}
                print(json_mod.dumps(json_data, indent=2, default=str))
            else:
                _render_result(result)

            return 0

        except Exception as e:
            print(f"Error: {e}")
            return 1

    # AD-016: Fail-fast on unregistered paths (no JIT fallback)
    # Silent JIT fallback masks registration bugs - fail immediately with helpful error
    from protocols.agentese.exceptions import node_not_registered

    # Find similar registered paths for typo correction
    all_paths = registry.list_paths()
    context_prefix = node_path.split(".")[0] if "." in node_path else ""
    similar = [p for p in all_paths if context_prefix and p.startswith(context_prefix)][:5]

    # If no context matches, show some available paths
    if not similar:
        similar = all_paths[:5]

    error = node_not_registered(node_path, similar=similar)
    print(f"Error: {error}")
    return 1


async def _invoke_via_registry(
    registry: Any,
    container: Any,
    node_path: str,
    aspect: str,
    observer: Any,
    **kwargs: Any,
) -> Any:
    """Invoke a path via the registry with DI container."""
    node = await registry.resolve(node_path, container)
    if node is None:
        raise ValueError(f"Failed to resolve node: {node_path}")
    return await node.invoke(aspect, observer, **kwargs)


def _render_result(result: Any) -> None:
    """Render a result to terminal."""
    if result is None:
        return

    # Handle Renderable types
    if hasattr(result, "summary"):
        print(result.summary)
        if hasattr(result, "content") and result.content:
            print(result.content)
        return

    # Handle dataclasses
    if hasattr(result, "__dataclass_fields__"):
        import json as json_mod
        from dataclasses import asdict

        print(json_mod.dumps(asdict(result), indent=2, default=str))
        return

    # Default: print string representation
    print(result)


def _project_chat(
    path: str,
    observer: Any,
    entity_name: str | None = None,
    one_shot_message: str | None = None,
    json_output: bool = False,
) -> int:
    """
    Project to ChatProjection for INTERACTIVE paths (deprecated).

    Chat functionality has been removed in the Crown Jewel Cleanup.
    """
    print("Chat functionality is not available in this version.")
    return 1


def _parse_kwargs_from_args(args: list[str], path: str) -> dict[str, Any]:
    """
    Parse kwargs from CLI arguments.

    Supports:
    - Positional arguments (mapped to "content" or "query" based on path)
    - --key=value or --key value flags
    - Boolean flags like --dry-run
    """
    kwargs: dict[str, Any] = {}
    positional: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]

        # Skip subcommand (first non-flag arg if it matches known commands)
        if i == 0 and not arg.startswith("-"):
            i += 1
            continue

        if arg.startswith("--"):
            # Handle --key=value
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                kwargs[key.replace("-", "_")] = value
            # Handle --key value or --boolean-flag
            elif i + 1 < len(args) and not args[i + 1].startswith("-"):
                key = arg[2:].replace("-", "_")
                kwargs[key] = args[i + 1]
                i += 1
            else:
                # Boolean flag
                key = arg[2:].replace("-", "_")
                kwargs[key] = True
        elif not arg.startswith("-"):
            positional.append(arg)

        i += 1

    # Map positional to expected parameter
    if positional:
        # Heuristic: capture uses "content", search uses "query"
        if "capture" in path:
            kwargs["content"] = " ".join(positional)
        elif "search" in path or "ghost" in path:
            kwargs["query"] = " ".join(positional)
        elif "surface" in path:
            kwargs["context"] = " ".join(positional)
        # Graph operations
        elif "neighbors" in path:
            kwargs["path"] = positional[0]
        elif "evidence" in path:
            kwargs["spec_path"] = positional[0]
        elif "trace" in path:
            if len(positional) >= 2:
                kwargs["start"] = positional[0]
                kwargs["end"] = positional[1]
            elif len(positional) == 1:
                kwargs["start"] = positional[0]
        else:
            # Default to content
            kwargs["content"] = " ".join(positional)

    return kwargs


def _run_async(coro: Any) -> Any:
    """Run an async coroutine synchronously, handling running event loops.

    This function handles three cases:
    1. No event loop running (normal CLI): Use asyncio.run()
    2. Event loop running in current thread: Spawn thread to run asyncio.run()
    3. Inside daemon thread pool: Create fresh event loop for this coroutine

    The key insight is that database sessions must be created and used within
    the same event loop. When running in daemon context, we create a fresh
    loop that lives for the duration of this coroutine.
    """
    import os

    try:
        loop = asyncio.get_running_loop()
        # Event loop already running in this thread
        # Spawn a new thread with its own loop
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running event loop in this thread
        # Check if we're inside daemon context (thread pool)
        inside_daemon = os.environ.get("KGENTS_INSIDE_DAEMON") is None and \
                       os.environ.get("KGENTS_DAEMON_WORKER") is not None

        if inside_daemon:
            # Running in daemon worker thread - create a fresh loop
            # that will be properly closed after the coroutine completes
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                # Clean up pending tasks
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                loop.close()
                asyncio.set_event_loop(None)
        else:
            # Normal CLI execution - use asyncio.run()
            return asyncio.run(coro)


# === Subcommand Routing ===


def route_to_path(
    subcommand: str,
    subcommand_map: dict[str, str],
    default_path: str,
) -> str:
    """
    Route a subcommand to an AGENTESE path.

    Args:
        subcommand: The CLI subcommand (e.g., "capture")
        subcommand_map: Mapping from subcommand to path
        default_path: Path to use if subcommand not found

    Returns:
        AGENTESE path
    """
    return subcommand_map.get(subcommand, default_path)


__all__ = [
    # Types
    "TerminalOutput",
    "CLIProjection",
    # Functions
    "project_command",
    "route_to_path",
    "derive_dimensions",
    # Chat projection (re-exported)
    "_project_chat",
]
