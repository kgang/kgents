"""
AGENTESE Router: Unified CLI-to-Logos bridge.

This module is the heart of Phase 3 CLI Integration.
It routes all CLI invocations through Logos:

    1. Direct paths: kg self.forest.manifest
    2. Shortcuts:    kg /forest
    3. Legacy cmds:  kg forest status
    4. Queries:      kg ?world.*
    5. Composition:  kg self.forest.manifest >> concept.summary.refine

The router resolves input to AGENTESE paths and invokes via Logos,
with automatic OTEL tracing and error handling.

Per spec/protocols/agentese-v3.md §12 (CLI Unification).
"""

from __future__ import annotations

import asyncio
import sys
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .legacy import expand_legacy, is_legacy_command
from .shortcuts import expand_shortcut, is_shortcut

if TYPE_CHECKING:
    from protocols.agentese import Logos, Observer
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Input Classification
# =============================================================================


class InputType:
    """Classification of CLI input."""

    DIRECT_PATH = "direct_path"  # self.forest.manifest
    SHORTCUT = "shortcut"  # /forest
    LEGACY = "legacy"  # forest status
    QUERY = "query"  # ?world.*
    SUBSCRIBE = "subscribe"  # subscribe world.town.*
    COMPOSITION = "composition"  # path >> path
    UNKNOWN = "unknown"


@dataclass
class ClassifiedInput:
    """Result of classifying CLI input."""

    input_type: str
    original: str
    agentese_path: str
    remaining_args: list[str] = field(default_factory=list)
    composition_parts: list[str] = field(default_factory=list)


def classify_input(args: list[str]) -> ClassifiedInput:
    """
    Classify CLI input into its type.

    Priority:
        1. Query (starts with ?)
        2. Subscribe (starts with "subscribe")
        3. Shortcut (starts with /)
        4. Composition (contains >>)
        5. Direct path (contains .)
        6. Legacy command (known legacy prefix)
        7. Unknown

    Args:
        args: Command-line arguments

    Returns:
        ClassifiedInput with type and expansion
    """
    if not args:
        return ClassifiedInput(
            input_type=InputType.UNKNOWN,
            original="",
            agentese_path="",
        )

    first = args[0]
    remaining = args[1:]

    # Composition: path >> path (check first, as it spans multiple args)
    full_input = " ".join(args)
    if ">>" in full_input:
        parts = [p.strip() for p in full_input.split(">>")]
        return ClassifiedInput(
            input_type=InputType.COMPOSITION,
            original=full_input,
            agentese_path=parts[0],
            composition_parts=parts,
        )

    # Query: ?pattern
    if first.startswith("?"):
        return ClassifiedInput(
            input_type=InputType.QUERY,
            original=first,
            agentese_path=first[1:],  # Remove leading ?
            remaining_args=remaining,
        )

    # Subscribe: subscribe pattern
    if first == "subscribe":
        if not remaining:
            return ClassifiedInput(
                input_type=InputType.SUBSCRIBE,
                original="subscribe",
                agentese_path="",
                remaining_args=[],
            )
        return ClassifiedInput(
            input_type=InputType.SUBSCRIBE,
            original=f"subscribe {remaining[0]}",
            agentese_path=remaining[0],
            remaining_args=remaining[1:],
        )

    # Shortcut: /name or /name.aspect
    if is_shortcut(first):
        expanded = expand_shortcut(first)
        return ClassifiedInput(
            input_type=InputType.SHORTCUT,
            original=first,
            agentese_path=expanded,
            remaining_args=remaining,
        )

    # Direct path: contains .
    if "." in first:
        return ClassifiedInput(
            input_type=InputType.DIRECT_PATH,
            original=first,
            agentese_path=first,
            remaining_args=remaining,
        )

    # Legacy command: known prefix
    if is_legacy_command(args):
        path, rest = expand_legacy(args)
        return ClassifiedInput(
            input_type=InputType.LEGACY,
            original=" ".join(args[: len(args) - len(rest)]),
            agentese_path=path,
            remaining_args=rest,
        )

    # Unknown
    return ClassifiedInput(
        input_type=InputType.UNKNOWN,
        original=first,
        agentese_path=first,
        remaining_args=remaining,
    )


# =============================================================================
# AGENTESE Router
# =============================================================================


@dataclass
class RouterConfig:
    """Configuration for the AGENTESE router."""

    # Output format
    json_output: bool = False
    trace_output: bool = False
    dry_run: bool = False

    # Telemetry
    otel_enabled: bool = True

    # Observer
    archetype: str = "cli"


@dataclass
class RouterResult:
    """Result of routing a CLI invocation."""

    success: bool
    result: Any = None
    error: str | None = None
    agentese_path: str = ""
    trace_id: str | None = None
    duration_ms: int = 0


class AgentesRouter:
    """
    Unified CLI-to-Logos router.

    Routes all CLI invocations through Logos with:
        - Automatic shortcut/legacy expansion
        - OTEL tracing
        - Error sympathy
        - JSON/human output modes
    """

    def __init__(
        self,
        logos: "Logos | None" = None,
        config: RouterConfig | None = None,
    ):
        self._logos = logos
        self._config = config or RouterConfig()
        self._observer: "Observer | None" = None

    @property
    def logos(self) -> Any:
        """Get or create the Logos instance (WiredLogos or Logos)."""
        if self._logos is None:
            from protocols.agentese import create_wired_logos

            self._logos = create_wired_logos()  # type: ignore[assignment]
        return self._logos

    @property
    def observer(self) -> "Observer":
        """Get or create the Observer."""
        if self._observer is None:
            from protocols.agentese import Observer

            self._observer = Observer.from_archetype(self._config.archetype)
        return self._observer

    async def route(
        self,
        args: list[str],
        ctx: "InvocationContext | None" = None,
    ) -> RouterResult:
        """
        Route CLI arguments through Logos.

        Args:
            args: Command-line arguments
            ctx: Optional invocation context for output

        Returns:
            RouterResult with success/error and result
        """
        start_time = time.time()
        trace_id: str | None = None

        # Classify input
        classified = classify_input(args)

        if classified.input_type == InputType.UNKNOWN:
            return RouterResult(
                success=False,
                error=f"Unknown command: {classified.original}",
                agentese_path="",
                duration_ms=int((time.time() - start_time) * 1000),
            )

        try:
            # Get trace context if OTEL enabled
            if self._config.otel_enabled:
                trace_id = self._start_trace(classified)

            # Route based on type
            if classified.input_type == InputType.QUERY:
                result = await self._handle_query(classified, ctx)
            elif classified.input_type == InputType.SUBSCRIBE:
                result = await self._handle_subscribe(classified, ctx)
            elif classified.input_type == InputType.COMPOSITION:
                result = await self._handle_composition(classified, ctx)
            else:
                result = await self._handle_invoke(classified, ctx)

            return RouterResult(
                success=True,
                result=result,
                agentese_path=classified.agentese_path,
                trace_id=trace_id,
                duration_ms=int((time.time() - start_time) * 1000),
            )

        except Exception as e:
            return RouterResult(
                success=False,
                error=str(e),
                agentese_path=classified.agentese_path,
                trace_id=trace_id,
                duration_ms=int((time.time() - start_time) * 1000),
            )

    async def _handle_invoke(
        self,
        classified: ClassifiedInput,
        ctx: "InvocationContext | None",
    ) -> Any:
        """Handle a direct path/shortcut/legacy invocation."""
        path = classified.agentese_path
        kwargs = self._parse_kwargs(classified.remaining_args)

        if self._config.dry_run:
            return {
                "dry_run": True,
                "path": path,
                "type": classified.input_type,
                "original": classified.original,
                "kwargs": kwargs,
            }

        # Special handling for interactive chat paths
        # These need to route to ChatProjection REPL instead of Logos invoke
        if path.endswith(".chat") or ".chat." in path:
            return await self._handle_chat(path, kwargs, ctx)

        # Use invoke() method - works with both Logos and WiredLogos
        result = await self.logos.invoke(path, self.observer, **kwargs)
        return result

    async def _handle_chat(
        self,
        path: str,
        kwargs: dict[str, Any],
        ctx: "InvocationContext | None",
    ) -> Any:
        """
        Handle interactive chat paths.

        Routes to ChatProjection REPL for paths like:
        - self.soul.chat
        - world.town.citizen.elara.chat
        - self.soul.chat.send (with message kwarg for one-shot)
        """
        from protocols.cli.chat_projection import run_chat_one_shot, run_chat_repl

        # Extract parent path (remove .chat.* suffix)
        parent_path = path
        if ".chat." in path:
            parent_path = path.split(".chat.")[0]
        elif path.endswith(".chat"):
            parent_path = path[:-5]

        # Check for one-shot message
        message = kwargs.get("message")

        # Derive entity name from path
        parts = parent_path.split(".")
        if "soul" in parts:
            entity_name = "K-gent"
        elif "citizen" in parts and len(parts) > 3:
            entity_name = parts[3].title()
        else:
            entity_name = parts[-1].title()

        # One-shot mode
        if message:
            run_chat_one_shot(
                node_path=parent_path,
                message=message,
                observer=self.observer,
                json_output=self._config.json_output,
            )
            return None  # Output handled by chat projection

        # Interactive REPL mode
        run_chat_repl(
            node_path=parent_path,
            observer=self.observer,
            entity_name=entity_name,
        )
        return None  # Output handled by chat projection

    async def _handle_query(
        self,
        classified: ClassifiedInput,
        ctx: "InvocationContext | None",
    ) -> Any:
        """Handle a query invocation."""
        pattern = classified.agentese_path
        kwargs = self._parse_kwargs(classified.remaining_args)

        # Show help if no pattern
        if not pattern:
            from protocols.cli.query_help import show_query_help

            show_query_help()
            return None

        # Extract query constraints from kwargs
        limit = int(kwargs.pop("limit", 100))
        offset = int(kwargs.pop("offset", 0))
        dry_run = bool(kwargs.pop("dry_run", False))
        json_output = bool(kwargs.pop("json", self.config.json_output))

        from protocols.agentese import query as agentese_query

        # Execute query with ? prefix
        result = agentese_query(
            self.logos,
            f"?{pattern}",
            limit=limit,
            offset=offset,
            observer=self.observer,
            dry_run=dry_run,
        )

        # Format output (unless JSON requested)
        if not json_output:
            from protocols.cli.query_help import format_query_result

            formatted = format_query_result(result)
            print(formatted)
            return None

        return result

    async def _handle_subscribe(
        self,
        classified: ClassifiedInput,
        ctx: "InvocationContext | None",
    ) -> Any:
        """Handle a subscription invocation."""
        pattern = classified.agentese_path

        if not pattern:
            print("Usage: kg subscribe <pattern>")
            print()
            print("Examples:")
            print("  kg subscribe self.memory.*")
            print("  kg subscribe world.town.**")
            return None

        print(f"Subscribing to: {pattern}")
        print("(Press Ctrl+C to stop)")
        print()

        try:
            from protocols.agentese import create_subscription_manager

            # Create subscription manager
            sub_manager = create_subscription_manager()
            subscription = await sub_manager.subscribe(pattern)

            try:
                async for event in subscription:
                    timestamp = event.timestamp.strftime("%H:%M:%S")
                    print(f"[{timestamp}] {event.event_type.value}: {event.path}")
                    if event.data:
                        print(f"  Data: {event.data}")
            except KeyboardInterrupt:
                print("\nSubscription ended.")
            finally:
                await subscription.close()
        except ImportError as e:
            print(f"Subscription system not available: {e}")

        return None

    async def _handle_composition(
        self,
        classified: ClassifiedInput,
        ctx: "InvocationContext | None",
    ) -> Any:
        """Handle a composition (a >> b >> c)."""
        from protocols.agentese import path as agentese_path

        # Build composed path
        parts = classified.composition_parts
        if len(parts) < 2:
            return await self._handle_invoke(classified, ctx)

        # Expand any shortcuts in parts
        expanded_parts = [expand_shortcut(p) if is_shortcut(p) else p for p in parts]

        if self._config.dry_run:
            return {
                "dry_run": True,
                "composition": [str(p) for p in expanded_parts],
                "type": "composition",
            }

        # Create and execute composition
        composed: Any = agentese_path(expanded_parts[0])
        for p in expanded_parts[1:]:
            composed = composed >> p

        result = await composed.run(self.observer, self.logos)
        return result

    def _parse_kwargs(self, args: list[str]) -> dict[str, Any]:
        """Parse remaining arguments into kwargs."""
        kwargs: dict[str, Any] = {}

        i = 0
        while i < len(args):
            arg = args[i]

            if arg.startswith("--"):
                key = arg[2:].replace("-", "_")

                if "=" in key:
                    key, value = key.split("=", 1)
                    kwargs[key] = value
                elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                    kwargs[key] = args[i + 1]
                    i += 1
                else:
                    kwargs[key] = True

            i += 1

        return kwargs

    def _start_trace(self, classified: ClassifiedInput) -> str | None:
        """Start OTEL trace for this invocation."""
        try:
            from opentelemetry import trace

            tracer = trace.get_tracer("kgents.cli")
            span = tracer.start_span(
                f"cli.{classified.input_type}",
                attributes={
                    "agentese.path": classified.agentese_path,
                    "agentese.input_type": classified.input_type,
                    "agentese.original": classified.original,
                },
            )
            return span.get_span_context().trace_id.to_bytes(16, "big").hex()
        except ImportError:
            return None
        except Exception:
            return None


# =============================================================================
# Module-Level Functions
# =============================================================================

# Global router instance (lazy-initialized)
_router: AgentesRouter | None = None


def get_router(logos: "Logos | None" = None) -> AgentesRouter:
    """Get or create the global router."""
    global _router
    if _router is None:
        _router = AgentesRouter(logos=logos)
    return _router


def route_sync(args: list[str], ctx: Any = None) -> RouterResult:
    """
    Route CLI arguments synchronously.

    Creates a new event loop if needed.
    """
    router = get_router()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(router.route(args, ctx))


# =============================================================================
# CLI Handler
# =============================================================================


def cmd_agentese(args: list[str], ctx: Any = None) -> int:
    """
    Direct AGENTESE invocation from CLI.

    This is the handler for direct AGENTESE paths:
        kg self.forest.manifest
        kg /forest
        kg ?world.*
        kg subscribe world.town.*

    Usage:
        kg <path>                    # Invoke AGENTESE path
        kg <path> --json             # JSON output
        kg <path> --trace            # Show trace ID
        kg <path> --dry-run          # Show what would happen
    """
    # Check for global flags
    json_output = "--json" in args
    trace_output = "--trace" in args
    dry_run = "--dry-run" in args

    # Remove flags from args
    clean_args = [a for a in args if a not in ("--json", "--trace", "--dry-run")]

    router = get_router()
    router._config.json_output = json_output
    router._config.trace_output = trace_output
    router._config.dry_run = dry_run

    result = route_sync(clean_args, ctx)

    if not result.success:
        print(f"Error: {result.error}")
        return 1

    # Output result
    if json_output:
        import json

        print(json.dumps(result.result, indent=2, default=str))
    elif result.result is not None:
        if hasattr(result.result, "__rich__"):
            from rich.console import Console

            console = Console()
            console.print(result.result)
        else:
            print(result.result)

    if trace_output and result.trace_id:
        print(f"\nTrace ID: {result.trace_id}")

    return 0
